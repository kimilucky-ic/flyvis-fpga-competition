"""Export archived result playback; never presented as live closed-loop video."""
from pathlib import Path
import hashlib,json
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).parent / 'sealed_v3_800_7c53b766f037'
STIMULUS = Path('C:/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/controlled_video_20261010_r1/sources/01_off_right.mp4')
def sha(data): return hashlib.sha256(data).hexdigest()
output = (OUT / 'original_archive_contents/run/PL_outputs_800_i32le.bin').read_bytes()
assert sha(output) == '1a1dd93416a310d292c2294a999d4c8d965b1887a8eb67d08b3a6b1249829665'
assert sha(STIMULUS.read_bytes()) == '0ce06450d5c59da25157780197dd64f7080969331301371027406fcb6c69d880'
codes = np.frombuffer(output,dtype='<i4').reshape(800,67)
states = codes / float(1<<22)
plt.style.use('dark_background')
fig,ax = plt.subplots(figsize=(6.8,4.8),dpi=100)
fig.patch.set_facecolor('#101418'); ax.set_facecolor('#101418')
image = ax.imshow(states.T,aspect='auto',origin='lower',interpolation='nearest',extent=(-.5,799.5,-.5,66.5),cmap='coolwarm')
ax.set_xlabel('Recorded reference request row')
ax.set_ylabel('H neuron index')
ax.set_title('Archived PL candidate matrix (all 800 requests)',fontsize=11)
bar = fig.colorbar(image,ax=ax,pad=.03)
bar.set_label('Q22 state = integer code / 2^22',fontsize=9)
fig.tight_layout(); fig.canvas.draw()
fig.savefig(OUT / 'archived_pl_candidates_800.png')
plot = cv2.cvtColor(np.asarray(fig.canvas.buffer_rgba())[:,:,:3],cv2.COLOR_RGB2BGR)
line_y0 = round(plot.shape[0]-ax.bbox.y1)
line_y1 = round(plot.shape[0]-ax.bbox.y0)
xs = [round(ax.transData.transform((i,0))[0]) for i in range(800)]
plt.close(fig)
cap = cv2.VideoCapture(str(STIMULUS)); inputs=[]
while True:
    ok,frame=cap.read()
    if not ok: break
    inputs.append(frame)
cap.release()
assert len(inputs)==240
video = OUT / 'FlyVis67_800_results_ARCHIVAL_REPLAY_NOT_CLOSED_LOOP.mp4'
writer = cv2.VideoWriter(str(video),cv2.VideoWriter_fourcc(*'mp4v'),30,(1280,800))
assert writer.isOpened()
def text(im,s,x,y,scale=.55,color=(215,225,230)):
    cv2.putText(im,s,(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,color,1,cv2.LINE_AA)
for k in range(300):
    row = min(799,round(k*799/299))
    im = np.full((800,1280,3),(24,20,16),dtype=np.uint8)
    text(im,'FlyVis T5c67 | verified 800 request FPGA result replay',35,45,.8)
    text(im,'ARCHIVAL PRESENTATION: input animation + previously computed PL outputs',35,80,.57)
    text(im,'Existing stimulus: 01_off_right.mp4 (slowed for viewing)',35,130,.49)
    text(im,'800 / 800 requests | 53,600 exact integer matches',575,130,.52,(130,235,150))
    source_frame = min(239,row*240//800)
    im[155:655,35:535] = cv2.resize(inputs[source_frame],(500,500))
    current_plot = plot.copy()
    cv2.line(current_plot,(xs[row],line_y0),(xs[row],line_y1),(110,245,140),2)
    im[155:635,575:1255] = current_plot
    text(im,'Displayed archived request row: %04d /0799' % row,575,672,.54,(130,235,150))
    text(im,'Actual live board campaign: 482.591 s; playback is shortened',35,710,.56)
    text(im,'PL computed 6537 edges/request and 67 candidate neuron updates',35,745,.54)
    text(im,'Recorded old_H | No feedback/COMMIT | Not live footage | Scientific precision pending',35,782,.47,(110,190,250))
    writer.write(im)
    if k==150: cv2.imwrite(str(OUT / 'presentation800_preview.jpg'),im)
writer.release()
cap = cv2.VideoCapture(str(video)); decoded=0
while True:
    ok,frame=cap.read()
    if not ok: break
    assert frame.shape[:2]==(800,1280)
    decoded+=1
cap.release()
assert decoded==300
manifest = {
    'role':'Archived800request result playback, not live recording or true closed loop',
    'video_file':video.name,'video_sha256':sha(video.read_bytes()),
    'fps':30,'frames':300,'duration_s':10,
    'stimulus_sha256':sha(STIMULUS.read_bytes()),'actual_pl_output_sha256':sha(output),
    'board_campaign_elapsed_s':482.59099932000026,
    'visual_mapping':'Whole accepted stimulus displayed once, slowed; indexed candidate rows from the archived800request run. Frames sample rows for presentation, not a realtime measurement.',
    'source_raw_archive_sha256':'aba7b8a54b61dc421eca48045b77d040d5c8e0fc9b9e67187b05dc77045d6c79',
    'true_closed_loop':False,'live_recording':False,'scientific_acceptance':'NOT_GRANTED',
    'plot_png_sha256':sha((OUT / 'archived_pl_candidates_800.png').read_bytes()),
}
(OUT / 'PRESENTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('VIDEO:',video)
print('VIDEO_SHA256:',manifest['video_sha256'])
