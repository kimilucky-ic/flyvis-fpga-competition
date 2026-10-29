/* Camera joint consumer of the ORIGINAL competition stage. No inference/PL code. */
(() => {
 'use strict';
 const fail=(ok,message)=>{if(!ok)throw Error(message);};
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 async function json(path,body){const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const v=await r.json();if(!r.ok)throw Error(v.error||'JOINT_HTTP_'+r.status);return v;}
 async function validate(p,identity,map){
  fail(p.schema==='flyvis-camera-joint-output/v1'&&p.execution_kind==='LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT'&&p.actual_new_computation===true,'JOINT_NOT_NEW_CAMERA');
  fail(p.run_id===identity.run_id&&p.session_id===identity.session_id&&p.source.run_id===p.run_id&&p.source_kind==='real_windows_camera'&&p.source.source_kind===p.source_kind,'JOINT_RUN_IDENTITY');
  fail(Number.isSafeInteger(p.step_id)&&p.step_id>=0&&p.serial===p.state_token&&p.state_token===p.step_id+1,'JOINT_STEP');
  fail(p.input_time_s===p.step_id*.005&&p.activity_time_s===p.input_time_s+.005&&p.temporal_mapping.policy==='LATEST_CONVERTED_AT_STEP_START_COMMIT_DRIVEN','JOINT_MODEL_TIME');
  const h=p.hardware,t=p.transaction,d=p.durable,s=p.spatial;
  fail(['ASID','server_session','boot_id','bit_sha256','hwh_sha256'].every(k=>h[k]===identity.hardware[k])&&t.ASID===h.ASID,'JOINT_HARDWARE_IDENTITY');
  fail(JSON.stringify(p.model)===JSON.stringify(identity.model)&&p.mapping_sha256===identity.mapping_sha256,'JOINT_MODEL');
  fail(t.status==='ACK_MATCHED_AND_PUBLISHED'&&t.integer_error===0&&t.step_id===p.step_id&&t.core_cycles===57681&&t.adapter_cycles>=t.core_cycles,'JOINT_ACK');
  fail(d.barrier==='STEP_PUBLISHED'&&Number.isSafeInteger(d.sequence)&&d.sequence>=0&&Number.isSafeInteger(d.end_offset)&&d.end_offset>0&&/^[a-f0-9]{64}$/.test(d.batch_sha256),'JOINT_DURABILITY');
  fail(p.whole_run_acceptance==='PENDING'&&p.REALTIME_STREAM_PASS==='NOT_CLAIMED'&&p.evidence_level==='ACK_MATCHED_DURABLE_PENDING_PS_AUDIT'&&p.PL_proven_global_ids.length===0,'JOINT_FALSE_PASS');
  fail(s.run_id===p.run_id&&s.step_id===p.step_id&&s.state_token===p.state_token&&s.map_sha256===map,'JOINT_SPATIAL');
  for(const [a,n,expected] of [[p.input_hex,721,p.source.hex_values_sha256],[s.values,5768,s.values_sha256],[p.flow.flat(),1442,p.flow_sha256]]){
   fail(a.length===n&&a.every(Number.isFinite),'JOINT_ARRAY');fail(await sha(new Float32Array(a).buffer)===expected,'JOINT_ARRAY_SHA');
  }
  const png=Uint8Array.from(atob(p.preview_png),c=>c.charCodeAt(0));fail(await sha(png)===p.source.png_sha256,'JOINT_PREVIEW_SHA');
  return new Blob([png],{type:'image/png'});
 }
 window.FlyVisJointCameraProtocol={validate};
 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id),panel=document.createElement('div');panel.className='cp-player';panel.id='cpJointControls';
 panel.innerHTML='<span>摄像头 GPU–FPGA 联合</span><button id="cpJointStart" disabled>开始本次已准备的联合会话</button><button id="cpJointStop" disabled>停止本次联合</button><button id="cpJointRecord" disabled>录制当前界面</button><button id="cpJointOffline" disabled>返回离线演示</button><span id="cpJointState">NOT_CONNECTED · 等待新硬件会话</span>';
 $('cpLiveControls').after(panel);
 let active=false,attempted=false,entered=false,epoch=0,last=0,health,projection,session,clock,hidden=[],heading='',policy='',boundary='',recorder=null,chunks=[],savedStageCallbacks=null,analysis=[],recordingStream=null,recordingCompletion=null;
 const input=document.createElement('canvas'),flow=document.createElement('canvas'),raw=document.createElement('canvas'),thumb=document.createElement('canvas');
 for(const c of [input,flow,thumb]){c.width=400;c.height=340;}
 function blank(text){ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text(text,60,160,30,'#b4d8e0');ui.stage.canvas.dataset.displayKind='NOT_AVAILABLE';}
 async function startRecording(){
  fail(!recorder,'本轮录像只能启动一次');fail(window.MediaRecorder,'当前窗口不支持画面录制，摄像头尚未启动');
  chunks=[];const mime=MediaRecorder.isTypeSupported('video/webm;codecs=vp8')?'video/webm;codecs=vp8':'video/webm';
  const id=crypto.randomUUID();recordingStream=ui.stage.canvas.captureStream(15);recorder=new MediaRecorder(recordingStream,{mimeType:mime});
  let saved,saveFailed;recordingCompletion=new Promise((resolve,reject)=>{saved=resolve;saveFailed=reject;});recordingCompletion.catch(()=>{});
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
  recorder.onstop=async()=>{try{
   const b=new Blob(chunks,{type:'video/webm'});fail(b.size>0,'JOINT_RECORDING_EMPTY');
   const r=await fetch('/api/joint-camera/recording',{method:'POST',headers:{'Content-Type':'video/webm'},body:b}),v=await r.json();
   fail(r.ok,v.error||'JOINT_RECORDING_SAVE_FAILED');$('cpJointState').textContent='本次界面录像已保存 · '+v.path;
   $('cpJointRecord').textContent='录像已自动保存';saved(v);
  }catch(e){$('cpJointState').textContent='录像保存失败：'+e.message;saveFailed(e);}
   finally{recordingStream.getTracks().forEach(t=>t.stop());}};
  await new Promise((resolve,reject)=>{
   const paintFirst=()=>{blank('录像准备中 · 摄像头与神经计算尚未开始');recordingStream.getVideoTracks()[0].requestFrame?.();};
   // Canvas capture may not emit MediaRecorder.start until a frame arrives.
   // Feed only explicit pre-run blank frames while awaiting that event.
   const pulse=setInterval(paintFirst,100),clear=()=>{clearInterval(pulse);clearTimeout(timer);};
   const timer=setTimeout(()=>{clear();reject(Error('JOINT_RECORDING_START_TIMEOUT'));},6000);
   recorder.addEventListener('start',()=>{clear();resolve();},{once:true});
   recorder.addEventListener('error',e=>{clear();reject(Error(e.error?.message||'JOINT_RECORDING_START_FAILED'));},{once:true});
   recorder.start(1000);
   paintFirst();
  });
  fail(recorder.state==='recording','JOINT_RECORDING_NOT_STARTED');const started=performance.now();
  blank('录像已启动 · 等待本次摄像头与第0步真实提交');
  await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);
  recordingStream.getVideoTracks()[0].requestFrame?.();
  $('cpJointRecord').disabled=true;$('cpJointRecord').textContent='正在全程录像 · 结束后自动保存';
  return {schema:'flyvis-joint-recorder-ready/v1',recorder_id:id,mime_type:mime,width:1920,height:1080,capture_fps:15,browser_started_ms:started,prestart_frame_requested:true};
 }
 async function finishRecording(){if(recorder?.state==='recording'){
  // Give the last actual committed canvas a capture opportunity before stopping.
  recordingStream.getVideoTracks()[0].requestFrame?.();await new Promise(r=>setTimeout(r,120));
  if(recorder.state==='recording')recorder.stop();
 }return recordingCompletion;}
 async function syncClock(){const a=performance.now(),v=await json('/api/joint-camera/clock'),b=performance.now();clock={mid:(a+b)/2,server:v.server_monotonic_ns,uncertainty:(b-a)/2,at:b};}
 function field(canvas,values,uv,gray){const c=canvas.getContext('2d');c.fillStyle='#091523';c.fillRect(0,0,400,340);const scale=5.1;
  uv.forEach(([u,v],i)=>{const x=200+1.5*v*scale,y=155+Math.sqrt(3)*(u+v/2)*scale;
   if(gray){const g=Math.round(Math.max(0,Math.min(1,values[i]))*255);c.fillStyle=`rgb(${g},${g},${g})`;c.beginPath();for(let k=0;k<6;k++){const a=k*Math.PI/3;k?c.lineTo(x+scale*Math.cos(a),y+scale*Math.sin(a)):c.moveTo(x+scale*Math.cos(a),y+scale*Math.sin(a));}c.closePath();c.fill();}
   else{const dx=values[0][i]*8,dy=-values[1][i]*8,n=Math.hypot(dx,dy),a=Math.atan2(dy,dx),h=Math.min(5,n*.35);c.strokeStyle='#74e4d5';c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);c.lineTo(x+dx-h*Math.cos(a-.5),y+dy-h*Math.sin(a-.5));c.moveTo(x+dx,y+dy);c.lineTo(x+dx-h*Math.cos(a+.5),y+dy-h*Math.sin(a+.5));c.stroke();}});
 }
 function stopView(reason,normal=false){active=false;++epoch;$('cpJointStart').disabled=true;$('cpJointStop').disabled=true;$('cpJointOffline').disabled=!entered;
  $('cpJointState').textContent=normal?'已停止 · 等待双方证据终验':'本次显示撤销：'+reason;
  if(!entered)return;
  if(normal){ui.stage.c.fillStyle='#182c38';ui.stage.c.fillRect(990,8,900,60);ui.stage.text('已停止 · 本次最后实际画面／整轮待终验',1010,47,24,'#ffd59e');ui.stage.canvas.dataset.displayKind='STOPPED_PENDING_JOINT_AUDIT';}
  else blank('NOT_AVAILABLE · '+reason);
  root.dataset.jointState=normal?'STOPPED_PENDING_PS_AUDIT':'FAILED';
  finishRecording().catch(()=>{});
 }
 async function paint(p,status,my){
  const perfStart=performance.now(),perf={};
  const blob=await validate(p,status.identity,health.projection_cache.upstream_map_sha256);
  perf.validate_ms=performance.now()-perfStart;let phaseAt=performance.now();
  fail(JSON.stringify(p.PL_participating_global_ids)===JSON.stringify(health.joint_spatial_global_ids),'JOINT_PARTICIPATING_IDS');
  const id=crypto.randomUUID(),r=await projection.render(p,id);
  perf.skeleton_render_ms=performance.now()-phaseAt;phaseAt=performance.now();
  const image=await createImageBitmap(blob);perf.bitmap_ms=performance.now()-phaseAt;phaseAt=performance.now();
  if(!active||my!==epoch){image.close();return;}
  const uv=health.coordinates_uv;field(thumb,p.input_hex,uv,true);field(flow,p.flow,uv,false);
  const c=input.getContext('2d');c.fillStyle='#091523';c.fillRect(0,0,400,340);const scale=Math.min(390/image.width,300/image.height);c.drawImage(image,(400-image.width*scale)/2,(300-image.height*scale)/2,image.width*scale,image.height*scale);image.close();c.drawImage(thumb,260,215,140,119);
  raw.width=r.width;raw.height=r.height;raw.getContext('2d',{alpha:false}).putImageData(new ImageData(r.pixels,r.width,r.height),0,0);
  perf.prepare_ms=performance.now()-phaseAt;
  if(!clock||performance.now()-clock.at>3000)await syncClock();
  phaseAt=performance.now();
  await new Promise(requestAnimationFrame);if(!active||my!==epoch)return;
  perf.raf_wait_ms=performance.now()-phaseAt;phaseAt=performance.now();
  const meta={run_id:p.run_id,types:r.receipt.types,means:[r.receipt.means],coordinates_uv:uv,activity_time_s:[p.activity_time_s]};
  ui.stage.draw(0,raw,r.receipt,meta,{input,flow,flowValues:p.flow.flat()},12,{joint:p.transaction,sourceKind:p.source_kind,step:p.step_id,stateToken:p.state_token,sourceSequence:p.source.sequence,clock:{mode:'COMMIT_DRIVEN_CAMERA_JOINT'},wallElapsed:p.wall_elapsed_s});
  const drawn=performance.now();perf.canvas_draw_ms=drawn-phaseAt;last=p.serial;
  root.dataset.run=p.run_id;root.dataset.frame=String(p.step_id);root.dataset.jointState='RUNNING_PENDING_AUDIT';
  $('cpClock').textContent=`采集 ${p.source.relative_s.toFixed(3)}s · 模型 ${p.activity_time_s.toFixed(3)}s · 实际联合 ${p.wall_elapsed_s.toFixed(2)}s`;
  $('cpStatus').textContent=`当次摄像头 → GPU chemical/R → 实体PL 5768 → COMMIT/ACK → 官方光流 · 步 ${p.step_id} · 整轮待终验`;
  $('cpIdentity').textContent=JSON.stringify({run_id:p.run_id,session_id:p.session_id,model:p.model,hardware:p.hardware,source:p.source,transaction:p.transaction,durable:p.durable,numerical_profile:p.numerical_profile,temporal_mapping:p.temporal_mapping,whole_run_acceptance:'PENDING'},null,2);
  const receipt=await json('/api/joint-camera/draw',{run_id:p.run_id,session_id:p.session_id,serial:p.serial,step_id:p.step_id,state_token:p.state_token,
   unified_commit_sha256:p.transaction.unified_commit_sha256,source_png_sha256:p.source.png_sha256,spatial_values_sha256:p.spatial.values_sha256,flow_sha256:p.flow_sha256,
   skeleton_raw_sha256:r.receipt.raw_sha256,projection_cache_sha256:r.receipt.projection_cache_sha256,browser_draw_ms:drawn,
   draw_server_monotonic_ns:Math.round(clock.server+(drawn-clock.mid)*1e6),clock_uncertainty_ms:clock.uncertainty,clock_age_s:(drawn-clock.at)/1000,browser_stage_timings:perf});
  $('cpJointState').textContent=`已提交 ${p.state_token}步 · PL ${p.transaction.core_cycles}拍 · 显示延迟上界 ${receipt.latency.upper_ms.toFixed(1)}ms · 待终验`;
 }
 async function loop(my){try{while(active&&my===epoch){const v=await json('/api/joint-camera/latest');
   if(v.status.error)throw Error(v.status.error);
   if(v.status.stop_acknowledged){if(v.packet&&v.packet.serial>last)await paint(v.packet,v.status,my);stopView('STOPPED',true);return;}
   const progress=v.status.progress,phaseNames={GPU_CHEMICAL_R:'GPU计算本次chemical/R',STEP_EXCHANGE_WAIT_CANDIDATE:'STEP交换／等待实体PL候选',VERIFYING_PL_AND_R_CANDIDATES:'核验H/R候选',COMMIT_EXCHANGE_WAIT_ACK:'统一COMMIT／等待ACK',ACK_MATCHED_DECODING_COMMITTED_STATE:'ACK已匹配／官方光流解码',STEP_PUBLISHED_DURABLE:'本步已提交并持久化'};
   if(progress)$('cpJointState').textContent=`第 ${progress.step_id} 步 · ${phaseNames[progress.phase]||progress.phase} · 主机里程碑，非PL忙寄存器读数`;
   if(v.packet&&v.packet.serial>last)await paint(v.packet,v.status,my);
   await new Promise(r=>setTimeout(r,100));
  }}catch(e){if(active&&my===epoch){stopView(e.message);json('/api/joint-camera/stop',{error:e.message}).catch(()=>{});}}}
 async function readiness(){if(active||attempted)return;try{const s=await json('/api/joint-camera/status');session=s;
   $('cpJointStart').disabled=!s.ready_for_camera;$('cpJointState').textContent=s.error||s.status||'NOT_CONNECTED';
  }catch(e){$('cpJointState').textContent='NOT_CONNECTED · '+e.message;}if(!attempted)setTimeout(readiness,2000);}
 $('cpJointStart').onclick=async()=>{if(active||attempted)return;
  try{fail(!window.FlyVisContinuous?.active(),'请先停止Full GPU会话');attempted=true;$('cpJointStart').disabled=true;
   session=await json('/api/joint-camera/status');fail(session.ready_for_camera,'联合计算与官方转换尚未就绪');
   ui.enterLive();entered=true;active=true;last=0;++epoch;savedStageCallbacks={onPlay:ui.stage.onPlay,onSeek:ui.stage.onSeek};ui.stage.onPlay=ui.stage.onSeek=()=>{};
   hidden=Array.from(document.querySelectorAll('.cp-player')).filter(e=>e!==panel).map(e=>[e,e.hidden]);hidden.forEach(([e])=>e.hidden=true);
   analysis=['cpAnalysis','cpSpatialDetails'].map(id=>[$(id),$(id).hidden]);analysis.forEach(([e])=>e.hidden=true);
   heading=document.querySelector('.cp-heading').textContent;policy=$('cpPolicyNotice').textContent;boundary=document.querySelector('.cp-boundary').textContent;
   document.querySelector('.cp-heading').textContent='当次摄像头 → GPU / 实体FPGA → 当前神经活动与光流';$('cpPolicyNotice').textContent='按COMMIT实际推进；采集与模型时间分别记录。运行中不宣称整轮PASS。';
   document.querySelector('.cp-boundary').textContent='固定CPU骨架 · 同类721节点均值 · 原Q24/FP32混合配置 · 本步ACK后已持久化／整轮待终验';
   blank('正在准备同一页面的固定CPU骨架；尚未开启摄像头…');health=await json('/api/joint-camera/prepare',{});projection=await FlyVisFixedSkeleton.load(health);
   const recording_ready=await startRecording();
   await json('/api/joint-camera/start',{run_id:session.run_id,session_id:session.session_id,recording_ready});
   $('cpJointStop').disabled=false;loop(epoch);
  }catch(e){stopView(e.message);json('/api/joint-camera/stop',{error:e.message}).catch(()=>{});}};
 $('cpJointStop').onclick=async()=>{try{$('cpJointStop').disabled=true;$('cpJointState').textContent='停止新采集，等待在途COMMIT/ACK及正常窗口结束…';await json('/api/joint-camera/stop',{});}catch(e){stopView(e.message);}};
 $('cpJointOffline').onclick=async()=>{if(active)await json('/api/joint-camera/stop',{});active=false;++epoch;
  await finishRecording();
  hidden.forEach(([e,v])=>e.hidden=v);document.querySelector('.cp-heading').textContent=heading;$('cpPolicyNotice').textContent=policy;document.querySelector('.cp-boundary').textContent=boundary;
  analysis.forEach(([e,v])=>e.hidden=v);
  if(savedStageCallbacks)Object.assign(ui.stage,savedStageCallbacks);await ui.leaveLive();entered=false;$('cpJointOffline').disabled=true;};
 $('cpJointRecord').disabled=true;$('cpJointRecord').textContent='启动联合会话前自动录像';
 window.addEventListener('beforeunload',()=>{if(active)fetch('/api/joint-camera/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}',keepalive:true}).catch(()=>{});});
 readiness();
})();
