/* Plain-language presentation of accepted arrays. No inference or new metric. */
(function (root) {
  'use strict';
  const cells = ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];
  function snapshot(s) {
    const d = s.dataset, frame = s.frame;
    if (s.loading || !d || !s.sample || s.sample.dataset_id !== d.id || !s.stimulus || !s.activity || !Number.isInteger(frame)) return null;
    const stride = d.cell_types.length;
    const values = cells.map(cell => {
      const index = d.cell_types.indexOf(cell);
      return {cell, index, value: index < 0 ? NaN : s.activity[frame * stride + index]};
    });
    const inputTime = d.time_s?.[frame];
    if (!Number.isFinite(inputTime) || !values.every(v => Number.isFinite(v.value))) return null;
    const r = s.directions;
    const metric = d.id === 'edge24' && !s.comparison && r?.dataset_id === d.id && r?.intensity === s.intensity && r?.official_peaks?.length === 12 && r.official_metric?.cell_type === r.cell_type && r.official_metric?.intensity === s.intensity &&
      Number.isFinite(r.official_metric?.official_dsi) && Number.isFinite(r.official_metric?.preferred_direction_deg) ?
      {cell:r.cell_type, dsi:r.official_metric.official_dsi, direction:r.official_metric.preferred_direction_deg} : null;
    return {values, inputTime, activityTime:d.activity_time_s?.[frame] ?? null, frame, metric};
  }
  if (typeof module !== 'undefined' && module.exports) { module.exports = {snapshot}; return; }
  const $ = id => document.getElementById(id);
  const make = (tag, cls, text) => {const e=document.createElement(tag); if(cls)e.className=cls; if(text)e.textContent=text; return e;};
  const demo = $('demoWorkspace');
  function details(title, cls) {
    const e=make('details',cls), summary=make('summary','',title);e.append(summary);
    e.addEventListener('toggle',()=>requestAnimationFrame(()=>root.dispatchEvent(new Event('resize'))));return e;
  }
  const examples=make('section','guide-examples'); examples.setAttribute('aria-label','一键选择讲解场景');
  examples.append(make('strong','','先选一个场景'));
  for (const [id,angle,intensity,label] of [['guideOn',60,1,'亮边缘移动 · ON 60°'],['guideOff',90,0,'暗边缘移动 · OFF 90°']]) {
    const b=make('button','',label);b.id=id;b.disabled=true;b.setAttribute('aria-pressed','false');
    b.onclick=()=>root.dispatchEvent(new CustomEvent('flyvis-demo-example',{detail:{angle,intensity}}));examples.append(b);
  }
  const all=details('其他刺激与全部实验条件','guide-all');
  all.append(document.querySelector('.controls')); examples.append(all);demo.prepend(examples);
  document.querySelector('.demo-hint').hidden=true;
  const tools=document.querySelector('.demo-tools');tools.querySelector('p').textContent='原始 FlyVis · 45,669 节点 · 已有真实计算结果';
  const grid=make('div','guide-grid');grid.id='guideGrid';
  function card(number,title,meaning) {
    const e=make('section','guide-card');e.append(make('span','guide-number',number),make('h2','',title),make('p','guide-meaning',meaning));grid.append(e);return e;
  }
  const visual=card('01 / 给它看什么','展示给网络的画面','观察明暗边界的位置。播放时，边界会随真实输入变化。');
  visual.append(document.querySelector('.stimulus-frame').closest('figure'));
  const visualNote=make('p','guide-caption');visualNote.id='guideVisualNote';visual.append(visualNote);
  const retina=card('02 / 网络收到什么','721 个亮度采样点','每个六边形记录一个位置的亮度。亮点与暗点组成这一时刻的视觉输入。');
  retina.append($('hex').closest('figure'));retina.append(make('p','guide-caption','颜色表示输入亮度。这里还没有神经元活动。'));
  const neurons=card('03 / 网络内部发生什么','哪些神经元有响应？','T4a–d、T5a–d 是细胞类型名。每行展示该类型一个中心节点的真实数值。');
  const rows=make('div','guide-bars');rows.id='guideBars';
  for (const cell of cells) {
    const b=make('button','guide-bar'); b.dataset.guideCell=cell;b.setAttribute('aria-label',`解释${cell}的方向响应`);
    b.append(make('span','guide-cell',cell));
    const track=make('span','guide-track');track.append(make('i','guide-zero'),make('i','guide-fill'));b.append(track,make('strong','guide-value','—'));rows.append(b);
    b.onclick=()=>{$('directionCell').value=cell;$('directionCell').dispatchEvent(new Event('change'));};
  }
  neurons.append(rows,make('p','guide-caption','中线为 0；左蓝为负、右青为正，条长表示数值大小。不是放电次数，也不是完整空间图。'));
  const primary=document.querySelector('.primary-grid');primary.before(grid);
  const playback=make('section','guide-playback');playback.setAttribute('aria-label','同步回放控制');
  const playHead=make('div','guide-play-head');playHead.append(document.querySelector('.transport'));
  const current=make('div','guide-current');current.id='guideCurrent';playHead.append(current);playback.append(playHead);
  for(const selector of ['.timeline-label','#timeline','.timeline-ticks'])playback.append(document.querySelector(selector));grid.before(playback);
  const observation=make('p','guide-observation');observation.id='guideObservation';grid.after(observation);
  const meaning=make('section','guide-conclusion');meaning.id='guideConclusion';
  const prose=make('div','guide-conclusion-copy');prose.append(make('span','guide-number','04 / 这能说明什么'),make('h2','','同一细胞，对不同方向的响应不同'));
  const message=make('p','guide-takeaway');message.id='guideTakeaway';prose.append(message);
  const limit=make('p','guide-caption','右图比较该细胞在 12 个方向实验中的官方峰值；伸得越远，峰值越大。它表示方向偏好，不是对当前画面的识别准确率。');prose.append(limit);
  const more=make('a','guide-next','再看：阻断 T4/T5 后，运动读出怎么变？ →');more.href='#scientificPilot';prose.append(more);
  meaning.append(prose,document.querySelector('.tuning'));observation.after(meaning);
  const history=details('查看完整响应曲线：横轴是时间，纵轴是活动值','guide-history');history.append(document.querySelector('.activity-panel'));
  const source=details('查看当前输入的来源、时间与原始定义','guide-source');source.append(document.querySelector('.input-panel'));
  primary.replaceWith(history,source);
  document.querySelector('.input-panel .panel-head h2').textContent='输入来源与时间定义';
  document.querySelector('.activity-panel .panel-head h2').textContent='这些响应随时间怎样变化';
  document.querySelector('.direction-panel .panel-head h2').textContent='同一细胞在不同方向下的完整曲线';
  document.querySelector('.demo-analysis>summary').textContent='深入比较不同方向、查看官方指标定义与运行记录';
  const definitionText=$('metricDefinition'), oldDefinition=definitionText.parentElement;
  const definition=details('官方方向指标的定义与适用范围','guide-definition');
  // Preserve the original definition element, which app.js updates by ID.
  definition.append(definitionText);oldDefinition.remove();meaning.append(definition);
  const scales=new WeakMap();
  let key='';
  function render(s) {
    const v=snapshot(s),d=s.dataset;
    for (const id of ['guideOn','guideOff'])$(id).disabled=!!s.loading||!s.catalog;
    $('guideOn').setAttribute('aria-pressed',String(d?.id==='edge24'&&s.angle===60&&s.intensity===1));
    $('guideOff').setAttribute('aria-pressed',String(d?.id==='edge24'&&s.angle===90&&s.intensity===0));
    if(!v){key='';meaning.querySelector('.tuning').hidden=true;limit.hidden=true;$('guideCurrent').textContent='等待当前实验的真实输入与活动';$('guideObservation').textContent='数据正在加载或不可用，暂不解释响应。';$('guideTakeaway').textContent='等待当前条件对应的已验收方向分析。';
      for(const b of rows.children){b.querySelector('.guide-value').textContent='—';b.querySelector('.guide-fill').style.width='0%';b.disabled=true;}return;}
    const next=[d.id,s.sample.sample_id,s.comparisonMode,v.frame,s.playing,s.directions?.cell_type,v.metric?.dsi].join(':');
    if(next===key)return;key=next;
    let scale=scales.get(s.activity);
    if(scale===undefined){scale=0;const stride=d.cell_types.length;for(let k=0;k<d.n_frames;k++)for(const {index} of v.values){const x=s.activity[k*stride+index];if(Number.isFinite(x))scale=Math.max(scale,Math.abs(x));}scale=scale||1;scales.set(s.activity,scale);}
    for(const [i,b] of [...rows.children].entries()){
      const x=v.values[i].value,fill=b.querySelector('.guide-fill');b.disabled=false;b.setAttribute('aria-pressed',String(s.directions?.cell_type===v.values[i].cell));
      b.querySelector('.guide-value').textContent=(x>0?'+':'')+x.toFixed(3);fill.style.width=(Math.abs(x)/scale*50)+'%';fill.style.left=(x<0?50-Math.abs(x)/scale*50:50)+'%';fill.classList.toggle('negative',x<0);
    }
    const description=d.camera?'已录制的真实摄像头画面':d.controlled_video?s.sample.conditions.title:d.family==='flash'?`闪光 · ${s.intensity?'变亮 ON':'变暗 OFF'}`:`${s.intensity?'亮':'暗'}刺激 · ${s.angle}°`;
    $('guideCurrent').textContent=`${s.playing?'正在回放':'已暂停'} · ${description} · 第 ${v.frame} 步`;
    const winner=v.values.reduce((a,b)=>b.value>a.value?b:a);
    const timing=v.activityTime===null?`按原实验时间标签 ${v.inputTime.toFixed(3)} s 展示`:`输入 ${v.inputTime.toFixed(3)} s → 更新后活动 ${v.activityTime.toFixed(3)} s`;
    $('guideObservation').textContent=`这一帧：${timing}。八个示例节点中，${winner.cell} 的活动数值最高（${winner.value.toFixed(3)}）。${s.comparison?'当前为 '+(s.comparisonMode==='Full_GPU'?'Full GPU':'Python 替换')+' 结果回放。':''}`;
    $('guideVisualNote').textContent=d.camera?'来自已录制的原始相机帧；与右侧输入和活动按时间对齐。':d.controlled_video?'来自原始视频文件；这是已有结果回放。':'由同一份 721 输入重建画面，便于看清边界；不是额外的相机图像。';
    visual.querySelector('.guide-meaning').textContent=d.camera?'这是已录下的摄像头画面。右侧是同一源帧转换后的网络输入。':d.controlled_video?'原始视频逐帧播放，右侧显示对应的视觉输入和神经活动。':d.family==='flash'?'观察画面的明暗变化，以及变化发生时神经元的响应。':'观察明暗边界的位置。播放时，边界会随真实输入变化。';
    const m=v.metric;
    $('guideTakeaway').textContent=m?`${m.cell} 在这组 ${s.intensity?'亮刺激 ON':'暗刺激 OFF'} 实验中的偏好方向为 ${m.direction.toFixed(1)}°，官方 DSI 为 ${m.dsi.toFixed(4)}。点上方其他类型，比较它们的方向偏好。`:'这项实验没有配套的正式 12 方向指标。可以观察真实活动随时间变化；这里不推断方向识别结果。';
    meaning.querySelector('.tuning').hidden=!m;limit.hidden=!m;
    meaning.querySelector('h2').textContent=m?'同一细胞，对不同方向的响应不同':'先看真实响应，再看这个实验能支持什么结论';
  }
  root.FlyVisGuide=Object.freeze({render});
  if(typeof state!=='undefined')render(state);
})(typeof window==='undefined'?globalThis:window);
