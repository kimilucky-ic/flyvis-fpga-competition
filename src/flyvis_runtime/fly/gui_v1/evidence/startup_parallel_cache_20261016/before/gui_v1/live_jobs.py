"""GUI-owned file job API. CPU only; never launches a device or falls back to replay."""
import re
import threading
import time
import uuid
from pathlib import Path

from live_protocol import HERE, Registry, TERMINAL, canonical, check_chunk, host_path, load, require, sha, utc, validate_scope, write


class LiveGPUAdapter:
    def init__(self, session_path=None, registry=None, *, protocol_test=False):
        self.session_path=host_path(session_path) if session_path else None
        self.registry=registry
        self.lock=threading.RLock()
        self.requests={}
        self.validated_events={}
        self.error=None
        self.protocol_test=protocol_test
        try:
            self.registry=self.registry or Registry()
            self.registry_sha=canonical(self.registry.data)
            if self.session_path:
                self.session=load(self.session_path)
                self.root=self.session_path.parent
                require(self.root.resolve().is_relative_to((HERE/'runtime'/'live').resolve()),'SESSION_WRITE_SCOPE')
        except (OSError,ValueError,KeyError,TypeError) as exc:self.error=str(exc)

    def connected(self):
        require(not self.error,self.error or 'REGISTRY_NOT_AVAILABLE')
        require(self.session_path is not None,'NOT_CONNECTED: GPU session not started')
        self.session=load(self.session_path);validate_scope(self.session,protocol_test=self.protocol_test)
        require(not (self.root/'STOP_REQUEST.json').exists(),'SESSION_STOPPED')
        require(not (self.root/'GPU_STOP_REQUEST.json').exists(),'GPU_SESSION_STOPPED')
        beat=load(self.root/'heartbeat.json')
        require(beat.get('evidence_scope')==self.session['evidence_scope'],'SERVICE_EVIDENCE_SCOPE')
        require(beat['session_id']==self.session['session_id'] and beat['registry_sha256']==self.registry_sha,'SERVICE_IDENTITY')
        require(time.time()-float(beat['unix_time'])<15 and float(beat['unix_time'])<=time.time()+2,'SERVICE_DISCONNECTED')
        require(beat['state']=='READY' and beat['device']['type']=='cuda','GPU_NOT_READY '+beat['state'])
        self.registry.unchanged()
        return beat

    def capabilities(self):
        state='NOT_CONNECTED';error=self.error
        try:self.connected();state='CONNECTED'
        except (OSError,ValueError,KeyError,TypeError) as exc:error=str(exc)
        service=self.service_status(state,error)
        data=self.registry.data if self.registry else {}
        return {'schema':'flyvis-live-capabilities/v1','status':state,'error':error,'backend':'original_FlyVis_CUDA_and_DecoderGAVP',
            'service':service,
            'session_id':getattr(self,'session',{}).get('session_id'),
            'stream_enabled':getattr(self,'session',{}).get('stream_enabled',False),
            'camera_capture_enabled':getattr(self,'session',{}).get('camera_enabled',False),
            'conditions':data.get('inputs',{}),'modes':data.get('modes',[]),'types':data.get('types',[]),'model':data.get('model'),
            'chunk_frames':32,'steps':485,'dt_s':.005,'camera_input':data.get('camera'),
            'FPGA_status':'NOT_CONNECTED','PL_execution':False,'LIVE_INTERACTIVE_GUI_PASS':'NOT_RUN','REALTIME_STREAM_PASS':'NOT_RUN',
            'fixed_jobs_enabled':not (getattr(self,'session',{}).get('camera_enabled',False)),
            'job_id':None,'run_id':None,'result':None}

    def service_status(self,connection,error):
        """Diagnostic state only; connected() remains the computation admission gate."""
        value={'state':'NOT_STARTED','terminal':True,'message':'未启动 GPU 服务；离线演示仍可使用。','error':error}
        if not self.session_path:return value
        try:
            require(not self.error,self.error or 'REGISTRY_NOT_AVAILABLE')
            session=load(self.session_path);validate_scope(session,protocol_test=self.protocol_test)
            if (self.root/'STOP_REQUEST.json').exists() or (self.root/'GPU_STOP_REQUEST.json').exists():
                return dict(value,state='STOPPED',message='本次 GPU 会话已停止；重新计算需要重新打开实时入口。')
            beat=load(self.root/'heartbeat.json') if (self.root/'heartbeat.json').exists() else None
            if beat:
                require(beat['session_id']==session['session_id'] and beat['registry_sha256']==self.registry_sha,'SERVICE_IDENTITY')
                # Old STOPPED heartbeats omitted scope. They may report stopped, never readiness.
                require(beat.get('evidence_scope')==session['evidence_scope'] or
                        (beat['state']=='STOPPED' and 'evidence_scope' not in beat),'SERVICE_EVIDENCE_SCOPE')
                failure=beat.get('error')
                if beat['state']=='FAILED':
                    code=(failure or {}).get('code','WORKER_FAILED')
                    message='GPU 等待资源超时，启动失败；摄像头尚未开始。请结束占用任务后重新打开实时入口。' if code=='GPU_BUSY_TIMEOUT' else 'GPU 服务失败，请查看本次 worker.log。'
                    return dict(value,state='FAILED',message=message,error=failure)
                if beat['state']=='STOPPED':return dict(value,state='STOPPED',message='本次 GPU 服务已退出；不会继续启动摄像头。')
            exit_path=self.root/'worker_exit.json'
            if exit_path.exists():
                ended=load(exit_path);require(ended['session_id']==session['session_id'],'SERVICE_IDENTITY')
                return dict(value,state='FAILED' if ended['exit_code'] else 'STOPPED',message='GPU 服务已退出，请查看本次 worker.log；离线演示仍可用。',error=ended)
            if connection=='CONNECTED':return dict(value,state='READY',terminal=False,message='GPU 已就绪；点击启动后才会采集和计算。',error=None)
            if beat:
                require(-2<=time.time()-float(beat['unix_time'])<15,'SERVICE_DISCONNECTED')
                require(beat['state']=='PRELOADING','SERVICE_NOT_READY')
                waiting=beat.get('phase')=='WAITING_FOR_SHARED_GPU'
                startup=beat.get('startup') if isinstance(beat.get('startup'),dict) else {}
                labels={'registry_and_frozen_source_validation':'校验本次模型与输入身份',
                        'torch_import':'加载GPU计算环境','original_full_model_load':'加载原始完整网络',
                        'original_full_module_import':'加载原始网络依赖',
                        'official_flyvis_import':'加载FlyVis原始库及其依赖',
                        'original_full_model_construct':'构建原始完整网络并核验参数',
                        'official_decoder_load':'加载官方光流解码器'}
                detail=labels.get(startup.get('stage'),'加载原始模型和官方光流')
                if beat.get('phase')=='WARMING_ORIGINAL_CUDA':detail='预热原始GPU网络和官方光流'
                return dict(value,state='WAITING_FOR_GPU' if waiting else 'PRELOADING',terminal=False,
                            startup=startup,
                            message='正在等待 GPU 资源（最多15秒）；摄像头尚未开始。' if waiting else '正在'+detail+'；摄像头尚未开始。')
            from datetime import datetime
            require(time.time()-datetime.fromisoformat(session['start_utc']).timestamp()<30,'WORKER_HEARTBEAT_MISSING')
            return dict(value,state='STARTING',terminal=False,message='正在启动 GPU 后台；摄像头尚未开始。')
        except (OSError,ValueError,KeyError,TypeError) as exc:
            return dict(value,state='DISCONNECTED',message='GPU 服务未连接或状态校验失败；摄像头未启动，请查看本次日志。',error=str(exc))

    def submit(self, body):
        with self.lock:
            self.connected()
            require(not self.session.get('camera_enabled'),'MODE_PROFILE_CAMERA_ONLY')
            require(isinstance(body,dict) and set(body)=={'schema','condition_id','mode','input_sha256','registry_sha256'},'SUBMIT_SCHEMA')
            require(body['schema']=='flyvis-live-submit/v1' and body['registry_sha256']==self.registry_sha,'REGISTRY_IDENTITY')
            condition=body['condition_id'];mode=body['mode']
            require(mode in self.registry.data['modes'],'MODE_NOT_AVAILABLE')
            binding=self.registry.binding(condition)
            require(body['input_sha256']==binding['input_sha256'],'INPUT_SHA_CHANGED')
            modes=['Full','Sham']+([] if mode in ('Full','Sham') else [mode])
            ledger_path=self.root/'submitted.json'
            ledger=load(ledger_path) if ledger_path.exists() else {'jobs':[],'steps':0}
            require(len(ledger['jobs'])<self.session['max_jobs'] and ledger['steps']+485*len(modes)<=self.session['max_steps'],'SESSION_BUDGET_EXHAUSTED')
            job_id=uuid.uuid4().hex;folder=self.root/'jobs'/job_id
            request={'schema':'flyvis-live-job/v1','job_id':job_id,'comparison_id':'live_t4t5_'+uuid.uuid4().hex,'session_id':self.session['session_id'],
                'created_utc':utc(),'condition_id':condition,'selected_mode':mode,'modes':modes,'run_ids':{m:uuid.uuid4().hex for m in modes},
                'binding':binding,'central_global_ids':self.registry.data['central_global_ids'],'registry_sha256':self.registry_sha,
                'execution_kind':'cpu_protocol_test' if self.protocol_test else 'new_inference','actual_new_computation':not self.protocol_test,'PL_execution':False}
            # Reserve budget before publishing. A crash may consume budget but cannot duplicate execution.
            ledger['jobs'].append(job_id);ledger['steps']+=485*len(modes);write(ledger_path,ledger)
            write(folder/'request.json',request);self.requests[job_id]=request
            write(folder/'status.json',{'job_id':job_id,'status':'QUEUED','updated_utc':utc(),'step':0,'total_steps':485*len(modes),
                'request_sha256':canonical(request),'result':None,'PL_execution':False})
            return self.poll(job_id)

    def request(self,job_id):
        require(bool(re.fullmatch(r'[a-f0-9]{32}',job_id)),'UNKNOWN_JOB')
        require(self.session_path is not None,'NOT_CONNECTED')
        folder=self.root/'jobs'/job_id
        if job_id not in self.requests:
            request=load(folder/'request.json')
            require(job_id in load(self.root/'submitted.json')['jobs'] and request['job_id']==job_id and request['session_id']==self.session['session_id'],'UNKNOWN_JOB')
            require(request['binding']==self.registry.binding(request['condition_id']) and request['registry_sha256']==self.registry_sha,'REQUEST_IDENTITY')
            self.requests[job_id]=request
        request=self.requests[job_id]
        require(load(folder/'request.json')==request,'REQUEST_CHANGED')
        return request,folder

    def poll(self,job_id):
        with self.lock:
            request,folder=self.request(job_id);value=load(folder/'status.json')
            require(value['job_id']==job_id and value['request_sha256']==canonical(request),'STATUS_IDENTITY')
            require(value['status'] in {'QUEUED','RUNNING','DECODING',*TERMINAL},'STATUS_SCHEMA')
            require(type(value['step']) is int and 0<=value['step']<=485*len(request['modes']),'STATUS_PROGRESS')
            require(value['total_steps']==485*len(request['modes']),'STATUS_TOTAL_STEPS')
            if (folder/'STOP_REQUEST.json').exists():
                reason=load(folder/'STOP_REQUEST.json').get('reason','CANCELLED')
                value.update(status='DISCONNECTED' if reason=='SERVICE_DISCONNECTED' else 'CANCELLED',error=reason,result=None)
            elif value['status'] not in TERMINAL:
                try:self.connected()
                except (OSError,ValueError,KeyError,TypeError) as exc:
                    write(folder/'STOP_REQUEST.json',{'reason':'SERVICE_DISCONNECTED','error':str(exc),'utc':utc()})
                    value.update(status='DISCONNECTED',error=str(exc),result=None)
            value.update(comparison_id=request['comparison_id'],condition_id=request['condition_id'],binding=request['binding'],run_ids=request['run_ids'],
                selected_mode=request['selected_mode'],execution_kind=request['execution_kind'],FPGA_status='NOT_CONNECTED',PL_execution=False)
            # A producer COMPLETE flag alone does not admit data. Result route performs full validation.
            value['result']=None
            return value

    def cancel(self,job_id):
        with self.lock:
            request,folder=self.request(job_id)
            require(load(folder/'status.json')['status'] not in TERMINAL,'JOB_ALREADY_TERMINAL')
            write(folder/'STOP_REQUEST.json',{'reason':'CANCELLED','utc':utc()})
            return self.poll(job_id)

    def events(self,job_id,after=-1):
        request,folder=self.request(job_id);status=self.poll(job_id)
        require(status['status'] not in {'CANCELLED','DISCONNECTED','FAILED'},'RESULT_NOT_AVAILABLE '+status['status'])
        rows=[];expected={m:0 for m in request['modes']}
        for path in sorted((folder/'chunks').glob('*.json')):
            event=load(path);index=len(rows)
            require(event['event_index']==index,'EVENT_SEQUENCE')
            stamp=[canonical(event)]
            for pin in event['files'].values():
                target=(folder/pin['path']).resolve();require(target.is_relative_to(folder.resolve()),'CHUNK_WRITE_SCOPE')
                stat=target.stat();stamp.append((stat.st_size,stat.st_mtime_ns))
            key=(job_id,index)
            if self.validated_events.get(key)!=stamp:
                check_chunk(event,request,expected.get(event.get('mode'),-1),folder);self.validated_events[key]=stamp
            else:require(event['start_step']==expected.get(event.get('mode'),-1),'CHUNK_ORDER_OR_SIZE')
            expected[event['mode']]=event['stop_step'];rows.append(event)
        require(self.poll(job_id)['status'] not in {'CANCELLED','DISCONNECTED','FAILED'},'RESULT_INVALIDATED')
        return {'job_id':job_id,'status':status['status'],'events':[r for r in rows if r['event_index']>after],'next_cursor':len(rows)-1,'validated_steps':expected}

    def chunk(self,job_id,index):
        request,folder=self.request(job_id)
        rows=self.events(job_id)['events'];require(0<=index<len(rows),'UNKNOWN_CHUNK')
        event=rows[index];arrays=check_chunk(event,request,event['start_step'],folder)
        answer={'event':event,'activity':arrays['activity'].tolist(),'flow':arrays['flow'].tolist(),'spatial':None}
        if 'spatial' in arrays:
            from spatial_state import spatial_registry
            spatial=spatial_registry();spatial.unchanged()
            answer['spatial']={'map_sha256':spatial.digest,'values':arrays['spatial'].tolist(),
                'layers':[spatial.layers(event['mode'],k) for k in range(event['start_step'],event['stop_step'])]}
        return answer

    def result(self,job_id):
        request,folder=self.request(job_id);status=self.poll(job_id)
        require(status['status']=='COMPLETED','RESULT_NOT_AVAILABLE '+status['status'])
        require(status['step']==status['total_steps'],'INCOMPLETE_STATUS_PROGRESS')
        result=load(folder/'result.json');rows=self.events(job_id)
        require(all(v==485 for v in rows['validated_steps'].values()),'INCOMPLETE_COMMIT_SEQUENCE')
        require(result['job_id']==job_id and result['comparison_id']==request['comparison_id'] and result['binding']==request['binding']
            and result['run_ids']==request['run_ids'] and result['request_sha256']==canonical(request),'FINAL_RESULT_IDENTITY')
        require(result['event_chain_sha256']==canonical(rows['events']) and result['actual_new_computation'] is True
            and result['execution_kind']=='new_inference' and result['PL_execution'] is False,'FINAL_EVIDENCE_IDENTITY')
        require(result['device']['type']=='cuda' and result['evidence_level']=='ACTUAL_ORIGINAL_GPU_EXECUTION'
            and result['integrity_checks']=={'original_weights_unchanged':True,'decoder_state_unchanged':True,'all_commits_verified':True},'FINAL_EXECUTION_EVIDENCE')
        require(isinstance(result['wall_time_s'],(int,float)) and result['wall_time_s']>0,'ACTUAL_TIME_REQUIRED')
        for mode in request['modes']:
            require(result['counts'][mode]['neural_steps']==485 and result['counts'][mode]['decoder_frames']==485,'FINAL_COUNTS')
            pins=result['files'][mode]
            require(set(pins)=={'activities_full.npy','flow.npy','final_state_full.npy','time.npy','activity_time.npy','step_events.jsonl','run_identity.json'},'FINAL_FILE_SET')
            for pin in pins.values():
                path=(folder/pin['path']).resolve();require(path.is_relative_to(folder.resolve()) and sha(path)==pin['sha256'],'FINAL_MANIFEST_SHA')
            steps=[load_line for load_line in map(__import__('json').loads,(folder/pins['step_events.jsonl']['path']).read_text(encoding='utf-8').splitlines())]
            require(len(steps)==485 and all(r['status']=='COMMITTED' and r['step_id']==k and r['run_id']==request['run_ids'][mode]
                and r['job_id']==job_id and r['comparison_id']==request['comparison_id'] for k,r in enumerate(steps)),'FINAL_COMMIT_LOG')
            import numpy as np
            full=np.load(folder/pins['activities_full.npy']['path'],mmap_mode='r',allow_pickle=False)
            flow=np.load(folder/pins['flow.npy']['path'],mmap_mode='r',allow_pickle=False)
            require(full.shape==(1,485,45669) and flow.shape==(1,485,2,721) and full.dtype==flow.dtype==np.float32,'FINAL_ARRAY_SCHEMA')
            require(np.array_equal(np.load(folder/pins['final_state_full.npy']['path'],allow_pickle=False),full[0,-1]),'FINAL_STATE_IDENTITY')
            require(np.array_equal(np.load(folder/pins['time.npy']['path'],allow_pickle=False),self.registry.time)
                and np.array_equal(np.load(folder/pins['activity_time.npy']['path'],allow_pickle=False),self.registry.time+.005),'FINAL_TIME_IDENTITY')
            for e in rows['events']:
                if e['mode']!=mode:continue
                a,b=e['start_step'],e['stop_step'];chunk=check_chunk(e,request,a,folder)
                require(np.isfinite(full[:,a:b]).all() and np.array_equal(full[0,a:b][:,request['central_global_ids']],chunk['activity'])
                    and np.array_equal(flow[0,a:b],chunk['flow']),'FULL_TRAJECTORY_CHUNK_IDENTITY')
                if 'spatial' in chunk:
                    from spatial_state import spatial_registry
                    require(np.array_equal(spatial_registry().extract(full[0,a:b]),chunk['spatial']),'FULL_TRAJECTORY_SPATIAL_IDENTITY')
        return result


