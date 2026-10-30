from pathlib import Path
P=Path('flyvis-lossless-study/ov5640_live_v261_20261026')
p=P/'assets/ui.js';s=p.read_text()
s=s.replace("if(typeof module!=='undefined')module.exports={DisplayCursor,groupSample,GroupHistory};",'''function displayDelay(workMs,{paused=false,hidden=false,finished=false,failed=false}={}){
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
if(typeof module!=='undefined')module.exports={DisplayCursor,groupSample,GroupHistory,displayDelay,DisplayMetrics};''')
s=s.replace("groups=new GroupHistory();let paused", "groups=new GroupHistory(),metrics=new DisplayMetrics();let paused")
s=s.replace(" async function poll(){\n  try{",''' $('exportDisplayTiming').onclick=()=>{const data={schema:'line11-browser-display-timing/v1',evidence:'BROWSER_DISPLAY_ONLY_NOT_CAMERA_TO_SCREEN_LATENCY',session_id:currentSession,summary:metrics.summary(),rows:metrics.rows};
  const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='LINE11_DISPLAY_'+(currentSession||'waiting').slice(0,8)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 async function poll(){
  const cycleStart=performance.now(),row={started_unix_ms:Date.now(),painted:false};let finished=false,failed=false;
  try{''')
s=s.replace("const wasPaused=paused;", "const wasPaused=paused||document.hidden;")
s=s.replace("const body=await response.json(),p=wasPaused?null:body.packet,s=wasPaused?body:body.status;", "const body=await response.json(),p=wasPaused?null:body.packet,s=wasPaused?body:body.status;row.fetch_ms=performance.now()-cycleStart;row.session_id=s.session_id;row.received=s.received;finished=s.finished;")
a=s.index("    const begin=performance.now(),image=new Image();")
b=s.index("   }\n  }catch(e)",a)
s=s[:a]+'''    const begin=performance.now(),image=new Image();image.src='/frame.png?step='+p.step_id+'&state='+p.state_token;
    groupSample(p); // Validate ROI before touching the visible frame.
    const imageReady=image.decode().then(()=>{row.image_ms=performance.now()-begin;});
    const boneBegin=performance.now();
    const boneReady=projection.render(p,'live-'+p.step_id,'CENTRAL_ROI37_T4T5').then(r=>{row.skeleton_ms=performance.now()-boneBegin;return r;});
    const [,r]=await Promise.all([imageReady,boneReady]);
    // One in-flight frame, no display queue. Recheck pause after async work.
    if(!paused&&!document.hidden&&currentSession===p.session_id){
     const paintStart=performance.now();
     $('camera').src=image.src;$('neural').getContext('2d').putImageData(new ImageData(r.pixels,r.width,r.height),0,0);
     groups.add(p);drawGroups($('groups'),groups,Number($('groupScale').value));
     cursor.commit(p);row.paint_ms=performance.now()-paintStart;row.paint_at_ms=performance.now();row.painted=true;row.step_id=p.step_id;
     $('display').textContent=`显示 ${cursor.shown} 帧 · 跳过 ${cursor.skipped} 帧 · 当前神经步 ${p.step_id+1}`;
     $('timing').textContent=`核心名义时间 ${p.timing.core_counter_nominal_ms?.toFixed(3)} ms；取帧 ${p.timing.capture_and_cache_ms?.toFixed(1)} ms；PS映射 ${p.timing.ps_mapping_ms?.toFixed(1)} ms\\n输入/STEP/发布 ${p.timing.input_upload_step_and_publication_ms?.toFixed(1)} ms；DDR复制 ${p.timing.ddr_copy_and_cache_ms?.toFixed(1)} ms\\n网页取数 ${row.fetch_ms.toFixed(1)} ms；输入图准备 ${row.image_ms.toFixed(1)} ms；骨架准备 ${row.skeleton_ms.toFixed(1)} ms；绘制 ${row.paint_ms.toFixed(1)} ms（准备阶段并行，不能相加）`;
    }
''' +s[b:]
s=s.replace("}catch(e){$('liveSummary').textContent='连接中断", "}catch(e){failed=true;$('liveSummary').textContent='连接中断")
s=s.replace("  setTimeout(poll,150);",'''  row.cycle_ms=performance.now()-cycleStart;
  if(row.session_id){metrics.add(row);const m=metrics.summary();$('displayTiming').textContent=`本页绘制 ${m.painted} 帧；平均更新间隔 ${m.mean_interval_ms===null?'—':m.mean_interval_ms.toFixed(1)+' ms'}；平均取数 ${m.fetch_ms.toFixed(1)} ms / 骨架准备 ${m.skeleton_ms.toFixed(1)} ms / 绘制 ${m.paint_ms.toFixed(1)} ms。仅网页侧计时，不是摄像头到屏幕延迟。`;}
  setTimeout(poll,displayDelay(performance.now()-cycleStart,{paused,hidden:document.hidden,finished,failed}));''')
p.write_text(s,encoding='utf-8')
p=P/'assets/index.html';s=p.read_text().replace('<div id="timing"></div>','<div id="timing"></div><p id="displayTiming">等待显示计时。</p><button id="exportDisplayTiming">下载显示计时</button>');p.write_text(s,encoding='utf-8')
