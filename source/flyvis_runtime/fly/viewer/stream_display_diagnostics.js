'use strict';
(() => {
  const number=(n,d=1)=>Number.isFinite(n)?n.toFixed(d):'未测得';
  function environment(doc,nav,win){
    return {display_host:doc.documentElement.dataset.flyvisDisplayHost||'BROWSER_UNSPECIFIED',
      browser_environment:{user_agent:nav.userAgent.slice(0,256),width:win.innerWidth,height:win.innerHeight,
        device_pixel_ratio:win.devicePixelRatio,has_focus:doc.hasFocus(),visibility:doc.visibilityState}};
  }
  function formatDraw(draw,fps,host){
    return `显示环境：${host==='WINDOWS_DESKTOP_WEBVIEW2'?'Windows 桌面 WebView2':'普通/内置浏览器（详见记录）'} · 实际绘制 ${number(fps)} FPS · 本帧绘图 ${number(draw.render_ms)} ms · 等待刷新 ${number(draw.raf_wait_ms)} ms · 最新数据在显示槽中 ${number(draw.packet_slot_age_ms)} ms`;
  }
  function formatSummary(s){
    if(s.status==='WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION')return '正在等待 GPU 停止和记录保存完成；这还不是完成确认。';
    return [`${s.status==='COMPLETED'?'本次运行已结束':'本次运行失败'} · ${s.reason}`,
      `run：${s.run_id}`,
      `已计算 ${s.computed_steps} 步 / 可靠提交 ${s.durable_steps} 步 / 日志 ${s.journal_rows} 条 · 记录完整：${s.evidence_complete?'是':'否'}`,
      `实际运行 ${number(s.compute_wall_s,3)} s / 模型推进 ${number(s.model_time_s,3)} s · 数学步长5ms`,
      `模型 ${number(s.steps_per_s,2)} 步/s · 实际显示 ${number(s.display_FPS,2)} FPS · 接收→绘制 p95 上界 ${number(s.receipt_to_draw_p95_upper_ms)} ms`,
      `绘图中位数 ${number(s.render_p50_ms)} ms · 等待刷新中位数 ${number(s.raf_wait_p50_ms)} ms · 样本 ${s.draw_count} 次 / ${number(s.draw_span_s)} s`,
      `窗口：${(s.display_hosts||[]).join(', ')||'未记录'} · 后台/隐藏绘制 ${s.hidden_draws} 次`,
      s.clock?.mode==='SLOW_MODEL_DEMO'?`慢速演示 ${s.clock.target_steps_per_s} 步/实际秒 · 完成观察：${s.observation_completed?'是':'否'} · 所选节奏±1%：${s.selected_pacing_within_1_percent?'达到':'未达到'} · 不作为200步/s原速实时验收`:
      `约200步/s节奏：${s.nominal_200_step_pacing===null?'未测得':s.nominal_200_step_pacing?'达到（0.5%范围内）':'未达到'} · FPS≥15：${s.display_at_least_15_FPS===null?'未测得':s.display_at_least_15_FPS?'是':'否'} · p95<200ms：${s.latency_p95_below_200_ms===null?'未测得':s.latency_p95_below_200_ms?'是':'否'}`,
      '本摘要不自动签发实时 PASS；请结合实际画面验收。实体 FPGA：NOT_CONNECTED。',
      `记录目录：${s.evidence_folder}`].join('\n');
  }
  function terminalReason(reason,status,run){
    const late=['STREAM_RESULT_REVOKED','RAW_REVOKED_DURING_RENDER','DRAW_RESULT_REVOKED','STREAM_STOP_REQUESTED'];
    return late.includes(reason)&&run&&status?.run_id===run.run_id&&status?.session_id===run.session_id&&status.result_valid===false&&status.compute?.error==='STREAM_OBSERVATION_COMPLETE'?'STREAM_OBSERVATION_COMPLETE':reason;
  }
  const api={environment,formatDraw,formatSummary,terminalReason};
  if(typeof module!=='undefined')module.exports=api;
  if(typeof window!=='undefined')window.FlyVisDisplayDiagnostics=api;
})();