class LiveRoutes:
    """Pure route dispatcher: test without ports, GUI, Torch, or background polling."""
    def init__(self,adapter):self.adapter=adapter
    def route(self,method,path,body=None):
        from urllib.parse import urlparse,parse_qs
        parsed=urlparse(path);a=self.adapter
        try:
            if method=='GET' and parsed.path=='/api/live/spatial-map':
                from spatial_state import spatial_registry
                return 200,spatial_registry().public()
            if method=='GET' and parsed.path=='/api/live':
                value=a.capabilities();value['registry_sha256']=getattr(a,'registry_sha',None);return 200,value
            input_match=re.fullmatch(r'/api/live/inputs/(ON60|OFF90)(?:/(stimulus.bin))?',parsed.path)
            if method=='GET' and input_match:
                require(a.registry is not None and not a.error,'INPUT_NOT_AVAILABLE')
                a.registry.unchanged();condition=input_match[1];array=a.registry.input(condition)
                if input_match[2]:return 200,array[0,:,0].astype('<f4').tobytes()
                return 200,{'condition_id':condition,'binding':a.registry.binding(condition),'coordinates':a.registry.uv.tolist(),
                    'shape':[485,721],'dtype':'little_endian_float32','input_time_s':a.registry.time.tolist(),
                    'activity_time_s':(a.registry.time+.005).tolist(),'display_kind':'FROZEN_INPUT_PREVIEW_ONLY'}
            if method=='POST' and parsed.path in ('/api/live/jobs','/api/inference'):return 202,a.submit(body)
            match=re.fullmatch(r'/api/live/jobs/([a-f0-9]{32})(?:/(events|result|cancel|chunks/\d+))?',parsed.path)
            require(match is not None,'UNKNOWN_ROUTE');job,tail=match[1],match[2]
            if method=='POST' and tail=='cancel':return 200,a.cancel(job)
            require(method=='GET','METHOD_NOT_ALLOWED')
            if not tail:return 200,a.poll(job)
            if tail=='events':return 200,a.events(job,int(parse_qs(parsed.query).get('after',['-1'])[0]))
            if tail=='result':return 200,a.result(job)
            if tail.startswith('chunks/'):return 200,a.chunk(job,int(tail.split('/')[1]))
            raise ValueError('UNKNOWN_ROUTE')
        except (ValueError,OSError,KeyError,TypeError) as exc:
            error=str(exc);code=503 if any(s in error for s in ('NOT_CONNECTED','GPU_NOT_','SERVICE_DISCONNECTED','SCOPE_')) else 409
            return code,{'status':'NOT_CONNECTED' if code==503 else 'NOT_AVAILABLE','error':error,'job_id':None,'run_id':None,'result':None,'PL_execution':False}
