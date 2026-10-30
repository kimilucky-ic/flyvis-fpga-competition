const assert=require('assert'),fs=require('fs');const P='flyvis-lossless-study/ov5640_neuron_monitor_20261026/',ui=require(process.cwd()+'/flyvis-lossless-study/ov5640_live_v261_20261026/assets/monitor.js');
const packets=JSON.parse(fs.readFileSync(P+'packets.json','utf8')),h=new ui.History();
for(const p of packets){const x=h.add(p);assert.deepEqual(ui.values(x,0,false),p.observer.means[0]);}
assert(ui.values(ui.sample(packets[0]),0,true).every(v=>v===0));
const v=ui.values(ui.sample(packets.at(-1)),0,false);assert.equal(ui.aggregate(v,14),v.slice(6,10).reduce((a,b)=>a+b,0)/4);assert.equal(ui.aggregate(v,15),v.slice(10,14).reduce((a,b)=>a+b,0)/4);
assert(packets.some(p=>p.observer.means.flat().some(v=>v<0)));
for(const change of [p=>p.observer.step_id++,p=>p.observer.state_sha256='0'.repeat(64),p=>p.observer.means[0][0]=NaN,p=>p.observer.map_sha256='bad']){const p=structuredClone(packets[0]);change(p);assert.throws(()=>ui.sample(p));}
const p=structuredClone(packets[0]);p.observer.reference_state_sha256='1'.repeat(64);assert.throws(()=>h.add(p));p.run_id='different';h.add(p);assert.equal(h.rows.size,1);
const html=fs.readFileSync('flyvis-lossless-study/ov5640_live_v261_20261026/assets/index.html','utf8');assert(html.includes('id="detailT4" hidden'));assert(html.includes('id="detailT5" hidden'));assert(!html.includes('motionCondition'));
fs.writeFileSync(P+'JS_RESULT.json',JSON.stringify({status:'PASS_SIGNED_VALUES_REFERENCE_SUMMARY_IDENTITY_AND_HISTORY',saved_packets:packets.length,negative_values_preserved:true,subtypes_default_collapsed:true,board_actions:0},null,2));console.log('PASS observer JS values, reference, summary, malformed identity rejection and run reset');
