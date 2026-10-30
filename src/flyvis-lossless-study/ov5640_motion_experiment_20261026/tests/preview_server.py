from pathlib import Path
import sys,json
from unittest.mock import patch
P=Path(__file__).resolve().parents[1];sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
import live_server
x=json.loads((P/'evidence/CPU_RESULT.json').read_text())['fixtures']['white_black'];cfg=json.loads(Path(x['config']).read_text())
with patch.object(live_server.App,'audit_if_ready',lambda self:None):app=live_server.App(cfg,Path(x['records']))
app.audit_result=json.loads(Path(x['audit']).read_text())
server=live_server.make_server(app,'127.0.0.1',0)
print('CPU_FIXTURE_PREVIEW http://127.0.0.1:'+str(server.server_port),flush=True)
server.serve_forever()
