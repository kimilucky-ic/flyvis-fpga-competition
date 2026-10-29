"""One bounded edit of the existing viewer presentation; no scientific code."""
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
p=ROOT/'viewer/competition_stage.js'
s=p.read_text(encoding='utf-8')
assert '   this.buildPrimer();' in s
s=s.replace('   this.buildPrimer();\n','')
a=s.index('  buildPrimer(){');b=s.index('  clearGuide(){',a)
s=s[:a]+s[b:]
s=s.replace('this.updatePrimer(null);','').replace('   this.updatePrimer(guide);\n','')
s=s.replace("this.cinema.textContent='录屏视图'","this.cinema.textContent='全屏'")
s=s.replace("   this.guideButton=document.createElement('button');", "   this.optionsButton=document.createElement('button');this.optionsButton.id='cpOptions';this.optionsButton.textContent='实验设置';this.optionsButton.setAttribute('aria-expanded','false');this.optionsButton.onclick=()=>{const open=document.getElementById('competitionWorkspace').classList.toggle('cp-show-tools');this.optionsButton.setAttribute('aria-expanded',String(open));};player.append(this.optionsButton);\n   this.guideButton=document.createElement('button');")
a=s.index('    if(point[1]>=991');b=s.index('    point=null;',a)
s=s[:a]+"    if(point[0]>=34&&point[0]<1342&&point[1]>=86&&point[1]<676&&Math.hypot(dx,dy)>4)this.onCamera?.({rotate:[Math.max(-.5,Math.min(.5,dx*.002)),Math.max(-.5,Math.min(.5,dy*.002))]});\n"+s[b:]
s=s.replace('p[0]>396&&p[1]>288&&p[1]<872','p[0]>=34&&p[0]<1342&&p[1]>=86&&p[1]<676')
a=s.index('  drawGuide(guide){');b=s.index('  directionArrow(',a)
s=s[:a]+'''  drawGuide(guide){
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
   this.text('本帧活动',x,869,27,'#e2f1f3',true);
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
'''+s[b:]
# Explain still computes exactly the same current-flow and scientific identity.
s=s.replace("   this.text(result,46,868,21,'#d6f2ec',true);this.text(baseline?'等待刺激':output.available?`${output.bearing.toFixed(1)}° · 画面中心`:'方向暂不可用',46,901,18,'#b7cfd8');\n   this.text('箭头：方向与强弱',46,935,18,'#98b8c7');\n",'')
a=s.index('  draw(k,image,r,meta,canvases,stepsPerSecond,live=null,explanation=null){')
b=s.index('   Object.assign(this.canvas.dataset,{run:',a)
identity=s[b:s.index('\n  }',b)]
identity=identity.replace("numericStripHeight:'54'","numericStripHeight:'0',layoutMode:'FOUR_PANELS'")
identity=identity.replace('this.drawGuide(guide);this.updateGuide(guide);',"this.drawGuide(guide);this.updateGuide(guide);\n   const output=window.FlyVisMotionExplanation.readout(fx,fy),baseline=this.canvas.dataset.explanationPhase==='PRE_STIMULUS';this.text(baseline?'等待运动':output.available?output.direction:'暂不可用',1120,878,31,'#a3ebd6',true);if(output.available&&!baseline)this.text(`${output.bearing.toFixed(1)}°`,1120,927,35,'#dceff2',true);")
draw='''  draw(k,image,r,meta,canvases,stepsPerSecond,live=null,explanation=null){
   const c=this.c,encoding=r.color_encoding,responseC=!live&&encoding.mode==='fixed_type_hue_baseline_response_brightness_v1',M=responseC?encoding.raw_activity_domain[1]:encoding.intensity_domain[1],palette=encoding.palette;
   c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);
   const camera=live?.sourceKind==='real_windows_camera',joint=live?.joint;
   this.box(20,20,1336,674);this.box(20,710,654,350);this.box(690,710,666,350);this.box(1372,20,528,1040);
   this.text('神经元',44,66,32,'#edf7f8',true);this.text('果蝇看到了什么',44,754,30,'#edf7f8',true);this.text('光流',714,754,30,'#edf7f8',true);this.text('神经元解释',1396,66,32,'#edf7f8',true);
   const rect={x:34,y:86,w:1308,h:590};this.drawNeurons(image,rect,responseC,palette);
   c.drawImage(canvases.input,0,0,400,340,44,780,300,255);c.drawImage(canvases.flow,0,0,400,270,706,780,390,263.25);
   const phase=live?(camera?'摄像头当前画面':`${live.parameters.polarity} ${live.parameters.direction_deg}°`):k<200?'灰背景适应':k<=284?'亮边缘沿 60° 移动':'运动已停止';
   this.wrapped(phase,366,856,280,25,'#a8dfd4',true,3);this.text(joint?'联合计算·待终验':live?'本次 GPU 计算':'离线回放',494,752,17,'#95c4b5');
   const ix=meta.coordinates_uv.findIndex(([u,v])=>u===0&&v===0),fx=canvases.flowValues[k*1442+ix],fy=canvases.flowValues[k*1442+721+ix];
   this.explain(explanation,live,fx,fy);const story=window.FlyVisMotionExplanation.activityStory(r.type_states,encoding,!!live);
'''
s=s[:a]+draw+identity+'\n  }\n }\n window.FlyVisCompetitionStage=CompetitionStage;\n})();\n'
p.write_text(s,encoding='utf-8')

p=ROOT/'viewer/competition.css';s=p.read_text(encoding='utf-8')
marker='/* Use the existing canvas letterboxing for an always-visible scientific primer. */'
assert marker in s;s=s[:s.index(marker)]
s+='''/* Default presentation: exactly four regions and one compact control bar. */
body[data-workspace=competition] main{max-width:none;padding:8px 12px}
body[data-workspace=competition] .topbar,body[data-workspace=competition] .intro,body[data-workspace=competition] main>footer{display:none!important}
body[data-workspace=competition] .workspace-nav{margin:0 0 7px;padding:0 0 6px}
body[data-workspace=competition] #cpStage{width:100%;height:auto;margin:0}
body[data-workspace=competition] .cp-stage-host{position:relative;box-sizing:border-box;width:100%;margin:8px 0 0}
#cpGuideOpen{display:none!important}
#competitionWorkspace:not(.cp-show-tools)>:not(.cp-player):not(.cp-stage-host){display:none!important}
#competitionWorkspace:not(.cp-show-tools) #cpExport{display:none!important}
#competitionWorkspace[data-sync=unavailable] #cpStatus{display:block!important;color:#ffbc9d}
#competitionWorkspace .cp-player{padding:8px 12px;gap:10px}
#competitionWorkspace .cp-direction-comparison,#competitionWorkspace .cp-role-key{display:none!important}
.competition-cinema .cp-stage-host{position:fixed!important;inset:0;margin:0!important;width:100%!important}
'''
p.write_text(s,encoding='utf-8')
print('Updated only viewer/competition_stage.js and viewer/competition.css')
