"""Build an isolated ready-to-check bundle. Offline CPU/file operations only."""
import argparse
import ast
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
CAND=STUDY/'hole_pipeline_20261016'
OLD=STUDY/'pipeline100_20261015/delivery_100mhz'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',default='r1');args=ap.parse_args()
    if not args.tag.isalnum():raise ValueError('Invalid output tag')
    bundle=HERE/('bundle_'+args.tag)
    archive=HERE/('flyvis_line11_22ms_preboard_'+args.tag+'.zip')
    extracted=HERE/('extracted_check_'+args.tag)
    if any(p.exists() for p in [bundle,archive,extracted]):raise FileExistsError('Never overwrite an existing preparation')
    save(HERE/('PREPARE_COMMAND_'+args.tag+'.json'),dict(argv=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
         python=sys.version,board_operations=0,GPU=False,EDA=False))
    sealed=read(CAND/'FINAL_MANIFEST_SHA256.json')
    if sha(CAND/'FINAL_MANIFEST_SHA256.json')!='be745d2394f9e34dde011dc59a4af2d4abf7d897321e43dc18efe4f506acd09a':
        raise ValueError('Wrong candidate seal')
    old_manifest=read(OLD/'release_manifest.json')
    selected={}
    def check(path,manifest,key):
        item=manifest[key]
        if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:raise ValueError('Changed source: '+str(path))
        selected[str(path)]=item['sha256']
    copy_from_candidate={
        'flyvis_full.bit':'soc_r2/release/flyvis_full.bit',
        'flyvis_full.hwh':'soc_r2/release/flyvis_full.hwh',
        'flyvis_driver.py':'flyvis_driver.py','frame_stepper.py':'frame_stepper.py',
        'evidence/AUDIT_soc_r2.json':'AUDIT_soc_r2.json',
        'evidence/full_network_CPU_summary.json':'cpu_r1/summary.json',
        'evidence/timing_routed.rpt':'soc_r2/release/timing_routed.rpt',
        'evidence/utilization_routed.rpt':'soc_r2/release/utilization_routed.rpt',
        'evidence/platform_properties.txt':'soc_r2/release/platform_properties.txt',
    }
    for key in list(copy_from_candidate.values())+['images/initial.hex','images/stimulus.hex','test_full.cpp']:
        check(CAND/key,sealed,key)
    for key in ['input_frame0.bin','expected_state1.bin','PROVENANCE.json','upstream_flyvis_license.txt']:
        check(OLD/key,old_manifest,key)
    audit=read(CAND/'AUDIT_soc_r2.json')
    if audit['status']!='PASS_FULL_SOC_100MHZ_ROUTE_LOCAL_ARTIFACTS_ONLY':raise ValueError('Candidate not accepted locally')
    # Reconcile the old board-family profile evidence with the current HWH.
    compatibility=read(STUDY/'board_compatibility_20261015/COMPATIBILITY.json')
    hwh=ET.parse(str(CAND/'soc_r2/release/flyvis_full.hwh')).getroot()
    ps=next(x for x in hwh.iter('MODULE') if x.get('INSTANCE')=='ps7')
    params={p.get('NAME'):p.get('VALUE') for p in ps.iter('PARAMETER')}
    matched={}
    for key,value in compatibility['profile_fields'].items():
        if params.get(key)!=str(value['vendor']):raise ValueError('Board profile mismatch: '+key)
        matched[key]=params[key]
    # Freeze only already-validated first-step vectors, no new neural inference.
    def hex_binary(path):
        return b''.join(struct.pack('<I',int(line,16)) for line in path.read_text().split())
    initial=hex_binary(CAND/'images/initial.hex')
    stimulus=hex_binary(CAND/'images/stimulus.hex')
    vectors=STUDY/'rtl_behavior_20261013/vectors/initial32'
    if initial!=(vectors/'initial.bin').read_bytes():raise ValueError('Initial state lineage mismatch')
    if stimulus!=(OLD/'input_frame0.bin').read_bytes():raise ValueError('Stimulus lineage mismatch')
    golden_first=(vectors/'golden.bin').read_bytes()[:45669*4]
    if golden_first!=(OLD/'expected_state1.bin').read_bytes():raise ValueError('First-step golden lineage mismatch')
    if len(initial)!=45669*4 or len(stimulus)!=721*4:raise ValueError('Wrong vector size')
    for path in [vectors/'initial.bin',vectors/'golden.bin',vectors/'case.json']:
        selected[str(path)]=sha(path)
    bundle.mkdir()
    for dest,source in copy_from_candidate.items():
        path=bundle/dest;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(CAND/source,path)
    for name in ['input_frame0.bin','expected_state1.bin','PROVENANCE.json','upstream_flyvis_license.txt']:
        shutil.copyfile(OLD/name,bundle/name)
    for name in ['board_check.py','test_board_check.py','README.md']:
        shutil.copyfile(HERE/name,bundle/name)
    snapshot=STUDY/'board_first_step_100mhz_20261015/read_current_board.py'
    shutil.copyfile(snapshot,bundle/'snapshot_board.py');selected[str(snapshot)]=sha(snapshot)
    (bundle/'initial_state.bin').write_bytes(initial)
    save(bundle/'CANDIDATE.json',dict(candidate='hole_pipeline_20261016/soc_r2',device=audit['device'],
         nodes=45669,ordered_edges=1513231,numeric_profile='strictFP32RNE',clock_MHz=100,
         cycles=2201418,core_ms_theory=22.01418,stage='ROUTED_LOCAL_ONLY_BOARD_NOT_RUN',
         artifact_identities=audit['artifacts'],profile_fields_match=matched,
         compatibility_source=str(STUDY/'board_compatibility_20261015/COMPATIBILITY.json'),
         physical_silk_observed=False,pynq_runtime_historical='2.7.0; must recheck live',
         selected_sources=selected,first_step_reference=read(vectors/'case.json'),
         no_CPU_neural_fallback=True,no_automatic_retry_or_recovery=True))
    manifest={p.relative_to(bundle).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
              for p in sorted(bundle.rglob('*')) if p.is_file()}
    save(bundle/'release_manifest.json',manifest)
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(bundle.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(bundle).as_posix())
    with zipfile.ZipFile(archive) as z:z.extractall(extracted)
    env=dict(__import__('os').environ,PYTHONDONTWRITEBYTECODE='1')
    commands=[[sys.executable,'-B','board_check.py'],
              [sys.executable,'-B','-m','unittest','-v','test_board_check']]
    logs=[]
    for index,command in enumerate(commands):
        p=subprocess.run(command,cwd=extracted,env=env,capture_output=True,text=True,timeout=45)
        log=HERE/(args.tag+('_offline.log' if index==0 else '_tests.log'))
        log.write_text(json.dumps(command)+'\n'+p.stdout+p.stderr,encoding='utf-8');logs.append(str(log))
        if p.returncode:raise RuntimeError('Focused offline check failed; see '+str(log))
        if index==1 and 'Ran 12 tests' not in p.stderr:raise RuntimeError('Unexpected test count')
    # Corrupt only a fresh temporary copy; source bundle and ZIP remain intact.
    target=extracted/'expected_state1.bin';original=target.read_bytes()
    try:
        target.write_bytes(original[:-1]+bytes([original[-1]^1]))
        p=subprocess.run(commands[0],cwd=extracted,env=env,capture_output=True,text=True,timeout=15)
        if p.returncode==0 or 'Bundle identity mismatch' not in p.stderr:raise RuntimeError('Corrupt package was accepted')
        (HERE/(args.tag+'_corruption.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
    finally:target.write_bytes(original)
    for name,item in manifest.items():
        if sha(extracted/name)!=item['sha256']:raise ValueError('Extracted copy mismatch: '+name)
    # A new selected-source post-check, not a rehash of the complete301-file seal.
    for path,value in selected.items():
        if sha(path)!=value:raise ValueError('Selected source changed during preparation')
    result=dict(status='PASS_OFFLINE_PREBOARD_PACKAGE_ONLY',at_UTC=datetime.now(timezone.utc).isoformat(),
         candidate='hole_pipeline_20261016/soc_r2',archive=str(archive),archive_bytes=archive.stat().st_size,
         archive_sha256=sha(archive),payload_files=len(manifest)+1,selected_source_files=len(selected),
         profile_fields_matched=len(matched),extracted_CPU_mock_tests=12,corruption_rejected=True,
         python38_syntax_checked=True,PYNQ_imported_in_CPU_checks=False,board_operations=0,
         GPU=False,EDA=False,neural_inference_rerun=False,source_RTL_unchanged=True,
         unchanged_driver_and_frame_stepper=True,physical_board_correctness='NOT_RUN',
         current_board_occupancy='NOT_QUERIED',actual_display='NOT_RUN',logs=logs)
    save(HERE/('PREPARE_RESULT_'+args.tag+'.json'),result)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
