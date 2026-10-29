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
 canvas.width=canvas.clientWidth<480?320:canvas.clientWidth<900?640:1280;canvas.height=8/(canvas.width/320)*180;
 const ctx=canvas.getContext('2d'),w=canvas.width,h=canvas.height,rows=[...history.samples.values()].sort((a,b)=>a.step-b.step);if(!rows.length)return;
 const point=rows[rows.length-1],types=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'],colors=['#efc65b','#5edce9','#5fe2b0','#b89aff','#ef8db5','#dcce66','#98c5fa','#c6dce9'];
 const end=Math.max(1,point.time),start=0,columns=w/320,cellW=w/columns,cellH=h/(8/columns);
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
if(typeof module!=='undefined')module.exports={DisplayCursor,groupSample,GroupHistory};
if(typeof document!=='undefined') (async()=>{
 const $=id=>document.getElementById(id),cursor=new DisplayCursor(),groups=new GroupHistory();let paused=false,projection=null;
 $('groupScale').onchange=()=>drawGroups($('groups'),groups,Number($('groupScale').value));
 window.addEventListener('resize',()=>drawGroups($('groups'),groups,Number($('groupScale').value)));
 $('toggle').onclick=()=>{paused=!paused;$('toggle').textContent=paused?'继续显示':'暂停显示';};
 try{projection=await FlyVisFixedSkeleton.load(await (await fetch('/projection')).json());}
 catch(e){$('error').textContent='骨架资源校验失败：'+e;return;}
 async function poll(){
  try{
   const wasPaused=paused;
   const response=await fetch(wasPaused?'/status':'/latest?after='+cursor.last,{cache:'no-store'});if(!response.ok)throw Error('电脑接收程序不可用');
   const body=await response.json(),p=wasPaused?null:body.packet,s=wasPaused?body:body.status;
   $('status').textContent=`电脑已保存 ${s.received} 步（60秒有界运行）；全状态验收：${s.audit_status}`+
       (s.mismatch_words!==null?`，差异 ${s.mismatch_words} 项`:'')+`\n板端状态：${s.producer_status||'等待/运行中，尚未收到计算完成记录'}`+`\n相机关闭：${s.camera_close_status==='CLOSED'?'已确认':s.camera_close_status==='FAILED'?'失败，保留内核与缓冲区':'尚未确认，不代表已关闭'}`;
   if(['FAIL_NUMERICAL_MISMATCH','AUDIT_ERROR'].includes(s.audit_status))throw Error('数值验收异常，停止展示新帧；保留全部记录');
   const stale=!s.last_received_unix||Date.now()/1000-s.last_received_unix>3||s.finished;
   document.body.classList.toggle('stale',stale||paused);
   $('error').textContent=s.finished?'本轮记录已接收，当前为最后保存帧；相机关闭状态单独显示。':(stale?'暂未收到新帧；当前画面是保存帧，未宣称相机仍在更新。':'数值验收完成前，画面标记为待验收。');
   if(p&&!paused&&cursor.accepts(p)){
    const begin=performance.now(),image=new Image();image.src='/frame.png?step='+p.step_id+'&state='+p.state_token;
    await image.decode();const r=await projection.render(p,'live-'+p.step_id,'CENTRAL_ROI37_T4T5');
    // Both images become visible only after the matching source and activity are ready.
    $('camera').src=image.src;$('neural').getContext('2d').putImageData(new ImageData(r.pixels,r.width,r.height),0,0);
    groups.add(p);drawGroups($('groups'),groups,Number($('groupScale').value));
    cursor.commit(p);$('display').textContent=`显示 ${cursor.shown} 帧 · 跳过 ${cursor.skipped} 帧 · 当前神经步 ${p.step_id+1}`;
    $('timing').textContent=`核心名义时间 ${p.timing.core_counter_nominal_ms?.toFixed(3)} ms；取帧 ${p.timing.capture_and_cache_ms?.toFixed(1)} ms；PS映射 ${p.timing.ps_mapping_ms?.toFixed(1)} ms\n输入/STEP/发布 ${p.timing.input_upload_step_and_publication_ms?.toFixed(1)} ms；DDR复制 ${p.timing.ddr_copy_and_cache_ms?.toFixed(1)} ms；步骤及记录 ${(p.timing.bridge_step_and_ram_record_ms??p.timing.bridge_step_and_durable_record_ms)?.toFixed(1)} ms\n本次浏览器取图和绘制 ${(performance.now()-begin).toFixed(1)} ms（独立计时，不代表跨设备单向延迟）`;
   }
  }catch(e){document.body.classList.add('stale');$('error').textContent='显示暂停/连接中断：'+e+'。只会重新读取保存帧，不会重算神经步。';}
  setTimeout(poll,150);
 }
 poll();
})();
