// CPU-only browser lifecycle stub: recording must precede capture; failure blocks capture.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../viewer/competition_joint.js'),'utf8');
async function run(recordingFailure){
 const calls=[],elements=new Map(),el=id=>{if(!elements.has(id))elements.set(id,{disabled:false,hidden:false,textContent:'',dataset:{},after(){}});return elements.get(id);};
 let currentRecorder;
 const stage={canvas:{dataset:{},captureStream(){calls.push('captureStream');return {getTracks:()=>[{stop(){calls.push('trackStopped');}}],getVideoTracks:()=>[{requestFrame(){calls.push('prestartFrame');if(currentRecorder?.state==='starting')currentRecorder.firstFrame();}}]};}},c:{fillRect(){}},text(){}};
 class Recorder{
  static isTypeSupported(){return true;}
  constructor(){this.state='inactive';this.events={};currentRecorder=this;}
  addEventListener(n,cb){(this.events[n]??=[]).push(cb);}
  start(){calls.push('recorderStart');this.state='starting';}
  firstFrame(){this.state='frame_received';setTimeout(()=>{if(recordingFailure){for(const cb of this.events.error||[])cb({error:Error('RECORDER_INJECTED_FAILURE')});}
   else{this.state='recording';for(const cb of this.events.start||[])cb();}},0);}
  stop(){this.state='inactive';calls.push('recorderStop');this.ondataavailable({data:new Blob(['CPU_ONLY_NOT_REAL_VIDEO'])});this.onstop();}
 }
 const win={FlyVisCompetitionUI:{stage,enterLive(){}},MediaRecorder:Recorder,addEventListener(){}};
 const fetch=async(path,options)=>{calls.push(path);return {ok:true,json:async()=>{
  if(path.endsWith('/status'))return {ready_for_camera:true,run_id:'CPU_RUN',session_id:'CPU_SESSION'};
  if(path.endsWith('/latest'))return {status:{stop_acknowledged:true},packet:null};
  if(path.endsWith('/recording'))return {path:'CPU_ONLY.webm'};return {};}};};
 vm.runInNewContext(source,{window:win,document:{getElementById:el,createElement:()=>({getContext:()=>({})}),querySelectorAll:()=>[],querySelector:el},
  fetch,MediaRecorder:Recorder,FlyVisFixedSkeleton:{load:async()=>({})},crypto:require('node:crypto').webcrypto,
  performance,Blob,console,setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame:cb=>setTimeout(cb,0)});
 await el('cpJointStart').onclick();await new Promise(r=>setTimeout(r,180));
 if(recordingFailure){assert(!calls.includes('/api/joint-camera/start'));}
 else{assert(calls.indexOf('recorderStart')<calls.indexOf('prestartFrame'));
  assert(calls.indexOf('prestartFrame')<calls.indexOf('/api/joint-camera/start'));
  assert(calls.includes('/api/joint-camera/recording'));assert(calls.includes('trackStopped'));}
 return {case:recordingFailure?'recorder_failure_blocks_capture':'recorder_before_capture_and_auto_save',status:'PASS'};
}
(async()=>{console.log(JSON.stringify(await run(false)));console.log(JSON.stringify(await run(true)));})().catch(e=>{console.error(e);process.exitCode=1;});
