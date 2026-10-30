"""CPU-only concurrency, resource, ancestry and owned-termination checks."""
from pathlib import Path
import ast,json
from gate_policy import group_eda_records,evaluate_gate,terminate_owned

P=Path(__file__).resolve().parent

def main():
    cases=[]
    own=r'C:\work\hardware_b'
    memory=dict(available_MiB=3500,commit_headroom_MiB=10000)
    def rec(pid,ppid,name,created,cwd=r'C:\work\hardware_a'):
        return dict(pid=pid,ppid=ppid,name=name,created=created,cwd=cwd,
                    cmdline=[r'C:\AMDDesignTools\2026.1.1\Vivado\bin\vivado.exe','-mode','batch'])
    def check(name,records,expected,concurrent=True,fresh=False,sample=None,errors=None):
        snapshot=dict(groups=group_eda_records(records),inspection_errors=errors or [])
        result=evaluate_gate(sample or memory,snapshot,concurrent,fresh,own)
        assert result['allowed']==expected,(name,result)
        cases.append(dict(name=name,status='PASS',result=result))
        return snapshot
    a=rec(100,10,'vivado.exe',1000)
    check('NO_EXISTING_EDA_OVERRIDE_IGNORES_A_THREAD',[],True)
    snapshot=check('ONE_VIVADO_WITH_EDA_CHILD_AND_WRAPPER',[a,rec(101,100,'cmd.exe',1001),rec(102,101,'rdi_synth.exe',1002)],True)
    assert len(snapshot['groups'])==1 and len(snapshot['groups'][0]['members'])==2
    check('TWO_INDEPENDENT_VIVADO_JOBS',[a,rec(200,20,'vivado.exe',1000)],False)
    check('EXISTING_XSIM_JOB',[rec(200,20,'xsim.exe',1000)],False)
    check('EXISTING_B_CWD',[rec(100,10,'vivado.exe',1000,own+r'\physical\build')],False)
    referenced=dict(a,cmdline=a['cmdline']+['-source',own+r'\physical\implement.tcl'])
    check('EXISTING_B_COMMAND_REFERENCE',[referenced],False)
    check('UNKNOWN_EXISTING_PROJECT',[dict(a,cwd=None)],False)
    check('INCOMPLETE_INVENTORY',[],False,errors=[dict(pid=1,error='unknown')])
    check('LOW_PHYSICAL_MEMORY',[],False,sample=dict(memory,available_MiB=3071))
    check('LOW_COMMIT_HEADROOM',[],False,sample=dict(memory,commit_headroom_MiB=4095))
    check('EXACT_CAPACITY_THRESHOLDS',[],True,sample=dict(available_MiB=3072,commit_headroom_MiB=4096))
    check('DEFAULT_SERIAL_REQUIRES_FRESH_A_RELEASE',[],False,concurrent=False)
    check('DEFAULT_SERIAL_FRESH_RELEASE',[],True,concurrent=False,fresh=True)
    check('DEFAULT_SERIAL_REJECTS_OTHER_VIVADO',[a],False,concurrent=False,fresh=True)
    # A later-created process at the old parent PID must not absorb a child.
    check('REUSED_PARENT_PID_NOT_AN_ANCESTOR',[dict(a,created=2000),rec(102,100,'rdi_synth.exe',1002)],False)
    killed=[]
    class FakeProcess:
        def init__(self,pid,created):self.pid=pid;self.created=created
        def create_time(self):return self.created
        def terminate(self):killed.append(self.pid)
    own_process=FakeProcess(300,30);reused=FakeProcess(301,31);unowned=FakeProcess(100,10)
    current={300:own_process,301:FakeProcess(301,99),100:unowned}
    actions=terminate_owned([own_process,reused,unowned],{(300,30):{},(301,31):{}},current.__getitem__)
    assert killed==[300] and any(x['action']=='SKIPPED_REUSED_PID' for x in actions)
    cases.append(dict(name='STOP_ONLY_KNOWN_OWNED_IDENTITIES_NEVER_OTHER_A_OR_REUSED_PID',status='PASS',actions=actions))
    for file in P.glob('*.py'):ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
    result=dict(status='PASS_CPU_ONLY_POLICY_CHECKS',cases=cases,case_count=len(cases),
                Python_AST='PASS',vendor_invocations=0,real_processes_terminated=0)
    (P/'POLICY_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],case_count=len(cases),vendor_invocations=0)))
if __name__=='__main__':main()
