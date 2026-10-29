"""CPU protocol fixtures using frozen bytes; NO actual hardware PASS is produced."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import numpy as np
from line11_result import (READINESS, BUNDLE_SHA, DRIVER_SHA, STEPPER_SHA, PASS,
                           FullPLResult, archive_files, digest, validate_files)
from live_protocol import host_path, load


def fixture():
    """In-memory producer-shaped envelope only; this is not board evidence."""
    contract = load(READINESS)
    base = host_path(contract['selected_local_candidate']).parent/'preboard_20261018/bundle_r1'
    files = {'actual_input.bin': (base/'input_frame0.bin').read_bytes(),
             'actual_initial.bin': (base/'initial_state.bin').read_bytes(),
             'actual_state1.bin': (base/'expected_state1.bin').read_bytes(), 'events.jsonl': b'CPU_PROTOCOL_FIXTURE_ONLY\n'}
    run, boot = 'LINE11_MANUAL_'+'0'*32, '00000000-0000-0000-0000-000000000000'
    images = dict(bit_sha256=contract['bit']['sha256'], hwh_sha256=contract['hwh']['sha256'])
    timings = dict(input_seconds=.1, step_call_seconds=.03, readback_seconds=.2, core_seconds_from_counter=.02201418)
    result = dict(status=PASS, board_result=True, evidence_level='PHYSICAL_BOARD', **images,
                  candidate='hole_pipeline_20261016/soc_r2', automatic_retry=False, DMA=False,
                  completed_steps=1, full_network_edges=1513231, state_words_checked=45669, mismatch_words=0,
                  hardware_counters=dict(completed_steps=1,nodes=45669,edges=1513231,faults=0,last_cycles=2201418),
                  observed_FCLK0_MHz=100, timing=timings)
    context = dict(run_id=run,boot_id=boot,status=PASS,backend='FULL_NETWORK_FPGA',hardware_operator='HUMAN_USER',
                   source_bundle_sha256=BUNDLE_SHA,driver_sha256=DRIVER_SHA,frame_stepper_sha256=STEPPER_SHA,
                   provenance=load(base/'PROVENANCE.json'),**images,model_dt_s=.005,frame_id=0,
                   node_order='global_node_id_0_through_45668',byte_order='little_endian_uint32_FP32_bits',
                   input_sha256=digest(files['actual_input.bin']),initial_sha256=digest(files['actual_initial.bin']),
                   board_id_label='CPU_PROTOCOL_FIXTURE_NOT_ACTUAL_BOARD')
    packet = dict(schema='flyvis-line11-saved-display-frame/v1',evidence='PHYSICAL_BOARD_ONE_STEP_ALL_STATES',
                  run_id=run,boot_id=boot,frame_id=0,completed_steps=1,input_bits_path='actual_input.bin',state_bits_path='actual_state1.bin',
                  validation_path='state1_compare.json',context_path='RUN_CONTEXT.json',input_bytes=2884,state_bytes=182676,
                  input_sha256=context['input_sha256'],state_sha256=digest(files['actual_state1.bin']),faults=0,
                  compute_cycles=2201418,clock_hz=100_000_000,input_upload_ms=100.,compute_wait_ms=30.,full_state_readback_ms=200.,elapsed_seconds=.33)
    values = {'result.json':result,'RUN_CONTEXT.json':context,'SAVED_DISPLAY_FRAME.json':packet,
              'board_before.json':dict(boot_id=boot),'bundle_check.json':dict(status='PASS_OFFLINE_BUNDLE_ONLY',**images)}
    for name, raw in [('initial_compare.json','actual_initial.bin'),('state1_compare.json','actual_state1.bin')]:
        values[name] = dict(words=45669,mismatch_words=0,actual_sha256=digest(files[raw]),expected_sha256=digest(files[raw]))
    files.update({k: json.dumps(v).encode() for k,v in values.items()})
    return seal(files), contract


def seal(files):
    files = dict(files)
    files['EVIDENCE_MANIFEST.json'] = json.dumps(dict(run_id='LINE11_MANUAL_'+'0'*32,status=PASS,
        files={k:dict(bytes=len(v),sha256=digest(v)) for k,v in files.items() if k!='EVIDENCE_MANIFEST.json'})).encode()
    return files


def change(files, name, **changes):
    files=copy.deepcopy(files);value=json.loads(files[name]);value.update(changes)
    files[name]=json.dumps(value).encode()
    return seal(files)


class SavedFirstStepTests(unittest.TestCase):
    def test_protocol_and_real_global_node_slice(self):
        files, contract = fixture()
        self.assertEqual(validate_files(files,contract)['packet']['completed_steps'],1)
        parent=READINESS.parent.parent/'line11_gui_import_20261018'
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            self.assertTrue(Path(tmp).resolve().is_relative_to(parent.resolve()))
            path=Path(tmp)/'CPU_PROTOCOL_FIXTURE.zip'
            with zipfile.ZipFile(path,'w') as z:
                for name,data in files.items():z.writestr(name,data)
            reader=FullPLResult(path)
            # This entire test is CPU fixture validation, not a hardware result.
            packet=reader.frame()
            self.assertEqual(packet['display_kind'],'OFFLINE_REPLAY_FULL_NETWORK_FPGA')
            self.assertEqual(len(packet['spatial']['values']),5768)
            self.assertEqual(packet['signed_means'],np.asarray(packet['spatial']['values'],dtype=np.float32).reshape(8,721).mean(axis=1,dtype=np.float64).tolist())
            self.assertIsNone(packet['flow'])
            geometry=reader.projection()
            self.assertEqual(geometry['consumer_kind'],'FULL_PL_VERIFIED_SAVED_RESULT')
            self.assertEqual(len(geometry['coordinates_uv']),721)
            self.assertGreater(len(reader.cache()),100)

    def test_last_global_node_corruption_even_with_resealed_manifest(self):
        files, contract=fixture();raw=bytearray(files['actual_state1.bin']);raw[-4]^=1
        files['actual_state1.bin']=bytes(raw)
        with self.assertRaisesRegex(ValueError,'ALL_WORD_MISMATCH'):validate_files(seal(files),contract)

    def test_identity_status_and_timing_fail_closed(self):
        files, contract=fixture()
        cases=[('result.json',dict(board_result=False,evidence_level='CPU_MOCK_ONLY')),
               ('RUN_CONTEXT.json',dict(boot_id='11111111-1111-1111-1111-111111111111')),
               ('RUN_CONTEXT.json',dict(source_bundle_sha256='0'*64)),
               ('RUN_CONTEXT.json',dict(model_dt_s=.01)),
               ('SAVED_DISPLAY_FRAME.json',dict(completed_steps=2)),
               ('SAVED_DISPLAY_FRAME.json',dict(full_state_readback_ms=-1)),
               ('result.json',dict(hardware_counters=dict(completed_steps=1,nodes=45669,edges=1513231,faults=1,last_cycles=2201418)))]
        for name, changes in cases:
            with self.subTest(changes=changes),self.assertRaises(ValueError):validate_files(change(files,name,**changes),contract)

    def test_unconfigured_or_missing_import_leaves_offline_available(self):
        self.assertEqual(FullPLResult().status()['status'],'NOT_CONFIGURED')
        reader=FullPLResult(READINESS.parent/'NO_SUCH_RESULT.zip')
        self.assertEqual(reader.status()['status'],'NOT_AVAILABLE')
        with self.assertRaises(ValueError):reader.frame()

    def test_zip_paths_duplicates_and_manifest_tamper(self):
        files, contract=fixture()
        damaged=dict(files);damaged['events.jsonl']+=b'changed'
        with self.assertRaisesRegex(ValueError,'FILE_SHA'):validate_files(damaged,contract)
        for extra in ['../outside','/absolute']:
            stream=io.BytesIO()
            with zipfile.ZipFile(stream,'w') as z:
                for name,data in files.items():z.writestr(name,data)
                z.writestr(extra,b'x')
            with self.assertRaisesRegex(ValueError,'UNSAFE_NAME'):archive_files(stream.getvalue())


if __name__=='__main__':unittest.main(verbosity=2)
