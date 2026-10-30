/* One input/backend picker in the existing workbench. Never fabricates results. */
(() => {
 'use strict';
 const box=document.createElement('section');box.className='controls';box.id='operatorSelection';
 box.innerHTML='<strong>本次输入与计算</strong><label>输入 <select id="opInput"><option value="camera">真实摄像头</option><option value="scientific28">28条件固定实验</option></select></label><label>计算 <select id="opBackend" disabled><option value="FULL_FPGA">纯FPGA · 全45669节点</option></select></label><label id="opConditionLabel" hidden>条件 <select id="opCondition"></select></label><button id="opPreview" hidden>预览所选动画</button><button id="opSelect">打开所选实验</button><button id="opStart" hidden disabled>开始本次计算</button><button id="opStop" hidden disabled>停止本次计算</button><button id="opClose">关闭实验台</button><a id="opNotebook" hidden>下载固定Notebook</a><span id="opHint">读取选项…</span>';
 const drawer=document.createElement('section');drawer.id='opDrawer';
 drawer.innerHTML='<div id="opDrawerContent"><h1>实验设置</h1><div id="opPrimary"></div><div id="opReplay"></div><div id="opAdvanced" hidden></div></div>';
 document.body.prepend(drawer);document.getElementById('opPrimary').append(box);
 document.body.classList.add('operator-unified');
 function collectPreview(){
  const tools=document.getElementById('cpLiveTools');
  if(tools)document.getElementById('opAdvanced').append(tools);
  const options=document.getElementById('cpOptions');if(options)options.hidden=true;

  const preview=document.getElementById('cpStimuli28Controls');
  if(preview){document.getElementById('opReplay').append(preview);
   document.getElementById('cpStimuli28Open').textContent='预览已有动画 / GPU离线结果';
   const pick=document.getElementById('cpStimuli28Condition');
   pick.addEventListener('change',()=>{document.getElementById('opInput').value='scientific28';document.getElementById('opCondition').value=pick.value;changed();});
  }
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',collectPreview,{once:true});else collectPreview();
 const $=id=>document.getElementById(id);let current=null,managed=false,ownerId=null;
 const labels={RIGHT:'右',LEFT:'左',UP:'上',DOWN:'下'};
 const ovOption=document.createElement('option');ovOption.value='ov5640';ovOption.textContent='OV5640板端 · 单帧验收（非60秒）';$('opInput').append(ovOption);
 function changed(){const fixed=$('opInput').value==='scientific28';$('opConditionLabel').hidden=!fixed;$('opPreview').hidden=!fixed;}
 $('opInput').addEventListener('change',changed);
 $('opPreview').addEventListener('click',async()=>{
  const open=$('cpStimuli28Open'),pick=$('cpStimuli28Condition');
  if(!open||!pick){$('opHint').textContent='动画读取器尚未就绪，请稍候。';return;}
  await open.onclick();
  if(!pick.hidden&&Array.from(pick.options).some(o=>o.value===$('opCondition').value)){
   pick.value=$('opCondition').value;pick.onchange();
  }
 });
 async function load(){try{
  const r=await fetch('/api/operator-selection'),m=await r.json();if(!r.ok)throw Error(m.error);
  managed=m.managed;current=m.selection;ownerId=m.owner?.root_id||null;heartbeat();$('opClose').disabled=!managed;
  for(const c of m.catalogue.conditions){const o=document.createElement('option');o.value=c.condition_id;
   const direction=c.condition_id.split('_').find(x=>labels[x]);
   const family=c.condition_id.startsWith('DOT_')?'小目标':c.condition_id.includes('EDGE_')?(c.condition_id.includes('_OFF_')?'暗边缘':'亮边缘'):'亮条';
   const motion=direction?labels[direction]:c.condition_id==='DOT_CCW'?'逆时针':c.condition_id==='DOT_CW'?'顺时针':'';
   o.textContent=family+' '+motion+(c.stationary?' · 静止/空白对照':'')+' · '+c.condition_id;$('opCondition').append(o);}
  if(current&&current.backend!=='FULL_FPGA'){throw Error('检测到旧GPU＋FPGA会话，未改标为纯FPGA。请按原流程正常结束并关闭，再从原入口打开；新实验仅使用纯FPGA。');}
  if(current){$('opInput').value=current.input;$('opBackend').value=current.backend;if(current.condition)$('opCondition').value=current.condition;}
  changed();$('opSelect').disabled=!managed;
  $('opHint').textContent=!managed?'请正常关闭后，从“flyvis_96b7ca62.cmd”进入此选择流程。':current?
   '当前选择已打开；运行对应固定Notebook，准备好后在这里点开始。第一次上传新版即可，以后换条件不改代码。':'选输入和后端，再打开。此操作不加载或复位板卡。';
  if(new URLSearchParams(location.search).has('replay_run')){
   document.body.classList.add('full-pl-replay');$('opStart').hidden=$('opStop').hidden=$('opNotebook').hidden=true;
   $('opInput').value='scientific28';$('opBackend').value='FULL_FPGA';$('opSelect').textContent='返回新实验设置';
   for(const id of ['opInput','opBackend','opCondition'])$(id).disabled=true;
   const r=await fetch('/api/full-pl-history'),data=await r.json(),saved=data.results?.find(item=>item.run_id===new URLSearchParams(location.search).get('replay_run'));
   if(!r.ok||!saved)throw Error(data.error||'未找到这次保存结果');$('opCondition').value=saved.condition_id;
   const selected=Array.from($('opCondition').options).find(o=>o.value===saved.condition_id);
   $('opHint').textContent='纯FPGA · '+(selected?.textContent||saved.condition_id)+' · 已保存结果 / OFFLINE REPLAY · 无需板卡';
   dispatchEvent(new Event('resize'));return;
  }
  if(current){for(const id of ['cpJointControls','cpLiveControls']){const legacy=$(id);if(legacy)legacy.style.display='none';}$('opStart').hidden=$('opStop').hidden=false;poll();$('opNotebook').hidden=false;$('opNotebook').href='/api/operator-selection/notebook';$('opNotebook').download=current.backend==='GPU_FPGA'?'FlyVis摄像头联合实验.ipynb':'FlyVis纯FPGA_ON60实验.ipynb';}
 }catch(e){$('opHint').textContent='选择不可用：'+e.message;$('opSelect').disabled=true;}}
 $('opSelect').addEventListener('click',async()=>{if(new URLSearchParams(location.search).has('replay_run')){location.href='/#competition';return;}try{
  $('opSelect').disabled=true;
  const body={input:$('opInput').value,backend:'FULL_FPGA',condition:$('opInput').value==='scientific28'?$('opCondition').value:null};
  const r=await fetch('/api/operator-selection',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),v=await r.json();
  if(!r.ok)throw Error(v.error);$('opHint').textContent='正在正常关闭当前入口并打开所选实验，请稍候…';
  transition(v.selection||body);
 }catch(e){$('opHint').textContent=e.message;$('opSelect').disabled=false;}});
 function transition(selection){
  // Keep the real interface visible; never navigate to a blob/inline-script page.
  const workspace=$('competitionWorkspace');if(workspace)workspace.hidden=true;
  managed=false; // Old session heartbeats must not touch the replacement session.
  for(const id of ['opInput','opBackend','opCondition','opPreview','opStart','opStop','opClose'])$(id).disabled=true;
  let attempts=0;
  $('opHint').textContent='正在准备所选后端，请稍候；尚未加载板卡或开始计算。';
  async function wait(){
   const controller=new AbortController(),deadline=setTimeout(()=>controller.abort(),5000);
   try{
    const r=await fetch('/api/operator-selection',{cache:'no-store',signal:controller.signal}),v=await r.json();
    if(r.ok&&v.owner?.root_id&&v.owner.root_id!==ownerId&&!v.owner.closing&&v.selection&&['backend','input','condition'].every(k=>v.selection[k]===selection[k])){
     $('opHint').textContent='电脑端已就绪，正在更新本页；下一步运行对应固定Notebook。';
     if(new URLSearchParams(location.search).has('replay_run'))location.href=location.pathname+'#competition';else location.reload();return;
    }
   }catch(e){}finally{clearTimeout(deadline);}
   if(++attempts<60)setTimeout(wait,1000);
   else $('opHint').textContent='电脑端未在等待期限内就绪，尚未确认切换成功。请保留此页和Notebook现场，不重复提交。';
  }
  setTimeout(wait,500);
 }

 let status=null;
 async function poll(){if(!managed)return;try{
  const path=current.backend==='GPU_FPGA'?'/api/joint-camera/status':'/api/full-pl-stream/status';
  const r=await fetch(path);status=await r.json();if(!r.ok)throw Error(status.error);
  if(current.input==='ov5640'){
   $('opStart').hidden=$('opStop').hidden=true;
   $('opNotebook').download='flyvis_ov5640单帧验收.ipynb';
   $('opSelect').disabled=['WAITING_CAPTURE','AUDITING','FAILED','FINISHED'].includes(status.status);
   $('opHint').textContent='OV5640板端 · 单帧一步 · '+({WAITING_FIRST_STEP:'请下载并手动运行固定Notebook；先核对实物条件',WAITING_CAPTURE:'板端已由你授权，等待结果；请勿切换实验或关内核',AUDITING:'真实保存结果审核/官方光流解码中',FINISHED:'审核完成；下方显示本次单帧结果，非连续视频',FAILED:'失败，保留板端内核与DDR，不自动重试'}[status.status]||status.status)+(status.error?' · '+status.error:'');
   setTimeout(poll,1000);return;
  }
  $('opStart').disabled=current.backend==='GPU_FPGA'?!status.can_start:!status.ready_to_start;
  $('opStop').disabled=current.backend==='GPU_FPGA'?!['RUNNING','GPU_PREPARING'].includes(status.workbench_phase):!(status.start_requested||status.ready_to_start)||['FINISHED','FAILED','STOPPED'].includes(status.status);
  if(current.backend==='FULL_FPGA'&&status.start_requested)$('opSelect').disabled=!(status.display_complete&&status.normal_end_ack);
  $('opStart').textContent=current.input==='scientific28'?'开始本条件 · 485步':'开始摄像头 · 60秒';
  const phases={WAIT_BOARD_PREPARATION:'请运行对应固定Notebook',BOARD_PREPARING:'正在准备板端',READY_TO_START:'准备完成，可以开始',START_REQUESTED:'已请求开始',GPU_PREPARING:'正在准备GPU',RUNNING:'实际计算中',AUDITING:'正在保存与核验',COMPLETE:'已结束，可再次开始',FAILED:'失败，请保留现场'};
  const phase=current.backend==='GPU_FPGA'?(phases[status.workbench_phase]||status.workbench_phase):(status.ready_to_start?'准备完成，可以开始':status.status==='WAITING_FIRST_STEP'?(status.start_requested?'已请求开始，等待首步核验':'请运行固定Notebook并等待准备'):status.status==='FINISHED'?(status.display_complete?(status.normal_end_ack?'正常结束，可选择下一实验；同一Notebook无需关内核':'审核完成，等待板端正常收尾；请勿关闭内核'):'计算已结束，等待审核与解码'):status.status);
  $('opHint').textContent=(current.input==='scientific28'?current.condition:'真实摄像头')+' · '+phase+' · 已提交/接收 '+(status.committed_steps||status.received_steps||0)+' 步'+(status.run_id?' · run '+status.run_id:'')+(status.error?' · '+status.error:'');

 }catch(e){$('opStart').disabled=true;$('opHint').textContent='电脑后台连接中断：'+e.message+'。请保留板端现场；此时不是神经计算成功。';}setTimeout(poll,1000);}
 $('opStart').addEventListener('click',async()=>{try{
  $('opStart').disabled=true;
  if(current.backend==='GPU_FPGA'){
   const b=$('cpJointStart');if(!b||b.disabled)throw Error('请等待原联合控制器准备完成');b.click();
  }else{
   if(!window.FlyVisFullPLBegin)throw Error('本次显示接口尚未就绪，请稍候');
   window.FlyVisFullPLBegin();
   const r=await fetch('/api/full-pl-stream/camera-start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({preparation_id:status.preparation_id})}),v=await r.json();if(!r.ok)throw Error(v.error);
  }
  
  $('opHint').textContent='已请求开始；下面只显示本次实际提交的状态，整轮待核验。';
 }catch(e){$('opHint').textContent=e.message;}});
 $('opStop').addEventListener('click',async()=>{try{
  const gpu=current.backend==='GPU_FPGA',path=gpu?'/api/joint-camera/stop':'/api/full-pl-stream/camera-stop',body=gpu?{}:{preparation_id:status.preparation_id};
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),v=await r.json();if(!r.ok)throw Error(v.error);
  $('opHint').textContent='已请求停止；等待在途步骤完成、保存和核验，再切换实验。';
 }catch(e){$('opHint').textContent=e.message;}});
 $('opClose').addEventListener('click',async()=>{try{const r=await fetch('/api/operator-selection/close',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}),v=await r.json();if(!r.ok)throw Error(v.error);$('opHint').textContent='正在正常关闭后台；完成后可关闭页面。';$('opClose').disabled=true;}catch(e){$('opHint').textContent=e.message;}});
 function heartbeat(){if(!managed||!ownerId)return;fetch('/api/operator-selection/heartbeat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({root_id:ownerId})}).catch(()=>{});}
 setInterval(heartbeat,3000);
 window.addEventListener('pagehide',()=>{if(managed&&ownerId&&navigator.sendBeacon)navigator.sendBeacon('/api/operator-selection/detach',new Blob([JSON.stringify({root_id:ownerId})],{type:'application/json'}));});
 load();
})();
