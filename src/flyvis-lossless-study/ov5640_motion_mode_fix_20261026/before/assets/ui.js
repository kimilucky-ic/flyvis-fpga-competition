/* Central ROI readout retained from the original competition page. */
const fail=(ok,message)=>{if(!ok)throw Error(message);};
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

class GroupHistory {
 constructor(){this.run=null;this.samples=new Map();}
 add(packet){const point=groupSample(packet);if(this.run!==packet.run_id){this.run=packet.run_id;this.samples.clear();}this.samples.set(point.step,point);if(this.samples.size>4096)this.samples.delete(this.samples.keys().next().value);return point;}
}
if(typeof window!=='undefined')window.FlyVisFullPLGroups={groupSample};
function drawGroups(canvas,history,domain=1){
 canvas.width=Math.max(320,Math.round(canvas.clientWidth));canvas.height=Math.max(250,Math.round(canvas.clientHeight));
 const ctx=canvas.getContext('2d'),w=canvas.width,h=canvas.height,rows=[...history.samples.values()].sort((a,b)=>a.step-b.step);if(!rows.length)return;
 const point=rows[rows.length-1],types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'],colors=['#efc65b','#5edce9','#5fe2b0','#b89aff','#ef8db5','#dcce66','#98c5fa','#c6dce9'];
 const end=Math.max(1,point.time),start=0,columns=w<480?1:w<900?2:4,cellW=w/columns,cellH=h/(8/columns);
 ctx.clearRect(0,0,w,h);ctx.fillStyle='#101923';ctx.fillRect(0,0,w,h);
 types.forEach((type,i)=>{const left=(i%columns)*cellW,top=Math.floor(i/columns)*cellH,x=left+42,y=top+45,cw=cellW-62,ch=cellH-76;
 ctx.fillStyle=colors[i];ctx.font='bold 19px system-ui';ctx.fillText(type,left+14,top+25);ctx.font='15px system-ui';ctx.textAlign='right';ctx.fillText((point.raw[i]>=0?'+':'')+point.raw[i].toFixed(3),left+cellW-15,top+25);ctx.textAlign='left';
 ctx.font='11px system-ui';ctx.fillStyle='#8fa7b8';ctx.strokeStyle='#2b4353';ctx.lineWidth=1;
 for(const value of [0,domain/2,domain]){const yy=y+ch-ch*value/domain;ctx.beginPath();ctx.moveTo(x,yy);ctx.lineTo(x+cw,yy);ctx.stroke();ctx.fillText(String(value),left+7,yy+4);}
 const px=t=>x+cw*(t-start)/(end-start),py=v=>y+ch-ch*Math.min(domain,Math.max(0,v))/domain;
 ctx.strokeStyle=colors[i];ctx.lineWidth=2;ctx.beginPath();rows.forEach((r,j)=>{if(j&&r.step-rows[j-1].step<=10)ctx.lineTo(px(r.time),py(r.values[i]));else ctx.moveTo(px(r.time),py(r.values[i]));});ctx.stroke();ctx.fillStyle=colors[i];ctx.beginPath();ctx.arc(px(point.time),py(point.values[i]),3,0,Math.PI*2);ctx.fill();
 ctx.fillStyle='#8fa7b8';ctx.fillText('0',x,y+ch+18);ctx.textAlign='right';ctx.fillText(end.toFixed(2)+' s 模型时间',x+cw,y+ch+18);ctx.textAlign='left';
 if(rows.some(r=>r.values[i]>domain)){ctx.fillStyle='#ffbc91';ctx.font='11px system-ui';ctx.fillText('↑ 有超出刻度的值，原值保留',x,y+12);}
 });
 Object.assign(canvas.dataset,{run:history.run,step:String(point.step),samples:String(rows.length),signedMeans:JSON.stringify(point.raw),scale:String(domain),roiCount:'37'});
}
/* Read-only latest-frame consumer: no STEP/retry/control API. */
class DisplayCursor {
 constructor(){this.session=null;this.last=-1;this.shown=0;this.skipped=0;}
 accepts(p){if(this.session&&p.session_id!==this.session)throw Error('显示会话改变，拒绝混合');return p.step_id>this.last;}
 commit(p){if(!this.accepts(p))return false;this.skipped+=p.step_id-this.last-1;this.last=p.step_id;this.session=p.session_id;this.shown++;return true;}
}
function displayDelay(workMs,{paused=false,hidden=false,finished=false,failed=false}={}){
 const period=failed||hidden||finished?1000:paused?500:55;
 return Math.max(8,period-Math.max(0,workMs));
}
class DisplayMetrics {
 constructor(){this.rows=[];this.lastPaint=null;this.session=null;}
 add(row){if(this.session&&this.session!==row.session_id)throw Error('显示计时会话不一致');this.session=row.session_id;
  if(row.painted){row.paint_interval_ms=this.lastPaint===null?null:row.paint_at_ms-this.lastPaint;this.lastPaint=row.paint_at_ms;}
  this.rows.push(row);if(this.rows.length>4096)this.rows.shift();
 }
 summary(){const paints=this.rows.filter(r=>r.painted),intervals=paints.map(r=>r.paint_interval_ms).filter(Number.isFinite);
  const mean=key=>paints.length?paints.reduce((v,r)=>v+(r[key]||0),0)/paints.length:0;
  return {painted:paints.length,mean_interval_ms:intervals.length?intervals.reduce((a,b)=>a+b,0)/intervals.length:null,fetch_ms:mean('fetch_ms'),image_ms:mean('image_ms'),skeleton_ms:mean('skeleton_ms'),paint_ms:mean('paint_ms'),cycle_ms:mean('cycle_ms')};
 }
}
if(typeof module!=='undefined')module.exports={DisplayCursor,groupSample,GroupHistory,displayDelay,DisplayMetrics};
if(typeof document!=='undefined') (async()=>{
 const $=id=>document.getElementById(id),cursor=new DisplayCursor(),groups=new GroupHistory(),metrics=new DisplayMetrics();let paused=false,projection=null,currentSession=null,creating=false;
 $('groupScale').onchange=()=>drawGroups($('groups'),groups,Number($('groupScale').value));
 window.addEventListener('resize',()=>drawGroups($('groups'),groups,Number($('groupScale').value)));
 $('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch(e){$('liveSummary').textContent='浏览器未启用全屏，可按F11进入全屏展示。';}};
 document.addEventListener('fullscreenchange',()=>{$('fullscreen').textContent=document.fullscreenElement?'退出全屏':'全屏展示';});
 $('detailsButton').onclick=()=>$('details').showModal();$('closeDetails').onclick=()=>$('details').close();
 $('nextRound').onclick=async()=>{if(creating||!currentSession)return;creating=true;$('nextRound').disabled=true;try{const response=await fetch('/next-round',{method:'POST',headers:{'Content-Type':'application/json','X-Line11-UI':'1'},body:JSON.stringify({session_id:currentSession,motion_condition:$('motionCondition').value})});const result=await response.json();if(!response.ok)throw Error(result.error||'创建失败');location.reload();}catch(e){$('liveSummary').textContent='未切换新一轮：'+e.message+'；可刷新查看当前会话。';}finally{creating=false;}};
 $('toggle').onclick=()=>{paused=!paused;$('toggle').textContent=paused?'继续显示':'暂停显示';};
 try{projection=await FlyVisFixedSkeleton.load(await (await fetch('/projection')).json());}
 catch(e){$('error').textContent='骨架资源校验失败：'+e;return;}
 $('exportDisplayTiming').onclick=()=>{const data={schema:'line11-browser-display-timing/v1',evidence:'BROWSER_DISPLAY_ONLY_NOT_CAMERA_TO_SCREEN_LATENCY',session_id:currentSession,summary:metrics.summary(),rows:metrics.rows};
  const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='LINE11_DISPLAY_'+(currentSession||'waiting').slice(0,8)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 async function poll(){
  const cycleStart=performance.now(),row={started_unix_ms:Date.now(),painted:false};let finished=false,failed=false;
  try{
   const wasPaused=paused||document.hidden;
   const response=await fetch(wasPaused?'/status':'/latest?after='+cursor.last,{cache:'no-store'});if(!response.ok)throw Error('电脑接收程序不可用');
   const body=await response.json(),p=wasPaused?null:body.packet,s=wasPaused?body:body.status;row.fetch_ms=performance.now()-cycleStart;row.session_id=s.session_id;row.received=s.received;finished=s.finished;
   if(currentSession&&currentSession!==s.session_id){location.reload();return;}currentSession=s.session_id;
   $('nextRound').disabled=creating||s.next_round_allowed!==true;
   $('nextRound').title=s.next_round_reason||'新功能需要重新启动电脑接收窗口';
   $('roundNotebook').download='LINE11_START_60S.ipynb';
   $('status').textContent=`电脑已保存 ${s.received} 步（60秒有界运行）；全状态验收：${s.audit_status} · ${s.audited_steps??0}/${s.received} 步`+
       (s.mismatch_words!==null?`，差异 ${s.mismatch_words} 项`:'')+`\n板端状态：${s.producer_status||'等待/运行中，尚未收到计算完成记录'}`+`\n相机关闭：${s.camera_close_status==='CLOSED'?'已确认':s.camera_close_status==='FAILED'?'失败，保留内核与缓冲区':'尚未确认，不代表已关闭'}`;
   if(['FAIL_NUMERICAL_MISMATCH','AUDIT_ERROR'].includes(s.audit_status))throw Error('数值验收异常，停止展示新帧；保留全部记录');
   $('liveSummary').textContent=s.finished?`本轮已结束 · ${s.received} 步 · ${s.audit_status==='PASS_ALL_SAVED_STATES'?'全状态验收通过':'正在验收 '+(s.audited_steps??0)+'/'+s.received+' 步'} · 当前为保存帧`:`已接收 ${s.received} 步 · ${!s.last_received_unix||Date.now()/1000-s.last_received_unix>3?'等待新记录 / 保存帧':'接收中 · 已验收 '+(s.audited_steps??0)+' 步'}`;
   $('liveSummary').textContent='会话 '+s.session_id.slice(0,8)+' · '+({'white_black':'白底黑条 · ','black_white':'黑底白条 · '}[s.motion_condition]||'')+$('liveSummary').textContent;
   if(s.evidence==='CPU_MOCK_ONLY')$('liveSummary').textContent='CPU模拟验证，非实板实验 · '+$('liveSummary').textContent;
   $('signal').style.background=s.audit_status==='PASS_ALL_SAVED_STATES'?'#71dccb':'#e7bb7c';
   const stale=!s.last_received_unix||Date.now()/1000-s.last_received_unix>3||s.finished;
   document.body.classList.toggle('stale',stale||paused);
   $('error').textContent=s.finished?'本轮记录已接收，当前为最后保存帧；相机关闭状态单独显示。':(stale?'暂未收到新帧；当前画面是保存帧，未宣称相机仍在更新。':'数值验收完成前，画面标记为待验收。');
   if(p&&!paused&&cursor.accepts(p)){
    const begin=performance.now(),image=new Image();image.src='/frame.png?step='+p.step_id+'&state='+p.state_token;
    groupSample(p); // Validate ROI before touching the visible frame.
    const rawImage=p.camera_png?new Image():null;if(rawImage)rawImage.src=p.camera_png;
    const rawReady=rawImage?rawImage.decode():Promise.resolve();
    const imageReady=image.decode().then(()=>{row.image_ms=performance.now()-begin;});
    const boneBegin=performance.now();
    const boneReady=projection.render(p,'live-'+p.step_id,'CENTRAL_ROI37_T4T5').then(r=>{row.skeleton_ms=performance.now()-boneBegin;return r;});
    const [,r]=await Promise.all([imageReady,boneReady,rawReady]);
    // One in-flight frame, no display queue. Recheck pause after async work.
    if(!paused&&!document.hidden&&currentSession===p.session_id){
     const paintStart=performance.now();
     $('rawCamera').hidden=!rawImage;if(rawImage)$('rawCamera').src=rawImage.src;
     $('experimentCue').textContent=p.experiment?`${p.experiment.label} · 采集计时 ${(p.experiment.elapsed_ns/1e9).toFixed(1)}秒\n${p.experiment.cue}\n这是该帧的计划提示；非实际边缘事件。右下角：同一步原始采集帧。`:'中央正方形视野 · 灰度输入 · 无补灰';
     $('camera').src=image.src;$('neural').getContext('2d').putImageData(new ImageData(r.pixels,r.width,r.height),0,0);
     groups.add(p);drawGroups($('groups'),groups,Number($('groupScale').value));
     cursor.commit(p);row.paint_ms=performance.now()-paintStart;row.paint_at_ms=performance.now();row.painted=true;row.step_id=p.step_id;
     $('display').textContent=`显示 ${cursor.shown} 帧 · 跳过 ${cursor.skipped} 帧 · 当前神经步 ${p.step_id+1}`;
     $('timing').textContent=`核心名义时间 ${p.timing.core_counter_nominal_ms?.toFixed(3)} ms；取帧 ${p.timing.capture_and_cache_ms?.toFixed(1)} ms；PS映射 ${p.timing.ps_mapping_ms?.toFixed(1)} ms\n输入/STEP/发布 ${p.timing.input_upload_step_and_publication_ms?.toFixed(1)} ms；DDR复制 ${p.timing.ddr_copy_and_cache_ms?.toFixed(1)} ms\n网页取数 ${row.fetch_ms.toFixed(1)} ms；输入图准备 ${row.image_ms.toFixed(1)} ms；骨架准备 ${row.skeleton_ms.toFixed(1)} ms；绘制 ${row.paint_ms.toFixed(1)} ms（准备阶段并行，不能相加）`;
    }
   }
  }catch(e){failed=true;$('liveSummary').textContent='连接中断或显示异常 · 当前为保存帧';$('signal').style.background='#edbe88';document.body.classList.add('stale');$('error').textContent='显示暂停/连接中断：'+e+'。只会重新读取保存帧，不会重算神经步。';}
  row.cycle_ms=performance.now()-cycleStart;
  if(row.session_id){metrics.add(row);const m=metrics.summary();$('displayTiming').textContent=`本页绘制 ${m.painted} 帧；平均更新间隔 ${m.mean_interval_ms===null?'—':m.mean_interval_ms.toFixed(1)+' ms'}；平均取数 ${m.fetch_ms.toFixed(1)} ms / 骨架准备 ${m.skeleton_ms.toFixed(1)} ms / 绘制 ${m.paint_ms.toFixed(1)} ms。仅网页侧计时，不是摄像头到屏幕延迟。`;}
  setTimeout(poll,displayDelay(performance.now()-cycleStart,{paused,hidden:document.hidden,finished,failed}));
 }
 poll();
})();
