from pathlib import Path
import random,json,hashlib
P=Path(__file__).resolve().parent;D=P/'directed_vectors';D.mkdir(exist_ok=True)
H,S,E,W=8,20,256,8; rng=random.Random(121012)
src=[rng.randrange(-4000000,4000000) for _ in range(S)];src[0]=2000001
x=[rng.randrange(-200000,200000) for _ in range(H)]
w=[-1048576,524288,0,1,-1,262145,-1048575,131071]
bias=[rng.randrange(-2000000,2000000) for _ in range(H)];inv=[20<<24]*H
edges=[]
for i in range(E):
    s=0 if i==0 else rng.randrange(S);t=0 if i<96 else (i//3)%H;wi=1 if i==0 else i%W
    edges.append(i|(s<<21)|(t<<36)|(wi<<49))
def rnd(v,n):return (1 if v>=0 else -1)*((abs(v)+(1<<(n-1)))>>n)
chem=[0]*H;tr=[];sig=0
for e in edges:
    s=(e>>21)&32767;t=(e>>36)&8191;wi=(e>>49)&1023
    term=rnd(max(src[s],0)*w[wi],20);chem[t]+=term
    tr.append(((term&((1<<31)-1))<<50)|(chem[t]&((1<<50)-1)))
    sig=(((sig<<1)|(sig>>63))^e)&((1<<64)-1)
cand=[]
for i in range(H):
    vel=rnd((-src[i]+bias[i]+chem[i]+x[i])*inv[i],24)
    cand.append(src[i]+rnd(vel*83886,24))
    assert -(1<<30)<=vel<(1<<30) and -(1<<30)<=cand[-1]<(1<<30)
def mem(name,vals,bits):
    (D/name).write_text(''.join(f'{v&((1<<bits)-1):0{(bits+3)//4}x}\n' for v in vals),encoding='ascii')
mem('edges.mem',edges,64);mem('requests.mem',src+x,32);mem('weights.mem',w,24)
mem('neurons.mem',[(a<<31)|(b&((1<<31)-1)) for a,b in zip(inv,bias)],62)
mem('expected.mem',cand,31);mem('edge_traces.mem',tr,81)
(D/'test_config.svh').write_text(f"`define TEST_SIG 64'h{sig:016x}\n",encoding='ascii')
pairs=[(a,b) for a in (-(1<<32),-1,0,1,(1<<32)-1) for b in (-(1<<30),-1,0,1,(1<<30)-1)]
pairs +=[(rng.randrange(-(1<<32),1<<32),rng.randrange(-(1<<30),1<<30)) for _ in range(999)]
mem('mul_a.mem',[a for a,b in pairs],33);mem('mul_b.mem',[b for a,b in pairs],31);mem('mul_expected.mem',[a*b for a,b in pairs],64)
vals=[-(1<<63),(1<<63)-1,-1,0,1]
for shift in (20,24):
    for a in (-200,-2,-1,0,1,2,200):
        for d in (-1,0,1):vals.append((a<<shift)+(1<<(shift-1))+d)
vals += [rng.randrange(-(1<<63),1<<63) for _ in range(1024-len(vals))]
mem('round_input.mem',vals,64);mem('round20_expected.mem',[rnd(v,20) for v in vals],45);mem('round24_expected.mem',[rnd(v,24) for v in vals],41)
(D/'IDENTITY.json').write_text(json.dumps(dict(H=H,S=S,E=E,W=W,signature=f'{sig:016x}',seed=121012,
    scope='New synthetic pipeline directed tests; independent signed integer oracle; does not replace frozen fullgraph oracle',
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.glob('*.mem'))}),indent=2)+'\n',encoding='utf-8')
print('New directed vectors ready: 256 edges, 8 candidates, 1024 multiply and 1024 rounding cases')
