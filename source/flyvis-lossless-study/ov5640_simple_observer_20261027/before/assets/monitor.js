/* Actual saved full-state observations; no model inference or board commands. */
const ObserverUI=(()=>{
 const MAP='4282f4524df248aa27a313768813fe2062c6d4f3633db4470e5d6c1291360dc8';
 const names=['L1','L2','Mi1','Tm3','Tm1','Tm2','T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'];
 const colors=['#e4c071','#71c9ed','#76ddba','#a8e0b4','#e1a4be','#c8a8e2','#6bdbc1','#80c9e4','#d6bd85','#b6a1e4','#e09eb4','#ccb977','#91b8dc','#bbcbd3'];
 const check=(ok,msg)=>{if(!ok)throw Error(msg);};
 function sample(p){
  const o=p.observer;check(o?.schema==='line11-neuron-observer/v1'&&o.map_sha256===MAP,'观察数据版本不符');
  check(o.step_id===p.step_id&&o.state_sha256===p.state_token&&Number.isSafeInteger(p.step_id)&&Number.isFinite(p.activity_time_s),'观察数据与神经步不符');
  for(const a of [o.means,o.reference])check(Array.isArray(a)&&a.length===5&&a.every(r=>Array.isArray(r)&&r.length===14&&r.every(Number.isFinite)),'观察值无效');
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
  const cols=w<450?Math.min(2,columns):columns,cellW=w/cols,cellH=h/Math.ceil(indices.length/cols),end=Math.max(.1,rows.at(-1)?.time||1);
  indices.forEach((index,i)=>{const left=(i%cols)*cellW,top=Math.floor(i/cols)*cellH,x=left+43,y=top+30,cw=cellW-58,ch=Math.max(20,cellH-50),color=colors[index%14];
   const val=rows.length?aggregate(rows.at(-1).plot,index):null;
   ctx.fillStyle=color;ctx.font='600 15px system-ui';ctx.fillText(labels[i],left+10,top+19);ctx.textAlign='right';ctx.font='13px system-ui';ctx.fillText(val===null?'等待记录':(val>=0?'+':'')+val.toFixed(3),left+cellW-12,top+19);ctx.textAlign='left';
   const px=t=>x+cw*t/end,py=v=>y+ch*(1-Math.max(-domain,Math.min(domain,v))/domain)/2;
   ctx.font='10px system-ui';for(const a of [-domain,0,domain]){ctx.strokeStyle=a===0?'#466171':'#263c4a';ctx.beginPath();ctx.moveTo(x,py(a));ctx.lineTo(x+cw,py(a));ctx.stroke();ctx.fillStyle='#8ca6b5';ctx.fillText(a.toFixed(domain<.1?3:2),left+3,py(a)+3);}
   ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=1.5;ctx.beginPath();rows.forEach((r,j)=>{const v=aggregate(r.plot,index);if(j&&r.step===rows[j-1].step+1)ctx.lineTo(px(r.time),py(v));else ctx.moveTo(px(r.time),py(v));});ctx.stroke();
   for(const r of rows){ctx.beginPath();ctx.arc(px(r.time),py(aggregate(r.plot,index)),1.25,0,Math.PI*2);ctx.fill();}
   ctx.fillStyle='#8ca6b5';ctx.fillText('0',x,y+ch+13);ctx.textAlign='right';ctx.fillText(end.toFixed(2)+' s 模型时间',x+cw,y+ch+13);ctx.textAlign='left';
   if(rows.some(r=>Math.abs(aggregate(r.plot,index))>domain)){ctx.fillStyle='#f1bf88';ctx.fillText('超出刻度，原值保留',x,y+12);}
  });
  canvas.dataset.samples=String(rows.length);canvas.dataset.roi=String(roi);canvas.dataset.relative=String(relative);
 }
 function start(map){
  const $=id=>document.getElementById(id),history=new History();check(JSON.stringify(map.types)===JSON.stringify(names)&&map.regions.length===5,'观察区域映射不符');
  const selected=new Set([0,1,2,3,4,5]);let collapsed=false;
  function redraw(){const roi=Number($('observerRoi').value),relative=$('observerReference').value==='first',rows=[...history.rows.values()].sort((a,b)=>a.step-b.step);let domain=Number($('groupScale').value);
   if(!Number.isFinite(domain)||domain<=0){domain=.05;for(const row of rows)for(const v of values(row,roi,relative))domain=Math.max(domain,Math.abs(v)*1.08);}
   const indices=[0,2,4,1,3,5].filter(i=>selected.has(i)),closed=collapsed||!indices.length;
   $('earlyCharts').hidden=closed;$('emptyGroups').hidden=collapsed||!!indices.length;
   $('groups').closest('.group-panel').dataset.collapsed=String(closed);
   $('collapseGroups').setAttribute('aria-expanded',String(!collapsed));$('collapseGroups').textContent=collapsed?'展开03':'收起03';
   if(!closed)draw($('groups'),rows,indices,indices.map(i=>names[i]+' · '+(i<2?'早期':i<4?'ON相关':'OFF相关')),domain,roi,relative,indices.length<=2?indices.length:indices.length<=4?2:3);
   $('groups').dataset.visibleTypes=JSON.stringify(indices.map(i=>names[i]));

   draw($('motionSummary'),rows,[14,15],['T4 · 四亚型均值','T5 · 四亚型均值'],domain,roi,relative,2);
   for(const key of ['T4','T5'])if(!$('detail'+key).hidden){const n=key==='T4'?6:10;draw($('chart'+key),rows,[n,n+1,n+2,n+3],names.slice(n,n+4),domain,roi,relative,4);}
   $('observerCaption').textContent=map.regions[roi].label+'37细胞 / 每亚型 · '+(relative?'减去本轮首步均值（不代表静止基线）':'原始有符号状态均值（模型单位，非校准mV）')+' · 蓝绿圈为对应视野位置 · 仅已显示步骤，跳帧留空';
   const overlay=$('roiOverlay'),ctx=overlay.getContext('2d');ctx.clearRect(0,0,417,417);ctx.strokeStyle='#7ef5d3';ctx.lineWidth=1.2;for(const [x,y] of map.regions[roi].pixels){ctx.beginPath();ctx.arc(x,y,6.5,0,Math.PI*2);ctx.stroke();}
  }
  names.slice(0,6).forEach((name,i)=>{$('curve'+name).onclick=()=>{selected.has(i)?selected.delete(i):selected.add(i);$('curve'+name).setAttribute('aria-pressed',String(selected.has(i)));if(selected.has(i))collapsed=false;redraw();};});
  $('collapseGroups').onclick=()=>{collapsed=!collapsed;redraw();};
  for(const id of ['observerRoi','observerReference','groupScale'])$(id).onchange=redraw;
  for(const key of ['T4','T5'])$('expand'+key).onclick=()=>{const e=$('detail'+key),b=$('expand'+key);e.hidden=!e.hidden;b.setAttribute('aria-expanded',String(!e.hidden));b.textContent=(e.hidden?'展开 ':'收起 ')+key+' a–d';redraw();};
  window.addEventListener('resize',redraw);redraw();return {add:p=>{history.add(p);redraw();},history,redraw};
 }
 return {sample,History,values,aggregate,start,MAP};
})();
if(typeof module!=='undefined')module.exports=ObserverUI;
