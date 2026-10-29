from pathlib import Path
P=Path('flyvis-lossless-study/ov5640_motion_experiment_20261026')
def edit(rel,fn):
 p=P/rel;s=p.read_text(encoding='utf-8-sig');p.write_text(fn(s),encoding='utf-8')
def binding(s):
 s=s.replace('self.failed=False;self.lock=threading.Lock();self.last_committed=None','self.failed=False;self.lock=threading.Lock();self.last_committed=None;self.retain_source=False')
 s=s.replace("                save_capsule(directory/'PREPARED.bin',metadata,inputs)","                if self.retain_source:\n                    if len(frame)!=WIDTH*HEIGHT*3:raise ValueError('source frame dimensions')\n                    metadata.update(frame_sha256=sha(frame),source_hash_retained=True,source_pixels_retained=True)\n                save_capsule(directory/'PREPARED.bin',metadata,inputs+(frame if self.retain_source else b''))")
 return s
edit('bundle/capture_binding.py',binding)
def protocol(s):
 s=s.replace('from camera_config import WIDTH,HEIGHT,MAPPING','from camera_config import WIDTH,HEIGHT,MAPPING\nimport motion_trial')
 s=s.replace("    if len(raw)!=4+n+(0 if compact else SOURCE_BYTES)+RECORD_BYTES", "    experiment=m['schema']=='line11-motion-record/v4'\n    source_size=WIDTH*HEIGHT*3 if experiment else SOURCE_BYTES\n    if len(raw)!=4+n+(0 if compact else source_size)+RECORD_BYTES")
 s=s.replace("m['schema'] not in ('line11-live-record/v1','line11-live-compact/v2','line11-live-compact/v3')", "m['schema'] not in ('line11-live-record/v1','line11-live-compact/v2','line11-live-compact/v3','line11-motion-record/v4')")
 s=s.replace('raw[4+n:4+n+SOURCE_BYTES]','raw[4+n:4+n+source_size]')
 s=s.replace("if m['schema']!='line11-live-compact/v3'", "if m['schema'] not in ('line11-live-compact/v3','line11-motion-record/v4')")
 s=s.replace('    return m,source,r',"    motion_trial.validate(m,config)\n    if (motion_trial.condition(config)!='demo')!=experiment:raise ValueError('experiment schema required')\n    if experiment and (m.get('camera_width')!=WIDTH or m.get('camera_height')!=HEIGHT or m.get('source_pixels_retained') is not True or p.get('source_pixels_retained') is not True or c.get('source_pixels_retained') is not True):raise ValueError('experiment camera contract')\n    return m,source,r",1)
 s=s.replace('    return m\n',"    name=motion_trial.condition(config)\n    if name!='demo':\n        start=context['experiment_start_ns']\n        if not p.get('source_pixels_retained') or c['frame_sha256']!=sha(source):raise ValueError('experiment source not retained/bound')\n        m.update(schema='line11-motion-record/v4',source_pixels_retained=True,experiment_start_ns=start,\n                 experiment=motion_trial.annotation(name,p['source_timestamp_ns']-start))\n    return m\n",1)
 return s
edit('bundle/live_protocol.py',protocol)
def board(s):
 s=s.replace('from camera_config import WIDTH,HEIGHT,MAPPING','from camera_config import WIDTH,HEIGHT,MAPPING\nimport motion_trial')
 s=s.replace("    config=dict(config)","    config=dict(config);motion_trial.condition(config)",1)
 s=s.replace("source_images_transferred=False,source_pixels_retained=False", "source_images_transferred=motion_trial.condition(config)!='demo',source_pixels_retained=motion_trial.condition(config)!='demo'")
 s=s.replace("        runtime.owner['bridge']=bridge", "        bridge.binding.retain_source=motion_trial.condition(config)!='demo'\n        runtime.owner['bridge']=bridge")
 s=s.replace('        previous_iteration_end=time.monotonic();window.begin()', "        if motion_trial.condition(config)!='demo':\n            context['experiment_start_ns']=time.monotonic_ns()\n            worker.context['experiment_start_ns']=context['experiment_start_ns']\n            save_json(out/'EXPERIMENT.json',dict(condition=motion_trial.condition(config),start_ns=context['experiment_start_ns'],segments=motion_trial.SEGMENTS,events_are_planned=True))\n        previous_iteration_end=time.monotonic();window.begin()")
 s=s.replace("每16步后台保存一次，不保存原图。", "每16步后台保存一次；纸条实验保留80×48原始采集帧，普通演示不保存原图。")
 # Mode printed before existing authorization, no extra manual confirmation loop.
 s=s.replace("    plan=read_memory_plan(config)", "    print('本轮模式：'+motion_trial.LABELS[motion_trial.condition(config)],flush=True)\n    plan=read_memory_plan(config)")
 return s
