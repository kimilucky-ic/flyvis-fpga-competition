"""Aggregate accepted evidence; no EDA launch and no change to historical files."""
from pathlib import Path
import json,hashlib,re
P=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=load(P/'ACCEPTED.json');o=load(P/'OOC_RESULT.json')
    baseline=load(P.parent/'ramfix_r2_ooc_20261012/OOC_RESULT.json')
    t=o['utilization_scopes']['top'];bt=baseline['utilization_scopes']['top']
    peak=a['checks']['fullpeak']['cycles'];stress=a['checks']['fullstress']['cycles']
    assert a['status']=='PASS_PIPELINE_A_RTL_ACCEPTANCE' and o['resource_fit']
    for name,digest in a['rtl_sha256'].items():assert sha(P/'rtl'/name)==digest
    assert o['accepted_rtl_sha256']==sha(P/'ACCEPTED.json')
    # Every evidence link in the report must point to a real artifact. The final
    # manifest/preservation files are produced subsequently by seal.py.
    deferred={'MANIFEST_SHA256.json','PRESERVATION_VERIFICATION.json'}
    for target in re.findall(r'\]\(([^)]+)\)',(P/'PIPELINE_RESULT.md').read_text(encoding='utf-8')):
        if target not in deferred:assert (P/target).is_file(),target
    result=dict(status='MILESTONE_COMPLETE_RTL_EXACT_OOC_RESOURCE_FIT_SETUP_MET_HOLD_OPEN',
        evidence_level=['RTL_SIMULATION','OOC_SYNTHESIS_ONLY'],rtl_sha256=a['rtl_sha256'],
        accepted_rtl_sha256=sha(P/'ACCEPTED.json'),ooc_result_sha256=sha(P/'OOC_RESULT.json'),
        previous_baseline_result_sha256=sha(P.parent/'ramfix_r2_ooc_20261012/OOC_RESULT.json'),
        edge_comparisons=867760,candidate_comparisons=11536,integer_mismatches=0,
        cycles=dict(old=2643658,continuous_supply=peak,gapped_supply=stress),
        conditional_100MHz_ms=dict(old=26.43658,continuous_supply=peak/100000,gapped_supply=stress/100000),
        cycle_speedup=dict(continuous_supply=2643658/peak,gapped_supply=2643658/stress),
        resources={k:t[k] for k in ('LUT','FF','BRAM36_equivalent','RAMB36','RAMB18','DSP','LUT_memory')},
        resource_delta_from_R2={k:t[k]-bt[k] for k in ('LUT','FF','BRAM36_equivalent','DSP','LUT_memory')},
        timing=o['timing'],ooc_host_runtime=o['host_runtime'],
        measured_HP0_bandwidth_MBps=None,board_step_ms=None,routed_frequency_MHz=None,
        stop='Current milestone complete; no place/route, SoC, board or further simulation scheduled',
        next_action='Separate OOC implementation with defined physical clock source; inspect setup/hold before HP0 integration',
        limitations=o['limits']+['Supply scenarios do not reproduce identical bus handshake traces of old R2','One frozen initial request per fullgraph supply scenario'])
    (P/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','cycles','resources','resource_delta_from_R2')},indent=2))
if __name__=='__main__':main()
