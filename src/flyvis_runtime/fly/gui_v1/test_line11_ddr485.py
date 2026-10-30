"""Bounded CPU envelopes + original CPU decoder. No physical/GPU/camera launch."""
import ast,importlib,io,json,struct,sys,time,unittest,uuid,zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import line11_ddr_board as board
from line11_ddr_start import DdrGuiSession
from line11_ddr_plan import load_plan,STARTUP_FILES,PLAN485_SHA
from line11_ddr_bridge import verify_release,digest,BIT_SHA,HWH_SHA,MANIFEST_SHA,INITIAL_BOUNDARY

HERE=Path(__file__).parent
E=HERE/'evidence/line11_ddr485_on60_20261018'


class Tests(unittest.TestCase):
    def test_485_complete_protocol_CPU_decoder_and_failures(self):
        root=E/'cpu_cases'/uuid.uuid4().hex;root.mkdir(parents=True)
        release,_=verify_release();sys.path.insert(0,str(release))
        fake=importlib.import_module('cpu_replay');acceptance=importlib.import_module('ddr_acceptance')
        stream=DdrGuiSession(root,software_test=True,total_steps=485);stream.package('http://192.0.2.1:8771')
        with zipfile.ZipFile(stream.link_path) as z:
            self.assertLess(sum(x.file_size for x in z.infolist()),128000000)
            extract=root/'extract';z.extractall(extract)
        self.assertEqual(board.verify(extract)['plan_manifest_sha256'],PLAN485_SHA)
        nb=json.loads((stream.output/'START_DDR.ipynb').read_text(encoding='utf-8'))
        ast.parse(''.join(nb['cells'][1]['source']),feature_version=(3,8))
        for n in STARTUP_FILES:ast.parse((extract/n).read_text(encoding='utf-8'),feature_version=(3,8))
        print('CPU485 package/bounds/board-default-no-execute verified',flush=True)
        inp,states,_=load_plan(E/'plan',485)
        template=(release/'cpu_fixture_ddr.bin').read_bytes()[:188416];codec=stream.seed.codec
        records=bytearray(485*188416)
        for i in range(485):
            raw=bytearray(template);struct.pack_into('<I',raw,8,i)
            x=inp[i*2884:(i+1)*2884];a=states[i*182676:(i+1)*182676]
            raw[128:3012]=x;raw[4096:186772]=a
            struct.pack_into('<I',raw,48,codec.rolling(x));struct.pack_into('<I',raw,52,codec.rolling(a))
            records[i*188416:(i+1)*188416]=raw
        buffer=fake.Buffer(len(records));mmio=fake.MMIO(buffer,bytes(records))
        session=acceptance.AcceptanceSession(mmio,lambda **kwargs:buffer,buffer.barrier,
            [inp[i*2884:(i+1)*2884] for i in range(485)],
            [states[i*182676:(i+1)*182676] for i in range(485)],root/'records')
        op=dict(schema='flyvis-line2-ddr-operator/v1',preparation_id=stream.preparation_id,
            evidence='CPU_MOCK_ONLY',exclusive_board_window=True,boot_id='11111111-2222-3333-4444-555555555555',
            bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,release_manifest_sha256=MANIFEST_SHA,pynq_version='2.7.0',machine='armv7l',
            clock=dict(clock_control=0x200500,io_pll_control=0x1e000,pll_status=4,reference_mhz=33.333333),
            hp0_read_control=0,hp0_write_control=0,cache_policy='CLEAR_FLUSH_DSB_BEFORE_ARM;INVALIDATE_DSB_IMMUTABLE_COPY_AFTER_PUBLISH',
            barrier_library_sha256='a'*64,initial_state_readback=INITIAL_BOUNDARY,
            startup_sha256={n:digest((HERE/n).read_bytes()) for n in STARTUP_FILES})
        class PC:
            def first(_,s,operator):
                self.assertEqual(len(s.descriptors),1)
                blob=io.BytesIO()
                with zipfile.ZipFile(blob,'w',zipfile.ZIP_DEFLATED) as z:
                    for n in ('record_000000.bin','receipt_000000.json','RUN_CONTEXT.json'):z.write(s.output/n,n)
                    z.writestr('OPERATOR.json',json.dumps(op));z.writestr('TIMING.json',json.dumps(s.timing[0]))
                return stream.accept_first(blob.getvalue(),'Bearer '+stream.preparation_token)['connection']
        class HTTP:
            def request(_,method,route,body,headers):
                _.reply=stream.accept(body,headers['Authorization']) if route.endswith('/frame') else stream.finish(json.loads(body),headers['Authorization'])
            def getresponse(_):return SimpleNamespace(status=200,read=lambda n:json.dumps(_.reply).encode())
            def close(_):pass
        stream.start_cpu_flow()
        try:
            with patch('line11_display_client.http.client.HTTPConnection',return_value=HTTP()):result=board.run_bounded(session,PC(),op,release)
            self.assertEqual(result['states_compared'],22149465);self.assertEqual(result['mismatch_words'],0)
            self.assertEqual(stream.count,484);self.assertEqual(stream.drawn,0)
            self.assertEqual(buffer.free_calls,0)
            self.assertEqual(len(list(session.output.glob('record_*.bin'))),485)
            print('CPU485 protocol:485 actual CPU envelopes,0 paint dependency; waiting original decoder',flush=True)
            stream.flow_consumer.thread.join(120)
            flow_status=stream.flow_consumer.status();self.assertIsNone(flow_status['error'],flow_status)
            self.assertEqual(flow_status['status'],'COMPLETE');self.assertEqual(flow_status['decoded'],485)
            target=np.load(E/'CPU_REFERENCE_FLOW.npy',allow_pickle=False)
            error=0.
            for k in range(485):
                base=stream.flow_consumer.output/('%06d'%k)
                actual=np.frombuffer(base.with_suffix('.flow.bin').read_bytes(),dtype='<f4').reshape(2,721)
                error=max(error,float(np.max(np.abs(actual-target[k]))))
                np.testing.assert_allclose(actual,target[k],atol=1e-5,rtol=1e-5)
                self.assertEqual(digest(base.with_suffix('.state.bin').read_bytes()),digest(states[k*182676:(k+1)*182676]))
                self.assertEqual(json.loads(base.with_suffix('.json').read_text())['run_id'],session.run_id)
            final=stream.latest()['frame'];self.assertEqual(final['step_id'],484)
            self.assertAlmostEqual(final['activity_time_s'],1.425);self.assertEqual(final['flow_status'],'OFFICIAL_DECODER_SAME_STATE')
            self.assertEqual(final['flow_binding']['full_state_sha256'],final['full_state_sha256'])
            self.assertTrue(stream.status()['display_complete'])
            for k in (0,199,200,484):
                saved=stream.replay(k)['frame']
                self.assertTrue(saved['offline_replay']);self.assertEqual(saved['display_kind'],'CPU_PROTOCOL_TEST_ONLY')
                self.assertEqual(saved['full_state_sha256'],digest(states[k*182676:(k+1)*182676]))
                self.assertEqual(saved['flow_binding']['frame_id'],k)
            # Delayed rendering of an earlier DECODED frame remains a valid same-run receipt.
            stream.paint(dict(run_id=session.run_id,session_id=stream.session_id,frame_id=0,
                full_state_sha256=digest(states[:182676]),receive_to_draw_lower_ms=0.,receive_to_draw_upper_ms=1.))
            with self.assertRaises(ValueError):stream._flow_ready(stream.decoded_frame,dict(stream.decoded_frame[4],binding=dict(final['flow_binding'],run_id='WRONG')))
            with self.assertRaisesRegex(RuntimeError,'exhausted'):session.produce_next()
            # Full evidence export now exceeds old16MB bound and still includes all raw states.
            exported=board.export_evidence(session.output,session.run_id)
            with zipfile.ZipFile(exported['path']) as z:
                self.assertIn('record_000484.bin',z.namelist());self.assertNotIn('PREPARATION.json',z.namelist())
            bad=bytearray((extract/'plan_expected_states.bin').read_bytes());bad[-1]^=1
            (extract/'plan_expected_states.bin').write_bytes(bad)
            with self.assertRaisesRegex(ValueError,'PLAN_DATA_CHANGED'):board.verify(extract)
            stream.abort('TEST_INJECTED_FAILURE');self.assertIsNone(stream.latest()['frame'])
            verification=dict(evidence='CPU_MOCK_PROTOCOL_PLUS_ACTUAL_CPU_OFFICIAL_DECODER_ONLY',
                status='PASS',states_compared=result['states_compared'],mismatch_words=0,received_steps_including_first=485,
                official_flow_frames=485,flow_max_abs_vs_CPU_batch=error,atol=1e-5,rtol=1e-5,
                browser_frames=0,board_or_GPU_execution=False,camera_device_opened=False,
                CPU_case=str(root),export=exported)
            verification['source_sha256']={n:digest((HERE/n).read_bytes()) for n in
                ('line11_ddr_flow.py','line11_ddr_start.py','line11_ddr_plan.py','line11_ddr_board.py','line11_stream.py')}
            (E/'CPU_PROTOCOL_FINAL.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
        finally:stream.close()

    def test_camera_scope_preview_binding_without_new_capture(self):
        plan=E/'camera_software_replay/plan';pin=digest((plan/'RUN_PLAN.json').read_bytes())
        inp,states,_=load_plan(plan,485,pin)
        m=json.loads((plan/'RUN_PLAN.json').read_bytes())
        self.assertEqual(m['execution_kind'],'EXPLICIT_SAVED_CAMERA_RECORDING_SOFTWARE_REPLAY')
        self.assertEqual(len(m['source_frames']),485);self.assertEqual(m['input_time_offset_s'],0.)
        # Exact frame pixels remain read-only and tied to measured capture receipts.
        for k in (0,200,484):
            row=m['source_frames'][k]
            raw=(Path(m['recording_directory'])/'raw_frames'/('frame_%06d.png'%row['source_frame'])).read_bytes()
            self.assertEqual(digest(raw),row['pixel_png_sha256']);self.assertIn('capture_utc',row)
        with self.assertRaisesRegex(ValueError,'MANIFEST_CHANGED'):load_plan(plan,485)
        self.assertNotIn('pynq',sys.modules)


if __name__=='__main__':unittest.main(verbosity=2)
