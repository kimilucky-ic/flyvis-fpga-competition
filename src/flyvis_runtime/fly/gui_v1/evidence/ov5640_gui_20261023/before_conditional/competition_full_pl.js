/* Saved first-step + bounded continuous full-PL states in the ORIGINAL stage. */
(() => {
 'use strict';
 const historyRun=new URLSearchParams(location.search).get('replay_run');
 const historyPath=path=>historyRun&&path.startsWith('/api/full-pl')?path+(path.includes('?')?'&':'?')+'replay_run='+encodeURIComponent(historyRun):path;
 const fail=(ok,message)=>{if(!ok)throw Error(message);};
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 async function json(path,body){const r=await fetch(historyPath(path),body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),p=await r.json();if(!r.ok)throw Error(p.error||'FULL_PL_HTTP_'+r.status);return p;}
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
 async function validateOV(p,s,h){
  fail(s.source_kind==='board_ov5640'&&s.status==='FINISHED'&&s.result_valid&&s.first_step_accepted,'OV5640_NOT_AUDITED');
  fail(p.source.kind==='board_ov5640'&&p.session_id===s.session_id&&p.run_id===s.run_id&&p.step_id===0&&p.state_token===1&&p.input_time_s===0&&p.activity_time_s===.005,'OV5640_IDENTITY');
  fail(p.display_kind==='OFFLINE_OV5640_ONE_STEP'&&p.board_connection==='NOT_CONNECTED'&&['CPU_MOCK_ONLY','OFFLINE_CPU_AUDIT_OF_OPERATOR_REPORTED_BOARD_CAPTURE'].includes(p.evidence_level)&&p.evidence_level===s.evidence,'OV5640_EVIDENCE');
  fail(p.hardware.bit_sha256==='781981526e8cc9916c096ff46b92046d90021d56c9438718fe5566cfdf1df7d7'&&p.hardware.hwh_sha256==='61465634adaa0e421a5b07c77b38e0739fdcfdf8e68e977f25bf2d803b9097ae','OV5640_IMAGE');
  fail(p.acceptance.mismatch_words===0&&p.acceptance.state_words_compared===45669&&p.acceptance.state_sha256===p.full_state_sha256&&p.acceptance.input_sha256===p.input_sha256&&p.acceptance.source_frame_sha256===p.source.raw_sha256,'OV5640_AUDIT_BINDING');
  await arrays(p,h);
  fail(p.flow_status==='OFFICIAL_DECODER_SAME_STATE'&&p.flow_binding.decoder==='DecoderGAVP'&&p.flow_binding.recursive_eval===true&&p.flow_binding.full_state_sha256===p.full_state_sha256&&p.flow_binding.run_id===p.run_id&&p.flow_binding.session_id===p.session_id&&p.flow_binding.frame_id===0,'OV5640_FLOW_IDENTITY');
  fail(p.flow.length===2&&p.flow.every(a=>a.length===721&&a.every(Number.isFinite))&&await sha(new Float32Array(p.flow.flat()).buffer)===p.flow_sha256,'OV5640_FLOW_SHA');
 }
 window.FlyVisFullPLProtocol={validate,validateStream,validateOV};
 // Fixed central hex radius3 ROI: same37 coordinates for all8types, SHA-bound spatial map.
 // Curves and full-PL skeleton brightness share these exact current-run central values.
 const centralIDs=[24399,25120,25841,26562,27283,28004,28725,29446];
 const roiOffsets=[270,271,272,273,298,299,300,301,302,327,328,329,330,331,332,357,358,359,360,361,362,363,388,389,390,391,392,393,418,419,420,421,422,447,448,449,450];
 const roiDefinition={kind:"CENTRAL_HEX_RADIUS3",count:37,radius:3,criterion:"max(abs(u),abs(v),abs(u+v))<=3",spatial_indices:Array.from({length:8},(_,i)=>roiOffsets.map(j=>i*721+j)),global_ids:Array.from({length:8},(_,i)=>roiOffsets.map(j=>centralIDs[i]+j-360)),aggregation:"mean_signed_then_rectify"};
 function groupSample(p){
  fail(p.spatial?.map_sha256==='5a2a439d3625c54762f9a83053157f6c6ae6f941403443177e52656597d8e001','FULL_PL_CENTRAL_MAP');
  fail(p.spatial.values?.length===5768,'FULL_PL_CENTRAL_ARRAY');
  const raw=roiDefinition.spatial_indices.map(indices=>indices.reduce((sum,i)=>{const v=p.spatial.values[i];fail(Number.isFinite(v),'FULL_PL_ROI_VALUES');return sum+v;},0)/37);
  fail(raw.every(Number.isFinite)&&Number.isFinite(p.activity_time_s)&&Number.isSafeInteger(p.step_id),'FULL_PL_CENTRAL_VALUES');
  return {step:p.step_id,time:p.activity_time_s,raw,values:raw.map(v=>Math.max(v,0)),roi:roiDefinition};
 }
 function drawGroups(stage,packet,anchor,history){
  if(history.run!==packet.run_id){history.run=packet.run_id;history.samples=new Map();}
  if(anchor?.run_id===packet.run_id&&(!history.bounds||anchor.step_id>=history.bounds.startStep))history.samples.set(anchor.step_id,groupSample(anchor));
  const point=groupSample(packet);history.samples.set(point.step,point);
  const rows=Array.from(history.samples.values()).filter(r=>r.step<=point.step&&(!history.bounds||r.step>=history.bounds.startStep)).sort((a,b)=>a.step-b.step);
  const c=stage.c,domain=[.5,1,2].includes(history.yDomain)?history.yDomain:1,start=history.bounds?.startTime??Math.min(0,anchor?.activity_time_s||0),end=history.bounds?.endTime??Math.max(2.425,point.time);
  const types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];
  const colors=['#efc65b','#5edce9','#5fe2b0','#b89aff','#ef8db5','#dcce66','#98c5fa','#c6dce9'];
  c.save();c.fillStyle='#0f1f2c';c.fillRect(1384,88,504,960);
  stage.text('中央区域 T4 / T5 · 同步响应',1396,119,25,'#e5f4f6',true);
  stage.text('T4偏好亮边缘｜T5偏好暗边缘；非互斥开关',1396,151,20,'#c2dce5');
  stage.text('曲线与骨架：同一步中央37节点均值',1396,180,18,'#a9c2cd');
  stage.text(`曲线共用纵轴0–${domain} · 骨架亮度范围仍为0–2`,1396,209,18,'#a9c2cd');
  const signed=v=>(v>=0?'+':'')+v.toFixed(3);
  types.forEach((type,i)=>{
   const top=234+i*86,x=1484,y=top+10,w=380,h=62,rowDomain=domain;
   const ref=stage.referenceDirections?.().find(r=>r.letter===type.slice(2));
   stage.text(type+(ref?' 偏好'+ref.arrow:''),1396,top+23,21,colors[i],true);
   stage.text(signed(point.raw[i]),1396,top+49,17,colors[i]);
   stage.text('37节点',1396,top+68,12,'#a9c2cd');
   const px=t=>x+w*(t-start)/(end-start),py=v=>y+h-h*Math.max(0,Math.min(rowDomain,v))/rowDomain;
   c.strokeStyle='#42606c';c.lineWidth=1;c.beginPath();c.moveTo(x,y+h);c.lineTo(x+w,y+h);c.stroke();
   c.strokeStyle='#29434e';c.beginPath();c.moveTo(x,y+h/2);c.lineTo(x+w,y+h/2);c.stroke();
   stage.text(String(domain),1868,y+12,12,'#9eb7c1');stage.text('0',1868,y+h,12,'#9eb7c1');
   c.strokeStyle=colors[i];c.fillStyle=colors[i];c.lineWidth=2.5;c.beginPath();
   rows.forEach((r,j)=>{if(j&&r.step-rows[j-1].step<=10)c.lineTo(px(r.time),py(r.values[i]));else c.moveTo(px(r.time),py(r.values[i]));});c.stroke();
   c.beginPath();c.arc(px(point.time),py(point.values[i]),3,0,Math.PI*2);c.fill();
   if(rows.some(r=>r.values[i]>rowDomain))stage.text('↑ 含超界值；原数值保留',1675,top+5,13,'#ffc976');
  });
  stage.text(start.toFixed(3),1484,938,15,'#a9c2cd');stage.text(end.toFixed(3)+' s 模型时间',1694,938,17,'#a9c2cd');
  stage.text('先求带符号均值，再整流；数字保留正负',1396,971,17,'#a9c2cd');
  stage.text('箭头为参考偏好；其他方向也可能有响应',1396,1000,18,'#a9c2cd');
  stage.text('局部群体响应；不等同官方单中央节点DSI',1396,1032,18,'#e5f4f6');
  c.restore();Object.assign(stage.canvas.dataset,{groupCurveRun:packet.run_id,groupCurveStep:String(point.step),groupCurveSamples:String(rows.length),groupCurveScale:'FIXED_RECTIFIED_0_'+domain+'_ALL_TYPES',curveYMax:String(domain),centralROISigned:JSON.stringify(point.raw),centralROIValues:JSON.stringify(point.values),centralROIDefinition:JSON.stringify(roiDefinition)});
 }
 function motionSummary(p){
  const cid=p.condition_id||p.plan_metadata?.condition_id||'',match=/^(EDGE|BAR)_(?:ON|OFF|BRIGHT|DARK)_(RIGHT|LEFT|UP|DOWN)(?:_(STATIC))?$/.exec(cid);
  const directions={RIGHT:{label:'向右',angle:0},LEFT:{label:'向左',angle:180},UP:{label:'向上',angle:90},DOWN:{label:'向下',angle:270}};
  const known=match?directions[match[2]]:null,stationary=!!match?.[3];
  const phase=!known?'采集输入 · 无预设方向':stationary?'静态对照':p.step_id<=200?'运动前 · 静态输入':p.step_id<400?'边缘 / 条纹移动中':'运动结束 · 保持末帧';
  const x=p.flow?.[0]?.[360],y=p.flow?.[1]?.[360],available=Number.isFinite(x)&&Number.isFinite(y),magnitude=available?Math.hypot(x,y):null;
  const angle=available&&magnitude>0?(Math.atan2(y,x)*180/Math.PI+360)%360:null;
  // Fixed display-only salience threshold, not a scientific confidence criterion.
  const weak=available&&magnitude<.5;
  return {known,phase,available,magnitude,angle,weak,displayThreshold:.5,
   conclusion:!available?'本步光流不可用':weak?'弱输出 · 不判方向':known&&(stationary||p.step_id<=200||p.step_id>=400)?'静态期输出 · 不判运动':'当前中央局部估计'};
 }
 function drawMotionSummary(stage,p){
  const s=motionSummary(p),c=stage.c;c.save();c.fillStyle='#10212d';c.fillRect(1104,787,238,252);
  stage.text('刺激：'+(s.known?s.known.label+' '+s.known.angle+'°':'未知 / 摄像头'),1114,815,18,'#c5edf1',true);
  stage.text(s.phase,1114,845,17,'#a9c2cd');
  stage.text(s.conclusion,1114,879,18,s.weak?'#b3c0c7':'#a3ebd6',true);
  stage.text('中央角度 '+(s.angle===null?'—':s.angle.toFixed(1)+'°'),1114,911,18,'#dceff2');
  stage.text('强度 '+(s.magnitude===null?'—':s.magnitude.toFixed(3))+' · 原始单位',1114,943,17,'#dceff2');
  stage.text('弱显示阈值 <0.5',1114,978,15,'#9db7c4');
  stage.text('非官方置信度 / 非识别率',1114,1006,14,'#9db7c4');c.restore();
  Object.assign(stage.canvas.dataset,{stimulusDirection:s.known?.label||'UNKNOWN',stimulusAngle:s.known?String(s.known.angle):'',stimulusPhase:s.phase,flowMagnitude:s.magnitude===null?'':String(s.magnitude),flowRawAngle:s.angle===null?'':String(s.angle),flowDirectionConclusion:s.conclusion,flowWeakDisplayThreshold:'0.5',flowWeakDisplayOnly:'true'});
  const detail='中央角度 '+(s.angle===null?'不可用':s.angle.toFixed(1)+'°')+'；强度 '+(s.magnitude===null?'不可用':s.magnitude.toFixed(3))+'（原始单位）';
  stage.canvas.dataset.explanationTitle=s.conclusion;stage.canvas.dataset.explanationDetail=detail;
  stage.canvas.setAttribute('aria-label','同一步真实输入、骨架与官方光流；'+s.phase+'；刺激'+(s.known?s.known.label:'方向未知')+'；'+s.conclusion+'；'+detail);
  if(stage.guide?.available)stage.updateGuide({...stage.guide,title:s.conclusion,detail,comparison:'刺激方向：'+(s.known?s.known.label:'未知')+'；'+s.phase,conclusion:s.conclusion});
 }
 window.FlyVisFullPLMotion={motionSummary,drawMotionSummary};
 window.FlyVisFullPLGroups={groupSample,drawGroups};

 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id);
 function fitReplayStage(){if(!historyRun||document.body.classList.contains('competition-cinema'))return;
  requestAnimationFrame(()=>{const available=Math.max(240,innerHeight-ui.stage.host.getBoundingClientRect().top-12);
   ui.stage.host.style.width=`min(100%, ${Math.floor(available*16/9)}px)`;ui.stage.host.style.marginLeft='auto';ui.stage.host.style.marginRight='auto';});
 }
 addEventListener('resize',fitReplayStage);
 const pendingHidden=new Map();
 window.FlyVisFullPLBegin=function(startRequested=true){
  ui.enterLive();ui.stage.clearGuide();
  for(const el of [root.querySelector('.cp-player'),$('cpLiveControls'),$('cpJointControls'),$('cpAnalysis'),$('cpSpatialDetails'),$('cpPolicyNotice')])if(el&&el.id!=='cpFullPL'){if(!pendingHidden.has(el))pendingHidden.set(el,el.hidden);el.hidden=true;}
  ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);
  ui.stage.text(startRequested?'本次现场计算 · 等待第一个核验状态':'本次实验已选定 · 准备好后点击开始',60,130,30);
  ui.stage.text('尚无本次神经活动；旧回放已清除。输入、骨架、曲线和光流将使用同一步。',60,190,24);
  ui.stage.canvas.dataset.displayKind=startRequested?'WAITING_CURRENT_RUN':'WAITING_PREPARED_INPUT';
  for(const k of ['session','stateToken','fullStateSha256','flowStateSha256','run','frame','inputTime','activityTime','centralROISigned','centralROIValues','skeletonBrightness','skeletonActivitySource'])delete ui.stage.canvas.dataset[k];
  root.querySelector('.cp-heading').textContent=startRequested?'本次现场计算请求 · 等待实际状态':'本次实验待开始 · 尚未计算';
  $('cpStatus').textContent=startRequested?'开始请求处理中；尚未收到本次已核验活动。':'请完成本次板端准备，然后点击上方开始；当前没有新实验结果。';
 };

 async function setup(){
  if(historyRun){document.body.classList.add('full-pl-replay');window.FlyVisFullPLBegin(false);ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text('正在核验已保存的完整实验 · OFFLINE REPLAY',60,130,30);fitReplayStage();}
  if(!historyRun&&!document.getElementById('cpSavedRuns')){
   try{const data=await json('/api/full-pl-history');if(data.results?.length){const list=document.createElement('div');list.id='cpSavedRuns';list.className='cp-player';
    const label=document.createElement('span');label.textContent='已保存结果（无需板卡）：';list.append(label);
    for(const [i,r] of data.results.slice(0,1).entries()){const link=document.createElement('a');link.href='/?replay_run='+encodeURIComponent(r.run_id)+'#competition';link.textContent=(i===0?'▶ 播放上次完整结果 · ':'')+r.condition_id;link.title='run '+r.run_id+' · OFFLINE REPLAY · 打开后核验';list.append(link);}ui.stage.host.before(list);}
   }catch(e){}
  }
  // Serialize archive admission: one saved-file validation, shared by subsequent GETs.
  const saved=await json('/api/full-pl/status'),stream=await json('/api/full-pl-stream/status');
  if(!saved.configured&&!stream.configured)return;
  const panel=document.createElement('div');panel.className='cp-player';panel.id='cpFullPL';
  const show=document.createElement('button'),watch=document.createElement('button'),back=document.createElement('button'),state=document.createElement('span');
  show.textContent='查看⑪已验收的完整首步';watch.textContent='接收并显示连续状态';watch.hidden=!stream.configured;back.textContent='返回原离线演示';back.hidden=true;
  const sourceLabel=document.createElement('span');sourceLabel.id='cpFullPLSourceLabel';
  panel.append(show,watch,back,sourceLabel,state);ui.stage.host.before(panel);
  const replay=document.createElement('button'),restart=document.createElement('button'),seek=document.createElement('input'),range=document.createElement('select'),axis=document.createElement('select');
  axis.id='cpFullPLCurveScale';axis.hidden=true;axis.setAttribute('aria-label','八类曲线统一纵轴');
  for(const [value,label] of [['1','曲线2倍 · 0–1'],['0.5','曲线4倍 · 0–0.5'],['2','全量刻度 · 0–2']]){const option=document.createElement('option');option.value=value;option.textContent=label;axis.append(option);}axis.value='1';
  range.id='cpFullPLReplayRange';range.hidden=true;range.setAttribute('aria-label','回放区间：节选或完整实验');
  const edge=/^EDGE_(ON|OFF)_(RIGHT|LEFT|UP|DOWN)$/.test(stream.condition_id||'');
  for(const [value,label] of [...(edge?[['central','中央响应节选 · 约10秒']]:[]),['motion','运动段 · 约17秒'],['full','完整485步 · 约40秒']]){const option=document.createElement('option');option.value=value;option.textContent=label;range.append(option);}
  range.value=edge?'central':'full';
  function playbackRange(){const selected=range.value;return selected==='central'?{start:250,end:370,label:'中央响应节选'}:selected==='motion'?{start:200,end:400,label:'运动段节选'}:{start:0,end:484,label:'完整结果'};}
  replay.id='cpFullPLReplay';restart.id='cpFullPLRestart';restart.textContent='▶ 从所选区间开头播放';restart.hidden=true;
  replay.textContent='▶ 播放所选区间 · OFFLINE REPLAY';replay.hidden=true;
  seek.type='range';seek.min=playbackRange().start;seek.max=playbackRange().end;seek.step=1;seek.value=playbackRange().start;seek.hidden=true;seek.setAttribute('aria-label','本次所选回放区间统一时间轴');
  const inputMode=document.createElement('select');inputMode.id='cpFullPLInputMode';inputMode.setAttribute('aria-label','感光输入显示');
  for(const [value,label] of [['binary','721六边形 · 黑白显示'],['gray','721六边形 · 真实灰度'],['source','矩形原图']]){const option=document.createElement('option');option.value=value;option.textContent=label;inputMode.append(option);}inputMode.value='binary';
  panel.append(restart,replay,range,axis,inputMode,seek);fitReplayStage();
  let lastInputStatus=null;
  inputMode.onchange=()=>{if(lastDrawnPacket)draw(lastDrawnPacket,lastInputStatus,generation).catch(e=>{state.textContent=e.message;});};
  if(!historyRun&&stream.configured&&stream.source_kind!=='board_ov5640'){const link=document.createElement('a');link.href='/api/full-pl-stream/link.zip';link.textContent=stream.first_step_accepted?'下载本次板端显示连接包':'下载新版DDR板端准备包';panel.append(link);}
  if(!historyRun&&stream.configured&&stream.preparation_id){const start=document.createElement('a');start.href=stream.camera_live?'/api/full-pl-stream/fixed.ipynb':'/api/full-pl-stream/start.ipynb';start.textContent=stream.camera_live?'下载本后端固定Notebook（摄像头/实验共用）':'下载同次START_DDR.ipynb（自动解压）';panel.append(start);}
  if(!historyRun&&stream.camera_live){const stop=document.createElement('button');stop.textContent='停止本次纯FPGA计算';stop.disabled=!stream.first_step_accepted;panel.append(stop);
   stop.onclick=async()=>{try{await json('/api/full-pl-stream/camera-stop',{preparation_id:stream.preparation_id});state.textContent='已请求停止，等待当前完整PL快照返回；不取消在途神经步。';}catch(e){state.textContent=e.message;}};}
  if(saved.status==='WAITING_FIRST_STEP'&&stream.configured){
   window.FlyVisFullPLBegin(!!stream.start_requested);
   show.disabled=true;watch.disabled=true;state.textContent='等待人工板端准备 · 首步完整状态验收后自动接收连续状态 · 尚未运行板卡';
   if(stream.source_kind==='board_ov5640')state.textContent='OV5640板端：请在上方下载固定Notebook。只采一帧、算一步；完整状态审核后自动显示，非60秒连续视频。';
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
  const groupHistory={run:null,samples:new Map(),yDomain:1};let lastDrawnPacket=null;
  axis.onchange=()=>{groupHistory.yDomain=Number(axis.value);if(lastDrawnPacket)drawGroups(ui.stage,lastDrawnPacket,anchor,groupHistory);};
  function clearStreamIdentity(){for(const k of ['session','stateToken','fullStateSha256','flowStateSha256','flowStatus','run','frame','inputTime','activityTime','means','centralROISigned','centralROIValues','centralROIDefinition','skeletonActivitySource','skeletonCentralROISigned','skeletonBrightness'])delete ui.stage.canvas.dataset[k];}
  function blank(text){ui.stage.clearGuide();ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text(text,60,130,30);clearStreamIdentity();ui.stage.canvas.dataset.displayKind='NOT_AVAILABLE';}
  function enter(){
   if(entered)return;ui.enterLive();entered=true;heading=root.querySelector('.cp-heading').innerHTML;
   for(const el of [root.querySelector('.cp-player'),$('cpLiveControls'),$('cpJointControls'),$('cpAnalysis'),$('cpSpatialDetails'),$('cpPolicyNotice'),$('cpReceipt').parentElement])if(el&&el!==panel){hidden.push([el,pendingHidden.has(el)?pendingHidden.get(el):el.hidden]);el.hidden=true;}
   pendingHidden.clear();
   callbacks={onPlay:ui.stage.onPlay,onSeek:ui.stage.onSeek,onCamera:ui.stage.onCamera};ui.stage.onPlay=()=>{if(!replay.hidden)replay.onclick();};ui.stage.onSeek=k=>{if(replay.hidden)return;const r=playbackRange();seek.value=Math.max(r.start,Math.min(r.end,Math.round(k)));seek.oninput();};ui.stage.onCamera=null;
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
    const value=Math.min(1,Math.max(0,p.input_hex[i])),g=inputMode.value==='binary'?(value>=.5?255:0):Math.round(value*255);c.fillStyle=`rgb(${g},${g},${g})`;c.fill();c.strokeStyle='#38505c';c.lineWidth=.35;c.stroke();});return canvas;
  }
  function flowCanvas(p){
   const canvas=document.createElement('canvas');canvas.width=400;canvas.height=340;const c=canvas.getContext('2d');c.fillStyle='#091523';c.fillRect(0,0,400,340);
   if(p.flow===null){c.fillStyle='#c9e0e5';c.font='18px sans-serif';c.fillText('NOT_AVAILABLE',35,115);c.fillText('本步尚未取得官方解码',35,145);return canvas;}
   health.coordinates_uv.forEach(([u,v],i)=>{const x=200+1.5*v*5,y=135+Math.sqrt(3)*(u+v/2)*5,dx=p.flow[0][i]*8,dy=-p.flow[1][i]*8,n=Math.hypot(dx,dy);if(n<.08)return;
    const a=Math.atan2(dy,dx),head=Math.min(7,n*.38);c.strokeStyle='#74e4d5';c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);
    for(const side of [-.5,.5]){c.moveTo(x+dx-head*Math.cos(a+side),y+dy-head*Math.sin(a+side));c.lineTo(x+dx,y+dy);}c.stroke();});return canvas;
  }
  async function draw(p,status,ticket){
   const rendered=await projection.render(p,'full-pl-'+p.session_id+'-'+p.serial,'CENTRAL_ROI37_T4T5');if(ticket!==generation)return false;
   const raw=document.createElement('canvas');raw.width=rendered.width;raw.height=rendered.height;raw.getContext('2d').putImageData(new ImageData(rendered.pixels,raw.width,raw.height),0,0);
   const liveStream=p.schema==='flyvis-full-pl-stream-display/v1';
   const meta={run_id:p.run_id,types:rendered.receipt.types,means:[rendered.receipt.means],coordinates_uv:health.coordinates_uv,input_time_s:[p.input_time_s],activity_time_s:[p.activity_time_s]};
   const elapsed=liveStream?p.elapsed_seconds:saved.timing.input_seconds+saved.timing.step_call_seconds+saved.timing.readback_seconds;
   const live={backend:p.backend,stream:liveStream,finished:status?.status==='FINISHED',sourceKind:p.source.kind,step:p.step_id,sourceSequence:p.source.sequence,wallElapsed:p.plan_metadata?.camera_live?p.wall_elapsed_s:elapsed,clock:{mode:liveStream?'FULL_PL_STEP_DRIVEN':'SAVED_RESULT',target_steps_per_s:p.plan_metadata?.step_rate_limit_hz}};
   let visual=inputCanvas(p);
   if(inputMode.value==='source'&&['recorded_camera_flyvis','real_windows_camera','controlled_animation','board_ov5640'].includes(p.source.kind)){
    const response=await fetch(historyPath(`/api/full-pl-stream/source-frame?step=${p.step_id}&run=${encodeURIComponent(p.run_id)}&state=${p.full_state_sha256}`));
    fail(response.ok,'FULL_PL_CAMERA_SOURCE_NOT_AVAILABLE');const blob=await response.blob();
    fail(await sha(await blob.arrayBuffer())===p.source.pixel_png_sha256,'FULL_PL_CAMERA_SOURCE_SHA');visual=await createImageBitmap(blob);
   }
   if(ticket!==generation){visual.close?.();return false;}
   ui.stage.draw(0,raw,rendered.receipt,meta,{input:visual,flow:flowCanvas(p),flowValues:p.flow===null?new Float32Array(1442).fill(NaN):new Float32Array(p.flow.flat())},0,live);
   visual.close?.();
   const inputCaption=inputMode.value==='binary'?'721六边形 · 显示阈值≥0.5':inputMode.value==='gray'?'721六边形 · 实际灰度':'矩形原始画面';
   ui.stage.c.fillStyle='#10212d';ui.stage.c.fillRect(350,794,308,140);
   ui.stage.text(inputCaption,365,824,18,'#b8e7eb');
   ui.stage.text(inputMode.value==='binary'?'仅显示二值化':'同一run / 同一步输入',365,856,16,'#9db7c4');
   if(inputMode.value==='binary')ui.stage.text('计算仍使用原始灰度输入',365,884,16,'#9db7c4');
   Object.assign(ui.stage.canvas.dataset,{inputDisplayMode:inputMode.value,inputDisplayThreshold:inputMode.value==='binary'?'0.5':'NONE',inputDisplaySha256:p.input_sha256,inputDisplayStep:String(p.step_id)});
   lastInputStatus=status;lastDrawnPacket=p;drawGroups(ui.stage,p,anchor,groupHistory);drawMotionSummary(ui.stage,p);
   ui.stage.text(`${p.offline_replay?playbackRange().label+' · OFFLINE REPLAY · ':''}${p.plan_metadata?.condition_id||'本次输入'} · k${p.step_id} · 输入 ${p.input_time_s.toFixed(3)}s → 活动 ${p.activity_time_s.toFixed(3)}s`,210,62,20,'#a9c2cd');
   Object.assign(ui.stage.canvas.dataset,{session:p.session_id,stateToken:String(p.state_token),fullStateSha256:p.full_state_sha256,flowStateSha256:p.flow_binding?.full_state_sha256||'',flowStatus:p.flow_status,displayKind:p.offline_replay?'OFFLINE_REPLAY_FULL_PL_TRAJECTORY':ui.stage.canvas.dataset.displayKind,skeletonActivitySource:rendered.receipt.brightness_source,skeletonCentralROISigned:JSON.stringify(rendered.receipt.central_roi_signed),skeletonBrightness:JSON.stringify(rendered.receipt.type_states.map(s=>s.brightness_factor))});
   root.querySelector('.cp-heading').textContent=p.offline_replay?'本次已保存结果 · '+playbackRange().label+' · OFFLINE REPLAY · 5ms数学步长':liveStream?(status.status==='FINISHED'?'⑪ 本次完整PL计算已结束 · 保留最后状态':'⑪ 连续完整PL状态 · 整段轨迹待审计 · 不宣称实时PASS'):'⑪ 实体FPGA · 固定输入首步 · OFFLINE REPLAY · 当前未连接板卡';
   $('cpStatus').textContent=`${p.plan_metadata?.condition_id||'固定输入'} · 第${p.step_id+1}/${p.plan_metadata?.steps||'?'}步 · 模型输入 ${p.input_time_s.toFixed(3)}s → 活动 ${p.activity_time_s.toFixed(3)}s · 本步生产耗时 ${Number.isFinite(elapsed)?(elapsed*1000).toFixed(2)+'ms':'未测量'} · ${p.flow===null?'本步光流NOT_AVAILABLE':'同一步官方光流（CPU解码）'}。`;
   if(p.source.kind==='recorded_camera_flyvis')$('cpStatus').textContent+=` 录制输入 · 采集帧${p.source.source_frame} · ${p.source.capture_utc} · OFFLINE/FROZEN INPUT，非持续实时摄像头。`;
   if(p.source.kind==='real_windows_camera'){
    sourceLabel.textContent=status.status==='FINISHED'?'纯FPGA摄像头本次运行结束 · 保留真实已解码状态':'本次真实摄像头 → 完整网络FPGA → 官方光流 · CPU独立审核中';
    $('cpStatus').textContent=`实际运行 ${p.wall_elapsed_s.toFixed(2)} / 60秒 · 本帧采集 ${p.capture_elapsed_s.toFixed(3)}秒 · 第${p.step_id+1}步 · 模型输入 ${p.input_time_s.toFixed(3)}秒 → 活动 ${p.activity_time_s.toFixed(3)}秒（5ms数学步长；最高8步/实际秒展示档，非硬件上限） · 采集帧${p.source.source_frame} · ${p.source.capture_utc} · 同一步骨架与CPU官方光流。 ${status.stop_reason||''}`;
   }
   if(p.source.kind==='controlled_animation'){
    sourceLabel.textContent=status.status==='FINISHED'?'固定实验已结束；查看实际核验状态':'固定科学刺激 → 全网FPGA → 官方光流';
    $('cpStatus').textContent=`${p.condition_id} · 第${p.step_id+1}/485步 · 实际 ${p.wall_elapsed_s.toFixed(2)}秒 · 模型输入 ${p.input_time_s.toFixed(3)}秒 → 活动 ${p.activity_time_s.toFixed(3)}秒 · 严格FP32全状态独立审核 ${status.numerical_audit||(p.offline_replay?'已保存逐步审核通过':'PENDING')} · 不宣称实时。`;
   }
   state.textContent=`run ${p.run_id} · boot ${p.hardware.boot_id} · ${liveStream?`已接收${status.received_steps}步 / 绘制回执${status.browser_receipts}帧`:'已保存首步结果'} · 右侧/骨架：同一步中央37节点区域均值`;
   if(p.offline_replay){const r=playbackRange();sourceLabel.textContent=`${r.label} · 当前第${p.step_id}步 / 所选${r.start}–${r.end}步 · 原始485步保留 · OFFLINE REPLAY`;ui.stage.canvas.dataset.playbackWindow=JSON.stringify(r);fitReplayStage();}
   if(historyRun)state.textContent='已核验保存结果 · 485步 · 非新计算';
   if(p.source.kind==='board_ov5640'){
    ui.stage.canvas.dataset.displayKind='OFFLINE_OV5640_ONE_STEP';
    root.querySelector('.cp-heading').textContent='OV5640单帧一步 · 已保存结果 / OFFLINE REPLAY · '+p.evidence_level;
    sourceLabel.textContent='板端OV5640来源 · 单帧结果；不宣称持续采集或实时PASS';
    $('cpStatus').textContent='同一帧 → 721输入 → 完整45669状态逐字审核 → CPU官方光流。只有一步5ms模型时间，不能据此判断方向选择性或连续速度。'+(p.source.color_order_verified?'':' 相机色序尚未实物色条确认。')+' 证据：'+p.evidence_level;
    state.textContent='本机接收身份 '+p.run_id+' · 原始板端身份与审核见展开信息；没有运行新GPU推理';
   }
   if(!panel.querySelector('details')){const detail=document.createElement('details'),summary=document.createElement('summary'),identity=document.createElement('pre');summary.textContent='当前状态身份与带符号活动';identity.id='cpFullPLIdentity';detail.append(summary,identity);panel.append(detail);}
   $('cpFullPLIdentity').textContent=JSON.stringify({run:p.run_id,session:p.session_id,step:p.step_id,hardware:p.hardware,model:p.model,input_sha256:p.input_sha256,full_state_sha256:p.full_state_sha256,signed_means:p.signed_means,central_roi:roiDefinition,central_roi_signed:groupSample(p).raw,central_curve:'max(mean(37 signed raw states),0); no baseline subtraction',flow:p.flow_status,transport_profile:p.transport_profile,initial_state_readback:p.initial_state_readback,cycle_definition:p.cycle_definition,source_audit:p.source_audit,brightness_source:rendered.receipt.brightness_source,brightness_factors:rendered.receipt.type_states.map(s=>s.brightness_factor),storage:status?.storage_policy||'SAVED_FIRST_STEP_ZIP'},null,2);
   return true;
  }
  async function drawReplay(step,ticket){
   await prepare();const r=await json('/api/full-pl-stream/replay?step='+step);await validateStream(r.frame,r.status,anchor,health);
   if(ticket!==generation)return;const windowRange=playbackRange(),offset=r.frame.plan_metadata?.input_time_offset_s||0;
   groupHistory.bounds={startStep:windowRange.start,startTime:(windowRange.start+1)*.005+offset,endTime:(windowRange.end+1)*.005+offset};
   enter();await draw(r.frame,r.status,ticket);seek.value=step;replayStep=step;
  }
  seek.oninput=async()=>{replaying=false;replay.textContent='▶ 播放所选区间 · OFFLINE REPLAY';const ticket=++generation;
   try{await drawReplay(Number(seek.value),ticket);}catch(e){if(ticket===generation){blank('NOT_AVAILABLE · 回放已撤销');state.textContent=e.message;}}
  };
  replay.onclick=async()=>{
   if(replaying){replaying=false;generation++;replay.textContent='继续回放本次结果 · OFFLINE REPLAY';return;}
   replaying=true;streaming=false;const selectedRange=playbackRange(),ticket=++generation,startStep=replayStep<selectedRange.start||replayStep>=selectedRange.end?selectedRange.start:replayStep;replay.textContent='Ⅱ 暂停回放';
   try{await drawReplay(startStep,ticket);const begin=performance.now();
    while(replaying&&ticket===generation&&replayStep<selectedRange.end){await new Promise(r=>setTimeout(r,1000/12.125));
     const step=Math.min(selectedRange.end,Math.max(replayStep+1,startStep+Math.floor((performance.now()-begin)*12.125/1000)));
     await drawReplay(step,ticket);if(step===selectedRange.end)break;}
   }catch(e){if(ticket===generation){blank('NOT_AVAILABLE · 回放已撤销');state.textContent=e.message;}}
   if(ticket===generation){replaying=false;replay.textContent='▶ 播放所选区间 · OFFLINE REPLAY';}
  };
  restart.onclick=async()=>{generation++;replaying=false;streaming=false;const r=playbackRange();replayStep=r.start;seek.min=r.start;seek.max=r.end;seek.value=r.start;groupHistory.run=null;groupHistory.samples.clear();await replay.onclick();};
  range.onchange=async()=>{await restart.onclick();};
  show.onclick=async()=>{const ticket=++generation;streaming=false;show.disabled=true;watch.disabled=false;
   try{await prepare();await validate(anchor,saved,health);if(ticket!==generation)return;enter();await draw(anchor,null,ticket);}
   catch(e){enter();blank('NOT_AVAILABLE · 本次显示已撤销');state.textContent=e.message;}
  };
  watch.onclick=async()=>{
   const ticket=++generation;streaming=true;replaying=false;revision=-1;groupHistory.bounds=null;show.disabled=false;watch.disabled=true;enter();blank('等待同一run/boot的后续完整PL状态…');root.querySelector('.cp-heading').textContent='等待⑪连续完整PL状态 · 尚未收到本次新结果';
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
      if(s.display_complete&&(!stream.camera_live||s.replay_available===true)){restart.hidden=false;replay.hidden=false;range.hidden=false;axis.hidden=false;seek.hidden=false;}return;}
     await new Promise(resolve=>setTimeout(resolve,Math.max(0,1000/(stream.camera_live?5:12)-(performance.now()-begin))));
    }
   }catch(e){if(ticket===generation){streaming=false;blank('NOT_AVAILABLE · 连续状态显示已撤销');state.textContent=e.message+'；没有回退旧活动。';watch.disabled=false;}}
  };
  if(stream.source_kind==='board_ov5640'){
   show.hidden=true;watch.hidden=true;axis.hidden=false;
   try{await prepare();await validateOV(anchor,stream,health);enter();await draw(anchor,stream,generation);
    const monitor=setInterval(async()=>{try{const current=await json('/api/full-pl-stream/status');
     if(!current.result_valid||current.session_id!==anchor.session_id||current.run_id!==anchor.run_id){clearInterval(monitor);blank('OV5640结果已撤销 · NOT_AVAILABLE');state.textContent=current.error||'OV5640_IDENTITY_CHANGED';}
    }catch(e){clearInterval(monitor);blank('OV5640结果连接中断');state.textContent=e.message;}},1500);
   }
   catch(e){enter();blank('OV5640结果显示未通过 · NOT_AVAILABLE');state.textContent=e.message;}
  }
  else if(historyRun&&stream.display_complete){restart.hidden=false;replay.hidden=false;range.hidden=false;axis.hidden=false;seek.hidden=false;show.hidden=true;watch.hidden=true;await restart.onclick();}
  else if(stream.configured&&stream.first_step_accepted)watch.onclick();
 }
 setup().catch(e=>{if(historyRun){ui.enterLive();ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text('保存结果未通过核验 · '+e.message,60,130,24);$('cpStatus').textContent=e.message;}}); // Optional ingress must never block old55/offline startup.
})();
