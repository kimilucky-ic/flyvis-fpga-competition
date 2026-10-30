"""One new CPU-only policy/HMAC admission test. No listener or devices."""
import json,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
s=unittest.defaultTestLoader.loadTestsFromName('test_ps_commit_evidence.PSAdmissionTests')
with (P/'CPU_ADMISSION.log').open('x',encoding='utf8') as f:r=unittest.TextTestRunner(stream=f,verbosity=2).run(s)
v=dict(tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),devices=0)
(P/'CPU_ADMISSION.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v));sys.exit(not r.wasSuccessful())
