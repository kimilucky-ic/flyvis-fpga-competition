"""Human-operated bounded DDR entry. Default verifies files ONLY (Python3.8).

--execute --exclusive-board-window authorizes one exact image load, one owned
allocation, one restore and the fixed3/32/485-step plan. Never launch automatically from PC.
"""
import argparse
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import platform
import struct
import sys
import threading
import time
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parent
MANIFEST_SHA='0d9cb412dcb5a37ce32b10341437b57e2171c99c0cc1c78cb6cf107647baadee'
BIT_SHA='d365f41da4b52dc8dbd0ba751f8691da448607747a6bcf04e619ab465d956b66'
HWH_SHA='69a4332593e32852aec9dbc7b177341f3303af067ee1f182c44152744f8598f1'


def require(ok,message):
    if not ok:raise RuntimeError(message)


def digest(raw):return hashlib.sha256(raw).hexdigest()


def verify(root):
    root=Path(root);raw=(root/'release_manifest.json').read_bytes()
    require(digest(raw)==MANIFEST_SHA,'Release manifest changed')
    manifest=json.loads(raw)
    for name,info in manifest.items():
        require(Path(name).name==name,'Unsafe package name')
        data=(root/name).read_bytes()
        require(len(data)==info['bytes'] and digest(data)==info['sha256'],'Source changed: '+name)
    config=json.loads((root/'PREPARATION.json').read_text(encoding='utf-8'))
    require(config['schema']=='flyvis-line2-ddr-preparation/v1' and config['total_steps'] in (3,32,485)
            and config['release_manifest_sha256']==MANIFEST_SHA,'Preparation scope')
    for name,expected in config['startup_sha256'].items():
        require(Path(name).name==name and digest((root/name).read_bytes())==expected,'Startup source changed')
    from line11_ddr_plan import load_plan,PLAN32_SHA,PLAN485_SHA
    if config['total_steps'] in (32,485):require(digest((root/'RUN_PLAN.json').read_bytes())==config['plan_manifest_sha256'],'Run plan manifest changed')
    load_plan(root,config['total_steps'],config.get('plan_manifest_sha256'))
    return config


class PreparationClient:
    def init__(self,config):
        self.config=config;target=urlparse(config['url'])
        require(target.scheme=='http' and target.path in ('','/') and not target.username and not target.password,'Direct PC GUI origin required')
        self.http=http.client.HTTPConnection(target.hostname,target.port or 80,timeout=10)

    def post(self,route,payload,mime):
        try:
            self.http.request('POST',route,body=payload,headers={'Authorization':'Bearer '+self.config['token'],'Content-Type':mime})
            r=self.http.getresponse();raw=r.read(16385)
            require(r.status==200 and len(raw)<=16384,'PC rejected preparation; HTTP '+str(r.status))
            return json.loads(raw)
        except BaseException:self.http.close();raise

    def ready(self):
        reply=self.post('/api/full-pl-stream/prepare',json.dumps({'preparation_id':self.config['preparation_id']}).encode(),'application/json')
        require(reply['status']=='WAITING_FIRST_STEP' and reply['preparation_id']==self.config['preparation_id'],'PC session is not ready')

    def first(self,session,operator):
        output=io.BytesIO()
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
            for name in ('record_000000.bin','receipt_000000.json','RUN_CONTEXT.json'):z.write(session.output/name,name)
            z.writestr('OPERATOR.json',json.dumps(operator))
            z.writestr('TIMING.json',json.dumps(session.timing[0]))
        reply=self.post('/api/full-pl-stream/first',output.getvalue(),'application/zip')
        require(reply['status']=='FIRST_STEP_ALL_WORDS_ACCEPTED_CONTINUE','First complete state was not accepted')
        self.http.close()
        return reply['connection']


def exclusive_inventory():
    own=os.getpid();others=[];listeners=[]
    for table in ('tcp','tcp6'):
        for line in Path('/proc/net',table).read_text().splitlines()[1:]:
            fields=line.split()
            if fields[3]=='0A':listeners.append(int(fields[1].rsplit(':',1)[1],16))
    for item in Path('/proc').iterdir():
        if not item.name.isdigit() or int(item.name)==own:continue
        try:cmd=(item/'cmdline').read_bytes().replace(b'\0',b' ').decode('utf-8','replace').lower()
        except (OSError,ProcessLookupError):continue
        if any(marker in cmd for marker in ('ipykernel','flyvis','a3r1','line11_ddr_board')):others.append(dict(pid=int(item.name),command=cmd[:512]))
    blocked=sorted(set(listeners).intersection({5771,5772,5790,5791}))
    require(not others and not blocked,'Board is occupied; no load/reset/stop attempted; '+json.dumps(
        dict(other_pids=[x['pid'] for x in others],blocked_ports=blocked)))
    return dict(own_pid=own,other_compute_processes=others,listening_ports=listeners)


