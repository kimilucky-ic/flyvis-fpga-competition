const fs=require('fs'),assert=require('assert'),vm=require('vm');
const b='C:/Users/hzy72/Documents/ChatGPT/fly',e=b+'/gui_v1/evidence/subtype_right_20261021';
const f=JSON.parse(fs.readFileSync(b+'/gui_v1/evidence/full_pl_acceptance_curves_20261021/curve_fixture.json'));
const ctx={window:{},document:{getElementById(){return null}}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(b+'/viewer/competition_full_pl.js','utf8'),ctx);
const {drawGroups,groupSample}=ctx.window.FlyVisFullPLGroups;
const c={save(){},restore(){},fillRect(x,y,w,h){assert(x>=1372&&x+w<=1900&&y>=20&&y+h<=1060)},beginPath(){},moveTo(){},lineTo(){},stroke(){},arc(){},fill(){}};
const stage={c,canvas:{dataset:{}},text(){}};const history={run:null,samples:new Map()},packet=k=>({run_id:f.run_id,step_id:k,activity_time_s:f.times[k],signed_means:f.means[k]});
for(let k=0;k<485;k++){drawGroups(stage,packet(k),packet(0),history);assert.deepEqual(JSON.parse(stage.canvas.dataset.subtypeMeans),f.means[k]);}
drawGroups(stage,packet(10),packet(0),history);assert.equal(stage.canvas.dataset.groupCurveSamples,'11');drawGroups(stage,{...packet(0),run_id:'test'},packet(0),history);assert.equal(history.samples.size,1);assert.throws(()=>groupSample({...packet(0),signed_means:[NaN]}));
const js=fs.readFileSync(b+'/viewer/operator_selection.js','utf8');const match=js.match(/if\((r.ok&&v.owner\?\.root_id.*?)\)\{/);assert(match);const ready=new Function('r','v','ownerId','selection','return '+match[1]);const selection={backend:'FULL_FPGA',input:'scientific28',condition:'EDGE_ON_RIGHT'};
assert(!ready({ok:true},{owner:{root_id:'old'},selection},'old',selection));assert(!ready({ok:true},{owner:{root_id:'new',closing:true},selection},'old',selection));assert(ready({ok:true},{owner:{root_id:'new',closing:false},selection},'old',selection));assert(!ready({ok:true},{owner:{root_id:'new'},selection:{...selection,condition:'OTHER'}},'old',selection));
fs.writeFileSync(e+'/JS_TEST.json',JSON.stringify({actual_rows:485,right_panel_only:true,eight_signed_subtypes:true,seek_run_isolation:true,same_condition_old_backend_rejected:true,closing_backend_rejected:true,new_matching_owner_accepted:true,evidence:'CPU_JS_FIXTURE_NO_BROWSER'},null,2));console.log('PASS 485 subtype rows; right panel bounds, run/seek, new-backend transition');
