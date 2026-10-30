const fs=require('fs'),path=require('path'),assert=require('assert');
const base='C:/Users/hzy72/Documents/ChatGPT/fly';
const dir=base+'/gui_v1/evidence/full_pl_null_label_20261021';
function code(file){const s=fs.readFileSync(file,'utf8');const start=s.indexOf("   root.querySelector('.cp-heading').textContent=");const end=s.indexOf('\n  async function drawReplay',start);return s.slice(start,end).replace(/\n  }\s*$/,'');}
function run(file,kind){
 const fields={cpStatus:{textContent:''},cpFullPLIdentity:{textContent:''}};
 const label={textContent:''},heading={textContent:''},state={textContent:''};
 const p={source:{kind},hardware:{boot_id:'CPU_FIXTURE'},plan_metadata:{steps:485},condition_id:'CPU_FIXTURE',step_id:484,input_time_s:2.42,activity_time_s:2.425,wall_elapsed_s:33.8,capture_elapsed_s:2.42,flow:[],run_id:'CPU_FIXTURE'};
 const f=new Function('p','status','root','$','sourceLabel','state','panel','liveStream','elapsed',code(file));
 assert(f(p,{status:'FINISHED',received_steps:485,browser_receipts:0},{querySelector:()=>heading},id=>fields[id]||null,label,state,{querySelector:()=>({})},true,.038));
 assert(fields.cpStatus.textContent.includes('485'));return label.textContent;
}
assert.throws(()=>run(dir+'/competition_full_pl.before.js','controlled_animation'),/Cannot set properties of null/);
const outputs=['controlled_animation','real_windows_camera'].map(k=>run(base+'/viewer/competition_full_pl.js',k));
fs.writeFileSync(dir+'/RESULT.json',JSON.stringify({evidence:'CPU_DOM_FIXTURE_NOT_BROWSER',original_bug_reproduced:true,fixed_branches:outputs.length,outputs,board_operations:0,new_neural_runs:0},null,2));
console.log('PASS: original null crash reproduced; fixed animation and camera labels execute without legacy GPU element');
