"""CPU-only readback of all serialized vectors and sealed previous delivery.

Does not run or replay the previous 92/298 acceptance or invoke any EDA tool.
"""
from pathlib import Path
import ast,hashlib,json,platform,time
from datetime import datetime,timezone,timedelta
import numpy as np
HERE=Path(__file__).resolve().parent;B=HERE.parent;ROOT=B.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def hexes(name):
    return [int(line,16) for line in (HERE/'vectors'/name).read_text(encoding='ascii').splitlines()]
def signed(v,bits):
    assert 0<=v<1<<bits
    return v-(1<<bits) if v&(1<<(bits-1)) else v
def main():
    started=time.perf_counter();prep=read(HERE/'PREPARATION.json');oracle=dict(np.load(HERE/'vectors/integer_oracle.npz'))
    assert prep['status']=='PASS_FULLSCALE_CPU_PREPARATION'
    assert sha(HERE/'prepare_fullscale.py')==prep['generator_sha256']
    for name,v in prep['files'].items():
        p=HERE/'vectors'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],name
    for name,v in prep['source_files'].items():assert sha(ROOT/name)==v['sha256'],name
    parent=read(B/'MANIFEST_SHA256.json')['files']
    assert sha(B/'MANIFEST_SHA256.json')==prep['parent_delivery_manifest_sha256']==read(B/'DELIVERY_VERIFICATION.json')['manifest_sha256']
    for name,v in parent.items():
        p=B/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],f'Previous delivery changed: {name}'
    edges=hexes('edges.mem');original=np.fromfile(ROOT/'flyvis-fpga/t4t5_scale_20261011/data/incoming_edges_le64.bin',dtype='<u8')
    assert len(edges)==433880 and np.array_equal(edges,original)
    packed=hexes('edge_traces.mem');assert len(packed)==len(edges)
    for i,value in enumerate(packed):
        assert value<1<<81
        assert signed(value>>50,31)==int(oracle['edge_term_q24'][i])
        assert signed(value&((1<<50)-1),50)==int(oracle['partial_chemical_q24'][i])
    requests=hexes('requests.mem');expect=np.r_[oracle['source_q24'],oracle['x_q24']]
    assert len(requests)==22170 and np.array_equal([signed(v,32) for v in requests],expect)
    for v in requests:assert signed(v,32)==signed(v&((1<<31)-1),31)
    assert np.array_equal([signed(v,31) for v in hexes('expected.mem')],oracle['candidate_q24'])
    weights=[signed(v,24) for v in hexes('weights.mem')]
    assert len(weights)==645 and np.array_equal(weights,np.fromfile(ROOT/'flyvis-fpga/t4t5_scale_20261011/data/weight_dictionary_q20_i32.bin',dtype='<i4'))
    neurons=hexes('neurons.mem');assert len(neurons)==5768
    for i,value in enumerate(neurons):
        assert value<1<<62
        assert signed(value&((1<<31)-1),31)==int(oracle['bias_q24'][i])
        assert signed(value>>31,31)==int(oracle['inv_tau_q24'][i])
    syntax=[]
    for p in sorted(HERE.glob('*.py')):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p));syntax.append(p.name)
    # Compile/elaborate/run are deliberately unavailable before the EDA gate.
    assert not (HERE/'LAUNCH_RECORD.json').exists(),'This is the pre-RTL handoff verifier'
    result=dict(status='PASS_CPU_PREPARATION_READBACK',checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        evidence_level='CPU_SERIALIZATION_AND_IDENTITY_ONLY',python=platform.python_version(),numpy=np.__version__,
        previous_delivery_files_unchanged=len(parent),previous_acceptance_rerun=False,
        original_LE64_records=433880,term_and_partial_pairs=433880,request_words=22170,candidate_words=5768,
        dictionary_words=645,neuron_parameter_words=5768,all_readback_mismatches=0,python_syntax_files=syntax,
        testbench_compile_or_elaboration=False,full_rtl_launches=0,elapsed_seconds=time.perf_counter()-started,
        scripts_sha256={p.name:sha(p) for p in sorted(HERE.glob('*.py'))},
        testbench_sha256=sha(HERE/'tb_fullscale.sv'),launcher_sha256=sha(HERE/'launch_xsim.ps1'),
        preparation_sha256=sha(HERE/'PREPARATION.json'),parent_delivery_manifest_sha256=sha(B/'MANIFEST_SHA256.json'))
    (HERE/'CPU_READBACK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
