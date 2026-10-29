from pathlib import Path
import json,hashlib
O=Path('flyvis-lossless-study/ov5640_layout_20261027');R=O.parent/'ov5640_live_v261_20261026'
p=R/'assets/ui.js';s=p.read_text('utf-8');s=s.replace("$('anatomyCaption').textContent='与曲线同一区域 / 同一步 · '","$('anatomyCaption').textContent='完整右侧视叶 ME / LO / LOP（非全脑）· 同一区域 / 同一步 · '");p.write_text(s,encoding='utf-8')
p=O/'test_pixels.py';s=p.read_text('utf-8').replace('all5529600RGBAbytes','all4608000RGBAbytes').replace('original transformed background','complete projected mesh background');p.write_text(s,encoding='utf-8')
changed=['assets/index.html','assets/monitor.js','assets/ui.js','assets/projection.json','assets/projection.bin']
seal=json.loads((O/'before/FINAL_MANIFEST_SHA256.json').read_text('utf-8'))
for k,v in seal.items():
 digest=hashlib.sha256((R/Path(k)).read_bytes()).hexdigest()
 if k.replace('\\','/') in changed:seal[k]=digest
 else:assert digest==v,k
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'INSTALL.json').write_text(json.dumps(dict(changed=changed,unchanged_sealed_files=len(seal)-len(changed),board_actions=0),indent=2))
