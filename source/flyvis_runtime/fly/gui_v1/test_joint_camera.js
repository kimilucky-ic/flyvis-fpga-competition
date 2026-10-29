/* Node CPU software checks. No browser, GPU, service, or camera is launched. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
global.window={};global.crypto=require('node:crypto').webcrypto;global.document={getElementById:()=>null};
vm.runInThisContext(fs.readFileSync('viewer/fixed_skeleton.js','utf8'));
vm.runInThisContext(fs.readFileSync('viewer/competition_joint.js','utf8'));
vm.runInThisContext(fs.readFileSync('viewer/competition_stage.js','utf8'));
const folder=process.argv[2],load=n=>JSON.parse(fs.readFileSync(path.join(folder,n),'utf8'));
(async()=>{
 const health=load('health.json'),b=fs.readFileSync(path.join(folder,'projection.cache')),buffer=b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),packets=load('packets.json'),expected=load('expected.json');
 const geometry=await window.FlyVisFixedSkeleton.decode(buffer,health),texts=[];
 for(let i=0;i<packets.length;i++){
  const out=await geometry.render(packets[i],'cpu-node-fixture');
  assert.equal(out.receipt.raw_sha256,expected[i].raw_sha256,'exact original cached CPU pixels');
  assert.equal(out.receipt.types.length,8);
  for(let t=0;t<8;t++)assert.ok(Math.abs(out.receipt.means[t]-expected[i].means[t])<1e-12);
 }
 // LIVE-looking metadata below is an isolated validator fixture. NEVER sent to
 // server, saved as a run, or admitted as actual camera/PL execution evidence.
 const p=structuredClone(packets[1]);
 await assert.rejects(window.FlyVisJointCameraProtocol.validate(p,p,p.spatial.map_sha256),/NOT_NEW_CAMERA/);
 p.execution_kind='LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT';p.source_kind=p.source.source_kind='real_windows_camera';
 p.actual_new_computation=true;p.evidence_level='ACK_MATCHED_DURABLE_PENDING_PS_AUDIT';
 await window.FlyVisJointCameraProtocol.validate(p,p,p.spatial.map_sha256);
 for(const mutate of [q=>q.flow[0][0]+=1,q=>q.whole_run_acceptance='PASS',q=>q.durable.barrier='COMMIT_INTENT',q=>q.hardware.ASID='wrong',q=>q.source.run_id='wrong']){
  const bad=structuredClone(p);mutate(bad);
  await assert.rejects(window.FlyVisJointCameraProtocol.validate(bad,p,p.spatial.map_sha256));
 }
 const context=new Proxy({},{get:(o,k)=>o[k]??(()=>{})}),stage={c:context,canvas:{dataset:{}},text:v=>texts.push(v),box:()=>{}};
 const r=await geometry.render(p,'cpu-stage-fixture'),uv=load('coordinates.json');
 window.FlyVisCompetitionStage.prototype.draw.call(stage,0,{width:r.width,height:r.height},r.receipt,
  {run_id:p.run_id,types:r.receipt.types,means:[r.receipt.means],coordinates_uv:uv,activity_time_s:[p.activity_time_s]},
  {input:{},flow:{},flowValues:p.flow.flat()},12,{joint:p.transaction,sourceKind:p.source_kind,step:p.step_id,sourceSequence:p.source.sequence,clock:{mode:'COMMIT_DRIVEN'},wallElapsed:0});
 assert.equal(stage.canvas.dataset.displayKind,'LIVE_CAMERA_GPU_FPGA_PENDING_AUDIT');
 assert.ok(texts.some(t=>t.includes('整轮待终验')));assert.ok(texts.some(t=>t.includes('PL 5768')));
 assert.ok(!texts.some(t=>t.includes('FPGA 未连接')));
 const report={status:'PASS_CPU_JS_JOINT_CONSUMER_AND_EXACT_PIXELS',saved_frames:4,means_checked:32,corruption_rejections:6,
  eight_types_visible:true,joint_stage_labels_checked:true,new_neural_updates:0,browser_acceptance:'NOT_RUN',GPU_or_camera_or_board_operations:0};
 fs.writeFileSync(path.join(folder,'js_result.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
