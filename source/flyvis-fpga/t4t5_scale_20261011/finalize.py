"""Bounded delivery check and identities; no baseline/RTL/EDA reruns."""
import importlib.metadata,json,platform,sys,math
import numpy as np
from extract_graph import HERE,ROOT,sha,write_json

def main():
    st=json.loads((HERE/'T4T5_FULL_GRAPH_STATS.json').read_text());au=json.loads((HERE/'INDEPENDENT_GRAPH_AUDIT.json').read_text())
    nu=json.loads((HERE/'NUMERIC_PROBE.json').read_text());bu=json.loads((HERE/'ARCHITECTURE_BUDGET.json').read_text())
    hi=json.loads((HERE/'HISTORICAL_EVIDENCE_AUDIT.json').read_text())
    assert st['H']==5768 and st['R']==39901 and sum(st['partitions'].values())==1513231
    assert st['partitions']==au['streaming_partition_counts'] and au['status']=='PASS'
    assert nu['requests']==36 and nu['H_outputs_per_architecture']==36*5768 and nu['edges_computed_B']==36*433880
    assert nu['status']=='PASS_BOUNDED_SOFTWARE_PROBE'
    d=dict(np.load(HERE/'data/incoming_edges.npz'));w=d['effective_weight'].astype('f8');t=d['target_h_index']
    q=lambda a:np.where(a>=0,np.floor(a*2**20+.5),np.ceil(a*2**20-.5)).astype('i8')
    wq=q(w);dictionary=np.fromfile(HERE/'data/effective_weight_dictionary_f32.bin',dtype='<f4');dq=q(dictionary.astype('f8'))
    assert np.array_equal(dq[d['dictionary_index']],wq)
    dq.astype('<i4').tofile(HERE/'data/weight_dictionary_q20_i32.bin')
    extra=dict(evidence_level='SOFTWARE_STATIC_ANALYSIS',q20_weight=dict(min_code=int(wq.min()),max_code=int(wq.max()),minimum_signed_width=next(i for i in range(2,33) if wq.min()>=-(1<<(i-1)) and wq.max()<(1<<(i-1))),
       max_abs_quantization_error=float(np.max(np.abs(wq/2**20-w))),maximum_nonzero_relative_error=float(np.max(np.abs(wq[w!=0]/2**20-w[w!=0])/np.abs(w[w!=0]))),
       original_nonzero_quantized_to_zero=int(np.count_nonzero((w!=0)&(wq==0))),unchanged_zero_weight_edge_count=int((w==0).sum()),dictionary_quantization_roundtrip=True),
       bank_scheduling=dict(two_lane_groups=len(t)//2,two_lane_same_bank_groups=int(np.count_nonzero(t[::2]%2==t[1::2]%2)),
        four_lane_groups=len(t)//4,four_lane_groups_with_conflict=sum(len(set((x%4).tolist()))<4 for x in t.reshape(-1,4)),
        rule='consecutive ordered edge groups, bank=target_index mod lane_count; not measured pipeline stalls'))
    write_json(HERE/'FORMAT_AND_BANK_AUDIT.json',extra)
    A=bu['architectures']['A'];B=bu['architectures']['B']
    assert A['cycles']==5768*9 and B['cycles']==9*433880+10*5768+1
    assert A['input_bytes']==3*5768*4 and B['input_bytes']==(2*5768+10634)*4
    assert B['PL_DDR_read_bytes']+B['PL_DDR_write_bytes']==3582792
    assert sum(bu['BRAM_A_components'].values())==29 and sum(bu['BRAM_B_components'].values())==49
    checks=[]
    for source,expected in hi['source_sha256'].items():
        actual=sha(source);checks.append({'path':source,'expected':expected,'actual':actual,'match':actual==expected})
    assert all(x['match'] for x in checks)
    versions={name:importlib.metadata.version(name) for name in ['numpy','torch','scipy','matplotlib']}
    write_json(HERE/'ENVIRONMENT.json',dict(python=sys.version,executable=sys.executable,platform=platform.platform(),packages=versions,
        task='read-only source / CPU software study',CUDA_used=False,EDA_started=False,board_IO=False))
    # No self-reference: final manifest excludes itself and the final check.
    entries={}
    for f in sorted(HERE.rglob('*')):
        if not f.is_file() or '__pycache__' in f.parts or f.name in ['MANIFEST_SHA256.json','DELIVERY_CHECK.json']:continue
        entries[str(f.relative_to(HERE))]={'bytes':f.stat().st_size,'sha256':sha(f)}
    write_json(HERE/'MANIFEST_SHA256.json',dict(algorithm='SHA256',scope='all deliverable files except manifest/check and Python bytecode',files=entries))
    for relative,info in entries.items():assert sha(HERE/relative)==info['sha256']
    write_json(HERE/'DELIVERY_CHECK.json',dict(status='PASS',evidence_level='DELIVERY_CONSISTENCY_ONLY',delivery_files_hashed_and_verified=len(entries),
        deliverable_bytes=sum(x['bytes'] for x in entries.values()),graph_partition_count_agreement=True,budget_arithmetic_checks=True,
        original_source_evidence_hash_comparisons=checks,all_selected_read_only_sources_unchanged=True,
        numeric_probe='36 software requests per A/B; stored R boundary; no live feedback',
        not_run=['new RTL simulation','new synthesis','new implementation','DDR bandwidth measurement','board execution','5768 GPU/PL closed loop'],
        user_architecture_choice='PENDING'))
    print(json.dumps(dict(status='PASS',files=len(entries),source_hashes=len(checks),bytes=sum(x['bytes'] for x in entries.values()),format_audit=extra),indent=2))

if __name__=='__main__':main()
