/* CPU saved-array protocol tests only; no GUI, camera, CUDA or board. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const ctx={window:{},document:{getElementById:()=>null},crypto:require('crypto').webcrypto,
 Uint8Array,Float32Array,Blob,atob:s=>Buffer.from(s,'base64').toString('binary')};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../viewer/competition_joint.js'),'utf8'),ctx);
const validate=ctx.window.FlyVisJointCameraProtocol.validate;
const p=JSON.parse(fs.readFileSync(path.join(__dirname,'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json'),'utf8'));
Object.assign(p,{runtime_policy:'MINIMAL_COMPUTE_ASYNC_V1',live_response_hz:5,
 display_kind:'LIVE_LOW_RATE_LATEST_COMMITTED_STATE',evidence_level:'ACK_MATCHED_RAM_ONLY_ASYNC_RECORDING'});
Object.assign(p.transaction,{integer_error:null,numerical_check:'DEFERRED_OFFLINE'});p.durable={barrier:'NOT_SYNCHRONOUS'};
const identity=Object.fromEntries(['run_id','session_id','model','mapping_sha256','hardware','runtime_policy','live_response_hz'].map(k=>[k,p[k]]));
(async()=>{await validate(p,identity,p.spatial.map_sha256);let checks=1;
 for(const edit of [q=>q.run_id='0'.repeat(32),q=>q.live_response_hz=20,q=>q.display_kind='LIVE_REALTIME',q=>q.REALTIME_STREAM_PASS='PASS']){
  const bad=JSON.parse(JSON.stringify(p));edit(bad);await assert.rejects(()=>validate(bad,identity,bad.spatial.map_sha256));checks++;
 }console.log(JSON.stringify({status:'PASS',checks,evidence:'CPU_SAVED_ARRAYS_PROTOCOL_ONLY',GPU:0,camera:0,board:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
