from pathlib import Path
import json,hashlib,shutil,sys
P=Path(__file__).resolve().parents[1];O=P.parent/'ov5640_live_crop_20261026';B=P/'bundle'
sys.path.insert(0,str(B));import offline_check
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
T=P/'evidence/negative_pair';shutil.copytree(B,T)
manifest=json.loads((T/'release_manifest.json').read_text());cases=[]
def reject(name,expected):
 try:offline_check.verify(T)
 except ValueError as e:assert expected in str(e),str(e);cases.append(dict(case=name,rejected=str(e)))
 else:raise AssertionError('Accepted '+name)
# Same filename with one corrupt byte: manifest must stop before runtime.
f=T/'flyvis_official.bit';raw=f.read_bytes();f.write_bytes(raw[:-1]+bytes([raw[-1]^1]));reject('corrupt_BIT','Package mismatch');f.write_bytes(raw)
# Coherent manifest alone must not admit a wrong candidate or mixed pair.
for name in ['flyvis_official.bit','flyvis_official.hwh']:
 shutil.copy2(O/'bundle'/name,T/name);manifest[name]=dict(bytes=(T/name).stat().st_size,sha256=sha(T/name));(T/'release_manifest.json').write_text(json.dumps(manifest))
 reject('old_'+name+'_with_rehashed_manifest','BIT/HWH mismatch')
 shutil.copy2(B/name,T/name);manifest[name]=dict(bytes=(T/name).stat().st_size,sha256=sha(T/name));(T/'release_manifest.json').write_text(json.dumps(manifest))
assert offline_check.verify(T)['board_result'] is False
changed=[f.name for f in B.iterdir() if f.is_file() and f.read_bytes()!=(O/'bundle'/f.name).read_bytes()]
assert set(changed)=={'flyvis_official.bit','flyvis_official.hwh','offline_check.py','live_board.py','release_info.json','release_manifest.json'},changed
old='LINE11_OFFICIAL_LIVE_CROP_60S';new='LINE11_OFFICIAL_LIVE_V261_60S'
assert (B/'live_board.py').read_text()==(O/'bundle/live_board.py').read_text().replace(old,new).replace('运行铺满版60秒','运行2026.1铺满版60秒')
for n in ['direct_input.py','camera_config.py','board_runtime.py','official_iic21.py','ddr_control.py','ddr_memory.py','record_worker.py','batch_records.py','live_protocol.py','live_transport.py','official_bridge.py','native_payload.py','payload_check.c','reference.exe','reference.cpp','initial_state.bin','edges.bin','meta.hex']:
 assert (B/n).read_bytes()==(O/'bundle'/n).read_bytes(),n
for n in ['full_audit.py','audit_saved_run.py']:assert (P/'pc'/n).read_bytes()==(O/'pc'/n).read_bytes()
a=json.loads((O/'pc/session.json').read_text());b=json.loads((P/'pc/session.json').read_text());assert a['session_id']!=b['session_id'] and a['token']!=b['token'] and a['port']!=b['port']
assert not (P/'pc/records').exists()
r=dict(status='PASS_FIRMWARE_NEGATIVE_CASES_AND_UNCHANGED_RUNTIME',cases=cases,changed_bundle_files=changed,core_runtime_and_mapping_unchanged=True,full_auditor_unchanged=True,session_isolated=True,received_records=0,board_operations=0)
(P/'evidence/IDENTITY_RESULT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