def live_context(root,overlay,config,inventory):
    from pynq import MMIO,PL
    from pynq.ps import Clocks
    import pynq
    tree=ET.parse(str(root/'flyvis_ddr.hwh'))
    ps=next(m for m in tree.iter('MODULE') if m.get('INSTANCE')=='ps7')
    params={p.get('NAME'):p.get('VALUE') for p in ps.iter('PARAMETER')}
    require(params['PCW_S_AXI_HP0_DATA_WIDTH']=='64' and params['PCW_USE_S_AXI_HP0']=='1','HWH HP0 profile')
    reference=float(params['PCW_CRYSTAL_PERIPHERAL_FREQMHZ'])
    slcr=Clocks._instance._slcr_mmio
    ctrl,pll,locked=(int(slcr.read(a)) for a in (0x170,0x108,0x10c))
    require(ctrl==0x200500 and pll==0x1e000 and locked&4 and abs(reference-33.333333)<.000001,'Clock does not match nominal100MHz; no clock rewrite')
    hp=MMIO(0xf8008000,0x18);rd,wr=int(hp.read(0)),int(hp.read(0x14))
    # AMD UG585 AFI_{RD,WR}CHAN_CTRL bit0: 0=64-bit, 1=32-bit.
    require(rd&1==0 and wr&1==0,'Live HP0 is not64-bit; no register rewrite')
    require(overlay.is_loaded() and Path(PL.bitfile_name).resolve()==(root/'flyvis_ddr.bit').resolve(),'Loaded overlay metadata mismatch')
    ip=overlay.ip_dict['network'];require(ip['phys_addr']==0x43c40000 and ip['addr_range']==4096,'Network MMIO address')
    return dict(schema='flyvis-line2-ddr-operator/v1',preparation_id=config['preparation_id'],
        evidence='HUMAN_EXECUTED_PHYSICAL_READS',exclusive_board_window=True,
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),pynq_version=str(pynq.__version__),machine=platform.machine(),
        bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,release_manifest_sha256=MANIFEST_SHA,
        clock=dict(clock_control=ctrl,io_pll_control=pll,pll_status=locked,reference_mhz=reference,
            raw_pynq_mhz=float(Clocks.fclk0_mhz),nominal_hz=100000000,physical_frequency_measured=False),
        hp0_read_control=rd,hp0_write_control=wr,inventory=inventory,
        cache_policy='CLEAR_FLUSH_DSB_BEFORE_ARM;INVALIDATE_DSB_IMMUTABLE_COPY_AFTER_PUBLISH',
        initial_state_readback='NOT_SUPPORTED_BY_ABI_00110004',startup_sha256=config['startup_sha256'])


def run_bounded(session,pc,operator,root):
    """Injectable orchestration; reuse accepted neural/control implementation."""
    from line11_display_client import Line11DisplayClient
    from line11_ddr_bridge import DdrAuditForwarder
    begin=time.monotonic_ns();audit_times=[];forward_times=[];commits=[]
    session.start()
    producer_begin=time.monotonic_ns()
    session.produce_next();commits.append(dict(frame_id=0,relative_ns=time.monotonic_ns()-producer_begin))
    before=time.monotonic_ns();first=session.audit_next()
    audit_times.append(dict(frame_id=0,ns=time.monotonic_ns()-before))
    before=time.monotonic_ns()
    connection=pc.first(session,operator)  # no second STEP until PC all-word acceptance
    first_gate_ns=time.monotonic_ns()-before
    client=Line11DisplayClient(connection)
    client.bind_retained_state(first.state_bits,1,operator['boot_id'])
    forwarder=DdrAuditForwarder(client,session.cookie,json.loads((session.output/'receipt_000000.json').read_text()))
    finished=threading.Event();errors=[]
    def audit():
        try:
            while not finished.is_set() or session.audited<len(session.descriptors):
                before=time.monotonic_ns();record=session.audit_next();audit_ns=time.monotonic_ns()-before
                if record is None:finished.wait(.002);continue
                audit_times.append(dict(frame_id=record.frame_id,ns=audit_ns))
                receipt=json.loads((session.output/('receipt_%06d.json'%record.frame_id)).read_text())
                before=time.monotonic_ns()
                forwarder.publish(record,receipt,session.timing[record.frame_id]['input_and_STEP_ns']/1e9)
                forward_times.append(dict(frame_id=record.frame_id,ns=time.monotonic_ns()-before))
        except BaseException as exc:
            errors.append(exc);session._fail(exc)
    auditor=threading.Thread(target=audit,name='line2-ddr-audit-display',daemon=False)
    auditor.start()
    try:
        for _ in range(len(session.inputs)-1):
            if errors:raise errors[0]
            session.produce_next()
            commits.append(dict(frame_id=len(session.descriptors)-1,relative_ns=time.monotonic_ns()-producer_begin))
    finally:
        finished.set();auditor.join(max(20,len(session.inputs)))
    require(not auditor.is_alive(),'Auditor still in flight; keep allocation and kernel')
    if errors:raise errors[0]
    result=session.finish();client.finish()
    integration=dict(clock='same board process monotonic_ns; no Windows/PS clock subtraction',
        total_start_through_finish_ns=time.monotonic_ns()-begin,
        first_step_PC_acceptance_roundtrip_ns=first_gate_ns,
        producer_start_through_last_commit_ns=commits[-1]['relative_ns'],
        commit_times=commits,audit_decode_compare_persist=audit_times,GUI_forward_serialization_roundtrip=forward_times,
        ranges_overlap='Producer and auditor overlap; do not sum these durations',
        input_plus_STEP=session.timing,GUI_paint_not_in_this_clock=True)
    from ddr_acceptance import save_new
    save_new(session.output/'INTEGRATION_TIMING.json',integration)
    # Preserve the completed allocation/state for explicit reconciliation;
    # do not auto-free, reload, reset or repeat a completed session.
    return result


