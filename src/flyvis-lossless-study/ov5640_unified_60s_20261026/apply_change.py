from pathlib import Path
import json,hashlib,shutil
R=Path('flyvis-lossless-study/ov5640_live_v261_20261026');O=Path('flyvis-lossless-study/ov5640_unified_60s_20261026');O.mkdir(exist_ok=True)
changed=['bundle/motion_trial.py','bundle/live_board.py','pc/round_sessions.py','pc/live_server.py','pc/export_motion.py','assets/index.html','assets/ui.js']
for rel in changed+['bundle/release_manifest.json','FINAL_MANIFEST_SHA256.json','pc/ACTIVE_ROUND.json']:
 p=O/'before'/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():raise RuntimeError('Existing backup')
 shutil.copy2(R/rel,p)
def edit(rel,fn):
 p=R/rel;p.write_text(fn(p.read_text(encoding='utf-8')),encoding='utf-8')
def trial(s):
 s=s.replace("CONDITIONS=('demo','white_black','black_white')","CONDITIONS=('demo','white_black','black_white','capture')")
 s=s.replace("LABELS={'demo':","LABELS={'capture':'60秒采集','demo':")
 marker='    t=elapsed_ns/1e9'
 insert="""    if name=='capture':
        return dict(schema='line11-capture-receipt/v1',condition=name,label=LABELS[name],elapsed_ns=elapsed_ns,
            phase='capture',trial=None,cue='',
            time_basis='PS_READFRAME_RETURN_RELATIVE_TO_LOOP_START_NOT_EXPOSURE',
            event_basis='UNANNOTATED_NO_ASSUMED_STIMULUS_OR_DIRECTION',model_dt_s=.005,
            sampled_frame_shape=[48,80,3],channel_order='BGR_ASSUMED_NOT_PHYSICALLY_VERIFIED',
            mapping_crop=dict(x=16,y=0,width=48,height=48))
"""
 return s.replace(marker,insert+marker)
edit('bundle/motion_trial.py',trial)
edit('bundle/live_board.py',lambda s:s.replace("segments=motion_trial.SEGMENTS,events_are_planned=True","segments=[] if motion_trial.condition(config)=='capture' else motion_trial.SEGMENTS,events_are_planned=motion_trial.condition(config)!='capture'").replace("print('本轮模式：'+motion_trial.LABELS[motion_trial.condition(config)],flush=True)","print('运行60秒；实验内容由你自行安排，无需选择模式。',flush=True)").replace('纸条实验保留80×48原始采集帧，普通演示不保存原图','本轮保留80×48原始采集帧、721项输入和全部神经状态'))
edit('pc/round_sessions.py',lambda s:s.replace("def advance(self,expected,mode='demo'):","def advance(self,expected,mode='capture'):").replace("        motion_trial.condition({'motion_condition':mode})","        if mode!='capture':raise ValueError('统一60秒入口不接受实验模式选择')").replace('每步721项输入和全部45669状态仍保存。','每步80×48原始画面、721项输入和全部45669状态均保存。实验内容由你自行安排。'))
edit('pc/live_server.py',lambda s:s.replace("args.get('motion_condition','demo')","args.get('motion_condition','capture')"))
edit('pc/export_motion.py',lambda s:s.replace("('white_black','black_white')","('white_black','black_white','capture')").replace("  for x,y in [(10,15),(25,30),(40,45)]:ax.axvspan(x,y,color='orange',alpha=.12)","  if config['motion_condition']!='capture':\n   for x,y in [(10,15),(25,30),(40,45)]:ax.axvspan(x,y,color='orange',alpha=.12)").replace("config['motion_condition']+' | shaded = planned movement, NOT detected edges'","('60s capture | stimulus events not annotated' if config['motion_condition']=='capture' else config['motion_condition']+' | shaded = planned movement, NOT detected edges')").replace("events='PLANNED_ONLY_ACTUAL_EDGE_TIMES_REQUIRE_IMAGE_ANALYSIS'","events='UNANNOTATED_ACTUAL_EDGE_TIMES_REQUIRE_IMAGE_ANALYSIS' if config['motion_condition']=='capture' else 'PLANNED_ONLY_ACTUAL_EDGE_TIMES_REQUIRE_IMAGE_ANALYSIS'"))
import re
edit('assets/index.html',lambda s:re.sub(r'<label for="motionCondition">.*?</select>','',s,count=1))
def ui(s):
 a=s.index('function updateRoundMode(');b=s.index("if(typeof module",a);s=s[:a]+s[b:]
 s=s.replace(',updateRoundMode','').replace(",motion_condition:$('motionCondition').value",'')
 s=s.replace("   const activeMode=updateRoundMode(s,$('motionCondition'),$('nextRound'),creating);","   $('nextRound').disabled=creating||s.next_round_allowed!==true;")
 s=s.replace("('本轮模式：'+activeMode+' · ')","'60秒采集 · '")
 s=re.sub(r"     \$\('experimentCue'\)\.textContent=.*?;\n","     $('experimentCue').textContent='中央正方形视野 · 灰度输入 · 原始画面与721项输入、神经状态逐步对应';\n",s,count=1)
 assert 'motionCondition' not in s and 'activeMode' not in s
 return s
edit('assets/ui.js',ui)
manifest=json.loads((R/'bundle/release_manifest.json').read_text())
for rel in changed:
 if rel.startswith('bundle/'):
  data=(R/rel).read_bytes();manifest[Path(rel).name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
(R/'bundle/release_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
seal=json.loads((R/'FINAL_MANIFEST_SHA256.json').read_text())
for rel in changed+['bundle/release_manifest.json']:
 keys=[k for k in seal if Path(k)==Path(rel)];assert len(keys)==1,rel
 seal[keys[0]]=hashlib.sha256((R/rel).read_bytes()).hexdigest()
for k,h in seal.items():assert hashlib.sha256((R/k).read_bytes()).hexdigest()==h,k
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'CHANGED.json').write_text(json.dumps(changed,indent=2))
print('Unified capture path installed locally; old packet readers preserved; seals verified')
