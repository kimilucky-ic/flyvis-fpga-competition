"use strict";
const $=id=>document.getElementById(id),canvas=$("stimulus"),ctx=canvas.getContext("2d",{alpha:false}),stage=$("stage");
const token=new URLSearchParams(location.search).get("token")||"";
let settings=null,session=null,armed=false,running=false,startMs=0,frameNumber=0,events=[],touch={x:320,y:320},lastTouch=0;
function configuration(){return {family:$("family").value,polarity:$("polarity").value,direction_deg:Number($("direction").value),speed_px_s:Number($("speed").value),active_s:Number($("duration").value),pre_s:1,post_s:1,dot_radius_px:Number($("radius").value),flicker_hz:Number($("frequency").value),gradient_period_px:Number($("period").value),dot_control:$("dotControl").value};}
async function request(path,data){const result=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","X-Stimulus-Token":token},body:JSON.stringify(data)});const body=await result.json();if(!result.ok)throw Error(body.error||"请求失败");return body;}
function push(kind,data={}){events.push({kind,client_performance_ms:performance.now(),...data});}
let flushPromise=null,finishing=false;
async function flush(){if(flushPromise)return flushPromise;if(!session||events.length===0)return true;const batch=events.splice(0,120);flushPromise=(async()=>{try{await request("/api/events",{session_id:session,events:batch});return true;}catch(error){events.unshift(...batch);$("status").textContent="日志传输失败："+error.message;if(events.length>1800){running=false;$("status").textContent="日志积压，已停止；本次需重新验收。";}return false;}finally{flushPromise=null;}})();return flushPromise;}
setInterval(flush,500);
function render(spec,elapsed){
 const active=Math.max(0,Math.min(spec.active_s,elapsed-spec.pre_s)),delta=spec.speed_px_s*(active-spec.active_s/2),angle=spec.direction_deg*Math.PI/180,dx=Math.cos(angle),dy=Math.sin(angle);
 ctx.fillStyle="white";ctx.fillRect(0,0,640,640);
 if(spec.family==="edge"){
  const image=ctx.createImageData(640,640);for(let y=0;y<640;y++)for(let x=0;x<640;x++){const crossed=(x-320)*dx+(y-320)*dy<delta;const value=(spec.polarity==="OFF"?crossed:!crossed)?0:255;const i=4*(y*640+x);image.data[i]=image.data[i+1]=image.data[i+2]=value;image.data[i+3]=255;}ctx.putImageData(image,0,0);
 }else if(spec.family==="dot"){
  const x=spec.dot_control==="touch"?touch.x:320+delta*dx,y=spec.dot_control==="touch"?touch.y:320+delta*dy;ctx.fillStyle="black";ctx.beginPath();ctx.arc(x,y,spec.dot_radius_px,0,2*Math.PI);ctx.fill();
 }else if(spec.family==="flicker"){
  ctx.fillStyle=(Math.floor(active*spec.flicker_hz*2)%2===0)?"black":"white";ctx.fillRect(0,0,640,640);
 }else if(spec.family==="fade"){
  const fraction=active/spec.active_s;const value=Math.round(255*(fraction<=.5?2*fraction:2-2*fraction));ctx.fillStyle=`rgb(${value},${value},${value})`;ctx.fillRect(0,0,640,640);
 }else if(spec.family==="gradient"){
  const image=ctx.createImageData(640,640);for(let y=0;y<640;y++)for(let x=0;x<640;x++){const value=Math.round(127.5*(1+Math.sin(2*Math.PI*((x-320)*dx+(y-320)*dy-delta)/spec.gradient_period_px)));const i=4*(y*640+x);image.data[i]=image.data[i+1]=image.data[i+2]=value;image.data[i+3]=255;}ctx.putImageData(image,0,0);
 }else{
  for(let i=0;i<8;i++){const value=Math.round(255*i/7);ctx.fillStyle=`rgb(${value},${value},${value})`;ctx.fillRect(i*80,0,80,640);}ctx.strokeStyle="black";ctx.lineWidth=4;ctx.strokeRect(2,2,636,636);ctx.fillStyle="white";ctx.fillRect(12,12,16,16);ctx.fillStyle="black";ctx.fillRect(600,12,16,16);ctx.fillRect(576,12,16,16);ctx.fillRect(306,310,28,4);ctx.fillRect(318,298,4,28);
 }
 return {active_s:active,logical_displacement_px:delta};
}
async function finish(kind){if(finishing)return;finishing=true;running=false;stage.classList.remove("playing");push(kind,{frames:frameNumber,elapsed_s:(performance.now()-startMs)/1000});let logged=true;while(events.length||flushPromise){if(!(await flush())){logged=false;break;}}$("start").disabled=true;$("standby").disabled=true;$("stop").disabled=true;armed=false;$("arm").disabled=!logged;document.querySelectorAll(".controls input,.controls select").forEach(node=>node.disabled=false);$("status").textContent=!logged?"播放已停止，但日志未交付；保持本页并检查连接。本次暂不能验收。":kind==="complete"?"播放完成并保持最终画面；日志已保存。电脑结束录制后再返回参数。":"本次播放已停止，日志已保存。";finishing=false;}
function tick(now){if(!running)return;const elapsed=(now-startMs)/1000,result=render(settings,elapsed);push("frame",{sequence:frameNumber++,elapsed_s:elapsed,...result});if(elapsed>=settings.pre_s+settings.active_s+settings.post_s){finish("complete");return;}requestAnimationFrame(tick);}
$("arm").onclick=async()=>{try{settings=configuration();const result=await request("/api/arm",{settings,client:{user_agent:navigator.userAgent,viewport:[innerWidth,innerHeight],device_pixel_ratio:devicePixelRatio}});session=result.session_id;events=[];armed=true;$("session").textContent="刺激会话："+session+"\n参数SHA："+result.settings_sha256;$("status").textContent=result.validation_only?"浏览器软件验证会话，不能用作正式相机输入。":"已准备。先全屏待机；电脑开始录制后轻触画面。";$("start").disabled=false;$("standby").disabled=false;render(settings,0);}catch(error){$("status").textContent=error.message;}};
async function fullscreenStage(){stage.classList.add("standby");try{if(stage.requestFullscreen&&!document.fullscreenElement)await stage.requestFullscreen();}catch(error){}const rect=canvas.getBoundingClientRect();$("exitStage").style.visibility=(rect.y>=52||rect.x>=140)?"visible":"hidden";}
async function startTrial(){if(!armed||running||finishing)return;await fullscreenStage();running=true;stage.classList.add("playing");startMs=performance.now();frameNumber=0;$("start").disabled=true;$("standby").disabled=true;$("arm").disabled=true;$("stop").disabled=false;document.querySelectorAll(".controls input,.controls select").forEach(node=>node.disabled=true);const rect=canvas.getBoundingClientRect();push("start",{fullscreen:!!document.fullscreenElement,viewport:[innerWidth,innerHeight],canvas_rect:{x:rect.x,y:rect.y,width:rect.width,height:rect.height}});requestAnimationFrame(tick);}
$("start").onclick=startTrial;$("standby").onclick=async()=>{if(armed&&!running){await fullscreenStage();render(settings,0);push("standby",{viewport:[innerWidth,innerHeight]});}};
canvas.addEventListener("pointerdown",()=>{if(armed&&!running&&stage.classList.contains("standby"))startTrial();});
$("exitStage").onclick=async()=>{if(running)await finish("stop");stage.classList.remove("standby");if(document.fullscreenElement)await document.exitFullscreen();};
$("stop").onclick=()=>finish("stop");$("calibrate").onclick=async()=>{if(!running){armed=false;$("start").disabled=true;$("standby").disabled=true;await fullscreenStage();render({...configuration(),family:"calibration"},0);$("status").textContent="校准：从左至右8级灰阶；左上1个标记，右上2个标记。全屏位置须与正式播放相同；退出全屏后选择参数。";}};
document.querySelectorAll(".controls input,.controls select").forEach(node=>node.addEventListener("change",()=>{if(!running){armed=false;$("start").disabled=true;$("standby").disabled=true;$("status").textContent="参数已改变，请重新准备会话。";render(configuration(),0);}}));
canvas.addEventListener("pointermove",event=>{if(!running||settings.family!=="dot"||settings.dot_control!=="touch")return;const rect=canvas.getBoundingClientRect();touch={x:Math.max(0,Math.min(640,(event.clientX-rect.left)*640/rect.width)),y:Math.max(0,Math.min(640,(event.clientY-rect.top)*640/rect.height))};if(performance.now()-lastTouch>50){push("touch",touch);lastTouch=performance.now();}});
window.addEventListener("resize",()=>{if(running)push("resize",{viewport:[innerWidth,innerHeight]});});document.addEventListener("visibilitychange",()=>{if(running){push("visibility",{state:document.visibilityState});if(document.hidden)finish("stop");}});document.addEventListener("fullscreenchange",()=>{if(running)push("fullscreen",{enabled:!!document.fullscreenElement});});
render(configuration(),0);
