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
