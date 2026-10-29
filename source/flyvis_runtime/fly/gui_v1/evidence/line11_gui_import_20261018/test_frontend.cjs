// CPU-only source/packet/stage checks. No browser, neural computation or PL.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),viewer=path.join(root,'../viewer');
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
global.window={};global.document={getElementById:()=>null};global.crypto=crypto.webcrypto;
for(const name of ['competition_full_pl.js','competition_explanation.js','competition_stage.js','fixed_skeleton.js'])vm.runInThisContext(fs.readFileSync(path.join(viewer,name),'utf8'),{filename:name});
(async()=>{
 const ready=JSON.parse(fs.readFileSync(path.join(root,'evidence/line11_board_readiness_20261018/READINESS.json')));
 const input=fs.readFileSync(ready.first_step_reference.input_path),full=fs.readFileSync(ready.first_step_reference.expected_path);
 // Existing frozen arrays are used only as CPU protocol test bytes.
 const vals=b=>Array.from({length:b.length/4},(_,i)=>b.readFloatLE(i*4));
 const spatial=vals(full).slice(0,5768),run='CPU_PROTOCOL_FIXTURE_ONLY',archive='0'.repeat(64);
 const p={schema:'flyvis-full-pl-first-step-display/v1',run_id:run,archive_sha256:archive,backend:'FULL_NETWORK_FPGA',display_kind:'OFFLINE_REPLAY_FULL_NETWORK_FPGA',board_connection:'NOT_CONNECTED',step_id:0,state_token:1,input_time_s:0,activity_time_s:.005,hardware:{boot_id:'CPU_FIXTURE_BOOT',completed_steps:1,faults:0},flow:null,flow_status:'NOT_AVAILABLE_NOT_DECODED',input_hex:vals(input),input_sha256:digest(input),spatial:{values:spatial,values_sha256:digest(Buffer.from(new Float32Array(spatial).buffer)),map_sha256:'CPU_FIXTURE_MAP'}};
 const s={status:'VERIFIED_SAVED_FIRST_STEP',run_id:run,boot_id:'CPU_FIXTURE_BOOT',archive_sha256:archive};const h={projection_cache:{upstream_map_sha256:'CPU_FIXTURE_MAP'}};
 await window.FlyVisFullPLProtocol.validate(p,s,h);
 await assert.rejects(()=>window.FlyVisFullPLProtocol.validate({...p,run_id:'OTHER_RUN'},s,h));
 await assert.rejects(()=>window.FlyVisFullPLProtocol.validate({...p,flow:[[0],[0]]},s,h));
 const stage=Object.create(window.FlyVisCompetitionStage.prototype);stage.canvas={dataset:{}};stage.c={fillRect(){},drawImage(){}};stage.wrapped=()=>{};const texts=[];stage.text=t=>texts.push(t);stage.box=()=>{};stage.drawNeurons=()=>{};stage.drawGuide=()=>{};stage.updateGuide=()=>{};
 const encoding={mode:'fixed_type_hue_absolute_activity',intensity_domain:[0,1],palette:{},encoding_sha256:'CPU_ENCODING'};
 const receipt={color_encoding:encoding,type_states:[],raw_sha256:'CPU_PIXELS'};
 const meta={run_id:run,coordinates_uv:[[0,0]],input_time_s:[0],activity_time_s:[.005],means:[[0,0,0,0,0,0,0,0]]};
 stage.draw(0,{},receipt,meta,{input:{},flow:{},flowValues:new Float32Array(1442).fill(NaN)},0,{backend:'FULL_NETWORK_FPGA',sourceKind:'line11_fixed_frame0',step:0,sourceSequence:0,wallElapsed:.3,clock:{mode:'SAVED_RESULT'}});
 assert.equal(stage.canvas.dataset.displayKind,'OFFLINE_REPLAY_FULL_NETWORK_FPGA');assert(texts.includes('实体PL结果·离线回放'));assert(!texts.includes('本次 GPU 计算'));
 const guide=window.FlyVisMotionExplanation.guide(stage.canvas.dataset);assert.equal(guide.canSeek,false);assert.match(guide.evidence,/实体PL首步/);assert.match(guide.input,/不是ON60/);assert.equal(stage.canvas.dataset.readoutSource,'NOT_AVAILABLE');
 console.log(JSON.stringify({status:'PASS_CPU_FRONTEND_PROTOCOL_AND_STAGE',checks:['frozen_bytes_packet','cross_run_rejected','borrowed_flow_rejected','full_PL_label','no_GPU_or_live_claim','no_ON60_or_485_seek','missing_flow_unavailable'],browser_operations:0,GPU:0,board:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
