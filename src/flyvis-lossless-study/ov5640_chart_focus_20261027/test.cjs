const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const O=__dirname,R=path.join(O,'../ov5640_live_v261_20261026');
const panel={dataset:{}};const els={};const ctx=new Proxy({fillText(){},clearRect(){}},{get:(t,k)=>k in t?t[k]:()=>{}});
for(const id of ['observerRoi','observerReference','groupScale','groups','motionSummary','detailT4','detailT5','chartT4','chartT5','expandT4','expandT5','observerCaption','roiOverlay','earlyCharts','emptyGroups','collapseGroups',...['L1','L2','Mi1','Tm3','Tm1','Tm2'].map(n=>'curve'+n)])els[id]={dataset:{},hidden:id.startsWith('detail'),clientWidth:1000,clientHeight:500,value:id==='observerRoi'?'0':id==='groupScale'?'auto':'raw',attrs:{},setAttribute(k,v){this.attrs[k]=v},getContext(){return ctx},closest(){return panel}};
const env={document:{getElementById:id=>els[id]},window:{addEventListener(){}},module:{exports:{}}};vm.runInNewContext(fs.readFileSync(path.join(R,'assets/monitor.js'),'utf8'),env);const api=env.module.exports;
const oldEnv={module:{exports:{}}};vm.runInNewContext(fs.readFileSync(path.join(O,'before/assets/monitor.js'),'utf8'),oldEnv);
const map=JSON.parse(fs.readFileSync(path.join(R,'assets/monitor.json'))),ui=api.start(map);
const packets=JSON.parse(fs.readFileSync(path.join(O,'../ov5640_neuron_monitor_20261026/packets.json')));
for(const p of packets){assert.equal(JSON.stringify(api.sample(p)),JSON.stringify(oldEnv.module.exports.sample(p)));ui.add(p)}
const snapshot=JSON.stringify([...ui.history.rows]);
for(const n of ['L1','L2','Mi1','Tm3','Tm2'])els['curve'+n].onclick();
assert.equal(els.groups.dataset.visibleTypes,'["Tm1"]');assert.equal(els.earlyCharts.hidden,false);
els.collapseGroups.onclick();assert(els.earlyCharts.hidden);els.collapseGroups.onclick();assert(!els.earlyCharts.hidden);
els.curveTm1.onclick();assert(els.earlyCharts.hidden&&!els.emptyGroups.hidden);els.curveMi1.onclick();assert(!els.earlyCharts.hidden);
assert.equal(JSON.stringify([...ui.history.rows]),snapshot);
for(const p of packets)for(let r=0;r<5;r++)for(const rel of [false,true])assert.equal(JSON.stringify(api.values(api.sample(p),r,rel)),JSON.stringify(oldEnv.module.exports.values(oldEnv.module.exports.sample(p),r,rel)));
els.expandT4.onclick();assert(!els.detailT4.hidden);els.observerRoi.value='1';els.observerReference.value='first';els.observerRoi.onchange();assert.equal(els.groups.dataset.roi,'1');assert.equal(els.groups.dataset.relative,'true');
const bad=JSON.parse(JSON.stringify(packets[0]));bad.observer.state_sha256='bad';assert.throws(()=>ui.add(bad));
fs.writeFileSync(path.join(O,'CPU_RESULT.json'),JSON.stringify({status:'PASS_DISPLAY_ONLY',saved_packets:packets.length,selection:'six/single/zero/restore',collapse_restore:true,history_unchanged:true,all_roi_reference_values_equal_previous:true,bad_identity_rejected:true,board_actions:0},null,2));console.log('PASS_DISPLAY_ONLY');
