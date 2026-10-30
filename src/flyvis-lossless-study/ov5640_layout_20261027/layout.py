from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026'
p=R/'assets/index.html';s=p.read_text('utf-8')
css='''
/* Left: input and anatomy. Right: response curves. */
.dashboard{grid-template-columns:minmax(340px,.75fr) minmax(600px,1.65fr);grid-template-rows:minmax(330px,1fr) auto;align-items:stretch}
.visuals{grid-column:1;grid-row:1 / 3;grid-template-columns:1fr;grid-template-rows:minmax(230px,.8fr) minmax(330px,1.2fr)}
.group-panel{grid-column:2;grid-row:1}.motion-panel{grid-column:2;grid-row:2;min-height:160px}
.panel{padding:12px 16px}.panel h2{font-size:15px}.panel .tag{font-size:9px}
.observer-controls{gap:6px}.anatomy-controls{gap:4px}.anatomy-controls small{min-width:31px}
.roi-legend{color:#7ef5d3;font-size:11px;margin:5px 0 0}.viewport{overflow:hidden}
body:has(.motion-panel button[aria-expanded="true"]) .dashboard{grid-template-rows:minmax(330px,1fr) auto}
@media(min-width:1101px){body{height:100dvh;min-height:880px}.visuals{height:auto}.group-panel{height:auto;margin:0}#groups{min-height:300px}}
@media(max-width:1100px){body{height:auto;min-height:100dvh;padding:14px}.dashboard{display:grid;grid-template-columns:1fr;grid-template-rows:auto auto auto}.visuals{grid-column:1;grid-row:1;grid-template-columns:1fr 1fr;grid-template-rows:430px;min-height:0;height:auto}.group-panel{grid-column:1;grid-row:2;height:460px;margin:0}.motion-panel{grid-column:1;grid-row:3}.panel .tag{display:none}}
@media(max-width:620px){.visuals{display:grid;grid-template-columns:1fr;grid-template-rows:350px 450px}.visuals .panel{height:auto}.group-panel{height:600px}.specs{gap:12px}.controls{flex-wrap:wrap}.toolbar{flex-wrap:wrap}}
'''
s=s.replace('</style>',css+'</style>')
s=s.replace('绿色圈标出的37个视野采样位置','蓝绿色圈：当前观察区域的37个位置，仅用于显示选区')
s=s.replace('<p class="caption" id="experimentCue">','<p class="roi-legend">◯ 蓝绿圈 = 曲线取平均的37个位置 · 不改变输入</p><p class="caption" id="experimentCue">')
s=s.replace('width="960" height="480"','width="640" height="600"')
s=s.replace('代表性真实形态 · 不对应单个模型细胞 · 亮度表示幅度，正负看数值与曲线','完整右侧视叶背景（ME / LO / LOP）· 非全脑<br>代表性真实形态 · 亮度表示幅度，正负看数值与曲线')
p.write_text(s,encoding='utf-8')
p=R/'assets/monitor.js';s=p.read_text('utf-8').replace("' · 仅已显示步骤，跳帧留空'","' · 蓝绿圈为对应视野位置 · 仅已显示步骤，跳帧留空'");p.write_text(s,encoding='utf-8')
changed=['assets/index.html','assets/monitor.js','assets/projection.json','assets/projection.bin']
seal=json.loads((O/'before/FINAL_MANIFEST_SHA256.json').read_text('utf-8'))
for k,v in seal.items():
 digest=hashlib.sha256((R/Path(k)).read_bytes()).hexdigest()
 if k.replace('\\','/') in changed:seal[k]=digest
 else:assert digest==v,k
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'INSTALL.json').write_text(json.dumps(dict(changed=changed,unchanged_sealed_files=len(seal)-len(changed),board_actions=0),indent=2))
# Reuse renderer/failure tests without overwriting prior evidence.
s=(O.parent/'ov5640_extended_anatomy_20261026/test_renderer.cjs').read_text('utf-8').replace("'old','CENTRAL_ROI37_T4T5'","'old',{roi:0,relative:false,visible:Array(14).fill(true)}")
(O/'test_renderer.cjs').write_text(s,encoding='utf-8')
s=(O.parent/'ov5640_extended_anatomy_20261026/test_pixels.py').read_text('utf-8').replace('(480,960,4)','(600,640,4)')
(O/'test_pixels.py').write_text(s,encoding='utf-8')
