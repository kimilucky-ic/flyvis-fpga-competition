/* Independent optional panel; failure never interrupts accepted replay. */
(() => {
  const el = id => document.getElementById(id);
  const labels = {Full_GPU:'Full GPU · 本次对照',Python_Replacement:'Python Replacement · SOURCE_RAW',FPGA_Replacement:'FPGA Replacement'};
  const row = (name,value) => {
    const div=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');
    dt.textContent=name;dd.textContent=value;div.append(dt,dd);el('phase3Identity').append(div);
  };
  async function refresh() {
    try {
      const response=await fetch('/api/phase3',{cache:'no-store'});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const data=await response.json(),input=data.input;
      el('phase3Status').textContent=data.status==='ready'?'已验证软件计算结果 · 当前离线回放':input?'输入身份已核对 · 等待本次800步对照结果':'交接不可用 · 原55条件仍可回放';
      el('phase3Modes').replaceChildren();el('phase3Identity').replaceChildren();
      for(const [key,label] of Object.entries(labels)){
        const node=document.createElement('span');
        node.textContent=`${label}：${data[key]?.available?'已验证结果包 · 回放':key==='FPGA_Replacement'?'unavailable · 无已验收板级结果':'等待 B 同身份结果包'}`;
        el('phase3Modes').append(node);
      }
      if(input){
        row('comparison_id',input.comparison_id);row('单条件输入 SHA256',input.identity_fingerprint.stimulus);
        row('完整初态 SHA256',input.identity_fingerprint.initial);row('GPU 展开参数 SHA256',input.identity_fingerprint.expanded);
        row('模型输入 / Euler 后活动时间','0.000–3.995 s / 0.005–4.000 s；step_id=0…799');
        row('源帧时间','60 FPS 文件时间；因果 ZOH；非摄像头采集时间');
        row('核验范围',input.scope);
      }
      el('phase3Open').disabled=data.status!=='ready';
      el('phase3Open').onclick=()=>window.dispatchEvent(new CustomEvent('flyvis-phase3-open',{detail:{comparison_id:input.comparison_id}}));
      const error=data.error||(data.errors||[]).join('；');
      el('phase3Blockers').textContent=error?`交接错误：${error}`:data.status==='ready'?'软件结果包已通过GUI只读核验。GPU在线服务未连接；FPGA须另有C实际板级结果与身份验收。':'待 B 提供同 comparison_id 的 Full GPU / 独立 Python H + GPU R 完整800步轨迹、逐步误差、PREPARED/COMMITTED摘要链、因果与失败验收及SHA清单。待 C 提供实际板级结果后才能开放FPGA。';
    }catch(error){
      el('phase3Status').textContent='交接状态读取失败 · 原55条件仍可回放';
      el('phase3Modes').replaceChildren();el('phase3Identity').replaceChildren();
      el('phase3Blockers').textContent=error.message;
    }
  }
  window.addEventListener('flyvis-phase3-clear',()=>el('phase3ComparisonView').classList.add('hidden'));
  window.addEventListener('flyvis-phase3-frame',event=>{
    const {frame,mode,info}=event.detail,run=info.modes[mode];
    el('phase3ComparisonView').classList.remove('hidden');
    el('phase3Step').textContent=`step_id=${frame} / 799 · 输入 ${(frame*.005).toFixed(3)} s · Euler后 ${(frame*.005+.005).toFixed(3)} s · 全网最大误差 ${info.errors.full.max_abs[frame].toExponential(3)} · 超限 ${info.errors.full.violations[frame]}`;
    el('phase3Run').textContent=`${mode} · ${run.evidence_level} · run_id=${run.run_id} · 原计算 ${run.wall_s.toFixed(3)} s；步时延 p50/p95/p99=${run.step_latency_ms.p50.toFixed(2)}/${run.step_latency_ms.p95.toFixed(2)}/${run.step_latency_ms.p99.toFixed(2)} ms。当前离线回放；5ms为模型步长。`;
    const canvas=el('phase3ErrorChart'),bounds=canvas.getBoundingClientRect(),scale=Math.min(devicePixelRatio||1,2),w=Math.max(1,bounds.width),h=Math.max(1,bounds.height);
    canvas.width=Math.round(w*scale);canvas.height=Math.round(h*scale);
    const ctx=canvas.getContext('2d');ctx.setTransform(scale,0,0,scale,0,0);ctx.clearRect(0,0,w,h);
    const left=60,right=w-15,top=20,bottom=h-25,values=info.errors.full.max_abs,peak=Math.max(...values)*1.15||1e-9;
    ctx.font='10px Segoe UI';ctx.fillStyle='#91a4b8';ctx.fillText('max |Python − Full| · 全45669节点',left,12);
    for(let i=0;i<3;i++){const y=bottom-(bottom-top)*i/2;ctx.strokeStyle='#253447';ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();ctx.fillText((peak*i/2).toExponential(1),2,y+3);}
    ctx.strokeStyle='#f4ca78';ctx.beginPath();values.forEach((v,k)=>{const x=left+(right-left)*k/799,y=bottom-(bottom-top)*v/peak;k?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();
    const x=left+(right-left)*frame/799;ctx.strokeStyle='#d1f4f3';ctx.beginPath();ctx.moveTo(x,top);ctx.lineTo(x,bottom);ctx.stroke();
    ctx.fillStyle='#91a4b8';ctx.fillText('0.005 s',left,h-5);ctx.fillText('Euler 后 4.000 s',right-100,h-5);
  });
  refresh();
})();
