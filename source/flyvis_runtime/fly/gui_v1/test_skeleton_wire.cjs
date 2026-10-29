// Pure CPU protocol fixture. Actual saved neural values; no fresh GPU execution.
const fs=require('fs'),assert=require('assert');global.window={};
require('../viewer/skeleton_wire.js');
const f=JSON.parse(fs.readFileSync(0,'utf8'));
assert.equal(f.scope,'CPU_TRANSPORT_FIXTURE_ONLY');
const r=f.receipt,p=f.packet,h=f.health;
// Exercise the production schema gate in memory, never publish this fixture.
r.source_evidence_level='ACTUAL_CONTINUOUS_FULL_GPU_STATE';
r.serial=p.serial;r.verified_by='CPU_TEST_ONLY';
function wire(receipt,pixels=f.pixels){const header=Buffer.from(JSON.stringify(receipt)),raw=Buffer.from(pixels,'base64'),b=Buffer.alloc(4+header.length+raw.length);b.writeUInt32LE(header.length);header.copy(b,4);raw.copy(b,4+header.length);return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);}
(async()=>{
 const out=await window.FlyVisSkeletonWire.decode(wire(r),p,r.request_id,h);assert.equal(out.pixels.length,1843200);
 for(const bad of [{run_id:'foreign'},{step_id:r.step_id+1},{raw_sha256:'0'.repeat(64)},
  {source_sequence:r.source_sequence+1},{image_width:961},{source_evidence_level:'OFFLINE_SOFTWARE_REPLAY'},
  {means:r.means.map((v,i)=>i===0?v+.01:v)},{type_filter:'T4'}]){
  await assert.rejects(()=>window.FlyVisSkeletonWire.decode(wire({...r,...bad}),p,r.request_id,h));
 }
 console.log(JSON.stringify({status:'PASS_CPU_BROWSER_WIRE',actual_source:'line10 CPU pixels and original ON60 values',bytes:out.pixels.length,negative_cases:8,GPU_operations:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
