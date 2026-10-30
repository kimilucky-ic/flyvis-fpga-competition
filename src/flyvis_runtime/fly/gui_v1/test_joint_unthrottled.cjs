/* Actual consumer with a virtual clock / fake HTTP+canvas, saved arrays only.
 * Not a browser, GPU benchmark, camera capture or physical-board test. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(path.join(__dirname,'../viewer/competition_joint.js'),'utf8');
const saved=JSON.parse(fs.readFileSync(path.join(__dirname,'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json'),'utf8'));
Object.assign(saved,{runtime_policy:'MINIMAL_COMPUTE_ASYNC_V1',live_response_hz:5,
 display_kind:'LIVE_LOW_RATE_LATEST_COMMITTED_STATE',evidence_level:'ACK_MATCHED_RAM_ONLY_ASYNC_RECORDING'});
Object.assign(saved.transaction,{integer_error:null,numerical_check:'DEFERRED_OFFLINE'});saved.durable={barrier:'NOT_SYNCHRONOUS'};
const identity=Object.fromEntries(['run_id','session_id','model','mapping_sha256','hardware','runtime_policy','live_response_hz'].map(k=>[k,saved[k]]));
async function scenario({errorAt=Infinity,wrongRun=false,renderMs=0}={}){
 let now=0,stopCalls=0,previewDraws=0;const nodes={},timers=[],draws=[],receipts=[];
 const context2d={fillRect(){},drawImage(){previewDraws++;},putImageData(){},beginPath(){},closePath(){},moveTo(){},lineTo(){},fill(){},stroke(){}};
 function node(id){return nodes[id]??=({id,hidden:false,disabled:false,textContent:id,dataset:{},children:[],
  append(){},after(){},getContext(){return context2d;}});}
 const stage={canvas:node('stage'),c:context2d,text(){},onPlay(){},onSeek(){},draw(k,raw,r,meta,images,fps,options){
  draws.push({step:options.step,at:now,source:options.sourceSequence,token:options.stateToken});}};
 const status=()=>({...identity,ready_for_camera:true,error:null,identity,stop_acknowledged:false});
 function packet(k){const p=JSON.parse(JSON.stringify(saved));Object.assign(p,{serial:k+1,step_id:k,state_token:k+1,input_time_s:k*.005,activity_time_s:k*.005+.005});
  Object.assign(p.spatial,{step_id:k,state_token:k+1});p.transaction.step_id=k;p.source.sequence=k;
  if(wrongRun&&k>0)p.run_id='0'.repeat(32);return p;}
 const ctx={window:{FlyVisCompetitionUI:{stage,enterLive(){},leaveLive:async()=>{}},addEventListener(){}},
  document:{getElementById:node,createElement:()=>node('new'+Object.keys(nodes).length),querySelector:node,querySelectorAll:()=>[]},
  crypto:require('crypto').webcrypto,Uint8Array,Uint8ClampedArray,Float32Array,Blob,console,
  atob:s=>Buffer.from(s,'base64').toString('binary'),performance:{now:()=>now},
  ImageData:class {constructor(data,width,height){Object.assign(this,{data,width,height});}},
  createImageBitmap:async()=>({width:8,height:8,close(){}}),requestAnimationFrame:fn=>fn(now),
  setTimeout:(fn,delay)=>{timers.push({fn,at:now+delay});return timers.length;},
  FlyVisFixedSkeleton:{load:async()=>({render:async p=>{now+=renderMs;return {width:1,height:1,pixels:new Uint8ClampedArray(4),
   receipt:{types:[],means:[],raw_sha256:'CPU_CANVAS_MOCK',projection_cache_sha256:'CPU_CANVAS_MOCK'}};}})},
  fetch:async(url,options)=>{let value;
   if(url.endsWith('/status'))value=status();
   else if(url.endsWith('/prepare'))value={projection_cache:{upstream_map_sha256:saved.spatial.map_sha256},joint_spatial_global_ids:saved.PL_participating_global_ids,coordinates_uv:Array.from({length:721},()=>[0,0])};
   else if(url.endsWith('/start'))value={};
   else if(url.endsWith('/latest'))value={status:{...status(),error:now>=errorAt?'CPU_TEST_REVOKED':null,stop_acknowledged:now>=450},packet:packet(Math.min(9,Math.floor(now/50)))};
   else if(url.endsWith('/preview'))value={...identity,live_preview:true,packet:{source:{...saved.source,sequence:Math.floor(now/60)},png:saved.preview_png}};
   else if(url.endsWith('/clock'))value={server_monotonic_ns:1e9};
   else if(url.endsWith('/draw')){receipts.push(JSON.parse(options.body));value={latency:{upper_ms:0}};}
   else if(url.endsWith('/stop')){stopCalls++;value={};}
   else throw Error(url);
   return {ok:true,json:async()=>value};}};
 vm.runInNewContext(code,ctx);
 const flush=async()=>{for(let i=0;i<10;i++)await new Promise(setImmediate);};
 await flush();await node('cpJointStart').onclick();await flush();
 for(let i=0;i<80&&node('competitionWorkspace').dataset.jointState!=='FAILED'&&node('competitionWorkspace').dataset.jointState!=='STOPPED_PENDING_PS_AUDIT';i++){
  await flush();timers.sort((a,b)=>a.at-b.at);const next=timers.shift();assert(next,'consumer stalled');now=Math.max(now,next.at);await next.fn();await flush();}
 await flush();
 assert.equal(receipts.length,draws.length);
 for(let k=0;k<draws.length;k++){const d=draws[k],r=receipts[k];assert.equal(r.step_id,d.step);assert.equal(r.state_token,d.token);assert.equal(r.run_id,saved.run_id);
  if(k)assert(d.at-draws[k-1].at>=200,'neural frames exceeded 5Hz');}
 return {draws,previewDraws,stopCalls,state:node('competitionWorkspace').dataset.jointState,display:stage.canvas.dataset.displayKind};
}
(async()=>{
 const fast=await scenario();assert.equal(fast.state,'STOPPED_PENDING_PS_AUDIT');assert.equal(fast.draws.at(-1).step,9);
 assert(fast.draws.length<10&&fast.draws.some((d,i)=>i&&d.step-fast.draws[i-1].step>1),'must coalesce, not replay queued frames');
 assert(fast.previewDraws>fast.draws.length,'camera preview must be independent of neural draw cadence');
 const slow=await scenario({renderMs:120});assert.equal(slow.state,'STOPPED_PENDING_PS_AUDIT');assert.equal(slow.draws.at(-1).step,9);
 const failed=await scenario({errorAt:100});assert.equal(failed.state,'FAILED');assert.equal(failed.draws.length,1);assert.equal(failed.stopCalls,1);assert.equal(failed.display,'NOT_AVAILABLE');
 const mixed=await scenario({wrongRun:true});assert.equal(mixed.state,'FAILED');assert.equal(mixed.draws.length,1);assert.equal(mixed.display,'NOT_AVAILABLE');
 console.log(JSON.stringify({status:'PASS',scenarios:4,evidence:'CPU_FAKE_HTTP_CANVAS_VIRTUAL_CLOCK_SAVED_ARRAYS_ONLY',
  fast_draws:fast.draws,slow_draws:slow.draws,preview_draws:fast.previewDraws,GPU:0,camera:0,board:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
