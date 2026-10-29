"""Create an isolated approved RAM template repair; never edit prior evidence."""
from pathlib import Path
import json, hashlib, shutil, difflib, ast
B=Path(__file__).resolve().parent
SIM=B/'ramfix_r1_sim_20261012'; OOC=B/'ramfix_r1_ooc_20261012'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(s,a,b):
    assert s.count(a)==1, a
    return s.replace(a,b)
assert not SIM.exists() and not OOC.exists()
SIM.mkdir(); OOC.mkdir(); (SIM/'rtl').mkdir()
for p in (B/'rtl').glob('*.sv'):
    if not p.name.startswith('tb_'):shutil.copyfile(p,SIM/'rtl'/p.name)
p=SIM/'rtl/ddr_synapse_core.sv'; old=p.read_text(encoding='utf-8'); new=old
new=change(new,'    wire cand_write=', '''    // CLEAR and SUM are mutually exclusive: one physical RAM write port.
    wire chemical_we=(state==CLEAR)||edge_write;
    wire [12:0] chemical_waddr=(state==CLEAR)?h_index:target;
    wire signed [49:0] chemical_wdata=(state==CLEAR)?50'sd0:sum[49:0];
    wire cand_write=''')
new=change(new,'        if(state==CLEAR) chemical_mem[h_index]<=0;', '        if(chemical_we) chemical_mem[chemical_waddr]<=chemical_wdata;')
new=change(new,'        if(edge_write) chemical_mem[target]<=sum[49:0];\n','')
p.write_text(new,encoding='utf-8')
(SIM/'RAM_PORT_CHANGE.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/ddr_synapse_core.sv',tofile='r1/ddr_synapse_core.sv')),encoding='utf-8')
save(SIM/'REVISION.json',dict(revision='RAM_WRITE_MUX_R1',authorization='User approved minimal RAM port repair and continuation until actual synthesis resources',original_rtl_sha256={p.name:sha(p) for p in (B/'rtl').glob('*.sv') if not p.name.startswith('tb_')},rtl_sha256={p.name:sha(p) for p in (SIM/'rtl').glob('*.sv')},change='Single chemical write statement, explicit CLEAR/SUM address/data mux; identical state machine and arithmetic',scope='Full-scale RTL validation followed by OOC synthesis only'))
src=B/'fullscale_direct_20261012'
for name in ('tb_fullscale.sv','windows_host.py','launch_xsim.ps1','A_EDA_RELEASE.json'):
    shutil.copyfile(src/name,SIM/name)
save(SIM/'DIRECT_LAUNCH_AUTHORIZATION.json',dict(user_instruction='同意继续吧直到把综合资源跑出来给我',scope='New RAM revision simulation and isolated OOC; prior evidence preserved'))
save(SIM/'STATIC_REVIEW.json',dict(original_review_sha256=sha(src/'STATIC_REVIEW.json'),bench_sha256=sha(SIM/'tb_fullscale.sv'),revision_sha256=sha(SIM/'REVISION.json'),write_exclusion='state CLEAR=2 and SUM=8 exclusive; enable/data unchanged',change='Only chemical RAM port template; all frozen vectors and comparisons retained',cycle_bound=7860104,step_limit=8000000))
s=(src/'run_fullscale.py').read_text(encoding='utf-8')
s=change(s,"    return prep\ndef main():", "    revision=json.loads((HERE/'REVISION.json').read_text(encoding='utf-8'))\n    for name,digest in revision['rtl_sha256'].items():assert sha(HERE/'rtl'/name)==digest\n    return prep\ndef main():")
s=change(s,"ledger=B/'FULLSCALE_LAUNCH_20261012.json'", "ledger=HERE/'REVISION_LAUNCH.json'")
s=change(s,"if ledger.exists() or (PREP/'LAUNCH_RECORD.json').exists():", "if ledger.exists():")
s=change(s,"shutil.copyfile(B/'rtl'/name,run/name)","shutil.copyfile(HERE/'rtl'/name,run/name)")
s=change(s,"ident=dict(at=now(),", "ident=dict(revision_sha256=sha(HERE/'REVISION.json'),at=now(),")
(SIM/'run_fullscale.py').write_text(s,encoding='utf-8')
s=(src/'audit_fullscale.py').read_text(encoding='utf-8')
s=change(s,"        need(sha(run/name)==sha(HERE.parent/'rtl'/name)==digest,f'Protected RTL changed: {name}')", "        need(sha(HERE.parent/'rtl'/name)==digest,f'Protected original RTL changed: {name}')\n    revision=read_json(HERE/'REVISION.json')\n    need(sha(HERE/'REVISION.json')==identity['revision_sha256'],'Revision changed')\n    for name,digest in revision['rtl_sha256'].items():\n        need(sha(run/name)==sha(HERE/'rtl'/name)==digest,f'Revised RTL changed: {name}')")
(SIM/'audit_fullscale.py').write_text(s,encoding='utf-8')
src=B/'ooc_fullscale_20261012'
for name in ('synth_fullscale.tcl','clock.xdc','launch_vivado.ps1'):shutil.copyfile(src/name,OOC/name)
s=(src/'run_ooc.py').read_text(encoding='utf-8')
s=change(s,"ACCEPTED=B/'fullscale_direct_20261012'", "ACCEPTED=B/'ramfix_r1_sim_20261012'")
s=change(s,"assert sha(B/'rtl'/name)==sha(sim/name)==identity['sources'][name]", "assert sha(ACCEPTED/'rtl'/name)==sha(sim/name)==identity['sources'][name]")
(OOC/'run_ooc.py').write_text(s,encoding='utf-8')
for dest in (SIM,OOC):
    for p in dest.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
print(json.dumps(dict(sim=str(SIM),ooc=str(OOC),revision=json.loads((SIM/'REVISION.json').read_text(encoding='utf-8'))),indent=2))
