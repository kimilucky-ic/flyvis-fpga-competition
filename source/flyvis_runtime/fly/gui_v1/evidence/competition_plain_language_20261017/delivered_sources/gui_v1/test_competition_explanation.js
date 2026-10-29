/* CPU protocol fixtures built from the saved payload. No browser or devices. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),window={},scope={window,TextDecoder,console};
vm.createContext(scope);
for(const file of ['competition_explanation.js','competition_stage.js'])vm.runInContext(fs.readFileSync(path.join(root,'viewer',file),'utf8'),scope);
const p=JSON.parse(fs.readFileSync(path.join(root,'flyvis-3d-studio/activity_replay_20261014/interpretation_20261017/explanation.json'),'utf8'));
const meta={run_id:p.run_id,input_time_s:p.frames.map(r=>r.input_time_s)},model=new window.FlyVisMotionExplanation();model.payload=p;
function receipt(k){const row=p.frames[k];return {run_id:p.run_id,activity_sha256:p.activity_sha256,frame_index:k,activity_time_s:row.activity_time_s,type_states:row.type_states.map(s=>({type:s.type,value:s.raw_mean,delta_signed:s.delta_from_fixed_C_baseline}))};}
const cases=[];function test(name,fn){fn();cases.push({name,status:'PASS'});}
test('same k217 original center',()=>assert.equal(model.frame(217,receipt(217),meta).raw_center_bearing_deg,68.23349215027797));
for(const [name,change] of [['wrong run',r=>r.run_id='camera'],['wrong step',r=>r.frame_index=218],['wrong activity time',r=>r.activity_time_s+=.005],['wrong activity identity',r=>r.activity_sha256='wrong'],['incomplete types',r=>r.type_states=[]],['wrong signed delta',r=>r.type_states[6].delta_signed*=-1]])test(name,()=>{const r=receipt(217);change(r);assert.throws(()=>model.frame(217,r,meta));});
test('derived ROI and raw center availability stay distinct',()=>{const r=model.frame(200,receipt(200),meta);assert.equal(r.direction_comparison_available,false);assert.equal(r.raw_direction_comparison_available,true);});
function draw(k,live=null){const stage=Object.create(window.FlyVisCompetitionStage.prototype);stage.canvas={dataset:{}};stage.text=()=>{};stage.directionArrow=()=>{};const r=model.frame(k,receipt(k),meta);stage.explain(r,live,...r.raw_center_vector);return stage.canvas.dataset;}
test('grey and stopped input hide comparison',()=>{for(const k of [150,360]){const d=draw(k);assert.equal(d.inputDirection,'');assert.equal(d.directionDifference,'');assert.equal(d.directionComparisonAvailable,'false');}});
test('matching movement shows real input and estimate',()=>{const d=draw(217);assert.equal(d.inputDirection,'60');assert.equal(Number(d.directionDifference),8.233492150277982);assert.equal(d.accuracyPass,'NOT_DEFINED');});
test('camera never inherits saved ON60 GT or baseline',()=>{const d=draw(217,{sourceKind:'real_windows_camera'});assert.equal(d.explanationSha,'');assert.equal(d.inputDirection,'');assert.equal(d.directionDifference,'');assert.equal(d.explanationStatus,'LIVE_GT_NOT_AVAILABLE');});
test('missing interpretation stays unavailable',()=>{const missing=new window.FlyVisMotionExplanation();assert.equal(missing.frame(217,receipt(217),meta).status,'NOT_AVAILABLE');});
test('direction words follow actual flow in all eight directions',()=>{for(const [x,y,label] of [[1,0,'右'],[1,1,'右上'],[0,1,'上'],[-1,1,'左上'],[-1,0,'左'],[-1,-1,'左下'],[0,-1,'下'],[1,-1,'右下']])assert.equal(window.FlyVisMotionExplanation.readout(x,y).direction,label);});
test('zero and invalid flow do not invent a direction',()=>{for(const [x,y] of [[0,0],[NaN,1],[1,Infinity]])assert.equal(window.FlyVisMotionExplanation.readout(x,y).available,false);});
test('same actual k217 flow gives plain result without GT classification',()=>{const r=window.FlyVisMotionExplanation.readout(...p.frames[217].raw_center_vector);assert.equal(r.direction,'右上');assert.ok(Math.abs(r.bearing-68.23349215027797)<1e-10);});
const encoding={mode:'fixed_type_hue_baseline_response_brightness_v1',display_deadband:.005};
test('actual k217 explains T4 increase and T5 decrease',()=>{const s=window.FlyVisMotionExplanation.activityStory(receipt(217).type_states,encoding);assert.deepEqual(Array.from(s.up),['T4a','T4b','T4c']);assert.deepEqual(Array.from(s.down),['T4d','T5a','T5b','T5c','T5d']);assert.ok(s.T4.includes('a、b、c组升高'));assert.ok(s.T5.includes('四组活动都降低'));});
test('actual grey frame describes baseline instead of a recognition verdict',()=>{const s=window.FlyVisMotionExplanation.activityStory(receipt(150).type_states,encoding);assert.equal(s.near.length,8);assert.ok(s.T4.includes('接近刺激前'));assert.ok(s.T5.includes('接近刺激前'));});
test('live source cannot inherit saved delta explanation',()=>{const s=window.FlyVisMotionExplanation.activityStory(receipt(217).type_states,encoding,true);assert.equal(s.available,false);assert.equal(s.up.length+s.down.length,0);assert.ok(s.why.includes('没有刺激前基线'));});
console.log(JSON.stringify({status:'PASS_CPU_PROTOCOL_FIXTURES_NOT_NEW_NEURAL_DATA',count:cases.length,cases},null,2));
