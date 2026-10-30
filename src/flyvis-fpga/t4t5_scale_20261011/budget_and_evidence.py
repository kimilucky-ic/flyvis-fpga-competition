"""Arithmetic budgets and read-only historical report/COE audit. No EDA runs."""
import csv,json,math,re,shutil
import numpy as np
from pathlib import Path
from extract_graph import HERE,ROOT,sha,write_json,table

def main():
    stats=json.loads((HERE/'T4T5_FULL_GRAPH_STATS.json').read_text());N=stats['H'];E=stats['H_incoming_edges'];B=stats['R_in_sources'];S=N+B
    rows=[]
    def row(route,item,value,unit,formula,status='ESTIMATE_FROM_EXACT_GRAPH',note=''):
        rows.append([route,item,value,unit,formula,status,note])
    for name,count,width in [('state_one_buffer',N,31),('state_old_plus_candidate',2*N,31),('chemical',N,50),('bias',N,31),('inverse_tau',N,31),('x_H',N,31),('source_cache_H_plus_Rin',S,31)]:
        row('storage',name,count*width,'bits',f'{count}*{width}','EXACT_FORMAT_PAYLOAD','does not include BRAM packing or interfaces')
    row('storage','H_four_f32_arrays_state_bias_inv_x',N*4*4,'bytes',f'{N}*4*4','EXACT_FORMAT_PAYLOAD')
    row('storage','H_bias_inv_type_dictionary',8*2*4,'bytes','8*2*4','EXACT_FORMAT_PAYLOAD','type block boundaries are stored; future arbitrary graph may require type tags')
    modes=[('dense_all_sources_f32',45669*N*4,'45669*5768*4'),('dense_cached_sources_f32',S*N*4,f'{S}*{N}*4'),
           ('sparse_raw_f32_plus_u16_src_dst_u32_gid',E*12,f'{E}*12'),('sparse_Q20_24b_packed_73bits',math.ceil(E*73/8),f'ceil({E}*(21+15+13+24)/8)'),
           ('ROM_dictionary_LE64',E*8+2580,f'{E}*8+645*4'),('DDR_dictionary_LE64',E*8+2580,f'{E}*8+645*4')]
    for name,size,formula in modes:row('storage_mode',name,size,'bytes',formula,'EXACT_FORMAT_PAYLOAD','dense loses global ID order unless accompanied by an order schedule')
    row('storage','full_graph_f32_effective_weights',stats['edges']*4,'bytes','1513231*4','EXACT_FORMAT_PAYLOAD')
    row('storage','H_incoming_f32_weights',E*4,'bytes',f'{E}*4','EXACT_FORMAT_PAYLOAD')
    row('storage','H_incoming_dictionary_indices_bitpacked_plus_dict',math.ceil(E*10/8)+2580,'bytes','ceil(E*10/8)+645*4','EXACT_FORMAT_PAYLOAD','weights only; excludes connectivity')
    row('ROM','LE64_edges_raw_lower_bound_BRAM36',math.ceil(E*64/36864),'tiles','ceil(E*64/36864)','CAPACITY_LOWER_BOUND')
    row('ROM','LE64_edges_SDP72x512_packed',math.ceil(E/512),'tiles','ceil(E/512)','MAPPING_ESTIMATE','single 64b edge per 72b row')
    row('ROM','f32_weight_only_36x1024',math.ceil(E/1024),'tiles','ceil(E/1024)','MAPPING_ESTIMATE')
    row('dense','valid_edge_mask_all_sources',math.ceil(45669*N/8),'bytes','ceil(45669*N/8)','EXACT_FORMAT_PAYLOAD','needed to distinguish absent edges from preserved zero-weight edges')
    # Explicit width/depth mapping. Conservative whole tiles, no half-tile co-packing.
    bramA=[('old_H',6),('chemical_input',6),('x_H',6),('candidate_H',6),('parameter_config',1),('stream_buffers',4)]
    bramB=[('source_cache',17),('chemical50',12),('x_H',6),('candidate_H',6),('weight_dictionary',1),('parameter_config',1),('edge_ping_pong_2x1024x64',4),('state_IO_buffers',2)]
    for route,items in [('A',bramA),('B',bramB)]:
        for item,tiles in items:row(route,'BRAM_'+item,tiles,'BRAM36_tiles','width/depth schedule in ARCH_A_B_COMPARISON.md','MAPPING_ESTIMATE')
        subtotal=sum(x[1] for x in items);row(route,'BRAM_core_subtotal',subtotal,'BRAM36_tiles','sum component allocation','MAPPING_ESTIMATE')
        row(route,'BRAM_system_reserve',16,'BRAM36_tiles','chosen interface/debug/packing allowance','BUDGET_NOT_SYNTH')
        row(route,'BRAM_total_budget',subtotal+16,'BRAM36_tiles','core+16','BUDGET_NOT_SYNTH')
        row(route,'LUT_core_low',2000 if route=='A' else 3000,'LUT','historical serial core calibration + new control','ORDER_OF_MAGNITUDE_ESTIMATE')
        row(route,'LUT_core_high',5000 if route=='A' else 7000,'LUT','uncertain DMA/config/control synthesis','ORDER_OF_MAGNITUDE_ESTIMATE')
        row(route,'FF_core_low',1500 if route=='A' else 2000,'FF','registered shared datapath/control','ORDER_OF_MAGNITUDE_ESTIMATE')
        row(route,'FF_core_high',4500 if route=='A' else 6000,'FF','uncertain buffering/control','ORDER_OF_MAGNITUDE_ESTIMATE')
        row(route,'DSP_core_budget',8,'DSP48E1','nominal ~4 for 33x31 multiplication; reserve8','BUDGET_NOT_SYNTH')
        row(route,'LUT_system_reserve',6000,'LUT','chosen interface/debug margin','BUDGET_NOT_SYNTH')
        row(route,'FF_system_reserve',8000,'FF','chosen interface/debug margin','BUDGET_NOT_SYNTH')
        row(route,'DSP_system_reserve',8,'DSP48E1','chosen reserve','BUDGET_NOT_SYNTH')
    budgets={}
    for route in ['A','B','C92','C298']:
        n,b,e=(N,B,E) if route in ['A','B'] else ((92,1900,9207) if route=='C92' else (298,2919,20928))
        inp=(3*n if route=='A' else b+2*n)*4;out=n*4;edgeb=0 if route!='B' else e*8
        cycles=(9*n if route=='A' else 9*e+10*n+1) if route in ['A','B'] else 6*e+7*n+1
        # B: 9 cycles/edge, N clear cycles, 9 cycles/neuron. No DDR stall included.
        mul=2*n if route=='A' else e+2*n;add=4*n if route=='A' else e+4*n
        budgets[route]=dict(H=n,R_in=b,edges_in_PL=0 if route=='A' else e,input_bytes=inp,output_bytes=out,link_bytes=inp+out,edge_DDR_bytes=edgeb,
           PL_DDR_read_bytes=inp+edgeb,PL_DDR_write_bytes=out,whole_DDR_min_bytes=edgeb+2*(inp+out),cycles=cycles,multiplies=mul,adds=add,
           minimum_resident_DDR_bytes=2*(inp+out)+edgeb+(2644 if route=='B' else (64 if route=='A' else 0)),
           cycles_evidence='MEASURED_PRIOR_BEHAVIORAL_RTL' if route.startswith('C') else 'DESIGN_ESTIMATE_NO_DDR_STALL')
        for key in ['input_bytes','output_bytes','link_bytes','edge_DDR_bytes','PL_DDR_read_bytes','PL_DDR_write_bytes','whole_DDR_min_bytes','minimum_resident_DDR_bytes','cycles','multiplies','adds']:
            row(route,key,budgets[route][key],'cycles' if key=='cycles' else ('operations' if key in ['multiplies','adds'] else 'bytes'),
                'see machine-readable ARCHITECTURE_BUDGET.json','MEASURED_PRIOR_BEHAVIORAL_RTL' if route.startswith('C') and key=='cycles' else 'ESTIMATE_FROM_EXACT_GRAPH')
        for f in [50,100]:row(route,f'compute_at_{f}MHz_ms',cycles/(f*1000),'ms',f'{cycles}/({f}*1000)','CLOCK_ASSUMPTION_NOT_TIMING_CLOSED')
        for bw in [50,100,200,400]:
            row(route,f'PL_DDR_traffic_at_{bw}MBps_ms',(inp+edgeb+out)/(bw*1000),'ms',f'bytes/({bw}*1000)','BANDWIDTH_ASSUMPTION_NOT_MEASURED')
        for bw in [10,50,100]:row(route,f'host_link_payload_at_{bw}MBps_ms',(inp+out)/(bw*1000),'ms',f'bytes/({bw}*1000)','BANDWIDTH_ASSUMPTION_NOT_MEASURED','plus roundtrip/kernel/copy/synchronization latency')
    for route,core in [('C92',24),('C298',48)]:
        row(route,'BRAM_core_estimate',core,'BRAM36_tiles','edge+request+parameter+chemical+candidate widths/depths','MAPPING_ESTIMATE')
        row(route,'BRAM_including_system_reserve',core+16,'BRAM36_tiles','core+16','BUDGET_NOT_SYNTH')
    table(HERE/'STORAGE_BANDWIDTH_BUDGET.csv',['architecture','item','value','unit','calculation','evidence','note'],rows)
    write_json(HERE/'ARCHITECTURE_BUDGET.json',dict(architectures=budgets,BRAM_A_components=dict(bramA),BRAM_B_components=dict(bramB),resource_envelopes_are_estimates=True,
        capacity={'LUT':53200,'FF':106400,'BRAM36':140,'DSP':220},first_lane_count=1,alternative_lane_count=2,
        no_measured_throughput=True,whole_DDR_note='PL transfers plus one PS staging write/read, excludes network NIC DMA, extra CPU/cache copies, refresh and other traffic'))
    # Archive compact authentic reports for review; immutable originals are read-only.
    olf=Path('D:/FPGA_Archive_20261011/fly-olfactory-network-fpga')
    proj=olf/'vivado_projects/FlyOlfactoryNetwork';rtl=proj/'FlyOlfactoryNetwork.srcs/sources_1/new'
    evidence=HERE/'evidence';evidence.mkdir(exist_ok=True)
    files={
        'olfactory_xc7a35t_routed_utilization.rpt':proj/'reports_2024_2/fly_impl_utilization.rpt',
        'olfactory_xc7a35t_routed_timing.rpt':proj/'reports_2024_2/fly_impl_timing_summary.rpt',
        '67_full_soc_routed_utilization.rpt':ROOT/'flyvis-fpga/phase4_67_20261010/build/v1_bankfix_20261011_153525/implementation_utilization.rpt',
        '67_full_soc_routed_timing.rpt':ROOT/'flyvis-fpga/phase4_67_20261010/build/v1_bankfix_20261011_153525/implementation_timing_summary.rpt',
        '67_HLS_OOC_utilization.rpt':ROOT/'flyvis-fpga/phase3_20261010/build/hoc_20261010_190227/hls_ooc_route_utilization.rpt',
        '67_HLS_OOC_timing.rpt':ROOT/'flyvis-fpga/phase3_20261010/build/hoc_20261010_190227/hls_ooc_route_timing.rpt',
        '67_RTL_OOC_utilization.rpt':ROOT/'flyvis-fpga/phase3_20261010/build/rtl_ooc_2026_1_20261010_184604/rtl_ooc_route_utilization.rpt',
        '67_RTL_OOC_timing.rpt':ROOT/'flyvis-fpga/phase3_20261010/build/rtl_ooc_2026_1_20261010_184604/rtl_ooc_route_timing.rpt'}
    hashes={}
    for name,src in files.items():
        shutil.copyfile(src,evidence/name);assert sha(src)==sha(evidence/name);hashes[str(src)]=sha(src)
    coe=[];bits={}
    for p in sorted((proj/'FlyOlfactoryNetwork.ip_user_files/mem_init_files').glob('*.coe')):
        text=p.read_text();radix=int(re.search(r'memory_initialization_radix\s*=\s*(\d+)',text,re.I)[1]);assert radix==2
        tok=re.split(r'[\s,;]+',text.split('memory_initialization_vector=')[-1].strip()) if 'memory_initialization_vector=' in text else re.split(r'[\s,;]+',re.split(r'memory_initialization_vector\s*=\s*',text,flags=re.I)[1].strip())
        arr=np.array([int(x,2) for x in tok if x]);assert np.isin(arr,[0,1]).all();bits[p.stem]=arr
        coe.append([p.name,len(arr),int(arr.sum()),radix,sha(p)]);hashes[str(p)]=sha(p)
    table(evidence/'olfactory_COE_counts.csv',['file','binary_entries','nonzero_entries','radix','sha256'],coe)
    gl=np.concatenate([bits[f'weight_glomeruli_{i}'] for i in range(7)]).reshape(312,2092)
    pn=np.concatenate([bits[f'weight_PNKC_{i}'].reshape(640,121) for i in range(3)],axis=0)
    counts={'ORN_to_LNPN':int(gl[:,:1780].sum()),'LNPN_to_LNPN':int(gl[:,1780:].sum()),'PN_to_KC':int(pn[:1919].sum()),'PN_to_APL':int(pn[1919].sum()),
        'KC_to_APL':int(bits['weight_KC_APLMBONa3_0'][:1919].sum()),'KC_to_MBON0':int(bits['weight_KC_APLMBONa3_0'][1919:].sum()),'KC_to_MBON1':int(bits['weight_KC_MBONa1_0'].sum())}
    for f in [rtl/'pqn_ctrl.vhd',rtl/'PQN_PN.vhd',rtl/'PQN_KC.vhd',rtl/'sc_accumulator_PNKC.vhd',rtl/'sc_accumulator_PNKC_ctrl.vhd',rtl/'sc_accumulator_KC_APLMBON.vhd',
        ROOT/'flyvis-fpga/phase3_20261010/hls/flyvis_t5c_source_raw.cpp',ROOT/'flyvis-fpga/phase3_20261010/rtl/flyvis_source_raw_core.sv',
        ROOT/'flyvis-fpga/phase4_rtl92_20261011/rtl/scalable_source_raw_core.sv',ROOT/'flyvis-fpga/phase4_rtl92_20261011/artifacts/simulation_audit.json',
        ROOT/'flyvis-circuit-selection/phase3_ablation_screen_20261010/artifacts/formal_analysis/three_candidate_function_comparison.csv']:
        hashes[str(f)]=sha(f)
    release=ROOT/'flyvis-fpga/phase4_67_20261010/build/v1_bankfix_20261011_153525';man=json.loads((release/'release_manifest.json').read_text())
    for key in ['bitstream','hwh']:
        f=release/man['files'][key]['path'];hashes[str(f)]=sha(f);assert hashes[str(f)]==man['files'][key]['sha256']
    write_json(HERE/'HISTORICAL_EVIDENCE_AUDIT.json',dict(status='READ_ONLY_VERIFIED',
        olfactory=dict(device='xc7a35tcpg236-1',tool='Vivado2024.2.2 build6060944',stage='Routed',LUT=9363,FF=7655,BRAM36_equivalent=47.5,DSP=10,WNS_ns=.778,WHS_ns=.016,
            ORN_external_channels=1780,PQN_updated_cells=2235,PQN_LN=191,PQN_PN=121,PQN_KC=1919,PQN_APL_MBON_ON=4,
            physical_binary_COE_entries=sum(x[1] for x in coe),static_nonzero_connections=counts,total_static_nonzero_connections=sum(counts.values()),
            note='KC->MBON1 memory port supports 2-bit learning codes, static initial COE uses 0/1. ORN input channels are not 1780 additional PQN update cells.'),
        full_soc_67=dict(device='xc7z020clg400-2',tool='Vivado2026.1.1 build6605303',stage='Routed',LUT=13857,FF=14932,BRAM36_equivalent=14,DSP=7,WNS_ns=.133,WHS_ns=.067),
        current_92_298='behavioral XSim only; no synthesis',source_sha256=hashes))
    write_json(HERE/'RESOURCE_GATE.json',dict(checked_at='2026-10-11T17:50:48.7766834+08:00',free_physical_MiB=3584.23,total_physical_MiB=16176.54,cpu_load_percent=2,eda_processes=[],
        policy_min_free_MiB=4096,result='DEFER_SYNTHESIS',note='Read-only live host snapshot. No Vivado/HLS/synthesis/implementation/board job launched.'))
    print(json.dumps(dict(budgets=budgets,olfactory=counts,old_binary_entries=sum(x[1] for x in coe)),indent=2))

if __name__=='__main__':main()
