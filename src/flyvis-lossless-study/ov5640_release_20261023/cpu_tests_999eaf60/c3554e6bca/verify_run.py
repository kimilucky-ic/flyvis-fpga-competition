"""PC CPU audit of one saved frame/input/full-state record; no board/network access."""
import json,hashlib,subprocess,time,uuid,zipfile,sys
from pathlib import Path,PurePosixPath
import numpy as np
from offline_check import verify
from capture_binding import save_json,sha
from ddr_acceptance import compare_bits
from snapshot_records import decode_record
from ps_input import PsInput

def unpack(source,out):
    source=Path(source)
    if source.is_dir():return source
    target=out/'extracted';target.mkdir()
    with zipfile.ZipFile(source) as z:
        items=z.infolist()
        if len(items)>150 or sum(i.file_size for i in items)>64*1024*1024:raise ValueError('Oversize result archive')
        names=set()
        for i in items:
            n=PurePosixPath(i.filename)
            if n.is_absolute() or '..' in n.parts or ':' in i.filename or '\\' in i.filename or i.filename in names:raise ValueError('Unsafe/duplicate archive path')
            names.add(i.filename)
            if i.is_dir():continue
            f=target.joinpath(*n.parts);f.parent.mkdir(parents=True,exist_ok=True)
            with f.open('xb') as dst:dst.write(z.read(i))
    return target

def audit(source,output,bundle=None):
    root=Path(bundle) if bundle else Path(__file__).resolve().parent
    identity=verify(root);out=Path(output);out.mkdir(parents=True,exist_ok=False)
    try:
        run=unpack(source,out)
        if list(run.rglob('IN_DOUBT.json')):raise RuntimeError('Run has unresolved hardware/input-binding failure')
        ctx=json.loads((run/'RUN_CONTEXT.json').read_text());res=json.loads((run/'RESULT.json').read_text())
        if ctx['evidence'] not in ('CPU_MOCK_ONLY','OPERATOR_PHYSICAL_RUN_UNATTESTED'):raise ValueError('Unknown evidence')
        for k in ('bit_sha256','hwh_sha256'):
            if ctx['identity'][k]!=identity[k]:raise ValueError('Run image identity mismatch')
        if res['completed_steps']!=1 or res['sequence']!=1 or res['neural_step_id']!=0 or res['status']!='ONE_FRAME_ONE_STEP_SAVED_ORACLE_PENDING':raise ValueError('Not exactly one completed step')
        if ctx['evidence']=='OPERATOR_PHYSICAL_RUN_UNATTESTED':
            from board_capture import check_conditions,nominal_clock
            check_conditions(ctx['conditions']);nominal_clock(json.loads((run/'CLOCK_REGISTERS.json').read_text()))
            if not ctx['boot_id']:raise ValueError('Boot identity absent')
            sr=json.loads((run/'SENSOR_READBACK.json').read_text())
            if sr['writes']!=248 or any(sr['observed'].get(a)!=v for a,v in sr['expected'].items()):raise ValueError('Sensor readback mismatch')
        d=run/'bound'/'000000';prepared=json.loads((d/'PREPARED.json').read_text());committed=json.loads((d/'COMMITTED.json').read_text())
        frame=(d/'source_frame.bin').read_bytes();input_bits=(d/'input.bin').read_bytes();actual_input=(d/'actual_input.bin').read_bytes()
        actual_state=(d/'actual_state.bin').read_bytes();raw=(d/'record.bin').read_bytes();record=decode_record(raw,0)
        if len(frame)!=921600 or len(input_bits)!=2884 or len(actual_state)!=182676:raise ValueError('Incomplete frame/input/all-state payload')
        if prepared['step_id']!=0 or prepared['source_frame_id']!=0 or committed['sequence']!=1:raise ValueError('Frame/step identity')
        if prepared['frame_sha256']!=sha(frame) or prepared['input_sha256']!=sha(input_bits) or committed['state_sha256']!=sha(actual_state):raise ValueError('Binding receipt hash')
        if record.input_bits!=actual_input or actual_input!=input_bits or record.state_bits!=actual_state or record.cycles!=res['cycles']:raise ValueError('DDR record/input/state/cycle identity')
        inp=np.frombuffer(input_bits,dtype='<f4')
        if not np.isfinite(inp).all() or (inp<0).any() or (inp>1).any():raise ValueError('Input intensity domain')
        mapped=PsInput(channel_order=res['channel_order']).render(np.frombuffer(frame,dtype=np.uint8).reshape(480,640,3))
        mapping_error=float(np.max(np.abs(mapped-inp)))
        save_json(out/'mapping.json',dict(max_absolute_error=mapping_error,tolerance=3e-6,
          input_source='Actual saved ARM input bits used by oracle; PC remapping is secondary tolerance check'))
        if mapping_error>3e-6:raise RuntimeError('Frame-to-721 mapping exceeds accepted tolerance')
        expected=out/'expected_state.bin';cmd=[str((root/'reference.exe').resolve()),str(root.resolve()),str((d/'input.bin').resolve()),str(expected.resolve())]
        start=time.monotonic();proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
        (out/'oracle.log').write_bytes(proc.stdout);save_json(out/'ORACLE_COMMAND.json',dict(command=cmd,seconds=time.monotonic()-start,exit_code=proc.returncode));proc.check_returncode()
        comparison=compare_bits(actual_state,expected.read_bytes());save_json(out/'state_compare.json',comparison)
        if comparison['mismatch_words']:raise RuntimeError('Strict FP32 full-state mismatch')
        result=dict(status='PASS_SAVED_ONE_STEP_ALL_STATES',evidence='CPU_MOCK_ONLY' if ctx['evidence']=='CPU_MOCK_ONLY' else 'OFFLINE_CPU_AUDIT_OF_OPERATOR_REPORTED_BOARD_CAPTURE',
          board_execution_independently_observed=False,board_operations=0,nodes=45669,edges=1513231,completed_steps=1,
          state_words_compared=45669,input_words_compared=721,mismatch_words=0,input_sha256=sha(input_bits),state_sha256=sha(actual_state),
          source_frame_sha256=sha(frame),record_sha256=sha(raw),mapping_max_absolute_error=mapping_error,
          physical_clock_measured=False,real_time_verified=False,color_order_verified=bool(res.get('camera_color_order_verified',False)))
        save_json(out/'ACCEPTANCE.json',result);return result
    except BaseException as exc:
        save_json(out/'FAILED.json',dict(error=repr(exc),board_operations=0,automatic_retry=False));raise
if __name__=='__main__':
    if len(sys.argv) not in (2,3):raise SystemExit('verify_run.py RESULT_DIRECTORY_OR_ZIP [NEW_AUDIT_DIRECTORY]')
    output=Path(sys.argv[2]) if len(sys.argv)==3 else Path.cwd()/('line11_audit_'+uuid.uuid4().hex[:12])
    print(json.dumps(audit(sys.argv[1],output),indent=2))
