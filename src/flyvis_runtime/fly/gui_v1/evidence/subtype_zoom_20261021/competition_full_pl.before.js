/* Saved first-step + bounded continuous full-PL states in the ORIGINAL stage. */
(() => {
 'use strict';
 const fail=(ok,message)=>{if(!ok)throw Error(message);};
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 async function json(path,body){const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),p=await r.json();if(!r.ok)throw Error(p.error||'FULL_PL_HTTP_'+r.status);return p;}
 async function arrays(p,h){
  fail(p.spatial.map_sha256===h.projection_cache.upstream_map_sha256,'FULL_PL_MAP');
  for(const [values,n,expected] of [[p.input_hex,721,p.input_sha256],[p.spatial.values,5768,p.spatial.values_sha256]]){
   fail(values.length===n&&values.every(Number.isFinite),'FULL_PL_ARRAY');
   fail(await sha(new Float32Array(values).buffer)===expected,'FULL_PL_ARRAY_SHA');
  }
 }
 async function validate(p,s,h){
  fail(s.status==='VERIFIED_SAVED_FIRST_STEP'&&p.schema==='flyvis-full-pl-first-step-display/v1','FULL_PL_NOT_VERIFIED');
  fail(p.run_id===s.run_id&&p.hardware.boot_id===s.boot_id&&p.archive_sha256===s.archive_sha256,'FULL_PL_RUN_BINDING');
  fail(p.backend==='FULL_NETWORK_FPGA'&&p.display_kind==='OFFLINE_REPLAY_FULL_NETWORK_FPGA'&&p.board_connection==='NOT_CONNECTED','FULL_PL_DISPLAY_KIND');
  const offset=p.plan_metadata?.input_time_offset_s||0;
  fail(p.step_id===0&&p.state_token===1&&p.input_time_s===offset&&p.activity_time_s===offset+.005&&p.hardware.completed_steps===1&&p.hardware.faults===0,'FULL_PL_STEP');
  fail(p.flow===null&&p.flow_status==='NOT_AVAILABLE_NOT_DECODED','FULL_PL_NO_BORROWED_FLOW');
  await arrays(p,h);
 }
 async function validateStream(p,s,anchor,h){
  fail(s.first_step_accepted&&['RECEIVING','FINISHED'].includes(s.status)&&s.result_valid,'FULL_PL_STREAM_NOT_VALID');
  fail(p.schema==='flyvis-full-pl-stream-display/v1'&&p.backend==='FULL_NETWORK_FPGA'
   &&p.run_id===s.run_id&&p.run_id===anchor.run_id&&p.session_id===s.session_id&&p.hardware.boot_id===s.boot_id,'FULL_PL_STREAM_IDENTITY');
  fail(p.anchor_archive_sha256===anchor.archive_sha256&&['bit_sha256','hwh_sha256','boot_id','clock_hz'].every(k=>p.hardware[k]===anchor.hardware[k]),'FULL_PL_STREAM_ANCHOR');
  const offset=anchor.plan_metadata?.input_time_offset_s||0;
  fail(p.plan_metadata?.input_time_offset_s===anchor.plan_metadata?.input_time_offset_s,'FULL_PL_PLAN_TIME');
  fail(Number.isSafeInteger(p.step_id)&&p.step_id>=(anchor.plan_metadata?.steps===485||anchor.plan_metadata?.camera_live?0:1)&&p.state_token===p.step_id+1&&p.serial===p.state_token
   &&p.hardware.completed_steps===p.state_token&&p.hardware.faults===0&&p.input_time_s===p.step_id*.005+offset
   &&p.activity_time_s===(p.step_id+1)*.005+offset,'FULL_PL_STREAM_STEP');
  fail(p.offline_replay?(s.status==='FINISHED'&&s.display_complete&&p.display_kind==='OFFLINE_REPLAY_FULL_PL_TRAJECTORY'):
   p.display_kind===(s.status==='RECEIVING'?'CURRENT_FULL_PL_STATE_PENDING_AUDIT':'FINISHED_FULL_PL_LAST_STATE'),'FULL_PL_STREAM_LABEL');
  await arrays(p,h);
  if(anchor.plan_metadata?.camera_live){fail(p.source.kind===(anchor.plan_metadata?.input_kind==='controlled_animation'?'controlled_animation':'real_windows_camera')&&p.source.run_id===p.run_id
   &&p.source.hex_values_sha256===p.input_sha256&&p.source.png_sha256===p.source.pixel_png_sha256
   &&Number.isFinite(p.wall_elapsed_s)&&Number.isFinite(p.capture_elapsed_s),'FULL_PL_LIVE_CAMERA_SOURCE_IDENTITY');}
  if(p.flow===null){fail(p.flow_status==='NOT_AVAILABLE_NOT_DECODED','FULL_PL_FLOW_MISSING');return;}
  const b=p.flow_binding;
  fail(p.flow_status==='OFFICIAL_DECODER_SAME_STATE'&&b.run_id===p.run_id&&b.session_id===p.session_id
   &&b.frame_id===p.step_id&&b.full_state_sha256===p.full_state_sha256&&b.decoder==='DecoderGAVP'&&b.recursive_eval===true,'FULL_PL_FLOW_BINDING');
  fail(p.flow.length===2&&p.flow.every(a=>a.length===721&&a.every(Number.isFinite)),'FULL_PL_FLOW_ARRAY');
  fail(await sha(new Float32Array(p.flow.flat()).buffer)===p.flow_sha256,'FULL_PL_FLOW_SHA');
 }
 window.FlyVisFullPLProtocol={validate,validateStream};
 // Display samples only: fixed signed scale, no synthetic neural states.
 function groupSample(p){
  fail(p.signed_means?.length===8&&p.signed_means.every(Number.isFinite),'FULL_PL_GROUP_MEANS');
  return {step:p.step_id,time:p.activity_time_s,means:p.signed_means.slice(),t4:p.signed_means.slice(0,4).reduce((a,b)=>a+b,0)/4,
   t5:p.signed_means.slice(4,8).reduce((a,b)=>a+b,0)/4};
 }
 function drawGroups(stage,packet,anchor,history){
  if(history.run!==packet.run_id){history.run=packet.run_id;history.samples=new Map();}
  if(anchor?.run_id===packet.run_id)history.samples.set(anchor.step_id,groupSample(anchor));
  const point=groupSample(packet);history.samples.set(point.step,point);
  const rows=Array.from(history.samples.values()).filter(r=>r.step<=point.step).sort((a,b)=>a.step-b.step);
  const c=stage.c,domain=.5,end=Math.max(2.425,point.time);
  const types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];
  const colors=['#efc65b','#5edce9','#5fe2b0','#b89aff','#ef8db5','#dcce66','#98c5fa','#c6dce9'];
  c.save();c.fillStyle='#0f1f2c';c.fillRect(1384,88,504,960);
  stage.text('八类神经元 · 同步真实活动',1396,119,25,'#e5f4f6',true);
  stage.text('T4：亮边缘通路   T5：暗边缘通路',1396,151,20,'#c2dce5');
  stage.text('每条为721节点均值；不是单细胞测量',1396,180,18,'#a9c2cd');
  stage.text('原始带符号活动 · 统一固定纵轴 ±0.5',1396,209,18,'#a9c2cd');
  const signed=v=>(v>=0?'+':'')+v.toFixed(3);
  types.forEach((type,i)=>{
   const top=234+i*86,x=1484,y=top+10,w=380,h=54;
   const ref=stage.referenceDirections?.().find(r=>r.letter===type.slice(2));
   stage.text(type+(ref?' '+ref.arrow:''),1396,top+23,21,colors[i],true);
   stage.text(signed(point.means[i]),1396,top+49,17,colors[i]);
   const px=t=>x+w*t/end,py=v=>y+h/2-h/2*Math.max(-domain,Math.min(domain,v))/domain;
   c.strokeStyle='#42606c';c.lineWidth=1;c.beginPath();c.moveTo(x,y+h/2);c.lineTo(x+w,y+h/2);c.stroke();
   c.strokeStyle=colors[i];c.fillStyle=colors[i];c.lineWidth=2;c.beginPath();
   rows.forEach((r,j)=>{if(j&&r.step-rows[j-1].step<=10)c.lineTo(px(r.time),py(r.means[i]));else c.moveTo(px(r.time),py(r.means[i]));});c.stroke();
   c.beginPath();c.arc(px(point.time),py(point.means[i]),3,0,Math.PI*2);c.fill();
   if(Math.abs(point.means[i])>domain)stage.text('越界',1815,top+5,13,'#ffc976');
  });
  stage.text('0',1484,938,15,'#a9c2cd');stage.text(end.toFixed(3)+' s 模型时间',1694,938,17,'#a9c2cd');
  stage.text('零线保留正负；超出纵轴截边，数值不截断',1396,971,17,'#a9c2cd');
  stage.text('箭头为参考偏好；曲线只用本次核验样本',1396,1000,18,'#a9c2cd');
  stage.text('方向结论结合光流，不能只看哪条最亮',1396,1032,18,'#e5f4f6');
  c.restore();Object.assign(stage.canvas.dataset,{groupCurveRun:packet.run_id,groupCurveStep:String(point.step),groupT4:String(point.t4),groupT5:String(point.t5),groupCurveSamples:String(rows.length),groupCurveScale:'FIXED_SIGNED_MINUS0_5_PLUS0_5',subtypeMeans:JSON.stringify(point.means)});
 }
 window.FlyVisFullPLGroups={groupSample,drawGroups};

 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id);
 window.FlyVisFullPLBegin=function(){
  ui.enterLive();ui.stage.clearGuide();
  ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);
  ui.stage.text('本次现场计算 · 等待第一个核验状态',60,130,30);
  ui.stage.canvas.dataset.displayKind='WAITING_CURRENT_RUN';
  for(const k of ['session','stateToken','fullStateSha256','flowStateSha256','run','frame'])delete ui.stage.canvas.dataset[k];
  root.querySelector('.cp-heading').textContent='本次现场计算请求 · 不显示旧实验结果';
  $('cpStatus').textContent='开始请求处理中；尚未收到本次已核验活动。';
 };

 async function setup(){
  const [saved,stream]=await Promise.all([json('/api/full-pl/status'),json('/api/full-pl-stream/status')]);
  if(!saved.configured&&!stream.configured)return;
  const panel=document.createElement('div');panel.className='cp-player';panel.id='cpFullPL';
  const show=document.createElement('button'),watch=document.createElement('button'),back=document.createElement('button'),state=document.createElement('span');
  show.textContent='查看⑪已验收的完整首步';watch.textContent='接收并显示连续状态';watch.hidden=!stream.configured;back.textContent='返回原离线演示';back.hidden=true;
  const sourceLabel=document.createElement('span');sourceLabel.id='cpFullPLSourceLabel';
  panel.append(show,watch,back,sourceLabel,state);ui.stage.host.before(panel);
  const replay=document.createElement('button'),seek=document.createElement('input');
  replay.textContent='播放本次485步 · 约40秒 · OFFLINE REPLAY';replay.hidden=true;
  seek.type='range';seek.min=0;seek.max=484;seek.step=1;seek.value=0;seek.hidden=true;seek.setAttribute('aria-label','本次完整结果统一时间轴');
  panel.append(replay,seek);
  if(stream.configured){const link=document.createElement('a');link.href='/api/full-pl-stream/link.zip';link.textContent=stream.first_step_accepted?'下载本次板端显示连接包':'下载新版DDR板端准备包';panel.append(link);}
  if(stream.configured&&stream.preparation_id){const start=document.createElement('a');start.href=stream.camera_live?'/api/full-pl-stream/fixed.ipynb':'/api/full-pl-stream/start.ipynb';start.textContent=stream.camera_live?'下载本后端固定Notebook（摄像头/实验共用）':'下载同次START_DDR.ipynb（自动解压）';panel.append(start);}
  if(stream.camera_live){const stop=document.createElement('button');stop.textContent='停止本次纯FPGA计算';stop.disabled=!stream.first_step_accepted;panel.append(stop);
   stop.onclick=async()=>{try{await json('/api/full-pl-stream/camera-stop',{preparation_id:stream.preparation_id});state.textContent='已请求停止，等待当前完整PL快照返回；不取消在途神经步。';}catch(e){state.textContent=e.message;}};}
  if(saved.status==='WAITING_FIRST_STEP'&&stream.configured){
   show.disabled=true;watch.disabled=true;state.textContent='等待人工板端准备 · 首步完整状态验收后自动接收连续状态 · 尚未运行板卡';
   if(stream.camera_live)state.textContent=stream.source_kind==='controlled_animation'?'纯FPGA固定实验：等待人工准备与首步独立核验；旧离线画面不是本次结果。':'纯FPGA摄像头60秒：等待人工准备与首步独立核验；当前下方仍是原离线演示。';
   let checking=false;
   const wait=setInterval(async()=>{if(checking)return;checking=true;try{const s=await json('/api/full-pl-stream/status');
    if(['FAILED','STOPPED'].includes(s.status)){clearInterval(wait);state.textContent='已停止 · '+(s.error||s.status)+'；请保留本次记录，不要重跑准备格。';}
    else if(s.first_step_accepted){clearInterval(wait);panel.remove();await setup();}
   else if(s.start_requested){if(ui.stage.canvas.dataset.displayKind!=='WAITING_CURRENT_RUN')window.FlyVisFullPLBegin();state.textContent='本次已开始 · 等待完整首步数值核验与官方光流';}
   }catch(e){clearInterval(wait);state.textContent='PC连接中断 · '+e.message;}finally{checking=false;}},750);
   return;
  }
  if(saved.status!=='VERIFIED_SAVED_FIRST_STEP'){show.disabled=true;watch.disabled=true;state.textContent='NOT_AVAILABLE · '+(saved.error||'首步结果未通过');return;}
  state.textContent='首步45,669状态逐字核对通过 · 连续轨迹独立审计待完成';
  let hidden=[],heading='',callbacks,entered=false,generation=0,revision=-1,projection,health,anchor,streaming=false,replaying=false,replayStep=0;
  const groupHistory={run:null,samples:new Map()};
  function clearStreamIdentity(){for(const k of ['session','stateToken','fullStateSha256','flowStateSha256','flowStatus','run','frame','inputTime','activityTime','means'])delete ui.stage.canvas.dataset[k];}
  function blank(text){ui.stage.clearGuide();ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text(text,60,130,30);clearStreamIdentity();ui.stage.canvas.dataset.displayKind='NOT_AVAILABLE';}
  function enter(){
   if(entered)return;ui.enterLive();entered=true;heading=root.querySelector('.cp-heading').innerHTML;
   for(const el of [root.querySelector('.cp-player'),$('cpLiveControls'),$('cpJointControls'),$('cpAnalysis'),$('cpSpatialDetails'),$('cpPolicyNotice'),$('cpReceipt').parentElement])if(el&&el!==panel){hidden.push([el,el.hidden]);el.hidden=true;}
   callbacks={onPlay:ui.stage.onPlay,onSeek:ui.stage.onSeek,onCamera:ui.stage.onCamera};ui.stage.onPlay=null;ui.stage.onSeek=null;ui.stage.onCamera=null;
   back.hidden=false;
  }
  back.onclick=async()=>{
   generation++;streaming=false;replaying=false;for(const [el,value] of hidden)el.hidden=value;hidden=[];back.hidden=true;show.disabled=false;watch.disabled=false;
   if(callbacks)Object.assign(ui.stage,callbacks);if(entered)root.querySelector('.cp-heading').innerHTML=heading;entered=false;clearStreamIdentity();await ui.leaveLive();
  };
  async function prepare(){
   if(!anchor)anchor=await json('/api/full-pl/frame');
   if(!health){health=await json('/api/full-pl/projection');projection=await FlyVisFixedSkeleton.load(health);}
  }
  function inputCanvas(p){
   const canvas=document.createElement('canvas');canvas.width=400;canvas.height=340;
   const uv=health.coordinates_uv;fail(uv?.length===721,'FULL_PL_INPUT_COORDINATES');
   const c=canvas.getContext('2d'),scale=5.5;c.fillStyle='#08111b';c.fillRect(0,0,400,340);
   uv.forEach(([u,v],i)=>{const x=200+1.5*v*scale,y=170+Math.sqrt(3)*(u+v/2)*scale;
    c.beginPath();for(let j=0;j<6;j++){const a=j*Math.PI/3,jx=x+Math.cos(a)*scale,jy=y+Math.sin(a)*scale;j?c.lineTo(jx,jy):c.moveTo(jx,jy);}c.closePath();
    const g=Math.round(Math.min(1,Math.max(0,p.input_hex[i]))*255);c.fillStyle=`rgb(${g},${g},${g})`;c.fill();});return canvas;
  }
  function flowCanvas(p){
   const canvas=document.createElement('canvas');canvas.width=400;canvas.height=340;const c=canvas.getContext('2d');c.fillStyle='#091523';c.fillRect(0,0,400,340);
   if(p.flow===null){c.fillStyle='#c9e0e5';c.font='18px sans-serif';c.fillText('NOT_AVAILABLE',35,115);c.fillText('本步尚未取得官方解码',35,145);return canvas;}
   health.coordinates_uv.forEach(([u,v],i)=>{const x=200+1.5*v*5,y=135+Math.sqrt(3)*(u+v/2)*5,dx=p.flow[0][i]*8,dy=-p.flow[1][i]*8,n=Math.hypot(dx,dy);if(n<.08)return;
    const a=Math.atan2(dy,dx),head=Math.min(7,n*.38);c.strokeStyle='#74e4d5';c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);
    for(const side of [-.5,.5]){c.moveTo(x+dx-head*Math.cos(a+side),y+dy-head*Math.sin(a+side));c.lineTo(x+dx,y+dy);}c.stroke();});return canvas;
  }
  async function draw(p,status,ticket){
   const rendered=await projection.render(p,'full-pl-'+p.session_id+'-'+p.serial);if(ticket!==generation)return false;
   const raw=document.createElement('canvas');raw.width=rendered.width;raw.height=rendered.height;raw.getContext('2d').putImageData(new ImageData(rendered.pixels,raw.width,raw.height),0,0);
   const liveStream=p.schema==='flyvis-full-pl-stream-display/v1';
   const meta={run_id:p.run_id,types:rendered.receipt.types,means:[rendered.receipt.means],coordinates_uv:health.coordinates_uv,input_time_s:[p.input_time_s],activity_time_s:[p.activity_time_s]};
   const elapsed=liveStream?p.elapsed_seconds:saved.timing.input_seconds+saved.timing.step_call_seconds+saved.timing.readback_seconds;
   const live={backend:p.backend,stream:liveStream,finished:status?.status==='FINISHED',sourceKind:p.source.kind,step:p.step_id,sourceSequence:p.source.sequence,wallElapsed:p.plan_metadata?.camera_live?p.wall_elapsed_s:elapsed,clock:{mode:liveStream?'FULL_PL_STEP_DRIVEN':'SAVED_RESULT',target_steps_per_s:p.plan_metadata?.step_rate_limit_hz}};
   let visual=inputCanvas(p);
   if(['recorded_camera_flyvis','real_windows_camera','controlled_animation'].includes(p.source.kind)){
    const response=await fetch(`/api/full-pl-stream/source-frame?step=${p.step_id}&run=${encodeURIComponent(p.run_id)}&state=${p.full_state_sha256}`);
    fail(response.ok,'FULL_PL_CAMERA_SOURCE_NOT_AVAILABLE');const blob=await response.blob();
    fail(await sha(await blob.arrayBuffer())===p.source.pixel_png_sha256,'FULL_PL_CAMERA_SOURCE_SHA');visual=await createImageBitmap(blob);
   }
   if(ticket!==generation){visual.close?.();return false;}
   ui.stage.draw(0,raw,rendered.receipt,meta,{input:visual,flow:flowCanvas(p),flowValues:p.flow===null?new Float32Array(1442).fill(NaN):new Float32Array(p.flow.flat())},0,live);
   visual.close?.();
   drawGroups(ui.stage,p,anchor,groupHistory);
   Object.assign(ui.stage.canvas.dataset,{session:p.session_id,stateToken:String(p.state_token),fullStateSha256:p.full_state_sha256,flowStateSha256:p.flow_binding?.full_state_sha256||'',flowStatus:p.flow_status});
   root.querySelector('.cp-heading').textContent=p.offline_replay?'⑪ 本次已保存计算结果 · OFFLINE REPLAY · 5ms数学步长 / 12.125步每秒播放':liveStream?(status.status==='FINISHED'?'⑪ 本次完整PL计算已结束 · 保留最后状态':'⑪ 连续完整PL状态 · 整段轨迹待审计 · 不宣称实时PASS'):'⑪ 实体FPGA · 固定输入首步 · OFFLINE REPLAY · 当前未连接板卡';
   $('cpStatus').textContent=`${p.plan_metadata?.condition_id||'固定输入'} · 第${p.step_id+1}/${p.plan_metadata?.steps||'?'}步 · 模型输入 ${p.input_time_s.toFixed(3)}s → 活动 ${p.activity_time_s.toFixed(3)}s · 本步生产耗时 ${(elapsed*1000).toFixed(2)}ms · ${p.flow===null?'本步光流NOT_AVAILABLE':'同一步官方光流（CPU解码）'}。`;
   if(p.source.kind==='recorded_camera_flyvis')$('cpStatus').textContent+=` 录制输入 · 采集帧${p.source.source_frame} · ${p.source.capture_utc} · OFFLINE/FROZEN INPUT，非持续实时摄像头。`;
   if(p.source.kind==='real_windows_camera'){
    sourceLabel.textContent=status.status==='FINISHED'?'纯FPGA摄像头本次运行结束 · 保留真实已解码状态':'本次真实摄像头 → 完整网络FPGA → 官方光流 · CPU独立审核中';
    $('cpStatus').textContent=`实际运行 ${p.wall_elapsed_s.toFixed(2)} / 60秒 · 本帧采集 ${p.capture_elapsed_s.toFixed(3)}秒 · 第${p.step_id+1}步 · 模型输入 ${p.input_time_s.toFixed(3)}秒 → 活动 ${p.activity_time_s.toFixed(3)}秒（5ms数学步长；最高8步/实际秒展示档，非硬件上限） · 采集帧${p.source.source_frame} · ${p.source.capture_utc} · 同一步骨架与CPU官方光流。 ${status.stop_reason||''}`;
   }
   if(p.source.kind==='controlled_animation'){
    sourceLabel.textContent=status.status==='FINISHED'?'固定实验已结束；查看实际核验状态':'固定科学刺激 → 全网FPGA → 官方光流';
    $('cpStatus').textContent=`${p.condition_id} · 第${p.step_id+1}/485步 · 实际 ${p.wall_elapsed_s.toFixed(2)}秒 · 模型输入 ${p.input_time_s.toFixed(3)}秒 → 活动 ${p.activity_time_s.toFixed(3)}秒 · 严格FP32全状态独立审核 ${status.numerical_audit||'PENDING'} · 不宣称实时。`;
   }
   state.textContent=`run ${p.run_id} · boot ${p.hardware.boot_id} · ${liveStream?`已接收${status.received_steps}步 / 绘制回执${status.browser_receipts}帧`:'已保存首步结果'} · 每类721节点真实均值`;
   if(!panel.querySelector('details')){const detail=document.createElement('details'),summary=document.createElement('summary'),identity=document.createElement('pre');summary.textContent='当前状态身份与带符号活动';identity.id='cpFullPLIdentity';detail.append(summary,identity);panel.append(detail);}
   $('cpFullPLIdentity').textContent=JSON.stringify({run:p.run_id,session:p.session_id,step:p.step_id,hardware:p.hardware,model:p.model,input_sha256:p.input_sha256,full_state_sha256:p.full_state_sha256,signed_means:p.signed_means,flow:p.flow_status,transport_profile:p.transport_profile,initial_state_readback:p.initial_state_readback,cycle_definition:p.cycle_definition,source_audit:p.source_audit,storage:status?.storage_policy||'SAVED_FIRST_STEP_ZIP'},null,2);
   return true;
  }
  async function drawReplay(step,ticket){
   await prepare();const r=await json('/api/full-pl-stream/replay?step='+step);await validateStream(r.frame,r.status,anchor,health);
   if(ticket!==generation)return;enter();await draw(r.frame,r.status,ticket);seek.value=step;replayStep=step;
  }
  seek.oninput=async()=>{replaying=false;replay.textContent='播放本次485步 · 约40秒 · OFFLINE REPLAY';const ticket=++generation;
   try{await drawReplay(Number(seek.value),ticket);}catch(e){if(ticket===generation){blank('NOT_AVAILABLE · 回放已撤销');state.textContent=e.message;}}
  };
  replay.onclick=async()=>{
   if(replaying){replaying=false;generation++;replay.textContent='继续回放本次结果 · OFFLINE REPLAY';return;}
   replaying=true;streaming=false;const ticket=++generation,startStep=replayStep>=484?0:replayStep,begin=performance.now();replay.textContent='暂停回放';
   try{while(replaying&&ticket===generation){const step=Math.min(484,startStep+Math.floor((performance.now()-begin)*12.125/1000));
    await drawReplay(step,ticket);if(step===484)break;await new Promise(r=>setTimeout(r,1000/12.125));}
   }catch(e){if(ticket===generation){blank('NOT_AVAILABLE · 回放已撤销');state.textContent=e.message;}}
   if(ticket===generation){replaying=false;replay.textContent='播放本次485步 · 约40秒 · OFFLINE REPLAY';}
  };
  show.onclick=async()=>{const ticket=++generation;streaming=false;show.disabled=true;watch.disabled=false;
   try{await prepare();await validate(anchor,saved,health);if(ticket!==generation)return;enter();await draw(anchor,null,ticket);}
   catch(e){enter();blank('NOT_AVAILABLE · 本次显示已撤销');state.textContent=e.message;}
  };
  watch.onclick=async()=>{
   const ticket=++generation;streaming=true;replaying=false;revision=-1;show.disabled=false;watch.disabled=true;enter();blank('等待同一run/boot的后续完整PL状态…');root.querySelector('.cp-heading').textContent='等待⑪连续完整PL状态 · 尚未收到本次新结果';
   try{
    await prepare();
    while(streaming&&ticket===generation){
     const begin=performance.now(),reply=await json('/api/full-pl-stream/latest?after='+revision),end=performance.now();if(ticket!==generation)return;
     const s=reply.status;
     if(['FAILED','STOPPED','DISABLED','WAITING_FIRST_STEP'].includes(s.status))throw Error(s.error||s.status);
     if(reply.frame){
      const p=reply.frame;await validateStream(p,s,anchor,health);if(ticket!==generation)return;
      if(await draw(p,s,ticket)){
       revision=p.revision;await new Promise(resolve=>requestAnimationFrame(resolve));if(ticket!==generation)return;
       const drew=performance.now(),pcReply=reply.response_pc_ns/1e6,received=p.received_pc_ns/1e6;
       const lo=Math.max(0,pcReply+(drew-end)-received),hi=Math.max(lo,pcReply+(drew-begin)-received);
       const receipt={run_id:p.run_id,session_id:p.session_id,frame_id:p.step_id,full_state_sha256:p.full_state_sha256,
        receive_to_draw_lower_ms:lo,receive_to_draw_upper_ms:hi,clock_uncertainty_ms:(end-begin)/2,raw_sha256:ui.stage.canvas.dataset.skeletonSha};
       await json('/api/full-pl-stream/paint',receipt);if(ticket!==generation)return;
       $('cpStatus').textContent+=` PC接收→绘制回调 ${lo.toFixed(1)}～${hi.toFixed(1)}ms（含时钟配对不确定度；非相机端到端）。`;
      }
     }
     if(s.official_flow?.error)throw Error(s.official_flow.error);
     if(s.official_flow?.pending)state.textContent+=` · 官方光流 ${s.official_flow.decoded}/${s.official_flow.accepted}，异步解码中`;
     if(s.status==='FINISHED'&&(!s.official_flow||s.display_complete)){streaming=false;watch.disabled=false;
      if(s.display_complete&&(!stream.camera_live||s.replay_available===true)){replay.hidden=false;seek.hidden=false;}return;}
     await new Promise(resolve=>setTimeout(resolve,Math.max(0,1000/(stream.camera_live?5:12)-(performance.now()-begin))));
    }
   }catch(e){if(ticket===generation){streaming=false;blank('NOT_AVAILABLE · 连续状态显示已撤销');state.textContent=e.message+'；没有回退旧活动。';watch.disabled=false;}}
  };
  if(stream.configured&&stream.first_step_accepted)watch.onclick();
 }
 setup().catch(()=>{}); // Optional ingress must never block old55/offline startup.
})();
