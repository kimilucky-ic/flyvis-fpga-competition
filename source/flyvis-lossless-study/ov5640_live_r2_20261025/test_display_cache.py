import concurrent.futures,io,json,sys,time
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P/'bundle'),str(P/'pc')]
from live_server import App
old=P.parent/'ov5640_live_20261024';c=json.loads((old/'pc/session.json').read_text());app=App(c,old/'pc/records')
reads=[];original=app.store.read

def counted(k):reads.append(k);return original(k)
app.store.read=counted
first=json.loads(app.latest(-1));p=first['packet'];assert p['step_id']==31 and reads==[31]
for i in range(100):assert json.loads(app.latest(31))['packet'] is None
for i in range(100):assert app.frame(31,p['state_token'])==app.frame(31,p['state_token'])
assert reads==[31] and app.display_builds==1
m,source,r=original(31);pixel=np.asarray(Image.open(io.BytesIO(app.frame(31,p['state_token']))))
assert np.array_equal(pixel,np.frombuffer(source,np.uint8).reshape(480,800,3)[:,:,::-1])
try:app.frame(31,'wrong_state')
except ValueError:pass
else:raise AssertionError('wrong binding accepted')
with concurrent.futures.ThreadPoolExecutor(4) as pool:
 values=list(pool.map(lambda _:app.display(30),range(8)))
assert all(x==values[0] for x in values) and reads.count(30)==1
app.display(29);assert len(app.display_cache)==2
app.frame(31,p['state_token']);assert reads.count(31)==2 and len(app.display_cache)==2
result=dict(status='PASS_CPU_DISPLAY_CACHE_ACTUAL_FRAMES',unchanged_polls=100,repeated_image_requests=200,
 first_frame_decodes=1,concurrent_same_frame_builds=1,cache_capacity=2,wrong_binding_rejected=True,
 source_pixels_equal=True,eviction_reload_safe=True,board_actions=0)
(P/'evidence/DISPLAY_CACHE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
