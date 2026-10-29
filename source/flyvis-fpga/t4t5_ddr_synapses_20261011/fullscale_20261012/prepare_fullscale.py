"""One full T4/T5 request from the frozen official initial state.

Light CPU preparation only: no graph reconstruction, GPU, simulator or tool
launch. Reuses original LE64 bytes and the original 645 dictionary indices.
All intermediate integer ranges are checked; an overflow saves FAIL and stops.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time,math
import numpy as np

HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=B.parents[1]
SCALE=ROOT/'flyvis-fpga/t4t5_scale_20261011'
A0=ROOT/'flyvis-circuit-selection/phase3_ablation_screen_20261010/input_bundle_r2/initial_state_full.npy'
H,S,E,W=5768,16402,433880,645
RTL_NAMES=('axi_edge_reader.sv','edge_fifo.sv','ddr_synapse_core.sv','ddr_synapse_top.sv')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def write_json(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def quant(a,n):
    x=np.asarray(a,dtype=np.float64)*(1<<n)
    if not np.all(np.isfinite(x)):raise ValueError('Nonfinite frozen parameter/input')
    return np.where(x>=0,np.floor(x+.5),np.ceil(x-.5)).astype(np.int64)
def mem(p,values,bits):
    mask=(1<<bits)-1
    with Path(p).open('w',encoding='ascii',newline='\n') as f:
        for v in values:f.write(f'{int(v)&mask:0{(bits+3)//4}x}\n')
def rounded(v,n):
    quotient,remainder=divmod(abs(v),1<<n)
    if remainder>=(1<<(n-1)):quotient+=1
    return -quotient if v<0 else quotient
def checked(v,n,label,index):
    if not -(1<<(n-1))<=v<(1<<(n-1)):
        raise OverflowError(dict(stage=label,index=index,value=v,signed_bits=n))
    return v
def checked_array(a,n,label):
    if np.any((a<-(1<<(n-1)))|(a>=(1<<(n-1)))):raise OverflowError(label)
def main():
    started=time.perf_counter();dest=HERE/'vectors'
    if dest.exists():raise FileExistsError('Frozen vectors already exist; do not replace a prepared request')
    dest.mkdir(parents=True)
    oldseal=json.loads((B/'MANIFEST_SHA256.json').read_text())
    expected_seal=json.loads((B/'DELIVERY_VERIFICATION.json').read_text())['manifest_sha256']
    assert sha(B/'MANIFEST_SHA256.json')==expected_seal
    protected={n:sha(B/'rtl'/n) for n in RTL_NAMES}
    for n,v in protected.items():assert v==oldseal['files']['rtl/'+n]['sha256']
    sm=json.loads((SCALE/'MANIFEST_SHA256.json').read_text())['files']
    names=['data/incoming_edges.npz','data/incoming_edges_le64.bin','data/H_parameters.npz',
        'data/effective_weight_dictionary_f32.bin','data/weight_dictionary_q20_i32.bin',
        'data/numeric_probe_outputs.npz','T4T5_FULL_GRAPH_STATS.json','NUMERIC_PROBE.json']
    inputs={}
    for name in names:
        p=SCALE/name;entry=sm.get(name,sm.get(name.replace('/','\\')))
        assert entry is not None and sha(p)==entry['sha256'],f'Frozen input changed: {name}'
        inputs[str(p.relative_to(ROOT))]=dict(sha256=sha(p),bytes=p.stat().st_size)
    stats=json.loads((SCALE/'T4T5_FULL_GRAPH_STATS.json').read_text())
    assert sha(A0)==next(v for k,v in stats['input_sha256'].items() if k.endswith('initial_state_full.npy'))
    inputs[str(A0.relative_to(ROOT))]=dict(sha256=sha(A0),bytes=A0.stat().st_size)
    d=dict(np.load(SCALE/'data/incoming_edges.npz'));p=dict(np.load(SCALE/'data/H_parameters.npz'))
    records=np.fromfile(SCALE/'data/incoming_edges_le64.bin',dtype='<u8')
    wf=np.fromfile(SCALE/'data/effective_weight_dictionary_f32.bin',dtype='<f4')
    wq=np.fromfile(SCALE/'data/weight_dictionary_q20_i32.bin',dtype='<i4').astype(np.int64)
    gid=(records&0x1fffff).astype(np.int64);src=((records>>21)&32767).astype(np.int64)
    dst=((records>>36)&8191).astype(np.int64);wi=((records>>49)&1023).astype(np.int64)
    assert len(records)==E and len(wf)==len(wq)==W
    assert np.all(records>>59==0) and np.all(np.diff(gid)>0)
    assert int(gid.min())>=0 and int(gid.max())<1513231
    assert int(src.max())==S-1 and int(dst.max())==H-1 and int(wi.max())==W-1
    for a,key in ((gid,'global_edge_id'),(src,'source_cache_index'),(dst,'target_h_index'),(wi,'dictionary_index')):
        assert np.array_equal(a,d[key]),key
    cache=d['cache_global_ids'];hids=d['H']
    assert len(cache)==S and len(hids)==H and len(np.unique(cache))==S
    assert np.array_equal(cache[:H],hids) and not np.any(np.isin(cache[H:],hids))
    assert np.array_equal(cache[src],d['source_global']) and np.array_equal(hids[dst],d['target_global'])
    assert np.array_equal(wf[wi].view(np.uint32),d['effective_weight'].view(np.uint32))
    assert np.array_equal(quant(wf,20),wq) and np.array_equal(quant(d['effective_weight'],20),wq[wi])
    assert int(np.count_nonzero(src<H))==82793 and int(np.count_nonzero(src>=H))==351087
    assert int(np.count_nonzero(wf[wi]==0))==8790 and int(np.count_nonzero(wq[wi]==0))==8790
    assert np.unique(wi).size==W and np.unique(dst).size==H
    a0=np.load(A0);assert a0.shape==(45669,) and np.array_equal(p['H'],hids)
    assert np.array_equal(p['initial_state'].view(np.uint32),a0[hids].view(np.uint32))
    source=quant(a0[cache],24);x=np.zeros(H,dtype=np.int64)
    bias=quant(p['bias'],24);inv=quant(p['inverse_tau'],24)
    for a,label in ((source,'source'),(bias,'bias'),(inv,'inverse_tau')):checked_array(a,31,label)
    checked_array(wq,24,'weight')
    chem=[0]*H;term=np.empty(E,dtype=np.int64);partial=np.empty(E,dtype=np.int64)
    per_target_abs=[0]*H;signature=0;positive_ties=negative_ties=0
    for k,rec in enumerate(records):
        # Independent scalar decode of the original on-disk record.
        rec=int(rec);s=(rec>>21)&32767;t=(rec>>36)&8191;index=(rec>>49)&1023
        product=max(0,int(source[s]))*int(wq[index])
        checked(product,64,'edge_product',k)
        value=checked(rounded(product,20),31,'edge_term',k)
        chem[t]=checked(chem[t]+value,50,'chemical_partial',k)
        term[k]=value;partial[k]=chem[t];per_target_abs[t]+=abs(value)
        if abs(product)%(1<<20)==1<<19:
            positive_ties+=product>0;negative_ties+=product<0
        signature=(((signature<<1)|(signature>>63))&((1<<64)-1))^rec
    out=[];drives=[];velocities=[];deltas=[]
    for i,c in enumerate(chem):
        checked(c,31,'chemical_to_euler',i)
        drive=checked(-int(source[i])+int(bias[i])+c+int(x[i]),33,'drive',i)
        vp=checked(drive*int(inv[i]),64,'velocity_product',i)
        velocity=checked(rounded(vp,24),31,'velocity',i)
        dp=checked(velocity*83886,64,'dt_product',i)
        delta=checked(rounded(dp,24),31,'delta',i)
        out.append(checked(int(source[i])+delta,31,'candidate',i))
        drives.append(drive);velocities.append(velocity);deltas.append(delta)
    # Second arithmetic path uses NPZ mapping rather than LE64 decoding.
    products=np.maximum(source[d['source_cache_index']],0)*quant(d['effective_weight'],20)
    terms2=np.where(products>=0,(products+(1<<19))>>20,-((-products+(1<<19))>>20))
    chemical2=np.zeros(H,dtype=np.int64);np.add.at(chemical2,d['target_h_index'],terms2)
    def vector_round(v,n):return np.where(v>=0,(v+(1<<(n-1)))>>n,-((-v+(1<<(n-1)))>>n))
    out2=source[:H]+vector_round(vector_round(inv*(-source[:H]+bias+chemical2+x),24)*83886,24)
    assert np.array_equal(term,terms2) and np.array_equal(chem,chemical2) and np.array_equal(out,out2)
    probe=np.load(SCALE/'data/numeric_probe_outputs.npz')
    assert np.array_equal(probe['H'],hids) and np.array_equal(probe['global_incoming_edge_ids'],gid)
    assert np.array_equal(out,probe['B_q24'][0]),'Mismatch with prior independently saved step-0 B oracle'
    mem(dest/'edges.mem',records,64);mem(dest/'weights.mem',wq,24)
    mem(dest/'neurons.mem',[(int(bi)&((1<<31)-1))|((int(iv)&((1<<31)-1))<<31) for bi,iv in zip(bias,inv)],62)
    mem(dest/'requests.mem',np.r_[source,x],32);mem(dest/'expected.mem',out,31)
    mem(dest/'edge_traces.mem',(((int(a)&((1<<31)-1))<<50)|(int(b)&((1<<50)-1)) for a,b in zip(term,partial)),81)
    np.savez(dest/'integer_oracle.npz',source_q24=source,x_q24=x,bias_q24=bias,inv_tau_q24=inv,
        chemical_q24=np.asarray(chem,dtype=np.int64),candidate_q24=np.asarray(out,dtype=np.int64),
        edge_term_q24=term,partial_chemical_q24=partial,H_global_ids=hids,cache_global_ids=cache)
    addr=0xff0;remaining=E;bursts=boundaries=0
    while remaining:
        count=min(16,remaining,(4096-(addr&4095))//8)
        assert count>0
        addr+=8*count;remaining-=count;bursts+=1;boundaries+=(addr&4095)==0
    lower=6*E+7*H+2
    conservative=16*E+16*bursts+8*H+4096
    step_limit=8000000
    assert 2000000<lower<conservative<step_limit
    contract=dict(profile='B_MINI_Q24_Q20_V1_UNCHANGED',request_count=1,source='official frozen initial_state_full.npy',
        step_id=0,old_state_tag_hex=sha(A0)[:8],state_width=31,state_frac=24,weight_width=24,weight_frac=20,
        chemical_width=50,drive_width=33,dt_code=83886,rounding='nearest_ties_away_from_zero',overflow='reject_no_saturation',
        H=H,source_count=S,edge_count=E,weight_count=W,HH=82793,RH=351087,zero_weight_edges=8790,
        signature_hex=f'{signature:016x}',base_addr_hex='00000ff0',fifo_ram_slots=4,fifo_total_slots=5,
        burst_count=bursts,page_boundary_ends=boundaries,axi_timeout_cycles=64,step_timeout_cycles=step_limit,
        ideal_schedule_cycles_lower_bound=lower,conservative_bfm_schedule_bound=conservative,
        bound_explanation='16 cycles per edge includes at most 7 mock R wait cycles, register latency and serialized lane; 16 per burst bounds AR stalls/control; 8H+4096 covers clear/update/drain. Wall watchdog separate.',
        mock_ddr_schedule='ARREADY false each cycle%5==0 (max 1 cycle); R gap=7 each index%1024==1023, else 3 if index%64>=48, else 0; one outstanding, valid held during stall',
        same_target_adjacent_edges=int(np.count_nonzero(dst[1:]==dst[:-1])),source_indices_ge_16384=int(np.count_nonzero(src>=16384)),
        distinct_edge_sources=int(np.unique(src).size),last_source_occurrences=int(np.count_nonzero(src==S-1)),
        source_negative=int(np.count_nonzero(source<0)),edge_negative_weights=int(np.count_nonzero(wq[wi]<0)),
        zero_terms=int(np.count_nonzero(term==0)),negative_terms=int(np.count_nonzero(term<0)),
        positive_half_ties=positive_ties,negative_half_ties=negative_ties,
        fanin_min=int(np.bincount(dst,minlength=H).min()),fanin_max=int(np.bincount(dst,minlength=H).max()),
        all_targets_present=True,all_dictionary_entries_present=True,no_new_zero_quantized_edges=True)
    peaks={k:dict(max_abs_q=int(max(abs(int(v)) for v in a)),max_abs_real=max(abs(int(v)) for v in a)/(1<<24),signed_bits=n)
        for k,a,n in [('source',source,31),('term',term,31),('partial_chemical',partial,50),('chemical',chem,31),
                      ('drive',drives,33),('velocity',velocities,31),('delta',deltas,31),('candidate',out,31)]}
    defines=f'`define FULL_SIGNATURE 64\'h{signature:016x}\n`define OLD_STATE_TAG 32\'h{sha(A0)[:8]}\n`define FULL_STEP_LIMIT {step_limit}\n`define FULL_BURSTS {bursts}\n`define FULL_BOUNDARIES {boundaries}\n'
    (dest/'full_config.svh').write_text(defines,encoding='ascii')
    manifest=dict(status='PASS_FULLSCALE_CPU_PREPARATION',evidence_level='SOURCE_AND_INTEGER_SOFTWARE_ONLY',prepared_at=now(),
        contract=contract,range_peaks=peaks,actual_input_abs_sum_bound_max_q24=max(per_target_abs),
        source_files=inputs,protected_parent_rtl_sha256=protected,parent_delivery_manifest_sha256=expected_seal,
        scalar_vector_edge_matches=E,scalar_vector_candidates=H,prior_saved_B_step0_candidate_matches=H,
        full_rtl_has_run=False,elapsed_seconds=time.perf_counter()-started,generator_sha256=sha(__file__),
        files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.iterdir()) if p.is_file()})
    write_json(HERE/'PREPARATION.json',manifest)
    print(json.dumps({k:manifest[k] for k in ('status','scalar_vector_edge_matches','scalar_vector_candidates','prior_saved_B_step0_candidate_matches','elapsed_seconds')}))
    print(json.dumps(contract,ensure_ascii=False))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        write_json(HERE/'PREPARATION_FAIL.json',dict(status='FAIL_CPU_PREPARATION',at=now(),error_type=type(exc).__name__,error=str(exc)))
        raise
