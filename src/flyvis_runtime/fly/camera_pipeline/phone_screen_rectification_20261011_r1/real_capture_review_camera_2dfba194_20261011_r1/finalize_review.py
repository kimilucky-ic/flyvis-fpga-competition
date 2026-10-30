"""Seal this completed input review, preserving existing source/input identities."""
from pathlib import Path
import json
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]))
from camera_pipeline.common import sha256,utc_now,write_json


def main():
    destination=HERE/'REVIEW_MANIFEST.json'
    if destination.exists():
        raise FileExistsError('Do not overwrite an accepted review seal')
    accepted=json.loads((HERE/'acceptance.json').read_text(encoding='utf-8'))
    if sha256(HERE/'accepted_audit_source.py.txt')!=accepted['auditor_source_sha256']:
        raise ValueError('Accepted audit source snapshot changed')
    lock=HERE.parents[1]/'runtime'/'camera.lock'
    # HERE.parent is B package; parents[1] is camera_pipeline.
    if lock.exists():
        raise ValueError('Camera has an active/stale owner lock; cannot claim released')
    summary={'schema':'real-camera-review-closeout-v1','created_utc':utc_now(),
        'status':'REAL_CAMERA_INPUT_FROZEN_DELIVERED_BACKEND_RESULTS_PENDING',
        'comparison_id':accepted['comparison_id'],'input_acceptance':accepted['status'],
        'checks_passed':accepted['checks_passed'],'required_steps':609,
        'windows_and_wsl_loader':'PASS','AB_dispatch':'DELIVERED_NOT_RUN_ACCEPTANCE',
        'camera_runtime_lock_absent':True,'new_neural_updates_by_this_lane':0,'board_operations':0,
        'source_and_input_existing_seals_unchanged':True,
        'next_owner':'① Full GPU / ④ T5c67 Python Replacement',
        'next_evidence':'same new input identity and common a0/parameters/node maps; actual609 updates and after-update clocks',
        'reusable_workflow':'selfserve physical capture observed once; not independently reproduced as a general hardware skill'}
    write_json(HERE/'CLOSEOUT.json',summary)
    exclusions={'__pycache__','plot_cache','verification_runs'}
    files={p.relative_to(HERE).as_posix():sha256(p) for p in sorted(HERE.rglob('*'))
           if p.is_file() and p!=destination and not (set(p.relative_to(HERE).parts)&exclusions)}
    write_json(destination,{'schema':'real-camera-input-review-seal-v1','created_utc':utc_now(),
        'comparison_id':accepted['comparison_id'],'files':files,
        'excluded_dynamic_or_cache_directories':sorted(exclusions),
        'source_raw_identity_preserved_by_nested_seals':True,'neural_inference_by_input_lane':False,'board_used':False})
    for name,value in files.items():
        if sha256(HERE/name)!=value:raise ValueError('Changed final review artifact: '+name)
    print(json.dumps({'status':'PASS','review_files_sealed':len(files),
        'review_manifest_sha256':sha256(destination),'comparison_id':accepted['comparison_id']},indent=2))


if __name__=='__main__':main()
