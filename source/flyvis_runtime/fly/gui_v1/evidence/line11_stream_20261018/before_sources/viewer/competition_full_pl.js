/* One saved, independently verified full-PL state in the original stage. */
(() => {
 'use strict';
 const fail=(ok,message)=>{if(!ok)throw Error(message);};
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 async function json(path){const r=await fetch(path),p=await r.json();if(!r.ok)throw Error(p.error||'FULL_PL_HTTP_'+r.status);return p;}
 async function validate(p,s,h){
  fail(s.status==='VERIFIED_SAVED_FIRST_STEP'&&p.schema==='flyvis-full-pl-first-step-display/v1','FULL_PL_NOT_VERIFIED');
  fail(p.run_id===s.run_id&&p.hardware.boot_id===s.boot_id&&p.archive_sha256===s.archive_sha256,'FULL_PL_RUN_BINDING');
  fail(p.backend==='FULL_NETWORK_FPGA'&&p.display_kind==='OFFLINE_REPLAY_FULL_NETWORK_FPGA'&&p.board_connection==='NOT_CONNECTED','FULL_PL_DISPLAY_KIND');
  fail(p.step_id===0&&p.state_token===1&&p.input_time_s===0&&p.activity_time_s===.005&&p.hardware.completed_steps===1&&p.hardware.faults===0,'FULL_PL_STEP');
  fail(p.flow===null&&p.flow_status==='NOT_AVAILABLE_NOT_DECODED','FULL_PL_NO_BORROWED_FLOW');
  fail(p.spatial.map_sha256===h.projection_cache.upstream_map_sha256,'FULL_PL_MAP');
  for(const [values,n,expected] of [[p.input_hex,721,p.input_sha256],[p.spatial.values,5768,p.spatial.values_sha256]]){
   fail(values.length===n&&values.every(Number.isFinite),'FULL_PL_ARRAY');
   fail(await sha(new Float32Array(values).buffer)===expected,'FULL_PL_ARRAY_SHA');
  }
 }
 window.FlyVisFullPLProtocol={validate};
 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id);
 async function setup(){
  const s=await json('/api/full-pl/status');if(!s.configured)return;
  const panel=document.createElement('div');panel.className='cp-player';panel.id='cpFullPL';
  const show=document.createElement('button'),back=document.createElement('button'),state=document.createElement('span');
  show.textContent='查看⑪已验收的完整首步';back.textContent='返回原离线演示';back.hidden=true;
  panel.append(show,back,state);ui.stage.host.before(panel);
  if(s.status!=='VERIFIED_SAVED_FIRST_STEP'){show.disabled=true;state.textContent='NOT_AVAILABLE · '+(s.error||'首步结果未通过');return;}
  state.textContent='已保存实体PL首步 · 45,669状态逐字核对 · 非实时连接';
  let hidden=[],heading='',callbacks,entered=false;
  back.onclick=async()=>{for(const [el,value] of hidden)el.hidden=value;hidden=[];back.hidden=true;show.disabled=false;
   if(callbacks)Object.assign(ui.stage,callbacks);root.querySelector('.cp-heading').innerHTML=heading;entered=false;await ui.leaveLive();};
  show.onclick=async()=>{
   show.disabled=true;
   try{
    const p=await json('/api/full-pl/frame'),h=await json('/api/full-pl/projection');await validate(p,s,h);
    const projection=await FlyVisFixedSkeleton.load(h),rendered=await projection.render(p,'saved-'+p.run_id);
    const raw=document.createElement('canvas');raw.width=rendered.width;raw.height=rendered.height;
    raw.getContext('2d').putImageData(new ImageData(rendered.pixels,raw.width,raw.height),0,0);
    const input=document.createElement('canvas'),flow=document.createElement('canvas');for(const c of [input,flow]){c.width=400;c.height=340;}
    // The actual input order uses the same frozen coordinate table as old replay.
    const uv=h.coordinates_uv;fail(uv?.length===721,'FULL_PL_INPUT_COORDINATES');
    const c=input.getContext('2d'),scale=5.5;c.fillStyle='#08111b';c.fillRect(0,0,400,340);
    uv.forEach(([u,v],i)=>{const x=200+1.5*v*scale,y=170+Math.sqrt(3)*(u+v/2)*scale;
     c.beginPath();for(let j=0;j<6;j++){const a=j*Math.PI/3,jx=x+Math.cos(a)*scale,jy=y+Math.sin(a)*scale;j?c.lineTo(jx,jy):c.moveTo(jx,jy);}c.closePath();
     const g=Math.round(Math.min(1,Math.max(0,p.input_hex[i]))*255);c.fillStyle=`rgb(${g},${g},${g})`;c.fill();});
    const f=flow.getContext('2d');f.fillStyle='#091523';f.fillRect(0,0,400,340);f.fillStyle='#c9e0e5';f.font='18px sans-serif';f.fillText('NOT_AVAILABLE',35,115);f.fillText('本次首步尚未运行官方解码',35,145);
    ui.enterLive();entered=true;heading=root.querySelector('.cp-heading').innerHTML;
    for(const el of [root.querySelector('.cp-player'),$('cpLiveControls'),$('cpJointControls'),$('cpAnalysis'),$('cpSpatialDetails'),$('cpPolicyNotice'),$('cpReceipt').parentElement]){if(el&&el!==panel){hidden.push([el,el.hidden]);el.hidden=true;}}
    callbacks={onPlay:ui.stage.onPlay,onSeek:ui.stage.onSeek,onCamera:ui.stage.onCamera};ui.stage.onPlay=null;ui.stage.onSeek=null;ui.stage.onCamera=null;
    const meta={run_id:p.run_id,types:rendered.receipt.types,means:[rendered.receipt.means],coordinates_uv:uv,input_time_s:[0],activity_time_s:[.005]};
    const live={backend:p.backend,sourceKind:'line11_fixed_frame0',step:0,sourceSequence:0,wallElapsed:s.timing.input_seconds+s.timing.step_call_seconds+s.timing.readback_seconds,clock:{mode:'SAVED_RESULT'}};
    ui.stage.draw(0,raw,rendered.receipt,meta,{input,flow,flowValues:new Float32Array(1442).fill(NaN)},0,live);
    root.querySelector('.cp-heading').textContent='⑪ 实体FPGA · 固定输入首步 · OFFLINE REPLAY · 当前未连接板卡';
    $('cpStatus').textContent=`模型时间 0 → 0.005秒；核心 ${(p.hardware.compute_cycles/p.hardware.clock_hz*1000).toFixed(3)}ms；上传 ${(s.timing.input_seconds*1000).toFixed(2)}ms；读回 ${(s.timing.readback_seconds*1000).toFixed(2)}ms。仅首步，连续运行未开放。`;
    state.textContent=`run ${p.run_id} · 输入/初态/全状态/节点映射已核验 · 八类各721节点均值驱动骨架`;
    back.hidden=false;const identity=document.createElement('pre');identity.textContent=JSON.stringify({run:p.run_id,hardware:p.hardware,model:p.model,input_sha256:p.input_sha256,initial_sha256:p.initial_sha256,full_state_sha256:p.full_state_sha256,archive_sha256:p.archive_sha256,signed_means:p.signed_means},null,2);
    panel.querySelector('details')?.remove();const detail=document.createElement('details'),summary=document.createElement('summary');summary.textContent='本步原始身份与带符号活动';detail.append(summary,identity);panel.append(detail);
   }catch(e){state.textContent='本次显示失败：'+e.message+'；未使用旧活动替代。';
    if(entered){ui.stage.c.fillStyle='#08111b';ui.stage.c.fillRect(0,0,1920,1080);ui.stage.text('NOT_AVAILABLE · 本次显示已撤销',60,130,30);ui.stage.canvas.dataset.displayKind='NOT_AVAILABLE';back.hidden=false;}else show.disabled=false;}
  };
 }
 setup().catch(()=>{}); // Optional backend must never block the original offline GUI.
})();
