/* Read-only interpretation, gated by the existing run/k/image receipt. No clock. */
(() => {
 'use strict';
 const SHA='9b31e0902b8cc14187ad7196ebdf75101c78dba64cabf60c8d21482d857811f1';
 const RUN='2041849d-b1f8-46ad-a059-49b598c19ab2';
 const check=(ok,message)=>{if(!ok)throw Error(message);};
 class MotionExplanation {
  static readout(fx,fy){
   if(!Number.isFinite(fx)||!Number.isFinite(fy))return {available:false,direction:null,magnitude:null,bearing:null};
   const magnitude=Math.hypot(fx,fy);
   if(magnitude<.0001)return {available:false,direction:null,magnitude,bearing:null};
   const bearing=(Math.atan2(fy,fx)*180/Math.PI+360)%360;
   // Plain quadrant wording; the exact angle remains the original atan2 value.
   const zero=magnitude*1e-12;
   const direction=Math.abs(fx)<=zero?(fy>0?'上':'下'):Math.abs(fy)<=zero?(fx>0?'右':'左'):(fx>0?'右':'左')+(fy>0?'上':'下');
   return {available:true,direction,magnitude,bearing};
  }
  static activityStory(states,encoding,live=false){
   const valid=!live&&encoding?.mode==='fixed_type_hue_baseline_response_brightness_v1'&&states?.length===8&&Number.isFinite(encoding.display_deadband)&&states.every(s=>Number.isFinite(s.delta_signed));
   if(!valid)return {available:false,T4:'T4：处理亮边缘运动',T5:'T5：处理暗边缘运动',why:'本模式亮度看活动幅度；没有刺激前基线，不判断升降。',up:[],down:[],near:[]};
   const tau=encoding.display_deadband,up=states.filter(s=>s.delta_signed>tau).map(s=>s.type),down=states.filter(s=>s.delta_signed<-tau).map(s=>s.type),near=states.filter(s=>Math.abs(s.delta_signed)<=tau).map(s=>s.type);
   const describe=family=>{
    const a=up.filter(t=>t.startsWith(family)),b=down.filter(t=>t.startsWith(family));
    if(a.length===4)return `${family}：四组活动都升高（＋）`;
    if(b.length===4)return `${family}：四组活动都降低（－）`;
    if(a.length+b.length===0)return `${family}：四组都接近刺激前水平`;
    const labels=items=>items.map(t=>t.slice(2)).join('、');
    return `${family}：`+[a.length?`${labels(a)}组升高`:null,b.length?`${labels(b)}组降低`:null].filter(Boolean).join('；');
   };
   return {available:true,T4:describe('T4'),T5:describe('T5'),why:'为什么亮？与刺激前相比变化越大越亮；＋是升高，－是降低。',up,down,near};
  }
  static guide(d){
   // Consume only the current, receipt-gated stage. No independent clock/data load.
   if(!d?.run||!/^\d+$/.test(d.frame||'')||!['OFFLINE_REPLAY','OFFLINE_REPLAY_FULL_NETWORK_FPGA','CURRENT_FULL_PL_STATE_PENDING_AUDIT','FINISHED_FULL_PL_LAST_STATE','LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT','LIVE_CAMERA_GPU','LIVE_DIGITAL_GPU'].includes(d.displayKind)||d.activityTime===''||!Number.isFinite(Number(d.activityTime))||(d.inputTime!==''&&!Number.isFinite(Number(d.inputTime))))return {available:false};
   const offline=d.displayKind==='OFFLINE_REPLAY',verified=offline&&d.explanationStatus==='VERIFIED',baseline=verified&&d.explanationPhase==='PRE_STIMULUS',held=verified&&d.explanationPhase==='HELD_FINAL_INPUT';
   const sameFlow=d.readoutSource==='SAME_FRAME_OFFICIAL_FLOW_CENTER';
   const fullPL=d.displayKind==='OFFLINE_REPLAY_FULL_NETWORK_FPGA',fullStream=['CURRENT_FULL_PL_STATE_PENDING_AUDIT','FINISHED_FULL_PL_LAST_STATE'].includes(d.displayKind);
   const input=fullStream?'本步实际721感光输入；未借用其他实验画面':fullPL?'⑪固定验证输入首帧；不是ON60实验':baseline?'灰色背景，运动还没开始':held?'边缘已停止，当前保持末帧':verified&&d.inputDirection!==''?`亮边缘沿 ${d.inputDirection}° 移动`:offline?'当前输入的运动标注未核验':d.sourceKind==='real_windows_camera'?'本次真实摄像头画面；运动方向未标注':'本次数字刺激；方向真值未核验';
   const title=baseline?'等待运动输入':sameFlow?d.explanationTitle.replace(/^网络估计：/,''):'本步方向暂不可用';
   return {available:true,run:d.run,step:Number(d.frame),inputTime:d.inputTime===''?null:Number(d.inputTime),activityTime:Number(d.activityTime),
    evidence:fullStream?(d.displayKind==='FINISHED_FULL_PL_LAST_STATE'?'本次PL计算已结束 · 保留最后状态 · 轨迹待审计':'当前完整PL状态 · 轨迹待审计 · 不宣称实时PASS'):fullPL?'实体PL首步 · OFFLINE REPLAY · 当前未连接':offline?'真实软件结果 · OFFLINE REPLAY':d.displayKind==='LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT'?'本步已提交 · GPU–FPGA 整轮待终验':'本次实际 GPU 计算',
    input,title,detail:sameFlow?d.explanationDetail:'缺少本步官方光流身份',comparison:verified&&sameFlow&&d.directionComparisonAvailable==='true'?d.comparisonDetail:'',
    T4:d.activityStoryT4||'T4：当前活动说明不可用',T5:d.activityStoryT5||'T5：当前活动说明不可用',
    why:d.activityStoryAvailable==='true'?'与刺激前相比，变化越大越亮。＋是升高，－是降低；变亮也可能是活动降低。':'亮度表示本步活动幅度；没有刺激前基线，不判断升高或降低。',
    conclusion:'方向由八类活动共同参与的网络读出，不能把最亮的一组当成识别结果。',
    quantity:'每组显示 721 个模型节点的平均活动；不是单个生物细胞的测量。',
    canSeek:offline};
  }
  constructor(){this.payload=null;this.error=null;}
  async load(meta,flow){
   try{
    const response=await fetch('/api/competition/explanation?run='+encodeURIComponent(meta.run_id));
    check(response.ok,'解释资料暂不可用');const bytes=await response.arrayBuffer();
    const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
    check(sha===SHA,'解释资料SHA256不匹配');const p=JSON.parse(new TextDecoder().decode(bytes));
    check(p.schema==='line10.motion_explanation.v1'&&p.version==='20261017.1'&&p.run_id===RUN&&meta.run_id===RUN&&p.activity_sha256===meta.activity_sha256&&p.frames.length===485,'解释资料运行身份不匹配');
    const i=meta.coordinates_uv.findIndex(([u,v])=>u===0&&v===0);check(i>=0,'中心坐标缺失');
    p.frames.forEach((r,k)=>{
     check(r.frame_index===k&&r.input_time_s===meta.input_time_s[k]&&r.activity_time_s===meta.activity_time_s[k],'解释资料双时间轴不匹配');
     check(r.raw_center_vector[0]===flow[k*1442+i]&&r.raw_center_vector[1]===flow[k*1442+721+i],'解释资料与原始光流不匹配');
     check(r.type_states.every((s,j)=>s.type===meta.types[j]&&s.raw_mean===meta.means[k][j]),'解释资料与实际活动不匹配');
     check(r.success_badge==='NOT_DEFINED'&&r.known_input.direction_deg===(k>=200&&k<=284?60:null),'解释资料阶段或判断不匹配');
    });
    this.payload=p;this.error=null;
   }catch(error){this.payload=null;this.error=error.message;}
   return this;
  }
  frame(k,receipt,meta){
   if(!this.payload)return {status:'NOT_AVAILABLE',error:this.error||'解释资料尚未核验'};
   const p=this.payload,r=p.frames[k];
   check(r&&receipt.run_id===p.run_id&&meta.run_id===p.run_id&&receipt.activity_sha256===p.activity_sha256&&receipt.frame_index===k&&receipt.activity_time_s===r.activity_time_s&&meta.input_time_s[k]===r.input_time_s,'解释与当前画面回执不同步');
   check(receipt.type_states?.length===8&&receipt.type_states.every((s,i)=>s.type===r.type_states[i].type&&s.value===r.type_states[i].raw_mean&&Math.abs(s.delta_signed-r.type_states[i].delta_from_fixed_C_baseline)<1e-12),'解释与C画面活动不匹配');
   return {status:'VERIFIED',run_id:p.run_id,sha256:SHA,...r,raw_direction_comparison_available:r.known_input.direction_deg!==null&&r.raw_center_bearing_deg!==null};
  }
 }
 window.FlyVisMotionExplanation=MotionExplanation;
})();
