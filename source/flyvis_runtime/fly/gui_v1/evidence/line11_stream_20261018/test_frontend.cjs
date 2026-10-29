// CPU protocol + actual stage methods. No browser/device/decoder is launched.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const gui=path.resolve(__dirname,'../..'),viewer=path.join(gui,'../viewer');
global.window={};global.document={getElementById:()=>null};global.crypto=crypto.webcrypto;
for(const name of ['competition_full_pl.js','competition_explanation.js','competition_stage.js'])vm.runInThisContext(fs.readFileSync(path.join(viewer,name),'utf8'),{filename:name});
const digest=b=>crypto.createHash('sha256').update(b).digest('hex'),values=b=>Array.from({length:b.length/4},(_,i)=>b.readFloatLE(i*4));
(async()=>{
 const ready=JSON.parse(fs.readFileSync(path.join(gui,'evidence/line11_board_readiness_20261018/READINESS.json')));
 const input=fs.readFileSync(ready.first_step_reference.input_path),full=fs.readFileSync(ready.first_step_reference.expected_path),spatial=values(full).slice(0,5768);
 const anchor={run_id:'CPU_PROTOCOL_FIXTURE_ONLY',archive_sha256:'CPU_ARCHIVE',hardware:{boot_id:'CPU_BOOT',bit_sha256:ready.bit.sha256,hwh_sha256:ready.hwh.sha256,clock_hz:100000000}};
 const p={schema:'flyvis-full-pl-stream-display/v1',backend:'FULL_NETWORK_FPGA',run_id:anchor.run_id,session_id:'CPU_SESSION',step_id:3,state_token:4,serial:4,revision:3,
  input_time_s:.015,activity_time_s:.02,display_kind:'CURRENT_FULL_PL_STATE_PENDING_AUDIT',anchor_archive_sha256:anchor.archive_sha256,
  hardware:{...anchor.hardware,completed_steps:4,faults:0},full_state_sha256:digest(full),input_hex:values(input),input_sha256:digest(input),spatial:{values:spatial,values_sha256:digest(Buffer.from(new Float32Array(spatial).buffer)),map_sha256:'CPU_MAP'},flow:null,flow_status:'NOT_AVAILABLE_NOT_DECODED'};
 const status={first_step_accepted:true,status:'RECEIVING',result_valid:true,run_id:p.run_id,session_id:p.session_id,boot_id:p.hardware.boot_id};
 const health={projection_cache:{upstream_map_sha256:'CPU_MAP'}};
 await window.FlyVisFullPLProtocol.validateStream(p,status,anchor,health);
 for(const bad of [{...p,session_id:'OTHER'},{...p,input_time_s:0},{...p,hardware:{...p.hardware,boot_id:'OTHER'}},{...p,anchor_archive_sha256:'OTHER'}])await assert.rejects(()=>window.FlyVisFullPLProtocol.validateStream(bad,status,anchor,health));
 const source=fs.readFileSync(path.join(gui,'evidence/minimal_gpu_software32_20261018/official_flow.npy'));
 const version=source[6],header=version===1?10+source.readUInt16LE(8):12+source.readUInt32LE(8);
 const flow=values(source.subarray(header,header+1442*4)),flowBinding={run_id:p.run_id,session_id:p.session_id,frame_id:p.step_id,full_state_sha256:p.full_state_sha256,decoder:'DecoderGAVP',recursive_eval:true};
 const withFlow={...p,flow:[flow.slice(0,721),flow.slice(721)],flow_status:'OFFICIAL_DECODER_SAME_STATE',flow_sha256:digest(source.subarray(header,header+1442*4)),flow_binding:flowBinding};
 await window.FlyVisFullPLProtocol.validateStream(withFlow,status,anchor,health);
 await assert.rejects(()=>window.FlyVisFullPLProtocol.validateStream({...withFlow,flow_binding:{...flowBinding,frame_id:2}},status,anchor,health));
 const stage=Object.create(window.FlyVisCompetitionStage.prototype);stage.canvas={dataset:{}};stage.c={fillRect(){},drawImage(){}};stage.wrapped=()=>{};const texts=[];stage.text=t=>texts.push(t);stage.box=()=>{};stage.drawNeurons=()=>{};stage.drawGuide=()=>{};stage.updateGuide=()=>{};
 const receipt={color_encoding:{mode:'fixed_type_hue_absolute_activity',intensity_domain:[0,1],palette:{},encoding_sha256:'CPU_ENCODING'},type_states:[],raw_sha256:'CPU_PIXELS'};
 const meta={run_id:p.run_id,coordinates_uv:[[0,0]],input_time_s:[.015],activity_time_s:[.02],means:[[0,0,0,0,0,0,0,0]]};
 const live={backend:'FULL_NETWORK_FPGA',stream:true,step:3,sourceSequence:3,clock:{mode:'FULL_PL_STEP_DRIVEN'}};
 stage.draw(0,{},receipt,meta,{input:{},flow:{},flowValues:new Float32Array(1442).fill(NaN)},0,live);
 assert.equal(stage.canvas.dataset.displayKind,'CURRENT_FULL_PL_STATE_PENDING_AUDIT');assert.equal(stage.canvas.dataset.readoutSource,'NOT_AVAILABLE');assert(texts.includes('实体PL状态·轨迹待审计'));
 let guide=window.FlyVisMotionExplanation.guide(stage.canvas.dataset);assert.equal(guide.canSeek,false);assert.match(guide.evidence,/待审计/);assert(!guide.evidence.includes('本次实际 GPU'));
 stage.draw(0,{},receipt,meta,{input:{},flow:{},flowValues:new Float32Array(flow)},0,{...live,finished:true});
 assert.equal(stage.canvas.dataset.displayKind,'FINISHED_FULL_PL_LAST_STATE');assert.equal(stage.canvas.dataset.readoutSource,'SAME_FRAME_OFFICIAL_FLOW_CENTER');
 guide=window.FlyVisMotionExplanation.guide(stage.canvas.dataset);assert.match(guide.evidence,/已结束/);
 console.log(JSON.stringify({status:'PASS_CPU_STREAM_FRONTEND_AND_STAGE',checks:12,browser_operations:0,GPU:0,board:0,fixture:'FROZEN_REFERENCE_BYTES_ONLY_NOT_NEW_PL_RESULT'}));
})().catch(e=>{console.error(e);process.exitCode=1;});
