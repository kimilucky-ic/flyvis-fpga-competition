/* One input/backend picker in the existing workbench. Never fabricates results. */
(() => {
 'use strict';
 const box=document.createElement('section');box.className='controls';box.id='operatorSelection';
 box.innerHTML='<strong>新实验</strong><label>输入 <select id="opInput"><option value="camera">真实摄像头</option><option value="scientific28">28条件固定实验</option></select></label><label>计算 <select id="opBackend"><option value="GPU_FPGA">GPU＋FPGA · 5768节点交给PL</option><option value="FULL_FPGA">纯FPGA · 全45669节点</option></select></label><label id="opConditionLabel" hidden>条件 <select id="opCondition"></select></label><button id="opSelect">打开所选实验</button><button id="opStart" hidden disabled>开始本次计算</button><button id="opStop" hidden disabled>停止本次计算</button><button id="opClose">关闭实验台</button><a id="opNotebook" hidden>下载本后端固定Notebook</a><span id="opHint">读取选项…</span>';
 const host=document.getElementById('competitionWorkspace')||document.querySelector('main')||document.body;host.prepend(box);
 const $=id=>document.getElementById(id);let current=null,managed=false,ownerId=null;
 const labels={RIGHT:'右',LEFT:'左',UP:'上',DOWN:'下'};
 function changed(){const fixed=$('opInput').value==='scientific28';$('opConditionLabel').hidden=!fixed;}
 $('opInput').addEventListener('change',changed);
 async function load(){try{
  const r=await fetch('/api/operator-selection'),m=await r.json();if(!r.ok)throw Error(m.error);
  managed=m.managed;current=m.selection;ownerId=m.owner?.root_id||null;heartbeat();$('opClose').disabled=!managed;
  for(const c of m.catalogue.conditions){const o=document.createElement('option');o.value=c.condition_id;
   o.textContent=c.condition_id+(c.stationary?' · 静止/空白对照':'');$('opCondition').append(o);}
  if(current){$('opInput').value=current.input;$('opBackend').value=current.backend;if(current.condition)$('opCondition').value=current.condition;}
  changed();$('opSelect').disabled=!managed;
  $('opHint').textContent=!managed?'请正常关闭后，从“flyvis_96b7ca62.cmd”进入此选择流程。':current?
   '当前选择已打开；运行对应固定Notebook，准备好后在这里点开始。第一次上传新版即可，以后换条件不改代码。':'选输入和后端，再打开。此操作不加载或复位板卡。';
  if(current){const legacy=$('cpJointControls');if(legacy)legacy.style.display='none';$('opStart').hidden=$('opStop').hidden=false;poll();$('opNotebook').hidden=false;$('opNotebook').href='/api/operator-selection/notebook';$('opNotebook').download=current.backend==='GPU_FPGA'?'FlyVis摄像头联合实验.ipynb':'FlyVis纯FPGA_ON60实验.ipynb';}
 }catch(e){$('opHint').textContent='选择不可用：'+e.message;$('opSelect').disabled=true;}}
 $('opSelect').addEventListener('click',async()=>{try{
  $('opSelect').disabled=true;
  const body={input:$('opInput').value,backend:$('opBackend').value,condition:$('opInput').value==='scientific28'?$('opCondition').value:null};
  const r=await fetch('/api/operator-selection',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),v=await r.json();
  if(!r.ok)throw Error(v.error);$('opHint').textContent='正在正常关闭当前入口并打开所选实验，请稍候…';
  transition(v.selection||body);
 }catch(e){$('opHint').textContent=e.message;$('opSelect').disabled=false;}});
 function transition(selection){
  // Unload old polling/draw handlers before the backend handoff. The same tab
  // waits on a same-origin Blob page; no second viewer can send stale receipts.
  if(typeof Blob==='undefined'||typeof URL==='undefined'||!URL.createObjectURL||typeof location==='undefined')return;
  const origin=location.origin,target=origin+'/#competition';
  const script=`const expected=${JSON.stringify(selection)},origin=${JSON.stringify(origin)},target=${JSON.stringify(target)};let attempts=0;async function wait(){try{const r=await fetch(origin+'/api/operator-selection',{cache:'no-store'}),v=await r.json();if(r.ok&&v.selection&&['backend','input','condition'].every(k=>v.selection[k]===expected[k])){location.replace(target);return;}}catch(e){}if(++attempts<120)setTimeout(wait,1000);else document.getElementById('message').textContent='入口尚未就绪；请查看本机runtime/operator下的backend.log，不自动重跑。';}wait();`;
  const html='<!doctype html><meta charset="utf-8"><title>FlyVis · 切换实验</title><p id="message">正在正常切换原实验台，请稍候。此阶段不会加载板卡。</p><script>'+script+'<'+ '/script>';
  location.replace(URL.createObjectURL(new Blob([html],{type:'text/html'})));
 }
 let status=null;
 async function poll(){try{
  const path=current.backend==='GPU_FPGA'?'/api/joint-camera/status':'/api/full-pl-stream/status';
  const r=await fetch(path);status=await r.json();if(!r.ok)throw Error(status.error);
  $('opStart').disabled=current.backend==='GPU_FPGA'?!status.can_start:!status.ready_to_start;
  $('opStop').disabled=current.backend==='GPU_FPGA'?!['RUNNING','GPU_PREPARING'].includes(status.workbench_phase):!(status.start_requested||status.ready_to_start)||['FINISHED','FAILED','STOPPED'].includes(status.status);
  $('opStart').textContent=current.input==='scientific28'?'开始本条件 · 485步':'开始摄像头 · 60秒';
  const phases={WAIT_BOARD_PREPARATION:'请运行对应固定Notebook',BOARD_PREPARING:'正在准备板端',READY_TO_START:'准备完成，可以开始',START_REQUESTED:'已请求开始',GPU_PREPARING:'正在准备GPU',RUNNING:'实际计算中',AUDITING:'正在保存与核验',COMPLETE:'已结束，可再次开始',FAILED:'失败，请保留现场'};
  const phase=current.backend==='GPU_FPGA'?(phases[status.workbench_phase]||status.workbench_phase):(status.ready_to_start?'准备完成，可以开始':status.status==='WAITING_FIRST_STEP'?'请运行固定Notebook并等待准备':status.status==='FINISHED'?(status.display_complete?'已结束，审核与光流完成':'计算已结束，等待审核与解码'):status.status);
  $('opHint').textContent=(current.input==='scientific28'?current.condition:'真实摄像头')+' · '+phase+' · 已提交/接收 '+(status.committed_steps||status.received_steps||0)+' 步'+(status.run_id?' · run '+status.run_id:'')+(status.error?' · '+status.error:'');

 }catch(e){$('opStart').disabled=true;}setTimeout(poll,1000);}
 $('opStart').addEventListener('click',async()=>{try{
  $('opStart').disabled=true;
  if(current.backend==='GPU_FPGA'){
   const b=$('cpJointStart');if(!b||b.disabled)throw Error('请等待原联合控制器准备完成');b.click();
  }else{
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
