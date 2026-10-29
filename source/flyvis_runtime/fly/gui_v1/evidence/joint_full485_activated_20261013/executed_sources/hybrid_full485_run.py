"""Explicit full485 entry reusing the tested joint worker and barrier."""
import argparse,json,shutil
from pathlib import Path
from hybrid_full485 import Full485Contract,validate_full_scope,source_pins
from hybrid_joint_evidence import board_acceptance
from live_protocol import HERE,load,sha,require,host_path,write,utc
from hybrid_a3 import module

SHORT_RECEIPT=HERE/'evidence/joint_live_20261013/JOINT_ACCEPTANCE.json'
SHORT_RECEIPT_SHA='a98f54be8e85e1102d4c0f127f14ee5438bffb5558761b7ec73f8bf4df8463bf'

def preflight():
    c=Full485Contract();a,words,_=c.initial();hmod=module('h_step',c.paths['h_step'])
    require(sha(SHORT_RECEIPT)==SHORT_RECEIPT_SHA,'SHORT_ACCEPTANCE_CHANGED')
    short=load(SHORT_RECEIPT);require(short['status']=='PASS_ACTUAL_THREE_STEP_GPU_FPGA_CLOSED_LOOP','SHORT_NOT_PASSED')
    require(shutil.disk_usage(HERE).free>=2*1024**3,'PC_FREE_SPACE_2G_REQUIRED')
    return dict(status='PASS_READONLY_FULL485_PREFLIGHT',model_steps=list(range(485)),input=c.reg.binding('ON60'),
        initial_full_digest=hmod.array_hash(a),initial_H_sha256=c.wire.digest(words).hex(),initial_file_sha256=c.reg.data['model']['initial_state_sha256'],
        mapping_sha256=c.mapping_sha,short_receipt_sha256=SHORT_RECEIPT_SHA,board_acceptance=board_acceptance(c),source_sha256=source_pins(),GPU_operations=0,board_operations=0)

def checked_scope(path):
    s=load(host_path(path));c=Full485Contract();acceptance=board_acceptance(c)
    validate_full_scope(s,c,acceptance);a,words,_=c.initial();hmod=module('h_step',c.paths['h_step'])
    require(s.get('source_sha256')==source_pins(),'EXECUTABLE_SOURCE_CHANGED')
    require(s.get('initial_full_digest')==hmod.array_hash(a) and s.get('initial_H_sha256')==c.wire.digest(words).hex(),'FULL485_INITIAL_DIGEST')
    require(s.get('short_receipt_sha256')==SHORT_RECEIPT_SHA and sha(SHORT_RECEIPT)==SHORT_RECEIPT_SHA,'SHORT_ACCEPTANCE_CHANGED')
    require(s.get('board_host_files') and all(sha(p)==digest for p,digest in s['board_host_files'].items()),'BOARD_HOST_SOURCES')
    require(shutil.disk_usage(HERE).free>=2*1024**3,'PC_FREE_SPACE_2G_REQUIRED')
    return s,c,acceptance

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--execute');g.add_argument('--worker');g.add_argument('--stop');a=p.parse_args()
    if a.worker:
        from hybrid_joint_run import worker
        worker(a.worker,profile='full485')
    elif a.execute:
        from hybrid_joint_run import execute
        execute(a.execute,profile='full485')
    elif a.stop:
        root=host_path(a.stop).resolve();require(root.parent==HERE/'runtime/hybrid_full485_runs','STOP_SCOPE')
        write(root/'STOP_REQUEST.json',{'utc':utc(),'reason':'USER_STOP'})
    else:print(json.dumps(preflight(),indent=2))
