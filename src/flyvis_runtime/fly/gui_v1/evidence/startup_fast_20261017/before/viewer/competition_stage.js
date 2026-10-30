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
   this.cinema=document.createElement('button');this.cinema.id='cpCinema';this.cinema.textContent='录屏视图';
   this.cinema.onclick=()=>document.body.classList.add('competition-cinema');player.append(this.cinema);
   this.exit=document.createElement('button');this.exit.id='cpCinemaExit';this.exit.textContent='返回操作界面 · Esc';this.exit.onclick=()=>document.body.classList.remove('competition-cinema');document.body.append(this.exit);
   document.addEventListener('keydown',e=>{if(e.key==='Escape')document.body.classList.remove('competition-cinema');if(e.code==='Space'&&document.body.classList.contains('competition-cinema')){e.preventDefault();this.onPlay?.();}});
   let point=null;const xy=e=>{const r=this.canvas.getBoundingClientRect();return [(e.clientX-r.left)*1920/r.width,(e.clientY-r.top)*1080/r.height];};
   this.canvas.onpointerdown=e=>{point=xy(e);this.canvas.setPointerCapture(e.pointerId);};
   this.canvas.onpointerup=e=>{if(!point)return;const p=xy(e),dx=p[0]-point[0],dy=p[1]-point[1];
    if(point[1]>=991&&point[1]<1040)this.onSeek?.(Math.round(Math.max(0,Math.min(1,(p[0]-46)/1828))*484));
    else if(point[0]>542&&point[1]>154&&point[1]<802&&Math.hypot(dx,dy)>4)this.onCamera?.({rotate:[Math.max(-.5,Math.min(.5,dx*.002)),Math.max(-.5,Math.min(.5,dy*.002))]});
    point=null;
   };
   this.canvas.onwheel=e=>{const p=xy(e);if(p[0]>542&&p[1]>154&&p[1]<802){e.preventDefault();this.onCamera?.({zoom:e.deltaY>0?.9:1.1});}};
   this.canvas.ondragstart=()=>false;
  }
  text(value,x,y,size=22,color='#d9e9f1',bold=false){const c=this.c;c.fillStyle=color;c.font=`${bold?'600 ':''}${size}px "Microsoft YaHei", "Segoe UI", sans-serif`;c.fillText(value,x,y);}
  box(x,y,w,h,color='#0f1f2c',border='#294353'){const c=this.c;c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,18);c.fill();c.strokeStyle=border;c.lineWidth=1;c.stroke();}
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
   this.text(result,50,885,26,'#d6f2ec',true);this.text(resultDetail,50,918,19,'#b7cfd8');
   this.text('方向由网络综合读出，不能只看最亮的一组。',50,949,18,'#98b8c7');
   if(output.available&&!baseline)this.directionArrow(output.bearing,'#76e5d0');
   Object.assign(this.canvas.dataset,{explanationStatus:live?'LIVE_GT_NOT_AVAILABLE':explanation?.status||'NOT_AVAILABLE',explanationSha:live?'':explanation?.sha256||'',inputDirection:input===null?'':String(input),estimatedDirection:estimate===null?'':String(estimate),directionDifference:difference===null?'':String(difference),explanationPhase:phase,directionComparisonAvailable:String(input!==null&&estimate!==null),accuracyPass:'NOT_DEFINED',explanationTitle:result,explanationDetail:resultDetail,comparisonTitle:title,comparisonDetail:detail,readoutDirection:output.direction||'',readoutBearing:output.bearing===null?'':String(output.bearing),readoutMagnitude:output.magnitude===null?'':String(output.magnitude),readoutSource:'SAME_FRAME_OFFICIAL_FLOW_CENTER'});
  }
  draw(k,image,r,meta,canvases,stepsPerSecond,live=null,explanation=null){
   const c=this.c,W=1920,H=1080,encoding=r.color_encoding,responseC=!live&&encoding.mode==='fixed_type_hue_baseline_response_brightness_v1',M=responseC?encoding.raw_activity_domain[1]:encoding.intensity_domain[1],palette=encoding.palette;
   c.fillStyle='#08111b';c.fillRect(0,0,W,H);
   this.text('FlyVis',36,49,34,'#f2fafb',true);this.text('从一束光，到运动感知',190,49,30,'#dcecf4',true);
   const camera=live?.sourceKind==='real_windows_camera',joint=live?.joint;
   this.text(joint?'摄像头 · GPU R / FPGA H':live?(camera?'真实摄像头 · 原始完整网络':`${live.parameters.polarity} ${live.parameters.direction_deg}° · 原始完整网络`):'ON 60° · 原始完整网络',1100,47,23,'#99bdcc');this.text(joint?'本步已提交 · 整轮待终验':live?'本次 GPU 新计算 · 实况显示':'真实软件结果 · 离线慢放',1515,47,23,'#80e1cb');
   // 72% of the main stage width belongs to the eight-skeleton response panel.
   this.box(28,82,480,420);this.box(28,518,480,450);this.box(526,82,1366,886);
   this.text('01  果蝇看到了什么？',50,127,28,'#e8f4fa',true);
   const phase=live?`${camera?'摄像头实际输入':'数字运动输入'} · 源帧 ${live.sourceSequence}`:k<200?'运动前：适应灰色背景':k<=284?'运动中：亮边缘沿 60° 移动':'运动停止：保持末帧输入';
   this.text(phase,50,166,22,'#8de2d3');
   c.drawImage(canvases.input,0,0,400,340,88,178,360,278);
   this.text(live?'本次实际画面 / 右下 721 点映射':'同次实验的 721 点视觉输入',62,480,21,'#9dbac8');
   this.text('03  网络估计往哪里动？',50,563,28,'#e8f4fa',true);
   c.drawImage(canvases.flow,0,0,400,270,68,588,400,270);
   const ix=meta.coordinates_uv.findIndex(([u,v])=>u===0&&v===0),fx=canvases.flowValues[k*1442+ix],fy=canvases.flowValues[k*1442+721+ix],m=Math.hypot(fx,fy);
   this.explain(explanation,live,fx,fy);
   this.text('02  哪些神经元在处理运动？',552,128,31,'#eef7fa',true);
   this.text('T4：处理亮边缘的运动',560,170,25,'#a5e8d8',true);this.text('T5：处理暗边缘的运动',1210,170,25,'#c7b8ff',true);
   this.text('每类都有 a、b、c、d 四组；颜色帮助你找到小组，下面解释它们为何变亮。',560,201,20,'#b1cbd5');
   const rect={x:548,y:211,w:1322,h:526},width=image.naturalWidth||image.width,height=image.naturalHeight||image.height,scale=Math.min(rect.w/width,rect.h/height),iw=width*scale,ih=height*scale;
   c.save();c.beginPath();c.rect(rect.x,rect.y,rect.w,rect.h);c.clip();c.drawImage(image,rect.x+(rect.w-iw)/2,rect.y+(rect.h-ih)/2,iw,ih);c.restore();
   const story=window.FlyVisMotionExplanation.activityStory(r.type_states,encoding,!!live);
   this.text(story.T4,560,765,22,'#a5e8d8',true);this.text(story.T5,1210,765,22,'#c7b8ff',true);
   this.text(story.why,560,800,21,'#c0d5de');this.text('下方保留每组的原始活动值和升降量；每组取721个模型节点均值。',560,825,17,'#9bbbc8');
   this.text(live?`固定范围 ±${M.toFixed(3)} | *亮度封顶`:`原值零线 0  |  固定范围 ±${M.toFixed(3)}`,1500,824,19,'#9ebdcb');
   meta.types.forEach((t,i)=>{
    const x=550+i*165,v=meta.means[k][i],hue=palette[t],zeroY=896;
    this.box(x,838,154,110,'#112430','#294252');
    c.fillStyle=hue;c.fillRect(x+12,850,12,12);this.text(t,x+31,866,22,hue,true);
    this.text(`${v>=0?'+':''}${v.toFixed(live?4:3)}`,x+76,866,live?18:20,'#eef4f9',true);
    if(live&&r.type_states[i].saturated)this.text('*',x+132,886,18,'#ffd59e',true);
    c.strokeStyle='#83a0b0';c.lineWidth=1;c.beginPath();c.moveTo(x+13,zeroY);c.lineTo(x+141,zeroY);c.stroke();
    const length=Math.min(1,Math.abs(v)/M)*25;c.fillStyle=hue;c.fillRect(x+36,v>=0?zeroY-length:zeroY,82,Math.max(length,1));
    const delta=responseC?r.type_states[i].delta_signed:null;
    this.text(responseC?`Δ ${delta>=0?'+':''}${delta.toFixed(3)}`:v>0?'正值':v<0?'负值':'零',x+(responseC?34:60),938,responseC?18:15,'#9fbdc9');
   });
   // Both clocks are explicit. Playback never changes the five-millisecond model step.
   this.text(live?`实际 ${live.wallElapsed.toFixed(2)} s · 模型 ${meta.activity_time_s[k].toFixed(3)} s`:`回放 ${(k/stepsPerSecond).toFixed(1)} / ${(485/stepsPerSecond).toFixed(1)} 秒`,34,998,22,'#dcecf4',true);
   this.text(joint?'按实际 COMMIT 推进 · 数学步长 5ms · 采集与模型时间分别记录':live?`${live.clock.target_steps_per_s}步/实际秒 · ${live.clock.model_seconds_per_wall_second}×时钟 · 数学步长 5ms`:`${stepsPerSecond} 模型步/播放秒  ·  原模型步长 5 ms`,490,998,21,'#93bdc9');
   this.text(`原始步 ${live?live.step:k+( '/484')}  ·  活动 t=${meta.activity_time_s[k].toFixed(3)} s`,1200,998,21,'#aac8d4');
   c.fillStyle='#263e4d';c.fillRect(46,1015,1828,8);if(!live){c.fillStyle='#77d7c7';c.fillRect(46,1015,1828*(k+1)/485,8);
   for(const edge of [200,285]){c.fillStyle='#ccdcdf';c.fillRect(46+1828*edge/485,1011,2,16);}}
   this.text((r.rendering_method==='fixed_SWCs_CPU_projection_composite'?'固定镜头投影 · ':'')+'真实 SWC 骨架代表细胞类型；亮度为模型均值，非单细胞测量。',34,1063,18,'#91aebb');
   this.text(`run ${meta.run_id.slice(0,8)} · ${joint?'PL 5768 · ACK匹配／待终验':'FPGA 未连接'}`,1420,1063,18,'#91aebb');
   Object.assign(this.canvas.dataset,{run:meta.run_id,frame:String(live?live.step:k),activityTime:String(meta.activity_time_s[k]),wallElapsed:live?String(live.wallElapsed):'',targetStepsPerSecond:live?String(live.clock.target_steps_per_s??'COMMIT_DRIVEN'):'',clockMode:live?live.clock.mode:'OFFLINE_REPLAY',skeletonSha:r.raw_sha256||r.png_sha256,colorEncoding:encoding.encoding_sha256,displayKind:joint?'LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT':live?(camera?'LIVE_CAMERA_GPU':'LIVE_DIGITAL_GPU'):'OFFLINE_REPLAY',sourceKind:live?.sourceKind||'recorded_experiment',sourceSequence:live?String(live.sourceSequence):String(k),means:JSON.stringify(meta.means[k]),brightnessVariant:responseC?'C':live?'LIVE_ABS':'LEGACY_ABS',rawActivityMax:String(M),deltaValues:responseC?JSON.stringify(r.type_states.map(s=>s.delta_signed)):'',activityStoryT4:story.T4,activityStoryT5:story.T5,activityStoryWhy:story.why,activityStoryAvailable:String(story.available),activityUp:JSON.stringify(story.up),activityDown:JSON.stringify(story.down),activityNear:JSON.stringify(story.near)});
  }
 }
 window.FlyVisCompetitionStage=CompetitionStage;
})();
