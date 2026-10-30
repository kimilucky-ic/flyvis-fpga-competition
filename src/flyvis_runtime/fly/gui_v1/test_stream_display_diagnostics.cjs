// CPU/DOM text fixtures only; these numbers are NOT measured display performance.
const assert=require('node:assert/strict');
const d=require('../viewer/stream_display_diagnostics.js');
const doc={documentElement:{dataset:{flyvisDisplayHost:'WINDOWS_DESKTOP_WEBVIEW2'}},hasFocus:()=>true,visibilityState:'visible'};
const e=d.environment(doc,{userAgent:'CPU_TEST_ONLY'},{innerWidth:1400,innerHeight:920,devicePixelRatio:1.5});
assert.equal(e.display_host,'WINDOWS_DESKTOP_WEBVIEW2');assert.equal(e.browser_environment.has_focus,true);
delete doc.documentElement.dataset.flyvisDisplayHost;assert.equal(d.environment(doc,{userAgent:'x'},{}).display_host,'BROWSER_UNSPECIFIED');
const result={status:'COMPLETED',run_id:'CPU_TEST_ONLY',reason:'CPU_TEST_ONLY',computed_steps:4000,durable_steps:4000,journal_rows:4000,evidence_complete:true,
steps_per_s:199.99,display_FPS:20,receipt_to_draw_p95_upper_ms:100,render_p50_ms:19,raf_wait_p50_ms:10,draw_count:201,draw_span_s:10,
display_hosts:['CPU_TEST_ONLY'],hidden_draws:0,nominal_200_step_pacing:true,display_at_least_15_FPS:true,latency_p95_below_200_ms:true,evidence_folder:'CPU_TEST_ONLY'};
assert.match(d.formatSummary(result),/199\.99/);assert.match(d.formatSummary(result),/不自动签发实时 PASS/);
assert.match(d.formatSummary({...result,status:'FAILED',evidence_complete:false,journal_rows:3999}),/记录完整：否/);
assert.match(d.formatSummary({...result,display_FPS:null,receipt_to_draw_p95_upper_ms:null}),/未测得/);
assert.match(d.formatSummary({status:'WAITING_FOR_GPU_AND_EVIDENCE_FINALIZATION'}),/还不是完成确认/);
assert.match(d.formatDraw({render_ms:19,raf_wait_ms:907,packet_slot_age_ms:37},1,'WINDOWS_DESKTOP_WEBVIEW2'),/等待刷新 907\.0 ms/);
console.log(JSON.stringify({status:'PASS_CPU_DISPLAY_DIAGNOSTICS',checks:8,actual_GPU_or_browser_runs:0}));
