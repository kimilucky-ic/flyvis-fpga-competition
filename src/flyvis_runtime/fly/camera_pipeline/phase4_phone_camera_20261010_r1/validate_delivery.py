"""Read-only checks of current preparation and all prior sealed camera evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import sha256,utc_now
from camera_pipeline.phase4_phone_camera_20261010_r1.config import ROOT,write_new,settings_sha

def prior_seals():
    camera=ROOT.parent
    specifications=[(camera/'results/validation/manifest.json',camera),
                    (camera/'phase2/results/manifest.json',camera),
                    (camera/'controlled_video_20261010_r1/manifest.json',camera/'controlled_video_20261010_r1'),
                    (camera/'phase3_input_20261010_r1/manifest.json',camera/'phase3_input_20261010_r1'),
                    (camera/'stimulus_library_extension_20261010_r1/manifest.json',camera/'stimulus_library_extension_20261010_r1')]
    checked=[]
    for manifest,base in specifications:
        document=json.loads(manifest.read_text(encoding='utf-8'));files=document['files']
        pairs=list(files.items()) if isinstance(files,dict) else [(r['path'],r['sha256']) for r in files]
        for name,digest in pairs:
            if sha256(base/name)!=digest:raise ValueError('Earlier sealed file changed: '+str(base/name))
        checked.append({'manifest':str(manifest),'files_verified':len(pairs),'status':'PASS'})
    protected=json.loads((camera/'logs/protected_before.json').read_text(encoding='utf-8'))['protected_files']
    for name,digest in protected.items():
        if sha256(name)!=digest:raise ValueError('Protected Golden Reference changed: '+name)
    upstream=camera.parent/'upstream/flyvis'
    status=subprocess.check_output(['git','-C',str(upstream),'status','--porcelain','--untracked-files=no'],text=True)
    commit=subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'],text=True).strip()
    if status or commit!='92b3845cc426dd309a1a0e1b3890156c42e14021':raise ValueError('Original tracked source identity changed')
    return {'prior_seals':checked,'protected_golden_files_verified':len(protected),'upstream_tracked_clean':True,'source_commit':commit}

def browser_checks():
    assets={p.name:sha256(p) for p in (ROOT/'web').iterdir() if p.is_file()};reports=[]
    for path in sorted((ROOT/'validation/browser_sessions_r2').glob('*/presentation.json')):
        spec=json.loads(path.read_text(encoding='utf-8'))
        if spec['state'] not in ('complete','stop'):continue
        if not spec['validation_only'] or spec['camera_capture'] or spec['source_assets_sha256']!=assets:
            raise ValueError('Current browser software test identity mismatch')
        if spec['settings_sha256']!=settings_sha(spec['settings']):raise ValueError('Browser parameter identity mismatch')
        log=path.parent/'events.jsonl';entries=[json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
        kinds=[r['client_event']['kind'] for r in entries]
        if kinds.count('start')!=1 or kinds.count('complete')!=1 or 'standby' not in kinds:raise ValueError('Current final hold/standby flow was not completed')
        reports.append({'session_id':spec['phone_stimulus_session_id'],'family':spec['settings']['family'],'direction':spec['settings']['direction_deg'],
                        'events':len(entries),'frame_callbacks':kinds.count('frame'),'parameter_sha256':spec['settings_sha256'],
                        'presentation_sha256':sha256(path),'events_sha256':sha256(log),'state':spec['state'],
                        'validation_only':True,'physical_phone_test':False})
    return reports

def verify_new_seal():
    path=ROOT/'manifest.json'
    if not path.exists():return {'status':'NOT_SEALED_YET'}
    manifest=json.loads(path.read_text(encoding='utf-8'))
    for name,digest in manifest['files'].items():
        target=(ROOT/name).resolve()
        if not target.is_relative_to(ROOT) or sha256(target)!=digest:raise ValueError('New delivery seal changed: '+name)
    return {'status':'PASS','files_verified':len(manifest['files'])}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seal',action='store_true');args=parser.parse_args()
    report={'schema':'phase4-preparation-readonly-validation-v1','created_utc':utc_now(),**prior_seals(),
            'browser_tests':browser_checks(),'camera_opened':False,'new_capture_executed':False,'new_neural_inference_executed':False,'board_used':False}
    if args.seal:
        files={str(p.relative_to(ROOT)):sha256(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and
               '__pycache__' not in p.parts and p.name!='manifest.json' and p.parts[len(ROOT.parts)] not in
               ('phone_sessions','recordings','inputs','preview_checks','capture_requests')}
        write_new(ROOT/'manifest.json',{'schema':'phase4-preparation-seal-v1','created_utc':utc_now(),'files':files,
                                      'runtime_output_directories_excluded':True})
    report['new_seal']=verify_new_seal()
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
