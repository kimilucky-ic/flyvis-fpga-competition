"""PC-only bounded rounds. Never imports PYNQ or sends board commands."""
from pathlib import Path
import ast,base64,hashlib,io,json,secrets,threading,uuid,zipfile
from live_protocol import atomic,canonical
import motion_trial
NOTEBOOK='LINE11_OFFICIAL_LIVE_V261_60S.ipynb'
BOARD_BASE='/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_V261_60S'

def admission(app):
    s=app.store;f=s.final;c=s.camera_close;a=app.audit_result;n=len(s.meta)
    if not f or not n:return False,'本轮尚未完成；使用本轮Notebook，不重复创建。'
    if f.get('status')!='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING' or f.get('error') is not None:return False,'本轮异常，保留内核和记录，先核查。'
    if not c or c.get('status')!='CLOSED' or c.get('camera_closed') is not True or c.get('error') is not None:return False,'相机尚未确认正常关闭。'
    if app.audit_running or not a or a.get('status')!='PASS_ALL_SAVED_STATES':return False,'等待全部状态验收通过。'
    if a.get('steps')!=n or a.get('state_words_compared')!=n*45669 or a.get('mismatch_words')!=0:return False,'验收计数不一致。'
    for obj in (f,c):
        if obj.get('session_id')!=app.config['session_id'] or obj.get('completed_steps')!=n or obj.get('packet_sha256')!=s.digests:return False,'完成记录身份不一致。'
        if obj.get('run_id')!=s.meta[0]['run_id'] or obj.get('boot_id')!=s.meta[0]['boot_id']:return False,'运行身份不一致。'
    if f.get('hardware_completed_steps')!=n or f.get('duration',{}).get('stop_reason')!='DURATION_REACHED':return False,'神经步尚未正常结束。'
    after=f.get('context',{}).get('NEURAL_AFTER.json',{})
    if after!={'0x10':38,'0x14':n,'0x18':0,'0x24':0,'0x4c':n,'0x50':0}:return False,'最终状态或DDR释放尚未完成。'
    return True,'上一轮相机已关闭、全部状态验收通过，可以创建新一轮。'

