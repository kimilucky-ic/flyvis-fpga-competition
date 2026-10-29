'use strict';
const $ = id => document.getElementById(id);
const TARGETS = ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];
const REPRESENTATIVES = ['L1','L2','Mi1','Tm3'];
const PALETTE = ['#5fe1e8','#85dda8','#a9a0ff','#6faaff','#ff9580','#f4ca78','#f395c7','#cfb08c','#83c7f0','#c8e878','#cc95e3','#e5e8ee'];
const CELL_COLORS = Object.fromEntries(TARGETS.map((c,i)=>[c,PALETTE[i]]));
const state = {catalog:null,dataset:null,sample:null,stimulus:null,activity:null,frame:240,selected:new Set(TARGETS),
  angle:0,intensity:1,radius:-1,playing:false,speed:.5,elapsed:0,lastTick:0,fraction:0,directions:null,
  compareAngles:new Set([0,180]),loadToken:0,directionToken:0,loading:true,cache:new Map(),toastTimer:null,
  cameraImage:null,frameToken:0,framePending:false,imageCache:new Map(),adapters:null,variant:1,comparison:null,comparisonMode:'Full_GPU'};

function node(tag,text,className){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;}
function color(cell){return CELL_COLORS[cell] || PALETTE[state.dataset.cell_types.indexOf(cell)%PALETTE.length];}
function toast(message){$('toast').textContent=message;$('toast').classList.remove('hidden');clearTimeout(state.toastTimer);state.toastTimer=setTimeout(()=>$('toast').classList.add('hidden'),4500);}
async function getJSON(url){const response=await fetch(url);if(!response.ok)throw new Error(`读取失败 (${response.status})：${url}`);return response.json();}
async function getArray(url,type){const response=await fetch(url);if(!response.ok)throw new Error(`活动/输入读取失败 (${response.status})`);return new type(await response.arrayBuffer());}
function showError(error){$('error').textContent=error.message||String(error);$('error').classList.remove('hidden');}
function setLoading(on){state.loading=on;$('loading').classList.toggle('hidden',!on);for(const id of ['play','reset','step','export','timeline'])$(id).disabled=on;window.FlyVisGuide?.render(state);}
function pause(){state.playing=false;$('play').textContent='▶ 播放';$('play').setAttribute('aria-label','播放');window.FlyVisGuide?.render(state);}
function sourceMedia(d=state.dataset){return d.camera||d.controlled_video;}

function selectedCondition(){
  const d=state.dataset;
  if(d.camera)return d.conditions[0];
  if(d.condition_selector)return d.conditions.find(c=>c.sample===state.variant);
  return d.conditions.find(c=>c.intensity===state.intensity && (d.family==='flash'?c.radius===state.radius:c.angle===state.angle));
}
function renderControls(){
  const d=state.dataset;
  document.querySelector('.input-panel').classList.toggle('camera-view',!!sourceMedia(d));
  $('dataset').value=d.id;
  $('angles').replaceChildren();
  const angles=[...new Set(d.conditions.map(c=>c.angle).filter(x=>x!==undefined))];
  if(d.condition_selector){$('angles').append(node('span',d.condition_selector_label||'十条件 · 参数独立验证','muted'));}
  else if(!angles.length){$('angles').append(node('span',d.camera?'真实录制 · 无受控方向标签':'Flash · 无运动方向','muted'));}
  if(!d.condition_selector)
  for(const angle of angles){const b=node('button',`${angle}°`);b.setAttribute('aria-label',`选择${angle}度`);b.setAttribute('aria-pressed',String(angle===state.angle));b.onclick=()=>{state.angle=angle;state.compareAngles=new Set([angle, (angle+180)%360].filter(a=>angles.includes(a)));changeSample();};$('angles').append(b);}
  for(const [id,polarity] of [['on',1],['off',0]]){const b=$(id);b.setAttribute('aria-pressed',String(state.intensity===polarity));b.disabled=!d.conditions.some(c=>c.intensity===polarity);}
  $('radiusLabel').classList.toggle('hidden',d.family!=='flash');$('radius').value=String(state.radius);
  document.querySelector('.polarity-control').classList.toggle('hidden',!!d.camera||!!d.condition_selector);
  $('conditionLabel').classList.toggle('hidden',!d.condition_selector);
  $('condition').setAttribute('aria-label',d.controlled_video?'受控视频完整实验条件':'MovingBar完整实验条件');
  if(d.condition_selector){$('condition').replaceChildren(...d.conditions.map(c=>{const option=node('option',d.controlled_video?`#${c.sample} · ${c.title}`:`#${c.sample} · ${c.angle}° · I=${c.intensity} · width=${c.width} · v=${c.speed}`);option.value=c.sample;return option;}));$('condition').value=String(state.variant);}
}

