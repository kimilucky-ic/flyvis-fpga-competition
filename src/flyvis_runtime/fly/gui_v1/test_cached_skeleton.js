/* CPU only: exact pixels versus actual CPU renderer on saved real ON60 activity. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
global.window={};global.crypto=require('node:crypto').webcrypto;
vm.runInThisContext(fs.readFileSync('viewer/fixed_skeleton.js','utf8'));
const folder=process.argv[2],load=name=>JSON.parse(fs.readFileSync(path.join(folder,name),'utf8'));
(async()=>{
 const health=load('cache_health.json'),b=fs.readFileSync(path.join(folder,'projection.cache')),buffer=b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);
 const projection=await window.FlyVisFixedSkeleton.decode(buffer,health),packets=load('packets.json'),receipts=load('receipts.json'),timings=[];
 for(let i=0;i<packets.length;i++){
  const out=await projection.render(packets[i],receipts[i].request_id);assert.equal(out.receipt.raw_sha256,receipts[i].raw_sha256,'exact original CPU reference pixels at '+packets[i].step_id);
  for(let j=0;j<8;j++)assert.ok(Math.abs(out.receipt.means[j]-receipts[i].means[j])<1e-12);
  timings.push(out.composeMs);
 }
 const corrupt=buffer.slice(0);new Uint8Array(corrupt)[corrupt.byteLength-1]^=1;
 await assert.rejects(window.FlyVisFixedSkeleton.decode(corrupt,health),/CACHE_FILE_SHA/);
 const bad=structuredClone(packets[0]);bad.spatial.map_sha256='0'.repeat(64);await assert.rejects(projection.render(bad,'bad'),/SPATIAL_MAP/);
 const sorted=[...timings].sort((a,b)=>a-b),report={status:'PASS_EXACT_CPU_PIXELS_SAVED_REAL_ACTIVITY',frames:packets.length,checked_means:packets.length*8,new_neural_steps:0,browser_GPU_used:false,environment:'Node CPU, not browser performance',cache_bytes:b.length,per_frame_skeleton_network_bytes:0,compose_ms_p50:sorted[Math.floor(sorted.length*.5)],compose_ms_p95:sorted[Math.floor(sorted.length*.95)]};
 fs.writeFileSync(path.join(folder,'node_cache_test.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
