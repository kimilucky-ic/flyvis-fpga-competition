"""Default file-only release check. No hardware imports or operations."""
import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from bit_container import bit_header
BIT_SHA='781981526e8cc9916c096ff46b92046d90021d56c9438718fe5566cfdf1df7d7'
HWH_SHA='61465634adaa0e421a5b07c77b38e0739fdcfdf8e68e977f25bf2d803b9097ae'
DCP_SHA='a5d591404720aaa9623f924377be7d4b690e122065db32930bb2b7b0ba6237cc'
def digest(data):return hashlib.sha256(data).hexdigest()
def verify(root):
    root=Path(root).resolve();manifest=json.loads((root/'release_manifest.json').read_text())
    required={'flyvis_ov5640.bit','flyvis_ov5640.hwh','reference.exe','edges.bin','meta.hex','initial_state.bin',
      'reference.cpp','host_reference.cpp','board_capture.py','single_frame.py','camera_memory.py','bounded_io.py',
      'capture_binding.py','ps_input.py','sensor_init.py','init_actions.json','ddr_control.py','ddr_memory.py',
      'snapshot_records.py','arm_barrier.c','verify_run.py','release_info.json','conditions.json','README.md'}
    if not required.issubset(manifest):raise ValueError('Incomplete package')
    for name,item in manifest.items():
        if Path(name).name!=name or name in ('','..','.') or ':' in name or '\\' in name:raise ValueError('Escaping manifest')
        f=(root/name).resolve()
        if f.parent!=root or not f.is_file() or f.stat().st_size!=item['bytes'] or digest(f.read_bytes())!=item['sha256']:raise ValueError('Package mismatch: '+name)
    if digest((root/'flyvis_ov5640.bit').read_bytes())!=BIT_SHA or digest((root/'flyvis_ov5640.hwh').read_bytes())!=HWH_SHA:raise ValueError('BIT/HWH identity')
    h=bit_header((root/'flyvis_ov5640.bit').read_bytes())
    if h['design'].split(';')[0]!='flyvis_ddr_wrapper' or h['part'].lower() not in ('7z020clg400','xc7z020clg400'):raise ValueError('BIT target/top')
    t=ET.parse(root/'flyvis_ov5640.hwh');i=t.find('SYSTEMINFO')
    if [i.get(k) for k in ('DEVICE','PACKAGE','SPEEDGRADE')]!=['7z020','clg400','-2']:raise ValueError('HWH part')
    modules={m.get('INSTANCE'):m for m in t.findall('.//MODULE')}
    def params(n):return {v.get('NAME'):v.get('VALUE') for v in modules[n].findall('./PARAMETERS/PARAMETER')}
    ps=params('ps7')
    for k,v in {'PCW_USE_S_AXI_HP0':'1','PCW_USE_S_AXI_HP1':'1','PCW_S_AXI_HP0_DATA_WIDTH':'64','PCW_S_AXI_HP1_DATA_WIDTH':'64','PCW_CRYSTAL_PERIPHERAL_FREQMHZ':'33.333333'}.items():
        if ps[k]!=v:raise ValueError('PS7 '+k)
    if float(ps['PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ'])!=100:raise ValueError('FCLK0')
    for name,base,high in [('network',0x43c40000,0x43c40fff),('camera_dma',0x43000000,0x4300ffff),('cam_iic',0x41600000,0x4160ffff),('camera_control',0x41200000,0x4120ffff)]:
        a=[x for x in t.findall('.//MEMRANGE') if x.get('INSTANCE')==name]
        if len(a)!=1 or int(a[0].get('BASEVALUE'),16)!=base or int(a[0].get('HIGHVALUE'),16)!=high:raise ValueError('Address '+name)
    dma=params('camera_dma')
    for k,v in {'C_INCLUDE_MM2S':'0','C_INCLUDE_S2MM':'1','C_S_AXIS_S2MM_TDATA_WIDTH':'24','C_M_AXI_S2MM_DATA_WIDTH':'64'}.items():
        if dma[k]!=v:raise ValueError('VDMA '+k)
    if params('cam_iic')['C_IIC_FREQ']!='100000' or params('camera_control')['C_GPIO2_WIDTH']!='3':raise ValueError('Camera control')
    info=json.loads((root/'release_info.json').read_text())
    if info['source_routed_dcp_sha256']!=DCP_SHA:raise ValueError('DCP provenance')
    if (root/'edges.bin').stat().st_size!=1513231*8 or (root/'initial_state.bin').stat().st_size!=45669*4:raise ValueError('Full network data')
    return dict(status='PASS_OFFLINE_OV5640_BIT_HWH_PACKAGE_ONLY',bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,files=len(manifest),nodes=45669,edges=1513231,clock_MHz=100,board_result=False,board_operations=0,external_signoff_complete=False,execution_authority='NONE')
if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parent),indent=2))
