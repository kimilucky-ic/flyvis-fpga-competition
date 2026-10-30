"""Single manual start/stop entry. Import has no process, port, or GPU side effects."""
import argparse
from datetime import datetime,timedelta,timezone
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

from live_protocol import HERE, Registry, canonical, load, sha, utc, write

ACTIVE=HERE/'runtime/demo_active.json'


def start(enable_gpu=False,no_open=False,camera=False,power_mode='current_unconfirmed',stream_seconds=300,stream=False,desktop=False,skeleton=False):
    if type(stream_seconds) is not int or not 10<=stream_seconds<=300:raise ValueError('STREAM_OBSERVATION_BOUND')
    if power_mode not in ('quiet','balanced','performance','current_unconfirmed'):raise ValueError('POWER_MODE_LABEL')
    stream=stream or skeleton
    enable_gpu=enable_gpu or camera or stream
    desktop_python=HERE/'desktop_env/Scripts/python.exe'
    if desktop and not desktop_python.exists():raise ValueError('EXISTING_DESKTOP_ENV_REQUIRED')
    if ACTIVE.exists() and load(ACTIVE)['state'] not in ('STOPPED','START_FAILED'):
        raise ValueError('A demo launch record is still active. Use -Stop and inspect its logs; no unrelated process will be killed.')
    # Read-only occupancy check, only on the user's manual start. Never reuse an unknown old service.
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1',8771))==0:raise ValueError('8771 is occupied. Close the existing GUI via its owner before using the new launcher.')
    stream_port=None
    if camera or stream:
        # Linux port 0 can select a Windows Hyper-V excluded port (e.g. 56275).
        # Probe the Windows side before the new worker starts; no request is replayed.
        for candidate in range(18771,18779):
            try:
                with socket.socket() as probe:probe.bind(('127.0.0.1',candidate))
                stream_port=candidate;break
            except OSError:continue
        if stream_port is None:raise ValueError('No available local stream port; no GPU worker started.')
    registry=Registry();session_id=uuid.uuid4().hex;root=HERE/'runtime/live'/session_id;root.mkdir(parents=True)
    begin=datetime.now(timezone.utc)
    session={'schema':'flyvis-live-session/v1','session_id':session_id,'gpu_enabled':bool(enable_gpu),'confirmed_by_user':bool(enable_gpu),
        'evidence_scope':'USER_MANUAL_GPU_SESSION',
        'authorization_reference':'USER_MANUAL_-EnableGPU_INVOCATION' if enable_gpu else None,'start_utc':begin.isoformat(),
        'end_utc':(begin+timedelta(seconds=900)).isoformat(),'max_jobs':2,'max_steps':2910,'board_enabled':False}
    session.update(camera_enabled=bool(camera),camera_max_steps=60000,camera_max_duration_s=300)
    session['stream_enabled']=bool(camera or stream)
    if stream_port is not None:session['stream_rpc_port']=stream_port
    session['stream_observation_s']=stream_seconds
    session['skeleton_home']=bool(skeleton)
    session['stream_adapter_sha256']={n:sha(HERE/n) for n in ('live_protocol.py','checked_full.py','decoder_audit.py','stream_runtime.py','stream_renderer.py','prepared_camera_input.py','stream_cadence.py','stream_evidence.py','stream_wire.py','stream_bridge.py','stream_clock.py','stream_transport.py','realtime_timing.py','camera_stream_protocol.py','spatial_state.py')} if session['stream_enabled'] else {}
    session.update(power_mode_user_label=power_mode,power_mode_verified_by_program=False,program_changes_power_settings=False)
    write(root/'session.json',session);write(root/'controller.json',{'session_id':session_id,'unix_time':time.time(),'pid':os.getpid()})
    children=[];streams=[];state={'state':'STARTING','session_id':session_id,'root':str(root),'pid':os.getpid(),'gpu_enabled':enable_gpu,'started_utc':utc(),'children':[]}
    write(ACTIVE,state)
    def child(command,name):
        stream=(root/(name+'.log')).open('ab');streams.append(stream)
        flags=(subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP) if os.name=='nt' else 0
        process=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,creationflags=flags,cwd=str(HERE))
        children.append((name,process));state['children'].append({'name':name,'pid':process.pid,'command':command});write(ACTIVE,state)
    try:
        command=[sys.executable,'-B',str(HERE/'server.py'),'--port','8771','--live-session',str(root/'session.json'),'--stop-file',str(root/'STOP_REQUEST.json'),'--controller-file',str(root/'controller.json')]
        if no_open or desktop:command.append('--no-open')
        child(command,'gui')
        if enable_gpu:
            def linux(path):
                s=str(Path(path).resolve());return '/mnt/'+s[0].lower()+'/'+s[3:].replace('\\','/')
            child(['wsl.exe','-d','FlyVisCPU','--exec',registry.data['runtime']['python'],'-B',linux(HERE/'live_worker.py'),'--session',linux(root/'session.json')],'worker')
        if desktop:child([str(desktop_python),'-B',str(HERE/'desktop.py'),'--managed-session',str(root/'session.json')],'desktop')
        state['state']='RUNNING';write(ACTIVE,state)
        print('FlyVis demo: http://127.0.0.1:8771/ | GPU '+('bounded session requested' if enable_gpu else 'NOT_CONNECTED')+' | '+str(root),flush=True)
        while not (root/'STOP_REQUEST.json').exists():
            write(root/'controller.json',{'session_id':session_id,'unix_time':time.time(),'pid':os.getpid()})
            if any(name=='gui' and p.poll() is not None for name,p in children):break
            if any(name=='desktop' and p.poll() is not None for name,p in children):break
            worker_exit=next((p.poll() for name,p in children if name=='worker'),None)
            if worker_exit is not None and 'worker_exit' not in state:
                state['worker_exit']=worker_exit;state['GPU_status']='NOT_CONNECTED';write(ACTIVE,state)
                write(root/'worker_exit.json',{'session_id':session_id,'exit_code':worker_exit,'utc':utc()})
                print('GPU worker exited; existing offline GUI remains available. No automatic retry.',flush=True)
            time.sleep(1)
    except KeyboardInterrupt:pass
    finally:
        write(root/'STOP_REQUEST.json',{'reason':'MANUAL_OR_LAUNCHER_STOP','utc':utc()});state['state']='STOPPING';write(ACTIVE,state)
        for name,process in children:
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                if name=='gui':process.terminate();process.wait(timeout=10)
                else:
                    # Never force-kill a CUDA worker and call the GPU free.
                    state['state']='STOP_WAITING_FOR_CUDA';state['error']='Worker did not acknowledge stop. No forced GPU termination; inspect worker log.'
        if state['state']!='STOP_WAITING_FOR_CUDA':state['state']='STOPPED'
        state['exit_codes']={name:process.poll() for name,process in children};state['stopped_utc']=utc();write(ACTIVE,state)
        if desktop and (root/'stream/result.json').exists() and (root/'stream/control.json').exists():
            try:
                from stream_manual_summary import manual_summary
                summary=manual_summary(root/'stream',load(root/'stream/control.json'))
                write(root/'stream/manual_summary.json',summary)
                write(HERE/'runtime/last_manual_test.json',dict(session_id=session_id,status=summary['status'],summary_path=str(root/'stream/manual_summary.json')))
            except (OSError,ValueError,KeyError,TypeError) as error:
                write(root/'manual_summary_error.json',dict(error=str(error),utc=utc()))
        for stream in streams:stream.close()
        print(state['state'],flush=True)
    return 0 if state['state']=='STOPPED' and all(code==0 for name,code in state['exit_codes'].items() if name in ('gui','desktop')) else 1


