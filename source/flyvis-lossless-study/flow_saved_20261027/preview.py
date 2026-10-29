from pathlib import Path
import sys,json
R=Path('flyvis-lossless-study/ov5640_live_v261_20261026').resolve();sys.path.insert(0,str(R/'pc'))
import live_server
from flow_reader import FlowReader
live_server.FLOW=FlowReader(R/'assets');sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];D=R/'pc/rounds'/sid;app=live_server.App(json.loads((D/'session.json').read_text()),D/'records');assert app.store.camera_close['status']=='CLOSED';assert app.audit_result['status']=='PASS_ALL_SAVED_STATES'
print('Saved flow preview 8810; no board controls',flush=True);live_server.make_server(app,port=8810).serve_forever()

