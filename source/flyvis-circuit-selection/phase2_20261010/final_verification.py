"""Read-only cross-check of accepted manifests, input identities and local links."""
from pathlib import Path
import json, re, subprocess
import numpy as np
from h_step import HUpdater, file_hash
from run_closed_loop import manifest_verify, validate_parameters

HERE=Path(__file__).resolve().parent
ART=HERE/'artifacts'
FPGA=HERE.parents[1]
A=HERE.parents[2]/'fly/gpu_phase2'


def load(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def main():
    out=ART/'closeout_verification'
    if out.exists():raise SystemExit('Existing verification preserved')
    checks=[]
    for name in ['full_cpu_r2','source_gpu_r1','aggregate_gpu_r1','live_feedback_r1',
            'full_gpu_reference_a','source_gpu_native_r1','aggregate_gpu_native_r1',
            'live_feedback_native_r1','reproduce_native_prefix_r1','native_gpu_inputs','native_gpu_step_io']:
        entries=load(ART/name/'artifact_manifest.json')
        for entry in entries:
            file=ART/name/entry['path'].replace('\\','/')
            assert file.stat().st_size==entry['bytes'] and file_hash(file)==entry['sha256'],str(file)
        checks.append(dict(scope=name,manifest_entries_verified=len(entries)))
    bundles=[]
    for name in ['reference_bundle_v1','reference_bundle_gpu_native_v1','init_cpu_r2']:
        entries=manifest_verify(A/'artifacts'/name)
        bundles.append(dict(bundle=name,manifest_entries_verified=len(entries)))
    native=A/'artifacts/reference_bundle_gpu_native_v1'
    cpu=A/'artifacts/reference_bundle_v1'
    u=HUpdater(ART/'native_gpu_inputs/static_boundary_gpu_native.npz')
    validate_parameters(u,native/'expanded_parameters.npz')
    for name in ['initial_state_full.npy','stimulus.npy','time.npy','candidates/B_T5c/node_map.csv','candidates/B_T5c/edge_partition_ids.npz']:
        assert file_hash(native/name)==file_hash(cpu/name)
    assert file_hash(native/'initial_state_full.npy')==file_hash(A/'artifacts/init_cpu_r2/initial_state_full.npy')
    snapshot=HERE/'dependencies/a_snapshot'
    expected=load(ART/'source_gpu_native_r1/run_identity.json')['A_snapshot_sha256']
    for name,digest in expected.items():assert file_hash(snapshot/name)==file_hash(A/name)==digest
    audit=load(ART/'final_native_audit/result.json')
    handoff=load(HERE/'handoff.json')
    assert handoff['status']==audit['status']=='PASS_SOFTWARE_CLOSED_LOOP'
    assert handoff['comparison_id']==audit['comparison_id']
    assert handoff['tolerance']['violations']==0 and handoff['native_H_production_updates']==0
    assert not handoff['final_FPGA_candidate_frozen']
    document_checks=[]
    for file in [HERE/'REPORT.md',HERE/'README.md',HERE/'EXECUTION_RECORD.md',HERE/'H_STEP_INTERFACE.md',
            HERE/'ABLATION_PROPOSALS.md',HERE.parent/'README.md',FPGA/'docs/workstreams/flyvis-circuit-selection.md']:
        count=0
        for link in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if link.startswith(('https:','http:','#')):continue
            assert (file.parent/link).exists(),(str(file),link)
            count+=1
        document_checks.append(dict(document=str(file.relative_to(FPGA)),links_checked=count))
    upstream=HERE.parents[2]/'fly/upstream/flyvis'
    git_status=subprocess.run(['git','-C',str(upstream),'status','--short'],check=True,capture_output=True,text=True).stdout
    assert not git_status.strip()
    out.mkdir()
    result=dict(status='PASS_FINAL_SOFTWARE_DELIVERY_VERIFICATION',evidence_level='SOFTWARE_ARTIFACT_AND_IDENTITY_AUDIT',
        accepted_manifests=checks,input_bundles=bundles,documents=document_checks,
        main_gate=audit['status'],comparison_id=audit['comparison_id'],
        all_H_native_parameters_exact=True,shared_a0_stimulus_time_mapping_bytes_identical=True,
        A_live_sources_match_used_snapshot=True,upstream_git_status_clean=True,
        code_sha256=file_hash(Path(__file__)),
        limits='No new simulation, synthesis or hardware test in this final verification; source cache files are excluded from evidence manifest')
    dump(out/'result.json',result)
    # Preserve the audit/export/reporting implementation used in this delivery.
    copies=out/'code_snapshot';copies.mkdir()
    import shutil
    for name in ['final_verification.py','audit_results.py','export_step_io.py','prepare_native_profile.py','render_stage2.py','build_delivery.py','seal_artifacts.py']:
        shutil.copyfile(HERE/name,copies/name)
    manifest=[dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=file_hash(p))
        for p in sorted(HERE.rglob('*')) if p.is_file() and 'runtime' not in p.relative_to(HERE).parts
        and '__pycache__' not in p.relative_to(HERE).parts and p!=HERE/'artifact_manifest.json']
    dump(HERE/'artifact_manifest.json',dict(schema='flyvis-B-phase2-delivery-manifest/v1',
        files=manifest,evidence_cache_excluded=True))
    print(json.dumps(dict(status=result['status'],accepted_entries=sum(r['manifest_entries_verified'] for r in checks),
        input_bundle_entries=sum(r['manifest_entries_verified'] for r in bundles),
        formal_delivery_files=len(manifest),formal_delivery_bytes=sum(r['bytes'] for r in manifest))),flush=True)


if __name__=='__main__':main()
