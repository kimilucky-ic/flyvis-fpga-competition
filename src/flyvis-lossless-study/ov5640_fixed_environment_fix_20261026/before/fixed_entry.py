"""Reusable operator Notebook; no hardware operation on this PC."""
import base64,hashlib,hmac,json,secrets
from pathlib import Path
from live_protocol import atomic,canonical
NAME='LINE11_START_60S.ipynb'
CLIENT='''import base64,hashlib,hmac,json,secrets,urllib.request
from pathlib import Path
def fetch_round(url,key):
    nonce=secrets.token_hex(32)
    req=urllib.request.Request(url+'/runner?nonce='+nonce,headers={'Authorization':'Bearer '+key})
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req,timeout=30) as response:
        raw=response.read(12*1024*1024+1)
    if len(raw)>12*1024*1024:raise RuntimeError('Launcher response exceeds bound; no LOAD')
    data=json.loads(raw)
    signed=(nonce+'|'+data['session_id']+'|'+data['sha256']).encode()
    expected=hmac.new(key.encode(),signed,hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,data['signature']):raise RuntimeError('Launcher signature mismatch; no LOAD')
    payload=base64.b64decode(data['notebook'],validate=True)
    if hashlib.sha256(payload).hexdigest()!=data['sha256']:raise RuntimeError('Notebook digest mismatch; no LOAD')
    nb=json.loads(payload)
    cells=[c for c in nb['cells'] if c['cell_type']=='code']
    if len(cells)!=1:raise RuntimeError('Expected one guarded code cell; no LOAD')
    return data['session_id'],payload,''.join(cells[0]['source'])
'''
def prepare(root):
    root=Path(root);pc=root/'pc';path=pc/'FIXED_ENTRY_KEY.json'
    if path.exists():key=json.loads(path.read_text())['key']
    else:
        key=secrets.token_hex(32);atomic(path,canonical({'key':key}))
    config=json.loads((pc/'session.json').read_text())
    code="if globals().get('_LINE11_FIXED_USED',False):raise RuntimeError('Restart kernel for a new round; do not repeat this cell')\n_LINE11_FIXED_USED=True\n"+CLIENT
    code+="if not Path('/proc/device-tree/model').exists():raise RuntimeError('Board-only entry; no LOAD')\n"
    code+="_sid,_payload,_code=fetch_round(%r,%r)\n"%(config['pc_url'],key)
    code+="_saved=Path('/home/xilinx/jupyter_notebooks/LINE11_FIXED_RECEIPTS')/_sid\n_saved.mkdir(parents=True,exist_ok=True)\n"
    code+="_receipt=_saved/'received.ipynb'\nif _receipt.exists() and _receipt.read_bytes()!=_payload:raise RuntimeError('Saved Notebook differs; no LOAD')\n_receipt.write_bytes(_payload)\n"
    code+="print('LINE11_FIXED_SESSION',_sid[:8],flush=True)\nexec(compile(_code,'received_'+_sid+'.ipynb','exec'),globals())\n"
    nb={'nbformat':4,'nbformat_minor':4,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'cells':[
        {'cell_type':'markdown','metadata':{},'source':['# FlyVis固定60秒入口\n','只需上传本文件一次。电脑保持接收窗口运行。上一轮相机正常关闭且全状态验收通过后，电脑页面点击“开始下一轮60秒”。\n','本文件选择 **Kernel → Restart & Run All（重启内核并运行全部）**，领取当前轮次，再输入 **运行2026.1铺满版60秒**。无需重新下载或上传Notebook。每轮从原始初态开始。\n','首次使用前关闭之前已正常结束的旧Notebook内核。异常未关闭的运行不能用重启来恢复，应保留内核与缓冲区核查。\n','领取失败不加载固件；本入口不自动创建下一轮、不自动操作板卡。']},
        {'cell_type':'code','metadata':{},'source':code.splitlines(True),'outputs':[],'execution_count':None}]}
    atomic(root/NAME,json.dumps(nb,ensure_ascii=False).encode())
    return key

def response(rounds,key,nonce):
    if len(nonce)!=64 or any(c not in '0123456789abcdef' for c in nonce):raise ValueError('Invalid request nonce')
    with rounds.lock:
        app=rounds.current
        with app.store.lock:
            if app.store.meta or app.store.final or app.store.camera_close:raise ValueError('Current round already has records; prepare next round after PASS and CLOSED')
            payload=rounds.notebook_path(app).read_bytes();sid=app.config['session_id']
        digest=hashlib.sha256(payload).hexdigest()
        signature=hmac.new(key.encode(),(nonce+'|'+sid+'|'+digest).encode(),hashlib.sha256).hexdigest()
        return dict(session_id=sid,sha256=digest,signature=signature,notebook=base64.b64encode(payload).decode())
