"""Direct CPU route/negative tests. Uses actual historical slices as TEST ONLY data.

Never binds HTTP, starts a worker, imports Torch, or invents neural activities.
CPU test scopes are explicitly rejected by the real worker authorization gate.
"""
import copy
from datetime import datetime,timedelta,timezone
import json
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path

import numpy as np
from live_protocol import HERE,Registry,canonical,checked_commit,check_chunk,load,sha,utc,validate_scope,write
from live_jobs import LiveGPUAdapter,LiveRoutes

REGISTRY=None


class Protocol(unittest.TestCase):
    def setUp(self):
        global REGISTRY
        REGISTRY=REGISTRY or Registry();self.registry=REGISTRY
        self.root=HERE/'runtime/live'/('CPU_PROTOCOL_TEST_'+uuid.uuid4().hex);self.root.mkdir(parents=True)
        begin=datetime.now(timezone.utc)
        self.session={'schema':'flyvis-live-session/v1','session_id':uuid.uuid4().hex,'gpu_enabled':True,'confirmed_by_user':True,
            'authorization_reference':'CPU_TEST_NOT_EXECUTION_PERMISSION','evidence_scope':'CPU_PROTOCOL_TEST_ONLY',
            'start_utc':begin.isoformat(),'end_utc':(begin+timedelta(seconds=60)).isoformat(),'max_jobs':2,'max_steps':2910,'board_enabled':False}
        write(self.root/'session.json',self.session)
        self.heartbeat()
        self.a=LiveGPUAdapter(self.root/'session.json',self.registry,protocol_test=True);self.routes=LiveRoutes(self.a)
    def tearDown(self):
        self.session['gpu_enabled']=False;write(self.root/'session.json',self.session)
        write(self.root/'STOP_REQUEST.json',{'reason':'CPU_TEST_FINISHED','utc':utc()})
    def heartbeat(self,age=0):
        write(self.root/'heartbeat.json',{'session_id':self.session['session_id'],'registry_sha256':canonical(self.registry.data),
            'unix_time':time.time()-age,'state':'READY','device':{'type':'cuda','name':'CPU_PROTOCOL_METADATA_ONLY'},'evidence_scope':'CPU_PROTOCOL_TEST_ONLY'})
    def body(self,condition='ON60',mode='BLOCK_T5_RELEASE'):
        return {'schema':'flyvis-live-submit/v1','condition_id':condition,'mode':mode,
            'input_sha256':self.registry.binding(condition)['input_sha256'],'registry_sha256':canonical(self.registry.data)}
    def submit(self,condition='ON60',mode='BLOCK_T5_RELEASE'):
        code,data=self.routes.route('POST','/api/live/jobs',self.body(condition,mode));self.assertEqual(code,202,data);return data
    def fixture(self):
        job=self.submit();request,folder=self.a.request(job['job_id']);chunks=folder/'chunks';chunks.mkdir()
        # Read just 32 actual original states and flow frames via mmap, not a GPU recomputation or bulk audit.
        source=self.registry.path_for('intervention').parent/'artifacts/pilot_gpu_r1/ON60/Full'
        activity=np.load(source/'activities_full.npy',mmap_mode='r',allow_pickle=False)[0,:32][:,request['central_global_ids']]
        flow=np.load(source/'flow.npy',mmap_mode='r',allow_pickle=False)[0,:32]
        files={}
        for name,array in [('activity',activity),('flow',flow)]:
            path=chunks/(name+'.npy');np.save(path,array,allow_pickle=False);files[name]={'path':str(path.relative_to(folder)),'sha256':sha(path)}
        event={'schema':'flyvis-live-chunk/v1',**{k:request[k] for k in ('job_id','comparison_id','condition_id','binding')},
            'mode':'Full','run_id':request['run_ids']['Full'],'start_step':0,'stop_step':32,'committed_stop_step':32,
            'event_index':0,'central_global_ids':request['central_global_ids'],'input_sha256':request['binding']['input_sha256'],
            'input_time_s':self.registry.time[:32].tolist(),'activity_time_s':(self.registry.time[:32]+.005).tolist(),
            'files':files,'execution_kind':'cpu_protocol_test','actual_new_computation':False,'evidence_level':'CPU_PROTOCOL_TEST_DOUBLE',
            'neural_steps_in_chunk':32,'decoder_frames_in_chunk':32,'PL_execution':False,'device':{'type':'cpu'},
            'source_activity':'HISTORICAL_ON60_FULL_SLICE_FOR_PROTOCOL_ONLY','new_neural_calls':0}
        return request,folder,event
    def test_01_no_backend_returns_503(self):
        routes=LiveRoutes(LiveGPUAdapter(registry=self.registry));code,value=routes.route('POST','/api/live/jobs',self.body())
        self.assertEqual(code,503);self.assertIsNone(value['result'])
    def test_02_scope_fixture_not_executable(self):
        with self.assertRaisesRegex(ValueError,'SCOPE_NOT_EXECUTABLE'):validate_scope(self.session)
    def test_03_submit_and_unique_identity(self):
        one=self.submit();two=self.submit('OFF90');self.assertNotEqual(one['job_id'],two['job_id']);self.assertNotEqual(one['run_ids'],two['run_ids'])
        self.assertEqual(one['status'],'QUEUED');self.assertIsNone(one['result']);self.assertTrue(one['comparison_id'].startswith('live_t4t5_'))
    def test_04_input_sha_changed(self):
        body=self.body();body['input_sha256']='0'*64;code,value=self.routes.route('POST','/api/live/jobs',body)
        self.assertEqual(code,409);self.assertIsNone(value['job_id'])
    def test_05_unknown_mode(self):
        body=self.body();body['mode']='FPGA_Replacement';self.assertEqual(self.routes.route('POST','/api/live/jobs',body)[0],409)
    def test_06_budget_no_third_job(self):
        self.submit();self.submit();self.assertEqual(self.routes.route('POST','/api/live/jobs',self.body())[0],409)
    def test_07_cancel_and_result_denied(self):
        job=self.submit();self.assertEqual(self.a.cancel(job['job_id'])['status'],'CANCELLED')
        self.assertEqual(self.routes.route('GET',f"/api/live/jobs/{job['job_id']}/result")[0],409)
    def test_08_disconnect_and_late_complete_denied(self):
        job=self.submit();self.heartbeat(age=20);self.assertEqual(self.a.poll(job['job_id'])['status'],'DISCONNECTED')
        request,folder=self.a.request(job['job_id']);status=load(folder/'status.json');status['status']='COMPLETED';write(folder/'status.json',status)
        self.heartbeat();self.assertEqual(self.a.poll(job['job_id'])['status'],'DISCONNECTED')
    def test_09_fail_not_commit(self):
        commits=[]
        def gate(_):raise ValueError('CANCEL_OR_SCOPE_EXPIRED')
        with self.assertRaises(ValueError):checked_commit('candidate metadata only',gate,commits.append)
        self.assertEqual(commits,[])
    def test_10_cpu_double_pass_only_explicit_test(self):
        request,folder,event=self.fixture();data=check_chunk(event,request,0,folder,test_only=True)
        self.assertEqual(data['flow'].shape,(32,2,721))
        with self.assertRaises(ValueError):check_chunk(event,request,0,folder)
    def test_11_old_run_identity(self):
        request,folder,event=self.fixture();event['run_id']='2041849d-b1f8-46ad-a059-49b598c19ab2'
        with self.assertRaisesRegex(ValueError,'RESULT_RUN_ID'):check_chunk(event,request,0,folder,test_only=True)
    def test_12_duplicate_step(self):
        request,folder,event=self.fixture()
        with self.assertRaisesRegex(ValueError,'CHUNK_ORDER'):check_chunk(event,request,32,folder,test_only=True)
    def test_13_time_offset(self):
        request,folder,event=self.fixture();event['activity_time_s']=event['input_time_s']
        with self.assertRaisesRegex(ValueError,'EULER_TIME'):check_chunk(event,request,0,folder,test_only=True)
    def test_14_hash_changed(self):
        request,folder,event=self.fixture();event['files']['flow']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'CHUNK_FILE'):check_chunk(event,request,0,folder,test_only=True)
    def test_15_nan_metadata(self):
        request,folder,event=self.fixture();event['input_time_s'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'EULER_TIME'):check_chunk(event,request,0,folder,test_only=True)
    def test_16_path_escape(self):
        request,folder,event=self.fixture();event['files']['activity']['path']='../request.json'
        with self.assertRaisesRegex(ValueError,'CHUNK_FILE'):check_chunk(event,request,0,folder,test_only=True)
    def test_17_false_hardware_claim(self):
        request,folder,event=self.fixture();event['PL_execution']=True
        with self.assertRaisesRegex(ValueError,'PL_CLAIM'):check_chunk(event,request,0,folder,test_only=True)
    def test_18_changed_request(self):
        job=self.submit();request,folder=self.a.request(job['job_id']);wrong=copy.deepcopy(request);wrong['binding']['model']['checkpoint_sha256']='0'*64;write(folder/'request.json',wrong)
        with self.assertRaisesRegex(ValueError,'REQUEST_CHANGED'):self.a.poll(job['job_id'])
    def test_19_new_result_never_available_when_queued(self):
        job=self.submit();self.assertEqual(self.routes.route('GET',f"/api/live/jobs/{job['job_id']}/result")[0],409)
    def test_20_scope_expiry(self):
        self.session['end_utc']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();write(self.root/'session.json',self.session)
        with self.assertRaises(ValueError):self.a.connected()
    def test_21_direct_input_preview_both_conditions(self):
        for condition in ('ON60','OFF90'):
            code,meta=self.routes.route('GET','/api/live/inputs/'+condition);self.assertEqual(code,200)
            code,binary=self.routes.route('GET','/api/live/inputs/'+condition+'/stimulus.bin');self.assertEqual(code,200)
            self.assertTrue(np.array_equal(np.frombuffer(binary,dtype='<f4').reshape(485,721),self.registry.input(condition)[0,:,0]))
            self.assertEqual(meta['display_kind'],'FROZEN_INPUT_PREVIEW_ONLY')
    def test_22_failed_status_no_event_or_result(self):
        job=self.submit();request,folder=self.a.request(job['job_id']);status=load(folder/'status.json');status['status']='FAILED';status['error']='decoder failed';write(folder/'status.json',status)
        self.assertEqual(self.routes.route('GET',f"/api/live/jobs/{job['job_id']}/events")[0],409)
    def test_23_test_scope_not_production_connection(self):
        adapter=LiveGPUAdapter(self.root/'session.json',self.registry);self.assertEqual(adapter.capabilities()['status'],'NOT_CONNECTED')
    def test_24_wrong_global_ids_and_counts(self):
        request,folder,event=self.fixture();event['central_global_ids']=list(reversed(event['central_global_ids']))
        with self.assertRaisesRegex(ValueError,'CENTRAL_NODE'):check_chunk(event,request,0,folder,test_only=True)
        event['central_global_ids']=request['central_global_ids'];event['decoder_frames_in_chunk']=0
        with self.assertRaisesRegex(ValueError,'CHUNK_COUNTS'):check_chunk(event,request,0,folder,test_only=True)
    def test_25_fake_complete_flag_no_result_admission(self):
        job=self.submit();request,folder=self.a.request(job['job_id']);status=load(folder/'status.json');status['status']='COMPLETED';write(folder/'status.json',status)
        write(folder/'result.json',{'status':'PASS','job_id':job['job_id']})
        code,value=self.routes.route('GET',f"/api/live/jobs/{job['job_id']}/result")
        self.assertEqual(code,409);self.assertIsNone(value['result'])
    def test_26_changed_frozen_file_pin(self):
        registry=copy.copy(self.registry);registry.pins=copy.deepcopy(registry.pins);registry.pins['stimulus_ON60']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'INPUT_SHA_CHANGED'):registry.input('ON60')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'evidence/live_interface_20261012/cpu_protocol.json');args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Protocol);run=unittest.TextTestRunner(verbosity=1).run(suite)
    no_devices=not any(name in sys.modules for name in ('torch','flyvis','cv2'))
    report={'status':'PASS_CPU_LIVE_INTERFACE_PROTOCOL' if run.wasSuccessful() and no_devices else 'FAIL','utc':utc(),
        'tests':run.testsRun,'failures':len(run.failures),'errors':len(run.errors),'CPU_fixture_source':'actual historical ON60 Full slices; explicit TEST ONLY, production rejects',
        'GUI_service_started':False,'HTTP_port_bound':False,'new_GPU_runs':0,'new_neural_steps':0,'new_decoder_calls':0,'camera_operations':0,'board_operations':0,
        'no_device_imports':no_devices,'LIVE_INTERACTIVE_GUI_PASS':'NOT_RUN','REALTIME_STREAM_PASS':'NOT_RUN'}
    write(args.output,report);print(json.dumps(report));sys.exit(0 if report['status'].startswith('PASS') else 1)
