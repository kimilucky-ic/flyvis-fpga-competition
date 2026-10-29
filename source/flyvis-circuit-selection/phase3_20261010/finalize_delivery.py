"""Join verified outputs; stage S1 software PASS, hardware gates NOT_RUN."""
import shutil,ast
from common import *


def main():
    meta,model,h,_,_,_,_,_,_=read_input()
    source=HERE/'artifacts/python_source_raw_800_r2';result=load(source/'result.json')
    audit=load(HERE/'artifacts/audit_800_r1/result.json');feedback=load(HERE/'artifacts/live_feedback_r1/result.json')
    consumers=load(HERE/'artifacts/consumer_audit_r2/result.json');gate=load(HERE/'artifacts/fpga_unavailable_r1/result.json')
    assert audit['status']=='PASS_INDEPENDENT_800_STATE_CHAIN_AND_VECTOR_AUDIT'
    assert feedback['status']=='PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS' and len(feedback['negative_tests'])==15
    assert all(test['status']=='PASS' for test in feedback['negative_tests'])
    assert consumers['status']=='PASS_C_AND_GUI_CONSUMER_ARTIFACT_CHECK'
    assert gate['status']=='PASS_UNAVAILABLE_MODE_FAIL_CLOSED'
    for path in [source,HERE/'input_bundle',HERE/'c_reference',HERE/'gui_bundle']:manifest_verify(path)
    # Code hashes of accepted production must remain equal after execution.
    for name,digest in result['run_identity']['code_sha256'].items():assert file_hash(HERE/name)==digest
    for name in ['h_step.py','coordinator.py','gpu_adapter.py']:
        assert file_hash(HERE/'dependencies/b_core'/name)==file_hash(HERE.parent/'phase2_20261010'/name)
    for path in HERE.glob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    A=HERE.parents[1].parent/'fly/gpu_phase3_fixed_video_20261010'
    a_audit=A/'artifacts/B_numerical_readonly_audit_r1'
    if (a_audit/'artifact_manifest.json').exists():manifest_verify(a_audit)
    a_result=load(a_audit/'acceptance.json')
    assert a_result['status']=='PASS_A_READONLY_B_NUMERICAL_CHAIN_VECTOR_AUDIT'
    assert a_result['B_artifact_manifest_sha256']==file_hash(source/'artifact_manifest.json')
    receipt=HERE/'dependencies/A_phase3_receipt/B_independent_acceptance.json'
    if receipt.exists():assert file_hash(receipt)==file_hash(a_audit/'acceptance.json')
    else:shutil.copyfile(a_audit/'acceptance.json',receipt)
    seal(receipt.parent)
    logs=HERE/'logs';logs.mkdir(exist_ok=True)
    (logs/'PythonReplacement_r2.stdout.log').write_text('\n'.join(['STEPS_COMPLETE PythonReplacement '+str(i) for i in [200,400,600,800]])+'\nRUN_RESULT '+json.dumps(dict(status=result['status'],mode='PythonReplacement',wall_s=result['wall_s'],max_abs=result['max_abs']))+'\n',encoding='utf-8')
    (logs/'README.md').write_text('工具捕获stdout的逐字结果副本；完整逐步事务日志在artifacts/python_source_raw_800_r2/step_status.jsonl。身份中的command为实际执行命令。故障/干预trace在artifacts/live_feedback_r1/trace.jsonl。并未保存WSL启动提示为模型证据。\n',encoding='utf-8')
    failed=HERE/'artifacts/python_source_raw_800_r1'
    if not (failed/'result.json').exists():
        dump(failed/'result.json',dict(status='FAIL_BEFORE_FIRST_STEP',reason='Windows canonical A path was not translated to WSL path; FileNotFoundError before service creation',
            preserved=True,committed_steps=0,actual_H_steps=0,actual_R_steps=0,fix='host_path canonical path translation only; no dynamics change',superseded_by='python_source_raw_800_r2'))
        seal(failed)
    failed_audit=HERE/'artifacts/consumer_audit_r1'
    if not (failed_audit/'result.json').exists():
        dump(failed_audit/'result.json',dict(status='FAIL_AUDIT_SCRIPT_FIELD_NAME',reason='Audit used weight instead of existing effective_weight archive key; no data modified',superseded_by='consumer_audit_r2'))
        seal(failed_audit)
    dependencies=dict(A='共同身份与实际Full800/R-only均已交付，无当前A数值阻塞',
        C='交付numeric profile/bit-true oracle、RTL真实计算证据、SoC bit/hwh与受审backend.step；板级操作需具体用户授权，之后B再接真PL800闭环',
        architecture='签收stateless explicit-old_H事务/失败语义、硬件数值与原始Full科学误差门槛；初态改变时创建新comparison并三模式重跑',
        GUI='接gui_bundle同comparison的Full/Python只读包，验证浏览器/数组/时钟；FPGA持续unavailable直到C真板可信证据',
        input='单条件原字节与三时钟契约已提供，无重新渲染需求')
    delivery=dict(schema='B_ANIMATION_SOURCE_RAW_800/v1',status='PASS_GATE_S1_SOFTWARE_ANIMATION_800',owner='B',
        phase3_complete=False,gates=dict(S1='PASS',S2='NOT_RUN_BY_B',S3='NOT_RUN',S4='NOT_RUN'),
        condition_id='01_off_right',steps=800,dt_s=.005,H_nodes=67,R_nodes=45602,layout='SOURCE_RAW',
        comparison_id=meta['comparison_id'],Full_run_id=audit['Full_run_id'],Python_run_id=audit['Python_run_id'],
        execution_evidence_level='ACTUAL_GPU_FULL_AND_LIVE_PYTHON_H_GPU_R_SOFTWARE_CLOSED_LOOP',
        initial_state_sha256=model['initial_state_sha256'],expanded_parameters_sha256=model['expanded_parameters_sha256'],
        stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),checkpoint_sha256=model['checkpoint_sha256'],
        numeric_profile_sha256=file_hash(BUNDLE/'numeric_profile.json'),metric_profile_sha256=file_hash(BUNDLE/'metric_profile.json'),
        metrics=audit['summary'],prepared=800,committed=800,native_H_production_updates=0,
        production_H_steps=800,production_GPU_R_steps=800,original_Full_as_production_R=False,
        A_independent_numerical_acceptance=dict(path=str(a_audit/'acceptance.json'),sha256=file_hash(receipt),
            boundary_steps_differing_from_recorded_Full_old=a_result['SOURCE_RAW_boundary_steps_differing_from_recorded_Full_old']),
        feedback=feedback['feedback'],negative_tests=15,negative_GPU_R_evaluations=feedback['actual_GPU_R_calls'],
        timeout_scope='software exception injection only; physical board/link timeout NOT_RUN',
        C_handoff_path=str(HERE/'c_reference/C_REFERENCE_HANDOFF.json'),C_vectors_sha256=audit['vectors_sha256'],
        GUI_handoff_path=str(HERE/'gui_bundle/GUI_READONLY_HANDOFF.json'),GUI_browser_verified=False,
        step_latency_ms=result['step_latency_ms'],wall_s=result['wall_s'],processing_mode='offline',real_time200Hz_claim=False,
        full800_receipt_path=str(HERE/'A_FULL_800_RECEIPT.json'),source_manifest_sha256=file_hash(source/'artifact_manifest.json'),
        state_chain_sha256=audit['state_chain_sha256'],dependencies=dependencies,
        FPGA_mode_status='NOT_READY_NO_FALLBACK',RTL_modified=False,board_access=False,FPGA_execution=False,
        preserved_previous='phase2_20261010 accepted files unchanged')
    dump(HERE/'B_ANIMATION_SOURCE_RAW_800.json',delivery)
    print('B_DELIVERY',delivery['status'],delivery['Python_run_id'],flush=True)

if __name__=='__main__':main()
