/* Original stage, frozen line-4 inputs and explicitly verified GPU replay. Never submits computation. */
(() => {
 'use strict';
 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id),base='/api/controlled-stimuli28';
 const controls=document.createElement('div');controls.className='cp-player';controls.id='cpStimuli28Controls';
 controls.innerHTML='<button id="cpStimuli28Open">加载28条件科学刺激</button><select id="cpStimuli28Condition" aria-label="科学刺激条件" hidden></select><button id="cpStimuli28Control" hidden>配对静止对照</button><button id="cpStimuli28Play" hidden>▶ 4倍慢放</button><input id="cpStimuli28Step" type="number" min="0" max="484" value="0" aria-label="刺激步号" hidden><input id="cpStimuli28Timeline" type="range" min="0" max="484" value="0" aria-label="科学刺激时间轴" hidden><button id="cpStimuli28Back" hidden>返回原离线演示</button><span id="cpStimuli28Status">仅冻结输入 · 神经元/光流待计算</span>';
 root.querySelector('.cp-player').after(controls);
 const identity=document.createElement('details');identity.hidden=true;
 identity.innerHTML='<summary>本条件运行身份与计时</summary><pre></pre>';controls.append(identity);
 const labels={RIGHT:'向右',LEFT:'向左',UP:'向上',DOWN:'向下'},dots={DOT_CCW:'逆时针圆周运动',DOT_CW:'顺时针圆周运动',DOT_STATIC:'静止黑圆点',DOT_BLANK_WHITE:'空白白场'},title=c=>`${c.family==='four_direction_bar'?'亮条':c.kind==='edge'?(c.polarity+'边缘'):'小目标'} · ${labels[c.condition_id.split('_').find(x=>labels[x])]||dots[c.condition_id]||c.condition_id} ${c.stationary?'· 静止/空白对照':''}`;
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 const check=(ok,message)=>{if(!ok)throw Error(message);};
 async function json(path){const r=await fetch(path),v=await r.json();check(r.ok,v.error||'刺激不可用');return v;}
 let meta=null,active=false,playing=false,epoch=0,step=0,rows=[],saved=[],timer=null,callbacks=null,oldAria='';
 const seriesCache=new Map(),palette=['#FFC857','#56D6E9','#61D99C','#B699FF','#FF82BC','#F4ED74','#5C9DFF','#E3EAF3'];
 function pause(){playing=false;clearTimeout(timer);$('cpStimuli28Play').textContent='▶ 4倍慢放';}
 function blank(message){const c=ui.stage.c;c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);ui.stage.text(message,70,150,32,'#ffd59e');Object.assign(ui.stage.canvas.dataset,{displayKind:'STIMULUS_ONLY_NOT_AVAILABLE',run:'',neuralState:'NOT_AVAILABLE',flow:'NOT_AVAILABLE',fullStateSha:'',flowStateSha:''});}
 function resetGuide(){ui.stage.clearGuide();ui.stage.guideButton.disabled=true;}
 function rect(x,y,w,h){const c=ui.stage.c;c.fillStyle='#101f2c';c.fillRect(x,y,w,h);c.strokeStyle='#29414d';c.strokeRect(x,y,w,h);}
 function retina(values){const c=ui.stage.c,scale=7.1;meta.coordinates_uv.forEach(([u,v],i)=>{
  const x=815+1.5*v*scale,y=330+Math.sqrt(3)*(u+v/2)*scale,g=Math.round(values[i]*255);c.fillStyle=`rgb(${g},${g},${g})`;c.beginPath();
  for(let j=0;j<6;j++){const a=j*Math.PI/3;j?c.lineTo(x+scale*Math.cos(a),y+scale*Math.sin(a)):c.moveTo(x+scale*Math.cos(a),y+scale*Math.sin(a));}c.closePath();c.fill();
 });}
 function responses(p,series){
  const c=ui.stage.c,n=p.neural_state,types=meta.GPU_results.types,d=meta.GPU_results.visual_domains;
  c.fillStyle='#101f2c';c.fillRect(35,580,1027,346);c.fillRect(1094,580,790,346);
  ui.stage.text('③ 八类T4/T5真实活动 · 721节点均值',54,616,27,'#edf7f8',true);
  ui.stage.text('④ 5,768节点空间活动 · 同一步完整状态',1110,616,25,'#edf7f8',true);
  const lo=d.mean_min,hi=d.mean_max,range=hi-lo||1;
  types.forEach((type,i)=>{
   const x=55+(i%4)*253,y=640+Math.floor(i/4)*139,w=229,h=88;
   const px=k=>x+k/484*w,py=v=>y+30+(hi-v)/range*h;
   c.fillStyle='#0b1721';c.fillRect(x,y+24,w,h+8);
   c.fillStyle='#16372f';c.fillRect(px(200),y+24,px(400)-px(200),h+8);
   c.strokeStyle='#3e5564';c.lineWidth=1;c.beginPath();c.moveTo(x,py(0));c.lineTo(x+w,py(0));c.stroke();
   c.strokeStyle=palette[i];c.lineWidth=1.6;c.beginPath();series.means.forEach((v,k)=>k?c.lineTo(px(k),py(v[i])):c.moveTo(px(k),py(v[i])));c.stroke();
   c.strokeStyle='#ffd28a';c.beginPath();c.moveTo(px(p.step_id),y+24);c.lineTo(px(p.step_id),y+h+32);c.stroke();
   ui.stage.text(`${type} ${n.means[i]>=0?'+':''}${n.means[i].toFixed(4)}`,x,y+18,19,palette[i],true);
   const mx=1125+(i%4)*190,my=655+Math.floor(i/4)*130,scale=1.58;
   meta.coordinates_uv.forEach(([u,v],j)=>{
    const value=n.spatial[i*721+j],z=Math.min(1,Math.asinh(Math.abs(value)/.02)/Math.asinh(Math.max(d.activity_abs_max,.02)/.02));
    const rgb=value>=0?[255,173,91]:[89,178,255];c.fillStyle=`rgb(${rgb.map(v=>Math.round(24+(v-24)*z)).join(',')})`;
    c.beginPath();c.arc(mx+68+1.5*v*scale,my+54+Math.sqrt(3)*(u+v/2)*scale,1.2,0,Math.PI*2);c.fill();
   });ui.stage.text(type,mx,my+8,18,palette[i],true);
  });
  ui.stage.text('共用固定纵轴 / 零基线；绿色为运动段；数值保留正负',55,918,17,'#a5c6ce');
  ui.stage.text('橙：正活动 / 蓝：负活动 · 全28条件固定asinh色标',1115,918,17,'#a5c6ce');
 }
 function officialFlow(p){
  const c=ui.stage.c,d=meta.GPU_results.visual_domains,scale=5.1,max=Math.max(d.flow_abs_max,1e-6);
  c.fillStyle='#101f2c';c.fillRect(1094,86,790,461);
  ui.stage.text('② 官方DecoderGAVP光流 · 同一完整状态',1115,124,26,'#edf7f8',true);
  meta.coordinates_uv.forEach(([u,v],j)=>{
   const x=1490+1.5*v*scale,y=318+Math.sqrt(3)*(u+v/2)*scale,fx=p.flow[0][j],fy=p.flow[1][j],magnitude=Math.hypot(fx,fy);
   const lengthShown=24*Math.asinh(magnitude/.005)/Math.asinh(Math.SQRT2*max/.005),dx=magnitude?fx/magnitude*lengthShown:0,dy=magnitude?-fy/magnitude*lengthShown:0;
   const length=Math.hypot(dx,dy);if(length<.06)return;const angle=Math.atan2(dy,dx),head=Math.min(5,length*.4);
   c.strokeStyle='#78e5d4';c.lineWidth=1.2;c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);
   for(const side of [-.5,.5]){c.moveTo(x+dx-head*Math.cos(angle+side),y+dy-head*Math.sin(angle+side));c.lineTo(x+dx,y+dy);}c.stroke();
  });
  ui.stage.text('721位置矢量场 · 全批次固定asinh箭长 · 原值未改',1130,526,21,'#a5c6ce');
 }
 function draw(p,image,series){const c=ui.stage.c,condition=rows.find(x=>x.condition_id===p.condition_id),computed=!!p.neural_state;resetGuide();c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);
  ui.stage.text('FlyVis · 受控科学刺激',34,48,32,'#edf7f8',true);ui.stage.text(computed?'真实Full GPU结果 · OFFLINE REPLAY':'仅播放真实冻结输入 · 尚未进行神经计算',965,48,25,'#ffc777',true);
  rect(32,82,1035,470);rect(1090,82,798,470);rect(32,576,1035,355);rect(1090,576,798,355);
  ui.stage.text('① 果蝇看到了什么？',54,124,30,'#edf7f8',true);ui.stage.text(title(condition),54,162,23,'#9be5d7');
  c.drawImage(image,72,185,340,340);retina(p.input_721);ui.stage.text('无损权威源图',77,540,19,'#a5c6ce');ui.stage.text('实际721维感光输入',665,540,19,'#a5c6ce');
  ui.stage.text('② 官方光流',1115,124,30,'#edf7f8',true);ui.stage.text('待计算 / NOT_RUN',1220,315,40,'#ffc777',true);ui.stage.text('本包没有光流或方向预测结果',1150,376,25,'#a5c6ce');
  ui.stage.text('③ T4 / T5 神经元',54,622,30,'#edf7f8',true);ui.stage.text('待计算 / NOT_RUN',290,757,40,'#ffc777',true);ui.stage.text('未显示旧曲线、零填充活动或预设方向',170,828,25,'#a5c6ce');
  ui.stage.text('④ 怎么理解神经元？',1115,622,30,'#edf7f8',true);ui.stage.text('这次只准备了刺激，还没有神经响应。',1115,690,27,'#d9e9f1');
  ui.stage.text('T4/T5怎样变化，要等原网络实际计算。',1115,740,27,'#d9e9f1');ui.stage.text('输入设定的方向不是模型识别出的方向。',1115,790,25,'#a5c6ce');
  ui.stage.text('Full / 干预 / 替换结果均待绑定真实run。',1115,840,25,'#a5c6ce');
  if(computed){officialFlow(p);responses(p,series);}
  const phase=step<200?'初始静止':step<400?'运动段':'运动停止';
  ui.stage.text(`步 ${step}/484 · ${phase} · 输入 ${p.input_time_s.toFixed(3)}s → ${computed?'实际活动':'更新后应为'} ${p.state_time_s.toFixed(3)}s`,34,977,25,'#9be5d7');
  ui.stage.text(`MP4帧 ${p.video_frame} · 观看时间 ${p.video_pts_s.toFixed(2)}s · 4倍慢放，非计算速度`,34,1025,24,'#a5c6ce');
  ui.stage.text(`输入身份 ${p.input_raw_sha256.slice(0,16)}… · FPGA NOT_CONNECTED`,1120,1025,20,'#a5c6ce');
  Object.assign(ui.stage.canvas.dataset,{displayKind:'STIMULUS_ONLY_OFFLINE_PREVIEW',stimulusCondition:p.condition_id,stimulusStep:String(step),
   stimulusInputSha:p.input_raw_sha256,stimulusStepSha:p.input_step_sha256,sourcePixelSha:p.source_pixel_sha256,neuralState:'NOT_RUN',flow:'NOT_RUN',run:'',frame:String(step)});
  if(computed){const n=p.neural_state;Object.assign(ui.stage.canvas.dataset,{displayKind:'STIMULI28_GPU_OFFLINE_REPLAY',run:n.run_id,neuralState:'ACTUAL_FULL_GPU',flow:'OFFICIAL_DECODER_SAME_STATE',fullStateSha:n.full_state_sha256,flowStateSha:n.full_state_sha256});
   ui.stage.text(`run ${n.run_id.slice(0,16)} · bias a0 · 5ms · 纯FPGA待板测`,34,1057,21,'#a5c6ce');
   identity.querySelector('pre').textContent=JSON.stringify({run_id:n.run_id,campaign_id:n.campaign_id,condition_id:p.condition_id,backend:n.backend,device:n.device,display_kind:n.display_kind,initial_raw_sha256:n.initial_raw_sha256,input_raw_sha256:p.input_raw_sha256,model:meta.GPU_results.model_checkpoint_sha256,numeric_profile:meta.GPU_results.numeric_profile,step_id:p.step_id,full_state_sha256:n.full_state_sha256,flow_sha256:n.flow_sha256,timing:series.timing,audit:meta.GPU_results.audit_scope,PL_execution:false,FPGA_status:'NOT_CONNECTED'},null,2);
  }else identity.querySelector('pre').textContent='本条件尚无神经计算结果。';
 }
 async function seek(k){const mine=++epoch,cid=$('cpStimuli28Condition').value;step=Math.max(0,Math.min(484,Math.round(k)));
  try{const p=await json(`${base}/conditions/${cid}/steps/${step}`);
   check(p.PACK_sha256===meta.PACK_sha256&&p.condition_id===cid&&p.step_id===step&&p.direction_prediction===null,'拒绝错条件/输入身份');
   let series=null;
   if(p.neural_state){const n=p.neural_state;
    check(meta.GPU_results&&n.condition_id===cid&&n.step_id===p.step_id&&n.state_token===p.step_id+1&&n.input_time_s===p.input_time_s&&n.activity_time_s===p.state_time_s&&n.run_id===p.run_id&&n.campaign_id===meta.GPU_results.campaign_id&&n.input_raw_sha256===p.input_raw_sha256&&n.initial_raw_sha256===meta.GPU_results.initial_raw_sha256&&n.decoder==='official_DecoderGAVP'&&n.display_kind==='OFFLINE_REPLAY'&&n.PL_execution===false,'拒绝错run/时间/初态或伪硬件结果');
    check(n.spatial.length===5768&&n.spatial.every(Number.isFinite)&&n.means.length===8&&n.means.every(Number.isFinite)&&await sha(new Float32Array(n.spatial).buffer)===n.spatial_sha256,'空间活动身份不符');
    check(p.flow.length===2&&p.flow.every(v=>v.length===721&&v.every(Number.isFinite))&&await sha(new Float32Array(p.flow.flat()).buffer)===n.flow_sha256,'官方光流身份不符');
    if(!seriesCache.has(cid)){const s=await json(`${base}/conditions/${cid}/results`);check(s.means.length===485&&s.means.every(v=>v.length===8&&v.every(Number.isFinite))&&await sha(new Float64Array(s.means.flat()).buffer)===s.means_sha256,'活动曲线身份不符');seriesCache.set(cid,s);}
    series=seriesCache.get(cid);check(series.run_id===n.run_id&&series.condition_id===cid&&series.input_raw_sha256===p.input_raw_sha256&&series.means[p.step_id].every((v,i)=>v===n.means[i]),'曲线与当前活动不同run/步');
   }else check(p.run_id===null&&p.flow===null&&p.all_backends_status==='NOT_RUN'&&!meta.GPU_results,'拒绝缺失或借用结果');
   check(p.input_721.length===721&&p.input_721.every(Number.isFinite)&&await sha(new Float32Array(p.input_721).buffer)===p.input_step_sha256,'721输入身份不符');
   check(p.video_frame===p.step_id&&p.video_pts_s===p.step_id/50&&p.input_time_s===p.step_id*.005&&p.state_time_s===(p.step_id+1)*.005,'步号或时间映射不符');
   const response=await fetch(p.source_png_url);check(response.ok,'源画面不可用');const blob=await response.blob();check(await sha(await blob.arrayBuffer())===p.png_sha256,'源图SHA不符');
   const image=await createImageBitmap(blob);try{if(!active||mine!==epoch)return;draw(p,image,series);}finally{image.close();}
   $('cpStimuli28Step').value=String(step);$('cpStimuli28Timeline').value=String(step);$('cpStimuli28Status').textContent=`${p.neural_state?'真实Full GPU / OFFLINE REPLAY':'刺激就绪'} · ${cid} · 步${step}${p.neural_state?' · 纯FPGA未运行':' · 神经元/光流待计算'}`;
   $('cpStimuli28Control').disabled=!rows.find(x=>x.condition_id===cid).matched_control;
  }catch(error){if(active&&mine===epoch){pause();blank('NOT_AVAILABLE · '+error.message);$('cpStimuli28Status').textContent=error.message;}}
 }
 $('cpStimuli28Open').onclick=async()=>{try{check(root.dataset.live!=='true'||active,'请先停止当前计算会话，再查看刺激');
  pause();
  if(!meta){$('cpStimuli28Status').textContent='正在只读核对28条件与已登记结果…';meta=await json(base);check(!meta.result_error,'GPU结果校验失败：'+meta.result_error);check(['VERIFIED_STIMULUS_ONLY','VERIFIED_ACTUAL_GPU_OFFLINE_REPLAY'].includes(meta.status)&&meta.neural_state===null&&meta.flow===null,'刺激/结果身份不符');rows=meta.conditions;
   for(const c of rows)$('cpStimuli28Condition').append(new Option(title(c),c.condition_id));}
  if(!active){ui.enterLive();active=true;saved=[];for(const el of root.children)if(el!==controls&&el!==ui.stage.host){saved.push([el,el.style.display]);el.style.display='none';}
   oldAria=ui.stage.canvas.getAttribute('aria-label');ui.stage.canvas.setAttribute('aria-label',meta.GPU_results?'本次真实GPU结果离线回放：源画面、721输入、T4T5活动、空间图及同态官方光流':'只读科学刺激：无损源图和721输入；神经元及官方光流待计算');
   callbacks={onSeek:ui.stage.onSeek,onPlay:ui.stage.onPlay,onCamera:ui.stage.onCamera};ui.stage.onSeek=k=>{pause();seek(k);};ui.stage.onPlay=()=>$('cpStimuli28Play').click();ui.stage.onCamera=()=>{};
   for(const el of controls.querySelectorAll('[hidden]'))el.hidden=false;}
  await seek(0);
 }catch(error){$('cpStimuli28Status').textContent='NOT_AVAILABLE · '+error.message;}};
 $('cpStimuli28Condition').onchange=()=>{pause();seek(0);};
 $('cpStimuli28Control').onclick=()=>{const control=rows.find(c=>c.condition_id===$('cpStimuli28Condition').value).matched_control;if(control){pause();$('cpStimuli28Condition').value=control;seek(0);}};
 $('cpStimuli28Step').onchange=e=>{pause();seek(Number(e.target.value));};$('cpStimuli28Timeline').oninput=e=>{pause();seek(Number(e.target.value));};
 $('cpStimuli28Step').oninput=$('cpStimuli28Step').onchange;
 $('cpStimuli28Play').onclick=()=>{if(playing){pause();return;}playing=true;$('cpStimuli28Play').textContent='Ⅱ 暂停';const origin=performance.now(),first=step===484?0:step;
  const tick=async()=>{if(!playing||!active)return;const k=Math.min(484,first+Math.floor((performance.now()-origin)/20));await seek(k);if(k===484){pause();return;}if(playing)timer=setTimeout(tick,Math.max(0,20-(performance.now()-origin)%20));};tick();};
 $('cpStimuli28Back').onclick=async()=>{pause();active=false;++epoch;blank('正在返回原离线演示；等待原结果核验');for(const key of ['stimulusCondition','stimulusStep','stimulusStepSha','stimulusInputSha','sourcePixelSha','neuralState','flow','fullStateSha','flowStateSha'])delete ui.stage.canvas.dataset[key];ui.stage.canvas.setAttribute('aria-label',oldAria);Object.assign(ui.stage,callbacks);callbacks=null;for(const [el,display] of saved)el.style.display=display;saved=[];for(const el of controls.children)if(el.id!=='cpStimuli28Open'&&el.id!=='cpStimuli28Status')el.hidden=true;$('cpStimuli28Status').textContent='28条件结果已关闭；原离线演示独立加载';await ui.leaveLive();};
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
})();
