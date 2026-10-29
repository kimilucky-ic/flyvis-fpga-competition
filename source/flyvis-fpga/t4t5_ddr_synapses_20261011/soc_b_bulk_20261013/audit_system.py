"""Independent file audit of actual production BD simulation; no oracle recompute."""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np
P = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    build = P / json.loads((P/'LATEST_BUILD.json').read_text())['build']
    sim = build/'project/b_soc.sim/sim_1/behav/xsim'
    stages=sorted((build/'stages').glob('simulate_*'),key=lambda x:int(x.name.split('_')[-1]))
    assert stages, 'No actual full-scale run'
    last=stages[-1]
    runtime=json.loads((last/'RUNTIME.json').read_text())
    assert runtime['exit_code']==0 and runtime['stop_reason'] is None
    identity=json.loads((last/'IDENTITY.json').read_text())
    for name,h in identity['source_sha256'].items():assert digest(build/'source'/name)==h
    for name in ('system_pass.txt','system_edges.csv','system_candidates.csv','simulate.log'):
        assert digest(last/name)==digest(sim/name), ('Runtime evidence changed',name)
    text = (sim/'system_pass.txt').read_text()
    assert text.startswith('B_ACTUAL_BD_SYSTEM_SIMULATION_PASS\n')
    counters = {k: int(v) for k,v in re.findall(r'(\w+)=(\d+)', text)}
    for key, value in dict(H=5768,S=16402,E=433880,candidate_comparisons=5768,
                           ordered_HP0_records=433880,ordered_retired_edges=433880,
                           candidate_mismatches=0,valid_REQUESTS=1,
                           invalid_START_rejected=1,DDR_timeout_rejected=1,input_format_rejected=1,input_words=22170,output_words=5768,ABI=2,DDR_canaries_pass=1).items():
        assert counters[key] == value, (key,counters)
    assert counters['write_stalls']>0 and counters['aw_stalls']>0
    assert counters['output_responses']==counters['output_bursts']
    assert counters['control_stalls'] > 0 and counters['DDR_stalls'] > 0
    runtime_log = (sim/'simulate.log').read_text(errors='replace')
    assert not re.search(r'(?mi)^\s*(?:ERROR:|Fatal:|UVM_FATAL|UVM_ERROR)',runtime_log), 'Protocol/runtime error in simulation log'
    # Deliberate 100000-cycle DDR latency exceeds the vendor recommendation,
    # not an AXI protocol requirement. Keep the warnings and reject other ones.
    runtime_warnings = re.findall(r'(?mi)^Warning: (.*)$', runtime_log)
    expected_warning = 'XILINX_RECS_CONTINUOUS_RTRANSFERS_MAX_WAIT:'
    assert all(w.startswith(expected_warning) for w in runtime_warnings), runtime_warnings
    first_warning = runtime_log.find('Warning: '+expected_warning)
    if first_warning >= 0:
        assert runtime_log.index('B_SYSTEM_FULL_REQUEST_PASS') < first_warning
    assert 'B_PSVIP_DDRC_SCHEDULING_PATCH_1PS active' in runtime_log
    model=json.loads((build/'simulation_model/MODEL_IDENTITY.json').read_text())
    assert digest(build/'simulation_model/processing_system7_vip_v1_0_vl_rfs.sv')==model['patched_sha256']
    assert digest(last/'processing_system7_vip_v1_0_vl_rfs.sv')==model['patched_sha256']
    assert digest(Path(model['original']))==model['original_sha256']
    edge_image = (build/'rom/edges.mem').open()
    oracle_path=P.parent/'fullscale_20261012/vectors/integer_oracle.npz'
    prep=json.loads((P.parent/'fullscale_20261012/PREPARATION.json').read_text())
    assert digest(oracle_path)==prep['files']['integer_oracle.npz']['sha256']
    oracle=dict(np.load(oracle_path,allow_pickle=False))
    count = 0
    with (sim/'system_edges.csv').open() as stream:
        for row, line in zip(csv.reader(stream), edge_image, strict=True):
            record = int(line,16)
            assert int(row[0]) == count and int(row[1],16) == record
            assert int(row[2]) == (record & ((1<<21)-1))
            assert int(row[3]) == ((record>>36) & ((1<<13)-1))
            assert int(row[4])==int(oracle['edge_term_q24'][count]), ('term',count)
            assert int(row[5])==int(oracle['partial_chemical_q24'][count]), ('sum',count)
            count += 1
    edge_image.close()
    assert count == 433880
    candidates = [int(x,16) for x in (build/'rom/expected.mem').read_text().split()]
    count = 0
    with (sim/'system_candidates.csv').open() as stream:
        for row, expected in zip(csv.reader(stream),candidates,strict=True):
            expected32 = expected | (0x80000000 if expected & 0x40000000 else 0)
            assert int(row[0]) == count and int(row[1],16) == expected32
            count += 1
    assert count == 5768
    original = json.loads((build/'INPUT_IDENTITY.json').read_text())
    for name, value in original['source_sha256'].items():
        if name=='ddr_candidate_writer.sv':
            # Restoring the diagnostic burst trial changed CRLF only; pin the
            # exact original unit-tested bytes and compare all normalized text.
            tested=P/'work/unit_20261013_084928_642814/source/ddr_candidate_writer.sv'
            assert digest(tested)==value
            assert (build/'source'/name).read_text()==tested.read_text()
        elif name not in ('tb_soc.sv','b_soc_engine.sv'): assert digest(build/'source'/name) == value
    for name,value in original['rom_sha256'].items(): assert digest(build/'rom'/name) == value
    generated_paths = [
        'project/b_soc.srcs/sources_1/bd/b_soc/b_soc.bd',
        'project/b_soc.gen/sources_1/bd/b_soc/hdl/b_soc_wrapper.v',
        'project/b_soc.gen/sources_1/bd/b_soc/synth/b_soc.v',
        'project/b_soc.gen/sources_1/bd/b_soc/sim/b_soc.v',
        'project/b_soc.ip_user_files/bd/b_soc/sim/b_soc.v',
        'project/b_soc.sim/sim_1/behav/xsim/tb_soc_vlog.prj',
        'project/b_soc.sim/sim_1/behav/xsim/tb_soc_vhdl.prj',
    ]
    result = dict(status='PASS_ACTUAL_PRODUCTION_BD_SYSTEM_FILE_AUDIT',
                  simulation_model=model,counters=counters,oracle_sha256=digest(oracle_path),exact_term_comparisons=433880,exact_sum_comparisons=433880,source_sha256={p.name:digest(p) for p in (build/'source').glob('*.sv')},
                  intentional_DDR_timeout_recommendation_warnings=len(runtime_warnings),
                  generated_file_sha256={name:digest(build/name) for name in generated_paths},
                  evidence_sha256={name:digest(sim/name) for name in ['system_pass.txt','system_edges.csv','system_candidates.csv','simulate.log']},
                  routed=False,board_execution=False,real_DDR_bandwidth=None)
    (build/'SYSTEM_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__': main()
