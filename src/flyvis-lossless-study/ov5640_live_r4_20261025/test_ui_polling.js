// CPU-only DOM shim: exercise polling/pause/reconnect without a board or browser.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=__dirname,out=fs.readFileSync(path.join(root,'evidence/latest_cpu.txt'),'utf8').trim();
const packet=JSON.parse(fs.readFileSync(path.join(out,'display_packets.json'),'utf8'))[1];
let queued=[],requests=[],renders=0,disconnect=false,pauseDuring=false;
const elements={};for(const id of ['toggle','status','error','camera','neural','display','timing'])elements[id]={textContent:'',src:'',getContext:()=>({putImageData:()=>{}})};
const status={received:32,max_steps:32,audit_status:'PASS_ALL_SAVED_STATES',mismatch_words:0,finished:true,producer_status:'ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING',camera_close_status:'NOT_CONFIRMED',last_received_unix:Date.now()/1000};
const context={performance,console,ImageData:class{},Image:class{async decode(){}},
 document:{getElementById:id=>elements[id],body:{classList:{toggle(){},add(){}}}},
 FlyVisFixedSkeleton:{load:async()=>({render:async()=>{renders++;return {pixels:new Uint8ClampedArray(4),width:1,height:1};}})},
 fetch:async url=>{requests.push(url);if(url==='/projection')return {json:async()=>({})};
  if(disconnect)throw Error('offline');
  if(pauseDuring){pauseDuring=false;elements.toggle.onclick();}
  return {ok:true,json:async()=>url==='/status'?status:{packet:url.endsWith('after=31')?null:packet,status}};
 },setTimeout:fn=>queued.push(fn)};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'assets/ui.js'),'utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 await flush();assert.equal(renders,1);assert(requests.includes('/latest?after=-1'));
 queued.shift()();await flush();assert.equal(renders,1);assert.equal(requests.at(-1),'/latest?after=31');
 elements.toggle.onclick();queued.shift()();await flush();assert.equal(requests.at(-1),'/status');assert.equal(renders,1);
 elements.toggle.onclick();disconnect=true;queued.shift()();await flush();assert(elements.error.textContent.includes('offline'));
 disconnect=false;queued.shift()();await flush();assert.equal(renders,1);assert(!elements.status.textContent.includes('undefined'));
 pauseDuring=true;queued.shift()();await flush();assert(!elements.status.textContent.includes('undefined'));
 assert(requests.every(x=>!x.includes('/step')&&!x.includes('/ingest')));
 assert(elements.status.textContent.includes('尚未确认，不代表已关闭'));
 status.camera_close_status='CLOSED';queued.shift()();await flush();assert(elements.status.textContent.includes('相机关闭：已确认'));
 status.camera_close_status='FAILED';queued.shift()();await flush();assert(elements.status.textContent.includes('相机关闭：失败'));
 const r={separate_camera_status_verified:true,status:'PASS_CPU_UI_POLLING_PAUSE_AND_RECONNECT',render_calls:1,unchanged_frame_not_redrawn:true,
 pause_uses_status_only:true,reconnect_reads_only:true,pause_during_inflight_response_safe:true,native_browser:false,hardware_actions:0};
 fs.writeFileSync(path.join(root,'evidence/UI_POLLING_RESULT.json'),JSON.stringify(r,null,2));console.log(JSON.stringify(r));
})().catch(e=>{console.error(e);process.exitCode=1});
