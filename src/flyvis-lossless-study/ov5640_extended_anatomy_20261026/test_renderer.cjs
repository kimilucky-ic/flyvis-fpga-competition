const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const O=__dirname,R=path.resolve(O,'../ov5640_live_v261_20261026');
const packets=JSON.parse(fs.readFileSync(path.resolve(O,'../ov5640_neuron_monitor_20261026/packets.json'),'utf8'));
const ObserverUI=require(path.join(R,'assets/monitor.js')),groups=require(path.join(R,'assets/ui.js'));
function context(file){const w={FlyVisFullPLGroups:{groupSample:groups.groupSample}};const ctx={window:w,ObserverUI,crypto:crypto.webcrypto,performance,ArrayBuffer,DataView,Float32Array,Uint8Array,Uint8ClampedArray,TextDecoder,TextEncoder,console};vm.runInNewContext(fs.readFileSync(file,'utf8'),ctx);return w.FlyVisFixedSkeleton;}
function ab(buf){return buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength);}
(async()=>{
 const P=context(path.join(R,'assets/fixed_skeleton.js')),health=JSON.parse(fs.readFileSync(path.join(R,'assets/projection.json'))),wire=fs.readFileSync(path.join(R,'assets/projection.bin'));const p=await P.decode(ab(wire),health),times=[];
 for(let i=0;i<packets.length;i++){const r=await p.render(packets[i],'test-'+i,{roi:0,relative:false,visible:Array(14).fill(true)});assert.deepEqual(r.receipt.values,packets[i].observer.means[0]);times.push(r.composeMs);}
 const modes=[{roi:0,relative:false,visible:Array(14).fill(true)},{roi:1,relative:true,visible:Array.from({length:14},(_,i)=>i!==0&&!(i>=6&&i<10))},{roi:0,relative:false,visible:Array(14).fill(false)}];
 const latest=packets.at(-1),receipts=[];
 for(let i=0;i<modes.length;i++){const r=await p.render(latest,'case'+i,modes[i]);fs.writeFileSync(path.join(O,'case'+i+'.rgba'),Buffer.from(r.pixels));receipts.push(r.receipt);const again=await p.render(latest,'repeat',modes[i]);assert.equal(again.receipt.raw_sha256,r.receipt.raw_sha256);}
 const bad=Buffer.from(wire);bad[bad.length-1]^=1;await assert.rejects(()=>P.decode(ab(bad),health));
 await assert.rejects(()=>p.render({...latest,step_id:9999},'bad',modes[0]));await assert.rejects(()=>p.render(latest,'bad',{roi:5}));
 const Old=context(path.join(O,'before/assets/fixed_skeleton.js'));const oldHealth=JSON.parse(fs.readFileSync(path.join(O,'before/assets/projection.json'))),oldP=await Old.decode(ab(fs.readFileSync(path.join(O,'before/assets/projection.bin'))),oldHealth),oldTimes=[];
 for(const packet of packets){const r=await oldP.render(packet,'old','CENTRAL_ROI37_T4T5');oldTimes.push(r.composeMs);}
 const stats=a=>({mean_ms:a.reduce((x,y)=>x+y,0)/a.length,median_ms:[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)],max_ms:Math.max(...a)});
 fs.writeFileSync(path.join(O,'RENDER_TEST.json'),JSON.stringify({status:'PASS_NODE_CPU_SAVED_RECORD_RENDER',records:packets.length,modes,receipts,new_stats:stats(times),old_stats:stats(oldTimes),timing_scope:'PC_NODE_TYPED_ARRAY_ONLY_NOT_BROWSER_OR_BOARD',corrupt_cache_rejected:true,step_mismatch_rejected:true,invalid_roi_rejected:true,deterministic_pixels:true,board_actions:0},null,2));console.log('PASS14type renderer, exact signedreadout, visibility, corruptcache and stepbinding; new',stats(times),'old',stats(oldTimes));
})().catch(e=>{console.error(e);process.exit(1)});
