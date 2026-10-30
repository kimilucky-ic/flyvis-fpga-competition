/* Scientific labels are derived from saved same-frame fixtures, no new inference. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'../../..'),window={};
const scope=vm.createContext({window,TextDecoder,console});
for(const file of ['competition_explanation.js','competition_stage.js'])vm.runInContext(fs.readFileSync(path.join(root,'viewer',file),'utf8'),scope);
const p=JSON.parse(fs.readFileSync(path.join(root,'flyvis-3d-studio/activity_replay_20261014/interpretation_20261017/explanation.json'),'utf8'));
const model=new window.FlyVisMotionExplanation();model.payload=p;
const meta={run_id:p.run_id,input_time_s:p.frames.map(r=>r.input_time_s)};
function data(k,live=false){
 const row=p.frames[k],states=row.type_states.map(s=>({type:s.type,value:s.raw_mean,delta_signed:s.delta_from_fixed_C_baseline}));
 const receipt={run_id:p.run_id,activity_sha256:p.activity_sha256,frame_index:k,activity_time_s:row.activity_time_s,type_states:states};
 const stage=Object.create(window.FlyVisCompetitionStage.prototype);stage.canvas={dataset:{}};stage.text=()=>{};stage.directionArrow=()=>{};
 stage.explain(model.frame(k,receipt,meta),live?{sourceKind:'real_windows_camera'}:null,...row.raw_center_vector);
 const story=window.FlyVisMotionExplanation.activityStory(states,{mode:'fixed_type_hue_baseline_response_brightness_v1',display_deadband:.005},live);
 return Object.assign(stage.canvas.dataset,{run:live?'CPU_FIXTURE_NEW_RUN':p.run_id,frame:String(k),inputTime:live?'':String(row.input_time_s),activityTime:String(row.activity_time_s),displayKind:live?'LIVE_CAMERA_GPU':'OFFLINE_REPLAY',sourceKind:live?'real_windows_camera':'recorded_experiment',activityStoryT4:story.T4,activityStoryT5:story.T5,activityStoryAvailable:String(story.available)});
}
const guide=window.FlyVisMotionExplanation.guide,cases=[];
function test(name,fn){fn();cases.push({name,status:'PASS'});}
test('same-run k217 guide preserves real direction and signed responses',()=>{const g=guide(data(217));assert.equal(g.run,p.run_id);assert.equal(g.step,217);assert.equal(g.inputTime,p.frames[217].input_time_s);assert.equal(g.activityTime,p.frames[217].activity_time_s);assert.equal(g.title,'朝右上运动');assert.ok(g.detail.includes('68.2'));assert.ok(g.comparison.includes('8.2'));assert.ok(g.T4.includes('a、b、c组升高'));assert.ok(g.T5.includes('都降低'));assert.ok(g.why.includes('变亮也可能是活动降低'));});
test('pre-stimulus guide describes adaptation rather than recognition',()=>{const g=guide(data(150));assert.equal(g.title,'等待运动输入');assert.ok(g.input.includes('运动还没开始'));assert.equal(g.comparison,'');});
test('held-frame guide does not keep moving-input GT',()=>{const g=guide(data(360));assert.ok(g.input.includes('边缘已停止'));assert.equal(g.comparison,'');assert.ok(g.detail.includes('运动停止后的响应'));});
test('live fixture never inherits saved input GT or baseline',()=>{const g=guide(data(217,true));assert.equal(g.run,'CPU_FIXTURE_NEW_RUN');assert.equal(g.canSeek,false);assert.equal(g.inputTime,null);assert.ok(g.input.includes('运动方向未标注'));assert.equal(g.comparison,'');assert.ok(g.why.includes('不判断升高或降低'));assert.ok(!g.T4.includes('a、b、c组升高'));});
test('failed or stopped display cannot expose a valid explanation',()=>{for(const state of ['NOT_AVAILABLE','STOPPED_LAST_ACTUAL_FRAME','STOPPED_PENDING_JOINT_AUDIT'])assert.equal(guide({...data(217),displayKind:state}).available,false);});
test('missing flow identity cannot retain direction verdict',()=>{assert.equal(guide({...data(217),readoutSource:''}).title,'本步方向暂不可用');});
test('invalid run step or activity time stays unavailable',()=>{for(const change of [{run:''},{frame:'-1'},{activityTime:''},{activityTime:'NaN'},{inputTime:'Infinity'}])assert.equal(guide({...data(217),...change}).available,false);});
test('revocation closes the guide and removes current scientific interpretation',()=>{const stage=Object.create(window.FlyVisCompetitionStage.prototype);let closed=0;stage.canvas={dataset:{}};stage.guide={available:true};stage.guideButton={disabled:false};stage.guideDialog={open:true,close(){closed++;}};stage.clearGuide();assert.equal(stage.guide,null);assert.equal(stage.guideButton.disabled,true);assert.equal(stage.canvas.dataset.guideStatus,'NOT_AVAILABLE');assert.equal(closed,1);});
console.log(JSON.stringify({status:'PASS_CPU_SAVED_RESULT_GUIDE_CONTRACT',count:cases.length,cases},null,2));
