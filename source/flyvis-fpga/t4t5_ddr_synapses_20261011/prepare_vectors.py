"""Read frozen A fixtures; emit B LE64 streams and independent scalar oracle.

No original graph rebuild, inference, or GPU. Old 92/298 candidate networks
are NOT all-T4/T5 subsets, so their regression dictionaries remain separate.
The all-T4/T5 645-entry dictionary is copied/identity-checked for stage 2 only.
"""
from pathlib import Path
import hashlib,json,shutil
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRIOR=ROOT/'flyvis-fpga/phase4_rtl92_20261011'
SCALE=ROOT/'flyvis-fpga/t4t5_scale_20261011'
MASK=(1<<64)-1
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p,obj): Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def readmem(p): return [int(s,16) for s in Path(p).read_text().split()]
def signed(v,bits): return v-(1<<bits) if v&(1<<(bits-1)) else v
def mem(p,values,bits):
    Path(p).write_text(''.join(f'{int(x)&((1<<bits)-1):0{(bits+3)//4}x}\n' for x in values),encoding='ascii')
def rounded(x,n):
    q=(abs(x)+(1<<(n-1)))>>n
    return -q if x<0 else q
def fits(x,n):
    if not -(1<<(n-1))<=x<(1<<(n-1)): raise OverflowError((x,n))
    return x
def sig(records):
    h=0
    for r in records: h=(((h<<1)|(h>>63))&MASK)^int(r)
    return h
def oracle(source,x,edges,weights,neurons):
    chem=[0]*len(x);trace=[]
    for gid,s,t,wi in edges:
        term=fits(rounded(max(0,source[s])*weights[wi],20),31)
        chem[t]=fits(chem[t]+term,50);trace.append((gid,t,term,chem[t]))
    out=[]
    for i,(bias,inv) in enumerate(neurons):
        fits(chem[i],31);drive=fits(-source[i]+bias+chem[i]+x[i],33)
        velocity=fits(rounded(drive*inv,24),31)
        delta=fits(rounded(velocity*83886,24),31)
        out.append(fits(source[i]+delta,31))
    return out,trace
