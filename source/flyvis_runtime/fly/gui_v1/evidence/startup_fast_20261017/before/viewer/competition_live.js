/* Same homepage, original continuous controller, line 10's original geometry. */
(() => {
 'use strict';
 const $=id=>document.getElementById(id),root=$('competitionWorkspace'),ui=window.FlyVisCompetitionUI;
 const controls=document.createElement('div');controls.className='cp-player';controls.id='cpLiveControls';
 controls.innerHTML='<label>视觉来源 <select id="cpLiveSource"><option value="digital_direct">数字运动刺激</option><option value="real_windows_camera">真实摄像头</option></select></label><label id="cpLiveCameraLabel" hidden>摄像头编号 <input id="cpLiveCameraId" type="number" min="0" max="15" step="1" value="0" style="width:55px"></label><button id="cpLiveStart">启动本次 GPU 数字实验</button><label>明暗 <select id="cpLivePolarity"><option>ON</option><option>OFF</option></select></label><label>方向 <select id="cpLiveDirection"></select></label><label>速度 <input id="cpLiveSpeed" type="number" min="1" max="640" value="160" style="width:70px"> px/s</label><label>骨架绘图 <select id="cpLiveRenderer"><option value="gpu">GPU · 原始像素（需无其它计算任务）</option><option value="cpu" selected>CPU · 缓存骨架，只更新亮度（默认）</option></select></label><button id="cpLiveStop" disabled>停止本次计算</button><button id="cpLiveOffline" disabled>返回原离线演示</button>';
 for(let a=0;a<360;a+=30)controls.querySelector('#cpLiveDirection').append(new Option(a+'°',a));
 controls.querySelector('#cpLiveDirection').value='60';
 const rateLabel=document.createElement('label');rateLabel.id='cpLiveRateLabel';rateLabel.hidden=true;
 rateLabel.innerHTML='模型推进 <select id="cpLiveRate"><option value="100">100步/秒 · 半速（默认）</option><option value="50">50步/秒 · 四分之一速</option><option value="200">200步/秒 · 原速</option></select>';controls.querySelector('#cpLiveStart').before(rateLabel);
 const liveTools=document.createElement('details');liveTools.id='cpLiveTools';liveTools.className='cp-more';liveTools.open=location.hash==='#liveSkeleton';
 const summary=document.createElement('summary');summary.textContent='新计算 · GPU实时数据驱动骨架亮度';liveTools.append(summary,controls);document.querySelector('.cp-heading').after(liveTools);
 const note=document.createElement('p');note.className='cp-policy-notice';note.id='cpLiveStatus';note.textContent='新计算使用原 Full GPU 与官方光流。固定八类骨架，只更新亮度；原离线演示照常保留。';liveTools.append(note);
 const stats=document.createElement('p');stats.id='cpLiveStats';stats.className='cp-status';liveTools.append(stats);
 const serviceNote=document.createElement('p');serviceNote.id='cpLiveService';serviceNote.className='cp-policy-notice';serviceNote.setAttribute('role','status');liveTools.prepend(serviceNote);liveTools.prepend(summary);
 const rawCanvas=document.createElement('canvas'),inputCanvas=document.createElement('canvas'),flowCanvas=document.createElement('canvas'),thumbnail=document.createElement('canvas');
 thumbnail.width=400;thumbnail.height=340;
 inputCanvas.width=flowCanvas.width=400;inputCanvas.height=flowCanvas.height=340;
 let health=null,projection=null,coordinates=null,active=false,ended=false,streamStarted=false,parameters=null,lastDraw=null,epoch=0,savedControls=[],sourceKind='digital_direct';
 let headingHTML='',policyText='',workspaceText='',analysisHidden=false,boundaryHTML='',spatialHidden=false;
 const json=FlyVisContinuous.request;
 $('cpLiveStart').disabled=true;
 async function readiness(){
  const deadline=performance.now()+180000;
  while(!active&&!ended){
   try{const info=await json('/api/live');if(active||ended)return;const service=FlyVisServiceStatus(info);
    serviceNote.textContent=service.message;root.dataset.serviceState=service.state;$('cpLiveStart').disabled=!service.ready||!info.stream_enabled;
    if(service.terminal)return;
    if(!service.ready&&performance.now()>deadline){serviceNote.textContent='GPU 准备超时；请查看本次日志并重新打开实时入口。';return;}
   }catch(e){if(active||ended)return;serviceNote.textContent='后台状态读取失败：'+e.message;$('cpLiveStart').disabled=true;return;}
   await new Promise(resolve=>setTimeout(resolve,2000));
  }
 }
 readiness();
 $('cpLiveSource').onchange=()=>{const camera=$('cpLiveSource').value==='real_windows_camera';$('cpLiveCameraLabel').hidden=!camera;
  $('cpLiveRateLabel').hidden=!camera;
  for(const id of ['cpLivePolarity','cpLiveDirection','cpLiveSpeed'])$(id).closest('label').hidden=camera;
  $('cpLiveStart').textContent=camera?'启动摄像头与 GPU 实验':'启动本次 GPU 数字实验';
  note.textContent=camera?'默认100步/秒；数学步长5ms不变，输入时间映射为半速模型演示，非原速科研实验。点击开始才采集，结束释放摄像头。':'数字输入使用原刺激渲染器与200步/秒原速；原离线演示保持。';};
 function field(canvas,values,gray){const c=canvas.getContext('2d');c.fillStyle='#091523';c.fillRect(0,0,400,340);
  const s=5.1;coordinates.forEach(([u,v],i)=>{const x=200+1.5*v*s,y=155+Math.sqrt(3)*(u+v/2)*s;
   if(gray){const g=Math.round(Math.max(0,Math.min(1,values[i]))*255);c.fillStyle=`rgb(${g},${g},${g})`;c.beginPath();for(let n=0;n<6;n++){const a=n*Math.PI/3;n?c.lineTo(x+s*Math.cos(a),y+s*Math.sin(a)):c.moveTo(x+s*Math.cos(a),y+s*Math.sin(a));}c.closePath();c.fill();}
   else{const dx=values[0][i]*8,dy=-values[1][i]*8,n=Math.hypot(dx,dy),angle=Math.atan2(dy,dx),head=Math.min(5,n*.35);c.strokeStyle='#74e4d5';c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);c.lineTo(x+dx-head*Math.cos(angle-.5),y+dy-head*Math.sin(angle-.5));c.moveTo(x+dx,y+dy);c.lineTo(x+dx-head*Math.cos(angle+.5),y+dy-head*Math.sin(angle+.5));c.stroke();}});
 }
 function blank(text){const c=ui.stage.c;c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);ui.stage.text(text,70,160,35,'#b4d8e0');ui.stage.canvas.dataset.displayKind='NOT_AVAILABLE';}
 function exitState(reason){if(ended)return;ended=true;active=false;++epoch;
  const normal=['STREAM_OBSERVATION_COMPLETE','USER_STOP'].includes(reason);
  serviceNote.textContent=normal?'本次输入与计算已停止。':'本次运行失败并已停止；请保留本次错误记录。';
  note.textContent=(normal?'本次计算已停止，正在等待证据保存确认。':'本次显示已撤销：'+reason+'。')+' 没有回退到旧神经活动。';
  root.dataset.liveState=normal?'STOPPING':'FAILED';$('workspaceStatus').textContent=normal?'本次计算已结束 · 等待保存确认':'NOT_AVAILABLE · 本次显示已撤销';
  $('cpStatus').textContent=normal?'已停止本次新计算 · 等待CUDA与持久化确认':'本次实时显示已撤销 · '+reason;
  if(normal&&lastDraw){const c=ui.stage.c;c.fillStyle='#182c38';c.fillRect(1040,8,860,60);ui.stage.text('已停止 · 下方保留本次计算的最后实际画面',1060,47,25,'#ffd59e');ui.stage.canvas.dataset.displayKind='STOPPED_LAST_ACTUAL_FRAME';}
  else blank('NOT_AVAILABLE · '+reason);
  $('cpLiveStop').disabled=true;$('cpLiveOffline').disabled=false;
  json('/api/competition-live/stop',{}).catch(()=>{});
  if(!streamStarted){
   serviceNote.textContent='显示端准备失败；尚未启动摄像头与神经计算。';
   note.textContent='未启动本次计算：'+reason+'。可返回原离线演示；错误已保留在本次日志。';
   root.dataset.liveSummary=JSON.stringify({status:'NOT_STARTED',reason});
   return;
  }
  (async()=>{for(let i=0;i<100;i++){const result=await json('/api/stream/summary');if(result.status!=='WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION'){
    const passed=normal&&result.status==='COMPLETED';
    note.textContent=passed?'本次计算与保存已完成。最后画面为本次真实结果；点击“返回原离线演示”可恢复历史播放器。':'本次显示未完成：'+(normal?(result.reason||result.status):reason)+'；计算记录已保留，不能称演示成功。';
    root.dataset.liveState=passed?'COMPLETED':'FAILED';root.dataset.liveSummary=JSON.stringify(result);$('workspaceStatus').textContent=passed?'本次 GPU 已完成 · 结果已保存':'本次运行未完成 · 证据保留';
    if(passed){serviceNote.textContent='本次 GPU 计算与保存已完成，摄像头已停止。';
     $('cpStatus').textContent=`本次已完成 · 实际 ${result.compute_wall_s.toFixed(2)} s / 模型 ${result.model_time_s.toFixed(3)} s · ${result.durable_steps} 步已可靠保存`;
     stats.textContent=`最终汇总：计算 ${result.computed_steps} 步 / 保存 ${result.durable_steps} 步 · ${result.steps_per_s.toFixed(2)} 步/s · 显示 ${result.display_FPS.toFixed(2)} FPS · 接收→绘制 p95 上界 ${result.receipt_to_draw_p95_upper_ms.toFixed(1)} ms`;}
    return;}
    await new Promise(r=>setTimeout(r,250));}})().catch(e=>{note.textContent+=' 保存状态读取失败：'+e.message;});
 }
 const consumer={ended:exitState,minIntervalMs:100,
  async prepare(item,current){const p=item.p,requestID=crypto.randomUUID(),t=performance.now();
   let raw,arrived=t,bytes=0;
   if(projection){raw=await projection.render(p,requestID);}
   else{
    const response=await fetch('/api/competition-live/frame',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id:p.run_id,session_id:p.session_id,serial:p.serial,step_id:p.step_id,state_token:p.state_token,request_id:requestID})}).catch(e=>{throw Error('骨架传输 /api/competition-live/frame: '+e.message);});
    if(!response.ok){const error=await response.json();throw Error(error.error||'RAW_HTTP');}
    const buffer=await response.arrayBuffer();bytes=buffer.byteLength;arrived=performance.now();raw=await FlyVisSkeletonWire.decode(buffer,p,requestID,health);
   }
   const checked=performance.now();
   if(!current())return {readyAt:checked,paint(){}};
   return {readyAt:checked,paint(){
    const begin=performance.now(),r=raw.receipt;if(rawCanvas.width!==raw.width)rawCanvas.width=raw.width;if(rawCanvas.height!==raw.height)rawCanvas.height=raw.height;
    rawCanvas.getContext('2d',{alpha:false}).putImageData(new ImageData(raw.pixels,raw.width,raw.height),0,0);
    const putDone=performance.now();field(inputCanvas,p.input_hex,true);thumbnail.getContext('2d').drawImage(inputCanvas,0,0);
    const ic=inputCanvas.getContext('2d');ic.fillStyle='#091523';ic.fillRect(0,0,400,340);
    const imageScale=Math.min(390/item.image.naturalWidth,300/item.image.naturalHeight),iw=item.image.naturalWidth*imageScale,ih=item.image.naturalHeight*imageScale;
    ic.drawImage(item.image,(400-iw)/2,(300-ih)/2,iw,ih);ic.fillStyle='#091523';ic.fillRect(265,210,135,130);ic.drawImage(thumbnail,260,215,140,119);
    field(flowCanvas,p.flow,false);
    const meta={run_id:p.run_id,types:r.types,means:[r.means],coordinates_uv:coordinates,activity_time_s:[p.activity_time_s]};
    ui.stage.draw(0,rawCanvas,r,meta,{input:inputCanvas,flow:flowCanvas,flowValues:[...p.flow[0],...p.flow[1]]},12,{parameters,sourceKind:p.source_kind,step:p.step_id,stateToken:p.state_token,sourceSequence:p.source.sequence,clock:p.clock,wallElapsed:p.wall_elapsed_s});
    if(root.dataset.liveState!=='RUNNING')serviceNote.textContent='已收到本次真实输入与 GPU 神经状态；正在同步显示。';
    lastDraw=r;root.dataset.run=p.run_id;root.dataset.frame=String(p.step_id);root.dataset.liveState='RUNNING';root.dataset.sync='verified';
    $('cpStatus').textContent=`本次实际 Full GPU · 实际运行 ${p.wall_elapsed_s.toFixed(2)} s · 模型输入 ${p.input_time_s.toFixed(3)} s → 活动/光流 ${p.activity_time_s.toFixed(3)} s · 源采集 ${p.source.relative_s.toFixed(3)} s · 同一COMMIT`;
    root.dataset.liveReceipt=JSON.stringify(r);$('cpClock').textContent=`实际 ${p.wall_elapsed_s.toFixed(2)} s / 模型 ${p.activity_time_s.toFixed(3)} s`;
    $('workspaceStatus').textContent=(sourceKind==='real_windows_camera'?'LIVE CAMERA GPU':'LIVE DIGITAL GPU')+' · 本次实际计算';
    $('cpIdentity').textContent=JSON.stringify({run_id:p.run_id,session_id:p.session_id,source_kind:p.source_kind,state_token:p.state_token,source:p.source,clock:p.clock,wall_elapsed_s:p.wall_elapsed_s,input_time_s:p.input_time_s,activity_time_s:p.activity_time_s,model:p.binding.model,spatial_sha:p.spatial.values_sha256,skeleton:r,FPGA_status:'NOT_CONNECTED'},null,2);
    return {skeleton_request_id:requestID,skeleton_raw_sha256:r.raw_sha256,skeleton_wire:projection?'FIXED_CPU_CACHE_V1':'RGBA8_NO_PNG',skeleton_bytes:bytes,
     ...(projection?{skeleton_cache_sha256:health.projection_cache.sha256,browser_cpu_compose_ms:raw.composeMs}:{}),
     skeleton_fetch_ms:arrived-t,skeleton_verify_ms:checked-arrived,skeleton_put_image_ms:putDone-begin,skeleton_draw_ms:performance.now()-putDone,
     skeleton_render_raw_ms:r.total_render_raw_ms,brightness_encoding:r.color_encoding.encoding_sha256,source_kind:p.source_kind,source_sequence:p.source.sequence,source_png_sha256:p.source.png_sha256,clock:p.clock,wall_elapsed_s:p.wall_elapsed_s,activity_time_s:p.activity_time_s};
   }};
  },
  drawn({p,fps,receipt,response,painted}){const q=receipt.summary.receipt_to_render_upper_bound,compute=response.status.compute;
   const capture=response.status.capture;
   stats.textContent=`${sourceKind==='real_windows_camera'?'摄像头采集':'输入接收'} ${capture.measured_delivery_fps?.toFixed(1)||'—'} FPS · 可靠提交 ${compute.committed_steps} 步 · 推进 ${compute.inference_steps_per_s?.toFixed(1)||'—'} 步/s · 实际显示 ${fps.toFixed(1)} FPS · 接收→绘制 p95 上界 ${q.p95_ms.toFixed(1)} ms · 待转换 ${compute.source_queue_length} 帧 · 输入历史 ${compute.input_queue_length} 帧（非积压） · 已显示 ${painted} 帧`;
   note.textContent=`${p.clock.target_steps_per_s}步/实际秒 · ${p.clock.mode==='SLOW_MODEL_DEMO'?'慢速模型演示，输入时间已映射，非原速科研':'原速时间尺度'} · 5ms数学步长不变 · 原始正负值保留 · FPGA 未连接`;
   root.dataset.liveFps=String(fps);root.dataset.liveLatency=String(q.p95_ms);root.dataset.livePainted=String(painted);
  }
 };
 $('cpLiveStart').onclick=async()=>{
  if(FlyVisContinuous.active())return;
  $('cpLiveStart').disabled=true;
  try{
   const capabilities=await json('/api/live');if(capabilities.status!=='CONNECTED'||!capabilities.stream_enabled)throw Error(FlyVisServiceStatus(capabilities).message);
   sourceKind=$('cpLiveSource').value;
   const cameraId=Number($('cpLiveCameraId').value);
   if(sourceKind==='real_windows_camera'){
    if(!capabilities.camera_capture_enabled)throw Error('本次入口未启用摄像头，请关闭后使用 start_live_skeleton.cmd 重新打开');
    if(!Number.isInteger(cameraId)||cameraId<0||cameraId>15)throw Error('摄像头编号须为0至15的整数');
   }
   ui.enterLive();active=true;ended=false;streamStarted=false;lastDraw=null;++epoch;serviceNote.textContent='GPU 已就绪，正在准备固定镜头；摄像头尚未启动。';headingHTML=document.querySelector('.cp-heading').innerHTML;policyText=$('cpPolicyNotice').textContent;workspaceText=$('workspaceStatus').textContent;
   savedControls=Array.from(document.querySelectorAll('.cp-player:not(#cpLiveControls) button,.cp-player:not(#cpLiveControls) input,.cp-player:not(#cpLiveControls) select')).filter(e=>e.id!=='cpCinema').map(e=>[e,e.disabled]);savedControls.forEach(([e])=>e.disabled=true);
   analysisHidden=$('cpAnalysis').hidden;$('cpAnalysis').hidden=true;
   spatialHidden=$('cpSpatialDetails').hidden;$('cpSpatialDetails').hidden=true;
   boundaryHTML=document.querySelector('.cp-boundary').innerHTML;document.querySelector('.cp-boundary').textContent='真实骨架 + 本次同类型721节点均值 · 固定对比度增强，不改变活动数值 · 原Full GPU / FPGA NOT_CONNECTED';
   parameters=sourceKind==='digital_direct'?{polarity:$('cpLivePolarity').value,direction_deg:Number($('cpLiveDirection').value),speed_px_s:Number($('cpLiveSpeed').value)}:null;
   document.querySelector('.cp-heading').textContent=(sourceKind==='real_windows_camera'?'本次摄像头画面':'本次数字输入')+' → 原 Full GPU → 5,768节点真实均值 → 八类骨架 / 官方光流';$('cpPolicyNotice').textContent='固定镜头，CPU缓存骨架；神经计算仍用GPU，先准备显示端。';
   $('cpStatus').textContent='正在准备本次固定镜头显示，尚未启动神经递推。';
   blank('正在准备骨架显示；尚未开始新的神经递推…');note.textContent='准备固定镜头与真实骨架，完成后启动本次所选输入。';
   health=await json('/api/competition-live/prepare',{renderer:$('cpLiveRenderer').value});
   projection=health.projection_cache?await FlyVisFixedSkeleton.load(health):null;
   consumer.minIntervalMs=health.projection_cache?0:($('cpLiveRenderer').value==='cpu'?250:100);
   coordinates=(await json('/api/live/inputs/ON60')).coordinates;
   note.textContent='骨架已就绪，正在准备官方输入转换；随后才打开摄像头。';root.dataset.liveState='WAITING_INPUT';
   await FlyVisContinuous.start({source_kind:sourceKind,parameters,camera_id:cameraId,target_steps_per_s:sourceKind==='real_windows_camera'?Number($('cpLiveRate').value):200,consumer});streamStarted=true;$('cpLiveStop').disabled=false;serviceNote.textContent='正在准备官方视觉转换并等待首帧；首帧到达后才开始神经递推。';
   for(const id of ['cpLiveSource','cpLiveCameraId','cpLiveRate','cpLivePolarity','cpLiveDirection','cpLiveSpeed','cpLiveRenderer'])$(id).disabled=true;
  }catch(e){note.textContent='未启动：'+e.message;if(active){exitState(e.message);if(FlyVisContinuous.active())await FlyVisContinuous.stop();}else $('cpLiveStart').disabled=true;}
 };
 $('cpLiveStop').onclick=()=>FlyVisContinuous.stop();
 $('cpLiveOffline').onclick=async()=>{
  if(FlyVisContinuous.active())await FlyVisContinuous.stop();
  document.querySelector('.cp-heading').innerHTML=headingHTML;$('cpPolicyNotice').textContent=policyText;$('workspaceStatus').textContent=workspaceText;
  savedControls.forEach(([e,disabled])=>e.disabled=disabled);$('cpAnalysis').hidden=analysisHidden;$('cpSpatialDetails').hidden=spatialHidden;document.querySelector('.cp-boundary').innerHTML=boundaryHTML;
  await ui.leaveLive();$('cpLiveOffline').disabled=true;note.textContent='已返回原离线实验；新GPU实验的原始记录保存在独立session目录。再次新算需要重新启动会话。';
 };
 window.addEventListener('beforeunload',()=>{if(active)fetch('/api/competition-live/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}',keepalive:true}).catch(()=>{});});
})();
