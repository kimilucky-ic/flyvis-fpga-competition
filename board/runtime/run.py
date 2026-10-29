"""Portable PC entry for the accepted full-network FPGA camera runtime."""
from pathlib import Path
import argparse,importlib,ipaddress,json,secrets,socket,sys,uuid,urllib.request,urllib.error,webbrowser
ROOT=Path(__file__).resolve().parent
APP=ROOT/'app'

def dependencies():
    for name in ('numpy','PIL','psutil'):
        importlib.import_module(name)
    sys.path[:0]=[str(APP/'pc'),str(APP/'bundle')]
    import stream_audit  # Preflight exactly the same module used by the child.

def configure(ip,port):
    address=ipaddress.ip_address(ip)
    if address.version!=4 or address.is_loopback or address.is_unspecified or address.is_multicast:
        raise ValueError('Please use a PC IPv4 address reachable from the board.')
    if not 1024<=port<=65535:raise ValueError('Port must be between1024 and65535.')
    path=APP/'pc/session.json'
    if path.exists():
        cfg=json.loads(path.read_text('utf8'))
        if cfg['pc_url']!=f'http://{ip}:{port}':
            raise ValueError('This copy already has a session at another address. Keep its records; extract a fresh copy for the new address.')
        return cfg
    import hashlib
    from live_protocol import atomic,canonical
    from round_sessions import notebook,NOTEBOOK
    info=json.loads((APP/'bundle/release_info.json').read_text('utf8'))
    cfg=dict(schema='line11-live-session/v1',session_id=uuid.uuid4().hex,token=secrets.token_hex(32),
        pc_url=f'http://{ip}:{port}',port=port,input_mapping='direct-grey-center-square-area/v2',
        crop_roi=dict(left=16,top=0,width=48,height=48),camera_width=80,camera_height=48,
        transfer_mode='live_compact',motion_condition='capture',max_steps=4096,ring_slots=64,
        minimum_period_s=0.,duration_s=60.,adaptive_memory=False,automatic_archives=False,
        diagnostics=False,camera_diagnostics=False,bit_sha256=info['bit_sha256'],hwh_sha256=info['hwh_sha256'],
        initial_state_sha256=hashlib.sha256((APP/'bundle/initial_state.bin').read_bytes()).hexdigest())
    # Reuse the existing guarded Notebook generator and preserve board-side checks.
    atomic(APP/NOTEBOOK,(APP/'notebook_template.json').read_bytes())
    payload,_=notebook(APP,cfg)
    atomic(APP/NOTEBOOK,payload)
    atomic(path,canonical(cfg))
    return cfg

def main():
    ap=argparse.ArgumentParser(description='FlyVis full-network FPGA camera reproduction')
    ap.add_argument('--ip');ap.add_argument('--port',type=int,default=8798)
    ap.add_argument('--no-browser',action='store_true');ap.add_argument('--prepare-only',action='store_true')
    ap.add_argument('--check-only',action='store_true');args=ap.parse_args()
    from selfcheck import verify,oracle_check
    verify(ROOT);dependencies()
    if args.check_only:
        print(json.dumps(oracle_check(ROOT),ensure_ascii=False,indent=2));return
    path=APP/'pc/session.json'
    if path.exists():
        cfg=json.loads(path.read_text('utf8'))
        if args.ip:configure(args.ip,args.port)
    else:
        if args.ip:ip=args.ip
        else:
            import psutil
            candidates=sorted({a.address for values in psutil.net_if_addrs().values() for a in values
                if a.family==socket.AF_INET and not a.address.startswith(('127.','169.254.'))})
            print('本机IPv4：'+', '.join(candidates))
            ip=input('首次设置：请输入板卡能访问的本机IPv4：').strip()
        cfg=configure(ip,args.port)
    if args.prepare_only:
        print('PASS_PREPARED_FRESH_SESSION_NO_BOARD_ACCESS');return
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(f"http://127.0.0.1:{cfg['port']}/status",timeout=2) as r:status=json.load(r)
    except urllib.error.HTTPError:raise RuntimeError('The configured port is occupied; keep the existing program and use another port in a fresh package copy.')
    except urllib.error.URLError:status=None
    if status is not None:
        valid={cfg['session_id']}
        pointer=APP/'pc/ACTIVE_ROUND.json'
        if pointer.exists():valid.add(json.loads(pointer.read_text())['session_id'])
        if status.get('application')!='line11-live-v261' or status.get('session_id') not in valid:
            raise RuntimeError('The configured port belongs to another receiver. Close its PC receiving window or use a different port in a fresh package copy.')
        if not args.no_browser:webbrowser.open(f"http://127.0.0.1:{cfg['port']}")
        print('已打开本复现包的接收页面。');return
    print('依赖及固件检查通过；PC地址：'+cfg['pc_url'])
    print('保持此窗口运行，在页面下载固定入口Notebook，上传板卡后由操作者确认运行。')
    import live_server
    sys.argv=[str(APP/'pc/live_server.py')]+(['--no-browser'] if args.no_browser else [])
    live_server.main()

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:pass
    except Exception as exc:
        print('启动停止：'+str(exc),file=sys.stderr);raise SystemExit(1)
