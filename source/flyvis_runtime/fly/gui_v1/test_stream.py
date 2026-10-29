"""Protocol tests only; historical arrays remain explicitly test fixtures."""
import base64
import copy
import hashlib
import json
import socket
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,check_chunk,load,sha,write
from stream_transport import AuditMonitor,LocalRPC,RPC,send,receive
from stream_runtime import StreamHub
from stream_bridge import StreamBridge,digital_spec
from spatial_state import SpatialRegistry
from test_live_protocol import Protocol

class StreamTests(unittest.TestCase):
    def setUp(self):
        self.h=StreamHub('s');self.control=dict(session_id='s',run_id='a'*32,source_kind='digital_direct',mode='Full',PL_execution=False)
        self.h.dispatch('bridge','start',self.control);self.h.dispatch('renderer','ready',None)
    def frame(self,n=0):
        return dict(png=base64.b64encode(b'CPU_PROTOCOL_BYTES_NOT_VIDEO').decode(),source=dict(run_id='a'*32,source_kind='digital_direct',
            sequence=n,relative_s=n/30,png_sha256=hashlib.sha256(b'CPU_PROTOCOL_BYTES_NOT_VIDEO').hexdigest()))
    def test_cross_run_input_rejected(self):
        f=self.frame();f['source']['run_id']='b'*32
        with self.assertRaisesRegex(ValueError,'INPUT_RUN'):self.h.dispatch('bridge','input',f)
    def test_sequence_loss_rejected(self):
        with self.assertRaisesRegex(ValueError,'SEQUENCE'):self.h.dispatch('bridge','input',self.frame(1))
    def test_stop_revokes_and_does_not_ack_cuda(self):
        self.h.packet={'fixture':True};s=self.h.dispatch('bridge','stop',None)
        self.assertFalse(s['result_valid']);self.assertFalse(s['stop_acknowledged']);self.assertIsNone(self.h.packet)
        with self.assertRaisesRegex(ValueError,'STOP'):self.h.dispatch('bridge','input',self.frame())
    def test_stale_controller_rejected_at_commit(self):
        self.h.bridge_at=time.monotonic()-4
        with self.assertRaisesRegex(ValueError,'DISCONNECTED'):self.h.check()
    def test_renderer_disconnect_rejected(self):
        self.h.renderer_at=time.monotonic()-4
        with self.assertRaisesRegex(ValueError,'RENDERER_DISCONNECTED'):self.h.check()
    def test_queue_overflow_has_no_substitution(self):
        for i in range(32):self.h.dispatch('bridge','input',self.frame(i))
        with self.assertRaisesRegex(ValueError,'OVERRUN'):self.h.dispatch('bridge','input',self.frame(32))
        self.assertEqual(len(self.h.raw),32)
    def test_auth_session_and_role(self):
        server=LocalRPC('s',self.h.dispatch);client=RPC(server.endpoint)
        try:
            self.assertEqual(client.call('status')['run_id'],'a'*32)
            invalid=RPC({**server.endpoint,'session_id':'other'})
            with self.assertRaises((OSError,ConnectionError)):invalid.call('status')
            self.assertEqual(client.call('status')['status'],'WAITING_SOURCE')
        finally:client.close();server.close()
    def test_atomic_windows_sharing_violation_is_bounded(self):
        import live_protocol
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            original=live_protocol.os.replace
            with patch('live_protocol.os.replace',side_effect=[PermissionError('sharing'),None]) as m:
                write(Path(d)/'x.json',{'test_only':True});self.assertEqual(m.call_count,2)
            with patch('live_protocol.os.replace',side_effect=PermissionError('persistent')),patch('live_protocol.time.sleep'):
                with self.assertRaises(PermissionError):write(Path(d)/'y.json',{})
    def test_monitor_failure_revokes_memory_gate(self):
        flag=[False]
        def audit():
            if flag[0]:raise ValueError('SOURCE_CHANGED')
        m=AuditMonitor(audit,.005)
        try:
            m.check();flag[0]=True;time.sleep(.03)
            with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):m.check('before_COMMIT')
        finally:m.close()
    def test_digital_controls_reject_nonfinite(self):
        with self.assertRaises(ValueError):digital_spec(dict(polarity='ON',direction_deg=60,speed_px_s=float('nan')))
    def test_spatial_chunk_roundtrip_and_tamper(self):
        p=Protocol();p.setUp()
        try:
            request,folder,event=p.fixture();s=SpatialRegistry()
            source=p.registry.path_for('intervention').parent/'artifacts/pilot_gpu_r1/ON60/Full/activities_full.npy'
            values=s.extract(np.load(source,mmap_mode='r',allow_pickle=False)[0,:32]);path=folder/'chunks/spatial.npy';np.save(path,values,allow_pickle=False)
            event['files']['spatial']=dict(path='chunks/spatial.npy',sha256=sha(path));event['spatial_map_sha256']=s.digest
            check_chunk(event,request,0,folder,test_only=True)
            event['spatial_map_sha256']='0'*64
            with self.assertRaises(ValueError):check_chunk(event,request,0,folder,test_only=True)
        finally:p.tearDown()
    def test_fake_PL_and_wrong_time_rejected(self):
        f=load(HERE/'evidence/realtime_prepare_20261012/node_test_fixture.json');s=SpatialRegistry();p=f['packet'];p['layers']['PL_proven_global_ids']=[1]
        with self.assertRaises(ValueError):s.validate(p,p['run_id'],p['step_id'],p['activity_time_s'],'Full')
        p=f['packet'];p['layers']=s.layers('Full',p['step_id'])
        with self.assertRaises(ValueError):s.validate(p,p['run_id'],p['step_id'],p['activity_time_s']+.005,'Full')
    def test_source_image_tamper_rejected(self):
        f=self.frame();f['source']['png_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'PNG_IDENTITY'):self.h.dispatch('bridge','input',f)
    def test_failed_results_revoke(self):
        self.h.packet={'test_only':True};self.h.revoke('GPU_TEST_FAILURE')
        self.assertIsNone(self.h.packet);self.assertFalse(self.h.status()['result_valid'])

if __name__=='__main__':unittest.main()
