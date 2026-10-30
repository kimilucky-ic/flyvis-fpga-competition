"""PC-only result acceptance. Untrusted ZIP contains data, never executable code."""
import argparse,json,hashlib,zipfile,re,stat
from pathlib import Path,PurePosixPath
from capture_binding import save_json
from offline_check import verify,BIT_SHA,HWH_SHA
from audit_bridge import audit

def unpack(path,dest):
    dest=Path(dest);dest.mkdir(exist_ok=False)
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or len(names)>100 or sum(x.file_size for x in z.infolist())>32*1024*1024:raise ValueError('Unbounded/duplicate ZIP')
        for item in z.infolist():
            n=item.filename;p=PurePosixPath(n)
            if p.is_absolute() or '..' in p.parts or ':' in n or '\\' in n or stat.S_ISLNK(item.external_attr>>16):raise ValueError('Unsafe ZIP member')
            q=dest.joinpath(*p.parts)
            if item.is_dir():q.mkdir(parents=True,exist_ok=True);continue
            q.parent.mkdir(parents=True,exist_ok=True)
            with q.open('xb') as f:f.write(z.read(item))
    return dest

def validate_run(run,output,bundle=None):
    root=Path(bundle) if bundle else Path(__file__).resolve().parent;verify(root)
    run,output=Path(run),Path(output)
    if (run/'IN_DOUBT.json').exists():raise ValueError('Uncertain session is not accepted')
    context=json.loads((run/'RUN_CONTEXT.json').read_text());result=json.loads((run/'RESULT.json').read_text())
    if context['revision']!='LINE11_OFFICIAL_FULL_R1':raise ValueError('Wrong revision')
    if context['identity']['bit_sha256']!=BIT_SHA or context['identity']['hwh_sha256']!=HWH_SHA:raise ValueError('Wrong firmware provenance')
    if result['status']!='ONE_OFFICIAL_FRAME_ONE_PL_STEP_SAVED_ORACLE_PENDING' or result['completed_steps']!=1 or result['compute_cycles']!=2201418:raise ValueError('Wrong completion/cycles')
    if context['evidence'] not in ('CPU_MOCK_ONLY','OPERATOR_PHYSICAL_RUN_UNATTESTED'):raise ValueError('Unknown evidence level')
    if result['evidence']!=context['evidence']:raise ValueError('Mixed evidence labels')
    before=json.loads((run/'NEURAL_BEFORE.json').read_text())
    if any(before[hex(a)] for a in (0x10,0x14,0x18,0x24)) or [before[hex(a)] for a in (0x30,0x34,0x38,0x3c)]!=[45669,1513231,0x00110004,188416]:raise ValueError('Invalid initial ABI record')
    after=json.loads((run/'NEURAL_AFTER.json').read_text());regs=after['registers'];pub=after['publication']
    if regs['0x10']&1 or not regs['0x10']&8 or regs['0x14']!=1 or regs['0x24']:raise ValueError('Invalid final registers')
    own=json.loads((run/'DDR_OWNERSHIP.json').read_text())
    if pub['sequence']!=1 or pub['frame_id']!=0 or pub['cycles']!=2201418 or pub['address']!=own['base'] or own['bytes']!=188416 or own['slots']!=1:raise ValueError('DDR publication/ownership record')
    if context['evidence']=='OPERATOR_PHYSICAL_RUN_UNATTESTED':
        from board_runtime import clocks,DRIVER_SHA
        from ps_preflight import inspect as inspect_hp
        rawclock=json.loads((run/'CLOCK.json').read_text());clocks(rawclock['raw'])
        hp=json.loads((run/'HP_WIDTH.json').read_text())
        checked=inspect_hp(lambda a:hp['raw_registers'][hex(a)])
        if not checked['HP0_HP1_64bit_verified']:raise ValueError('HP evidence')
        drivers=json.loads((run/'DRIVERS.json').read_text())
        if any(drivers[k]['sha256']!=v for k,v in DRIVER_SHA.items()):raise ValueError('Official driver identity evidence')
    if json.loads((run/'capture/PROFILE.json').read_text())['evidence']!=context['evidence']:raise ValueError('Mixed capture evidence')
    from snapshot_records import decode_record
    if decode_record((run/'capture/bound/000000/record.bin').read_bytes(),0).cycles!=2201418:raise ValueError('Wrong actual record cycles')
    compare=audit(run/'capture',output,bundle=root)
    if compare['steps']!=1 or compare['state_words_compared']!=45669:raise ValueError('Exactly one complete state required')
    accepted=dict(status='PASS_OFFLINE_OPERATOR_RECORD_ALL_45669_STATES' if context['evidence']=='OPERATOR_PHYSICAL_RUN_UNATTESTED' else 'PASS_CPU_MOCK_ALL_45669_STATES',
        evidence=context['evidence'],state_words_compared=45669,mismatch_words=0,actual_input_words=721,
        bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,physical_execution_independently_observed=False,
        physical_clock_measured=False,hardware_operations_by_verifier=0)
    save_json(output/'ACCEPTANCE.json',accepted);return accepted

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('result_zip');ap.add_argument('output');a=ap.parse_args()
    dest=Path(a.output);dest.mkdir(exist_ok=False)
    r=unpack(a.result_zip,dest/'raw')
    print(json.dumps(validate_run(r,dest/'audit'),indent=2))
