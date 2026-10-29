/* One scientific run, one display clock. A renderer receipt gates the entire frame. */
(() => {
 'use strict';
 const $=id=>document.getElementById(id), root=$('competitionWorkspace');
 const stage=new FlyVisCompetitionStage();
 const explanation=new FlyVisMotionExplanation();
 const directionText=document.createElement('p');directionText.id='cpDirectionComparison';directionText.className='cp-direction-comparison';directionText.hidden=true;directionText.setAttribute('role','status');directionText.textContent='正在读取本步网络的运动判断…';stage.host.before(directionText);
 root.querySelector('.cp-role-key').hidden=true; // Consolidated in the stage and its synchronized guide.
 const interpretationDetails=document.createElement('details');interpretationDetails.className='cp-more';const interpretationSummary=document.createElement('summary');interpretationSummary.textContent='功能依据、参考方向与指标定义';interpretationDetails.append(interpretationSummary);const interpretationContent=document.createElement('div');interpretationDetails.append(interpretationContent);$('cpIdentity').parentElement.after(interpretationDetails);
 stage.onSources=()=>{document.body.classList.remove('competition-cinema');interpretationDetails.open=true;interpretationDetails.scrollIntoView({block:'center',behavior:'smooth'});};
 const profileLabel=document.createElement('label');profileLabel.className='cp-profile-label';profileLabel.textContent='演示模式 ';const profileSelect=document.createElement('select');profileSelect.id='cpProfile';profileSelect.setAttribute('aria-label','演示模式');profileSelect.append(new Option('轻量演示 · 录屏推荐','light'),new Option('标准查看 · 自动让出GPU','standard'));profileLabel.append(profileSelect);document.querySelector('.cp-player').insertBefore(profileLabel,document.querySelector('.cp-player label'));
 const policyNotice=document.createElement('p');policyNotice.id='cpPolicyNotice';policyNotice.className='cp-policy-notice';policyNotice.textContent='八类骨架同步响应 · 固定镜头优先读取已核验画面 · 简化真实脑区背景 · 仅回放已保存结果';$('cpPanels').before(policyNotice);
 profileLabel.hidden=true; // C is the sole accepted presentation; avoid a transient obsolete selector.
 const curveDetails=document.createElement('details'),curveSummary=document.createElement('summary');curveSummary.textContent='查看所选类型的真实活动曲线';curveDetails.append(curveSummary);$('cpTrace').before(curveDetails);curveDetails.append($('cpTrace'));
 let meta,input,flow,spatial,viewer,frame=0,selected='T4a',filter='all',playing=false,busy=false,epoch=0,desired=null,baseClock=0,baseFrame=0,camera=null,pick=null;
 let receipt=null,renderCount=0,startDisplay=0,initialized=false,profile='light',maxFps=12,stepStride=1,playTimer=null,seekTimer=null,packInfo=null,fixedView=true,exporting=false;
 const exportButton=document.createElement('button');exportButton.id='cpExport';exportButton.textContent='生成40秒演示视频';exportButton.disabled=true;document.querySelector('.cp-player').append(exportButton);
 const exportStatus=document.createElement('p');exportStatus.id='cpExportStatus';exportStatus.className='cp-export-status';stage.host.before(exportStatus);
 const finite=a=>!a.some(x=>!Number.isFinite(x));
 const signed=x=>(x>=0?'+':'')+x.toFixed(3);
 async function json(url,options){try{const r=await fetch(url,options),j=await r.json();if(!r.ok||j.status==='NOT_AVAILABLE')throw Error(j.error||`HTTP ${r.status}`);return j;}catch(error){throw Error(`${url}: ${error.message}`);}}
 async function exportImage(url){for(let attempt=0;attempt<3;attempt++){try{const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw Error(`HTTP ${response.status}`);return await response.blob();}catch(error){if(!(error instanceof TypeError)||attempt===2)throw Error(`${url}: ${error.message}`);root.dataset.imageReadRetries=String(Number(root.dataset.imageReadRetries||0)+1);await new Promise(resolve=>setTimeout(resolve,150*(attempt+1)));}}}
 // Only the read-only frozen renderer and identity/byte-bound capture support retries.
 async function exportJSON(url,options){for(let attempt=0;attempt<3;attempt++){try{const response=await fetch(url,options),j=await response.json();if(!response.ok||j.status==='NOT_AVAILABLE')throw Error(j.error||`HTTP ${response.status}`);return j;}catch(error){if(!(error instanceof TypeError)||attempt===2)throw Error(`${url}: ${error.message}`);root.dataset.exportTransportRetries=String(Number(root.dataset.exportTransportRetries||0)+1);await new Promise(resolve=>setTimeout(resolve,150*(attempt+1)));}}}
 async function binary(name,length){const spec=meta.arrays[name],r=await fetch(spec.url);if(!r.ok||r.headers.get('X-Run-ID')!==meta.run_id)throw Error('数组运行身份不匹配');const bytes=await r.arrayBuffer();if(bytes.byteLength!==spec.bytes)throw Error('数组长度不匹配');const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');if(digest!==spec.sha256)throw Error('数组 SHA256 不匹配');const a=new Float32Array(bytes);if(a.length!==length||!finite(a))throw Error('数组形状或数值不匹配');return a;}
 function pause(){playing=false;clearTimeout(playTimer);playTimer=null;$('cpPlay').textContent='▶ 播放';$('cpStatus').textContent=$('cpStatus').textContent.replace(/^正在播放/,'已暂停');}
 function stamp(el,k){el.dataset.run=meta.run_id;el.dataset.frame=String(k);el.dataset.activityTime=String(meta.activity_time_s[k]);}
 function canvas(id){const el=$(id),c=el.getContext('2d');c.clearRect(0,0,el.width,el.height);return {c,w:el.width,h:el.height};}
 function polygon(c,x,y,r){c.beginPath();for(let j=0;j<6;j++){const a=j*Math.PI/3;const xx=x+Math.cos(a)*r,yy=y+Math.sin(a)*r;j?c.lineTo(xx,yy):c.moveTo(xx,yy);}c.closePath();}
 function retina(id,k,grid){const {c,w,h}=canvas(id),s=Math.min((w-30)/46,(h-35)/53);c.fillStyle='#080f17';c.fillRect(0,0,w,h);meta.coordinates_uv.forEach(([u,v],i)=>{const x=w/2+1.5*v*s,y=h/2+Math.sqrt(3)*(u+v/2)*s;polygon(c,x,y,s*1.02);const g=Math.round(Math.max(0,Math.min(1,input[k*721+i]))*255);c.fillStyle=`rgb(${g},${g},${g})`;c.fill();if(grid){c.strokeStyle='#537582';c.lineWidth=.5;c.stroke();}});stamp($(id),k);}
 function arrow(c,x,y,dx,dy,color,width=1){const n=Math.hypot(dx,dy);if(n<.08)return;const a=Math.atan2(dy,dx),head=Math.min(7,n*.38);c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);c.moveTo(x+dx-head*Math.cos(a-.5),y+dy-head*Math.sin(a-.5));c.lineTo(x+dx,y+dy);c.lineTo(x+dx-head*Math.cos(a+.5),y+dy-head*Math.sin(a+.5));c.stroke();}
 function optical(k){const {c,w,h}=canvas('cpFlow'),plotH=270,s=Math.min((w-40)/46,(plotH-70)/53);c.fillStyle='#091523';c.fillRect(0,0,w,h);meta.coordinates_uv.forEach(([u,v],i)=>{const x=w/2+1.5*v*s,y=plotH/2+Math.sqrt(3)*(u+v/2)*s;c.fillStyle='#293e4d';c.fillRect(x,y,1,1);arrow(c,x,y,flow[k*1442+i]*8,-flow[k*1442+721+i]*8,'#74e4d5',1);});
  const i=meta.coordinates_uv.findIndex(([u,v])=>u===0&&v===0),x=flow[k*1442+i],y=flow[k*1442+721+i],mag=Math.hypot(x,y);c.fillStyle='#0e2230';c.fillRect(12,h-63,w-24,51);arrow(c,40,h-37,x*20,-y*20,'#ffc889',2.4);c.fillStyle='#b3d6df';c.font='12px sans-serif';c.fillText(`中心向量 x ${signed(x)} · y ${signed(y)}`,90,h-32);
  const text=mag<.01?'此刻中心位置的运动读出接近零。':`此刻中心位置指向${x>=0?'右':'左'}${y>=0?'上':'下'}方；向量长度 ${mag.toFixed(3)}（原始单位）。`;
  $('cpFlowText').textContent=text;stamp($('cpFlow'),k);
 }
 function trace(k){const {c,w,h}=canvas('cpTrace'),i=meta.types.indexOf(selected),vals=meta.means.map(a=>a[i]);let lo=Math.min(0,...vals),hi=Math.max(0,...vals),pad=(hi-lo||1)*.1;lo-=pad;hi+=pad;const x=j=>44+j/484*(w-58),y=v=>12+(hi-v)/(hi-lo)*(h-38);c.fillStyle='#0b1721';c.fillRect(0,0,w,h);c.fillStyle='#18362f';c.fillRect(x(200),8,x(285)-x(200),h-30);c.strokeStyle='#2e4655';c.beginPath();c.moveTo(44,y(0));c.lineTo(w-14,y(0));c.stroke();c.strokeStyle='#84dbcc';c.lineWidth=1.8;c.beginPath();vals.forEach((v,j)=>j?c.lineTo(x(j),y(v)):c.moveTo(x(j),y(v)));c.stroke();c.strokeStyle='#ffd59e';c.beginPath();c.moveTo(x(k),8);c.lineTo(x(k),h-23);c.stroke();c.fillStyle='#a6c2d0';c.font='12px sans-serif';c.fillText(hi.toFixed(2),1,14);c.fillText(lo.toFixed(2),1,h-25);c.fillText('-0.995 s',44,h-5);c.fillText('更新后活动时间',w/2-40,h-5);c.fillText('1.425 s',w-65,h-5);stamp($('cpTrace'),k);}
 function neurons(k){const i=meta.types.indexOf(selected),v=meta.means[k][i],delta=k? v-meta.means[k-1][i]:0;for(const b of $('cpTypes').children){const ix=meta.types.indexOf(b.dataset.type);b.querySelector('small').textContent=signed(meta.means[k][ix]);b.setAttribute('aria-pressed',String(b.dataset.type===selected));}
  const scope=filter==='all'?'八类骨架同步响应':filter==='T4'||filter==='T5'?`${filter} 四类同步响应`:`单独观察 ${filter}`;
  $('cpNeuronText').textContent=`${scope}。当前读数 ${selected}：721 个同类型模型节点平均活动 ${signed(v)}，${Math.abs(delta)<.00001?'与前一步基本相同':delta>0?'比前一步升高':'比前一步降低'}。`;
  if(curveDetails.open)trace(k);else stamp($('cpTrace'),k);
 }
 function spatialFrame(k){if(!spatial||!viewer||!$('cpSpatialDetails').open)return;viewer.accept({map_sha256:meta.spatial_metadata.map_sha256,run_id:meta.run_id,step_id:k,state_token:k+1,activity_time_s:meta.activity_time_s[k],mode:'SOFTWARE_PILOT / OFFLINE_REPLAY',values:Array.from(spatial.subarray(k*5768,(k+1)*5768)),layers:{disabled_global_ids:[],release_blocked_global_ids:[],software_replaced_global_ids:[],PL_proven_global_ids:[],FPGA_status:'NOT_CONNECTED'}});}
 function draw(k,image,r){const explanationFrame=explanation.frame(k,r,meta);frame=k;receipt=r;selected=r.selected_type;if(image.src)$('cpAnatomy').src=image.src;stamp($('cpAnatomy'),k);retina('cpStimulus',k,false);if($('cpRetinaDetails').open)retina('cpRetina',k,true);optical(k);neurons(k);spatialFrame(k);$('cpTimeline').value=k;$('cpClock').textContent=`第 ${k} / 484 步 · ${meta.activity_time_s[k].toFixed(3)} s`;$('cpRenderWait').hidden=true;root.dataset.frame=String(k);root.dataset.run=meta.run_id;renderCount++;if(!startDisplay)startDisplay=performance.now();
  for(const b of document.querySelectorAll('[data-cp-filter]'))b.setAttribute('aria-pressed',String(b.dataset.cpFilter===r.type_filter));
  root.dataset.sync='verified';$('cpScaleMin').textContent='|Δ| = 0';$('cpScaleMax').textContent=r.color_encoding.intensity_domain[1].toFixed(3);$('cpColorNote').textContent='C版：固定颜色识别类型；亮度表示偏离刺激前固定基线的幅度。八类共用固定Δ尺度，保留22%底亮与±Δ标记。下方原值条图仍使用原始活动范围和零线，未改变数据。';
  const policy=r.presentation_policy;maxFps=policy.max_fps;stepStride=policy.step_stride;root.dataset.profile=r.profile;root.dataset.fpsCap=String(maxFps);root.dataset.stepStride=String(stepStride);
  policyNotice.textContent=`${r.frame_source==='VERIFIED_PRERENDERED_FRAME'?'固定镜头缓存 · 当前不启动三维渲染进程':policy.degraded?'计算优先 · 降级显示':`${r.adapter.adapter_type} 三维绘图`} · 回放 ${$('cpSpeed').value} 模型步/秒 · 数学步长仍为5ms · 仅回放已保存结果`;
  $('cpStatus').textContent=`${playing?'正在播放':'已暂停'} · ${k<200?'运动前适应':k<=284?'亮边缘正在移动':'运动停止，保持末帧输入'} · 输入 ${meta.input_time_s[k].toFixed(3)} s → 神经活动与光流 ${meta.activity_time_s[k].toFixed(3)} s · C版画面已同步 · 已核验固定镜头（当前无需三维绘图）`;
  $('cpReceipt').textContent=`实际渲染回执：${JSON.stringify(r)}；本页收到 ${renderCount} 幅匹配帧。`;
  for(const b of $('cpTypes').children){const color=r.color_encoding.palette[b.dataset.type];b.style.setProperty('--type-color',color);b.style.color=color;}
  stage.draw(k,image,r,meta,{input:$('cpStimulus'),flow:$('cpFlow'),flowValues:flow},Number($('cpSpeed').value),null,explanationFrame);
  if(!root.dataset.offlineFirstFrameMs)root.dataset.offlineFirstFrameMs=String(performance.now());
  directionText.textContent=`${stage.canvas.dataset.explanationTitle} · ${stage.canvas.dataset.explanationDetail}`;stamp(directionText,k);directionText.dataset.status=explanationFrame.status;directionText.dataset.sha256=explanationFrame.sha256||'';
  directionText.append(document.createElement('br'),document.createTextNode(`${stage.canvas.dataset.activityStoryT4}；${stage.canvas.dataset.activityStoryT5}。${stage.canvas.dataset.activityStoryWhy}`));
 }
 function validReceipt(r,k,id){return r&&r.run_id===meta.run_id&&r.activity_sha256===meta.activity_sha256&&r.frame_index===k&&Math.abs(r.activity_time_s-meta.activity_time_s[k])<1e-12&&r.request_id===id&&r.type_filter===filter&&r.requested_profile===profile&&r.color_encoding?.encoding_sha256===packInfo?.color_encoding.encoding_sha256;}
 async function show(k){if(root.dataset.live==='true')return;desired=Math.max(0,Math.min(484,Math.round(k)));if(busy)return;busy=true;const mine=epoch,kNow=desired;desired=null;const id=crypto.randomUUID();
  const command={run_id:meta.run_id,activity_sha256:meta.activity_sha256,frame_index:kNow,activity_time_s:meta.activity_time_s[kNow],request_id:id,type_filter:'all',selected_type:selected,presentation_profile:'light',use_prerendered:true};
  try{const j=await json('/api/competition/render',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(command)});
   if(mine!==epoch)return;if(!validReceipt(j.receipt,kNow,id))throw Error('三维回执身份或时间不匹配，已拒绝混帧');const img=new Image();img.src=j.image_url;await img.decode();if(mine!==epoch)return;draw(kNow,img,j.receipt);
  }catch(error){if(mine===epoch){pause();stage.clearGuide();$('cpRenderWait').hidden=false;$('cpRenderWait').textContent='三维同步暂不可用';$('cpStatus').textContent=`NOT_AVAILABLE · ${error.message} · 已暂停；未以旧画面冒充新帧`;root.dataset.sync='unavailable';}}
  finally{busy=false;if(desired!==null)show(desired);}
 }
 function seek(k){if(exporting)return;pause();epoch++;show(k);}
 function tick(){if(!playing)return;if(root.hidden||document.hidden){pause();return;}const elapsed=(performance.now()-baseClock)/1000,rate=Number($('cpSpeed').value),raw=Math.min(484,baseFrame+Math.floor(elapsed*rate)),k=raw===484?484:baseFrame+Math.floor((raw-baseFrame)/stepStride)*stepStride;if(!busy&&k!==frame)show(k);if(elapsed>=(485-baseFrame)/rate&&frame===484&&!busy){pause();return;}playTimer=setTimeout(tick,1000/Math.max(2,Math.min(maxFps,rate)));}
 $('cpPlay').onclick=()=>{if(!meta)return;if(playing){pause();return;}playing=true;$('cpPlay').textContent='Ⅱ 暂停';baseClock=performance.now();baseFrame=frame===484?0:frame;tick();};
 $('cpStart').onclick=()=>seek(0);$('cpTimeline').oninput=e=>{pause();epoch++;clearTimeout(seekTimer);const k=Number(e.target.value);seekTimer=setTimeout(()=>show(k),80);};$('cpSpeed').onchange=()=>{pause();show(frame);};
 profileSelect.onchange=()=>{pause();profile=profileSelect.value;fixedView=profile==='light';maxFps=profile==='light'?12:15;stepStride=1;epoch++;if(meta)show(frame);};
 curveDetails.ontoggle=()=>{if(curveDetails.open&&meta&&receipt)trace(frame);};
 for(const b of document.querySelectorAll('[data-cp-filter]'))b.onclick=()=>{filter=b.dataset.cpFilter;epoch++;for(const x of document.querySelectorAll('[data-cp-filter]'))x.setAttribute('aria-pressed',String(x===b));show(frame);};
 $('cpReset').onclick=()=>{fixedView=true;camera=packInfo&&profile==='light'?null:{reset:'detail'};epoch++;show(frame);};
 stage.onSeek=k=>{if(!exporting&&root.dataset.live!=='true')seek(k);};stage.onCamera=()=>{if(root.dataset.live!=='true')policyNotice.textContent='C版比赛画面使用已核验固定镜头；拖动底部时间轴可同步查看真实响应。';};
 stage.onPlay=()=>{if(!exporting)$('cpPlay').click();};
 let pointer=null;const image=$('cpAnatomy');image.ondragstart=()=>false;image.onpointerdown=e=>{if(exporting)return;pause();pointer={x:e.clientX,y:e.clientY};image.setPointerCapture(e.pointerId);};image.onpointerup=e=>{if(!pointer||exporting)return;fixedView=false;const dx=e.clientX-pointer.x,dy=e.clientY-pointer.y;if(Math.hypot(dx,dy)<4){const b=image.getBoundingClientRect(),ratio=(receipt?.image_width||800)/(receipt?.image_height||500),ww=Math.min(b.width,b.height*ratio),hh=ww/ratio,x=(e.clientX-b.left-(b.width-ww)/2)/ww,y=(e.clientY-b.top-(b.height-hh)/2)/hh;if(x>=0&&x<=1&&y>=0&&y<=1)pick=[x,y];}else camera={rotate:[Math.max(-.5,Math.min(.5,dx*.003)),Math.max(-.5,Math.min(.5,dy*.003))]};pointer=null;epoch++;show(frame);};image.onwheel=e=>{e.preventDefault();if(exporting)return;pause();fixedView=false;camera={zoom:e.deltaY>0?.9:1.1};epoch++;show(frame);};
 let exportCancelled=false,exportID=null;
 const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 exportButton.onclick=async()=>{
  if(exporting){exportCancelled=true;exportButton.disabled=true;exportStatus.textContent='正在取消，已生成的证据会保留…';return;}
  if(!packInfo)return;
  pause();epoch++;desired=null;exporting=true;exportCancelled=false;
  const controls=Array.from(root.querySelectorAll('button,input,select')).filter(el=>el!==exportButton),previous=controls.map(el=>el.disabled);
  controls.forEach(el=>el.disabled=true);exportButton.textContent='取消视频生成';
  try{
   const waitStart=performance.now();while(busy){if(performance.now()-waitStart>30000)throw Error('上一幅画面仍未完成');await delay(20);}
   profile='light';profileSelect.value='light';filter='all';fixedView=true;camera=null;pick=null;$('cpSpeed').value=String(packInfo.playback_steps_per_second);
   const opened=await json('/api/competition/movie/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id:meta.run_id,manifest_sha256:packInfo.manifest_sha256})});exportID=opened.export_id;
   for(let k=0;k<485;k++){
    if(exportCancelled)throw Error('用户取消');
    const id=crypto.randomUUID(),j=await exportJSON('/api/competition/render',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id:meta.run_id,activity_sha256:meta.activity_sha256,frame_index:k,activity_time_s:meta.activity_time_s[k],request_id:id,type_filter:'all',selected_type:selected,presentation_profile:'light',use_prerendered:true})});
    if(!validReceipt(j.receipt,k,id)||j.receipt.frame_source!=='VERIFIED_PRERENDERED_FRAME')throw Error('导出时拒绝不匹配的帧');
    const imageBlob=await exportImage(j.image_url),bytes=await imageBlob.arrayBuffer();
    const imageSHA=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
    if(imageSHA!==j.receipt.png_sha256)throw Error('导出图片SHA不匹配 '+k);
    const bitmap=await createImageBitmap(imageBlob);try{draw(k,bitmap,j.receipt);}finally{bitmap.close();}
    const blob=await new Promise(resolve=>stage.canvas.toBlob(resolve,'image/png'));if(!blob)throw Error('无法保存实际界面画面');
    const captured=await exportJSON(`/api/competition/movie/${exportID}/frame/${k}`,{method:'POST',headers:{'Content-Type':'image/png','X-Run-ID':meta.run_id,'X-Frame-Pack':packInfo.manifest_sha256,'X-Skeleton-SHA256':j.receipt.png_sha256,'X-Activity-Time':String(meta.activity_time_s[k]),'X-Color-Encoding':j.receipt.color_encoding.encoding_sha256},body:blob});
    if(captured.export_id!==exportID||captured.captured!==k+1||captured.manifest_sha256!==packInfo.manifest_sha256)throw Error('保存回执身份或步号不匹配');
    exportStatus.textContent=`保存实际界面 ${k+1}/485：八类骨架、输入、活动和光流保持同一步。`;
   }
   await json('/api/competition/movie/finish',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({export_id:exportID})});
   exportStatus.textContent='485幅C版界面已保存，正在用CPU编码40.000秒视频；不运行神经推理。';
   let result;for(let attempt=0;attempt<310;attempt++){if(exportCancelled)throw Error('用户取消');await delay(1000);result=await json('/api/competition/movie/status');if(result.export_id!==exportID)throw Error('导出任务身份改变');if(result.status==='COMPLETED')break;if(['FAILED','CANCELLED'].includes(result.status))throw Error(result.error);}
   if(result?.status!=='COMPLETED')throw Error('编码超时');
   exportStatus.textContent=`已完成：${result.video_path} · 1080P / 30 FPS / 40.000秒 · 485个真实状态，重复帧、不插值。`;
   const link=document.createElement('a');link.href=result.video_url;link.download='FlyVis_ON60_40s_1080p.mp4';link.textContent=' 下载视频';exportStatus.append(link);root.dataset.movieExport=exportID;root.dataset.movieStatus='COMPLETED';
  }catch(error){if(exportID)try{await json('/api/competition/movie/cancel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({export_id:exportID})});}catch(_){}exportStatus.textContent=`视频未完成：${error.message}。部分证据保留，未标为成功。`;root.dataset.movieStatus='FAILED';}
  finally{exporting=false;exportID=null;controls.forEach((el,i)=>el.disabled=previous[i]);exportButton.disabled=false;exportButton.textContent='生成40秒演示视频';}
 };
 $('cpRetinaDetails').ontoggle=()=>{if(meta&&input&&receipt)retina('cpRetina',frame,true);};
 $('cpSpatialDetails').ontoggle=async()=>{if(!$('cpSpatialDetails').open||!meta)return;try{if(!spatial)spatial=await binary('spatial',485*5768);if(!viewer){viewer=new FlyVisSpatialView('cpSpatial');viewer.setMetadata(meta.spatial_metadata);viewer.$('limit').value='2';}spatialFrame(frame);}catch(e){$('cpSpatial').textContent=e.message;}};
 window.addEventListener('flyvis-workspace',e=>{if(e.detail.page!=='competition'){pause();if(stage.guideDialog.open)stage.guideDialog.close();}else initialize();});document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
 async function initialize(){if(initialized)return;initialized=true;try{meta=await json('/api/competition');if(meta.status!=='VERIFIED'||meta.display_kind!=='OFFLINE_REPLAY'||meta.PL_execution!==false||meta.frame_count!==485)throw Error('仅允许正式准入的同次软件结果');[input,flow]=await Promise.all([binary('input',485*721),binary('flow',485*1442)]);packInfo=await json('/api/competition/frames');if(packInfo.brightness_variant!=='C')throw Error('C版素材未准入');exportButton.disabled=false;const speed=$('cpSpeed').options[0];speed.value=String(packInfo.playback_steps_per_second);speed.textContent='12.125 步/秒 · 40秒';$('cpSpeed').value=speed.value;profileSelect.disabled=true;profileLabel.hidden=true;for(const button of document.querySelectorAll('[data-cp-filter]'))button.disabled=true;$('cpReset').disabled=true;image.onpointerdown=image.onpointerup=image.onwheel=null;$('cpIdentity').textContent=JSON.stringify({...meta,means:'485×8，来自本次完整活动的类型均值',coordinates_uv:'721 frozen coordinates',spatial_metadata:{map_sha256:meta.spatial_metadata.map_sha256,nodes:5768,types:meta.types},frame_pack:packInfo},null,2);
  await explanation.load(meta,flow);
  stage.guideReferences=explanation.payload?.type_roles||[];
  const info=document.createElement('p');info.textContent='T4主要参与亮边缘运动（ON），T5主要参与暗边缘运动（OFF）。八类共同参与同一网络计算；ON60是输入条件，不是模型给出的分类。a–d的方向仅作参考偏好，不代表本次单方向实验测得的调谐。亮度显示|Δ|，请同时读＋/－与原值。';interpretationContent.append(info);
  if(explanation.payload){
   const pref=document.createElement('p');pref.textContent='参考偏好：'+explanation.payload.type_roles.map(r=>`${r.type} ${r.reference_display_direction_zh} ${r.reference_preferred_direction_deg}°`).join(' · ');interpretationContent.append(pref);
   const sources=document.createElement('p');for(const source of explanation.payload.scientific_sources){const a=document.createElement('a');a.href=source.url;a.textContent=source.title;a.target='_blank';a.rel='noopener noreferrer';sources.append(a,document.createTextNode('  '));}interpretationContent.append(sources);
   const stats=document.createElement('p');stats.textContent='事后主窗统计（200–285，primary331 ROI）：原始平均向量方向70.905°，偏10.905°；扣固定基线后的派生方向62.238°，偏2.238°。两者不是当前中心点读数，也不是识别准确率。Q/E/angle衡量干预相对Sham的差异；本实验未定义识别PASS阈值。';interpretationContent.append(stats);
  }else {const unavailable=document.createElement('p');unavailable.textContent='解释数据 NOT_AVAILABLE：'+explanation.error;interpretationContent.append(unavailable);}
  for(const t of meta.types){const b=document.createElement('button');b.dataset.type=t;b.dataset.group=t.slice(0,2);b.textContent=t;const s=document.createElement('small');s.textContent='—';b.append(s);b.onclick=()=>{selected=t;filter='all';epoch++;show(frame);};$('cpTypes').append(b);} $('cpPanels').hidden=false;for(const id of ['cpPlay','cpStart','cpTimeline'])$(id).disabled=false;await show(frame);
 }catch(error){stage.clearGuide();$('cpStatus').textContent=`NOT_AVAILABLE · ${error.message}`;}}
 window.FlyVisCompetitionUI={stage,
  enterLive(){if(exporting)throw Error('请先结束视频导出');pause();stage.clearGuide();epoch++;desired=null;clearTimeout(seekTimer);root.dataset.live='true';directionText.hidden=true;interpretationDetails.hidden=true;},
  async leaveLive(){root.dataset.live='false';directionText.hidden=true;interpretationDetails.hidden=false;epoch++;await initialize();await show(frame);},
  offlineMetadata:()=>meta};
 document.body.classList.remove('competition-pending');
 if(!root.hidden)initialize();
})();
