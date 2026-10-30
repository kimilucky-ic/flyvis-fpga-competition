/* Actual saved full-state observations; no model inference or board commands. */
const ObserverUI=(()=>{
 const MAP='3c8b887e1bcb867f75ed064f5c7f81603d10246e1fe51b2d03922ee5c544ab4f';
 const names=['L1','L2','Mi1','Tm3','Tm1','Tm2','T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];
 const colors=['#e4c071','#71c9ed','#76ddba','#a8e0b4','#e1a4be','#c8a8e2','#6bdbc1','#80c9e4','#d6bd85','#b6a1e4','#e09eb4','#ccb977','#91b8dc','#bbcbd3'];
 const hints=['看亮暗切换的早期变化','看亮暗切换的早期变化','重点看变亮（黑→白）','重点看变亮（黑→白）','重点看变暗（白→黑）','重点看变暗（白→黑）','亮边向左 ←（180°）','亮边向右 →（0°）','亮边向上 ↑（90°）','亮边向下 ↓（270°）','暗边向左 ←（180°）','暗边向右 →（0°）','暗边向上 ↑（90°）','暗边向下 ↓（270°）'];
 const check=(ok,msg)=>{if(!ok)throw Error(msg);};
 function sample(p){
  const o=p.observer;check(o?.schema==='line11-neuron-observer/v2'&&o.map_sha256===MAP,'观察数据版本不符');
  check(o.step_id===p.step_id&&o.state_sha256===p.state_token&&Number.isSafeInteger(p.step_id)&&Number.isFinite(p.activity_time_s),'观察数据与神经步不符');
  for(const a of [o.means,o.reference])check(Array.isArray(a)&&a.length===2&&a.every(r=>Array.isArray(r)&&r.length===14&&r.every(Number.isFinite)),'观察值无效');
  check(o.reference_step_id===0&&/^[a-f0-9]{64}$/.test(o.reference_state_sha256),'参考记录不符');
  return {step:p.step_id,time:p.activity_time_s,means:o.means,reference:o.reference,referenceSha:o.reference_state_sha256};
 }
 class History{
  constructor(){this.run=null;this.rows=new Map();this.referenceSha=null;}
  add(p){const x=sample(p);const run=p.session_id+':'+p.run_id;if(this.run!==run){this.run=run;this.rows.clear();this.referenceSha=null;}
   check(!this.referenceSha||this.referenceSha===x.referenceSha,'本轮参考状态变化');this.referenceSha=x.referenceSha;
   this.rows.set(x.step,x);if(this.rows.size>4096)this.rows.delete(this.rows.keys().next().value);return x;
  }
 }
 function values(row,roi,relative){return row.means[roi].map((v,i)=>relative?v-row.reference[roi][i]:v);}
 function aggregate(v,index){return index===14?v.slice(6,10).reduce((a,b)=>a+b,0)/4:index===15?v.slice(10,14).reduce((a,b)=>a+b,0)/4:v[index];}
 function draw(canvas,rows,indices,labels,domain,roi,relative,columns){
  const w=canvas.width=Math.max(240,Math.round(canvas.clientWidth)),h=canvas.height=Math.max(80,Math.round(canvas.clientHeight));const ctx=canvas.getContext('2d');ctx.clearRect(0,0,w,h);
  const plotted=rows.map(r=>({...r,plot:values(r,roi,relative)}));rows=plotted;
  const cols=w<450?1:columns,cellW=w/cols,cellH=h/Math.ceil(indices.length/cols),end=Math.max(.1,rows.at(-1)?.time||1);
  indices.forEach((index,i)=>{const left=(i%cols)*cellW,top=Math.floor(i/cols)*cellH,x=left+72,y=top+86,cw=cellW-90,ch=Math.max(20,cellH-122),color=colors[index%14];
   const val=rows.length?aggregate(rows.at(-1).plot,index):null;
   ctx.fillStyle=color;ctx.font='600 32px system-ui';ctx.fillText(labels[i],left+10,top+36);ctx.textAlign='right';ctx.font='27px system-ui';ctx.fillText(val===null?'等待记录':(val>=0?'+':'')+val.toFixed(3),left+cellW-12,top+36);ctx.textAlign='left';
   ctx.fillStyle='#a9c2d0';ctx.font='19px system-ui';ctx.fillText(hints[index],left+10,top+64);
   const px=t=>x+cw*t/end,py=v=>y+ch*(1-Math.max(-domain,Math.min(domain,v))/domain)/2;
   ctx.font='19px system-ui';for(const a of [-domain,0,domain]){ctx.strokeStyle=a===0?'#466171':'#263c4a';ctx.beginPath();ctx.moveTo(x,py(a));ctx.lineTo(x+cw,py(a));ctx.stroke();ctx.fillStyle='#8ca6b5';ctx.fillText(a.toFixed(domain<.1?3:2),left+3,py(a)+3);}
   ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=2.3;ctx.beginPath();rows.forEach((r,j)=>{const v=aggregate(r.plot,index);if(j&&r.step===rows[j-1].step+1)ctx.lineTo(px(r.time),py(v));else ctx.moveTo(px(r.time),py(v));});ctx.stroke();
   for(const r of rows){ctx.beginPath();ctx.arc(px(r.time),py(aggregate(r.plot,index)),1.7,0,Math.PI*2);ctx.fill();}
   ctx.fillStyle='#8ca6b5';ctx.fillText('0',x,y+ch+27);ctx.textAlign='right';ctx.fillText(end.toFixed(2)+' s 模型时间',x+cw,y+ch+27);ctx.textAlign='left';
   if(rows.some(r=>Math.abs(aggregate(r.plot,index))>domain)){ctx.fillStyle='#f1bf88';ctx.fillText('超出刻度，原值保留',x,y+12);}
  });
  canvas.dataset.samples=String(rows.length);canvas.dataset.roi=String(roi);canvas.dataset.relative=String(relative);
 }
 function start(map){
  const $=id=>document.getElementById(id),history=new History();let motion=false,current=null,baseline=null,baselineMeans=null,tiles=[],zoom=null;
  check(JSON.stringify(map.types)===JSON.stringify(names)&&map.regions.length===2&&map.regions[0].count===37&&map.regions[1].count===721,'观察区域映射不符');
  function redraw(){const roi=Number($('observerRoi').value),relative=$('observerReference').value==='selected'&&baseline!==null,rows=[...history.rows.values()].sort((a,b)=>a.step-b.step).map(r=>relative?{...r,reference:baselineMeans}:r);let domain=Number($('groupScale').value);
   if(!Number.isFinite(domain)||domain<=0){domain=.05;for(const row of rows)for(const v of values(row,roi,relative))domain=Math.max(domain,Math.abs(v)*1.08);}
   const indices=motion?[6,7,8,9,10,11,12,13]:[0,2,4,1,3,5];
   if($('groupScale').value==='auto'&&current)for(let i=0;i<current.values.length;i++)domain=Math.max(domain,Math.abs(current.values[i]-(relative?baseline.values[i]:0))*1.08);
   if($('heatmaps').getClientRects().length)tiles=HeatmapUI.draw($('heatmaps'),current,relative?baseline:null,indices,names,domain,roi);
   $('heatTitle').textContent=motion?'02 / T4 · T5空间响应':'02 / 亮暗通路空间响应';
   $('heatScale').textContent='蓝 −'+domain.toFixed(2)+'　浅色 0　红 +'+domain.toFixed(2);
   $('heatCaption').textContent=(relative?'相对选定基线：第'+(baseline.step+1)+'步':'原始有符号状态 · 未设置静止基线')+' · 全部721个/类 · 同一步 · '+($('heatmaps').dataset.clipped!=='0'?'有超出色标的值，原值保留':'点击图放大');
   $('setBaseline').disabled=!current;
   if(zoom!==null){HeatmapUI.draw($('heatZoomCanvas'),current,relative?baseline:null,[zoom],names,domain,roi);$('heatZoomTitle').textContent=names[zoom]+' · '+(current?'第'+(current.step+1)+'步':'等待记录')+' · 统一色标 ±'+domain.toFixed(2);}
   $('groups').closest('.group-panel').dataset.mode=motion?'motion':'brightness';
   draw($('groups'),rows,indices,indices.map(i=>names[i]),domain,roi,relative,motion?4:3);
   $('groups').dataset.visibleTypes=JSON.stringify(indices.map(i=>names[i]));
   $('groupTitle').textContent=motion?'T4 · T5运动响应 · 8个亚型':'亮度响应 · 6类神经元';
   $('switchCharts').textContent=motion?'切换到亮度响应（6图）':'切换到T4/T5运动响应（8图）';
   $('chartGuide').textContent=motion?'官方优选方向（按左侧输入画面）：a ←左，b →右，c ↑上，d ↓下。T4看亮边、T5看暗边；本次是否符合须看实际响应。':'L1/L2看亮暗变化；Mi1/Tm3重点看变亮；Tm1/Tm2重点看变暗。这里是观察重点，不保证曲线一定上升。';
   $('observerCaption').textContent=(roi===0?'中央37个 / 每类 · 适合局部刺激':'全部721个 / 每类 · 整幅平均，局部响应可能被稀释')+' · '+(relative?'相对选定基线（第'+(baseline.step+1)+'步）':'原始有符号状态（模型单位）')+' · 仅已显示步骤，跳帧留空';
   document.querySelector('.roi-legend').textContent=roi===0?'◯ 蓝绿圈 = 中央37个位置 · 不改变输入':'全部 = 每类721个位置分别取平均 · 不改变输入';
   const overlay=$('roiOverlay'),ctx=overlay.getContext('2d');ctx.clearRect(0,0,417,417);ctx.strokeStyle='#7ef5d3';ctx.lineWidth=1.2;
   if(roi===0)for(const [x,y] of map.regions[0].pixels){ctx.beginPath();ctx.arc(x,y,6.5,0,Math.PI*2);ctx.stroke();}
  }
  for(const id of ['observerRoi','observerReference','groupScale'])$(id).onchange=redraw;
  $('switchCharts').onclick=()=>{motion=!motion;redraw();};
  $('setBaseline').onclick=()=>{if(!current)return;baseline={...current,values:current.values.slice()};baselineMeans=history.rows.get(current.step).means.map(x=>x.slice());$('selectedReference').disabled=false;$('observerReference').value='selected';redraw();};
  $('heatmaps').onclick=e=>{if(!current)return;const b=$('heatmaps').getBoundingClientRect(),x=(e.clientX-b.left)*$('heatmaps').width/b.width,y=(e.clientY-b.top)*$('heatmaps').height/b.height;const tile=tiles.find(q=>x>=q.left&&x<q.left+q.cw&&y>=q.top&&y<q.top+q.ch);if(tile){zoom=tile.index;$('heatZoom').showModal();redraw();}};
  $('closeHeatZoom').onclick=()=>{zoom=null;$('heatZoom').close();};
  $('heatmaps').onmousemove=e=>{if(!current)return;const b=$('heatmaps').getBoundingClientRect(),x=(e.clientX-b.left)*$('heatmaps').width/b.width,y=(e.clientY-b.top)*$('heatmaps').height/b.height;const q=tiles.find(q=>x>=q.left&&x<q.left+q.cw&&y>=q.top&&y<q.top+q.ch);if(!q)return;let nearest=0,dist=Infinity;HeatmapUI.xy.forEach(([px,py],k)=>{const dd=(x-q.sx-px*q.size/417)**2+(y-q.sy-py*q.size/417)**2;if(dd<dist){nearest=k;dist=dd;}});const v=current.values[q.index*721+nearest],rel=$('observerReference').value==='selected'&&baseline; $('heatmaps').title=names[q.index]+' · 节点 '+map.regions[1].ids[q.index][nearest]+' · 原始 '+v.toFixed(6)+(rel?' · 变化 '+(v-baseline.values[q.index*721+nearest]).toFixed(6):'');};
  window.addEventListener('resize',redraw);redraw();return {add:(p,spatial)=>{sample(p);check(spatial&&spatial.step===p.step_id&&spatial.state===p.state_token&&spatial.run===p.session_id+':'+p.run_id,'热力图与曲线身份不符');if(current&&current.run!==spatial.run){baseline=null;baselineMeans=null;$('observerReference').value='raw';$('selectedReference').disabled=true;}history.add(p);current=spatial;redraw();},history,redraw};
 }
 return {sample,History,values,aggregate,start,MAP};
})();
if(typeof module!=='undefined')module.exports=ObserverUI;
