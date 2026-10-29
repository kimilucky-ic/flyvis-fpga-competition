// CPU-only VM/DOM/HTTP substitutes. No browser, listener or device is started.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(require('path').join(__dirname,'../../..','viewer/competition_full_pl.js'),'utf8');
const settle=()=>new Promise(r=>setImmediate(r));
(async()=>{
 for(const terminal of ['FAILED','STOPPED']){
  let timer,cleared=0,statusPolls=0;const before=[];
  const el=()=>({children:[],append(...x){this.children.push(...x)},remove(){this.removed=true}});
  const context={Uint8Array,Float32Array,Number,Array,Math,Error,JSON,Promise,performance:{now:()=>0},
   document:{getElementById:()=>({}),createElement:el},
   window:{FlyVisCompetitionUI:{stage:{host:{before:p=>before.push(p)}}}},
   setInterval:fn=>(timer=fn,1),clearInterval:()=>cleared++,setTimeout,
   fetch:async path=>({ok:true,json:async()=>path==='/api/full-pl/status'?{configured:true,status:'WAITING_FIRST_STEP'}:
    (++statusPolls===1?{configured:true,status:'WAITING_FIRST_STEP',first_step_accepted:false}:{configured:true,status:terminal,error:'CPU injected failure'})})};
  vm.runInNewContext(source,context);await settle();
  assert.equal(before.length,1);const panel=before[0];
  assert.equal(panel.children[0].disabled,true);assert.equal(panel.children[1].disabled,true);
  assert.equal(panel.children[4].href,'/api/full-pl-stream/link.zip');
  assert.match(panel.children[3].textContent,/等待人工板端准备/);
  await timer();assert.equal(cleared,1);assert.match(panel.children[3].textContent,/已停止/);
 }
 {
  let timer,savedReads=0,streamReads=0,watchStarts=0;const before=[];
  const el=()=>({children:[],append(...x){this.children.push(...x)},remove(){this.removed=true},
   set onclick(fn){this.handler=fn},get onclick(){return (...args)=>{
    if(this.textContent==='接收并显示连续状态'){watchStarts++;return Promise.resolve();}
    return this.handler(...args);
   }}});
  const context={Uint8Array,Float32Array,Number,Array,Math,Error,JSON,Promise,performance:{now:()=>0},
   document:{getElementById:()=>({}),createElement:el},window:{FlyVisCompetitionUI:{stage:{host:{before:p=>before.push(p)}}}},
   setInterval:fn=>(timer=fn,1),clearInterval:()=>{},setTimeout,
   fetch:async path=>({ok:true,json:async()=>path==='/api/full-pl/status'?
    {configured:true,status:++savedReads===1?'WAITING_FIRST_STEP':'VERIFIED_SAVED_FIRST_STEP'}:
    {configured:true,status:++streamReads===1?'WAITING_FIRST_STEP':'READY_WAITING_PRODUCER',first_step_accepted:streamReads>1}})};
  vm.runInNewContext(source,context);await settle();await timer();await settle();
  assert.equal(before.length,2);assert.equal(before[0].removed,true);assert.equal(watchStarts,1);
 }
 console.log('PASS 3 CPU UI waiting/failure/accepted-auto-watch cases; no browser/device/server');
})().catch(e=>{console.error(e);process.exitCode=1});
