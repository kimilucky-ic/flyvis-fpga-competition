from pathlib import Path
import json,hashlib,shutil,xml.etree.ElementTree as ET,sys,zipfile,re
P=Path(__file__).resolve().parent;R=P.parent;B=Path('C:/fpga_work/line11_v261_20261026');D=P/'release'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=json.loads((P/'RESULT.json').read_text());assert result['timing']['WNS_ns']>=0
log=(B/'bitgen.log').read_text(errors='replace');assert 'write_bitstream completed successfully' in log and not re.search(r'^ERROR:',log,re.M)
drc=(B/'bitgen_drc.rpt').read_text();assert not re.search(r'^\|[^\n]*\|\s*(Error|Critical Warning)\s*\|',drc,re.M)
bit=B/'flyvis_official.bit';hwh=B/'imported3/base/hw_handoff/base.hwh'
sys.path.insert(0,str(R/'ov5640_live_crop_20261026/bundle'));from bit_container import bit_header
header=bit_header(bit.read_bytes());assert header['part']=='7z020clg400' and header['design'].split(';')[0]=='base_wrapper'
a=ET.parse(R/'ddr_ring_soc_20261026/release/base.hwh');b=ET.parse(hwh)
def module(t,name):return next(m for m in t.iter('MODULE') if m.get('FULLNAME')==name)
def params(t,name):return {x.get('NAME'):x.get('VALUE') for x in module(t,name).findall('./PARAMETERS/PARAMETER')}
pa,pb=params(a,'/ps7_0'),params(b,'/ps7_0');diff={k:[pa.get(k),pb.get(k)] for k in pa.keys()|pb.keys() if pa.get(k)!=pb.get(k)}
assert not {k:v for k,v in diff.items() if k.startswith('PCW_')},diff
ma={m.get('FULLNAME'):m.get('VLNV') for m in a.iter('MODULE')};mb={m.get('FULLNAME'):m.get('VLNV') for m in b.iter('MODULE')};assert ma==mb
ranges=lambda t:sorted(json.dumps(x.attrib,sort_keys=True) for x in t.iter('MEMRANGE'))
assert ranges(a)==ranges(b),'HWH address map differs'
for n in ['/network','/cam_iic','/video/axi_vdma']:
 assert params(a,n)==params(b,n),('Interface configuration changed',n)
for n in ['PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ','PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ']:assert float(pb[n])==100
assert [b.find('SYSTEMINFO').get(k) for k in ('DEVICE','PACKAGE','SPEEDGRADE')]==['7z020','clg400','-2']
for f in [P/'evidence/CROP_BASELINE_SHA256.json',P/'evidence/BASELINE_BUILD_SHA256.json']:
 ids=json.loads(f.read_text());assert all(sha(Path(n))==v for n,v in ids.items())
shutil.copy2(bit,D/'flyvis_official.bit');shutil.copy2(hwh,D/'flyvis_official.hwh')
for name in ['bitgen.log','bitgen.jou','bitgen.tcl','bitgen_drc.rpt']:shutil.copy2(B/name,P/'evidence'/name)
result.update(status='PASS_VIVADO2026_1_FULL_SOC_100MHZ_BIT_HWH_OFFLINE_ONLY',bit_generated=True,bit_sha256=sha(bit),hwh_sha256=sha(hwh),bit_header=header,PS_parameter_differences=diff,interfaces_equal_to_passed_ring=True,crop_release_files_preserved=len(json.loads((P/'evidence/CROP_BASELINE_SHA256.json').read_text())),next='Prepare separate crop software release with new paired firmware hashes and CPU package validation, then user-controlled board acceptance; old passing package unchanged')
result['limits']=[s for s in result['limits'] if not s.startswith('No new bitstream')]+['No physical board operation or new real-world performance/numerical claim; old physical PASS does not certify new bitstream','Current crop Notebook pins old BIT/HWH hashes; do not overwrite its firmware in place']
(P/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
info={k:result[k] for k in ['status','tool','part','top','network','bit_sha256','hwh_sha256','routed_dcp_sha256','bit_header','timing','resources','limits']}
(D/'release_info.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
with zipfile.ZipFile(P/'LINE11_VIVADO2026_1_BIT_HWH_OFFLINE.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['flyvis_official.bit','flyvis_official.hwh','release_info.json']:z.write(D/n,n)
for name in ['migrated_ip_status.rpt','combined_ip_status.rpt','migrated_cells.txt','integration_contract.txt']:
 shutil.copy2(B/name,P/'evidence'/name)
(P/'evidence/BUILD_STATUS.json').write_text(json.dumps(dict(stage='COMPLETE_OFFLINE_VERIFIED',board_operations=0,bit_generated=True,tool='Vivado2026.1 SW6511674')))
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps({str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.name!='FINAL_MANIFEST_SHA256.json'},indent=2))
print(json.dumps({k:result[k] for k in ['status','timing','resources','bit_sha256','hwh_sha256','crop_release_files_preserved']},indent=2))