async function changeDataset(id,initial={}){
  pause();state.frameToken++;state.cameraImage=null;state.imageCache.clear();state.framePending=false;
  state.dataset={...state.catalog.datasets.find(d=>d.id===id)};state.angle=initial.angle??0;state.intensity=initial.intensity??1;state.radius=-1;state.variant=1;
  state.compareAngles=new Set([0,180]);state.elapsed=0;state.frame=240;
  $('directionCell').replaceChildren(...TARGETS.map(c=>{const o=node('option',c);o.value=c;return o;}));$('directionCell').value='T4c';
  renderCellPicker();await changeSample();
}
async function changeSample(){
  state.comparison=null;state.comparisonMode='Full_GPU';comparisonModeUI();
  const token=++state.loadToken;pause();setLoading(true);state.directions=null;state.directionToken++;
  state.frameToken++;state.stimulus=null;state.activity=null;state.sample=null;state.cameraImage=null;
  $('cameraTiming').classList.add('hidden');$('conditionTag').textContent='正在加载真实数据';
  $('directionLegend').replaceChildren();$('compareAngles').replaceChildren();
  $('dsi').textContent='—';$('preferred').textContent='—';updateLegend();render();
  blankCanvas('directionChart','等待当前实验活动');blankCanvas('polar','等待当前实验指标');
  $('error').classList.add('hidden');renderControls();
  const started=performance.now(),d=state.dataset,condition=selectedCondition();
  if(!condition){setLoading(false);showError(new Error('没有验收过的该方向/亮度组合。'));return;}
  try{
    const key=`${d.id}:${condition.sample}`;
    let data=state.cache.get(key);
    if(!data){
      const sample=await getJSON(`/api/datasets/${d.id}/samples/${condition.sample}`);
      const [stimulus,activity]=await Promise.all([getArray(sample.stimulus.url,Float64Array),getArray(sample.activity.url,Float32Array)]);
      const frames=sample.n_frames||d.n_frames;
      if(stimulus.length!==frames*721 || activity.length!==frames*d.cell_types.length)throw new Error('数组长度不符合实验轴定义');
      data={sample,stimulus,activity};state.cache.set(key,data);
      if(state.cache.size>6)state.cache.delete(state.cache.keys().next().value);
    }
    if(token!==state.loadToken)return;
    if(data.sample.time_s){d.time_s=data.sample.time_s;d.n_frames=data.sample.n_frames;}
    state.sample=data.sample;state.stimulus=data.stimulus;state.activity=data.activity;state.frame=Math.min(state.frame,d.n_frames-1);
    state.fraction=state.frame;state.elapsed=0;
    $('loadTime').textContent=`${(performance.now()-started).toFixed(1)} ms`;
    $('timeline').max=String(d.n_frames-1);$('timeStart').textContent=`${d.time_s[0].toFixed(3)} s`;$('timeEnd').textContent=`${d.time_s.at(-1).toFixed(3)} s`;
    $('conditionTag').textContent=d.controlled_video?condition.title:d.camera?'真实录像 / native / ZOH':d.condition_selector?`${condition.angle}° / I=${condition.intensity} / w=${condition.width} / v=${condition.speed}`:d.family==='flash'?`Flash / ${state.intensity?'ON':'OFF'}`:`${state.angle}° / ${state.intensity?'ON':'OFF'} / v=${condition.speed}`;
    const figure=document.querySelector('.stimulus-frame').closest('figure');
    figure.querySelector('figcaption').textContent=d.controlled_video?'合成视频文件 · 原始解码帧':d.camera?'真实录制画面 · 无损原帧':'运动刺激 · 采样输入重建';
    $('stimulus').setAttribute('aria-label',d.controlled_video?'与当前模拟输入严格对齐的受控合成视频源帧':d.camera?'与当前模拟输入严格对齐的真实录制视频帧':'当前帧的真实视觉输入重建');
    figure.querySelector('.canvas-label').textContent=d.controlled_video?'CONTROLLED VIDEO':d.camera?'RECORDED CAMERA':'STIMULUS';
    document.querySelector('.input-footnote').textContent=d.controlled_video?'合成视频文件直接输入 Full 网络；六条件从共同冻结初态独立运行。画面、721输入和活动逐步对齐；24秒合集仅为媒体演示。':d.camera?'画面来自原始无损 PNG；依据实测接收时间因果保持。右图和活动对应同一模拟步，不使用恒帧率 AVI 时间。':'两图来自同一帧 stimulus.npy。灰度为真实亮度；左图采用相邻采样点填充，不代表原始相机图像。';
    $('timeOrigin').textContent=d.controlled_video?'短片起点 / 200步·秒⁻¹':d.camera?'采集起点 / 200步·秒⁻¹':'0 s · 刺激起点';
    const image=sourceMedia(d)?await cameraImage(state.frame):null;
    if(token!==state.loadToken)return;
    state.cameraImage=image;
    $('cameraTiming').classList.toggle('hidden',!sourceMedia(d));
    updateRuntime();updateLegend();setLoading(false);render();await loadDirections();
  }catch(error){if(token===state.loadToken){setLoading(false);state.stimulus=null;state.activity=null;state.cameraImage=null;updateRuntime();$('executionKind').textContent='数据不可用';showError(error);render();}}
}

function renderCellPicker(){
  const list=$('allCells');list.replaceChildren();
  for(const cell of state.dataset.cell_types){const label=node('label');label.dataset.cell=cell;const input=node('input');input.type='checkbox';input.checked=state.selected.has(cell);input.setAttribute('aria-label',`显示${cell}曲线`);input.onchange=()=>{if(input.checked)state.selected.add(cell);else state.selected.delete(cell);updateLegend();renderActivity();};label.append(input,document.createTextNode(cell));list.append(label);}
  $('cellSearch').value='';
}
function preset(cells){state.selected=new Set(cells);renderCellPicker();updateLegend();renderActivity();}
function updateLegend(){
  $('legend').replaceChildren();
  for(const cell of state.selected){const b=node('button');b.title=`移除${cell}曲线`;b.setAttribute('aria-label',`移除${cell}曲线`);const sw=node('i',undefined,'swatch');sw.style.backgroundColor=color(cell);const v=node('span','—','value');v.dataset.valueCell=cell;b.append(sw,node('span',cell),v);b.onclick=()=>{state.selected.delete(cell);renderCellPicker();updateLegend();renderActivity();};$('legend').append(b);}
  $('targetsPreset').setAttribute('aria-pressed',String(TARGETS.every(c=>state.selected.has(c))&&state.selected.size===8));
  $('representativesPreset').setAttribute('aria-pressed',String(REPRESENTATIVES.every(c=>state.selected.has(c))&&state.selected.size===4));
}