def notebook(root,config):
    """Same guarded cell and firmware, unique board directory per session."""
    root=Path(root);config=json.loads(canonical(config));sid=config['session_id'];base=BOARD_BASE+'/SESSION_'+sid
    files={p.name:p.read_bytes() for p in sorted((root/'bundle').iterdir()) if p.is_file() and p.name!='release_manifest.json'}
    raw=files['live_board.py'].decode('utf-8');assert raw.count("base=Path('"+BOARD_BASE+"')")==1
    files['live_board.py']=raw.replace("base=Path('"+BOARD_BASE+"')","base=Path('"+base+"')").encode('utf-8')
    manifest={n:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for n,v in files.items()}
    files['release_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for n,v in sorted(files.items()):
            item=zipfile.ZipInfo(n,(2026,10,26,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,v)
    payload=buf.getvalue();digest=hashlib.sha256(payload).hexdigest();hashes={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}
    nb=json.loads((root/NOTEBOOK).read_text(encoding='utf-8'));code=''.join(nb['cells'][1]['source']);lines=code.splitlines();replaced=[]
    for i,line in enumerate(lines):
        if line.startswith('_raw='):lines[i]='_raw=base64.b64decode(%r)'%base64.b64encode(payload).decode();replaced.append('raw')
        elif line.startswith('if hashlib.sha256(_raw)'):lines[i]="if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')"%digest;replaced.append('digest')
        elif line.startswith('_hashes='):lines[i]='_hashes=%r'%hashes;replaced.append('hashes')
        elif line.startswith('_root='):lines[i]="_root=Path(%r)/('package_'+%r)"%(base,digest[:12]);replaced.append('root')
        elif line.startswith('_config='):lines[i]='_config=%r'%config;replaced.append('config')
    assert set(replaced)=={'raw','digest','hashes','root','config'}
    code='\n'.join(lines)+'\n';ast.parse(code,feature_version=(3,8));nb['cells'][1].update(source=code.splitlines(True),outputs=[],execution_count=None)
    nb['cells'][0]['source']=("# 新一轮60秒 · 会话 "+sid[:8]+"\n\n上一轮相机正常关闭且全状态验收通过后，先关闭上一轮Notebook内核，释放其保留的缓冲区。本轮使用独立新内核，不能重复运行旧Notebook。电脑页面应显示会话 "+sid[:8]+"，已接收0步。\n\n运行下方唯一代码格，确认时输入 **运行2026.1铺满版60秒**。这才会加载固件、初始化相机并从初始神经状态运行新60秒；不是延续上一轮状态。每步80×48原始画面、721项输入和全部45669状态均保存。实验内容由你自行安排。异常保留内核与缓冲区，不重跑、不复位。\n\n结束后等待板端 NORMAL_CAMERA_CLOSED 和电脑 PASS_ALL_SAVED_STATES，再点击电脑页面的“开始下一轮60秒”。\n").splitlines(True)
    return json.dumps(nb,ensure_ascii=False).encode('utf-8'),base

class Rounds:
    def __init__(self,root,factory):
        self.root=Path(root);self.factory=factory;self.lock=threading.RLock();self.pc=self.root/'pc';self.pointer=self.pc/'ACTIVE_ROUND.json'
        self.current=self.load()
    def load(self):
        if not self.pointer.exists():return self.factory(json.loads((self.pc/'session.json').read_text()),self.pc/'records')
        receipt=json.loads(self.pointer.read_text());sid=receipt['session_id'];p=self.directory(sid);config=json.loads((p/'session.json').read_text())
        if config['session_id']!=sid or hashlib.sha256((p/NOTEBOOK).read_bytes()).hexdigest()!=receipt['notebook_sha256']:raise ValueError('Active round identity mismatch')
        return self.factory(config,p/'records')
    def directory(self,sid):
        if not isinstance(sid,str) or len(sid)!=32 or any(c not in '0123456789abcdef' for c in sid):raise ValueError('Invalid session')
        return self.pc/'rounds'/sid
    def notebook_path(self,app):
        if app.store.path==self.pc/'records':return self.root/NOTEBOOK
        return self.directory(app.config['session_id'])/NOTEBOOK
    def advance(self,expected,mode='capture'):
        if mode!='capture':raise ValueError('统一60秒入口不接受实验模式选择')
        with self.lock:
            old=self.current;sid=old.config['session_id']
            # Repeated request after switching returns the same successor, never another.
            if expected!=sid:
                if self.pointer.exists():
                    receipt=json.loads(self.pointer.read_text())
                    if receipt.get('parent_session_id')==expected and receipt['session_id']==sid and motion_trial.condition(old.config)==mode:return dict(session_id=sid,duplicate=True,notebook='/notebook')
                raise ValueError('页面会话已变更，请刷新；未创建新一轮。')
            allowed,reason=admission(old)
            if not allowed:raise ValueError(reason)
            # Deterministic successor avoids duplicate creation across retries/restarts.
            next_id=uuid.uuid5(uuid.NAMESPACE_URL,'line11-next:'+sid).hex;p=self.directory(next_id);p.mkdir(parents=True,exist_ok=True)
            config_path=p/'session.json'
            if config_path.exists():config=json.loads(config_path.read_text())
            else:
                config=dict(old.config,session_id=next_id,token=secrets.token_hex(32),motion_condition=mode);atomic(config_path,canonical(config))
            if config['session_id']!=next_id or any(config[k]!=old.config[k] for k in old.config if k not in ('session_id','token','motion_condition')):raise ValueError('Pending successor configuration mismatch')
            if motion_trial.condition(config)!=mode:raise ValueError('已准备另一种实验，不能覆盖；先核查当前会话')
            nb,base=notebook(self.root,config);nbpath=p/NOTEBOOK
            if nbpath.exists():
                if nbpath.read_bytes()!=nb:raise ValueError('Pending Notebook differs; keep evidence')
            else:atomic(nbpath,nb)
            fresh=self.factory(config,p/'records')
            if fresh.store.meta or fresh.store.final:raise ValueError('Successor already contains records')
            receipt=dict(schema='line11-active-round/v1',session_id=next_id,parent_session_id=sid,previous_records=str(old.store.path),notebook_sha256=hashlib.sha256(nb).hexdigest(),board_directory=base,board_actions=0)
            atomic(p/'ROUND.json',canonical(receipt));atomic(self.pointer,canonical(receipt));self.current=fresh
            return dict(session_id=next_id,duplicate=False,notebook='/notebook')
