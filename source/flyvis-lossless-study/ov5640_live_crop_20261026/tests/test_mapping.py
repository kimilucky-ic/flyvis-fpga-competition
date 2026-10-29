"""CPU-only mapping comparison: no capture, board, GPU or EDA."""
from pathlib import Path
import sys,json,struct,hashlib,time,statistics,importlib.util
import numpy as np
P=Path(__file__).resolve().parents[1];B=P/'bundle';sys.path.insert(0,str(B))
from direct_input import DirectAreaInput
from ps_input import PsInput,receptor_centers
oldpath=P.parent/'ov5640_live_ring_20261026/bundle/direct_input.py'
spec=importlib.util.spec_from_file_location('accepted_mapper',oldpath);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
new=DirectAreaInput();square=old.DirectAreaInput(48,48,'BGR');previous=old.DirectAreaInput(48,80,'BGR');reference=PsInput(48,48,'BGR')
assert new.contract['crop']==dict(top=0,left=16,height=48,width=48)
assert new.contract['grey_pixels']==2304 and new.contract['aspect_preserved']
assert np.all(new.bias==0) and new.valid.all() and new.area_indices.max()<2304
assert np.allclose(new.area_weights.sum(axis=0),1,rtol=0,atol=3e-7)
frames=[];sources=[]
for f in sorted((P.parent/'ov5640_live_r2_20261025/pc/records').glob('*.packet')):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw)[0]
 assert len(raw)==4+n+800*480*3+188416
 full=np.frombuffer(raw[4+n:4+n+800*480*3],np.uint8).reshape(480,800,3)
 frames.append(full[::10,::10].copy());sources.append(dict(path=str(f.resolve()),sha256=hashlib.sha256(raw).hexdigest()))
assert len(frames)==32
rng=np.random.default_rng(2601026)
frames.extend(rng.integers(0,256,(16,48,80,3),dtype=np.uint8))
frames.extend([np.full((48,80,3),v,np.uint8) for v in (0,127,255)])
frames.append(np.repeat(np.broadcast_to(np.arange(80,dtype=np.uint8)*3,(48,80))[:,:,None],3,axis=2))
frames.append(np.repeat(np.broadcast_to((np.arange(48,dtype=np.uint8)*5)[:,None],(48,80))[:,:,None],3,axis=2))
for channel in range(3):
 f=np.zeros((48,80,3),np.uint8);f[:,:,channel]=255;frames.append(f)
maxerr=0.;changed=0;differences=[]
for i,f in enumerate(frames):
 before=f.copy();crop=np.ascontiguousarray(f[:,16:64]);a=new.render(f);b=square.render(crop);ref=reference.render(crop)
 assert a.dtype==np.float32 and a.shape==(721,) and np.array_equal(a.view(np.uint32),b.view(np.uint32)),i
 error=float(np.max(np.abs(a-ref)));maxerr=max(maxerr,error);assert error<3e-6,(i,error)
 assert np.array_equal(f,before)
 altered=f.copy();altered[:,:16]=255-altered[:,:16];altered[:,64:]=255-altered[:,64:]
 assert np.array_equal(new.render(altered).view(np.uint32),a.view(np.uint32))
 old_a=previous.render(f);changed+=int(np.count_nonzero(a.view(np.uint32)!=old_a.view(np.uint32)))
 differences.append(float(np.mean(np.abs(a-old_a))))
assert np.all(new.render(np.zeros((48,80,3),np.uint8))==0)
assert np.min(new.render(np.full((48,80,3),255,np.uint8)))>0.9999998
bad=[np.zeros((48,48,3),np.uint8),np.zeros((48,80,3),np.float32),np.zeros((80,48,3),np.uint8)]
for f in bad:
 try:new.render(f)
 except ValueError:pass
 else:raise AssertionError('bad frame accepted')
# Light paired timing of same32 image fixtures. Desktop result, not ARM promise.
oldtimes=[];newtimes=[]
for i in range(128):
 f=frames[i%32]
 order=((previous,oldtimes),(new,newtimes)) if i%2==0 else ((new,newtimes),(previous,oldtimes))
 for mapper,times in order:
  start=time.perf_counter_ns();mapper.render(f);times.append((time.perf_counter_ns()-start)/1e6)
result=dict(status='PASS_CPU_CENTER_SQUARE_MAPPING',cases=len(frames),retained_camera_frames=32,downsample_fixture='800x480 saved R2 ->80x48 by fixed stride10; not new sensor capture',receptors=721,padded_receptors=0,old_fully_padded_receptors=int(np.count_nonzero(previous.bias==.5)),grey_pixels=2304,old_grey_pixels=3840,crop=dict(left=16,top=0,width=48,height=48),all_cases_bitwise_equal_explicit_square_mapper=True,max_abs_vs_independent_full_canvas_reference=maxerr,discarded_sides_have_no_effect=True,source_unchanged=True,invalid_shapes_types_rejected=3,changed_words_vs_letterbox=changed,mean_abs_change_vs_letterbox=float(np.mean(differences)),mapping_changes_stimulus=True,old_max_taps=previous.contract['max_taps'],new_max_taps=new.contract['max_taps'],desktop_timing_ms=dict(old_median=statistics.median(oldtimes),new_median=statistics.median(newtimes),paired_calls_each=128,ARM_measurement=False),board_operations=0,GPU_operations=0)
(P/'evidence/MAPPING_RESULT.json').write_text(json.dumps(result,indent=2));(P/'evidence/FIXTURE_SOURCES.json').write_text(json.dumps(sources,indent=2))
# Three bound inputs for focused bridge test; exactly what new mapper produces.
(P/'evidence/test_inputs.bin').write_bytes(b''.join(new.render(f).astype('<f4').tobytes() for f in frames[:3]))
print(json.dumps(result,indent=2))
