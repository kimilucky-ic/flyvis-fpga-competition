"""Explicit single synchronous source/chemical read port after R1 LUTRAM mapping."""
from pathlib import Path
import json,hashlib,shutil,difflib,ast
B=Path(__file__).resolve().parent
PREV=B/'ramfix_r1_sim_20261012';SIM=B/'ramfix_r2_sim_20261012';OOC=B/'ramfix_r2_ooc_20261012'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
assert not SIM.exists() and not OOC.exists()
SIM.mkdir();OOC.mkdir();(SIM/'rtl').mkdir()
rev=json.loads((PREV/'REVISION.json').read_text(encoding='utf-8'))
for name in rev['rtl_sha256']:shutil.copyfile(PREV/'rtl'/name,SIM/'rtl'/name)
p=SIM/'rtl/ddr_synapse_core.sv';old=p.read_text(encoding='utf-8');new=old
new=change(new,'    wire cand_write=', '''    // READ and N_READ are mutually exclusive: one synchronous read port.
    wire state_read=(state==READ)||(state==N_READ);
    wire [14:0] source_raddr=(state==READ)?src:{2'b0,h_index};
    wire [12:0] chemical_raddr=(state==READ)?target:h_index;
    wire cand_write=''')
new=change(new,'''        if(state==READ) begin
            source_q<=source_mem[src];weight_q<=weight_rom[weight_index];chemical_q<=chemical_mem[target];
        end
        if(state==N_READ) begin
            source_q<=source_mem[h_index];x_q<=x_mem[h_index];
            chemical_q<=chemical_mem[h_index];neuron_q<=neuron_rom[h_index];
        end''','''        if(state_read) begin
            source_q<=source_mem[source_raddr];chemical_q<=chemical_mem[chemical_raddr];
        end
        if(state==READ) weight_q<=weight_rom[weight_index];
        if(state==N_READ) begin
            x_q<=x_mem[h_index];neuron_q<=neuron_rom[h_index];
        end''')
p.write_text(new,encoding='utf-8')
(SIM/'RAM_PORT_CHANGE_FROM_R1.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='r1/ddr_synapse_core.sv',tofile='r2/ddr_synapse_core.sv')),encoding='utf-8')
original=(B/'rtl/ddr_synapse_core.sv').read_text(encoding='utf-8')
(SIM/'RAM_PORT_CHANGE_FROM_ORIGINAL.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile='original/ddr_synapse_core.sv',tofile='r2/ddr_synapse_core.sv')),encoding='utf-8')
rev.update(revision='RAM_WRITE_AND_READ_MUX_R2',previous_revision_sha256=sha(PREV/'REVISION.json'),rtl_sha256={name:sha(SIM/'rtl'/name) for name in rev['rtl_sha256']},change='Explicit chemical single write port and source/chemical single synchronous read ports. Mutually exclusive FSM states mux addresses/enables; no arithmetic or cycle change.')
save(SIM/'REVISION.json',rev)
for name in ('tb_fullscale.sv','windows_host.py','launch_xsim.ps1','A_EDA_RELEASE.json','DIRECT_LAUNCH_AUTHORIZATION.json','run_fullscale.py','audit_fullscale.py'):
    shutil.copyfile(PREV/name,SIM/name)
review=json.loads((PREV/'STATIC_REVIEW.json').read_text(encoding='utf-8'))
review.update(revision_sha256=sha(SIM/'REVISION.json'),change=rev['change'],read_exclusion='READ=5 and N_READ=10 cannot both be active; identical enable and address at each posedge; 15-bit source index retained')
save(SIM/'STATIC_REVIEW.json',review)
for name in ('synth_fullscale.tcl','clock.xdc','launch_vivado.ps1'):
    shutil.copyfile(B/'ramfix_r1_ooc_20261012'/name,OOC/name)
s=(B/'ramfix_r1_ooc_20261012/run_ooc.py').read_text(encoding='utf-8')
s=change(s,"ACCEPTED=B/'ramfix_r1_sim_20261012'","ACCEPTED=B/'ramfix_r2_sim_20261012'")
(OOC/'run_ooc.py').write_text(s,encoding='utf-8')
for dest in (SIM,OOC):
    for p in dest.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
print(json.dumps(rev,indent=2))
