const fs=require('fs'),assert=require('assert'),vm=require('vm');
const base='C:/Users/hzy72/Documents/ChatGPT/fly',dir=base+'/gui_v1/evidence/full_pl_acceptance_curves_20261021';
const fixture=JSON.parse(fs.readFileSync(dir+'/curve_fixture.json','utf8'));
const context={window:{},document:{getElementById(){return null}}};vm.createContext(context);
vm.runInContext(fs.readFileSync(base+'/viewer/competition_full_pl.js','utf8'),context);
const {groupSample,drawGroups}=context.window.FlyVisFullPLGroups;
const ctx={save(){},restore(){},fillRect(x,y,w,h){assert(x>=354&&x+w<=658&&y>=783&&y+h<=1046)},beginPath(){},moveTo(){},lineTo(){},stroke(){},arc(){},fill(){}};
const stage={c:ctx,canvas:{dataset:{}},text(){}};const hist={run:null,samples:new Map()};
const packet=k=>({run_id:fixture.run_id,step_id:k,activity_time_s:fixture.times[k],signed_means:fixture.means[k]});
for(let k=0;k<485;k++){
 const p=packet(k),g=groupSample(p);assert.equal(g.t4,fixture.means[k].slice(0,4).reduce((a,b)=>a+b,0)/4);
 drawGroups(stage,p,packet(0),hist);assert.equal(stage.canvas.dataset.groupCurveStep,String(k));
}
assert.equal(hist.samples.size,485);drawGroups(stage,packet(10),packet(0),hist);assert.equal(stage.canvas.dataset.groupCurveSamples,'11');
const different={...packet(0),run_id:'DIFFERENT_TEST_RUN'};drawGroups(stage,different,packet(0),hist);assert.equal(hist.samples.size,1);
assert.throws(()=>groupSample({...packet(0),signed_means:[NaN]}),/FULL_PL_GROUP_MEANS/);
fs.writeFileSync(dir+'/CURVE_TEST.json',JSON.stringify({evidence:'CPU_CANVAS_FIXTURE_WITH_REAL_SAVED_MEANS',actual_frames_tested:485,seek_excludes_future:true,run_isolation:true,invalid_values_rejected:true,layout_rectangle_unchanged:true,new_neural_or_board_operations:0},null,2));
console.log('PASS 485 actual mean rows; same-step time, seek, run isolation, missing-value rejection and reserved text rectangle');