edit('bundle/live_board.py',board)
def rounds(s):
 s=s.replace('from live_protocol import atomic,canonical','from live_protocol import atomic,canonical\nimport motion_trial')
 s=s.replace('def advance(self,expected):','def advance(self,expected,mode=\'demo\'):\n        motion_trial.condition({\'motion_condition\':mode})')
 s=s.replace("if receipt.get('parent_session_id')==expected and receipt['session_id']==sid:return", "if receipt.get('parent_session_id')==expected and receipt['session_id']==sid and motion_trial.condition(old.config)==mode:return")
 s=s.replace("config=dict(old.config,session_id=next_id,token=secrets.token_hex(32))", "config=dict(old.config,session_id=next_id,token=secrets.token_hex(32),motion_condition=mode)")
 s=s.replace("if k not in ('session_id','token')", "if k not in ('session_id','token','motion_condition')")
 s=s.replace("            nb,base=notebook(self.root,config)", "            if motion_trial.condition(config)!=mode:raise ValueError('已准备另一种实验，不能覆盖；先核查当前会话')\n            nb,base=notebook(self.root,config)")
 return s
edit('pc/round_sessions.py',rounds)
def server(s):
 s=s.replace('import argparse,','import base64\nimport motion_trial_PLACEHOLDER\nimport argparse,').replace('import motion_trial_PLACEHOLDER\n','')
 s=s.replace('import fixed_entry','import fixed_entry\nimport motion_trial')
 s=s.replace("return dict(application='line11-live-v261',", "return dict(application='line11-live-v261',motion_condition=motion_trial.condition(self.config),")
 s=s.replace("            else:\n                a=np.frombuffer(source,np.uint8).reshape(480,800,3);img=Image.fromarray(a[:,:,::-1],'RGB')", "            else:\n                if m['schema']=='line11-motion-record/v4':\n                    # Preserve the existing721display; raw camera preview shares this exact packet.\n                    a=np.frombuffer(source,np.uint8).reshape(48,80,3);rawbuf=io.BytesIO();Image.fromarray(a[:,:,::-1],'RGB').save(rawbuf,format='PNG')\n                    packet.update(camera_png='data:image/png;base64,'+base64.b64encode(rawbuf.getvalue()).decode(),experiment=m['experiment'])\n                    values=np.frombuffer(r.input_bits,'<f4');packet['input_721']=values.tolist()\n                    img=Image.new('RGB',(417,417),(35,35,35));draw=ImageDraw.Draw(img)\n                    for (row,col),value in zip(receptor_centers(),values):\n                        gray=int(np.clip(value,0,1)*255+.5);draw.ellipse((int(col)-5,int(row)-5,int(col)+5,int(row)+5),fill=(gray,gray,gray))\n                else:\n                    a=np.frombuffer(source,np.uint8).reshape(480,800,3);img=Image.fromarray(a[:,:,::-1],'RGB')")
 s=s.replace("return self.reply(200,rounds.advance(json.loads(data)['session_id']))", "args=json.loads(data)\n                    return self.reply(200,rounds.advance(args['session_id'],args.get('motion_condition','demo')))")
 return s
edit('pc/live_server.py',server)
def html(s):
 s=s.replace('<button id="nextRound"', '<select id="motionCondition" aria-label="下一轮模式"><option value="demo">普通演示</option><option value="white_black">实验：白底黑条</option><option value="black_white">实验：黑底白条</option></select><button id="nextRound"',1)
 s=s.replace('<div class="viewport"><img id="camera"', '<div class="viewport" style="position:relative"><img id="rawCamera" hidden alt="同一步80×48原始采集帧，假定BGR颜色顺序" style="position:absolute;right:0;bottom:8px;width:40%;height:auto;border:1px solid #71dccb;image-rendering:pixelated"><img id="camera"',1)
 s=s.replace('<p class="caption">中央正方形视野 · 灰度输入 · 无补灰</p>','<p class="caption" id="experimentCue">中央正方形视野 · 灰度输入 · 无补灰</p>',1)
 # hidden must override existing .viewport img display:block.
 s=s.replace('</style>','[hidden]{display:none!important}#experimentCue{white-space:pre-line;color:#b9d5e4}</style>',1)
 return s
edit('assets/index.html',html)
def ui(s):
 s=s.replace('JSON.stringify({session_id:currentSession})', "JSON.stringify({session_id:currentSession,motion_condition:$('motionCondition').value})")
 s=s.replace("const imageReady=image.decode().then", "const rawImage=p.camera_png?new Image():null;if(rawImage)rawImage.src=p.camera_png;\n    const rawReady=rawImage?rawImage.decode():Promise.resolve();\n    const imageReady=image.decode().then")
 s=s.replace('await Promise.all([imageReady,boneReady])','await Promise.all([imageReady,boneReady,rawReady])')
 s=s.replace("     $('camera').src=image.src;", "     $('rawCamera').hidden=!rawImage;if(rawImage)$('rawCamera').src=rawImage.src;\n     $('experimentCue').textContent=p.experiment?`${p.experiment.label} · 采集计时 ${(p.experiment.elapsed_ns/1e9).toFixed(1)}秒\\n${p.experiment.cue}\\n这是该帧的计划提示；非实际边缘事件。右下角：同一步原始采集帧。`:'中央正方形视野 · 灰度输入 · 无补灰';\n     $('camera').src=image.src;")
 return s
edit('assets/ui.js',ui)
