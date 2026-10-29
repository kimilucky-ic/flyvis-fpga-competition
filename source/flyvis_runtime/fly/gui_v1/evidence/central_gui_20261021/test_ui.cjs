const fs=require('fs'),assert=require('assert'),vm=require('vm');
const b='C:/Users/hzy72/Documents/ChatGPT/fly',e=b+'/gui_v1/evidence/central_gui_20261021';
const packets=JSON.parse(fs.readFileSync(e+'/fixture.json'));
const ctx={window:{},document:{getElementById(){return null}}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(b+'/viewer/competition_full_pl.js','utf8'),ctx);
const {drawGroups,groupSample}=ctx.window.FlyVisFullPLGroups;
const texts=[];const c={save(){},restore(){},fillRect(x,y,w,h){assert(x>=1372&&x+w<=1900&&y>=20&&y+h<=1060)},beginPath(){},moveTo(x,y){assert(Number.isFinite(x)&&Number.isFinite(y))},lineTo(x,y){assert(Number.isFinite(x)&&Number.isFinite(y))},stroke(){},arc(){},fill(){}};
const stage={c,canvas:{dataset:{}},text(t){texts.push(t)}},history={run:null,samples:new Map()};
for(const p of packets){const anchor=packets.find(a=>a.run_id===p.run_id);const s=groupSample(p);assert.deepEqual(Array.from(s.raw),p.expected);assert.deepEqual(Array.from(s.values),p.expected.map(v=>Math.max(0,v)));drawGroups(stage,p,anchor,history);assert.deepEqual(JSON.parse(stage.canvas.dataset.centralRaw),p.expected);assert.equal(stage.canvas.dataset.groupCurveScale,'FIXED_RECTIFIED_0_3');}
const p=packets[11];drawGroups(stage,p,p,history);assert.equal(stage.canvas.dataset.groupCurveSamples,'1');
drawGroups(stage,{...p,run_id:'new-run'},p,history);assert.equal(history.samples.size,1);
assert.throws(()=>groupSample({...p,spatial:{...p.spatial,map_sha256:'wrong'}}),/CENTRAL_MAP/);
assert.throws(()=>groupSample({...p,spatial:{...p.spatial,values:[]}}),/CENTRAL_ARRAY/);
const bad=JSON.parse(JSON.stringify(p));bad.spatial.values[360]=NaN;assert.throws(()=>groupSample(bad),/CENTRAL_VALUES/);
assert(texts.some(t=>t.includes('不再取721均值')));assert(texts.some(t=>t.includes('非本次DSI')));
const before=fs.readFileSync(e+'/competition_full_pl.js.before','utf8'),after=fs.readFileSync(b+'/viewer/competition_full_pl.js','utf8');assert.equal(before.slice(before.indexOf(' async function validate'),before.indexOf(' // Display samples')),after.slice(after.indexOf(' async function validate'),after.indexOf(' // Central u=')));
fs.writeFileSync(e+'/RESULT.json',JSON.stringify({status:'PASS_CPU_SAVED_DATA_UI_CHECK',verified_saved_central_rows:970,actual_full_spatial_packets:22,central_global_ids:JSON.parse(stage.canvas.dataset.centralGlobalIds),right_panel_bounds:true,signed_values_and_rectified_curves:true,run_and_seek_isolation:true,wrong_map_shape_nan_rejected:true,protocol_validators_unchanged:true,browser_visual_acceptance:'NOT_RUN',gpu_board_inference:'NOT_RUN'},null,2));console.log('PASS central extraction, raw/rectified values, right bounds, seek/run isolation, negative cases; validators unchanged');
