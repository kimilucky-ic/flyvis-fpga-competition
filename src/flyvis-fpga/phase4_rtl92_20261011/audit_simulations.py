"""Independent post-simulation CSV, identity, source and count audit."""
from pathlib import Path
import json,csv,re,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
current={p.name:sha(p) for p in (HERE/'rtl').glob('*.sv')}
accepted=[]; historical=[]
for run in sorted((HERE/'build').iterdir()):
    log=run/'xsim.log'
    if not log.exists():continue
    txt=log.read_text(errors='replace')
    m=re.search(r'ALL_PASS requests=(\d+) nodes=(\d+) edges=(\d+) banks=(\d+) chemical_reads=(\d+) request_reads=(\d+) same_target_pairs=(\d+) min_write_read_gap=(\d+) min_edge_write_read_gap=(\d+)',txt)
    if not m:continue
    sources={name:sha(run/name) for name in current}
    if sources!=current:
        historical.append(str(run.relative_to(HERE)));continue
    req,n,e,banks,cr,rr,repeats,gap,edgegap=map(int,m.groups())
    manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
    assert (req,n,e)==(manifest['n_requests'],manifest['n_h'],manifest['n_edges'])
    for name,digest in manifest['fixture_sha256'].items():
        if name.endswith('.mem'):assert sha(run/'rom'/name)==digest,(run,name)
    bits=np.array([int(v.strip(),16) for v in (run/'rom/expected.mem').read_text().splitlines()],dtype=np.int64)
    expected=np.where(bits>=(1<<30),bits-(1<<31),bits)
    with (run/'outputs.csv').open() as f: rows=list(csv.DictReader(f))
    assert len(rows)==n*req
    actual=np.array([int(x['raw_q24']) for x in rows],dtype=np.int64)
    assert np.array_equal(actual,expected),(run,'output mismatch')
    assert [(int(x['step']),int(x['neuron'])) for x in rows]==[(s,h) for s in range(req) for h in range(n)]
    with (run/'simulation_summary.csv').open() as f: summary=list(csv.DictReader(f))
    assert len(summary)==req
    assert all(int(x['status'])==0 and int(x['cycles'])==6*e+7*n+1 and int(x['edges'])==e for x in summary)
    assert repeats==manifest['consecutive_same_target_pairs']*req
    assert edgegap>=3 and gap>=1
    for label in ('malformed_sign','missing_input','numeric_overflow'):
        assert f'ERROR_PASS {label}' in txt,(run,label)
    result={'run':str(run.relative_to(HERE)).replace('\\','/'),'candidate':manifest['candidate'],
        'banks':banks,'requests':req,'n_h':n,'n_boundary':manifest['n_boundary'],'edges_per_request':e,
        'ordered_edges_verified':e*req,'states_verified':n*req,'compute_cycles_per_step':6*e+7*n+1,
        'candidate_and_partial_chemical_exact':True,'same_target_pairs_verified':repeats,
        'min_chemical_write_to_read_cycles':gap,'min_edge_write_to_read_cycles':edgegap,
        'synchronous_read_assertions':{'chemical':cr,'request':rr},'fault_cases_pass':3,
        'rtl_recurrent_feedback_steps':sum(c['internally_recurrent'] for c in manifest['cases']),
        'source_sha256':sources,'files_sha256':{x:sha(run/x) for x in ('xsim.log','xvlog.log','xelab.log','outputs.csv','simulation_summary.csv','manifest.json')},
        'tool':'Vivado XSim 2026.1.1 build 6605303','simulation_clock_period_ns':10,
        'wall_runtime_is_not_synthesis_timing':True}
    accepted.append(result)
required={('A_T4c',1),('A_T4c',2),('A_T4c',4),('C_T4T5_all_centers',1),('hazard',1),('hazard',2),('hazard',4)}
observed={(x['candidate'],x['banks']) for x in accepted}; missing=sorted(required-observed)
status={'status':'PASS' if accepted and not missing else 'INCOMPLETE_CURRENT_SOURCE_MATRIX',
    'evidence_level':'INDEPENDENT_INTEGER_ORACLE_AND_BEHAVIORAL_RTL_SIMULATION',
    'accepted_runs':accepted,'historical_passes_before_current_testbench':historical,
    'required_candidate_bank_groups':sorted(required),'missing_groups':missing,
    'limits':['RAM attributes and synchronous simulation do not prove physical BRAM inference.',
              'No synthesis, routed timing, SoC or board claim follows from this audit.']}
(HERE/'artifacts/simulation_audit.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print(json.dumps({'status':status['status'],'accepted_runs':len(accepted),'ordered_edges':sum(x['ordered_edges_verified'] for x in accepted),
    'states':sum(x['states_verified'] for x in accepted),'candidates':[x['candidate'] for x in accepted]}))
