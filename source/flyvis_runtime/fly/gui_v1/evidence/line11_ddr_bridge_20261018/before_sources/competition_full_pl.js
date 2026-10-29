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
  fail(p.step_id===0&&p.state_token===1&&p.input_time_s===0&&p.activity_time_s===.005&&p.hardware.completed_steps===1&&p.hardware.faults===0,'FULL_PL_STEP');
  fail(p.flow===null&&p.flow_status==='NOT_AVAILABLE_NOT_DECODED','FULL_PL_NO_BORROWED_FLOW');
  await arrays(p,h);
 }
 async function validateStream(p,s,anchor,h){
  fail(s.first_step_accepted&&['RECEIVING','FINISHED'].includes(s.status)&&s.result_valid,'FULL_PL_STREAM_NOT_VALID');
  fail(p.schema==='flyvis-full-pl-stream-display/v1'&&p.backend==='FULL_NETWORK_FPGA'
   &&p.run_id===s.run_id&&p.run_id===anchor.run_id&&p.session_id===s.session_id&&p.hardware.boot_id===s.boot_id,'FULL_PL_STREAM_IDENTITY');
  fail(p.anchor_archive_sha256===anchor.archive_sha256&&['bit_sha256','hwh_sha256','boot_id','clock_hz'].every(k=>p.hardware[k]===anchor.hardware[k]),'FULL_PL_STREAM_ANCHOR');
  fail(Number.isSafeInteger(p.step_id)&&p.step_id>=1&&p.state_token===p.step_id+1&&p.serial===p.state_token
   &&p.hardware.completed_steps===p.state_token&&p.hardware.faults===0&&p.input_time_s===p.step_id*.005
   &&p.activity_time_s===(p.step_id+1)*.005,'FULL_PL_STREAM_STEP');
  fail(p.display_kind===(s.status==='RECEIVING'?'CURRENT_FULL_PL_STATE_PENDING_AUDIT':'FINISHED_FULL_PL_LAST_STATE'),'FULL_PL_STREAM_LABEL');
  await arrays(p,h);
  if(p.flow===null){fail(p.flow_status==='NOT_AVAILABLE_NOT_DECODED','FULL_PL_FLOW_MISSING');return;}
  const b=p.flow_binding;
  fail(p.flow_status==='OFFICIAL_DECODER_SAME_STATE'&&b.run_id===p.run_id&&b.session_id===p.session_id
   &&b.frame_id===p.step_id&&b.full_state_sha256===p.full_state_sha256&&b.decoder==='DecoderGAVP'&&b.recursive_eval===true,'FULL_PL_FLOW_BINDING');
  fail(p.flow.length===2&&p.flow.every(a=>a.length===721&&a.every(Number.isFinite)),'FULL_PL_FLOW_ARRAY');
  fail(await sha(new Float32Array(p.flow.flat()).buffer)===p.flow_sha256,'FULL_PL_FLOW_SHA');
 }
 window.FlyVisFullPLProtocol={validate,validateStream};
 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id);
 async function setup(){
  const [saved,stream]=await Promise.all([json('/api/full-pl/status'),json('/api/full-pl-stream/status')]);
  if(!saved.configured&&!stream.configured)return;
  const panel=document.createElement('div');panel.className='cp-player';panel.id='cpFullPL';
  const show=document.createElement('button'),watch=document.createElement('button'),back=document.createElement('button'),state=document.createElement('span');
  show.textContent='查看⑪已验收的完整首步';watch.textContent='接收并显示连续状态';watch.hidden=!stream.configured;back.textContent='返回原离线演示';back.hidden=true;
  panel.append(show,watch,back,state);ui.stage.host.before(panel);
  if(stream.configured&&stream.first_step_accepted){const link=document.createElement('a');link.href='/api/full-pl-stream/link.zip';link.textContent='下载本次板端显示连接包';panel.append(link);}
  if(saved.status!=='VERIFIED_SAVED_FIRST_STEP'){show.disabled=true;watch.disabled=true;state.textContent='NOT_AVAILABLE · '+(saved.error||'首步结果未通过');return;}
  state.textContent='首步45,669状态逐字核对通过 · 连续轨迹独立审计待完成';
  let hidden=[],heading='',callbacks,entered=false,generation=0,revision=-1,projection,health,anchor,streaming=false;
  function clearStreamIdentity(){for(const k of ['session','stateToken','fullStateSha256','flowStateSha256','flowStatus','run','frame','inputTime','activityTime','means'])delete ui.stage.canvas.dataset[k];}
  function blank(text){ui.stage.clearGuide();ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text(text,60,130,30);clearStreamIdentity();ui.stage.canvas.dataset.displayKind='NOT_AVAILABLE';}
  function enter(){
   if(entered)return;ui.enterLive();entered=true;heading=root.querySelector('.cp-heading').innerHTML;
   for(const el of [root.querySelector('.cp-player'),$('cpLiveControls'),$('cpJointControls'),$('cpAnalysis'),$('cpSpatialDetails'),$('cpPolicyNotice'),$('cpReceipt').parentElement])if(el&&el!==panel){hidden.push([el,el.hidden]);el.hidden=true;}
   callbacks={onPlay:ui.stage.onPlay,onSeek:ui.stage.onSeek,onCamera:ui.stage.onCamera};ui.stage.onPlay=null;ui.stage.onSeek=null;ui.stage.onCamera=null;
   back.hidden=false;
  }
  back.onclick=async()=>{
   generation++;streaming=false;for(const [el,value] of hidden)el.hidden=value;hidden=[];back.hidden=true;show.disabled=false;watch.disabled=false;
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
   const live={backend:p.backend,stream:liveStream,finished:status?.status==='FINISHED',sourceKind:liveStream?'line11_frame_input':'line11_fixed_frame0',step:p.step_id,sourceSequence:p.source.sequence,wallElapsed:elapsed,clock:{mode:liveStream?'FULL_PL_STEP_DRIVEN':'SAVED_RESULT'}};
   ui.stage.draw(0,raw,rendered.receipt,meta,{input:inputCanvas(p),flow:flowCanvas(p),flowValues:p.flow===null?new Float32Array(1442).fill(NaN):new Float32Array(p.flow.flat())},0,live);
   Object.assign(ui.stage.canvas.dataset,{session:p.session_id,stateToken:String(p.state_token),fullStateSha256:p.full_state_sha256,flowStateSha256:p.flow_binding?.full_state_sha256||'',flowStatus:p.flow_status});
   root.querySelector('.cp-heading').textContent=liveStream?(status.status==='FINISHED'?'⑪ 本次完整PL计算已结束 · 保留最后状态':'⑪ 连续完整PL状态 · 整段轨迹待审计 · 不宣称实时PASS'):'⑪ 实体FPGA · 固定输入首步 · OFFLINE REPLAY · 当前未连接板卡';
   $('cpStatus').textContent=`第${p.step_id}步 · 模型输入 ${p.input_time_s.toFixed(3)}s → 活动 ${p.activity_time_s.toFixed(3)}s · 本步生产耗时 ${(elapsed*1000).toFixed(2)}ms · ${p.flow===null?'本步光流NOT_AVAILABLE':'同一步官方光流'}。`;
   state.textContent=`run ${p.run_id} · boot ${p.hardware.boot_id} · ${liveStream?`已接收${status.received_steps}步 / 绘制回执${status.browser_receipts}帧`:'已保存首步结果'} · 每类721节点真实均值`;
   if(!panel.querySelector('details')){const detail=document.createElement('details'),summary=document.createElement('summary'),identity=document.createElement('pre');summary.textContent='当前状态身份与带符号活动';identity.id='cpFullPLIdentity';detail.append(summary,identity);panel.append(detail);}
   $('cpFullPLIdentity').textContent=JSON.stringify({run:p.run_id,session:p.session_id,step:p.step_id,hardware:p.hardware,model:p.model,input_sha256:p.input_sha256,full_state_sha256:p.full_state_sha256,signed_means:p.signed_means,flow:p.flow_status,storage:status?.storage_policy||'SAVED_FIRST_STEP_ZIP'},null,2);
   return true;
  }
  show.onclick=async()=>{const ticket=++generation;streaming=false;show.disabled=true;watch.disabled=false;
   try{await prepare();await validate(anchor,saved,health);if(ticket!==generation)return;enter();await draw(anchor,null,ticket);}
   catch(e){enter();blank('NOT_AVAILABLE · 本次显示已撤销');state.textContent=e.message;}
  };
  watch.onclick=async()=>{
   const ticket=++generation;streaming=true;revision=-1;show.disabled=false;watch.disabled=true;enter();blank('等待同一run/boot的后续完整PL状态…');root.querySelector('.cp-heading').textContent='等待⑪连续完整PL状态 · 尚未收到本次新结果';
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
     if(s.status==='FINISHED'){streaming=false;watch.disabled=false;return;}
     await new Promise(resolve=>setTimeout(resolve,Math.max(0,1000/12-(performance.now()-begin))));
    }
   }catch(e){if(ticket===generation){streaming=false;blank('NOT_AVAILABLE · 连续状态显示已撤销');state.textContent=e.message+'；没有回退旧活动。';watch.disabled=false;}}
  };
  if(stream.configured&&stream.first_step_accepted)watch.onclick();
 }
 setup().catch(()=>{}); // Optional ingress must never block old55/offline startup.
})();