function setupCanvas(id){
  const canvas=$(id),r=canvas.getBoundingClientRect(),scale=Math.min(window.devicePixelRatio||1,2);
  const w=Math.max(1,r.width),h=Math.max(1,r.height);
  if(canvas.width!==Math.round(w*scale)||canvas.height!==Math.round(h*scale)){canvas.width=Math.round(w*scale);canvas.height=Math.round(h*scale);}
  const ctx=canvas.getContext('2d');ctx.setTransform(scale,0,0,scale,0,0);ctx.clearRect(0,0,w,h);
  return {ctx,w,h,canvas};
}
function blankCanvas(id,message){const {ctx,w,h}=setupCanvas(id);ctx.fillStyle='#8b9cb1';ctx.font='11px Segoe UI, Microsoft YaHei';ctx.textAlign='center';ctx.fillText(message,w/2,h/2);}
function drawInput(id,mesh){
  if(!state.stimulus)return blankCanvas(id,'等待真实输入');
  if(id==='stimulus'&&sourceMedia()){
    if(!state.cameraImage)return blankCanvas(id,'正在同步源视频帧');
    const {ctx,w,h}=setupCanvas(id),im=state.cameraImage;
    const scale=Math.min(w/im.width,h/im.height);ctx.drawImage(im,(w-im.width*scale)/2,(h-im.height*scale)/2,im.width*scale,im.height*scale);return;
  }
  const {ctx,w,h}=setupCanvas(id),d=state.dataset;
  // Original flyvis.utils.hex_utils.hex_to_pixel(mode='default'): x=1.5v, y=-sqrt(3)(u+v/2).
  // Canvas y points down; invert the official y for the display. Never reorder input indices.
  const points=d.coordinates.map(c=>({x:1.5*c.v,y:Math.sqrt(3)*(c.u+c.v/2),index:c.hex_pixel}));
  const maxX=Math.max(...points.map(p=>Math.abs(p.x)))+1,maxY=Math.max(...points.map(p=>Math.abs(p.y)))+1;
  const size=Math.min((w-20)/(2*maxX),(h-27)/(2*maxY));
  const x0=w/2,y0=(h-11)/2;
  for(const p of points){
    const raw=state.stimulus[state.frame*721+p.index];const gray=Math.round(Math.max(0,Math.min(1,raw))*255);
    ctx.fillStyle=`rgb(${gray},${gray},${gray})`;ctx.beginPath();
    const radius=size*(mesh ? .9 : 1.025);
    for(let i=0;i<6;i++){const theta=i*Math.PI/3,x=x0+p.x*size+radius*Math.cos(theta),y=y0+p.y*size+radius*Math.sin(theta);if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
    ctx.closePath();ctx.fill();
    if(mesh){ctx.strokeStyle='#1a2934';ctx.lineWidth=.35;ctx.stroke();}
  }
  if(mesh){ctx.strokeStyle='#5fe1e880';ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(x0-5,y0);ctx.lineTo(x0+5,y0);ctx.moveTo(x0,y0-5);ctx.lineTo(x0,y0+5);ctx.stroke();}
}

function drawTimeChart(id,series){
  if(!state.activity)return blankCanvas(id,'等待真实活动');
  if(!series.length)return blankCanvas(id,'选择至少一条曲线');
  const {ctx,w,h}=setupCanvas(id),time=state.dataset.activity_time_s||state.dataset.time_s;
  const margin={left:48,right:18,top:26,bottom:31},pw=w-margin.left-margin.right,ph=h-margin.top-margin.bottom;
  if(pw<=0||ph<=0)return;
  let lo=Infinity,hi=-Infinity;
  for(const s of series)for(let i=0;i<time.length;i++){const value=s.value(i);lo=Math.min(lo,value);hi=Math.max(hi,value);}
  if(!Number.isFinite(lo)||!Number.isFinite(hi))return blankCanvas(id,'没有有效活动数据');
  const pad=Math.max((hi-lo)*.12,.015);lo-=pad;hi+=pad;
  const x=t=>margin.left+(t-time[0])/(time.at(-1)-time[0])*pw,y=v=>margin.top+(hi-v)/(hi-lo)*ph;
  ctx.fillStyle='#0c1420';if(time[0]<0)ctx.fillRect(margin.left,margin.top,x(0)-margin.left,ph);
  ctx.font='9px Segoe UI, Microsoft YaHei';ctx.fillStyle='#70859b';ctx.textAlign='left';ctx.fillText('activity / 模型单位',margin.left,12);if(time[0]<0)ctx.fillText('预刺激',margin.left+7,margin.top+12);
  ctx.textAlign='right';ctx.fillText('time / s',w-margin.right,h-4);
  for(let i=0;i<5;i++){
    const value=lo+(hi-lo)*i/4,yy=y(value);ctx.strokeStyle='#253447';ctx.lineWidth=.6;ctx.beginPath();ctx.moveTo(margin.left,yy);ctx.lineTo(w-margin.right,yy);ctx.stroke();
    ctx.fillStyle='#91a4b8';ctx.fillText(value.toFixed(Math.abs(hi-lo)<1?3:2),margin.left-8,yy+3);
  }
  for(let i=0;i<5;i++){
    const tt=time[0]+(time.at(-1)-time[0])*i/4,xx=x(tt);ctx.textAlign='center';ctx.fillStyle='#8299b0';ctx.fillText(tt.toFixed(2),xx,h-15);
  }
  ctx.save();ctx.beginPath();ctx.rect(margin.left,margin.top,pw,ph);ctx.clip();
  ctx.strokeStyle='#54677b';ctx.lineWidth=.8;ctx.setLineDash([3,4]);ctx.beginPath();ctx.moveTo(x(0),margin.top);ctx.lineTo(x(0),margin.top+ph);ctx.stroke();ctx.setLineDash([]);
  for(const s of series){ctx.strokeStyle=s.color;ctx.lineWidth=1.55;ctx.beginPath();for(let i=0;i<time.length;i++){const xx=x(time[i]),yy=y(s.value(i));if(!i)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy);}ctx.stroke();}
  const cursor=x(time[state.frame]);ctx.strokeStyle='#d1f4f3';ctx.lineWidth=.85;ctx.beginPath();ctx.moveTo(cursor,margin.top);ctx.lineTo(cursor,margin.top+ph);ctx.stroke();
  for(const s of series){ctx.fillStyle=s.color;ctx.beginPath();ctx.arc(cursor,y(s.value(state.frame)),2.6,0,2*Math.PI);ctx.fill();}
  ctx.restore();ctx.fillStyle='#c7ecef';ctx.font='9px Segoe UI';ctx.textAlign='center';ctx.fillText(`${time[state.frame].toFixed(3)} s`,Math.max(margin.left+20,Math.min(w-margin.right-20,cursor)),margin.top-5);
  $(id)._plot={left:margin.left,right:w-margin.right};
}
function renderActivity(){
  if(!state.dataset)return;
  if(!state.activity || (sourceMedia()&&!state.cameraImage)){
    blankCanvas('activity','等待当前真实活动与画面');for(const v of $('legend').querySelectorAll('[data-value-cell]'))v.textContent='—';return;
  }
  const count=state.dataset.cell_types.length;
  const series=[...state.selected].map(cell=>({color:color(cell),value:i=>state.activity[i*count+state.dataset.cell_types.indexOf(cell)]}));
  drawTimeChart('activity',series);
  if(state.activity)for(const v of $('legend').querySelectorAll('[data-value-cell]')){const index=state.dataset.cell_types.indexOf(v.dataset.valueCell);v.textContent=state.activity[state.frame*count+index].toFixed(3);}
}

