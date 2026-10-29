"""ONE bounded CPU protocol check of sealed RTL records; no board/GPU run."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from line11_ddr_bridge import (verify_release,record_codec,DdrAuditForwarder,PROFILE,
    BIT_SHA,HWH_SHA,CORE_CYCLES,INITIAL_BOUNDARY,ZIP_SHA,digest)
from line11_display_client import Line11DisplayClient
from line11_result import FullPLResult
from line11_stream import FullPLStream


class DdrBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root,cls.files=verify_release()
        cls.codec=record_codec(cls.root,cls.files)
        raw=(cls.root/'cpu_fixture_ddr.bin').read_bytes()
        cls.raw=[raw[i*188416:(i+1)*188416] for i in range(3)]
        cls.records=[cls.codec.decode_record(x,i) for i,x in enumerate(cls.raw)]
        expected=(cls.root/'expected_states.bin').read_bytes();inputs=(cls.root/'inputs.bin').read_bytes()
        for i,r in enumerate(cls.records):
            assert r.state_bits==expected[i*182676:(i+1)*182676]
            assert r.input_bits==inputs[i*2884:(i+1)*2884]
        cls.old=FullPLResult(cls.root.parents[1]/'board_acceptance_20261018_r1/LINE11_MANUAL_456b728e575241fa804d62b4015d1b67_RESULT.zip')
        cls.old.frame()
        cls.run_id='DDR_CPU_PROTOCOL_ONLY';cls.cookie=17
        audit=cls.codec.AuditSequence(3);cls.receipts=[]
        for i,r in enumerate(cls.records):
            audit.append(r)
            cls.receipts.append(dict(audit.receipts[-1],run_id=cls.run_id,cookie=cls.cookie,evidence='CPU_MOCK_ONLY',
                board_result=False,record_bytes=188416,record_sha256=digest(cls.raw[i])))

    def seed(self):
        p=self.old.frame();p.update(run_id=self.run_id,session_id=self.run_id,transport_profile=PROFILE,
            initial_state_readback=INITIAL_BOUNDARY,operator_context_pc_verified=False,
            audit_chain=self.receipts[0]['chain'],audit_cookie=self.cookie)
        p['hardware'].update(bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,compute_cycles=CORE_CYCLES)
        return SimpleNamespace(frame=lambda:p,spatial=self.old.spatial,archive_sha=ZIP_SHA)

    def client(self):
        stream=FullPLStream(self.seed(),True,2,protocol_test=True)
        config=stream.connection('http://192.0.2.1:8771')
        class MemoryHTTP:
            def request(_,method,route,body,headers):_.value=stream.accept(body,headers['Authorization'])
            def getresponse(_):return SimpleNamespace(status=200,read=lambda n:json.dumps(_.value).encode())
            def close(_):pass
        with patch('line11_display_client.http.client.HTTPConnection',return_value=MemoryHTTP()):client=Line11DisplayClient(config)
        client.bind_retained_state(self.records[0].state_bits,1,config['boot_id'])
        return stream,client

    def test_all_three_records_match_frozen_oracle_and_spatial_map(self):
        self.assertEqual(len(self.files)+1,23)  # manifest is the 23rd ZIP member
        self.assertEqual(sum(len(x.state_bits)//4 for x in self.records),137007)
        self.assertEqual(digest(self.records[0].state_bits),self.old.frame()['full_state_sha256'])
        for r in self.records:
            self.assertEqual(r.cycles,CORE_CYCLES)
            self.assertEqual(len(self.old.spatial.extract(np.frombuffer(r.state_bits,dtype='<f4'))),5768)

    def test_audited_records_to_existing_GUI_ingress_and_no_physical_label(self):
        stream,client=self.client();forwarder=DdrAuditForwarder(client,self.cookie,self.receipts[0])
        for i in (1,2):forwarder.publish(self.records[i],self.receipts[i],0.)  # CPU fixture, not measured board time
        p=stream.latest()['frame']
        self.assertEqual(p['step_id'],2);self.assertEqual(stream.status()['received_steps'],2)
        self.assertEqual(p['spatial']['values'],self.old.spatial.extract(np.frombuffer(self.records[2].state_bits,dtype='<f4')).tolist())
        self.assertEqual(p['source_audit']['chain'],self.receipts[2]['chain'])
        self.assertEqual(p['display_kind'],'CPU_PROTOCOL_TEST_ONLY')
        self.assertEqual(p['initial_state_readback'],INITIAL_BOUNDARY)
        self.assertIsNone(p['flow'])

    def test_CPU_context_cannot_open_production_or_use_old_MMIO_admission(self):
        production=FullPLStream(self.seed(),True)
        with self.assertRaisesRegex(ValueError,'OPERATOR_CONTEXT_NOT_ACCEPTED'):production.connection('http://192.0.2.1:8771')
        old=FullPLStream(self.old,True).connection('http://192.0.2.1:8771')
        with self.assertRaisesRegex(ValueError,'REQUIRES_DDR_GUI_ADMISSION'):
            DdrAuditForwarder(SimpleNamespace(config=old),self.cookie,self.receipts[0])

    def test_wrong_chain_array_and_evidence_stop_without_retry(self):
        for changes in [dict(chain='0'*64),dict(state_sha256='0'*64),dict(evidence='OPERATOR_PHYSICAL_READS_UNATTESTED'),dict(frame_id=2)]:
            stream,client=self.client();forwarder=DdrAuditForwarder(client,self.cookie,self.receipts[0])
            bad=dict(self.receipts[1],**changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):forwarder.publish(self.records[1],bad,0.)
            self.assertEqual(stream.status()['received_steps'],0)
            with self.assertRaisesRegex(ValueError,'FAILED_NO_RETRY'):forwarder.publish(self.records[1],self.receipts[1],0.)


if __name__=='__main__':unittest.main(verbosity=2)
