"""Offline full-state audit for 1..3 bridge records; never accesses hardware."""
import json, subprocess, time
from pathlib import Path
import numpy as np
from ps_input import PsInput
from snapshot_records import decode_record
from capture_binding import sha, save_json, save_new
from ddr_acceptance import compare_bits


def audit(run, output, bundle=None):
    run, output = Path(run), Path(output)
    bundle = Path(bundle) if bundle else Path(__file__).resolve().parent
    output.mkdir(exist_ok=False)
    if (run/'STOPPED.json').exists() or list(run.rglob('IN_DOUBT.json')):
        raise ValueError('uncertain run, preserve evidence')
    profile = json.loads((run/'PROFILE.json').read_text())
    if profile['schema'] != 'line11-official-bridge/v1' or profile['channel_order'] != 'BGR':
        raise ValueError('unexpected mapping profile')
    if (profile['width'], profile['height'], profile['nodes'], profile['edges']) != (800,480,45669,1513231):
        raise ValueError('dimensions/profile mismatch')
    paths = sorted((run/'bound').iterdir())
    if not 1 <= len(paths) <= 3 or len(paths) > profile['capacity']:
        raise ValueError('bounded offline audit supports 1..3 steps')
    inputs, states, hashes = [], [], []
    mapper = PsInput(height=480, width=800, channel_order='BGR')
    for k, d in enumerate(paths):
        if d.name != '%06d'%k or not d.is_dir(): raise ValueError('gap/extra record')
        p=json.loads((d/'PREPARED.json').read_text());c=json.loads((d/'COMMITTED.json').read_text())
        frame=(d/'source_frame.bin').read_bytes();inp=(d/'input.bin').read_bytes()
        actual=(d/'actual_input.bin').read_bytes();state=(d/'actual_state.bin').read_bytes()
        if len(frame)!=480*800*3 or len(inp)!=2884 or len(state)!=182676: raise ValueError('payload lengths')
        if p['step_id']!=k or p['source_frame_id']!=k or c['sequence']!=k+1: raise ValueError('binding order')
        if any(c.get(key)!=value for key,value in p.items() if key!='evidence'): raise ValueError('receipt mismatch')
        if p['frame_sha256']!=sha(frame) or p['input_sha256']!=sha(inp) or c['state_sha256']!=sha(state): raise ValueError('hash mismatch')
        record=decode_record((d/'record.bin').read_bytes(),k)
        if inp!=actual or record.input_bits!=actual or record.state_bits!=state: raise ValueError('record binding mismatch')
        mapped=mapper.render(np.frombuffer(frame,np.uint8).reshape(480,800,3))
        error=float(np.max(np.abs(mapped-np.frombuffer(inp,dtype='<f4'))))
        if not np.isfinite(error) or error>3e-6: raise ValueError('mapping mismatch')
        inputs.append(inp);states.append(state)
        hashes.append(dict(step=k,frame_sha256=sha(frame),input_sha256=sha(inp),state_sha256=sha(state),mapping_max_abs=error))
    save_new(output/'inputs.bin',b''.join(inputs))
    cmd=[str((bundle/'reference.exe').resolve()),str(bundle.resolve()),str((output/'inputs.bin').resolve()),str((output/'expected.bin').resolve())]
    start=time.monotonic();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    save_new(output/'oracle.log',p.stdout)
    save_json(output/'COMMAND.json',dict(command=cmd,exit_code=p.returncode,seconds=time.monotonic()-start))
    p.check_returncode()
    expected=(output/'expected.bin').read_bytes()
    if len(expected)!=len(states)*182676: raise ValueError('oracle output length')
    per_step=[compare_bits(state,expected[k*182676:(k+1)*182676]) for k,state in enumerate(states)]
    comparison=dict(steps=per_step,mismatch_words=sum(x['mismatch_words'] for x in per_step))
    save_json(output/'COMPARE.json',comparison)
    if comparison['mismatch_words']: raise ValueError('strict FP32 all-state mismatch')
    result=dict(status='PASS_OFFLINE_BOUND_RECORD_AUDIT',evidence=profile['evidence'],steps=len(states),
        state_words_compared=len(states)*45669,mismatch_words=0,records=hashes,
        simulation_or_board_verified=False,clock_measured=False,board_operations=0)
    save_json(output/'RESULT.json',result)
    return result
