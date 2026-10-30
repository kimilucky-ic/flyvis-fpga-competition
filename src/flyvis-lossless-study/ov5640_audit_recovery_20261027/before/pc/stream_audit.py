"""PC-only sequential oracle over immutable received packets. Never sends board commands."""
import argparse,json,os,shutil,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'bundle'))
import numpy as np
import psutil
from live_protocol import Store,atomic,canonical,sha,unpack
from ps_input import PsInput
from direct_input import DirectAreaInput
LOW_PRIORITY=getattr(subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0)

def refresh(store):
    # Atomic packet publication precedes receiver ACK. No receiver lock or writes.
    while True:
        path=store.path/('%06d.packet'%len(store.meta))
        if not path.exists():break
        raw=path.read_bytes();m,_,_=unpack(raw,store.config);store._next(m)
        store.meta.append(m);store.digests.append(sha(raw))
    if store.final is None and (store.path/'FINISH.json').exists():
        obj=json.loads((store.path/'FINISH.json').read_text());store._check_finish(obj);store.final=obj
    return len(store.meta)

def reception_busy(store):
    if store.final is not None or not store.meta:return False
    p=store.path/('%06d_receive.json'%(len(store.meta)-1))
    try:
        return time.time()-p.stat().st_mtime<2 and json.loads(p.read_text()).get('receive_to_commit_ms',0)>100
    except FileNotFoundError:return False

def run(records,config,bundle,output,progress_path,parent_alive=lambda:True,oracle=None):
    records=Path(records);bundle=Path(bundle);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    work=output/'oracle_bundle';work.mkdir()
    for name in ('edges.bin','meta.hex','initial_state.bin'):shutil.copyfile(str(bundle/name),str(work/name))
    store=Store(records,config);rows=[];commands=[];mismatch=0;start=time.monotonic();active=0.;pressure=0.;finish_seen=None
    mapper=None;last_progress=[None,0.]
    def progress(status):
        signature=(status,len(rows),len(store.meta));now=time.monotonic()
        if signature==last_progress[0] and now-last_progress[1]<1:return
        try:
            atomic(progress_path,canonical(dict(status=status,steps=len(rows),received=len(store.meta),mismatch_words=mismatch,active_seconds=active,pressure_yield_seconds=pressure,output=str(output))))
            last_progress[:]=[signature,now]
        except PermissionError:
            # Windows reader/antivirus may briefly hold this advisory UI file.
            # Durable comparisons/expected states/RESULT still fail closed.
            pass
    while True:
        if not parent_alive():raise InterruptedError('PC receiver exited; preserve partial audit')
        available=refresh(store)
        if store.final is not None:
            if finish_seen is None:finish_seen=time.monotonic()
            if store.final['status']!='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING' or store.final.get('error') is not None:raise ValueError('Producer did not finish normally')
        remaining=available-len(rows)
        if store.final is not None and remaining==0:break
        if remaining<3 and store.final is None:
            progress('WAITING_FOR_RECORDS');time.sleep(.1);continue
        if reception_busy(store):
            progress('YIELDING_TO_RECEIVER');time.sleep(.2);pressure+=.2;continue
        t=time.monotonic();first=len(rows);n=min(3,remaining);inputs=[];states=[];newrows=[]
        for k in range(first,first+n):
            m,source,r=store.read(k);error=None
            if source is not None:
                motion=m['schema']=='line11-motion-record/v4'
                if mapper is None:mapper=DirectAreaInput(48,80,'BGR') if motion else PsInput(480,800,'BGR')
                mapped=mapper.render(np.frombuffer(source,np.uint8).reshape((48,80,3) if motion else (480,800,3))).astype('<f4')
                error=float(np.max(np.abs(mapped-np.frombuffer(r.input_bits,'<f4'))))
                if error>3e-6:raise ValueError('source mapping mismatch')
            inputs.append(r.input_bits);states.append(r.state_bits)
            newrows.append(dict(step_id=k,input_sha256=sha(r.input_bits),actual_state_sha256=sha(r.state_bits),mapping_max_abs=error,timing=m['timing']))
        i=output/('%06d_inputs.bin'%first);o=output/('%06d_expected.bin'%first);i.write_bytes(b''.join(inputs));initial_sha=sha((work/'initial_state.bin').read_bytes())
        cmd=[str((bundle/'reference.exe').resolve()),str(work.resolve()),str(i.resolve()),str(o.resolve())]
        if oracle is None:
            p=subprocess.run(cmd,capture_output=True,timeout=60,creationflags=LOW_PRIORITY)
            (output/('%06d_oracle.log'%first)).write_bytes(p.stdout+p.stderr);p.check_returncode()
        else:oracle(first,n,work,i,o)
        commands.append(dict(command=cmd,first_step=first,steps=n,initial_expected_sha256=initial_sha,returncode=0))
        atomic(output/'COMMANDS.json',canonical(commands));expected=o.read_bytes()
        if len(expected)!=n*182676:raise ValueError('oracle output length')
        for j,row in enumerate(newrows):
            e=expected[j*182676:(j+1)*182676];diff=int(np.count_nonzero(np.frombuffer(e,'<u4')!=np.frombuffer(states[j],'<u4')));mismatch+=diff
            row.update(expected_state_sha256=sha(e),mismatch_words=diff,state_words=45669)
            atomic(output/('%06d_COMPARE.json'%row['step_id']),canonical(row));rows.append(row)
        # Expected feedback only, including after a mismatch. Never board feedback.
        atomic(work/'initial_state.bin',expected[-182676:]);active+=time.monotonic()-t;progress('AUDITING')
    if not rows:raise ValueError('No records')
    if not parent_alive():raise InterruptedError('PC receiver exited before completion')
    result=dict(status='PASS_ALL_SAVED_STATES' if mismatch==0 else 'FAIL_NUMERICAL_MISMATCH',evidence='OFFLINE_OPERATOR_RECORD_AUDIT' if store.meta[0]['evidence']=='OPERATOR_PHYSICAL_RUN_UNATTESTED' else 'CPU_MOCK_ONLY',
        steps=len(rows),state_words_compared=len(rows)*45669,mismatch_words=mismatch,all_neural_records_retained=True,
        source_mapping_audited=all(x['mapping_max_abs'] is not None for x in rows),source_images_transferred=source is not None,
        normal_camera_close_receipt=store.final['camera_closed'],session_status=store.final['status'],elapsed_s=time.monotonic()-start,
        active_seconds=active,pressure_yield_seconds=pressure,after_finish_seen_seconds=time.monotonic()-finish_seen,
        scheduling='PC_LOW_PRIORITY_INCREMENTAL',independent_live_observation=False,physical_frequency_measured=False,rows=rows)
    atomic(output/'RESULT.json',canonical(result));progress('COMPLETE');return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--records',required=True);parser.add_argument('--config',required=True);parser.add_argument('--bundle',required=True);parser.add_argument('--output',required=True);parser.add_argument('--parent',type=int,required=True);args=parser.parse_args()
    records=Path(args.records);parent=psutil.Process(args.parent);created=parent.create_time()
    def alive():
        try:return parent.is_running() and parent.create_time()==created
        except psutil.Error:return False
    progress=records/'AUDIT_PROGRESS.json'
    try:run(records,json.loads(Path(args.config).read_text()),args.bundle,args.output,progress,alive)
    except BaseException as exc:
        atomic(Path(args.output)/'ERROR.json',canonical(dict(status='AUDIT_ERROR',error=repr(exc))));raise
if __name__=='__main__':main()
