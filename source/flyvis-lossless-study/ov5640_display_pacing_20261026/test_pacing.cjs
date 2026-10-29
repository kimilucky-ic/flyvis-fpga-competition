const assert=require('assert'),fs=require('fs'),path=require('path');
const P=path.resolve(__dirname,'../ov5640_live_v261_20261026/assets/ui.js');const {displayDelay,DisplayMetrics,DisplayCursor}=require(P);
assert.equal(displayDelay(10),45);assert.equal(displayDelay(54),8);assert.equal(displayDelay(300),8);
assert.equal(displayDelay(10,{paused:true}),490);assert.equal(displayDelay(10,{hidden:true}),990);assert.equal(displayDelay(10,{finished:true}),990);assert.equal(displayDelay(10,{failed:true}),990);
const m=new DisplayMetrics();m.add({session_id:'a',painted:true,paint_at_ms:100,fetch_ms:2});m.add({session_id:'a',painted:false});m.add({session_id:'a',painted:true,paint_at_ms:155,fetch_ms:4});assert.equal(m.summary().mean_interval_ms,55);assert.equal(m.summary().fetch_ms,3);assert.throws(()=>m.add({session_id:'b'}));
for(let i=0;i<5000;i++)m.add({session_id:'a',painted:false});assert.equal(m.rows.length,4096);
const c=new DisplayCursor();assert(c.commit({session_id:'a',step_id:1}));assert(c.commit({session_id:'a',step_id:8}));assert.equal(c.skipped,7);assert(!c.commit({session_id:'a',step_id:2}));assert.throws(()=>c.commit({session_id:'b',step_id:9}));
const s=fs.readFileSync(P,'utf8');assert(!s.includes('setTimeout(poll,150)'));assert(s.includes('await Promise.all([imageReady,boneReady])'));assert(s.includes('if(!paused&&!document.hidden&&currentSession===p.session_id)'));
fs.writeFileSync(path.join(__dirname,'SCHEDULER_RESULT.json'),JSON.stringify({status:'PASS_CPU_DISPLAY_PACING_AND_BOUNDS',target_cycle_ms:55,minimum_yield_ms:8,paused_ms:500,inactive_ms:1000,metrics_capacity:4096,no_duplicate_or_regressing_display:true,async_pause_guard:true,board_actions:0},null,2));console.log('PASS display scheduling, bounds, identity and duplicate guards');
