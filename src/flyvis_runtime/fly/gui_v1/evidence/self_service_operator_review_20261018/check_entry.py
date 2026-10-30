"""Independent pure-Python operator boundary review. No device imports/calls."""
import hashlib,importlib.util,io,json
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).parent
path=ROOT/'fixed_board_review_snapshot.py'
spec=importlib.util.spec_from_file_location('fixed_board_review_snapshot',path)
entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
cfg=dict(installation_id='CPU_REVIEW',key='11'*32,pc_url='http://192.0.2.1:18790',bit_path='CPU_NOT_A_BITFILE')
inv=dict(existing_run=dict(run_id='a'*32,scope_sha256='b'*64,boot_id='CPU_BOOT'))

class Reply:
    def init__(self,value):self.data=json.dumps(value).encode()
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):return self.data[:n]

def opener(status):
    def request(req,timeout):
        body=json.loads(req.data)['body'];source='line2_software_only_success=True\n'
        response=dict(status=status,nonce=body['nonce'],inventory=body['inventory'])
        if status=='PREPARE':response.update(source=source,source_sha256=hashlib.sha256(source.encode()).hexdigest())
        return Reply(dict(body=response,mac=entry.signature(response,cfg['key'])))
    return request

rows=[]
for name,namespace,status in [
    ('first_same_notebook_entry',{},'PREPARE'),
    ('same_PC_ALREADY_PREPARED',{'line2_fixed_attempt':'previous','camera3_service_instance':SimpleNamespace(state='BOARD_PREPARED')},'ALREADY_PREPARED'),
    ('PC_reopened_new_preparation_after_clean_completed_owner',{'line2_fixed_attempt':'previous','camera3_service_instance':SimpleNamespace(state='FINISHED_PENDING_AUDIT')},'PREPARE'),
    ('failed_previous_owner_must_not_reprepare',{'line2_fixed_attempt':'previous','camera3_service_instance':SimpleNamespace(state='FAILED')},'PREPARE'),
]:
    try:
        entry.run(namespace,cfg,inspect=lambda *args:inv,open_url=opener(status),ask=lambda _:None)
        rows.append(dict(case=name,result='ACCEPTED',software_code_executed=namespace.get('line2_software_only_success',False)))
    except Exception as error:rows.append(dict(case=name,result='REJECTED',error=type(error).__name__+': '+str(error)))
result=dict(evidence='CPU_IN_MEMORY_AUTHENTICATED_BOUNDARY_ONLY',source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    board_access=False,GPU=False,camera=False,GUI=False,cases=rows)
(ROOT/'ENTRY_REVIEW.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
