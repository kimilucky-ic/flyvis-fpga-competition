"""Create a fresh isolated candidate from the sealed 25.61003 ms release."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent
B=R/'synapse_stream_20261016'
P=R/'row_prefetch_20261016'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    seals={}
    for base in [B,R/'throughput_20261016',R/'pipeline100_20261015']:
        mf=base/'FINAL_MANIFEST_SHA256.json';items=json.loads(mf.read_text(encoding='utf-8'))
        for n,v in items.items():assert sha(base/n)==v['sha256'],n
        seals[base.name]=dict(files=len(items),bytes=sum(x['bytes'] for x in items.values()),manifest_sha256=sha(mf))
    P.mkdir(exist_ok=False);(P/'baseline_sources').mkdir()
    names=['fp32_rne.sv','banked_state_mem.sv','sync_mem.sv','compact_edge_gen.sv','flyvis_lane.sv',
        'flyvis_full_top.sv','flyvis_soc_ip.sv','host_reference.cpp','test_full.cpp','lane_scoreboard.cpp',
        'edge_test.cpp','edge_test_top.sv','run_cpu.py','run_hazard.py','run_contexts.py','run_generator.py',
        'cpu_guard.py','run_remaining_cpu.py','audit_candidate.py','build_soc.tcl','build_soc_from_checkpoint.tcl',
        'thread_limit.tcl','launch.ps1','INPUT_IDENTITY.json','flyvis_driver.py','frame_stepper.py','run_soc.py',
        'prepare_resume.py','check_experiment.py','finalize.py']
    for n in names:
        shutil.copyfile(B/n,P/'baseline_sources'/n)
        (P/n).write_bytes((B/n).read_bytes().replace(B.as_posix().encode(),P.as_posix().encode()))
    for d in ['images','platform','hazard_fixture','context_fixture','operators_r2']:shutil.copytree(B/d,P/d)
    for n in ['run_remaining_cpu.py','run_soc.py']:
        s=(P/n).read_text(encoding='utf-8').replace('generator_r3','generator_r1').replace('hazard_positive_r2','hazard_positive_r1').replace('hazard_negative_r2','hazard_negative_r1')
        if n=='run_remaining_cpu.py':s=s.replace("[P.parent/'throughput_20261016',P.parent/'pipeline100_20261015']","[P.parent/'synapse_stream_20261016',P.parent/'throughput_20261016',P.parent/'pipeline100_20261015']")
        (P/n).write_text(s,encoding='utf-8')
    (P/'BASELINE_CHECK.json').write_text(json.dumps(dict(status='PASS_THREE_BASELINE_SEALS',seals=seals,board_operations=0),indent=2)+'\n',encoding='utf-8')
    shutil.copyfile(Path(__file__),P/'prepare_experiment.py')
    print(json.dumps(seals))
if __name__=='__main__':main()
