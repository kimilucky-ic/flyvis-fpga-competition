/* The actual GUI stage is also the exported video frame. No new neural values. */
(() => {
 'use strict';
 class CompetitionStage {
  constructor(){
   this.canvas=document.createElement('canvas');this.canvas.id='cpStage';this.canvas.width=1920;this.canvas.height=1080;
   this.canvas.setAttribute('aria-label','同步比赛演示：视觉输入、八类真实骨架、带符号活动概览及官方光流');
   this.host=document.createElement('div');this.host.className='cp-stage-host';this.host.append(this.canvas);
   const panels=document.getElementById('cpPanels');panels.before(this.host);
   const analysis=document.createElement('details');analysis.id='cpAnalysis';analysis.className='cp-more';
   const summary=document.createElement('summary');summary.textContent='深入分析 · 原始图表、曲线、视角控制';analysis.append(summary);panels.before(analysis);analysis.append(panels);
   this.c=this.canvas.getContext('2d',{alpha:false});this.c.fillStyle='#08111b';this.c.fillRect(0,0,1920,1080);this.text('正在核验同次实验与三维画面…',80,120,34,'#b4d8e0');
   const player=document.querySelector('.cp-player');
   this.cinema=document.createElement('button');this.cinema.id='cpCinema';this.cinema.textContent='全屏';
   this.cinema.onclick=()=>document.body.classList.add('competition-cinema');player.append(this.cinema);
   this.optionsButton=document.createElement('button');this.optionsButton.id='cpOptions';this.optionsButton.textContent='实验设置';this.optionsButton.setAttribute('aria-expanded','false');this.optionsButton.onclick=()=>{const open=document.getElementById('competitionWorkspace').classList.toggle('cp-show-tools');this.optionsButton.setAttribute('aria-expanded',String(open));};player.append(this.optionsButton);
   this.guideButton=document.createElement('button');this.guideButton.id='cpGuideOpen';this.guideButton.textContent='放大科学讲解';this.guideButton.disabled=true;this.guideButton.onclick=()=>this.openGuide();player.append(this.guideButton);
   this.guideDialog=document.createElement('dialog');this.guideDialog.id='cpGuideDialog';this.guideDialog.className='cp-guide-dialog';this.guideDialog.setAttribute('aria-labelledby','cpGuideTitle');
   this.guideDialog.innerHTML='<header><div><small>跟随当前画面 · 不另开计算任务</small><h2 id="cpGuideTitle">这一帧，怎么看懂？</h2></div><button id="cpGuideClose" aria-label="关闭科学讲解">关闭 ×</button></header><p id="cpGuideClock"></p><div class="cp-guide-grid"><section><h3>① 果蝇看到了什么？</h3><p id="cpGuideInput"></p><h3>② 网络读出了什么？</h3><strong id="cpGuideResult"></strong><p id="cpGuideDetail"></p><p id="cpGuideComparison"></p></section><section><h3 class="cp-guide-T4">③ T4 · 主要处理亮边缘运动</h3><p id="cpGuideT4"></p><h3 class="cp-guide-T5">T5 · 主要处理暗边缘运动</h3><p id="cpGuideT5"></p><p id="cpGuideReference"></p></section></div><section class="cp-guide-why"><h3>④ 为什么这些神经元变亮？</h3><p id="cpGuideWhy"></p><p id="cpGuideConclusion"></p><small id="cpGuideQuantity"></small></section><footer><div><button id="cpGuidePrev">前一步</button><button id="cpGuidePlay">播放 / 暂停</button><button id="cpGuideNext">后一步</button></div><button id="cpGuideSources">科学依据与原始身份</button></footer><small id="cpGuideIdentity"></small>';
   document.body.append(this.guideDialog);this.guideFields={};for(const id of ['Clock','Input','Result','Detail','Comparison','T4','T5','Reference','Why','Conclusion','Quantity','Identity'])this.guideFields[id]=this.guideDialog.querySelector('#cpGuide'+id);
   this.guideDialog.querySelector('#cpGuideClose').onclick=()=>this.guideDialog.close();this.guideDialog.querySelector('#cpGuideSources').onclick=()=>{this.guideDialog.close();this.onSources?.();};
   this.guideDialog.querySelector('#cpGuidePrev').onclick=()=>{if(this.guide?.canSeek)this.onSeek?.(Math.max(0,this.guide.step-1));};this.guideDialog.querySelector('#cpGuideNext').onclick=()=>{if(this.guide?.canSeek)this.onSeek?.(Math.min(484,this.guide.step+1));};this.guideDialog.querySelector('#cpGuidePlay').onclick=()=>{if(this.guide?.canSeek)this.onPlay?.();};
   this.guideObserver=new MutationObserver(()=>{if(!['STOPPED_PENDING_JOINT_AUDIT','OFFLINE_REPLAY','OFFLINE_REPLAY_FULL_NETWORK_FPGA','CURRENT_FULL_PL_STATE_PENDING_AUDIT','FINISHED_FULL_PL_LAST_STATE','LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT','LIVE_CAMERA_GPU','LIVE_DIGITAL_GPU'].includes(this.canvas.dataset.displayKind))this.clearGuide();});this.guideObserver.observe(this.canvas,{attributes:true,attributeFilter:['data-display-kind']});
   this.exit=document.createElement('button');this.exit.id='cpCinemaExit';this.exit.textContent='返回操作界面 · Esc';this.exit.onclick=()=>document.body.classList.remove('competition-cinema');document.body.append(this.exit);
   document.addEventListener('keydown',e=>{if(e.key==='Escape')document.body.classList.remove('competition-cinema');if(e.code==='Space'&&document.body.classList.contains('competition-cinema')){e.preventDefault();this.onPlay?.();}});
   let point=null;const xy=e=>{const r=this.canvas.getBoundingClientRect();return [(e.clientX-r.left)*1920/r.width,(e.clientY-r.top)*1080/r.height];};
   this.canvas.onpointerdown=e=>{point=xy(e);this.canvas.setPointerCapture(e.pointerId);};
   this.canvas.onpointerup=e=>{if(!point)return;const p=xy(e),dx=p[0]-point[0],dy=p[1]-point[1];
    if(point[0]>=34&&point[0]<1342&&point[1]>=86&&point[1]<676&&Math.hypot(dx,dy)>4)this.onCamera?.({rotate:[Math.max(-.5,Math.min(.5,dx*.002)),Math.max(-.5,Math.min(.5,dy*.002))]});
    point=null;
   };
   this.canvas.onwheel=e=>{const p=xy(e);if(p[0]>=34&&p[0]<1342&&p[1]>=86&&p[1]<676){e.preventDefault();this.onCamera?.({zoom:e.deltaY>0?.9:1.1});}};
   this.canvas.ondragstart=()=>false;
  }
  text(value,x,y,size=22,color='#d9e9f1',bold=false){const c=this.c;c.fillStyle=color;c.font=`${bold?'600 ':''}${size}px "Microsoft YaHei", "Segoe UI", sans-serif`;c.fillText(value,x,y);}
  box(x,y,w,h,color='#0f1f2c',border='#294353'){const c=this.c;c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,18);c.fill();c.strokeStyle=border;c.lineWidth=1;c.stroke();}
  wrapped(value,x,y,width,size=22,color='#c0d5de',bold=false,maxLines=3){
   this.c.font=`${bold?'600 ':''}${size}px "Microsoft YaHei", "Segoe UI", sans-serif`;
   const lines=[];let line='';for(const char of String(value)){if(line&&this.c.measureText(line+char).width>width){lines.push(line);line='';}line+=char;}if(line)lines.push(line);
   lines.slice(0,maxLines).forEach((text,i)=>this.text(i===maxLines-1&&lines.length>maxLines?text.slice(0,-1)+'…':text,x,y+i*(size+9),size,color,bold));
  }
  referenceDirections(){
   const roles=this.guideReferences||[],arrows={0:'→',90:'↑',180:'←',270:'↓'};
   const rows=['a','b','c','d'].map(letter=>{const a=roles.find(r=>r.type==='T4'+letter),b=roles.find(r=>r.type==='T5'+letter);return a&&b&&a.reference_preferred_direction_deg===b.reference_preferred_direction_deg&&arrows[a.reference_preferred_direction_deg]?{letter,deg:a.reference_preferred_direction_deg,arrow:arrows[a.reference_preferred_direction_deg],name:a.reference_display_direction_zh}:null;});
   return rows.every(Boolean)?rows:[];
  }
  clearGuide(){this.guide=null;if(this.guideButton)this.guideButton.disabled=true;if(this.guideDialog?.open)this.guideDialog.close();this.canvas.dataset.guideStatus='NOT_AVAILABLE';if(this.c){this.c.fillStyle='#0f1f2c';this.c.fillRect(1385,85,500,960);this.text('当前帧未核验',1396,126,25,'#c0d5de');}}
  openGuide(){if(this.guide?.available&&!this.guideDialog.open)this.guideDialog.showModal();}
  updateGuide(guide){
   this.guide=guide;if(!guide.available){this.clearGuide();return;}
   this.guideButton.disabled=false;const f=this.guideFields;
   f.Clock.textContent=`第 ${guide.step} 步 · 输入 ${guide.inputTime===null?'时间未提供':guide.inputTime.toFixed(3)+' s'} → 更新后活动 ${guide.activityTime.toFixed(3)} s · ${guide.evidence}`;
   for(const [key,value] of Object.entries({Input:guide.input,Result:guide.title,Detail:guide.detail,Comparison:guide.comparison,T4:guide.T4,T5:guide.T5,Why:guide.why,Conclusion:guide.conclusion,Quantity:guide.quantity}))f[key].textContent=value;
   const references=guide.canSeek?this.guideReferences:[];
   f.Reference.textContent=references?.length?'a–d 官方参考偏好：'+references.filter(r=>r.family==='T4').map(r=>`${r.type.slice(2)} ${r.reference_display_direction_zh}`).join('、')+'。这是参考标注，不是由本次单方向实验测得的调谐。':'';
   f.Identity.textContent=`run ${guide.run} · k${guide.step} · 说明与画面使用同一步；FPGA 身份以本次运行证据为准。`;
   Object.assign(this.guideDialog.dataset,{run:guide.run,frame:String(guide.step),inputTime:guide.inputTime===null?'':String(guide.inputTime),activityTime:String(guide.activityTime),evidence:guide.evidence});
   for(const id of ['Prev','Play','Next'])this.guideDialog.querySelector('#cpGuide'+id).hidden=!guide.canSeek;
   Object.assign(this.canvas.dataset,{guideStatus:'AVAILABLE',guideRun:guide.run,guideFrame:String(guide.step),guideInput:guide.input,guideTitle:guide.title,guideWhy:guide.why});
   this.canvas.setAttribute('aria-label',`同一步输入、神经元与官方光流。科学解读：${guide.input}；网络读出：${guide.title}；${guide.T4}；${guide.T5}；${guide.why}`);
  }
  drawGuide(guide){
   const x=1396,w=480;
   if(!guide.available){this.text('当前帧未核验',x,120,25,'#c0d5de');return;}
   this.wrapped('T4、T5 是两类处理局部运动的果蝇视觉神经元。',x,115,w,24,'#c5dce5',false,2);
   this.text('T4：看变亮的边缘（ON）',x,201,27,'#a5e8d8',true);
   this.text('T5：看变暗的边缘（OFF）',x,249,27,'#c7b8ff',true);
   this.text('a–d：四个方向亚型',x,334,27,'#e2f1f3',true);
   const refs=this.referenceDirections();if(refs.length)refs.forEach((r,i)=>this.text(`${r.letter}  ${r.arrow} ${r.name.replace(/^向/,'')}`,x+(i%2)*242,390+Math.floor(i/2)*58,31,'#b9e8db',true));else this.text('参考方向未核验',x,390,23,'#b8cad2');
   this.text('官方参考偏好；本帧方向看光流。',x,499,20,'#a9c2cd');
   this.text('颜色与亮度',x,578,27,'#e2f1f3',true);
   this.text('颜色区分类型。',x,619,23,'#c5dce5');
   this.wrapped(guide.why,x,660,w,23,'#c5dce5',false,3);
   this.wrapped('每条骨架代表一类，亮度取该类 721 个模型节点的均值。',x,772,w,20,'#9ebac8',false,2);
   this.text(this.canvas.dataset.explanationPhase==='HELD_FINAL_INPUT'?'停止后的响应':this.canvas.dataset.explanationPhase==='PRE_STIMULUS'?'灰背景下的活动':'本帧活动',x,869,27,'#e2f1f3',true);
   if(this.canvas.dataset.activityStoryAvailable==='true'){
    this.wrapped(guide.T4,x,913,w,23,'#a5e8d8',false,2);this.wrapped(guide.T5,x,991,w,23,'#c7b8ff',false,2);
   }else this.wrapped('本模式没有核验刺激前基线，升降对比暂不可用。',x,913,w,23,'#b7cbd5',false,3);
  }
  drawNeurons(image,rect,responseC,palette){
   const c=this.c,width=image.naturalWidth||image.width,height=image.naturalHeight||image.height,scale=Math.min(rect.w/width,rect.h/height),iw=width*scale,ih=height*scale,dx=rect.x+(rect.w-iw)/2,dy=rect.y+(rect.h-ih)/2;
   c.drawImage(image,dx,dy,iw,ih);
   // Only fixed C's old annotation boxes/caption are restyled; all geometry and
   // activity pixels, the scale bar and the immutable original PNG are retained.
   if(responseC&&width===1280&&height===640){
    c.save();c.translate(dx,dy);c.scale(scale,scale);
    for(const [x,types] of [[205,['T4d','T4c','T4b','T4a']],[930,['T5c','T5d','T5b','T5a']]])types.forEach((t,i)=>{const y=78+i*134;c.fillStyle='#08141f';c.fillRect(x-1,y-1,147,70);this.box(x,y+12,145,44,'#0b1a25',palette[t]);this.text(t,x+13,y+43,26,palette[t],true);});
    c.fillStyle='#08141f';c.fillRect(290,612,770,24);c.restore();
   }
   this.canvas.dataset.neuronImageRect=JSON.stringify({x:dx,y:dy,w:iw,h:ih});this.canvas.dataset.annotationPolicy=responseC?'C_FIXED_TYPE_LABELS_ONLY':'ORIGINAL_LABELS';
  }
  directionArrow(deg,color){const c=this.c,x=453,y=902,length=29,a=deg*Math.PI/180,dx=Math.cos(a)*length,dy=-Math.sin(a)*length,theta=Math.atan2(dy,dx);c.strokeStyle=color;c.lineWidth=3;c.beginPath();c.moveTo(x,y);c.lineTo(x+dx,y+dy);for(const side of [-.5,.5]){c.moveTo(x+dx-8*Math.cos(theta+side),y+dy-8*Math.sin(theta+side));c.lineTo(x+dx,y+dy);}c.stroke();}
  explain(explanation,live,fx,fy){
   let input=null,estimate=null,difference=null,phase='NOT_AVAILABLE',title='方向解释暂不可用',detail='实际光流仍显示；未套用其他运行的说明';
   if(live){
    estimate=Math.hypot(fx,fy)>=.0001?(Math.atan2(fy,fx)*180/Math.PI+360)%360:null;
    title=estimate===null?'中心运动估计接近零':`模型估计 ${estimate.toFixed(1)}°（中心）`;
    detail='输入方向GT未核验 · 方向偏差不可用';phase='LIVE_GT_NOT_AVAILABLE';
   }else if(explanation?.status==='VERIFIED'){
    phase=explanation.phase;
    if(explanation.raw_direction_comparison_available){
     input=explanation.known_input.direction_deg;estimate=explanation.raw_center_bearing_deg;difference=explanation.raw_center_difference_from_input_deg;
     title=`输入 ${input}° → 估计 ${estimate.toFixed(1)}°`;
     detail=`相差 ${difference.toFixed(1)}° · 中心位置 / 原始光流`;
    }else if(phase==='PRE_STIMULUS'){title='等待运动输入';detail='当前为灰背景 · 此阶段不评方向偏差';}
    else if(phase==='HELD_FINAL_INPUT'){title='运动停止 · 观察后续响应';detail='保持末帧输入 · 此阶段不评方向偏差';}
    else {title='中心运动读出接近零';detail='当前方向不可用 · 没有识别成功率阈值';}
   }
   // The result sentence comes from this frame's official flow, never input GT.
   const output=window.FlyVisMotionExplanation.readout(fx,fy);
   const baseline=!live&&explanation?.status==='VERIFIED'&&phase==='PRE_STIMULUS';
   const held=!live&&explanation?.status==='VERIFIED'&&phase==='HELD_FINAL_INPUT';
   const result=baseline?'正在适应灰背景':output.available?`网络估计：朝${output.direction}运动`:'中心方向暂不可用';
   const resultDetail=baseline?'尚未出现运动刺激，当前是基线响应':output.available?`${output.bearing.toFixed(1)}° · 画面中心${held?' · 运动停止后的响应':''}`:'当前向量不足以显示方向';
   Object.assign(this.canvas.dataset,{explanationStatus:live?'LIVE_GT_NOT_AVAILABLE':explanation?.status||'NOT_AVAILABLE',explanationSha:live?'':explanation?.sha256||'',inputDirection:input===null?'':String(input),estimatedDirection:estimate===null?'':String(estimate),directionDifference:difference===null?'':String(difference),explanationPhase:phase,directionComparisonAvailable:String(input!==null&&estimate!==null),accuracyPass:'NOT_DEFINED',explanationTitle:result,explanationDetail:resultDetail,comparisonTitle:title,comparisonDetail:detail,readoutDirection:output.direction||'',readoutBearing:output.bearing===null?'':String(output.bearing),readoutMagnitude:output.magnitude===null?'':String(output.magnitude),readoutSource:'SAME_FRAME_OFFICIAL_FLOW_CENTER'});
  }
  draw(k,image,r,meta,canvases,stepsPerSecond,live=null,explanation=null){
   const c=this.c,encoding=r.color_encoding,responseC=!live&&encoding.mode==='fixed_type_hue_baseline_response_brightness_v1',M=responseC?encoding.raw_activity_domain[1]:encoding.intensity_domain[1],palette=encoding.palette;
   c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);
   const camera=live?.sourceKind==='real_windows_camera',joint=live?.joint,fullPL=live?.backend==='FULL_NETWORK_FPGA';
   this.box(20,20,1336,674);this.box(20,710,654,350);this.box(690,710,666,350);this.box(1372,20,528,1040);
   this.text('神经元',44,66,32,'#edf7f8',true);this.text('果蝇看到了什么',44,754,30,'#edf7f8',true);this.text('光流',714,754,30,'#edf7f8',true);this.text('神经元解释',1396,66,32,'#edf7f8',true);
   const rect={x:34,y:86,w:1308,h:590};this.drawNeurons(image,rect,responseC,palette);
   c.drawImage(canvases.input,0,0,400,340,44,780,300,255);c.drawImage(canvases.flow,0,0,400,270,706,780,390,263.25);
   const phase=fullPL?(live.stream?'本步721感光输入':'⑪ 固定首帧 · 模型首步'):live?(camera?'摄像头当前画面':`${live.parameters.polarity} ${live.parameters.direction_deg}°`):k<200?'灰背景适应':k<=284?'亮边缘沿 60° 移动':'运动已停止';
   this.wrapped(phase,366,856,280,25,'#a8dfd4',true,3);this.text(fullPL?(live.stream?(live.finished?'本次计算已结束':'实体PL状态·轨迹待审计'):'实体PL结果·离线回放'):joint?'联合计算·待终验':live?'本次 GPU 计算':'离线回放',494,752,17,'#95c4b5');
   const ix=meta.coordinates_uv.findIndex(([u,v])=>u===0&&v===0),fx=canvases.flowValues[k*1442+ix],fy=canvases.flowValues[k*1442+721+ix];
   this.explain(explanation,live,fx,fy);const story=window.FlyVisMotionExplanation.activityStory(r.type_states,encoding,!!live);
   Object.assign(this.canvas.dataset,{run:meta.run_id,frame:String(live?live.step:k),inputTime:meta.input_time_s?.[k]===undefined?'':String(meta.input_time_s[k]),activityTime:String(meta.activity_time_s[k]),wallElapsed:live?String(live.wallElapsed):'',targetStepsPerSecond:live?String(live.clock.target_steps_per_s??'COMMIT_DRIVEN'):'',clockMode:live?live.clock.mode:'OFFLINE_REPLAY',skeletonSha:r.raw_sha256||r.png_sha256,colorEncoding:encoding.encoding_sha256,displayKind:joint?'LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT':live?(camera?'LIVE_CAMERA_GPU':'LIVE_DIGITAL_GPU'):'OFFLINE_REPLAY',sourceKind:live?.sourceKind||'recorded_experiment',sourceSequence:live?String(live.sourceSequence):String(k),means:JSON.stringify(meta.means[k]),brightnessVariant:responseC?'C':live?'LIVE_ABS':'LEGACY_ABS',rawActivityMax:String(M),deltaValues:responseC?JSON.stringify(r.type_states.map(s=>s.delta_signed)):'',activityStoryT4:story.T4,activityStoryT5:story.T5,activityStoryWhy:story.why,activityStoryAvailable:String(story.available),activityUp:JSON.stringify(story.up),activityDown:JSON.stringify(story.down),activityNear:JSON.stringify(story.near),neuronViewport:JSON.stringify(rect),numericStripHeight:'0',layoutMode:'FOUR_PANELS'});
   if(fullPL)Object.assign(this.canvas.dataset,{backend:'FULL_NETWORK_FPGA',displayKind:live.stream?(live.finished?'FINISHED_FULL_PL_LAST_STATE':'CURRENT_FULL_PL_STATE_PENDING_AUDIT'):'OFFLINE_REPLAY_FULL_NETWORK_FPGA',clockMode:live.stream?'FULL_PL_STEP_DRIVEN':'SAVED_RESULT',readoutSource:live.stream&&Number.isFinite(fx)&&Number.isFinite(fy)?'SAME_FRAME_OFFICIAL_FLOW_CENTER':'NOT_AVAILABLE',explanationStatus:'NOT_AVAILABLE'});else delete this.canvas.dataset.backend;
   const guide=window.FlyVisMotionExplanation.guide(this.canvas.dataset);this.drawGuide(guide);this.updateGuide(guide);
   const output=window.FlyVisMotionExplanation.readout(fx,fy),baseline=this.canvas.dataset.explanationPhase==='PRE_STIMULUS';this.text(baseline?'等待运动':output.available?`中心：${output.direction}`:'暂不可用',1120,878,27,'#a3ebd6',true);if(output.available&&!baseline)this.text(`${output.bearing.toFixed(1)}°`,1120,927,35,'#dceff2',true);
  }
 }
 window.FlyVisCompetitionStage=CompetitionStage;
})();
