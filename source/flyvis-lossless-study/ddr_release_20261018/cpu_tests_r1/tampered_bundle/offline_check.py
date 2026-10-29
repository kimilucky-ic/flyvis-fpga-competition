"""Default entry: local file/bit-container/HWH checks only. Never imports PYNQ."""
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

BIT_SHA='d365f41da4b52dc8dbd0ba751f8691da448607747a6bcf04e619ab465d956b66'
HWH_SHA='69a4332593e32852aec9dbc7b177341f3303af067ee1f182c44152744f8598f1'
DCP_SHA='c693e828c6028d0d6c41462e10aa52dfe1faa4bfc2ecc3b1e7d7f4e2b6227506'
def digest(data):return hashlib.sha256(data).hexdigest()

def bit_header(raw):
    # Independent parser of the standard tagged .bit container; no bitstream
    # execution. See PYNQ2.7 embedded_device.parse_bit_header for the format.
    if len(raw)<32:raise ValueError('Truncated bitstream')
    size=struct.unpack_from('>H',raw)[0];pos=2+size
    if size!=9 or raw[2:pos]!=bytes.fromhex('0ff00ff00ff00ff000') or raw[pos:pos+2]!=b'\0\1':raise ValueError('BIT preamble')
    pos+=2;out={}
    for tag,name in ((97,'design'),(98,'part'),(99,'date'),(100,'time'),(101,'payload_bytes')):
        if pos>=len(raw) or raw[pos]!=tag:raise ValueError('BIT tag/order')
        pos+=1;width=4 if tag==101 else 2
        if pos+width>len(raw):raise ValueError('BIT length field')
        length=int.from_bytes(raw[pos:pos+width],'big');pos+=width
        if length<1 or pos+length>len(raw):raise ValueError('BIT field bounds')
        if tag==101:
            if pos+length!=len(raw) or b'\xaa\x99\x55\x66' not in raw[pos:pos+128]:raise ValueError('BIT payload/sync')
            out[name]=length
        else:
            if raw[pos+length-1]!=0:raise ValueError('BIT unterminated text')
            out[name]=raw[pos:pos+length-1].decode('ascii')
        pos+=length
    return out

def verify(root):
    root=Path(root).resolve();manifest=json.loads((root/'release_manifest.json').read_text(encoding='utf-8'))
    required={'flyvis_ddr.bit','flyvis_ddr.hwh','inputs.bin','expected_states.bin','initial_state.bin',
        'ddr_control.py','snapshot_records.py','ddr_memory.py','ddr_acceptance.py','offline_check.py','arm_barrier.c','release_info.json','cpu_fixture_ddr.bin','cpu_replay.py'}
    if not required.issubset(manifest):raise ValueError('Required release files missing')
    for name,item in manifest.items():
        if Path(name).name!=name or name in ('','.', '..'):raise ValueError('Non-flat/escaping manifest')
        f=(root/name).resolve()
        if f.parent!=root or not f.is_file() or f.stat().st_size!=item['bytes'] or digest(f.read_bytes())!=item['sha256']:raise ValueError('Package identity mismatch: '+name)
    if manifest['flyvis_ddr.bit']['sha256']!=BIT_SHA or manifest['flyvis_ddr.hwh']['sha256']!=HWH_SHA:raise ValueError('Wrong release BIT/HWH')
    header=bit_header((root/'flyvis_ddr.bit').read_bytes())
    if header['design'].split(';')[0]!='flyvis_ddr_wrapper' or header['part'].lower() not in ('7z020clg400','xc7z020clg400'):raise ValueError('Wrong BIT top/part')
    tree=ET.parse(str(root/'flyvis_ddr.hwh'));info=tree.find('SYSTEMINFO')
    if info is None or [info.get(k) for k in ('DEVICE','PACKAGE','SPEEDGRADE')]!=['7z020','clg400','-2']:raise ValueError('Wrong HWH target')
    modules={m.get('INSTANCE'):m for m in tree.findall('.//MODULE')}
    ps={x.get('NAME'):x.get('VALUE') for x in modules['ps7'].findall('./PARAMETERS/PARAMETER')}
    if (float(ps['PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ'])!=100 or ps['PCW_USE_S_AXI_HP0']!='1'
            or ps['PCW_S_AXI_HP0_DATA_WIDTH']!='64' or ps['PCW_USE_M_AXI_GP0']!='1'
            or ps['PCW_CRYSTAL_PERIPHERAL_FREQMHZ']!='33.333333'):raise ValueError('Wrong PS7/HP0 clock configuration')
    ranges=[r for r in tree.findall('.//MEMRANGE') if r.get('INSTANCE')=='network']
    if len(ranges)!=1 or int(ranges[0].get('BASEVALUE'),16)!=0x43c40000 or int(ranges[0].get('HIGHVALUE'),16)!=0x43c40fff:raise ValueError('Wrong GP0 range')
    for name,n in [('inputs.bin',3*2884),('expected_states.bin',3*182676),('initial_state.bin',182676),('cpu_fixture_ddr.bin',3*188416)]:
        if (root/name).stat().st_size!=n:raise ValueError('Wrong complete-network plan length')
    release=json.loads((root/'release_info.json').read_text(encoding='utf-8'))
    if release['source_routed_dcp_sha256']!=DCP_SHA:raise ValueError('Wrong route provenance')
    return dict(status='PASS_OFFLINE_BIT_HWH_PACKAGE_ONLY',bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,
        bit_header=header,files=len(manifest),nodes=45669,edges=1513231,clock_MHz=100,
        clock_evidence='HWH_AND_PRIOR_POST_ROUTE_TIMING_NOT_PHYSICAL_MEASUREMENT',board_operations=0,
        execution_authority='NONE; physical operation requires separate user authorization')

def plan(root):
    verify(root);root=Path(root);inputs=(root/'inputs.bin').read_bytes();states=(root/'expected_states.bin').read_bytes()
    return ([inputs[i*2884:(i+1)*2884] for i in range(3)],
            [states[i*182676:(i+1)*182676] for i in range(3)])

if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parent),indent=2))
