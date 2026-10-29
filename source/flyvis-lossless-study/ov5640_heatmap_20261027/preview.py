from pathlib import Path
import sys,json
R=Path('flyvis-lossless-study/ov5640_live_v261_20261026').resolve();sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
from live_server import App,make_server
sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];D=R/'pc/rounds'/sid;app=App(json.loads((D/'session.json').read_text()),D/'records');assert app.store.camera_close['status']=='CLOSED';assert app.audit_result['status']=='PASS_ALL_SAVED_STATES';server=make_server(app,port=8808);print('Saved records preview 8808; no new round',flush=True);server.serve_forever()
