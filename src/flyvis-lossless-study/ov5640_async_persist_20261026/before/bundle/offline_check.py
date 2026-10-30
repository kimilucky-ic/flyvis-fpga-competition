"""Default is file-only. No PYNQ, network or hardware imports."""
import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from bit_container import bit_header
BIT_SHA='b88cd46383b4884e74384a2f418c251e8d4bb20a86fd3ea6a487be1f58409044'
HWH_SHA='00eb04c23bd2c6666aaec6a9e7809829bedca8591471d7160bb813ae86e6851f'
DCP_SHA='47a822e7a2ee755b7b1d22c50d0c3c2bdd5965df1dae5d8cfa11439273ca6931'
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(root):
    root=Path(root).resolve();m=json.loads((root/'release_manifest.json').read_text())
    required={'flyvis_official.bit','flyvis_official.hwh','reference.exe','reference.cpp','host_reference.cpp','edges.bin','meta.hex','initial_state.bin','official_bridge.py','official_iic21.py','board_runtime.py','board_run.py','operator_entry.py','capture_binding.py','ps_input.py','ddr_control.py','ddr_memory.py','snapshot_records.py','arm_barrier.c','audit_bridge.py','verify_result.py','ps_preflight.py','release_info.json'}
    if not required.issubset(m):raise ValueError('Incomplete package')
    for n,v in m.items():
        if Path(n).name!=n or n in ('','.','..') or ':' in n or '\\' in n or '/' in n:raise ValueError('Unsafe manifest member')
        p=(root/n).resolve()
        if p.parent!=root or not p.is_file() or p.stat().st_size!=v['bytes'] or sha(p.read_bytes())!=v['sha256']:raise ValueError('Package mismatch: '+n)
    if sha((root/'flyvis_official.bit').read_bytes())!=BIT_SHA or sha((root/'flyvis_official.hwh').read_bytes())!=HWH_SHA:raise ValueError('BIT/HWH mismatch')
    head=bit_header((root/'flyvis_official.bit').read_bytes())
    if head['design'].split(';')[0]!='base_wrapper' or head['part']!='7z020clg400':raise ValueError('BIT target/top')
    t=ET.parse(root/'flyvis_official.hwh');si=t.find('SYSTEMINFO')
    if [si.get(k) for k in ('DEVICE','PACKAGE','SPEEDGRADE')]!=['7z020','clg400','-2']:raise ValueError('HWH part')
    mods={v.get('FULLNAME'):v for v in t.findall('.//MODULE')}
    def params(n):return {p.get('NAME'):p.get('VALUE') for p in mods[n].findall('./PARAMETERS/PARAMETER')}
    ps=params('/ps7_0')
    for k,v in {'PCW_USE_S_AXI_HP0':'1','PCW_USE_S_AXI_HP1':'1','PCW_S_AXI_HP0_DATA_WIDTH':'64','PCW_S_AXI_HP1_DATA_WIDTH':'64','PCW_CRYSTAL_PERIPHERAL_FREQMHZ':'33.333333'}.items():
        if ps[k]!=v:raise ValueError('PS parameter '+k)
    for k in ['PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ','PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ']:
        if float(ps[k])!=100:raise ValueError('Clock target')
    for name,base,high in [('network',0x43c40000,0x43c40fff),('video_axi_vdma',0x43000000,0x4300ffff),('cam_iic',0x41600000,0x4160ffff)]:
        a=[x for x in t.findall('.//MEMRANGE') if x.get('INSTANCE')==name]
        if len(a)!=1 or int(a[0].get('BASEVALUE'),16)!=base or int(a[0].get('HIGHVALUE'),16)!=high:raise ValueError('Address '+name)
    for name,vlnv in [('/cam_iic','xilinx.com:ip:axi_iic:2.1'),('/video/axi_vdma','xilinx.com:ip:axi_vdma:6.3'),('/video/camera_in/frontend/v_vid_in_axi4s_0','xilinx.com:ip:v_vid_in_axi4s:5.0')]:
        if mods[name].get('VLNV')!=vlnv:raise ValueError('IP version')
    dma=params('/video/axi_vdma')
    for k,v in {'C_INCLUDE_MM2S':'1','C_INCLUDE_S2MM':'1','C_NUM_FSTORES':'4','C_M_AXI_S2MM_DATA_WIDTH':'64','C_S_AXIS_S2MM_TDATA_WIDTH':'24'}.items():
        if dma[k]!=v:raise ValueError('Official VDMA configuration')
    if params('/cam_iic')['C_IIC_FREQ']!='100000':raise ValueError('IIC frequency')
    info=json.loads((root/'release_info.json').read_text())
    if info.get('control_ABI')!='0x00110005' or info.get('bit_sha256')!=BIT_SHA or info.get('hwh_sha256')!=HWH_SHA:raise ValueError('Ring release identity')
    from camera_config import MAPPING
    if info.get("mapping")!=MAPPING or MAPPING!="direct-grey-center-square-area/v2":raise ValueError("Input mapping revision")
    from ddr_control import VERSION
    if VERSION!=0x00110005:raise ValueError('Ring control version')
    if info['source_routed_dcp_sha256']!=DCP_SHA:raise ValueError('DCP provenance')
    if (root/'edges.bin').stat().st_size!=1513231*8 or (root/'initial_state.bin').stat().st_size!=45669*4:raise ValueError('Full network dimensions')
    return dict(status='PASS_OFFLINE_OFFICIAL_FULL_PACKAGE_ONLY',revision='LINE11_OFFICIAL_LIVE_V261_60S',mapping=MAPPING,bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,files=len(m),nodes=45669,edges=1513231,clock_hz=100000000,board_result=False,execution_authority='NONE')
if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parent),indent=2))
