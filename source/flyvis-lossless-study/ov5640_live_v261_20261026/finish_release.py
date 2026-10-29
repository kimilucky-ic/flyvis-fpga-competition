from pathlib import Path
import json,hashlib,ast
P=Path(__file__).resolve().parent;O=P.parent/'ov5640_live_crop_20261026';F=P.parent/'vivado2026_1_20261026'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
counts={}
for root,seal in [(O,'BASELINE_RELEASE_SHA256.json'),(F,'FIRMWARE_RELEASE_SHA256.json')]:
 m=json.loads((P/'evidence'/seal).read_text());assert all(sha(root/n)==h for n,h in m.items());counts[root.name]=len(m)
checks={}
for name in ['PACKAGE_CPU_RESULT.json','HTTP_RESULT.json','IDENTITY_RESULT.json']:
 v=json.loads((P/'evidence'/name).read_text());assert v['status'].startswith('PASS');checks[name]=v
for f in list((P/'bundle').glob('*.py'))+list((P/'pc').glob('*.py')):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))
c=json.loads((P/'pc/session.json').read_text());info=json.loads((P/'bundle/release_info.json').read_text());d=json.loads((P/'DELIVERY.json').read_text())
assert d['notebook_sha256']==checks['HTTP_RESULT.json']['notebook_sha256']
r=dict(status='PASS_CPU_VIVADO2026_1_CROP_60S_RELEASE_BOARD_PENDING',evidence='OFFLINE_PACKAGE_AND_CPU_GUARDS_NOT_PHYSICAL_BOARD',source_software=O.name,source_firmware=F.name,tool=info['tool'],network=dict(nodes=45669,edges=1513231,input_words=721,numeric='UNCHANGED_STRICT_FP32',clock_target_hz=100000000),mapping=dict(revision=c['input_mapping'],camera_width=80,camera_height=48,crop_roi=c['crop_roi'],unchanged_from_passed_crop=True),run=dict(duration_s=60,ring_slots=64,minimum_period_s=0,max_steps_safety_bound=4096,port=c['port'],pc_url=c['pc_url'],default_transfer='721actual_inputs_and_all45669states',operator_confirmation='运行2026.1铺满版60秒',board_directory='/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_V261_60S'),firmware=dict(bit_sha256=info['bit_sha256'],hwh_sha256=info['hwh_sha256'],DCP_sha256=info['source_routed_dcp_sha256'],ABI='0x00110005'),delivery=d,checks=checks,preservation=counts,board_operations=0,GPU_operations=0,Vivado_runs_this_package_turn=0,limits=['New bitstream has no physical acceptance; previous1093step60s crop PASS belongs to old bitstream','No new performance claim;54.90ms/step is old operator observation','Unchanged camera,grey mapping,ARM runtime,DDR release,storage,transport and oracle; no new full-network numerical simulation was needed for identity-only software change','Existing conditional external camera timing and blocking official camera call limits remain','No permanent receiver started; operator starts newPC entry and authorizes board notebook'],next='Operator launches newPC entry, uploads new singleNotebook to independent kernel after oldcamera normalclose, confirms once, returns60s completion and all-state audit')
(P/'RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'COMMANDS.json').write_text(json.dumps(dict(python='C:/Users/hzy72/Documents/ChatGPT/fly/.venv/Scripts/python.exe -X utf8 -B',cwd=str(P),steps=['prepare.py','build_release.py','tests/test_release.py','tests/test_http.py (temporary127.0.0.1 only)','tests/test_identity.py','finish_release.py'],no_board=True,no_new_Vivado=True),indent=2))
seal={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts and ('evidence' not in f.relative_to(P).parts or f.parent==P/'evidence') and f.name!='FINAL_MANIFEST_SHA256.json'}
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2))
print(json.dumps(dict(status=r['status'],notebook=d['notebook'],notebook_bytes=d['notebook_bytes'],notebook_sha256=d['notebook_sha256'],preserved=counts,sealed_files=len(seal),port=c['port']),ensure_ascii=False))
