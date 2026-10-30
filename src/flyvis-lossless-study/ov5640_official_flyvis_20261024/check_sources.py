"""No EDA process: source identities, recorded interfaces and Tcl grammar only."""
from pathlib import Path
import hashlib,json,re,zipfile,xml.etree.ElementTree as ET
import tkinter
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,x):(ROOT/'evidence'/n).write_text(json.dumps(x,indent=2)+'\n')
z=zipfile.ZipFile(r'D:\BaiduNetdiskDownload\正点原子\4_Source_Code\5_PYNQ_Design\ZYNQ_7020_PYNQ.zip')
m=json.loads((ROOT/'BASELINE.json').read_text())
for name,expected in m.items():
 data=z.read(name) if name.startswith('6_ov5640_lcd/') else (REPO/name).read_bytes()
 assert sha(data)==expected,name
for p in (ROOT/'neural').iterdir():
 assert p.read_bytes()==(REPO/'flyvis-lossless-study/ov5640_reset_20261023/build_r7'/p.name).read_bytes(),p
for p in (ROOT/'software').iterdir():
 if p.name not in ['official_bridge.py','audit_bridge.py']:
  assert p.read_bytes()==(REPO/'flyvis-lossless-study/ov5640_single_r2_20261024/bundle'/p.name).read_bytes(),p
assert (ROOT/'software/edges.bin').stat().st_size==1513231*8
assert (ROOT/'software/initial_state.bin').stat().st_size==45669*4
source='6_ov5640_lcd/vivado/ov5640_lcd/ov5640_lcd.srcs/'
assert (ROOT/'vendor/base.bd').read_bytes()==z.read(source+'sources_1/bd/base/base.bd')
assert (ROOT/'vendor/base.xdc').read_bytes()==z.read(source+'constrs_1/new/base.xdc')
for p in (ROOT/'vendor/ip_repo').rglob('*'):
 if p.is_file():assert p.read_bytes()==z.read(p.relative_to(ROOT/'vendor').as_posix())
bd=json.loads((ROOT/'vendor/base.bd').read_text())['design']
hwh=ET.parse(REPO/'flyvis-lossless-study/ov5640_official_20261024/ov5640_lcd_7020.hwh')
modules={m.get('FULLNAME'):m for m in hwh.findall('.//MODULE')}
components={}
def walk(b,p=''):
 for n,c in b.get('components',{}).items():
  q=p+'/'+n;components[q]=c;walk(c,q)
walk(bd)
checked={}
for path in ['/ps7_0','/cam_iic','/axi_intc_0','/concat_interrupts','/video/axi_vdma','/video/camera_in/frontend/cmos_capture_data_0','/video/camera_in/frontend/v_vid_in_axi4s_0','/video/video_out/frontend/axi_dynclk','/video/video_out/frontend/vtc_out']:
 assert components[path]['vlnv']==modules[path].get('VLNV'),path
 checked[path]=components[path]['vlnv']
ps={p.get('NAME'):p.get('VALUE') for p in modules['/ps7_0'].findall('./PARAMETERS/PARAMETER')}
for k in ['PCW_FPGA0_PERIPHERAL_FREQMHZ','PCW_FPGA1_PERIPHERAL_FREQMHZ','PCW_USE_S_AXI_HP0','PCW_USE_S_AXI_HP1','PCW_CRYSTAL_PERIPHERAL_FREQMHZ']:
 assert components['/ps7_0']['parameters'][k]['value']==ps[k]
assert ps['PCW_FPGA0_PERIPHERAL_FREQMHZ']=='100' and ps['PCW_USE_S_AXI_HP1']=='0'
assert set(bd['interface_nets']['video_M_AXI']['interface_ports'])=={'ps7_0/S_AXI_HP0','video/M_AXI'}
segments=bd['addressing']['/ps7_0']['address_spaces']['Data']['segments']
for v in segments.values():
 addr=int(v['offset'],16);size=int(v['range'][:-1])*1024
 assert not (addr<0x43c41000 and 0x43c40000<addr+size)
tcl=(ROOT/'prepare_soc.tcl').read_text(encoding='utf-8-sig');interp=tkinter.Tcl()
assert int(interp.call('info','complete',tcl))==1
interp.eval('proc version {args} {return "2026.1.1"}')
try:interp.eval(tcl)
except tkinter.TclError as e:assert 'separately audited IP migration' in str(e)
else:raise AssertionError('wrong version did not stop')
# This exercises only the early guard, not any Vivado command.
assert not re.search(r'^\s*(synth_design|launch_runs|route_design|program_hw_devices|upgrade_ip)\b',tcl,re.M)
ctx=json.loads((ROOT/'baseline/CONTEXT.json').read_text());res=json.loads((ROOT/'baseline/RESULT.json').read_text())
assert res['raw_sha256']==sha((ROOT/'baseline/frame_raw.bin').read_bytes())
for mod,x in ctx['installed_driver_files'].items():
 p=ROOT/'baseline'/('pynq_lib_'+mod[len('pynq.lib.'):].replace('.','_')+'.py')
 assert sha(p.read_bytes())==x['sha256']
report=(ROOT/'vendor/base_wrapper_utilization_placed.rpt').read_text()
def number(label):return float(re.search(r'\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',report)[1])
resources={k:number(v) for k,v in [('LUT','Slice LUTs'),('FF','Slice Registers'),('BRAM36_eq','Block RAM Tile'),('DSP','DSPs')]}
timing=(ROOT/'vendor/base_wrapper_timing_summary_routed.rpt').read_text()
write('STATIC_CHECK.json',dict(status='PASS_SOURCE_AND_GRAMMAR_ONLY',preserved_baseline_entries=len(m),neural_files_identical=58,
 nodes=45669,edges=1513231,matched_official_HWH_IPs=checked,clock_target_hz=100000000,
 planned_camera_HP=0,planned_neural_HP=1,planned_neural_address='0x43c40000',address_overlap=False,
 vendor_tool='2020.2',current_known_install='C:/AMDDesignTools/2026.1.1',
 migration_required=['axi_iic:2.0 versus installed2.1','v_vid_in_axi4s:4.0 versus installed5.0','other IP core revisions require IP status review'],
 official_placed_resources=resources,official_resource_report='vendor/base_wrapper_utilization_placed.rpt',
 official_routed_constraint_gaps={k:int(re.search(r'checking '+k+r' \((\d+)\)',timing)[1]) for k in ['no_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay']},
 combined_resources=None,combined_timing=None,combined_BIT_HWH=None,
 tcl_complete=True,wrong_tool_guard_tested=True,BD_validated=False,Vivado_processes=0,board_operations=0,
 remaining=['Full vendor video2lcd submodule/cache/VDMA dependency capture and ownership audit','Choose exact2020.2 build or audited2026 IP migration','Validate combined BD, then synthesis/route100MHz','Admit HP1 runtime width/cache/allocation and external timing before operator notebook']))
write('CANDIDATE_FILES.json',{str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in ROOT.rglob('*') if p.is_file() and 'evidence' not in p.relative_to(ROOT).parts})
print('PASS source identities, full dimensions, official interfaces, address space, Tcl grammar/version guard; NO Vivado/board validation')