def build(name):
    dest=HERE/'fixtures'/name;dest.mkdir(parents=True,exist_ok=True)
    source_hashes={}; prior_cases=[]
    if name in ('mini','addr15'):
        h,b=4,(16398 if name=='addr15' else 8)
        weights=[1<<20,-(1<<20),1,-1,1<<19,-(1<<19),0]
        sources=[0,1,2,3,4,5,6,7,4,5,4,4,2,0,1,4,4,0,4,5]
        targets=[0]*12+[1,2,3,0,0,1,2,3]
        wis=[0,1,2,3,4,5,0,0,2,3,6,1,4,0,0,4,5,6,0,1]
        if name=='addr15': sources[18]=16401
        edges=[(100+i,s,t,w) for i,(s,t,w) in enumerate(zip(sources,targets,wis))]
        neurons=[(0,1<<24)]*h;cases=[]
        for k in range(1 if name=='addr15' else 6):
            source=[1<<24,-(1<<24),3,-3,1<<19,1<<19,0,-(1<<24),0,0,0,0]
            if name=='addr15':source.extend([0]*(h+b-len(source)));source[16401]=1<<22
            source[4]+=k
            cases.append((source,[0,(k-3)<<20,-(k+1)<<22,0]))
    else:
        src=PRIOR/('fixtures'+name)
        oldmanifest=json.loads((src/'manifest.json').read_text())
        for f,expected in oldmanifest['fixture_sha256'].items():
            if sha(src/f)!=expected: raise ValueError(f'Frozen fixture hash changed: {src/f}')
        d=np.load(src/'original_mapping.npz');h=oldmanifest['n_h'];b=oldmanifest['n_boundary']
        weights=list(dict.fromkeys(int(v) for v in d['weight_q20']));lookup={v:i for i,v in enumerate(weights)}
        edges=[(int(g),int(s) if sh else h+int(s),int(t),lookup[int(w)]) for g,sh,s,t,w in zip(
            d['original_global_edge_ids'],d['source_is_h'],d['source_local'],d['target_local'],d['weight_q20'])]
        neurons=[(signed(v&((1<<31)-1),31),signed(v>>31,31)) for v in readmem(src/'neurons.mem')]
        request=readmem(src/'requests.mem');prior_out=readmem(src/'expected.mem');prior_trace=readmem(src/'edge_traces.mem')
        cases=[];words=b+2*h
        for k in range(4):
            raw=[signed(v,32) for v in request[k*words:(k+1)*words]]
            cases.append((raw[b:b+h]+raw[:b],raw[b+h:]))
        source_hashes={str((src/f).relative_to(ROOT)):sha(src/f) for f in oldmanifest['fixture_sha256']}
        source_hashes[str((src/'manifest.json').relative_to(ROOT))]=sha(src/'manifest.json')
        prior_cases=oldmanifest['cases'][:4]
    assert len(weights)<=1024 and h<=8192 and h+b<=32768
    records=[g|(s<<21)|(t<<36)|(w<<49) for g,s,t,w in edges]
    assert all(a[0]<z[0] for a,z in zip(edges,edges[1:]))
    decoded=[(r&((1<<21)-1),(r>>21)&32767,(r>>36)&8191,(r>>49)&1023) for r in records]
    assert decoded==edges
    req=[];out=[];tr=[];round_pos=round_neg=zero_terms=0
    for k,(source,x) in enumerate(cases):
        if prior_cases and prior_cases[k]['internally_recurrent']:
            assert source[:h]==out[-h:], 'Frozen short recurrence old H differs from preceding candidate'
        result,trace=oracle(source,x,edges,weights,neurons)
        if name not in ('mini','addr15'):
            assert result==[signed(v,31) for v in prior_out[k*h:(k+1)*h]]
            assert [(t,s) for _,_,t,s in trace]==[(signed(v>>50,31),signed(v&((1<<50)-1),50)) for v in prior_trace[k*len(edges):(k+1)*len(edges)]]
        for _,s,_,w in edges:
            product=max(0,source[s])*weights[w]
            if abs(product)%(1<<20)==1<<19:
                if product>0:round_pos+=1
                if product<0:round_neg+=1
        zero_terms+=sum(t==0 for _,_,t,_ in trace)
        req.extend(source+x);out.extend(result)
        tr.extend(((term&((1<<31)-1))<<50)|(cs&((1<<50)-1)) for _,_,term,cs in trace)
    mem(dest/'edges.mem',records,64);mem(dest/'weights.mem',weights,24)
    mem(dest/'neurons.mem',[(bi&((1<<31)-1))|((iv&((1<<31)-1))<<31) for bi,iv in neurons],62)
    mem(dest/'requests.mem',req,32);mem(dest/'expected.mem',out,31);mem(dest/'edge_traces.mem',tr,81)
    (dest/'fixture_config.svh').write_text(f'`define TEST_H {h}\n`define TEST_S {h+b}\n`define TEST_E {len(edges)}\n`define TEST_W {len(weights)}\n`define TEST_STEPS {len(cases)}\n`define TEST_SIGNATURE 64\'h{sig(records):016x}\n`define TEST_MINI {int(name=="mini")}\n',encoding='ascii')
    summary=dict(name=name,H=h,source_count=h+b,edge_count=len(edges),weight_count=len(weights),requests=len(cases),
        original_graph=name not in ('mini','addr15'),all_T4T5_full_graph=False,source_hashes=source_hashes,prior_cases=prior_cases,
        dictionary='per-fixture Q20 regression dictionary; no alteration of full 645-entry dictionary',
        signature=f'{sig(records):016x}',same_target_pairs=sum(a[2]==z[2] for a,z in zip(edges,edges[1:])),
        zero_weight_edges=sum(weights[w]==0 for _,_,_,w in edges),zero_terms=zero_terms,positive_half_ties=round_pos,negative_half_ties=round_neg,
        prior_oracle_crosscheck=name not in ('mini','addr15'),files={p.name:sha(p) for p in dest.iterdir() if p.suffix in ('.mem','.svh')})
    js(dest/'manifest.json',summary);return summary
def main():
    result=[build(n) for n in ('mini','addr15','92','298')]
    # A bounded identity bridge, NOT repeat audit of the 1.5M-edge graph.
    manifest=json.loads((SCALE/'MANIFEST_SHA256.json').read_text())['files']
    identity={}
    for n in ('incoming_edges_le64.bin','effective_weight_dictionary_f32.bin','weight_dictionary_q20_i32.bin'):
        f=SCALE/'data'/n;key='data\\'+n
        expected=manifest.get(key,manifest.get('data/'+n))['sha256']
        assert sha(f)==expected
        identity[str(f.relative_to(ROOT))]=dict(sha256=expected,bytes=f.stat().st_size)
    stage2=HERE/'stage2_format';stage2.mkdir(exist_ok=True)
    shutil.copyfile(SCALE/'data/weight_dictionary_q20_i32.bin',stage2/'weight_dictionary_q20_i32.bin')
    js(stage2/'INHERITED_IDENTITY.json',dict(status='SOURCE_IDENTITY_ONLY_FULL_RTL_NOT_RUN',
        full_H=5768,source_count=16402,edges=433880,HH=82793,RH=351087,zero_weight_edges=8790,weight_entries=645,files=identity))
    js(HERE/'FIXTURE_PREPARATION.json',dict(status='PASS_SOFTWARE_FIXTURES',generator_sha256=sha(__file__),fixtures=result))
    print(json.dumps([{k:s[k] for k in ('name','H','source_count','edge_count','weight_count','requests','same_target_pairs')} for s in result]))
if __name__=='__main__':main()
