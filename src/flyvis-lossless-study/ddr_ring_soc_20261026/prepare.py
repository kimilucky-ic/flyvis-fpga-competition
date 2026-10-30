from pathlib import Path
import shutil, hashlib, json
P=Path(__file__).resolve().parent; R=P.parent
B=Path('C:/fpga_work/line11_ring_20261026'); O=Path('C:/fpga_work/line11_off26_r2_20261024')
ring=R/'ddr_ring_20261026'
if B.exists():raise RuntimeError('Fresh isolated directory required')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ids=json.loads((ring/'SOURCE_SHA256.json').read_text());assert all(sha(ring/f)==h for f,h in ids.items())
old=[*(O/'vendor').rglob('*'),*(O/'neural').glob('*'),O/'base_2026.bd',O/'camera_budget.xdc',O/'migrate3.tcl',O/'combine.tcl',O/'synth.tcl',O/'route_resume.tcl']
seal={str(f):sha(f) for f in old if f.is_file()}
(P/'evidence/BASELINE_BUILD_SHA256.json').write_text(json.dumps(seal,indent=2))
B.mkdir();shutil.copytree(O/'vendor',B/'vendor');shutil.copytree(O/'neural',B/'neural')
for n in ('base_2026.bd','camera_budget.xdc','migrate3.tcl','combine.tcl','synth.tcl','launch.ps1'):shutil.copy2(O/n,B/n)
relocations={}
for f in (ring/'rtl').glob('*.sv'):
 raw=f.read_text();prefix='C:/Users/hzy72/Documents/ChatGPT/fpga/flyvis-lossless-study/hole_pipeline_20261016/images/'
 updated=raw.replace(prefix,B.as_posix()+'/neural/')
 assert updated.replace(B.as_posix()+'/neural/',prefix)==raw
 dest=B/'neural'/f.name;dest.write_text(updated,encoding='utf-8')
 relocations[f.name]=dict(source_sha256=sha(f),build_sha256=sha(dest),path_replacements=raw.count(prefix),logic_unchanged=True)
for f in (B/'neural').glob('*.hex'):
 origin=R/'hole_pipeline_20261016/images'/f.name
 assert origin.exists() and sha(f)==sha(origin),str(f)
route=(O/'route_resume.tcl').read_text()
route=route.replace('write_checkpoint release_routed/combined_routed.dcp','write_checkpoint release_routed/combined_routed.dcp\nreport_clock_interaction -file release_routed/clock_interaction.rpt\nreport_exceptions -file release_routed/exceptions.rpt')
(B/'route.tcl').write_text(route)
combine=(B/'combine.tcl').read_text()
combine=combine.replace('validate_bd_design\nsave_bd_design', '''if {[get_property CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ $ps] != 100} {error "Neural clock changed"}
if {[get_property CONFIG.PCW_S_AXI_HP1_DATA_WIDTH $ps] != 64} {error "HP1 width changed"}
set report [open integration_contract.txt w]
puts $report "RING_ABI 0x00110005; N45669 NE1513231 INPUT721; HP1 DDR64bit; target100MHz; no board operations"
close $report
validate_bd_design
save_bd_design''')
(B/'combine.tcl').write_text(combine)
for f in B.glob('*.tcl'):assert 'write_bitstream' not in f.read_text() and 'open_hw' not in f.read_text()
(P/'evidence/BUILD_INPUTS.json').write_text(json.dumps(dict(build=str(B),baseline=str(O),relocations=relocations,vendor_unchanged=True,camera_constraints_unchanged=True,part='xc7z020clg400-2',full_network=True),indent=2))
print('Prepared',B,'with',len(seal),'baseline source identities; no EDA or hardware started')
