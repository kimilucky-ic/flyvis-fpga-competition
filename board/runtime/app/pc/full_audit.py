"""PC only. Ordered strict-FP32 oracle in <=3-step chunks, expected-state feedback."""
import json,shutil,subprocess,time
from pathlib import Path
import numpy as np
from live_protocol import atomic,canonical,sha
from ps_input import PsInput
from direct_input import DirectAreaInput

def audit(store,bundle,output):
    bundle=Path(bundle);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    if store.final is None:raise ValueError('no producer completion receipt')
    count=len(store.meta);work=output/'oracle_bundle';work.mkdir()
    for name in ('edges.bin','meta.hex','initial_state.bin'):shutil.copyfile(str(bundle/name),str(work/name))
    mapper=DirectAreaInput(48,80,'BGR') if store.config.get('motion_condition','demo')!='demo' else PsInput(480,800,'BGR');rows=[];inputs=[];states=[];start=time.monotonic()
    for k in range(count):
        m,source,r=store.read(k);error=None
        if source is not None:
            mapped=mapper.render(np.frombuffer(source,np.uint8).reshape((48,80,3) if m['schema']=='line11-motion-record/v4' else (480,800,3))).astype('<f4')
            actual=np.frombuffer(r.input_bits,'<f4');error=float(np.max(np.abs(mapped-actual)))
            if error>3e-6:raise ValueError('source mapping mismatch step '+str(k))
        inputs.append(r.input_bits);states.append(r.state_bits)
        rows.append(dict(step_id=k,input_sha256=sha(r.input_bits),actual_state_sha256=sha(r.state_bits),mapping_max_abs=error,
                         timing=m['timing']))
    mismatch=0;commands=[]
    for first in range(0,count,3):
        n=min(3,count-first);i=output/('%06d_inputs.bin'%first);o=output/('%06d_expected.bin'%first)
        i.write_bytes(b''.join(inputs[first:first+n]));initial_sha=sha((work/'initial_state.bin').read_bytes())
        cmd=[str((bundle/'reference.exe').resolve()),str(work.resolve()),str(i.resolve()),str(o.resolve())]
        p=subprocess.run(cmd,capture_output=True,timeout=60);(output/('%06d_oracle.log'%first)).write_bytes(p.stdout+p.stderr)
        commands.append(dict(command=cmd,first_step=first,steps=n,initial_expected_sha256=initial_sha,returncode=p.returncode))
        atomic(output/'COMMANDS.json',canonical(commands));p.check_returncode();expected=o.read_bytes()
        if len(expected)!=n*182676:raise ValueError('oracle output length')
        for j in range(n):
            k=first+j;e=expected[j*182676:(j+1)*182676]
            diff=int(np.count_nonzero(np.frombuffer(e,'<u4')!=np.frombuffer(states[k],'<u4')))
            rows[k].update(expected_state_sha256=sha(e),mismatch_words=diff,state_words=45669);mismatch+=diff
            atomic(output/('%06d_COMPARE.json'%k),canonical(rows[k]))
        # Never reset to the observed board state, including after a mismatch.
        atomic(work/'initial_state.bin',expected[-182676:])
    physical=store.meta[0]['evidence']=='OPERATOR_PHYSICAL_RUN_UNATTESTED'
    result=dict(status='PASS_ALL_SAVED_STATES' if mismatch==0 else 'FAIL_NUMERICAL_MISMATCH',
                evidence='OFFLINE_OPERATOR_RECORD_AUDIT' if physical else 'CPU_MOCK_ONLY',steps=count,
                state_words_compared=count*45669,mismatch_words=mismatch,all_neural_records_retained=True,
                source_mapping_audited=all(x['mapping_max_abs'] is not None for x in rows),source_images_transferred=source is not None,normal_camera_close_receipt=store.final['camera_closed'],session_status=store.final['status'],
                elapsed_s=time.monotonic()-start,independent_live_observation=False,physical_frequency_measured=False,
                rows=rows)
    atomic(output/'RESULT.json',canonical(result));return result
