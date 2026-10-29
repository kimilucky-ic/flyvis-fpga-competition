"""One-time source edit; no browser or computation."""
from pathlib import Path
p=Path(__file__).resolve().parents[3]/'viewer/live_camera.js'
s=p.read_text(encoding='utf-8')
start=s.index(' async function poll(token)')
end=s.index(' function parameters()',start)
old=s[start:end]
body=old[old.index('    lastSerial=p.serial;'):old.index('\n   }\n  }await')]
body=body.replace('receiptPending=request(', 'receiptPending=request(')
body=body.replace('render_ms:draw.render_ms,client_requests:', 'render_ms:draw.render_ms,raf_wait_ms:draw.raf_wait_ms,packet_slot_age_ms:draw.packet_slot_age_ms,document_visible:!document.hidden,client_requests:')
body=body.replace('});receiptPending.catch(()=>{});', '}).catch(e=>{if(running&&token===generation)fail(e);}).finally(()=>{receiptPending=null;});')
replacement=''' let receivedSerial=-1;
 function fail(e){running=false;++generation;clear();$('cameraStatus').textContent=`NOT_AVAILABLE · ${e.message}`;$('cameraStop').disabled=false;request('/api/stream/stop',{}).catch(()=>{});}
 const displaySlot=new FlyVisStreamWire.LatestFrame(callback=>{const queued=performance.now();requestAnimationFrame(()=>callback(queued));},item=>{
  const {p,response,image,token,readyAt}=item;if(!running||token!==generation||receiptPending)return;
  try{
   validate(p);const tick=performance.now();$('cameraImage').src=image.src;drawField('cameraHex',p.input_hex,true);drawField('cameraFlow',p.flow,false);drawCurve(p.recent_activity);spatial.accept(p.spatial);
   const draw={at:performance.now(),render_ms:performance.now()-tick,raf_wait_ms:tick-item.queuedAt,packet_slot_age_ms:tick-readyAt};
'''+body+'''
  }catch(e){fail(e);}
 });
 async function poll(token){try{while(running&&token===generation){
  if(!clock||performance.now()-clock.at>4000)await calibrate();
  const response=await request(`/api/stream/latest?wire=f32&after=${receivedSerial}`),status=response.status;
  streamReady=!!status.renderer_ready;$('cameraStatus').textContent=`${status.status} · ${status.capture?.state||''} · ${sourceKind} / 原 Full CUDA / 实时达标未验收`;
  if(status.result_valid===false)throw new Error(status.compute?.error||'STREAM_RESULT_REVOKED');
  if(response.packet){const p=FlyVisStreamWire.decode(response.packet);validate(p);
   let image=lastImage;if(lastImageSHA!==p.source.png_sha256){image=new Image();image.src='data:image/png;base64,'+p.preview_png;await image.decode();lastImage=image;lastImageSHA=p.source.png_sha256;}
   if(!running||token!==generation)return;receivedSerial=p.serial;const now=performance.now();
   const queuedAt=displaySlot.pending?.queuedAt??now;displaySlot.offer({p,response,image,token,readyAt:now,queuedAt});
  }
  await new Promise(resolve=>setTimeout(resolve,10));
 }}catch(e){if(running&&token===generation)fail(e);}}
'''
s=s[:start]+replacement+s[end:]
s=s.replace("function clear(){$('cameraIdentity')", "function clear(){displaySlot.clear();$('cameraIdentity')")
p.write_text(s,encoding='utf-8')