async function loadDirections(){
  if(state.comparison){
    const cell=$('directionCell').value,index=state.dataset.cell_types.indexOf(cell),count=state.dataset.cell_types.length;
    state.compareAngles=new Set([0,1]);
    state.directions={cell_type:cell,traces:['Full_GPU','Python_Replacement'].map((mode,i)=>({sample_id:i,label:mode==='Full_GPU'?'Full GPU':'Python H + GPU R',activity:Array.from({length:800},(_,k)=>state.comparison.arrays[mode][k*count+index])})),official_metric:null,official_peaks:[],metric_status:{available:false,reason:'固定同输入/初态800步对照；误差单列，不计算DSI。'}};
    renderCompareButtons();renderDirections();return;
  }
  const token=++state.directionToken,d=state.dataset,cell=$('directionCell').value,intensity=state.intensity;
  $('dsi').textContent='—';$('preferred').textContent='—';state.directions=null;renderDirections();
  try{const result=await getJSON(`/api/datasets/${d.id}/directions?cell=${encodeURIComponent(cell)}&intensity=${intensity}&sample=${state.sample.sample_id}`);if(token!==state.directionToken)return;state.directions=result;if(d.controlled_video)state.compareAngles=new Set(result.traces.map(t=>t.sample_id));renderCompareButtons();renderDirections();}
  catch(error){if(token===state.directionToken){showError(error);blankCanvas('directionChart','方向数据读取失败');}}
}
function renderCompareButtons(){
  const result=state.directions;$('compareAngles').replaceChildren();
  for(const trace of result.traces){const angle=state.dataset.controlled_video?trace.sample_id:trace.angle_deg,b=node('button',state.dataset.controlled_video?trace.label:`${angle}°`);b.setAttribute('aria-label',state.dataset.controlled_video?`比较${trace.label}曲线`:`比较${angle}度曲线`);b.setAttribute('aria-pressed',String(state.compareAngles.has(angle)));b.onclick=()=>{if(state.compareAngles.has(angle))state.compareAngles.delete(angle);else if(state.compareAngles.size<4)state.compareAngles.add(angle);else return toast('最多同时比较 4 个方向，先取消一条曲线。');renderCompareButtons();renderDirections();};$('compareAngles').append(b);}
}
function renderDirections(){
  window.FlyVisGuide?.render(state);
  const r=state.directions;
  if(!r){blankCanvas('directionChart','读取方向响应…');blankCanvas('polar','指标身份核对中');return;}
  const chosen=r.traces.filter(t=>state.compareAngles.has(state.dataset.controlled_video?t.sample_id:t.angle_deg));
  if(!r.traces.length)blankCanvas('directionChart',state.dataset.camera?'真实录制无受控方向条件':'Flash 没有运动方向条件');
  else drawTimeChart('directionChart',chosen.map((t,i)=>({color:PALETTE[i===0?0:i===1?4:2+i],value:f=>t.activity[f]})));
  $('directionLegend').replaceChildren();
  chosen.forEach((t,i)=>{const n=node('span'),sw=node('i',undefined,'swatch');sw.style.backgroundColor=PALETTE[i===0?0:i===1?4:2+i];n.append(sw,document.createTextNode(state.dataset.controlled_video?`${r.cell_type} · ${t.label}`:`${r.cell_type} · ${t.angle_deg}° · ${state.dataset.condition_selector?`I=${r.intensity}`:r.intensity?'ON':'OFF'}`));$('directionLegend').append(n);});
  const metric=r.official_metric;
  $('dsi').textContent=metric?metric.official_dsi.toFixed(4):'未提供';
  $('preferred').textContent=metric?`${metric.preferred_direction_deg.toFixed(1)}°`:'未提供';
  $('metricNote').textContent=metric?'单模型 · MovingEdge · speed=19':'该实验未提供匹配的正式 DSI';
  $('metricDefinition').textContent=metric?
    '沿用已验收的 FlyVis 官方 peak_responses、direction_selectivity_index、preferred_direction 输出。峰值为官方时间窗口内整流原始活动最大值，不扣基线。DSI = |Σ峰值·exp(iθ)| / max亮度(Σ峰值)。分母跨 ON/OFF；只代表单模型、speed=19。偏好方向较弱时须结合峰值和 DSI 判断。活动、条件、时间与权重身份已匹配。':
    '本条件没有匹配的完整 12 方向官方分析结果。页面仅比较原始活动曲线，不自行计算或补造 DSI。'+(r.metric_status.reason?` 指标状态：${r.metric_status.reason}`:'');
  renderPolar();
}
function renderPolar(){
  const r=state.directions;if(!r?.official_peaks?.length)return blankCanvas('polar','无正式方向指标');
  const {ctx,w,h}=setupCanvas('polar'),peaks=r.official_peaks;
  const cx=w/2,cy=h/2+3,radius=Math.min(w,h)*.34,max=Math.max(...peaks.map(p=>p.rectified_peak));
  ctx.strokeStyle='#2f4458';ctx.lineWidth=.7;ctx.font='9px Segoe UI';ctx.fillStyle='#92a8bd';
  for(const factor of [.25,.5,.75,1]){ctx.beginPath();ctx.arc(cx,cy,radius*factor,0,Math.PI*2);ctx.stroke();}
  for(const a of [0,90,180,270]){const theta=a*Math.PI/180;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(cx+radius*Math.cos(theta),cy-radius*Math.sin(theta));ctx.stroke();ctx.textAlign='center';ctx.fillText(`${a}°`,cx+(radius+16)*Math.cos(theta),cy-(radius+11)*Math.sin(theta)+3);}
  ctx.fillStyle='#8298af';ctx.textAlign='center';ctx.fillText(`官方整流峰值 / max ${max.toFixed(3)}`,cx,10);
  ctx.beginPath();peaks.forEach((p,i)=>{const theta=p.angle_deg*Math.PI/180,rr=max>0?p.rectified_peak/max*radius:0;const x=cx+rr*Math.cos(theta),y=cy-rr*Math.sin(theta);if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.closePath();ctx.fillStyle=state.intensity?'#5fe1e820':'#ff958020';ctx.fill();ctx.strokeStyle=state.intensity?PALETTE[0]:PALETTE[4];ctx.lineWidth=1.6;ctx.stroke();
  for(const p of peaks){const theta=p.angle_deg*Math.PI/180,rr=max>0?p.rectified_peak/max*radius:0;ctx.fillStyle=ctx.strokeStyle;ctx.beginPath();ctx.arc(cx+rr*Math.cos(theta),cy-rr*Math.sin(theta),1.8,0,Math.PI*2);ctx.fill();}
}

function updateRuntime(){
  const d=state.dataset;$('recordedDevice').textContent=d.recorded_gpu?`${d.recorded_device.toUpperCase()} · ${d.recorded_gpu.replace('NVIDIA GeForce ','')}`:d.recorded_device.toUpperCase();
  $('inferenceTime').textContent=d.historical_inference_s!==null?`${d.historical_inference_s.toFixed(3)} s / ${d.conditions.length} 条件`:'原记录未单列推理计时';
  $('model').textContent=`${d.model} / ${d.n_neurons.toLocaleString()} 节点`;
  $('executionKind').textContent=d.controlled_video?'受控视频结果回放':d.camera?'录制结果回放':'软件回放';
  $('adapterState').textContent=`${state.adapters?.gpu?.status==='not_connected'?'未连接':'状态不可用'} / ${d.camera?'已验证录制结果':d.controlled_video?'合成文件 · 非摄像头':'离线参考'}`;
  $('sourceClockLabel').textContent=d.controlled_video?'源视频帧 / 文件呈现时间':'真实采集帧 / 接收时间';
  if(d.camera)$('cameraMode').textContent=`native BoxEye(15,13) · 因果帧保持 · 实测 ${d.camera.measured_fps.toFixed(2)} FPS → 200步/秒；原任务 ${d.origin_job_id}。采集时间为主机接收时间。`;
  if(d.controlled_video)$('cameraMode').textContent='文件60 FPS → 200步/秒 · native / 因果帧保持；每段4秒，独立恢复共同初态。无摄像头接收UTC或单调时间。输入不含4秒端点，末次活动为4秒。';
  if(state.comparison){
    const run=state.comparison.info.modes[state.comparisonMode];
    $('recordedDevice').textContent=run.device;$('inferenceTime').textContent=`${run.wall_s.toFixed(3)} s / 本次固定动画记录`;
    $('executionKind').textContent=state.comparisonMode==='Full_GPU'?'Full GPU 计算结果回放':'Python H + GPU R 计算结果回放';
    $('cameraMode').textContent=`共同输入与a0 · SOURCE_RAW · step_id=0…799 · ${run.run_id}；本页面离线回放，没有发起新计算。`;
  }
}
function render(){
  window.FlyVisGuide?.render(state);
  if(!state.dataset)return;drawInput('stimulus',false);drawInput('hex',true);renderActivity();
  if(state.directions)renderDirections();
  if(state.comparison)window.dispatchEvent(new CustomEvent('flyvis-phase3-frame',{detail:{frame:state.frame,mode:state.comparisonMode,info:state.comparison.info}}));
  $('timeline').value=String(state.frame);$('timeLabel').textContent=`t = ${state.dataset.time_s[state.frame].toFixed(3)} s`;
  $('frameLabel').textContent=`FRAME ${String(state.frame).padStart(3,'0')} / ${state.dataset.n_frames-1}`;
  $('playbackTime').textContent=`${state.elapsed.toFixed(2)} s`;
  if(sourceMedia()){const d=state.dataset,c=sourceMedia(d),index=c.input_source_indices[state.frame];
    $('captureTime').textContent=d.controlled_video?`源帧 ${index} / 文件时间 ${c.source_time_s[index].toFixed(6)} s`:`源帧 ${index} / ${c.source_time_s[index].toFixed(6)} s / ${c.received_utc[index]}`;
    $('inputTime').textContent=`${d.time_s[state.frame].toFixed(3)} s`;
    $('activityTime').textContent=`${d.activity_time_s[state.frame].toFixed(3)} s`;
  }
}
async function cameraImage(frame){
  const d=state.dataset,c=sourceMedia(d),sample=state.sample.sample_id,index=c.input_source_indices[frame],key=`${d.id}:${sample}:${index}`;
  if(!state.imageCache.has(key)){
    const promise=(async()=>{const response=await fetch(c.frame_url_template.replace('{sample}',sample).replace('{index}',index));if(!response.ok)throw new Error(`源视频帧读取失败 (${response.status})`);return createImageBitmap(await response.blob());})();
    state.imageCache.set(key,promise);
    if(state.imageCache.size>12)state.imageCache.delete(state.imageCache.keys().next().value);
  }return state.imageCache.get(key);
}
async function setFrame(frame){
  const token=++state.frameToken,d=state.dataset;state.framePending=true;
  try{const image=sourceMedia(d)?await cameraImage(frame):null;
    if(token!==state.frameToken||d!==state.dataset)return;
    state.cameraImage=image;state.frame=frame;render();
  }catch(error){if(token===state.frameToken){pause();state.cameraImage=null;state.stimulus=null;state.activity=null;$('executionKind').textContent='同步读取失败';showError(error);render();}}
  finally{if(token===state.frameToken)state.framePending=false;}
}
function seek(frame){pause();frame=Math.max(0,Math.min(state.dataset.n_frames-1,Math.round(frame)));state.fraction=frame;return setFrame(frame);}
function animate(timestamp){
  if(state.playing&&!state.loading){
    if(state.lastTick){const seconds=(timestamp-state.lastTick)/1000;state.elapsed+=seconds;state.fraction+=seconds*state.speed/state.dataset.dt_s;
      if(state.fraction>=state.dataset.n_frames){if($('loop').checked)state.fraction%=state.dataset.n_frames;else{state.fraction=state.dataset.n_frames-1;pause();}}
      const frame=Math.floor(state.fraction);if(frame!==state.frame&&!state.framePending)setFrame(frame);
    }state.lastTick=timestamp;
  }else state.lastTick=0;
  requestAnimationFrame(animate);
}
function chartSeek(event){const plot=event.currentTarget._plot;if(!plot||state.loading)return;const x=event.clientX-event.currentTarget.getBoundingClientRect().left;seek((x-plot.left)/(plot.right-plot.left)*(state.dataset.n_frames-1));}

function openProvenance(){
  const d=state.dataset,content=$('provenanceContent');content.replaceChildren();
  if(state.comparison){
    const info=state.comparison.info,run=info.modes[state.comparisonMode];
    content.append(node('p',`本次固定动画对照 · ${state.comparisonMode} · offline_replay`));
    const list=node('dl');
    for(const [key,value] of [['comparison_id',info.comparison_id],['run_id',run.run_id],['实际计算证据级别',run.evidence_level],['当前活动完整轨迹SHA256',run.source_activity_sha256],['本次800步实际计算用时',`${run.wall_s} s；${run.timing_scope}`]]){const row=node('div');row.append(node('dt',key),node('dd',value));list.append(row);}
    content.append(list);const link=node('a','打开本次只读对照身份与误差');link.href=`/api/phase3/comparisons/${info.comparison_id}`;link.target='_blank';content.append(link);
    content.append(node('p','下面保留原视觉输入实验的来源；神经活动以本次run_id和完整轨迹SHA为准。'));
  }
  const fields=[['实验',`${d.title} · sample ${state.sample.sample_id} · ${JSON.stringify(state.sample.conditions)}`],['原始目录',d.source_directory],['模型版本 / 源码 commit',`FlyVis ${d.flyvis_version} / ${d.source_commit}`],['权重 SHA256',d.checkpoint_sha256],['导出定义',`${d.n_neurons.toLocaleString()} 神经元 / ${d.n_connections.toLocaleString()} 连接；每类一个中心节点，共 65 类。全部网络已模拟。`],['时间轴与活动语义',`${d.time_reference}；200 个模拟时间步/秒；模型单位，不是 Hz、脉冲或已标定毫伏。`]];
  if(d.camera)fields.push(['原始录像目录',d.camera.source_directory],['转换输入目录',d.camera.input_directory],['录制 / 输入 / 活动 SHA256',`${d.camera.source_sha256} / ${d.camera.input_sha256} / ${d.camera.output_sha256}`],['处理与执行身份',`${d.processing_mode}；原任务 ${d.origin_job_id} / ${d.origin_execution_kind}；本页面 offline_replay。`]);
  if(d.controlled_video){const c=d.controlled_video;fields.push(['来源类型','synthetic_controlled_video；合成文件直接输入，source_is_camera=false'],['当前源视频 SHA256',c.source_video_sha256[state.sample.sample_id]],['冻结输入 / 活动 SHA256',`${c.input_sha256} / ${c.output_sha256}`],['共同完整初态 SHA256',c.common_initial_state_sha256],['条件与执行身份',`${c.condition_execution}；${d.processing_mode}；历史任务 ${d.origin_job_id} / ${d.origin_execution_kind}。24秒合集不是连续网络活动。`]);}
  for(const [label,value] of fields){const n=node('div',undefined,'source-field');n.append(node('span',label,'field-label'),node('code',value));content.append(n);}
  const identityURL=d.controlled_video?`/api/datasets/${d.id}/files/result.json`:d.camera?`/api/datasets/${d.id}/files/input.metadata.json`:d.condition_selector?`/api/datasets/${d.id}/files/artifacts.bar_cuda_r1.result.json`:`/api/datasets/${d.id}/files/metadata.json`;
  const links=node('div',undefined,'source-links');for(const [label,url] of [['原始 metadata / result',identityURL],['原始 manifest',d.manifest_url]]){const a=node('a',label);a.href=url;a.target='_blank';a.rel='noopener';links.append(a);}content.append(links);
  if(d.geometry_identity_source)content.append(node('p','中心节点及721坐标沿用相同 checkpoint 的 edge24 身份文件；全部十条件 cell_types 顺序已逐位匹配。','provenance-note'));
  for(const f of [...d.files.filter(f=>d.camera||d.condition_selector||['stimulus.npy','activity_central.npy','time.npy','samples.csv','cell_types.npy','demo_payload.json','neurons.csv','input_hex_coordinates.csv'].includes(f.name)),...(d.official_metrics.files||[])]){
    const n=node('div',undefined,'source-file'),a=node('a',f.name);a.href=f.url;a.target='_blank';a.rel='noopener';n.append(a,node('code',f.sha256));content.append(n);
  }
  content.append(node('p',`启动时已校验 ${d.verification.manifest_files} 个源文件；当前为离线回放。`+(d.official_metrics.available?'正式方向指标：活动逐位一致，输入经原实验 float32 转换后相等，12方向/ON-OFF条件匹配。':'此实验不展示正式 DSI。'),'provenance-note'));
  $('provenance').showModal();
}
function exportCSV(){
  if(state.comparison)return exportComparisonCSV();
  if(state.loading||!state.activity||!state.selected.size)return toast('请先选择要导出的细胞曲线。');
  const cells=[...state.selected],d=state.dataset,condition=state.sample.conditions;
  const extra=d.controlled_video?['condition_id','source_kind','kind','direction','activity_time_s','source_frame','source_time_s','held_frame_age_s','common_initial_state_sha256']:d.camera?['activity_time_s','source_frame','capture_time_s','received_utc']:d.condition_selector?['width','speed']:[];
  const header=['dataset','sample','angle_deg','intensity','radius','frame','time_s',...extra,...cells];const rows=[header.join(',')];
  for(let i=0;i<d.n_frames;i++){const c=sourceMedia(d),index=c?.input_source_indices[i],times=d.controlled_video?[condition.condition_id,d.source_kind,condition.kind,condition.direction??'',d.activity_time_s[i],index,c.source_time_s[index],d.time_s[i]-c.source_time_s[index],c.common_initial_state_sha256]:d.camera?[d.activity_time_s[i],index,d.camera.source_time_s[index],d.camera.received_utc[index]]:d.condition_selector?[condition.width,condition.speed]:[];rows.push([d.id,state.sample.sample_id,condition.angle??'',condition.intensity??'',condition.radius??'',i,d.time_s[i],...times,...cells.map(c=>state.activity[i*d.cell_types.length+d.cell_types.indexOf(c)])].join(','));}
  const url=URL.createObjectURL(new Blob([rows.join('\r\n')],{type:'text/csv;charset=utf-8'}));const a=node('a');a.href=url;a.download=`flyvis_${d.id}_sample${state.sample.sample_id}_curves.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);
  toast('已导出选定曲线；数值直接来自当前原始活动，包含实验标签、帧号与时间轴。');
}

function comparisonModeUI(){
  const active=state.comparison;
  for(const b of document.querySelectorAll('[data-mode]')){
    const selected=b.dataset.mode==='original'&&!active||active&&(b.dataset.mode==='original'&&state.comparisonMode==='Full_GPU'||b.dataset.mode==='python'&&state.comparisonMode==='Python_Replacement');
    b.classList.toggle('active',!!selected);b.setAttribute('aria-pressed',String(!!selected));
    if(b.dataset.mode==='original')b.querySelector('small').textContent=active?'本次Full GPU · 结果回放':'已验证 · 离线回放';
    if(b.dataset.mode==='python'){b.querySelector('small').textContent=active?'本次SOURCE_RAW · 结果回放':'未验证';b.querySelector('.mode-lock').textContent=active?'已接入':'待接入';}
  }
  document.querySelector('.intro-note strong').textContent=active?'固定动画 · 同身份软件闭环对照':'原始完整网络 · 软件回放';
  document.querySelector('.intro-note span').textContent=active?'实际Full / Python H + GPU R结果 · 当前回放':'固定预训练模型 / 原始活动 / 无新推理';
  if(!active){$('modeNotice').classList.add('hidden');window.dispatchEvent(new CustomEvent('flyvis-phase3-clear'));}
}

window.addEventListener('flyvis-phase3-open',async event=>{
  const started=performance.now();
  try{
    await changeDataset('controlled6');
    if(state.dataset.id!=='controlled6'||state.sample?.sample_id!==1)throw new Error('固定动画加载已被条件切换取消');
    const token=++state.loadToken;setLoading(true);pause();
    const id=event.detail.comparison_id,base=`/api/phase3/comparisons/${id}`;
    const info=await getJSON(base);
    const [full,python]=await Promise.all([getArray(`${base}/Full_GPU/activity.bin`,Float32Array),getArray(`${base}/Python_Replacement/activity.bin`,Float32Array)]);
    if(token!==state.loadToken)return;
    if(info.comparison_id!==id||full.length!==800*65||python.length!==800*65||info.cell_types.join()!==state.dataset.cell_types.join())throw new Error('本次对照身份、数组轴或细胞映射不匹配');
    state.comparison={info,arrays:{Full_GPU:full,Python_Replacement:python}};state.comparisonMode='Full_GPU';state.activity=full;
    $('loadTime').textContent=`${(performance.now()-started).toFixed(1)} ms`;
    document.querySelector('.input-footnote').textContent='固定01_off_right原视频与同字节721输入；Full GPU和独立Python H + GPU R从同一完整初态计算800步。当前为实际计算结果回放，FPGA尚未接入。';
    $('conditionTag').textContent='01_off_right · 本次800步软件对照';
    comparisonModeUI();updateRuntime();setLoading(false);render();await loadDirections();
  }catch(error){setLoading(false);showError(error);}
});

function exportComparisonCSV(){
  const c=state.comparison,d=state.dataset,cells=[...state.selected],mode=state.comparisonMode,run=c.info.modes[mode],count=d.cell_types.length;
  const header=['comparison_id','run_id','mode','display_kind','source_full_activity_sha256','full_run_id','python_run_id','full_activity_sha256','python_activity_sha256','stimulus_sha256','initial_state_sha256','step_id','input_time_s','activity_time_s','source_frame','source_time_s',...cells.map(x=>`${x}_Full`),...cells.map(x=>`${x}_Python`),...cells.map(x=>`${x}_Python_minus_Full`)];
  const rows=[header.join(',')];
  for(let k=0;k<800;k++){
    const source=d.controlled_video.input_source_indices[k],value=(m,x)=>c.arrays[m][k*count+d.cell_types.indexOf(x)];
    rows.push([c.info.comparison_id,run.run_id,mode,'offline_replay',run.source_activity_sha256,c.info.modes.Full_GPU.run_id,c.info.modes.Python_Replacement.run_id,c.info.modes.Full_GPU.source_activity_sha256,c.info.modes.Python_Replacement.source_activity_sha256,c.info.identity_fingerprint.stimulus,c.info.identity_fingerprint.initial,k,d.time_s[k],d.activity_time_s[k],source,d.controlled_video.source_time_s[source],...cells.map(x=>value('Full_GPU',x)),...cells.map(x=>value('Python_Replacement',x)),...cells.map(x=>value('Python_Replacement',x)-value('Full_GPU',x))].join(','));
  }
  const url=URL.createObjectURL(new Blob([rows.join('\r\n')],{type:'text/csv;charset=utf-8'})),a=node('a');a.href=url;a.download=`flyvis_phase3_${mode}_800_curves.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);toast('已导出本次两模式原值、误差、步号及运行身份。');
}

async function init(){
  setLoading(true);
  try{
    const [catalog,adapters]=await Promise.all([getJSON('/api/catalog'),getJSON('/api/adapters').catch(()=>({gpu:{status:'not_connected'},modes:[]}))]);state.catalog=catalog;state.adapters=adapters;
    $('dataset').replaceChildren(...catalog.datasets.map(d=>{const o=node('option',d.title);o.value=d.id;return o;}));
    $('dataset').onchange=()=>changeDataset($('dataset').value);
    $('on').onclick=()=>{state.intensity=1;changeSample();};$('off').onclick=()=>{state.intensity=0;changeSample();};
    $('radius').onchange=()=>{state.radius=Number($('radius').value);changeSample();};
    $('condition').onchange=()=>{state.variant=Number($('condition').value);state.compareAngles=new Set([0,180]);changeSample();};
    $('play').onclick=async()=>{if(state.playing)pause();else if(state.activity){if(state.frame===state.dataset.n_frames-1)await seek(0);state.fraction=state.frame;state.lastTick=0;state.playing=true;$('play').textContent='Ⅱ 暂停';$('play').setAttribute('aria-label','暂停');}};
    $('reset').onclick=()=>{state.elapsed=0;seek(0);};$('step').onclick=()=>seek(state.frame+1);$('timeline').oninput=()=>seek(Number($('timeline').value));
    $('speed').onchange=()=>state.speed=Number($('speed').value);
    $('targetsPreset').onclick=()=>preset(TARGETS);$('representativesPreset').onclick=()=>preset(REPRESENTATIVES);
    $('cellSearch').oninput=()=>{const term=$('cellSearch').value.trim().toLowerCase();for(const label of $('allCells').children)label.hidden=!label.dataset.cell.toLowerCase().includes(term);};
    $('directionCell').onchange=()=>loadDirections();$('provenanceButton').onclick=openProvenance;$('closeProvenance').onclick=()=>$('provenance').close();$('export').onclick=exportCSV;
    for(const button of document.querySelectorAll('[data-mode]'))button.onclick=()=>{
      if(state.comparison&&['original','python'].includes(button.dataset.mode)){
        pause();state.comparisonMode=button.dataset.mode==='original'?'Full_GPU':'Python_Replacement';state.activity=state.comparison.arrays[state.comparisonMode];comparisonModeUI();updateRuntime();render();return;
      }
      if(button.dataset.mode==='original'){$('modeNotice').classList.add('hidden');return;}
      const mode=adapters.modes.find(m=>m.id===button.dataset.mode)||{id:button.dataset.mode,label:button.textContent};
      $('modeNotice').textContent=`${mode.label}：${mode.id==='fpga'?'板级结果尚未交付，FPGA不可用':'该替换模式尚未验收'}。当前保留${state.comparison?'已加载的真实软件对照结果回放':'原始完整网络的真实回放'}。`;$('modeNotice').classList.remove('hidden');
    };
    $('submitInference').onclick=async()=>{
      if(state.loading||!state.sample)return;const button=$('submitInference');button.disabled=true;$('gpuStatus').textContent='正在提交固定输入…';
      try{const response=await fetch('/api/inference',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dataset_id:state.dataset.id,sample_ids:[state.sample.sample_id],input_sha256:state.sample.source_input_sha256})});const result=await response.json();
        $('gpuStatus').textContent=result.status==='not_connected'?'未连接 · 尚未创建新计算任务':`任务状态：${result.status}`;
        $('gpuDetail').textContent=result.error||'等待正式 GPU 服务契约与结果验证接口';
      }catch(error){$('gpuStatus').textContent='任务提交失败';$('gpuDetail').textContent=error.message;}
      finally{button.disabled=false;}
    };
    for(const id of ['activity','directionChart']){const canvas=$(id);canvas.onpointerdown=event=>{canvas.setPointerCapture(event.pointerId);chartSeek(event);};canvas.onpointermove=event=>{if(event.buttons===1)chartSeek(event);};}
    document.addEventListener('keydown',e=>{if(!$('play').getClientRects().length||['INPUT','SELECT','TEXTAREA','BUTTON','SUMMARY','A'].includes(e.target.tagName)||$('provenance').open)return;if(e.code==='Space'){e.preventDefault();if(!state.loading)$('play').click();}else if(e.code==='ArrowRight'&&!state.loading){e.preventDefault();seek(state.frame+1);}else if(e.code==='ArrowLeft'&&!state.loading){e.preventDefault();seek(state.frame-1);}});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
    new ResizeObserver(()=>render()).observe(document.querySelector('main'));
    if(catalog.unavailable_datasets.length){const notice=catalog.unavailable_datasets.map(d=>`${d.title}：${d.error}`).join('；');$('importNotice').textContent=`数据未开放：${notice}。其余已验收离线实验仍可使用。`;$('importNotice').classList.remove('hidden');}
    await changeDataset(catalog.default_dataset,catalog.default_dataset==='edge24'?{angle:60}:{});requestAnimationFrame(animate);
  }catch(error){setLoading(false);showError(error);}
}
window.addEventListener('flyvis-demo-example',async event=>{
  const {angle,intensity}=event.detail||{};
  if(state.loading||!state.catalog||!((angle===60&&intensity===1)||(angle===90&&intensity===0)))return;
  await changeDataset('edge24',{angle,intensity});
  if(state.loading||state.dataset.id!=='edge24'||state.angle!==angle||state.intensity!==intensity||!state.activity)return;
  preset(TARGETS);$('directionCell').value=intensity?'T4c':'T5c';await loadDirections();
});
if(window.FlyVisStartup)FlyVisStartup.onPanel(['demoWorkspace','inferencePanel'],init);else init();
