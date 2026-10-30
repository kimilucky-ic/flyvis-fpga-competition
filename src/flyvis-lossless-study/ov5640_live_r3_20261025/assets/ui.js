/* Read-only latest-frame consumer: no STEP/retry/control API. */
class DisplayCursor {
 constructor(){this.session=null;this.last=-1;this.shown=0;this.skipped=0;}
 accepts(p){if(this.session&&p.session_id!==this.session)throw Error('显示会话改变，拒绝混合');return p.step_id>this.last;}
 commit(p){if(!this.accepts(p))return false;this.skipped+=p.step_id-this.last-1;this.last=p.step_id;this.session=p.session_id;this.shown++;return true;}
}
if(typeof module!=='undefined')module.exports={DisplayCursor};
if(typeof document!=='undefined') (async()=>{
 const $=id=>document.getElementById(id),cursor=new DisplayCursor();let paused=false,projection=null;
 $('toggle').onclick=()=>{paused=!paused;$('toggle').textContent=paused?'继续显示':'暂停显示';};
 try{projection=await FlyVisFixedSkeleton.load(await (await fetch('/projection')).json());}
 catch(e){$('error').textContent='骨架资源校验失败：'+e;return;}
 async function poll(){
  try{
   const wasPaused=paused;
   const response=await fetch(wasPaused?'/status':'/latest?after='+cursor.last,{cache:'no-store'});if(!response.ok)throw Error('电脑接收程序不可用');
   const body=await response.json(),p=wasPaused?null:body.packet,s=wasPaused?body:body.status;
   $('status').textContent=`电脑已保存 ${s.received}/${s.max_steps} 步；全状态验收：${s.audit_status}`+
       (s.mismatch_words!==null?`，差异 ${s.mismatch_words} 项`:'')+`\n板端状态：${s.producer_status||'等待/运行中，尚未收到正常关闭记录'}`;
   if(['FAIL_NUMERICAL_MISMATCH','AUDIT_ERROR'].includes(s.audit_status))throw Error('数值验收异常，停止展示新帧；保留全部记录');
   const stale=!s.last_received_unix||Date.now()/1000-s.last_received_unix>3||s.finished;
   document.body.classList.toggle('stale',stale||paused);
   $('error').textContent=s.finished?'本轮已经结束，当前为最后保存帧。':(stale?'暂未收到新帧；当前画面是保存帧，未宣称相机仍在更新。':'数值验收完成前，画面标记为待验收。');
   if(p&&!paused&&cursor.accepts(p)){
    const begin=performance.now(),image=new Image();image.src='/frame.png?step='+p.step_id+'&state='+p.state_token;
    await image.decode();const r=await projection.render(p,'live-'+p.step_id);
    // Both images become visible only after the matching source and activity are ready.
    $('camera').src=image.src;$('neural').getContext('2d').putImageData(new ImageData(r.pixels,r.width,r.height),0,0);
    cursor.commit(p);$('display').textContent=`显示 ${cursor.shown} 帧 · 跳过 ${cursor.skipped} 帧 · 当前神经步 ${p.step_id+1}`;
    $('timing').textContent=`核心名义时间 ${p.timing.core_counter_nominal_ms?.toFixed(3)} ms；取帧 ${p.timing.capture_and_cache_ms?.toFixed(1)} ms；PS映射 ${p.timing.ps_mapping_ms?.toFixed(1)} ms\n输入/STEP/发布 ${p.timing.input_upload_step_and_publication_ms?.toFixed(1)} ms；DDR复制 ${p.timing.ddr_copy_and_cache_ms?.toFixed(1)} ms；步骤及记录 ${p.timing.bridge_step_and_durable_record_ms?.toFixed(1)} ms\n本次浏览器取图和绘制 ${(performance.now()-begin).toFixed(1)} ms（独立计时，不代表跨设备单向延迟）`;
   }
  }catch(e){document.body.classList.add('stale');$('error').textContent='显示暂停/连接中断：'+e+'。只会重新读取保存帧，不会重算神经步。';}
  setTimeout(poll,150);
 }
 poll();
})();
