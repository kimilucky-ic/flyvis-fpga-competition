"""Bounded CPU regression and readback of the named 3-step software GPU check."""
import ast,contextlib,io,json,unittest
from unittest.mock import patch
import numpy as np
from live_protocol import HERE,load,require,sha,utc,write,Registry
from hybrid_v2 import V2Contract

OUT=HERE/'evidence/joint_prepare_20261013'
GPU=HERE/'runtime/hybrid_software_checks/ca3f3c24c04d4c5d9c0dde9d36c8a511'


def main():
    OUT.mkdir(exist_ok=True)
    import verify_hybrid_prepare as legacy
    # Redirect all generated regression receipts, never overwrite yesterday.
    with patch.object(legacy,'OUT',OUT/'legacy'),contextlib.redirect_stdout(io.StringIO()):
        legacy.main()
    from test_hybrid_v2 import V2Protocol
    log=io.StringIO();result=unittest.TextTestRunner(stream=log).run(unittest.defaultTestLoader.loadTestsFromTestCase(V2Protocol))
    (OUT/'v2_tests.log').write_text(log.getvalue(),encoding='utf8');require(result.wasSuccessful(),'V2_FAILED')
    reg=Registry();c=V2Contract();write(OUT/'joint_status.json',c.readiness())
    receipt=load(GPU/'result.json');scope=load(GPU/'scope.json')
    for name,digest in load(GPU/'manifest.json')['files'].items():require(sha(GPU/name)==digest,'GPU_RECORD_CHANGED '+name)
    for name,digest in scope['source_sha256'].items():require(sha(HERE/name)==digest,'GPU_TESTED_SOURCE_CHANGED '+name)
    require(receipt['status']=='PASS_GPU_SOFTWARE_PREFLIGHT_ONLY' and receipt['PL_execution'] is False,'GPU_SCOPE')
    require(receipt['model']==reg.data['model'] and receipt['input_sha256']==reg.pins['stimulus_ON60']['sha256'],'GPU_IDENTITY')
    states=np.load(GPU/'software_mixed_states.npy');flows=np.load(GPU/'official_flow.npy');stimulus=np.load(GPU/'stimulus_721.npy')
    require(states.shape==(3,45669) and flows.shape==(3,2,721) and np.isfinite(flows).all(),'GPU_SHAPES')
    np.testing.assert_array_equal(stimulus,reg.input('ON60')[0,200:203,0])
    a,old,_=c.initial();checked=0
    for j,k in enumerate(range(200,203)):
        p=GPU/f'candidates_{k}.npz';arrays=dict(np.load(p));payload=(GPU/f'software_reference_request_{k}.bin').read_bytes()
        candidate=(GPU/f'software_reference_H_{k}.bin').read_bytes()
        np.testing.assert_array_equal(arrays['old_full'],a)
        require(payload[:c.wire.WORD_BYTES]==old,'CANONICAL_SOFTWARE_RECURRENCE')
        require(payload==old+c.wire.encode_activity(arrays['chemical_H'])+c.wire.encode_activity(arrays['x_full'][c.h]),'CURRENT_GPU_PAYLOAD')
        checked+=c.validate_H(payload,candidate)['integer_values_checked']
        np.testing.assert_array_equal(states[j,c.h],c.decode(candidate));np.testing.assert_array_equal(states[j,c.r],arrays['new_R'])
        require(receipt['rows'][j]['R_vs_original_Full_max_abs']==0 and receipt['rows'][j]['native_H_production_updates']==0,'R_OR_H_GUARD')
        a=states[j];old=candidate
    names=['hybrid_v2.py','hybrid_gpu.py','hybrid_gpu_check.py','hybrid_joint_registry.json','test_hybrid_v2.py','verify_joint_prepare.py','server.py']
    for name in names:
        if name.endswith('.py'):ast.parse((HERE/name).read_text(encoding='utf8'))
    import sys
    require(not any(m in sys.modules for m in ('torch','flyvis','cv2','pynq')),'DEVICE_IMPORT_IN_READBACK')
    old=load(OUT/'legacy/verification.json')
    report=dict(status='PASS_SOFTWARE_READINESS_ONLY',utc=utc(),CPU_tests=old['CPU_tests']+result.testsRun,
        legacy_CPU_tests=old['CPU_tests'],v2_CPU_tests=result.testsRun,JS_tests=old['JS_tests'],
        GPU_preflight=dict(path=str(GPU),run_id=receipt['run_id'],status=receipt['status'],source='CURRENT_GPU_R_AND_CHEMICAL_CPU_H_REFERENCE',
            software_reference_words_checked=checked,result_sha256=sha(GPU/'result.json'),manifest_sha256=sha(GPU/'manifest.json')),
        preserved_39_source_pins=old['original_39_pins'],legacy_evidence_unmodified=True,
        new_board_operations=0,new_GUI_launches=0,FPGA_closed_loop='NOT_RUN',video='NOT_CREATED_PENDING_REAL_JOINT_RESULTS',
        files_sha256={n:sha(HERE/n) for n in names})
    write(OUT/'verification.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
