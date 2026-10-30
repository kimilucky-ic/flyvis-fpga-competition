"""Fixed operator Notebook for the existing ON60 DDR entry; no device operations.

The original GUI serves its current, private preparation ZIP after pairing.
Only the human-run Notebook calls the unchanged board entrypoint.
"""
import argparse
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import uuid

HERE = Path(__file__).resolve().parent
NAME = "FlyVis纯FPGA_ON60实验.ipynb"
ROUTE = "/api/full-pl-stream/notebook-bundle"
MAX_ZIP = 128_000_000

BOARD_SOURCE = r'''import hashlib, json, re, runpy, sys, urllib.error, urllib.request, zipfile
from pathlib import Path

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(262144), b''):
            h.update(chunk)
    return h.hexdigest()

def run(entry, namespace, transport=None, ask=None, execute=None):
    attempt=namespace.get('_line2_pure_fpga_attempt')
    previous=namespace.get('_line2_completed_owner')
    require(attempt is None or (attempt.get('status')=='COMPLETED_AUDITED'
            and isinstance(previous,dict) and previous.get('run_id')==attempt.get('preparation_id')
            and not previous.get('retired')), '本内核已经尝试且未正常收尾；保留内核/DDR和记录，不自动重复加载或重试。')
    origin = entry['pc_origin']
    camera_live = entry.get('camera_live', False)
    capacity = 485
    require(re.fullmatch(r'http://192\.168\.2\.\d{1,3}:\d{1,5}', origin), '仅允许本机板卡网段的PC入口')
    # Direct LAN request: do not send the private pairing through system proxies.
    transport = transport or urllib.request.build_opener(urllib.request.ProxyHandler({})).open
    ask = ask or input
    execute = execute or runpy.run_path
    def request(body):
        req = urllib.request.Request(origin + '/api/full-pl-stream/notebook-bundle',
            data=json.dumps(body).encode(), headers={'Content-Type':'application/json',
            'Authorization':'Bearer ' + entry['pairing_key']})
        try:
            return transport(req, timeout=120)
        except urllib.error.HTTPError as error:
            try:
                detail = json.loads(error.read(4096)).get('error', 'HTTP ' + str(error.code))
            except (ValueError, TypeError):
                detail = 'HTTP ' + str(error.code)
            raise RuntimeError('电脑未提供可用的纯FPGA准备包；请打开纯FPGA启动入口。' + detail) from None
        except urllib.error.URLError as error:
            raise RuntimeError('无法连接电脑纯FPGA入口；先打开“flyvisfpga_4b9b8382.cmd”，检查网线。' + str(error.reason)) from None
    with request({'op':'manifest'}) as response:
        raw = response.read(8193)
    require(len(raw) <= 8192, 'PC准备描述超过上限')
    m = json.loads(raw)
    if entry.get('selectable_input'):
        camera_live=bool(m.get('camera_live'))
    require(m['schema'] == 'flyvis-line2-ddr-fixed-notebook/v1'
            and m['status'] == 'WAITING_FIRST_STEP' and m['steps'] == capacity
            and m.get('camera_live', False) == camera_live
            and re.fullmatch('[0-9a-f]{32}', m['preparation_id'])
            and re.fullmatch('[0-9a-f]{64}', m['zip_sha256'])
            and 0 < m['zip_bytes'] <= 128000000, '请先启动电脑端“纯FPGA ON60”入口，禁止混用GPU联合会话')
    require(attempt is None or m['preparation_id']!=attempt['preparation_id'],'上一实验已经完成；先在网页选择并打开下一实验，不重复本次运行。')
    directory = Path('LINE11_DDR_' + m['preparation_id']).resolve()
    archive = directory.with_suffix('.zip')
    require(not directory.exists() and not archive.exists(), '本次准备已下载或尝试；不自动重试，请保留现场')
    print('本次输入：'+str(m.get('source_kind','ON60'))+' / '+str(m.get('condition_id',''))+'；同一固定Notebook。')
    print('纯FPGA：45,669节点，' + ('固定科学输入485步；模型dt=5ms，按计算推进。' if m.get('source_kind')=='controlled_animation' else '当次摄像头实际60秒，默认最多8步/实际秒；485槽约87.2MiB，模型dt=5ms。' if camera_live else 'ON60共485步，模型dt=5ms。') + 'PC仅采集、转换、独立审核、解码和显示。')
    require(ask('确认板卡已独占释放，允许加载本次DDR固件和分配内存；输入“准备”：').strip() == '准备',
            '已取消；没有加载、复位或分配内存')
    with request({'op':'package', 'preparation_id':m['preparation_id']}) as response:
        with archive.open('xb') as output:
            count = 0
            while True:
                chunk = response.read(262144)
                if not chunk:
                    break
                count += len(chunk)
                require(count <= m['zip_bytes'], '准备包超过描述大小')
                output.write(chunk)
    require(count == m['zip_bytes'] and sha_file(archive) == m['zip_sha256'], '准备包不完整或SHA错误')
    with zipfile.ZipFile(archive) as z:
        rows = z.infolist()
        require(len(rows) < 40 and sum(r.file_size for r in rows) < 128000000
                and len({r.filename for r in rows}) == len(rows), '准备包数量/大小/重名错误')
        require(all(Path(r.filename).name == r.filename and '\\' not in r.filename
                    and not r.is_dir() and not r.flag_bits & 1
                    and (r.external_attr >> 16) & 0o170000 != 0o120000 for r in rows), '不安全的ZIP路径')
        config = json.loads(z.read('PREPARATION.json'))
        require(config['schema'] == ('flyvis-line2-ddr-live-camera/v1' if camera_live else 'flyvis-line2-ddr-preparation/v1')
                and config['preparation_id'] == m['preparation_id'] and config['url'] == origin
                and config['total_steps'] == capacity
                and config['release_manifest_sha256'] == entry['release_manifest_sha256']
                and (camera_live or config['plan_manifest_sha256'] == entry['plan_manifest_sha256'])
                and config['startup_sha256'] == (entry['startup_sha256'] if camera_live else {n:v for n,v in entry['startup_sha256'].items() if n!='line11_live_camera_board.py'}), '会话/485步ON60/源码身份不匹配')
        names=entry['startup_sha256'] if camera_live else {n:v for n,v in entry['startup_sha256'].items() if n!='line11_live_camera_board.py'}
        require(set(config['startup_sha256'])==set(names),'板端程序集合不匹配')
        for name, expected in names.items():
            require(hashlib.sha256(z.read(name)).hexdigest() == expected, '板端程序改变：' + name)
        require(hashlib.sha256(z.read('release_manifest.json')).hexdigest() == entry['release_manifest_sha256']
                and (camera_live or hashlib.sha256(z.read('RUN_PLAN.json')).hexdigest() == entry['plan_manifest_sha256']), '模型/固件/输入计划身份改变')
        directory.mkdir()
        z.extractall(directory)
    namespace['_line2_pure_fpga_attempt'] = {'preparation_id':m['preparation_id'], 'directory':str(directory), 'status':'ATTEMPTED_KEEP_ON_FAILURE'}
    print('本次准备包已验证；完整首步由PC验收后继续。' + ('本次固定科学输入485步；等待实验台开始。' if m.get('source_kind')=='controlled_animation' else '本次真实摄像头60秒；按实验台提示开始。' if camera_live else '本次固定ON60共485步。'))
    board_entry = 'line11_live_camera_board.py' if camera_live else 'line11_ddr_board.py'
    previous_argv = sys.argv
    sys.path.insert(0, str(directory))
    try:
        sys.argv = [str(directory/board_entry), '--execute', '--exclusive-board-window']
        # Fresh source paths for the next package; never reuse cached modules
        # whose ROOT still points at a previous preparation directory.
        if previous is not None:
            old_directory=Path(attempt['directory']).resolve()
            for name,module in list(sys.modules.items()):
                filename=getattr(module,'__file__',None)
                if filename and Path(filename).resolve().parent==old_directory:
                    del sys.modules[name]
            result=execute(str(directory/board_entry),run_name='__main__',
                           init_globals={'LINE2_PREVIOUS_COMPLETED_OWNER':previous})
        else:
            result=execute(str(directory/board_entry),run_name='__main__')
        owner=result.get('LINE2_COMPLETED_OWNER') if isinstance(result,dict) else None
        if owner is not None:
            require(owner.get('schema')=='line2-normal-owned-ddr/v1' and owner.get('run_id')==m['preparation_id']
                    and owner.get('proof',{}).get('status')=='NORMAL_RETURN_ACKED','本次正常收尾身份不匹配；保留现场')
            namespace['_line2_completed_owner']=owner
            namespace['_line2_pure_fpga_attempt']['status']='COMPLETED_AUDITED'
    finally:
        sys.argv = previous_argv
'''


