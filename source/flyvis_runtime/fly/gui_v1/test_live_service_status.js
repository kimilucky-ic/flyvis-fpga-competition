const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context={window:{}};vm.runInNewContext(fs.readFileSync('viewer/live_service_status.js','utf8'),context);
const describe=context.window.FlyVisServiceStatus;
assert.equal(describe({status:'CONNECTED'}).ready,true);
for(const state of ['FAILED','STOPPED','DISCONNECTED','NOT_STARTED']){
 const r=describe({status:'NOT_CONNECTED',service:{state,terminal:true,message:state}});
 assert.equal(r.ready,false);assert.equal(r.terminal,true);assert.equal(r.state,state);
}
assert.equal(describe({status:'NOT_CONNECTED',service:{state:'PRELOADING',terminal:false}}).terminal,false);
assert.equal(describe({status:'NOT_CONNECTED',error:'old server'}).terminal,true);
console.log('PASS: 7 service display cases; no browser/device launch');
