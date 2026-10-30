/* Original stage, frozen line-4 inputs only. Never submits computation. */
(() => {
 'use strict';
 const ui=window.FlyVisCompetitionUI,root=document.getElementById('competitionWorkspace');if(!ui||!root)return;
 const $=id=>document.getElementById(id),base='/api/controlled-stimuli28';
 const controls=document.createElement('div');controls.className='cp-player';controls.id='cpStimuli28Controls';
 controls.innerHTML='<button id="cpStimuli28Open">加载28条件科学刺激</button><select id="cpStimuli28Condition" aria-label="科学刺激条件" hidden></select><button id="cpStimuli28Control" hidden>配对静止对照</button><button id="cpStimuli28Play" hidden>▶ 4倍慢放</button><input id="cpStimuli28Step" type="number" min="0" max="484" value="0" aria-label="刺激步号" hidden><input id="cpStimuli28Timeline" type="range" min="0" max="484" value="0" aria-label="科学刺激时间轴" hidden><button id="cpStimuli28Back" hidden>返回原离线演示</button><span id="cpStimuli28Status">仅冻结输入 · 神经元/光流待计算</span>';
 root.querySelector('.cp-player').after(controls);
 const labels={RIGHT:'向右',LEFT:'向左',UP:'向上',DOWN:'向下'},dots={DOT_CCW:'逆时针圆周运动',DOT_CW:'顺时针圆周运动',DOT_STATIC:'静止黑圆点',DOT_BLANK_WHITE:'空白白场'},title=c=>`${c.family==='four_direction_bar'?'亮条':c.kind==='edge'?(c.polarity+'边缘'):'小目标'} · ${labels[c.condition_id.split('_').find(x=>labels[x])]||dots[c.condition_id]||c.condition_id} ${c.stationary?'· 静止/空白对照':''}`;
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 const check=(ok,message)=>{if(!ok)throw Error(message);};
 async function json(path){const r=await fetch(path),v=await r.json();check(r.ok,v.error||'刺激不可用');return v;}
 let meta=null,active=false,playing=false,epoch=0,step=0,rows=[],saved=[],timer=null,callbacks=null,oldAria='';
 function pause(){playing=false;clearTimeout(timer);$('cpStimuli28Play').textContent='▶ 4倍慢放';}
 function blank(message){const c=ui.stage.c;c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);ui.stage.text(message,70,150,32,'#ffd59e');ui.stage.canvas.dataset.displayKind='STIMULUS_ONLY_NOT_AVAILABLE';}
 function resetGuide(){ui.stage.clearGuide();ui.stage.guideButton.disabled=true;}
 function rect(x,y,w,h){const c=ui.stage.c;c.fillStyle='#101f2c';c.fillRect(x,y,w,h);c.strokeStyle='#29414d';c.strokeRect(x,y,w,h);}
 function retina(values){const c=ui.stage.c,scale=7.1;meta.coordinates_uv.forEach(([u,v],i)=>{
  const x=815+1.5*v*scale,y=330+Math.sqrt(3)*(u+v/2)*scale,g=Math.round(values[i]*255);c.fillStyle=`rgb(${g},${g},${g})`;c.beginPath();
  for(let j=0;j<6;j++){const a=j*Math.PI/3;j?c.lineTo(x+scale*Math.cos(a),y+scale*Math.sin(a)):c.moveTo(x+scale*Math.cos(a),y+scale*Math.sin(a));}c.closePath();c.fill();
 });}
 function draw(p,image){const c=ui.stage.c,condition=rows.find(x=>x.condition_id===p.condition_id);resetGuide();c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);
  ui.stage.text('FlyVis · 受控科学刺激',34,48,32,'#edf7f8',true);ui.stage.text('仅播放真实冻结输入 · 尚未进行神经计算',965,48,25,'#ffc777',true);
  rect(32,82,1035,470);rect(1090,82,798,470);rect(32,576,1035,355);rect(1090,576,798,355);
  ui.stage.text('① 果蝇看到了什么？',54,124,30,'#edf7f8',true);ui.stage.text(title(condition),54,162,23,'#9be5d7');
  c.drawImage(image,72,185,340,340);retina(p.input_721);ui.stage.text('无损权威源图',77,540,19,'#a5c6ce');ui.stage.text('实际721维感光输入',665,540,19,'#a5c6ce');
  ui.stage.text('② 官方光流',1115,124,30,'#edf7f8',true);ui.stage.text('待计算 / NOT_RUN',1220,315,40,'#ffc777',true);ui.stage.text('本包没有光流或方向预测结果',1150,376,25,'#a5c6ce');
  ui.stage.text('③ T4 / T5 神经元',54,622,30,'#edf7f8',true);ui.stage.text('待计算 / NOT_RUN',290,757,40,'#ffc777',true);ui.stage.text('未显示旧曲线、零填充活动或预设方向',170,828,25,'#a5c6ce');
  ui.stage.text('④ 怎么理解神经元？',1115,622,30,'#edf7f8',true);ui.stage.text('这次只准备了刺激，还没有神经响应。',1115,690,27,'#d9e9f1');
  ui.stage.text('T4/T5怎样变化，要等原网络实际计算。',1115,740,27,'#d9e9f1');ui.stage.text('输入设定的方向不是模型识别出的方向。',1115,790,25,'#a5c6ce');
  ui.stage.text('Full / 干预 / 替换结果均待绑定真实run。',1115,840,25,'#a5c6ce');
  const phase=step<200?'初始静止':step<400?'运动段':'运动停止';
  ui.stage.text(`步 ${step}/484 · ${phase} · 输入 ${p.input_time_s.toFixed(3)}s → 更新后应为 ${p.state_time_s.toFixed(3)}s`,34,977,25,'#9be5d7');
  ui.stage.text(`MP4帧 ${p.video_frame} · 观看时间 ${p.video_pts_s.toFixed(2)}s · 4倍慢放，非计算速度`,34,1025,24,'#a5c6ce');
  ui.stage.text(`输入身份 ${p.input_raw_sha256.slice(0,16)}… · FPGA NOT_CONNECTED`,1120,1025,20,'#a5c6ce');
  Object.assign(ui.stage.canvas.dataset,{displayKind:'STIMULUS_ONLY_OFFLINE_PREVIEW',stimulusCondition:p.condition_id,stimulusStep:String(step),
   stimulusInputSha:p.input_raw_sha256,stimulusStepSha:p.input_step_sha256,sourcePixelSha:p.source_pixel_sha256,neuralState:'NOT_RUN',flow:'NOT_RUN',run:'',frame:String(step)});
 }
 async function seek(k){const mine=++epoch,cid=$('cpStimuli28Condition').value;step=Math.max(0,Math.min(484,Math.round(k)));
  try{const p=await json(`${base}/conditions/${cid}/steps/${step}`);
   check(p.PACK_sha256===meta.PACK_sha256&&p.condition_id===cid&&p.step_id===step&&p.run_id===null&&p.neural_state===null&&p.flow===null&&p.direction_prediction===null&&p.all_backends_status==='NOT_RUN','拒绝错条件/伪神经结果');
   check(p.input_721.length===721&&p.input_721.every(Number.isFinite)&&await sha(new Float32Array(p.input_721).buffer)===p.input_step_sha256,'721输入身份不符');
   check(p.video_frame===p.step_id&&p.video_pts_s===p.step_id/50&&p.input_time_s===p.step_id*.005&&p.state_time_s===(p.step_id+1)*.005,'步号或时间映射不符');
   const response=await fetch(p.source_png_url);check(response.ok,'源画面不可用');const blob=await response.blob();check(await sha(await blob.arrayBuffer())===p.png_sha256,'源图SHA不符');
   const image=await createImageBitmap(blob);try{if(!active||mine!==epoch)return;draw(p,image);}finally{image.close();}
   $('cpStimuli28Step').value=String(step);$('cpStimuli28Timeline').value=String(step);$('cpStimuli28Status').textContent=`刺激就绪 · ${cid} · 步${step} · 神经元/光流待计算`;
   $('cpStimuli28Control').disabled=!rows.find(x=>x.condition_id===cid).matched_control;
  }catch(error){if(active&&mine===epoch){pause();blank('NOT_AVAILABLE · '+error.message);$('cpStimuli28Status').textContent=error.message;}}
 }
 $('cpStimuli28Open').onclick=async()=>{try{check(root.dataset.live!=='true'||active,'请先停止当前计算会话，再查看刺激');
  pause();
  if(!meta){$('cpStimuli28Status').textContent='正在只读核对28条件冻结包…';meta=await json(base);check(meta.status==='VERIFIED_STIMULUS_ONLY'&&meta.neural_state===null&&meta.flow===null&&meta.all_backends_status==='NOT_RUN','刺激身份不符');rows=meta.conditions;
   for(const c of rows)$('cpStimuli28Condition').append(new Option(title(c),c.condition_id));}
  if(!active){ui.enterLive();active=true;saved=[];for(const el of root.children)if(el!==controls&&el!==ui.stage.host){saved.push([el,el.style.display]);el.style.display='none';}
   oldAria=ui.stage.canvas.getAttribute('aria-label');ui.stage.canvas.setAttribute('aria-label','只读科学刺激：无损源图和721输入；神经元、方向预测及官方光流待计算');
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
 $('cpStimuli28Back').onclick=async()=>{pause();active=false;++epoch;ui.stage.canvas.setAttribute('aria-label',oldAria);Object.assign(ui.stage,callbacks);callbacks=null;for(const [el,display] of saved)el.style.display=display;saved=[];for(const el of controls.children)if(el.id!=='cpStimuli28Open'&&el.id!=='cpStimuli28Status')el.hidden=true;await ui.leaveLive();};
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
})();