def installation(here=HERE):
    path = Path(here) / 'runtime/line11_ddr_notebook/INSTALLATION_PRIVATE.json'
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8') as f:
            json.dump(dict(installation_id=uuid.uuid4().hex, pairing_key=secrets.token_hex(32)), f)
    value = json.loads(path.read_text(encoding='utf-8'))
    if len(bytes.fromhex(value['pairing_key'])) != 32:
        raise ValueError('DDR_NOTEBOOK_PAIRING_INVALID')
    return value


def export_notebook(origin, here=HERE, *, camera_live=False,selectable_input=False):
    from line11_ddr_bridge import MANIFEST_SHA
    from line11_ddr_plan import STARTUP_FILES, PLAN485_SHA
    root = Path(here)
    pairing = installation(root)
    startup_files=STARTUP_FILES
    name=NAME
    if camera_live:
        startup_files=STARTUP_FILES+('line11_live_camera_board.py',)
        name='FlyVis纯FPGA摄像头60秒.ipynb'
    if selectable_input:startup_files=STARTUP_FILES+('line11_live_camera_board.py',)
    entry = dict(selectable_input=selectable_input,pc_origin=origin, pairing_key=pairing['pairing_key'],camera_live=camera_live,
                 release_manifest_sha256=MANIFEST_SHA, plan_manifest_sha256=PLAN485_SHA,
                 startup_sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in startup_files},
                 source=BOARD_SOURCE, source_sha256=hashlib.sha256(BOARD_SOURCE.encode()).hexdigest())
    cell = """# 固定纯FPGA ON60入口；每次相同代码，不复制令牌。
from pathlib import Path
import hashlib, json
line2_entry = json.loads(Path('FlyVis纯FPGA_ON60实验.ipynb').read_text(encoding='utf-8'))['metadata']['flyvis_pure_fpga']
assert hashlib.sha256(line2_entry['source'].encode()).hexdigest() == line2_entry['source_sha256'], 'Notebook程序已改变'
exec(compile(line2_entry['source'], 'FLYVIS_PURE_FPGA_NOTEBOOK', 'exec'), globals(), globals())
run(line2_entry, globals())
"""
    if camera_live:cell=cell.replace(NAME,name).replace('固定纯FPGA ON60入口','固定纯FPGA真实摄像头60秒入口')
    text = ("# FlyVis 纯FPGA · ON60 · 485步\n"
            "此文件与GPU＋FPGA摄像头Notebook不同。全部45,669节点由⑪DDR固件计算；PC用CPU做官方光流解码。\n"
            "电脑先双击“flyvisfpga_4b9b8382.cmd”，手动打开 http://127.0.0.1:8771/#competition。\n"
            "首次上传本Notebook，保持文件名；运行下面唯一代码格，确认独占板卡后输入“准备”。自动领取当次包，先验收首步，再连续484步。\n"
            "模型时间2.425秒，完成后约40秒离线回放；不是60秒摄像头实时实验。当前485步为软件已准备，实板待验。\n"
            "每个PC会话只接受一次实验；失败保留内核、DDR和输出，不重跑、不自动复位。⑦与⑪不能同时占用板卡或8771。\n"
            "本文件含本机私有配对信息，仅供本机和板端使用。软件升级需换新版Notebook。")
    if camera_live:
        text=("# FlyVis 纯FPGA · 真实摄像头 · 实际60秒\n"
              "电脑先双击“flyvisfpga60_4da53e0f.cmd”，手动打开原8771页面。仅此Notebook对应持续摄像头，ON60文件保留。\n"
              "首次上传一次并保留文件名；板卡独占释放后运行唯一格，输入“准备”。同一次原⑪DDR固件加载与初始化，完整首步PC验收后持续使用PL旧态反馈。\n"
              "复用原Windows摄像头、官方BoxEye和最新帧保持；全部45,669神经元由FPGA计算。PC仅采集/转换/独立CPU审核/官方光流解码/显示，没有GPU神经计算。\n"
              "实际60秒由首个输入发出开始，在完整已发布快照边界结束；加载与后审核另计。模型仍5ms一步，模型时间=实际步数×5ms。\n"
              "默认最多8步/实际秒；沿用485个不可覆盖DDR槽（91,381,760字节，约87.2MiB）。这是展示实验档，不是FPGA吞吐上限。最多480步对应2.4秒模型时间，实际摄像头持续60秒。现场CMA可用容量未测，不足会在加载前停止。\n"
              "本次为软件准备，60秒实板、采集FPS、延迟、停止和重开尚待人工验证。失败保留内核与DDR，不自动复位/重试。\n"
              "文件含本机私有配对信息；不公开。")
    if selectable_input:
        text=('# FlyVis 纯FPGA · 摄像头 / 28条件固定实验\n'
              '先在原实验台同一选择区选择输入和纯FPGA后端，然后打开本文件运行唯一代码格，输入“准备”。\n'
              '只部署本文件一次；以后更换条件不改代码。初始化后本格等待实验台“开始”，不要重复运行。摄像头实际60秒；固定实验485个5ms模型步。\n'
              '完整网络由PL递推，PC独立核验严格FP32并用官方DecoderGAVP解码；GPU结果不充当逐位参考。\n'
              '正常结束显示 NORMAL_END_READY_FOR_NEXT 后，可在网页打开下一条件，再运行同一格、输入“准备”；无需关闭FlyVis或本内核。新身份人工准备时才加载新固件并交接旧DDR。\n'
              '仅同一纯FPGA路径支持此正常交接；切换后端仍需独占释放。失败/IN_DOUBT或审核未完成保留现场，不自动复位重试。\n'
              '软件接口测试不等于本次条件已经上板。文件含本机私有配对，不公开。')
    nb = dict(nbformat=4, nbformat_minor=4,
              metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
                            flyvis_pure_fpga=entry),
              cells=[dict(cell_type='markdown', metadata={}, source=text.splitlines(keepends=True)),
                     dict(cell_type='code', metadata={}, execution_count=None, outputs=[], source=cell.splitlines(keepends=True))])
    path = root / name
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def notebook_bundle(session, authorization, body, here=HERE):
    """Only serve current, unconsumed fixed ON60 preparation; never touch devices."""
    pair = installation(here)
    if not isinstance(authorization, str) or not hmac.compare_digest(authorization, 'Bearer ' + pair['pairing_key']):
        raise ValueError('DDR_NOTEBOOK_UNAUTHORIZED')
    if session is None or not hasattr(session, 'authenticate_preparation'):
        raise ValueError('DDR_NOTEBOOK_START_PURE_FPGA_PC_ENTRY_FIRST')
    from line11_ddr_plan import PLAN485_SHA
    camera_live=bool(getattr(session,'camera_live',False))
    if camera_live:
        if session.total_steps!=485:raise ValueError('DDR_NOTEBOOK_CAMERA_CAPACITY')
    elif session.total_steps != 485 or (session.seed.plan_sha or PLAN485_SHA) != PLAN485_SHA:
        raise ValueError('DDR_NOTEBOOK_ONLY_FIXED_ON60_485')
    if session.state != 'WAITING_FIRST_STEP':
        raise ValueError('DDR_NOTEBOOK_PREPARATION_ALREADY_CONSUMED_OR_CLOSED')
    path = session.link_path
    if body.get('op') == 'manifest':
        raw = path.read_bytes()
        if not 0 < len(raw) <= MAX_ZIP:
            raise ValueError('DDR_NOTEBOOK_PACKAGE_SIZE')
        return dict(schema='flyvis-line2-ddr-fixed-notebook/v1', status=session.state,
                    steps=session.total_steps,camera_live=camera_live,preparation_id=session.preparation_id,
                    zip_sha256=hashlib.sha256(raw).hexdigest(), zip_bytes=len(raw),
                    source_kind=getattr(session.seed,'plan',{}).get('input_kind'),condition_id=getattr(session.seed,'plan',{}).get('condition_id'))
    if body.get('op') == 'package' and body.get('preparation_id') == session.preparation_id:
        return path.read_bytes()
    raise ValueError('DDR_NOTEBOOK_PACKAGE_REQUEST_MISMATCH')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export a fixed Notebook only; no listeners/devices')
    parser.add_argument('--pc-origin', default='http://192.168.2.89:8771')
    parser.add_argument('--camera-live',action='store_true')
    args = parser.parse_args()
    print('EXPORTED_FIXED_PURE_FPGA_NOTEBOOK ' + str(export_notebook(args.pc_origin,camera_live=args.camera_live)))
