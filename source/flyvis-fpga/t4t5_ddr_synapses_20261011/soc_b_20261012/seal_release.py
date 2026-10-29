"""Seal the accepted full-SoC candidate; never programs or contacts a board."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,shutil,xml.etree.ElementTree as ET,zipfile
import psutil
P=Path(__file__).resolve().parent
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
B=P/load(P/'LATEST_BUILD.json')['build']
system=load(B/'SYSTEM_AUDIT.json');physical=load(B/'IMPLEMENTATION_AUDIT.json')
simrun=load(B/'stages/simulate_15/RUNTIME.json');implrun=load(B/'stages/implement_1/RUNTIME.json')
assert system['status']=='PASS_ACTUAL_PRODUCTION_BD_SYSTEM_FILE_AUDIT'
assert physical['status']=='PASS_FULL_SOC_ROUTED_REPORTS'
assert all(r['exit_code']==0 and r['stop_reason'] is None for r in (simrun,implrun))
for name,value in system['source_sha256'].items(): assert sha(B/'source'/name)==value
for name,value in system['generated_file_sha256'].items(): assert sha(B/name)==value
for name,value in physical['report_sha256'].items(): assert sha(B/name)==value
for name,identity in physical['bit_hwh'].items(): assert sha(B/name)==identity['sha256']
original=load(B/'INPUT_IDENTITY.json')
for name,value in original['rom_sha256'].items(): assert sha(B/'rom'/name)==value
for name in ('axi_edge_reader.sv','ddr_synapse_core.sv','ddr_synapse_top.sv','edge_fifo.sv'):
    assert sha(B/'source'/name)==original['source_sha256'][name]
    assert sha(P.parent/'pipeline_a_20261012/rtl'/name)==original['source_sha256'][name]

# Read the actual BIT header and payload length, then the delivered HWH.
raw=(B/'flyvis_b.bit').read_bytes();position=2+int.from_bytes(raw[:2],'big')
assert raw[position:position+2]==b'\x00\x01';position+=2;header={}
for tag in ('a','b','c','d'):
    assert raw[position]==ord(tag);position+=1
    length=int.from_bytes(raw[position:position+2],'big');position+=2
    header[tag]=raw[position:position+length].rstrip(b'\0').decode('ascii');position+=length
assert raw[position]==ord('e');position+=1
payload_bytes=int.from_bytes(raw[position:position+4],'big');position+=4
assert position+payload_bytes==len(raw)
assert header['a'].startswith('b_soc_wrapper;') and 'Version=2026.1.1;' in header['a']
assert header['b']=='7z020clg400'
hwh=ET.parse(B/'flyvis_b.hwh').getroot()
assert hwh.find('SYSTEMINFO').attrib==dict(ARCH='zynq',DEVICE='7z020',NAME='b_soc',PACKAGE='clg400',SPEEDGRADE='-2')
modules={m.attrib['INSTANCE']:m for m in hwh.findall('.//MODULE')}
def params(name): return {e.attrib['NAME']:e.attrib['VALUE'] for e in modules[name].findall('./PARAMETERS/PARAMETER')}
engine=params('engine');ps=params('ps7');reset=params('reset')
for k,v in dict(H_COUNT='5768',SOURCE_COUNT='16402',EDGE_COUNT='433880',WEIGHT_COUNT='645',AXI_TIMEOUT='65536',STEP_TIMEOUT='50000000',C_BASEADDR='0x43C20000',C_HIGHADDR='0x43C3FFFF').items():assert engine[k]==v
assert ps['PCW_FPGA0_PERIPHERAL_FREQMHZ']=='100' and ps['PCW_USE_S_AXI_HP0']=='1' and ps['PCW_S_AXI_HP0_DATA_WIDTH']=='64'
assert reset['C_EXT_RESET_HIGH']=='0' and reset['C_AUX_RESET_HIGH']=='1'
aperture=next(e.attrib for e in hwh.findall('.//MEMRANGE') if e.attrib.get('ADDRESSBLOCK')=='HP0_DDR_LOWOCM')
assert int(aperture['BASEVALUE'],16)==0 and int(aperture['HIGHVALUE'],16)==0x3fffffff
owned_alive=[]
for run in (simrun,implrun):
    for item in run['processes']:
        try:
            proc=psutil.Process(item['pid'])
            if abs(proc.create_time()-item['created'])<0.001:owned_alive.append(item)
        except psutil.NoSuchProcess: pass
assert not owned_alive,owned_alive

release=P/'candidate/b_soc_20261012_222612_100mhz';release.mkdir(parents=True,exist_ok=True)
for name in ('flyvis_b.bit','flyvis_b.hwh'):
    target=release/name
    if target.exists():assert sha(target)==sha(B/name)
    else:shutil.copyfile(B/name,target)
shutil.copyfile(P/'arm_controller.py',release/'arm_controller.py')
archive=release/'flyvis_b_BIT_HWH.zip'
if not archive.exists():
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as out:
        for name in ('flyvis_b.bit','flyvis_b.hwh'):out.write(release/name,name)
with zipfile.ZipFile(archive) as z:
    assert z.namelist()==['flyvis_b.bit','flyvis_b.hwh']
    for name in z.namelist(): assert hashlib.sha256(z.read(name)).hexdigest()==sha(B/name)
release_identity=dict(status='PASS_BIT_HWH_IDENTITY_BOARD_NOT_RUN',bit_header=header,bit_payload_bytes=payload_bytes,
    HWH_params={k:engine[k] for k in ('H_COUNT','SOURCE_COUNT','EDGE_COUNT','WEIGHT_COUNT','AXI_TIMEOUT','STEP_TIMEOUT','C_BASEADDR','C_HIGHADDR')},
    HP0_aperture=aperture,clock_MHz=100,reset_EXT_HIGH=0,reset_AUX_HIGH=1,
    files={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in release.iterdir() if f.is_file()},
    system_audit_sha256=sha(B/'SYSTEM_AUDIT.json'),implementation_audit_sha256=sha(B/'IMPLEMENTATION_AUDIT.json'),
    frozen_core_and_all_five_ROM_unchanged=True,owned_processes_still_alive=owned_alive,board_IO=0,GPU=0)
save(P/'RELEASE_IDENTITY.json',release_identity)
history=P/'history/20261012_2023';history.mkdir(parents=True,exist_ok=True)
for name in ('SOC_RESULT.json','MILESTONE_RESULT.md','MANIFEST_SHA256.json'):
    if (P/name).exists() and not (history/name).exists():shutil.copyfile(P/name,history/name)
status='PASS_FULL_B_SOC_SYSTEM_SIM_ROUTE_BIT_HWH_BOARD_NOT_RUN'
result=dict(at=datetime.now(timezone(timedelta(hours=8))).isoformat(),status=status,
    design='b_soc_wrapper',part=physical['part'],tool=physical['tool'],build=str(B.relative_to(P)),candidate=str(release.relative_to(P)),
    full_system_simulation=system['counters'],simulation_warnings=system['intentional_DDR_timeout_recommendation_warnings'],
    resources=physical['resources'],timing=physical['timing'],HP0_timing=physical['HP0_timing'],
    DRC_rules=physical['DRC_rules'],check_timing=physical['check_timing'],route=physical['route'],
    methodology_violations=physical['methodology_violations'],clock_MHz=100,
    native_reset_synchronizer_exceptions_only=True,
    runtime={label:{k:r[k] for k in ('wall_seconds','peak_working_set_MiB','peak_private_MiB','min_free_MiB','min_commit_MiB','stop_reason')} for label,r in [('system_simulation',simrun),('full_SoC_implementation',implrun)]},
    bit_hwh=physical['bit_hwh'],board_IO=0,GPU=0,real_HP0_bandwidth_MBps=None,actual_board_step_latency_ms=None,
    conditional_simulation_compute_ms=system['counters']['compute_cycles']/100000,
    edge_bytes_per_step=3471040,edge_only_MBps_required_for_5ms=694.208,
    unresolved=['Actual board DDR/HP0 throughput and CMA cache behavior','ARM MMIO state load/candidate readback wall time','GPU/PL common old-state and COMMIT integration','Independent future board authorization and availability'],
    next_action='After separate board authorization and A release, load this exact candidate and perform one bounded ARM/DDR compute/readback comparison.')
save(P/'SOC_RESULT.json',result)
print(json.dumps(dict(status=status,candidate=str(release),bit_hwh=physical['bit_hwh']),ensure_ascii=False))
