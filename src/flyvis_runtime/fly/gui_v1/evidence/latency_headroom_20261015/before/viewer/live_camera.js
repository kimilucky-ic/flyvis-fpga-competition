'use strict';
(() => {
 const $=id=>document.getElementById(id);let running=false,generation=0,run=null,lastSerial=-1,painted=0,start=0,uv=null,clock=null,sourceKind=null,inputSequence=0,segment=0,segmentStart=0,lastParameters=null,firstPaint=0;
 const spatial=new FlyVisSpatialView('cameraSpatial');let streamReady=false,lastImage=null,lastImageSHA=null,lastIdentityAt=0,receiptPending=null,requestMetrics={};
 let consumer=null,starting=false,consumerPending=null,preparingFrame=false,nextPreparedAt=0;
 const colors=['#69cfff','#ffb97e','#cba3f5','#7bdbab','#ead76c','#fa93bc','#8aa7ff','#b6d47e'];
 for(const id of ['cameraHex','cameraFlow','cameraCurve']){$(id).width=760;$(id).height=id==='cameraCurve'?300:350;}
 async function request(path,body){
  const key=path.split('?')[0],m=requestMetrics[key]||(requestMetrics[key]={count:0,wall_ms:0,parse_ms:0,transport_retries:0});
  // Only retry read-only GET transport failures. POSTs, identity errors, HTTP
  // rejections and invalid JSON are never replayed or hidden.
  for(let attempt=0;attempt<(body===undefined?3:1);attempt++){
   const t=performance.now();let r;
   try{r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});}
   catch(e){if(body===undefined&&attempt<2){m.transport_retries++;await new Promise(resolve=>setTimeout(resolve,100*(attempt+1)));continue;}throw Error(key+': '+e.message);}
   const arrived=performance.now(),value=await r.json();m.count++;m.wall_ms+=performance.now()-t;m.parse_ms+=performance.now()-arrived;
   if(!r.ok)throw Error(value.error||value.status);return value;
  }
 }
 function clear(){displaySlot.clear();$('cameraIdentity').textContent='当前结果无效或已撤销；历史 run 身份保存在本次会话日志。';spatial.clear();for(const id of ['cameraHex','cameraFlow','cameraCurve'])$(id).getContext('2d').clearRect(0,0,760,350);$('cameraImage').removeAttribute('src');$('cameraMetrics').textContent='本次有效读数已撤销';$('cameraLatency').textContent='NOT_MEASURED · 当前时钟/绘制读数已撤销';}
 function drawField(id,values,gray){const c=$(id).getContext('2d');c.clearRect(0,0,760,350);if(!values||!uv)return;uv.forEach(([u,v],i)=>{const x=380+1.5*v*5.8,y=175+Math.sqrt(3)*(u+v/2)*5.8;if(gray){let g=Math.round(values[i]*255);c.fillStyle=`rgb(${g},${g},${g})`;c.beginPath();for(let n=0;n<6;n++){const a=n*Math.PI/3;n?c.lineTo(x+5.5*Math.cos(a),y+5.5*Math.sin(a)):c.moveTo(x+5.5*Math.cos(a),y+5.5*Math.sin(a));}c.closePath();c.fill();}else{const dx=values[0][i]*8,dy=-values[1][i]*8;c.strokeStyle='#72d5f8';c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);c.stroke();}});}
 function drawCurve(rows){const c=$('cameraCurve').getContext('2d');c.clearRect(0,0,760,300);if(!rows.length)return;const values=rows.flatMap(r=>r.activity);let lo=Math.min(...values),hi=Math.max(...values);if(hi===lo)hi=lo+1;const t0=rows[0].activity_time_s,t1=rows.at(-1).activity_time_s;c.font='14px sans-serif';c.fillStyle='#bdd';c.fillText(`T4a–d / T5a–d · Euler后 ${t0.toFixed(3)}–${t1.toFixed(3)} s · 实际显示采样`,15,20);for(let i=0;i<8;i++){c.strokeStyle=colors[i];c.beginPath();rows.forEach((r,k)=>{const x=30+(r.activity_time_s-t0)/Math.max(.005,t1-t0)*700,y=270-(r.activity[i]-lo)/(hi-lo)*225;k?c.lineTo(x,y):c.moveTo(x,y);});c.stroke();}}
 function validate(p){if(p.commit_semantics&&(p.commit_semantics!=='FSYNC_CONFIRMED_PUBLIC_WATERMARK'||p.durable_commit_steps!==p.state_token))throw new Error('STREAM_UNSAVED_STATE_REJECTED');const clock=run?.binding?.clock,sourceTime=p.source.relative_s*(clock?.model_seconds_per_wall_second??1);if(clock&&(p.clock?.target_steps_per_s!==clock.target_steps_per_s||p.source.model_relative_s!==sourceTime||p.clock.model_dt_s!==.005))throw Error('CAMERA_CLOCK_IDENTITY_REJECTED');if(!run||p.run_id!==run.run_id||p.session_id!==run.session_id||p.execution_kind!==(sourceKind==='digital_direct'?'LIVE_DIGITAL_GPU':'LIVE_CAMERA_GPU')||p.evidence_level!=='ACTUAL_CONTINUOUS_FULL_GPU_STATE'||p.device.type!=='cuda'||p.PL_execution!==false||p.state_token!==p.step_id+1||sourceTime>p.input_time_s||p.activity_time_s!==p.input_time_s+.005||p.spatial.run_id!==p.run_id||p.spatial.step_id!==p.step_id)throw new Error('CAMERA_OUTPUT_IDENTITY_REJECTED');}
 async function calibrate(){let best=null;for(let n=0;n<3;n++){const a=performance.now(),v=await request('/api/stream/clock'),b=performance.now();if(v.clock!=='Windows_perf_counter_ns')throw new Error('CLOCK_DOMAIN');const q={at:b,uncertainty:(b-a)/2,offset:v.server_monotonic_ns/1e6-(a+b)/2};if(!best||q.uncertainty<best.uncertainty)best=q;}if(best.uncertainty>50)throw new Error('CLOCK_RTT_TOO_HIGH');clock=best;}
 let receivedSerial=-1;
 let summaryPending=null;
 async function collectSummary(){
  if(summaryPending)return summaryPending;
  summaryPending=(async()=>{for(let i=0;i<80;i++){
   const result=await request('/api/stream/summary');$('cameraManualSummary').textContent=FlyVisDisplayDiagnostics.formatSummary(result);
   if(result.status!=='WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION'){$('cameraStatus').textContent=result.status==='COMPLETED'?'本次运行已结束 · 已保存测试记录':'本次运行失败 · '+result.reason;return;}
   await new Promise(resolve=>setTimeout(resolve,250));
  }$('cameraManualSummary').textContent+='\n仍在等待后台确认，请保留窗口/日志，不要重复开始。';})().catch(e=>{$('cameraManualSummary').textContent='测试记录读取失败：'+e.message+'。请保留本次日志。';});
  return summaryPending;
 }
 async function fail(e){
  if(!running)return;running=false;++generation;clear();let reason=e.message;
  // Reject late images as before. Only an exact same-run normal terminal status
  // can classify a cancellation as completion; fetch/data/identity errors remain failures.
  if(['STREAM_RESULT_REVOKED','RAW_REVOKED_DURING_RENDER','DRAW_RESULT_REVOKED','STREAM_STOP_REQUESTED'].includes(reason)){
   try{const response=await request(`/api/stream/latest?wire=f32&after=${receivedSerial}`),s=response.status;
    reason=FlyVisDisplayDiagnostics.terminalReason(reason,s,run);
   }catch(_){}
  }
  consumer?.ended?.(reason);$('cameraStatus').textContent=reason==='STREAM_OBSERVATION_COMPLETE'?'观察时间结束 · 正在保存与停止':`NOT_AVAILABLE · ${reason}`;
  $('cameraStop').disabled=false;const failure=reason==='STREAM_OBSERVATION_COMPLETE'?{}:{run_id:run.run_id,error:reason.slice(0,1000)};
  request('/api/stream/stop',failure).catch(()=>{}).finally(collectSummary);
 }
 async function prepareConsumer(item){
  consumerPending=item;if(preparingFrame)return;preparingFrame=true;
  try{while(consumerPending){
    const wait=Math.max(0,nextPreparedAt-performance.now());if(wait)await new Promise(r=>setTimeout(r,wait));
    const next=consumerPending;consumerPending=null;
    const current=()=>running&&next.token===generation;if(!current())break;
    nextPreparedAt=performance.now()+Math.max(0,consumer.minIntervalMs||0);
    const drawing=await consumer.prepare(next,current);if(current())displaySlot.offer({...next,drawing});
  }}catch(e){if(running&&item.token===generation)fail(e);}
  finally{preparingFrame=false;}
 }

 const displaySlot=new FlyVisStreamWire.LatestFrame(callback=>{const queued=performance.now();requestAnimationFrame(()=>callback(queued));},item=>{
  const {p,response,image,token,readyAt}=item;if(!running||token!==generation||receiptPending)return;
  if(consumer){
   receiptPending=(async()=>{
    const current=()=>running&&token===generation;
    const drawing=item.drawing;if(!drawing||!current())return;
    validate(p);const tick=performance.now(),extra=drawing.paint();if(!current())return;
    const at=performance.now();painted++;if(!firstPaint)firstPaint=at;
    const fps=(painted-1)/Math.max(.001,(at-firstPaint)/1000);
    const receipt=await request('/api/stream/draw',{run_id:p.run_id,serial:p.serial,step_id:p.step_id,
     draw_server_monotonic_ns:(at+clock.offset)*1e6,clock_uncertainty_ms:clock.uncertainty,
     clock_age_s:(at-clock.at)/1000,render_ms:at-tick,raf_wait_ms:tick-drawing.readyAt,
     packet_slot_age_ms:tick-readyAt,document_visible:!document.hidden,
     ...FlyVisDisplayDiagnostics.environment(document,navigator,window),...extra});
    if(current())consumer.drawn?.({p,fps,receipt,response,clock,painted});
   })().catch(e=>{if(running&&token===generation)fail(e);}).finally(()=>{receiptPending=null;});return;
  }
  try{
   validate(p);const tick=performance.now();$('cameraImage').src=image.src;drawField('cameraHex',p.input_hex,true);drawField('cameraFlow',p.flow,false);drawCurve(p.recent_activity);spatial.accept(p.spatial);
   const draw={at:performance.now(),render_ms:performance.now()-tick,raf_wait_ms:tick-item.queuedAt,packet_slot_age_ms:tick-readyAt};
    lastSerial=p.serial;if(!firstPaint)firstPaint=performance.now();painted++;const fps=(painted-1)/Math.max(.001,(performance.now()-firstPaint)/1000),capture=response.status.capture,compute=response.status.compute;
    const displayEnvironment=FlyVisDisplayDiagnostics.environment(document,navigator,window);$('cameraDisplayDiagnostics').textContent=FlyVisDisplayDiagnostics.formatDraw(draw,fps,displayEnvironment.display_host);
    receiptPending=request('/api/stream/draw',{run_id:p.run_id,serial:p.serial,step_id:p.step_id,draw_server_monotonic_ns:(draw.at+clock.offset)*1e6,clock_uncertainty_ms:clock.uncertainty,clock_age_s:(draw.at-clock.at)/1000,render_ms:draw.render_ms,raf_wait_ms:draw.raf_wait_ms,packet_slot_age_ms:draw.packet_slot_age_ms,document_visible:!document.hidden,...displayEnvironment,client_requests:structuredClone(requestMetrics)}).then(receipt=>{if(!running||token!==generation)return;const latency=receipt.summary.receipt_to_render_upper_bound;$('cameraLatency').textContent=`接收→rAF绘制延迟保守上界 p50/p95/p99：${latency.p50_ms.toFixed(1)} / ${latency.p95_ms.toFixed(1)} / ${latency.p99_ms.toFixed(1)} ms · 时钟不确定度 ±${clock.uncertainty.toFixed(1)} ms · 实时验收 NOT_RUN`;}).catch(e=>{if(running&&token===generation)fail(e);}).finally(()=>{receiptPending=null;});
    $('cameraMetrics').textContent=`采集 ${capture.measured_delivery_fps?.toFixed(1)||'—'} FPS · 可靠提交 ${compute.committed_steps} 步（计算 ${compute.computed_steps??compute.committed_steps} / 待保存 ${compute.journal_pending_steps??0}）· 当前画面 ${p.state_token} 步 / ${p.activity_time_s.toFixed(3)} s · 实际推进 ${compute.inference_steps_per_s?.toFixed(1)||'—'} 步/s · 显示 ${fps.toFixed(1)} FPS · 模型积压 ${(p.model_lag_s*1000).toFixed(1)} ms · 源帧 ${p.source.sequence} · 源/转换队列 ${compute.source_queue_length}/${compute.input_queue_length} · 转换前丢弃 ${capture.source_frames_dropped_before_render||0} · 显示槽覆盖 ${Math.max(0,p.serial-painted)} · Decoder ${p.decoder_status}`;
    if(performance.now()-lastIdentityAt>1000){lastIdentityAt=performance.now();$('cameraIdentity').textContent=JSON.stringify({run_id:p.run_id,session_id:p.session_id,model:p.binding.model,spatial_map:p.spatial.map_sha256,initialization:p.binding.initialization,device:p.device,source_sequence:p.source.sequence,received_monotonic_ns:p.source.received_monotonic_ns,input_time_s:p.input_time_s,activity_time_s:p.activity_time_s,source_sha256:p.source.sha256,hex_sha256:p.source.hex_values_sha256,capture_read_s:p.source.capture_read_s,renderer_s:p.source.render_elapsed_s,timing:p.timing,client_requests:requestMetrics,identity_summary_refresh_s:1,PL_execution:false,REALTIME_STREAM_PASS:'NOT_RUN'},null,2);}
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
   const queuedAt=displaySlot.pending?.queuedAt??now,item={p,response,image,token,readyAt:now,queuedAt};
   if(consumer)prepareConsumer(item);else displaySlot.offer(item);
  }
  await new Promise(resolve=>setTimeout(resolve,streamReady?40:150));
 }}catch(e){if(running&&token===generation)fail(e);}}
 function parameters(){return {polarity:$('streamPolarity').value,direction_deg:Number($('streamDirection').value),speed_px_s:Number($('streamSpeed').value)};}
 async function prepareRenderer(){const info=await request('/api/flow');const frame=$('digitalRenderer');if(!frame.contentWindow?.render){await new Promise((resolve,reject)=>{frame.onload=resolve;frame.onerror=()=>reject(new Error('ORIGINAL_RENDERER_LOAD'));frame.src=info.presentation.url;});}if(typeof frame.contentWindow.render!=='function')throw new Error('ORIGINAL_RENDERER_UNAVAILABLE');}
 async function digitalInput(token){try{while(running&&token===generation){if(!streamReady){await new Promise(r=>setTimeout(r,100));continue;}const spec=parameters(),key=JSON.stringify(spec),now=performance.now();if(key!==lastParameters){segment++;segmentStart=now;lastParameters=key;}const elapsed=(now-segmentStart)/1000,renderer=$('digitalRenderer').contentWindow;renderer.render({...spec,family:'edge',pre_s:0,active_s:2,post_s:0},elapsed%2);const canvas=renderer.document.getElementById('stimulus');await request('/api/stream/input',{run_id:run.run_id,sequence:inputSequence,png:canvas.toDataURL('image/png').split(',')[1],parameters:spec,segment_id:segment,render_elapsed_s:elapsed});inputSequence++;await new Promise(r=>setTimeout(r,Math.max(0,33-(performance.now()-now))));}}catch(e){if(running)fail(e);}}
 async function startStream(options={}){
  if(running||starting)throw Error('STREAM_ALREADY_ACTIVE');starting=true;consumer=options.consumer||null;
  try{clear();if(options.source_kind)$('streamSource').value=options.source_kind;
   if(options.camera_id!==undefined)$('cameraId').value=String(options.camera_id);
   if(options.parameters){$('streamPolarity').value=options.parameters.polarity;$('streamDirection').value=String(options.parameters.direction_deg);$('streamSpeed').value=String(options.parameters.speed_px_s);}
   sourceKind=$('streamSource').value;const meta=await request('/api/live/inputs/ON60');uv=meta.coordinates;
   spatial.setMetadata(await request('/api/live/spatial-map'));if(sourceKind==='digital_direct')await prepareRenderer();await calibrate();
   run=await request('/api/stream/start',sourceKind==='digital_direct'?{source_kind:sourceKind,parameters:parameters()}:{source_kind:sourceKind,camera_id:Number($('cameraId').value),target_steps_per_s:options.target_steps_per_s??100});
   running=true;summaryPending=null;receivedSerial=-1;painted=0;lastSerial=-1;firstPaint=0;streamReady=false;lastImage=null;lastImageSHA=null;
   $('cameraManualSummary').textContent='本次新计算进行中，最终保存结果尚未确认。';inputSequence=0;lastParameters=null;start=performance.now();
   $('cameraStart').disabled=true;$('cameraId').disabled=true;$('streamSource').disabled=true;$('cameraStop').disabled=false;
   const token=++generation;poll(token);if(sourceKind==='digital_direct')digitalInput(token);return {run,coordinates:uv};
  }finally{starting=false;}
 }
 async function stopStream(){running=false;++generation;clear();consumer?.ended?.('USER_STOP');
  try{let status=await request('/api/stream/stop',{});for(let i=0;i<40&&!status.stop_acknowledged;i++){await new Promise(r=>setTimeout(r,250));status=await request('/api/stream/stop',{});}
   $('cameraStatus').textContent=status.stop_acknowledged?'已停止 · CUDA在途工作完成，读数已撤销':'停止请求已发出 · 等待CUDA确认';
  }catch(e){$('cameraStatus').textContent=e.message;}$('cameraStop').disabled=true;await collectSummary();
 }
 $('cameraStart').addEventListener('click',()=>startStream().catch(e=>{$('cameraStatus').textContent=`NOT_CONNECTED · ${e.message}`;}));
 $('cameraStop').addEventListener('click',stopStream);
 window.FlyVisContinuous={start:startStream,stop:stopStream,request,active:()=>running||starting};
 window.addEventListener('beforeunload',()=>{if(running)fetch('/api/stream/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}',keepalive:true}).catch(()=>{});});
 async function manualReadiness(){
  if(location.hash!=='#liveCamera')return;
  $('cameraStart').disabled=true;
  for(let n=0;n<60;n++){
   try{const info=await request('/api/live'),service=FlyVisServiceStatus(info);if(service.ready){$('cameraStatus').textContent=service.message+(info.camera_capture_enabled?'':'（本次未启用摄像头）');$('streamSource').querySelector('option[value=real_windows_camera]').disabled=!info.camera_capture_enabled;$('cameraId').disabled=!info.camera_capture_enabled;$('cameraStart').disabled=false;return;}
    $('cameraStatus').textContent=service.message;if(service.terminal)return;
   }catch(e){$('cameraStatus').textContent='正在等待本次后台 · '+e.message;}
   await new Promise(resolve=>setTimeout(resolve,2000));
  }
  $('cameraStatus').textContent='GPU 准备超时，请保留日志并重新打开实时入口。';$('cameraStart').disabled=true;
 }
 manualReadiness();
})();
