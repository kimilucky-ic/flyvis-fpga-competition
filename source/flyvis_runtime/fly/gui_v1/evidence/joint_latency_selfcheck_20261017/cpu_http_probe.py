"""Bounded CPU-only authenticated /guard probe. No neural or hardware endpoint.

Uses the existing PCClockClient/PreparationAuthority guard body, a deliberately
non-hardware CPU binding, and a fresh diagnostic key. Never copies live keys.
"""
import argparse,copy,http.client,json,os,secrets,socket,statistics,sys,threading,time
from datetime import datetime,timedelta,timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parent;GUI=HERE.parents[1];sys.path.insert(0,str(GUI))
from joint_camera_preparation import PCClockClient,PreparationAuthority,LocalAddressHTTPServer,clock_binding
from joint_camera_control import hardware_module
from live_protocol import load

def summary(rows):
    selected=sorted(r['total_ms'] for r in rows)
    return dict(count=len(rows),p50_ms=statistics.median(selected),p95_ms=selected[int(.95*(len(selected)-1))],
        max_ms=max(selected),long_over_100ms=[r for r in rows if r['total_ms']>100],
        connect_calls=sum(r.get('connect_calls',0) for r in rows))

def server(host):
    old=load(GUI/'runtime/joint/34e96b4d227f488bb3214190089569d1/hardware_handoff.json')
    h={k:copy.deepcopy(old[k]) for k in ('software_package','control_package','software_sha256')}
    now=datetime.now(timezone.utc)
    scope=dict(run_id='CPU_DIAGNOSTIC_NOT_A_NEURAL_RUN',server_session='CPU_ONLY',boot_id='NO_PHYSICAL_BOARD',
        start_utc=now.isoformat(),end_utc=(now+timedelta(seconds=180)).isoformat(),execution_authority='NONE')
    h.update(run_id=scope['run_id'],server_session=scope['server_session'],boot_id=scope['boot_id'],
        listener_id='CPU_HTTP_ONLY',plan_sha256='0'*64,status='CPU_DIAGNOSTIC_NOT_PREPARED',
        pc_authority_endpoint=dict(host=host,port=18793),control_config=dict(control_key=secrets.token_hex(32)))
    a=PreparationAuthority.__new__(PreparationAuthority)
    a.helpers=hardware_module(h,'control2');a.clock=hardware_module(h,'clock').PCClockAuthority()
    a.lock=threading.RLock();a.error=None;a.seen=set();a.config=h['control_config'];a.binding=clock_binding(h,scope,'0'*64)
    h['pc_clock_id']=a.clock.id
    done=threading.Event();observed=[];servers=[]
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            if self.server.keepalive:self.connection.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        def do_POST(self):
            started=time.perf_counter_ns()
            try:
                assert self.path=='/guard', 'CPU_GUARD_ONLY'
                n=int(self.headers.get('Content-Length',0));assert 0<n<4096
                reply=a.dispatch('/guard',json.loads(self.rfile.read(n)));body=json.dumps(reply).encode()
                self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
                observed.append(dict(mode='persistent' if self.server.keepalive else 'fresh',duration_ms=(time.perf_counter_ns()-started)/1e6))
            except Exception as e:
                body=json.dumps(dict(error=str(e))).encode();self.send_response(409);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def log_message(self,*args):pass
    for port,keepalive in ((18793,False),(18794,True)):
        handler=type('GuardHandler',(Handler,),dict(protocol_version='HTTP/1.1' if keepalive else 'HTTP/1.0'))
        srv=LocalAddressHTTPServer((host,port),handler);srv.keepalive=keepalive
        threading.Thread(target=srv.serve_forever,daemon=True).start();servers.append(srv)
    path=HERE/'CPU_HTTP_CONFIG_PRIVATE.json'
    path.write_text(json.dumps(dict(handoff=h,scope=scope,scope_sha256='0'*64,role='CPU_DIAGNOSTIC_ONLY_NO_DEVICE_AUTHORITY')),encoding='utf8')
    print('CPU_GUARD_ONLY_READY '+host,flush=True)
    until=time.monotonic()+100
    try:
        while time.monotonic()<until and not (HERE/'CPU_HTTP_CLIENT_DONE.json').exists():time.sleep(.1)
    finally:
        for srv in servers:srv.shutdown();srv.server_close()
        (HERE/'CPU_HTTP_SERVER_RESULT.json').write_text(json.dumps(dict(status='CPU_ONLY',requests=len(observed),
            max_handler_ms=max((r['duration_ms'] for r in observed),default=0),rows=observed),indent=2),encoding='utf8')

def client():
    config=load(HERE/'CPU_HTTP_CONFIG_PRIVATE.json');base=config['handoff'];all_rows={};current=None;keep=False
    original=http.client.HTTPConnection
    class Measured(original):
        def connect(self):
            t=time.perf_counter_ns()
            try:
                super().connect()
                if keep:self.sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
            finally:
                current['connect_ms']=current.get('connect_ms',0)+(time.perf_counter_ns()-t)/1e6
                current['connect_calls']=current.get('connect_calls',0)+1
        def request(self,*args,**kwargs):
            t=time.perf_counter_ns()
            try:return super().request(*args,**kwargs)
            finally:current['request_inclusive_ms']=(time.perf_counter_ns()-t)/1e6
        def getresponse(self):
            t=time.perf_counter_ns();response=super().getresponse();current['wait_headers_ms']=(time.perf_counter_ns()-t)/1e6
            read=response.read
            def timed_read(*args,**kwargs):
                t=time.perf_counter_ns()
                try:return read(*args,**kwargs)
                finally:current['read_body_ms']=(time.perf_counter_ns()-t)/1e6
            response.read=timed_read;return response
        def close(self):
            if not keep:super().close()
    try:
        for mode in ('fresh','persistent'):
            keep=mode=='persistent';h=copy.deepcopy(base);h['pc_authority_endpoint']['port']=18794 if keep else 18793
            checker=PCClockClient(h,config['scope'],config['scope_sha256']);shared=None;rows=[]
            def factory(*args,**kwargs):
                nonlocal shared
                if not keep:return Measured(*args,**kwargs)
                if shared is None:shared=Measured(*args,**kwargs)
                return shared
            with patch('http.client.HTTPConnection',side_effect=factory):
                for i in range(320):
                    current=dict(ordinal=i+1);t=time.perf_counter_ns();cpu=time.thread_time_ns();checker.check()
                    current.update(total_ms=(time.perf_counter_ns()-t)/1e6,thread_cpu_ms=(time.thread_time_ns()-cpu)/1e6)
                    rows.append(current);time.sleep(.02)
            if shared:original.close(shared)
            all_rows[mode]=dict(summary=summary(rows),rows=rows)
        result=dict(status='PASS_CPU_AUTHENTICATED_HTTP_ONLY',hardware_connections=0,neural_steps=0,
            production_files_modified=False,variants=all_rows,
            limits='Different day and Windows adapter; CPU protocol transport only. Persistent variant is diagnostic, not installed in production.')
    except BaseException as e:
        result=dict(status='FAILED_CPU_HTTP_PROBE',error=str(e),variants=all_rows)
        raise
    finally:
        if 'result' in locals():
            (HERE/'CPU_HTTP_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
            (HERE/'CPU_HTTP_CLIENT_DONE.json').write_text(json.dumps(dict(status=result['status'])),encoding='utf8')
    print(json.dumps({k:({m:v['summary'] for m,v in val.items()} if k=='variants' else val) for k,val in result.items()},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--server');p.add_argument('--client',action='store_true');args=p.parse_args()
    if args.server:server(args.server)
    elif args.client:client()
