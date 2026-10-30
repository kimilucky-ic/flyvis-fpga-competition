"""One fixed PC entry; reuse existing local receiver without board access."""
from pathlib import Path
import json,subprocess,sys,urllib.request,urllib.error,webbrowser
P=Path(__file__).resolve().parents[1]
c=json.loads((P/'pc/session.json').read_text());url='http://127.0.0.1:'+str(c['port'])
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    with opener.open(url+'/status',timeout=2) as response:status=json.load(response)
except urllib.error.URLError:
    raise SystemExit(subprocess.call([sys.executable,'-X','utf8','-B',str(P/'pc/live_server.py')],cwd=P))
if status.get('application')!='line11-live-v261':raise RuntimeError('8798 is occupied by an older or different receiver; close only its PC receiving window, then launch again.')
webbrowser.open(url)
print('Opened existing receiver. Create the next round from the page; no board operation.')
