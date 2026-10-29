from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;R=P.parent;O=Path('C:/fpga_work/line11_ring_20261026');B=Path('C:/fpga_work/line11_v261_20261026')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not B.exists(),'Fresh directory required'
old=json.loads((R/'ddr_ring_soc_20261026/FINAL_MANIFEST_SHA256.json').read_text())
assert all(sha(R/'ddr_ring_soc_20261026'/n)==v for n,v in old.items())
crop=R/'ov5640_live_crop_20261026';cropids=json.loads((crop/'FINAL_MANIFEST_SHA256.json').read_text())
assert all(sha(crop/n)==v for n,v in cropids.items())
(P/'evidence/CROP_BASELINE_SHA256.json').write_text(json.dumps({str(crop/n):v for n,v in cropids.items()},indent=2))
files=[*(O/'vendor').rglob('*'),*(O/'neural').rglob('*'),*[O/n for n in ['base_2026.bd','camera_budget.xdc','migrate3.tcl','combine.tcl','synth.tcl','route.tcl','audit_routed.tcl','launch.ps1']]]
seal={str(f):sha(f) for f in files if f.is_file()};(P/'evidence/BASELINE_BUILD_SHA256.json').write_text(json.dumps(seal,indent=2))
B.mkdir();shutil.copytree(O/'vendor',B/'vendor');shutil.copytree(O/'neural',B/'neural')
for n in ['base_2026.bd','camera_budget.xdc','migrate3.tcl','combine.tcl','synth.tcl','route.tcl','audit_routed.tcl','launch.ps1']:shutil.copy2(O/n,B/n)
rel={}
for f in (B/'neural').glob('*.sv'):
 raw=f.read_text();updated=raw.replace(O.as_posix()+'/',B.as_posix()+'/');assert updated.replace(B.as_posix()+'/',O.as_posix()+'/')==raw
 f.write_text(updated,encoding='utf-8');rel[f.name]=dict(source_sha256=sha(O/'neural'/f.name),build_sha256=sha(f),path_replacements=raw.count(O.as_posix()+'/'),logic_unchanged=True)
s=(B/'launch.ps1').read_text().replace('C:/AMDDesignTools/2026.1.1/Vivado/bin/vivado.bat','D:/2026.1/Vivado/bin/vivado.bat');(B/'launch.ps1').write_text(s)
# Reject mixed build paths in build Tcl; old .bd tool_version is not falsified.
for f in B.glob('*.tcl'):assert O.as_posix() not in f.read_text()
(B/'bitgen.tcl').write_text('set_param general.maxThreads 1\nset here [file dirname [file normalize [info script]]]\ncd $here\nopen_checkpoint release_routed/combined_routed.dcp\nreport_drc -file bitgen_drc.rpt\nwrite_bitstream flyvis_official.bit\nclose_design\nexit\n')
(P/'evidence/BUILD_INPUTS.json').write_text(json.dumps(dict(build=str(B),baseline=str(O),relocations=rel,tool='D:/2026.1/Vivado/bin/vivado.bat',vendor_unchanged=True,camera_constraints_unchanged=True,part='xc7z020clg400-2',full_network=True),indent=2))
(P/'COMMANDS.json').write_text(json.dumps(dict(scope='Authorized independent Vivado2026.1 validation synthesis route bitgen; no board',python='C:/Users/hzy72/Documents/ChatGPT/fly/.venv/Scripts/python.exe',commands=['prepare.py','run_build.py migrate3 combine','run_build.py synth route','finish_route.py','run_build.py bitgen','finalize.py'],tool='D:/2026.1/Vivado/bin/vivado.bat',build=str(B),threads=1),indent=2))
print('Prepared',B,'baseline files',len(seal),'crop sealed files',len(cropids))
