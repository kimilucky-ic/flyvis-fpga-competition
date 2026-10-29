/* Unit protocol fixture: visibility is a CPU stub, never a browser screenshot. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const events={},panels={demo:{hidden:true},research:{hidden:true},other:{hidden:true}};
for(const p of Object.values(panels))p.getClientRects=()=>p.hidden?[]:[{}];
const document={readyState:'loading',getElementById:id=>panels[id],addEventListener:(name,fn)=>{(events[name]??=[]).push(fn);}};
const window={addEventListener:document.addEventListener},scope={document,window,Promise,console};vm.createContext(scope);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../viewer/startup.js'),'utf8'),scope);
const emit=name=>events[name]?.forEach(fn=>fn());let d=0,r=0,m=0;
window.FlyVisStartup.onPanel('demo',()=>d++);window.FlyVisStartup.onPanel('research',()=>r++);
window.FlyVisStartup.onPanel(['research','other'],()=>m++);
assert.equal(d+r+m,0);emit('DOMContentLoaded');assert.equal(d+r+m,0);
panels.research.hidden=false;emit('flyvis-workspace');assert.equal(d,0);assert.equal(r,1);assert.equal(m,1);
emit('flyvis-workspace');emit('toggle');assert.equal(r,1);assert.equal(m,1);
panels.demo.hidden=false;emit('flyvis-workspace');assert.equal(d,1);
console.log(JSON.stringify({status:'PASS_CPU_PANEL_LAZY_PROTOCOL',cases:['no_fetch_before_ready','hidden_panels_not_started','selected_panel_started','other_panels_remain_idle','reopen_no_duplicate','multiple_panel_aliases_once']}));
