from core import *

check();execution=load(HERE/'TEST_EXECUTION.json');records=[];csvrows=[]
for case in load(HERE/'testing/INPUTS.json'):
    root=HERE/'testing/runs'/case['id'];r=[load(root/mode/'RESULT.json') for mode in ['Full','CNN']]
    if not all(x['complete'] for x in r):
        records.append(dict(case=case['id'],group=case['group'],pass_gate=False,status='FAIL_INCOMPLETE',windows={}));continue
    full,cnn=[np.load(root/mode/'states_raw.npy',mmap_mode='r') for mode in ['Full','CNN']]
    ff,cf=[np.load(root/mode/'flow.npy',mmap_mode='r') for mode in ['Full','CNN']]
    row,errors=score(case,full,cnn,ff,cf);row['status']='PASS_ORIGINAL_GATE' if row['pass_gate'] else 'FAIL_OR_NOT_EVALUABLE'
    np.save(root/'STEP_ERRORS.npy',errors);records.append(row)
    for name,w in row['windows'].items():
        if case['group']=='static':csvrows.append(dict(case=case['id'],window=name,scope='static',E=None,M=None,Q=None,field_angle=None,
            H_RMSE=w['H_RMSE'],R_RMSE=w['R_RMSE'],flow_RMSE=w['flow_RMSE'],passed=w['pass_gate']))
        else:
            for scope in ['flow','foreground_flow']:
                if scope not in w:continue
                f=w[scope];csvrows.append(dict(case=case['id'],window=name,scope=scope,E=f['field_error_E'],M=f['magnitude_ratio'],Q=f['Q'],field_angle=f['angle_deg'],
                    H_RMSE=None,R_RMSE=None,flow_RMSE=None,passed=f['pass_gate']))
first=load(HERE/'testing/INPUTS.json')[0]['id'];root=HERE/'testing/runs'/first
sham_same=np.array_equal(np.load(root/'Full/states_raw.npy',mmap_mode='r'),np.load(root/'Sham/states_raw.npy',mmap_mode='r'))
summary=dict(status='PASS_ALL_NEW_PREREGISTERED_GATES' if all(r['pass_gate'] for r in records) and sham_same else 'COMPLETED_WITH_FAILURES_OR_LIMITATIONS',
    records=records,passed=sum(r['pass_gate'] for r in records),total=len(records),Sham_all_states_bitwise_equal=sham_same,
    model_SHA=load(HERE/'MODEL_FREEZE.json')['sha256'],parameters=31168,training_updates_during_test=0,GPU=0,board=0,
    function_claim='controlled stimuli equivalence-to-Full gates; not neuronal-function percentage, direction accuracy, biological recovery, or natural optical flow truth',
    actual_commits=execution['commits'],actual_neural_wall_s=execution['wall_s'])
dump(HERE/'SUMMARY.json',summary)
with (HERE/'METRICS.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(csvrows)
print(json.dumps(dict(status=summary['status'],passed=summary['passed'],total=len(records),sham=sham_same)),flush=True)
