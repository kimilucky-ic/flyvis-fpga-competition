"""CPU/stdlib-only synthetic gate tests; never launch reference/replacement."""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
from run_gate import validate_window,LaunchBlocked

HERE=Path(__file__).resolve().parent
def main():
    now=datetime(2026,10,11,12,tzinfo=timezone.utc)
    c=dict(campaign_id='TEST_ONLY',proposal_sha256='TEST_PROPOSAL',GPU_uuid='TEST_GPU',candidate_ids=['B_T5c','C_T4T5_all_centers'])
    t=dict(campaign_id='TEST_ONLY',proposal_sha256='TEST_PROPOSAL',decision='APPROVE_UNCHANGED_v1',authoritative_record='synthetic CPU fixture')
    a=dict(campaign_id='TEST_ONLY',owner='A_GPU',conflict_free=True,GPU_uuid='TEST_GPU',
        available_start=(now-timedelta(minutes=5)).isoformat(),available_end=(now+timedelta(minutes=90)).isoformat(),valid_until=(now+timedelta(minutes=90)).isoformat())
    w=dict(campaign_id='TEST_ONLY',GPU_uuid='TEST_GPU',candidate_ids=c['candidate_ids'],proposal_sha256='TEST_PROPOSAL',
        human_run_authorized=True,authorization_source='synthetic fixture only',human_confirmation_text='synthetic fixture only',
        start=now.isoformat(),end=(now+timedelta(minutes=90)).isoformat())
    cases=[]
    assert validate_window(c,t,a,w,now)==now+timedelta(minutes=90)
    cases.append(dict(test='complete synthetic window accepted by pure validator',pass_=True,actual_GPU_launch=False))
    mutations=[
        ('technical recommendation not approval',0,'decision','RECOMMEND'),
        ('no technical authority record',0,'authoritative_record',None),
        ('technical different proposal',0,'proposal_sha256','WRONG'),
        ('technical different campaign',0,'campaign_id','WRONG'),
        ('A not confirmed',1,'conflict_free',False),
        ('A wrong owner',1,'owner','UNKNOWN'),
        ('A wrong GPU',1,'GPU_uuid','WRONG'),
        ('A wrong campaign',1,'campaign_id','WRONG'),
        ('A availability too late',1,'available_start',(now+timedelta(minutes=1)).isoformat()),
        ('A availability too short',1,'available_end',(now+timedelta(minutes=89)).isoformat()),
        ('A confirmation expired',1,'valid_until',(now-timedelta(seconds=1)).isoformat()),
        ('human permission absent',2,'human_run_authorized',False),
        ('human text absent',2,'human_confirmation_text',None),
        ('human authority source absent',2,'authorization_source',None),
        ('human wrong GPU',2,'GPU_uuid','WRONG'),
        ('human wrong campaign',2,'campaign_id','WRONG'),
        ('candidate order changed',2,'candidate_ids',list(reversed(c['candidate_ids']))),
        ('threshold proposal changed',2,'proposal_sha256','WRONG'),
        ('slot starts in future',2,'start',(now+timedelta(seconds=1)).isoformat()),
        ('slot expired',2,'end',(now-timedelta(seconds=1)).isoformat()),
        ('slot longer than90min',2,'end',(now+timedelta(minutes=91)).isoformat()),
        ('start timezone absent',2,'start',now.replace(tzinfo=None).isoformat()),
        ('end missing',2,'end',None),
    ]
    for title,which,key,value in mutations:
        docs=[deepcopy(t),deepcopy(a),deepcopy(w)];docs[which][key]=value
        try:validate_window(c,*docs,now=now)
        except LaunchBlocked as e:cases.append(dict(test=title,pass_=True,error=str(e),actual_GPU_launch=False))
        else:raise AssertionError('gate incorrectly accepted '+title)
    result=dict(status='PASS_24_CPU_ONLY_LAUNCH_GATE_CASES',test_count=len(cases),cases=cases,
        evidence_level='SYNTHETIC_AUTHORIZATION_VALIDATOR_TESTS_ONLY',CUDA_operations=0,neural_updates=0,FPGA_execution=False,
        human_run_authorized=False,does_not_test_GPU_R_or_H_numeric_equivalence=True)
    out=HERE/'launch_gate_tests_20261011_r1.json'
    with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(result['status'],len(cases))
if __name__=='__main__':main()
