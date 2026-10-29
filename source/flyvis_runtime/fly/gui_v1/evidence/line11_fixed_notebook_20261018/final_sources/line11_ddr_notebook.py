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
    require('_line2_pure_fpga_attempt' not in namespace,
            '本内核已经尝试纯FPGA实验；保留内核/DDR和记录，不自动重复加载或重试。')
    origin = entry['pc_origin']
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
    require(m['schema'] == 'flyvis-line2-ddr-fixed-notebook/v1'
            and m['status'] == 'WAITING_FIRST_STEP' and m['steps'] == 485
            and re.fullmatch('[0-9a-f]{32}', m['preparation_id'])
            and re.fullmatch('[0-9a-f]{64}', m['zip_sha256'])
            and 0 < m['zip_bytes'] <= 128000000, '请先启动电脑端“纯FPGA ON60”入口，禁止混用GPU联合会话')
    directory = Path('LINE11_DDR_' + m['preparation_id']).resolve()
    archive = directory.with_suffix('.zip')
    require(not directory.exists() and not archive.exists(), '本次准备已下载或尝试；不自动重试，请保留现场')
    print('纯FPGA：45,669节点，ON60共485步，模型dt=5ms。PC只接收/解码/显示。')
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
        require(config['schema'] == 'flyvis-line2-ddr-preparation/v1'
                and config['preparation_id'] == m['preparation_id'] and config['url'] == origin
                and config['total_steps'] == 485
                and config['release_manifest_sha256'] == entry['release_manifest_sha256']
                and config['plan_manifest_sha256'] == entry['plan_manifest_sha256']
                and config['startup_sha256'] == entry['startup_sha256'], '会话/485步ON60/源码身份不匹配')
        for name, expected in entry['startup_sha256'].items():
            require(hashlib.sha256(z.read(name)).hexdigest() == expected, '板端程序改变：' + name)
        require(hashlib.sha256(z.read('release_manifest.json')).hexdigest() == entry['release_manifest_sha256']
                and hashlib.sha256(z.read('RUN_PLAN.json')).hexdigest() == entry['plan_manifest_sha256'], '模型/固件/输入计划身份改变')
        directory.mkdir()
        z.extractall(directory)
    namespace['_line2_pure_fpga_attempt'] = {'preparation_id':m['preparation_id'], 'directory':str(directory)}
    print('本次准备包已验证。复用原板端入口；完整首步由PC验收后才继续其余484步。')
    previous_argv = sys.argv
    sys.path.insert(0, str(directory))
    try:
        sys.argv = [str(directory/'line11_ddr_board.py'), '--execute', '--exclusive-board-window']
        execute(str(directory/'line11_ddr_board.py'), run_name='__main__')
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


def export_notebook(origin, here=HERE):
    from line11_ddr_bridge import MANIFEST_SHA
    from line11_ddr_plan import STARTUP_FILES, PLAN485_SHA
    root = Path(here)
    pairing = installation(root)
    entry = dict(pc_origin=origin, pairing_key=pairing['pairing_key'],
                 release_manifest_sha256=MANIFEST_SHA, plan_manifest_sha256=PLAN485_SHA,
                 startup_sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in STARTUP_FILES},
                 source=BOARD_SOURCE, source_sha256=hashlib.sha256(BOARD_SOURCE.encode()).hexdigest())
    cell = """# 固定纯FPGA ON60入口；每次相同代码，不复制令牌。
from pathlib import Path
import hashlib, json
line2_entry = json.loads(Path('FlyVis纯FPGA_ON60实验.ipynb').read_text(encoding='utf-8'))['metadata']['flyvis_pure_fpga']
assert hashlib.sha256(line2_entry['source'].encode()).hexdigest() == line2_entry['source_sha256'], 'Notebook程序已改变'
exec(compile(line2_entry['source'], 'FLYVIS_PURE_FPGA_NOTEBOOK', 'exec'), globals(), globals())
run(line2_entry, globals())
"""
    text = ("# FlyVis 纯FPGA · ON60 · 485步\n"
            "此文件与GPU＋FPGA摄像头Notebook不同。全部45,669节点由⑪DDR固件计算；PC用CPU做官方光流解码。\n"
            "电脑先双击“flyvisfpga_4b9b8382.cmd”，手动打开 http://127.0.0.1:8771/#competition。\n"
            "首次上传本Notebook，保持文件名；运行下面唯一代码格，确认独占板卡后输入“准备”。自动领取当次包，先验收首步，再连续484步。\n"
            "模型时间2.425秒，完成后约40秒离线回放；不是60秒摄像头实时实验。当前485步为软件已准备，实板待验。\n"
            "每个PC会话只接受一次实验；失败保留内核、DDR和输出，不重跑、不自动复位。⑦与⑪不能同时占用板卡或8771。\n"
            "本文件含本机私有配对信息，仅供本机和板端使用。软件升级需换新版Notebook。")
    nb = dict(nbformat=4, nbformat_minor=4,
              metadata=dict(kernelspec=dict(display_name='Python 3', language='python', name='python3'),
                            flyvis_pure_fpga=entry),
              cells=[dict(cell_type='markdown', metadata={}, source=text.splitlines(keepends=True)),
                     dict(cell_type='code', metadata={}, execution_count=None, outputs=[], source=cell.splitlines(keepends=True))])
    path = root / NAME
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
    if session.total_steps != 485 or (session.seed.plan_sha or PLAN485_SHA) != PLAN485_SHA:
        raise ValueError('DDR_NOTEBOOK_ONLY_FIXED_ON60_485')
    if session.state != 'WAITING_FIRST_STEP':
        raise ValueError('DDR_NOTEBOOK_PREPARATION_ALREADY_CONSUMED_OR_CLOSED')
    path = session.link_path
    if body.get('op') == 'manifest':
        raw = path.read_bytes()
        if not 0 < len(raw) <= MAX_ZIP:
            raise ValueError('DDR_NOTEBOOK_PACKAGE_SIZE')
        return dict(schema='flyvis-line2-ddr-fixed-notebook/v1', status=session.state,
                    steps=485, preparation_id=session.preparation_id,
                    zip_sha256=hashlib.sha256(raw).hexdigest(), zip_bytes=len(raw))
    if body.get('op') == 'package' and body.get('preparation_id') == session.preparation_id:
        return path.read_bytes()
    raise ValueError('DDR_NOTEBOOK_PACKAGE_REQUEST_MISMATCH')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export a fixed Notebook only; no listeners/devices')
    parser.add_argument('--pc-origin', default='http://192.168.2.89:8771')
    args = parser.parse_args()
    print('EXPORTED_FIXED_PURE_FPGA_NOTEBOOK ' + str(export_notebook(args.pc_origin)))
