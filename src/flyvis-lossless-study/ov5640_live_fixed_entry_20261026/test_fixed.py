from pathlib import Path
import ast,copy,hashlib,json,sys,threading,types,urllib.request,urllib.error
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
import fixed_entry
from live_server import App,make_server
from round_sessions import notebook
T=E/'cpu_r2';T.mkdir(exist_ok=False);(T/'pc').mkdir()
config=json.loads((P/'pc/session.json').read_text());(T/'pc/session.json').write_text(json.dumps(config))
ptr=json.loads((P/'pc/ACTIVE_ROUND.json').read_text());source=P/'pc/rounds'/ptr['session_id'];current=json.loads((source/'session.json').read_text());nbpath=source/'LINE11_OFFICIAL_LIVE_V261_60S.ipynb'
a=App(current,T/'records');r=types.SimpleNamespace(root=T,current=a,lock=threading.RLock(),notebook_path=lambda app:nbpath)
srv=make_server(a,'127.0.0.1',0,r);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(srv.server_address[1]);key=json.loads((T/'pc/FIXED_ENTRY_KEY.json').read_text())['key']
ns={};exec(fixed_entry.CLIENT,ns);fetch=ns['fetch_round'];op=urllib.request.build_opener(urllib.request.ProxyHandler({}));neg=[]
def fails(label,fn):
 try:fn()
 except Exception:neg.append(label)
 else:raise AssertionError(label+' accepted')
try:
 sid,payload,code=fetch(url,key);assert sid==current['session_id'] and payload==nbpath.read_bytes();ast.parse(code,feature_version=(3,8))
 assert code==''.join(json.loads(payload)['cells'][1]['source'])
 fixed=(T/fixed_entry.NAME).read_bytes();key2=fixed_entry.prepare(T);assert key2==key and (T/fixed_entry.NAME).read_bytes()==fixed
 with op.open(url+'/fixed-notebook') as res:assert res.read()==fixed
 fails('wrong credential',lambda:fetch(url,'0'*64))
 fails('missing credential',lambda:op.open(url+'/runner?nonce='+'a'*64))
 fails('bad nonce',lambda:fixed_entry.response(r,key,'x'))
 original=fixed_entry.response
 def corrupt(mode):
  def altered(*args):
   d=original(*args)
   if mode=='signature':d['signature']='0'*64
   else:d['notebook']=d['notebook'][:-4]+'AAAA'
   return d
  return altered
 for mode in ['signature','payload']:
  fixed_entry.response=corrupt(mode);fails(mode,lambda:fetch(url,key))
 fixed_entry.response=original
 a.store.meta.append({});fails('nonempty round',lambda:fetch(url,key));a.store.meta.clear()
 a.store.final={'status':'failed'};fails('finished round',lambda:fetch(url,key));a.store.final=None
 # Same permanent client obtains a different session from the same server.
 newer=dict(current,session_id='e'*32,token='d'*64);newraw,_=notebook(P,newer);newpath=T/'second.ipynb';newpath.write_bytes(newraw)
 r.current=App(newer,T/'second_records');r.notebook_path=lambda app:newpath
 sid2,payload2,code2=fetch(url,key);assert sid2==newer['session_id'] and payload2==newraw and sid2!=sid
 assert (T/fixed_entry.NAME).read_bytes()==fixed
 cell=''.join(json.loads(fixed)['cells'][1]['source']);ast.parse(cell,feature_version=(3,8));scope={}
 try:exec(cell,scope)
 except RuntimeError as ex:assert 'Board-only' in str(ex)
 else:raise AssertionError('desktop guard')
 try:exec(cell,scope)
 except RuntimeError as ex:assert 'Restart kernel' in str(ex)
 else:raise AssertionError('repeat guard')
 assert 'ATTEMPT_' in (P/'bundle/live_board.py').read_text()
 # No firmware/model/runtime modifications.
 manifest=json.loads((E/'before/FINAL_MANIFEST_SHA256.json').read_text());unchanged=0
 for name,digest in manifest.items():
  if name in ['pc\\live_server.py','assets\\index.html','assets\\ui.js']:continue
  assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name;unchanged+=1
 result=dict(status='PASS_CPU_HTTP_REUSABLE_NOTEBOOK',two_sessions_one_fixed_notebook=True,exact_existing_guarded_cell=True,restart_stable_key_and_entry=True,negative_cases=neg,desktop_and_repeat_guard=True,unchanged_sealed_files=unchanged,hardware_actions=0,physical_repeat_pending=True)
 (E/'CPU_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
finally:srv.shutdown();srv.server_close();thread.join(5)

