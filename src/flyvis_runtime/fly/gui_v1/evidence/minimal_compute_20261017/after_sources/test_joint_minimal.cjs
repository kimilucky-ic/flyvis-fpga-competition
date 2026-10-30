/* CPU-only protocol consumer checks using saved real arrays; no browser/device. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const here=__dirname,source=fs.readFileSync(path.join(here,'../viewer/competition_joint.js'),'utf8');
const ctx={window:{},document:{getElementById:()=>null},crypto:require('crypto').webcrypto,
 Uint8Array,Float32Array,Blob,atob:s=>Buffer.from(s,'base64').toString('binary')};
vm.runInNewContext(source,ctx);
const validate=ctx.window.FlyVisJointCameraProtocol.validate;
const original=JSON.parse(fs.readFileSync(path.join(here,'runtime/joint/f2fd7b4d54a4445daa8a15065c60088e/final_snapshot.json'),'utf8'));
const copy=v=>JSON.parse(JSON.stringify(v));
const identity=p=>Object.fromEntries(['run_id','session_id','model','mapping_sha256','hardware','runtime_policy'].map(k=>[k,p[k]]));
(async()=>{
 let checks=0;
 await validate(original,identity(original),original.spatial.map_sha256);checks++;
 const p=copy(original);p.runtime_policy='MINIMAL_COMPUTE_ASYNC_V1';p.evidence_level='ACK_MATCHED_RAM_ONLY_ASYNC_RECORDING';
 p.display_kind='POST_COMPUTE_SAME_RUN_NOT_REALTIME';p.transaction.integer_error=null;p.transaction.numerical_check='DEFERRED_OFFLINE';
 p.durable={barrier:'NOT_SYNCHRONOUS',recording:{complete:true}};
 await validate(p,identity(p),p.spatial.map_sha256);checks++;
 for(const change of [q=>q.evidence_level='ACK_MATCHED_DURABLE_PENDING_PS_AUDIT',q=>q.durable.barrier='STEP_PUBLISHED',
     q=>q.transaction.integer_error=0,q=>q.display_kind='LIVE_REALTIME']){
  const bad=copy(p);change(bad);await assert.rejects(()=>validate(bad,identity(bad),bad.spatial.map_sha256));checks++;
 }
 const oldIdentity=identity(original);await assert.rejects(()=>validate(p,oldIdentity,p.spatial.map_sha256));checks++;
 console.log(JSON.stringify({status:'PASS',checks,evidence:'CPU_SAVED_ARRAYS_PROTOCOL_ONLY',GPU:0,camera:0,board:0,browser:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
