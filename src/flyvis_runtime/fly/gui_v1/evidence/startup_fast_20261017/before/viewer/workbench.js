/* Optional evidence workbench. No timers advancing a device, no generated activity. */
(() => {
  const el=id=>document.getElementById(id), labels={Full_GPU:'Full GPU',Sham_Ablation:'Sham / Ablation',Python_Replacement:'Python Replacement',FPGA_Replacement:'FPGA Replacement'};
  let info=null,mode='Full_GPU',run=null,frame=0,token=0,stepToken=0,arrays=new Map(),stimulus=null,sourceImage=null,imageKey=null;
  let targets=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];const colors=['#5fe1e8','#85dda8','#a9a0ff','#6faaff','#ff9580','#f4ca78','#f395c7','#cfb08c'];
  async function json(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}：${url}`);return r.json();}
  async function floats(url,kind){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}：真实数组不可用`);return new kind(await r.arrayBuffer());}
  const show=value=>value===null||value===undefined?'NOT_AVAILABLE':typeof value==='object'?JSON.stringify(value):String(value);
  function field(name,value){const d=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=show(value);d.append(dt,dd);el('wbIdentity').append(d);}
  function clearView(message){++stepToken;el('wbView').classList.add('hidden');el('wbProgress').textContent='真实执行进度：NOT_AVAILABLE';el('wbStages').replaceChildren();el('wbCurrent').textContent=message;sourceImage?.close();sourceImage=null;imageKey=null;el('wbExport').disabled=true;}
  function setIdentity(){
    el('wbIdentity').replaceChildren();
    field('display_kind','offline replay');field('comparison_id',info?.comparison_id);field('当前模式',labels[mode]);field('实际 backend',run?.backend_id);field('run_id',run?.run_id);field('模型',run?.model_id);field('权重 SHA256',info?.identity_fingerprint.model);field('共同初态 SHA256',info?.identity_fingerprint.initial);field('本次活动来源 SHA',run?.source_activity_sha256);field('原实际设备',run?.device);field('历史使用真板',run?run.board_used?'是：实际板级证据记录':'否：GPU／软件计算记录':null);field('当前真板连接',null);field('原计算 wall 秒',run?.wall_s);field('证据级别',run?.evidence_level);
    field('板卡／bit／hwh',run?.board);field('PL周期与GPU / PS / PL延迟',run?.hardware_metrics&&Object.values(run.hardware_metrics).some(v=>v!==null)?run.hardware_metrics:null);
    el('wbConnections').textContent='当前计算后端：NOT_AVAILABLE · 当前真板连接：NOT_AVAILABLE；历史记录不证明当前连接';
  }
  function modeButtons(){
    el('wbModes').replaceChildren();
    for(const [key,label] of Object.entries(labels)){
      const b=document.createElement('button'),strong=document.createElement('strong'),small=document.createElement('small');strong.textContent=label;small.textContent=info?.modes[key]?.status||'NOT_AVAILABLE';b.append(strong,small);b.setAttribute('aria-pressed',String(mode===key));b.onclick=()=>{mode=key;modeButtons();selectMode();};el('wbModes').append(b);
    }
  }
  async function refresh(){
    const request=++token;
    try{
      const data=await json('/api/workbench');if(request!==token)return;
      el('wbStatus').textContent=`已准入真实运行记录 · offline replay；执行后端 ${data.execution_backend.status}；仅按真实事件更新，无实时要求。`;
      el('wbErrors').textContent=(data.import_errors||[]).join('；');
      const old=el('wbComparison').value;el('wbComparison').replaceChildren();
      for(const c of data.comparisons){const o=document.createElement('option');o.value=c.comparison_id;o.textContent=`${c.title} · ${c.steps}步 · offline replay`;el('wbComparison').append(o);}
      if(data.comparisons.some(c=>c.comparison_id===old))el('wbComparison').value=old;
      if(!data.comparisons.length){info=null;run=null;modeButtons();setIdentity();clearView('NOT_AVAILABLE：没有已准入的比较结果。原55条件仍可使用。');return;}
      await loadComparison();
    }catch(e){if(request!==token)return;info=null;run=null;setIdentity();modeButtons();clearView('NOT_AVAILABLE：工作台数据读取失败；原展示可继续使用。');el('wbErrors').textContent=e.message;}
  }
  async function loadComparison(){
    const request=++token;clearView('读取真实比较身份…');arrays=new Map();stimulus=null;run=null;
    try{
      const next=await json(`/api/workbench/comparisons/${el('wbComparison').value}`);if(request!==token)return;
      info=next;frame=Math.min(frame,info.steps-1);modeButtons();
      el('wbCells').replaceChildren();for(const cell of info.cell_types){const option=document.createElement('option');option.value=option.textContent=cell;option.selected=targets.includes(cell);el('wbCells').append(option);}
      el('wbStep').max=el('wbStepNumber').max=String(info.steps-1);el('wbPrimary').disabled=info.error_scope!=='full_network_and_registered_groups';
      el('wbReports').replaceChildren();
      if(!info.formal_functional_reports.length)el('wbReports').textContent='正式 Sham/Ablation 功能报告：NOT_AVAILABLE。当前只读到执行规范，未将规范当成正式结果。';
      for(const report of info.formal_functional_reports){const a=document.createElement('a');a.href=report.report_url;a.textContent=`${report.variant} 正式报告 · ${report.run_id}`;a.target='_blank';a.rel='noopener';el('wbReports').append(a,document.createElement('br'));}
      await selectMode();
    }catch(e){if(request!==token)return;run=null;setIdentity();clearView('NOT_AVAILABLE：比较源无法验证或读取');el('wbErrors').textContent=e.message;}
  }
  async function selectMode(){
    ++token;
    const candidates=info?.runs.filter(r=>r.mode===mode)||[];run=candidates[0]||null;el('wbRunLabel').classList.toggle('hidden',candidates.length<2);el('wbRun').replaceChildren();
    for(const r of candidates){const o=document.createElement('option');o.value=r.run_id;o.textContent=`${r.variant||r.mode} · ${r.run_id}`;el('wbRun').append(o);}
    if(!run){clearView(`${labels[mode]} · NOT_AVAILABLE：没有此 comparison_id 下已验收的真实结果。`);setIdentity();return;}
    await loadRun();
  }
  async function loadRun(){
    const request=++token;clearView('读取真实活动…');setIdentity();
    try{
      const full=info.runs.find(r=>r.mode==='Full_GPU'),needed=[run,full].filter((r,i,a)=>r&&a.findIndex(x=>x?.run_id===r.run_id)===i);
      for(const r of needed)if(!arrays.has(r.run_id)){const values=await floats(r.activity_url,Float32Array);if(request!==token)return;if(values.length!==info.steps*info.cell_types.length||!values.every(Number.isFinite))throw new Error('活动轴或有限值不匹配');arrays.set(r.run_id,values);}
      if(!stimulus){const values=await floats(info.preview.stimulus_url,Float64Array);if(request!==token)return;if(values.length!==info.steps*721)throw new Error('视觉输入轴不匹配');stimulus=values;}
      el('wbView').classList.remove('hidden');el('wbCurrent').textContent=`当前 ${labels[mode]}${run.variant?' / '+run.variant:''} · offline replay · ${run.run_id}；不是新任务，也不是当前板卡状态。`;
      const p=run.progress;el('wbProgress').textContent=`历史实际记录：${p.execution_state} · ${p.committed_steps===null?`完整参考步 ${p.reference_steps}`:`统一 COMMIT ${p.committed_steps}`} / ${info.steps}；回放游标不推进计算。`;
      el('wbEvents').href=run.evidence_url;el('wbExport').disabled=false;await inspectFrame();
    }catch(e){if(request!==token)return;clearView(`${labels[mode]} · NOT_AVAILABLE：真实活动读取失败`);el('wbErrors').textContent=e.message;}
  }
  function canvas(id){const c=el(id),r=c.getBoundingClientRect(),s=Math.min(devicePixelRatio||1,2);c.width=Math.max(1,Math.round(r.width*s));c.height=Math.max(1,Math.round(r.height*s));const ctx=c.getContext('2d');ctx.scale(s,s);return {ctx,w:r.width,h:r.height};}
  function chart(id,series){
    const {ctx,w,h}=canvas(id),left=39,right=w-10,top=20,bottom=h-26,time=info.activity_time_s;
    let lo=Math.min(...series.map(s=>Math.min(...s.values))),hi=Math.max(...series.map(s=>Math.max(...s.values)));const pad=Math.max((hi-lo)*.1,Math.abs(hi)*.03,1e-9);lo-=pad;hi+=pad;
    const x=k=>left+(right-left)*k/(info.steps-1),y=v=>bottom-(v-lo)/(hi-lo)*(bottom-top);
    ctx.font='9px Segoe UI';ctx.fillStyle='#8aa0b5';ctx.fillText(`${time[0].toFixed(3)} s`,left,h-7);ctx.fillText(`${time.at(-1).toFixed(3)} s`,right-44,h-7);
    for(let i=0;i<3;i++){const v=lo+(hi-lo)*i/2;ctx.strokeStyle='#243547';ctx.beginPath();ctx.moveTo(left,y(v));ctx.lineTo(right,y(v));ctx.stroke();ctx.fillText(Math.abs(v)<.001?v.toExponential(1):v.toFixed(2),0,y(v)+3);}
    series.forEach(s=>{ctx.strokeStyle=s.color;ctx.globalAlpha=s.alpha||1;ctx.lineWidth=s.alpha ? .5 : 1.3;ctx.beginPath();s.values.forEach((v,k)=>k?ctx.lineTo(x(k),y(v)):ctx.moveTo(x(k),y(v)));ctx.stroke();});ctx.globalAlpha=1;ctx.strokeStyle='#d1f4f3';ctx.beginPath();ctx.moveTo(x(frame),top);ctx.lineTo(x(frame),bottom);ctx.stroke();
  }
  function renderCharts(){
    const a=arrays.get(run.run_id),full=info.runs.find(r=>r.mode==='Full_GPU'),base=arrays.get(full?.run_id),count=info.cell_types.length,series=[];
    targets.forEach((cell,i)=>{const col=info.cell_types.indexOf(cell),color=colors[i%colors.length];if(base&&full.run_id!==run.run_id)series.push({color,alpha:.25,values:Array.from({length:info.steps},(_,k)=>base[k*count+col])});series.push({color,values:Array.from({length:info.steps},(_,k)=>a[k*count+col])});});chart('wbActivity',series);
    el('wbReadouts').textContent=targets.map(cell=>`${cell} ${a[frame*count+info.cell_types.indexOf(cell)].toFixed(3)}`).join(' · ')+(full.run_id!==run.run_id?'；细线为同身份 Full 参考':'');
    const err=info.error_scope==='full_network_and_registered_groups'?info.errors.full:info.errors[run.run_id];chart('wbError',[{color:'#f4ca78',values:err.max_abs}]);
    el('wbErrorCaption').textContent=info.error_scope==='full_network_and_registered_groups'?`Python − Full · 全45669节点 max_abs；当前 ${err.max_abs[frame].toExponential(3)}，原容差超限 ${info.errors.full.violations[frame]}；不是DSI`:`当前模式 − Full · 仅65中心 max_abs ${err.max_abs[frame].toExponential(3)}；不是全网指标或DSI`;
    const {ctx,w,h}=canvas('wbInput'),d=info.preview.dataset,media=d.controlled_video||d.camera,left=media?w*.46:0,available=w-left;
    if(sourceImage)ctx.drawImage(sourceImage,0,15,left-8,h-30);
    const points=d.coordinates.map(c=>({x:1.5*c.v,y:Math.sqrt(3)*(c.u+c.v/2),i:c.hex_pixel})),extent=Math.max(...points.map(p=>Math.max(Math.abs(p.x),Math.abs(p.y))))+1,size=Math.min(available,h-15)/(extent*2);
    for(const p of points){const gray=Math.round(Math.max(0,Math.min(1,stimulus[frame*721+p.i]))*255);ctx.fillStyle=`rgb(${gray},${gray},${gray})`;ctx.beginPath();for(let i=0;i<6;i++){const theta=i*Math.PI/3,x=left+available/2+(p.x+.85*Math.cos(theta))*size,y=h/2+(p.y+.85*Math.sin(theta))*size;i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.closePath();ctx.fill();}
    const sourceFrame=media?.input_source_indices[frame];el('wbInputCaption').textContent=media?`原始源帧 ${sourceFrame} · 源时间 ${media.source_time_s[sourceFrame].toFixed(6)} s · 721真实亮度；${d.camera?'真实采集记录':'合成受控视频'}`:'721真实采样输入；未新增空间神经网络图';
  }
  async function inspectFrame(){
    if(!run||!arrays.has(run.run_id)||!stimulus)return;const request=++stepToken;
    el('wbStep').value=el('wbStepNumber').value=String(frame);el('wbTime').textContent=`step ${frame}/${info.steps-1} · 输入 ${info.input_time_s[frame].toFixed(3)} s · Euler后 ${info.activity_time_s[frame].toFixed(3)} s`;
    el('wbStages').replaceChildren();
    try{
      const step=await json(`/api/workbench/runs/${run.run_id}/steps/${frame}`);if(request!==stepToken)return;
      for(const [name,value] of [['PL计算／历史记录',step.pl_status],['返回候选',step.candidate_status],['统一 COMMIT',step.commit_status+(step.unified_commit?` · token ${step.unified_commit.state_token}`:'')],['实际校验',step.validation_status]]){const d=document.createElement('div'),label=document.createElement('span'),v=document.createElement('strong');label.textContent=name;v.textContent=value;d.append(label,v);el('wbStages').append(d);}
      const d=info.preview.dataset,media=d.controlled_video||d.camera;
      if(media){const index=media.input_source_indices[frame],key=info.comparison_id+'/'+index,url=media.frame_url_template.replace('{sample}',info.preview.sample.sample_id).replace('{index}',index);if(imageKey!==key){sourceImage?.close();sourceImage=null;renderCharts();const response=await fetch(url);if(!response.ok)throw new Error('原始源帧读取失败');const image=await createImageBitmap(await response.blob());if(request!==stepToken){image.close();return;}sourceImage=image;imageKey=key;}}
      if(request===stepToken)renderCharts();
    }catch(e){if(request===stepToken){el('wbErrors').textContent=e.message;el('wbView').classList.add('hidden');}}
  }
  function exportCSV(){
    if(!run||!arrays.has(run.run_id))return;const a=arrays.get(run.run_id),count=info.cell_types.length,rows=[['comparison_id','run_id','mode','variant','display_kind','source_activity_sha256','step_id','input_time_s','activity_time_s',...info.cell_types].join(',')];
    for(let k=0;k<info.steps;k++)rows.push([info.comparison_id,run.run_id,run.mode,run.variant||'','offline_replay',run.source_activity_sha256,k,info.input_time_s[k],info.activity_time_s[k],...a.subarray(k*count,(k+1)*count)].join(','));
    const url=URL.createObjectURL(new Blob([rows.join('\r\n')],{type:'text/csv;charset=utf-8'})),link=document.createElement('a');link.href=url;link.download=`flyvis_workbench_${run.mode}_${run.run_id}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  el('wbRefresh').onclick=refresh;el('wbComparison').onchange=loadComparison;el('wbRun').onchange=()=>{run=info.runs.find(r=>r.run_id===el('wbRun').value);loadRun();};el('wbStep').oninput=()=>{frame=Number(el('wbStep').value);inspectFrame();};el('wbExport').onclick=exportCSV;
  el('wbStepNumber').oninput=()=>{const value=el('wbStepNumber').value,k=Number(value);if(value!==''&&info&&Number.isInteger(k)&&k>=0&&k<info.steps){frame=k;inspectFrame();}};
  el('wbStepNumber').onchange=()=>{el('wbStepNumber').value=String(frame);};
  el('wbPrimary').onclick=()=>{if(info)window.dispatchEvent(new CustomEvent('flyvis-phase3-open',{detail:{comparison_id:info.comparison_id}}));};
  el('wbCells').onchange=()=>{targets=Array.from(el('wbCells').selectedOptions,o=>o.value);if(!targets.length){el('wbCells').options[0].selected=true;targets=[el('wbCells').options[0].value];}if(run&&arrays.has(run.run_id))renderCharts();};
  window.addEventListener('flyvis-workbench-open',event=>{const detail=event.detail;if(!detail||!Array.from(el('wbComparison').options).some(o=>o.value===detail.comparison_id))return;el('wbComparison').value=detail.comparison_id;mode=labels[detail.mode]?detail.mode:'Full_GPU';loadComparison();});
  window.addEventListener('flyvis-flow-input-changed',()=>{++token;info=null;run=null;arrays=new Map();stimulus=null;el('wbPrimary').disabled=true;el('wbRunLabel').classList.add('hidden');clearView('本次输入已更改：尚未冻结、计算。此处旧运行曲线和身份已清空；可手动刷新并查看独立历史记录。');setIdentity();modeButtons();});
  el('wbSubmit').onclick=async()=>{const b=el('wbSubmit');b.disabled=true;try{const r=await fetch('/api/workbench/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({comparison_id:info?.comparison_id,mode})}),value=await r.json();el('wbSubmitStatus').textContent=`${value.status} · 未创建任务；${value.error}`;}catch(e){el('wbSubmitStatus').textContent='NOT_AVAILABLE · '+e.message;}finally{b.disabled=false;}};
  new ResizeObserver(()=>{if(run&&arrays.has(run.run_id)&&!el('wbView').classList.contains('hidden'))renderCharts();}).observe(el('wbView'));
  refresh();
})();