def stop():
    if not ACTIVE.exists():print('No managed demo launch. No process touched.');return
    state=load(ACTIVE);root=Path(state['root']).resolve()
    if not root.is_relative_to((HERE/'runtime/live').resolve()):raise ValueError('STOP_WRITE_SCOPE')
    write(root/'STOP_REQUEST.json',{'reason':'MANUAL_STOP_COMMAND','utc':utc()})
    print('Stop requested for managed session '+state['session_id']+'; GPU release requires worker acknowledgment.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['start','stop','status']);parser.add_argument('--enable-gpu',action='store_true');parser.add_argument('--no-open',action='store_true');parser.add_argument('--camera',action='store_true');parser.add_argument('--power-mode',choices=['quiet','balanced','performance','current_unconfirmed'],default='current_unconfirmed');parser.add_argument('--stream-seconds',type=int,default=300);parser.add_argument('--stream',action='store_true');parser.add_argument('--desktop',action='store_true');parser.add_argument('--skeleton',action='store_true');args=parser.parse_args()
    if args.action=='start':raise SystemExit(start(args.enable_gpu,args.no_open,args.camera,args.power_mode,args.stream_seconds,args.stream,args.desktop,args.skeleton))
    elif args.action=='stop':stop()
    else:print(load(ACTIVE) if ACTIVE.exists() else {'state':'NOT_STARTED'})
