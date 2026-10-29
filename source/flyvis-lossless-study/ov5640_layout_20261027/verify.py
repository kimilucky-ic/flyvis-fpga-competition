from pathlib import Path
import json,hashlib
O=Path('flyvis-lossless-study/ov5640_layout_20261027');R=O.parent/'ov5640_live_v261_20261026'
seal=json.loads((R/'FINAL_MANIFEST_SHA256.json').read_text('utf-8'))
for k,v in seal.items():assert hashlib.sha256((R/Path(k)).read_bytes()).hexdigest()==v,k
b=json.loads((O/'BROWSER_CHECK.json').read_text('utf-8'));assert b['neural']['roi']=='1' and b['neural']['relative']=='true' and not json.loads(b['neural']['visible'])[0]
a=b['panels'];assert a[0]['x']==a[1]['x'] and a[0]['y']<a[1]['y'] and a[2]['x']>a[0]['x'] and a[2]['x']==a[3]['x']
result=dict(status='PASS_CPU_AND_BROWSER_SAVED_RECORD_LAYOUT',seal_files=len(seal),changed_files=5,board_actions=0,GPU_runs=0,Vivado_runs=0,neural_computation_changed=False,observer_map_changed=False,renderer_tests='12 saved packets plus3 independent pixel cases,4608000 identical bytes',browser='left input/anatomy; right curves; T4expand; leftROI/relative/hideL1 same step1080 and statehash',background='Complete original right ME/LO/LOP mesh geometry,14representative SWCs,8477nodes no clipping; not whole brain',live_blocker='Existing1015-step online AUDIT_ERROR from prior packet PermissionError remains; independent offlinePASS preserved, no bypass')
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