def export_evidence(output,run_id):
    """After computation only: raw records + receipts, no token/config export."""
    output=Path(output);files=sorted(p for p in output.rglob('*') if p.is_file())
    require(sum(p.stat().st_size for p in files)<128000000,'Bounded evidence export size')
    manifest={str(p.relative_to(output)).replace('\\','/'):dict(bytes=p.stat().st_size,sha256=digest(p.read_bytes())) for p in files}
    archive=output.parent/('LINE2_DDR_'+run_id+'_RESULT.zip')
    before=time.monotonic_ns()
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,str(p.relative_to(output)).replace('\\','/'))
        z.writestr('EXPORT_MANIFEST.json',json.dumps(dict(run_id=run_id,files=manifest),indent=2))
    return dict(path=str(archive),sha256=digest(archive.read_bytes()),bytes=archive.stat().st_size,
                packaging_ns=time.monotonic_ns()-before,scope='POST_COMPUTE_FILESYSTEM_ONLY')


def main(argv=None):
    parser=argparse.ArgumentParser(description='Default offline verification; human-only hardware execution')
    parser.add_argument('--execute',action='store_true');parser.add_argument('--exclusive-board-window',action='store_true')
    args=parser.parse_args(argv);config=verify(ROOT)
    if not args.execute:
        print('OFFLINE_PACKAGE_VERIFIED; 0 board/GPU/camera operations');return
    require(args.exclusive_board_window,'Human exclusive board authorization required before hardware imports')
    pc=PreparationClient(config);pc.ready()  # reject wrong/stale/closed PC session BEFORE programming
    require(platform.machine()=='armv7l','Zynq ARMv7 only')
    import pynq
    require(str(pynq.__version__).startswith('2.7.'),'Prepared PYNQ2.7 only')
    require(b'xlnx,zynq-7000' in Path('/proc/device-tree/compatible').read_bytes(),'Current device is not Zynq7000')
    inventory=exclusive_inventory()
    marker=ROOT/'EXECUTION_STARTED.json'
    with marker.open('x',encoding='utf-8') as f:json.dump(dict(preparation_id=config['preparation_id'],inventory=inventory),f)
    output=ROOT/('result_'+config['preparation_id'])
    output.mkdir(exist_ok=False)
    session=None
    try:
        overlay=pynq.Overlay(str(ROOT/'flyvis_ddr.bit'),download=False)
        overlay.download()  # exactly one human-authorized load, no recovery/reload
        operator=live_context(ROOT,overlay,config,inventory)
        from ddr_memory import pynq_allocator_and_barrier
        allocator,barrier=pynq_allocator_and_barrier(output/'native',operator_authorized=True)
        native=json.loads((output/'native/identity.json').read_text())
        operator['barrier_library_sha256']=native['library_sha256']
        (output/'OPERATOR.json').write_text(json.dumps(operator,indent=2),encoding='utf-8')
        from ddr_acceptance import AcceptanceSession
        from line11_ddr_plan import load_plan
        inputs,expected,plan_id=load_plan(ROOT,config['total_steps'],config.get('plan_manifest_sha256'));steps=config['total_steps']
        session=AcceptanceSession(pynq.MMIO(0x43c40000,4096),allocator,barrier,
            [inputs[i*2884:(i+1)*2884] for i in range(steps)],
            [expected[i*182676:(i+1)*182676] for i in range(steps)],output/'records','OPERATOR_PHYSICAL_READS_UNATTESTED')
        del inputs,expected  # avoid keeping a second88MB reference on the512MB PS
        result=run_bounded(session,pc,operator,ROOT)
        print('LINE2_DDR_%d_STEPS_FINISHED '%steps+json.dumps(result))
        print('LINE2_DDR_EVIDENCE_ZIP '+json.dumps(export_evidence(output,session.run_id)))
    except BaseException as exc:
        if session is not None:session._fail(exc)
        (output/'LAUNCH_STOP.json').write_text(json.dumps(dict(error=type(exc).__name__+': '+str(exc),
            state='IN_DOUBT_KEEP_KERNEL_AND_DDR_NO_RETRY_RESET_OR_FREE')),encoding='utf-8')
        raise


if __name__=='__main__':main()
