"""CPU architecture arithmetic and dependency scan, NOT an RTL performance test.

Reuses the sealed LE64 stream. Does not reconstruct the graph or recompute the
integer oracle. No EDA, GPU, board, or accepted-artifact mutations.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,numpy as np
HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=B.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    old=load(B/'ramfix_r2_sim_20261012/FULL_RTL_RESULT.json')
    ooc=load(B/'ramfix_r2_ooc_20261012/OOC_RESULT.json')
    prep=load(B/'fullscale_20261012/PREPARATION.json');c=prep['contract']
    stream=ROOT/'flyvis-fpga/t4t5_scale_20261011/data/incoming_edges_le64.bin'
    assert sha(stream)=='208da3b1a8984928bcc338e0f773a664398ef5df1e53a9a889d29e3fed197ff2'
    records=np.fromfile(stream,dtype='<u8');E,H=c['edge_count'],c['H'];assert len(records)==E
    targets=((records>>36)&8191).astype(np.int32)
    last=[-1]*H;gaps=[]
    for i,t in enumerate(targets):
        if last[t]>=0:gaps.append(i-last[t])
        last[t]=i
    old_overhead=7*H+2
    assert 6*E+old_overhead==old['cycles']==2643658
    scenarios=[]
    for lanes in (1,2):
        cycles=(E+lanes-1)//lanes+old_overhead
        scenarios.append(dict(arithmetic_lanes=lanes,assumed_lane_initiation_interval=1,
            ideal_core_cycles_excluding_pipeline_fill_drain_and_hazards=cycles,
            at_100MHz_ms=cycles/100000,
            ideal_speedup_over_old_core=old['cycles']/cycles,
            assumptions='Perfect sustained supply; ordered accumulation without stalls; old clear+neuron overhead; not RTL or timing evidence'))
    indices=np.arange(E)
    delay=np.where(indices%1024==1023,7,np.where(indices%64>=48,3,0))
    old_bfm_lower=2*E+int(delay.sum())
    d=dict(status='CPU_ARCHITECTURE_OPTIONS_ONLY_NOT_RTL_OR_SYNTHESIS',source_sha256=sha(stream),
        accepted_simulation_result_sha256=sha(B/'ramfix_r2_sim_20261012/FULL_RTL_RESULT.json'),
        accepted_ooc_result_sha256=sha(B/'ramfix_r2_ooc_20261012/OOC_RESULT.json'),
        inherited_counts=dict(H=H,E=E,source_count=c['source_count'],weights=c['weight_count'],zeros=c['zero_weight_edges']),
        baseline=dict(core_cycles=old['cycles'],edge_cycles=6*E,non_edge_cycles=old_overhead,
            edge_cycle_fraction=6*E/old['cycles'],resources=ooc['utilization_scopes']['top']),
        scenarios=scenarios,
        dependencies=dict(min_same_target_edge_index_distance=min(gaps),same_target_distance_le_8=sum(g<=8 for g in gaps),same_target_distance_le_16=sum(g<=16 for g in gaps),
            distinct_targets=len(set(targets)),adjacent_same_target=int(np.sum(targets[1:]==targets[:-1])),
            limitation='Only frozen official sequence; arbitrary adjacent repeats still require forwarding or hazard stall and new directed validation'),
        ddr=dict(bytes_per_step=E*8,bus_width_bits=64,assumed_bus_clock_MHz=100,
            arithmetic_line_rate_MB_s=800,edge_transfer_only_line_rate_floor_ms=E/100000,
            edge_bandwidth_for_5ms_MB_s=E*8/.005/1e6,
            source_x_candidate_32bit_wire_bytes_per_step=(c['source_count']+2*H)*4,
            all_payload_if_same_DDR_for_5ms_MB_s=(E*8+(c['source_count']+2*H)*4)/.005/1e6,
            single_outstanding_reader_nominal_empty_clocks_per_burst=2,
            reader_saturated_model_cycles_including_old_non_edge_overhead=E+2*c['burst_count']+old_overhead,
            reader_saturated_model_ms_at_100MHz=(E+2*c['burst_count']+old_overhead)/100000,
            reader_model_limit='Aggregate PREP/ADDR bubbles; not cycle-accurate; finite prefetch/start/end effects omitted',
            measured_HP0_bandwidth_MB_s=None),
        old_bfm=dict(minimum_clocks_per_beat=2,sum_programmed_gap_cycles=int(delay.sum()),
            optimistic_transfer_lower_bound_cycles=old_bfm_lower,optimistic_transfer_lower_bound_ms_at_100MHz=old_bfm_lower/100000,
            explanation='posedge model deasserts rvalid after every beat, then generates next beat on a later posedge; excludes burst/AR/first/last overhead. Preserve old stress schedule and add a separate continuous-beat BFM for peak throughput.'),
        proposed_stage_budget=dict(DSP_max=16,BRAM36_equivalent_max=90,description='Proposed design budget for recommended one-edge-per-clock pipeline, NOT utilization prediction or user-approved constraint'),
        decision='PENDING_USER_ARCHITECTURE_CHOICE; no new RTL or EDA launched')
    (HERE/'THROUGHPUT_OPTIONS.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:d[k] for k in ('scenarios','dependencies','ddr','old_bfm')},indent=2))
if __name__=='__main__':main()
