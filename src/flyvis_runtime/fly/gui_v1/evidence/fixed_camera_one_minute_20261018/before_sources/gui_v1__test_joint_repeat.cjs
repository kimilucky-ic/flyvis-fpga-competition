/* Lifecycle-only fake HTTP/DOM. No browser, camera, GPU or physical board. */
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const nodes={},timers=[],starts=[];let phase='READY_TO_START',round=0,entered=0;
function node(id){return nodes[id]??=( {id,hidden:false,disabled:false,textContent:'original-'+id,dataset:{},append(){},after(){},getContext(){return {fillRect(){},drawImage(){}}}} );}
const canvas={dataset:{}},stage={canvas,c:{fillStyle:'',fillRect(){}},text(){},onPlay(){},onSeek(){}};
const status=()=>({repeat_enabled:true,family_id:'family',workbench_phase:phase,can_start:['READY_TO_START','COMPLETE'].includes(phase),
 ready_for_camera:phase==='GPU_PREPARING',runtime_policy:'MINIMAL_COMPUTE_ASYNC_V1',live_response_hz:5,
 run_id:'run'+round,session_id:'session'+round,identity:null,error:null});
const ctx={window:{FlyVisCompetitionUI:{stage,enterLive(){entered++;},leaveLive:async()=>{}},addEventListener(){}},
 document:{getElementById:node,createElement:()=>node('new'+Math.random()),querySelector:node,querySelectorAll:()=>[]},
 crypto:require('crypto').webcrypto,Uint8Array,Float32Array,Blob,performance:{now:()=>1},console,
 setTimeout:(fn,delay)=>{timers.push({fn,delay});return timers.length;},
 FlyVisFixedSkeleton:{load:async()=>({})},
 fetch:async(path,options)=>{let body=options?.body?JSON.parse(options.body):null,value;
  if(path.endsWith('/status'))value=status();
  else if(path.endsWith('/rearm')){assert.equal(body.family_id,'family');round++;phase='GPU_PREPARING';value={status:'START_REQUESTED'};}
  else if(path.endsWith('/prepare'))value={};
  else if(path.endsWith('/start')){starts.push(body);phase='RUNNING';value={};}
  else if(path.endsWith('/latest')){phase='AUDITING';value={status:{...status(),stop_acknowledged:true},packet:null};}
  else if(path.endsWith('/preview'))value={run_id:'run'+round,session_id:'session'+round,live_preview:false,packet:null};
  else if(path.endsWith('/stop')||path.endsWith('/quit'))value={};
  else throw Error(path);
  return {ok:true,json:async()=>value};
 }};
vm.runInNewContext(fs.readFileSync(require('path').join(__dirname,'../viewer/competition_joint.js'),'utf8'),ctx);
const drain=async()=>{for(let k=0;k<30;k++)await Promise.resolve();};
(async()=>{
 await drain();assert.equal(node('cpJointStart').disabled,false);
 await node('cpJointStart').onclick();await drain();assert.equal(starts.length,1);assert.equal(node('cpJointStart').disabled,true);
 phase='COMPLETE';const ready=timers.find(x=>x.delay===500);assert(ready);await ready.fn();await drain();
 assert.equal(node('cpJointStart').disabled,false);assert(node('cpJointState').textContent.includes('再次开始'));
 await node('cpJointStart').onclick();await drain();assert.equal(starts.length,2);assert.notEqual(starts[0].run_id,starts[1].run_id);
 assert.equal(entered,2);assert.equal(node('cpJointQuit').hidden,false);
 console.log(JSON.stringify({status:'PASS',checks:9,scope:'MOCK_HTTP_DOM_REPEAT_START_AUDIT_START_ONLY',GPU:0,camera:0,board:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
