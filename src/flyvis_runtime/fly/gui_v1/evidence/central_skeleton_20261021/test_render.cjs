const fs=require('fs'),assert=require('assert'),vm=require('vm'),{webcrypto}=require('crypto'),{performance}=require('perf_hooks');
const b='C:/Users/hzy72/Documents/ChatGPT/fly',e=b+'/gui_v1/evidence/central_skeleton_20261021';
function context(){const c={window:{},document:{getElementById(){return null}},crypto:webcrypto,performance,TextEncoder,TextDecoder,ArrayBuffer,DataView,Uint8Array,Uint8ClampedArray,Float32Array};vm.createContext(c);return c;}
(async()=>{
const h=JSON.parse(fs.readFileSync(e+'/health.json')),bytes=fs.readFileSync(e+'/projection.cache'),blob=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
const c=context();vm.runInContext(fs.readFileSync(b+'/viewer/competition_full_pl.js','utf8'),c);vm.runInContext(fs.readFileSync(b+'/viewer/fixed_skeleton.js','utf8'),c);const projection=await c.window.FlyVisFixedSkeleton.decode(blob,h);
const old=context();vm.runInContext(fs.readFileSync(e+'/fixed_skeleton.js.before','utf8'),old);const prior=await old.window.FlyVisFixedSkeleton.decode(blob,h);
const packets=JSON.parse(fs.readFileSync(b+'/gui_v1/evidence/central_gui_20261021/fixture.json'));let last=null;const results=[];
for(const p0 of packets){const p={...p0,source:{sequence:p0.step_id}};const a=await projection.render(p,'cpu-test','CENTRAL_T4T5');
 assert.deepEqual(Array.from(a.receipt.central_signed),p.expected);assert.deepEqual(Array.from(a.receipt.central_rectified),p.expected.map(v=>Math.max(v,0)));
 for(let i=0;i<8;i++){assert.equal(a.receipt.type_states[i].activity_signed,p.expected[i]);assert.equal(a.receipt.type_states[i].brightness_factor,.25+.75*Math.pow(Math.min(1,Math.max(0,p.expected[i])/3),.45));if(p.expected[i]<=0)assert.equal(a.receipt.type_states[i].brightness_factor,.25);}
 const legacy=await projection.render(p,'legacy'),original=await prior.render(p,'legacy');assert.equal(legacy.receipt.raw_sha256,original.receipt.raw_sha256);
 assert.equal(a.receipt.brightness_source,'CENTRAL_T4T5_RECTIFIED');assert(a.receipt.raw_sha256!==legacy.receipt.raw_sha256);
 if(p.step_id===310){const name=results.length<11?'ON':'OFF';fs.writeFileSync(e+'/'+name+'_rgba.bin',a.pixels);fs.writeFileSync(e+'/'+name+'_receipt.json',JSON.stringify(a.receipt,null,2));}
 results.push({run:p.run_id,step:p.step_id,central_signed:a.receipt.central_signed,brightness:a.receipt.type_states.map(s=>s.brightness_factor),pixel_sha256:a.receipt.raw_sha256});last=p;
}
await assert.rejects(()=>projection.render(last,'bad','INVALID'),/READOUT_MODE/);
await assert.rejects(()=>projection.render({...last,spatial:{...last.spatial,map_sha256:'wrong'}},'bad','CENTRAL_T4T5'),/SPATIAL_MAP/);
fs.writeFileSync(e+'/RESULT.json',JSON.stringify({status:'PASS_CPU_SAVED_STATE_REAL_GEOMETRY_RENDER',saved_packets:22,all_central_values_match_right_curve:true,negative_values_keep_outline:true,legacy_pixel_hashes_unchanged:22,fixed_domain:[0,3],gamma:.45,min_brightness:.25,actual_browser:'NOT_RUN',new_neural_experiments:0,results},null,2));console.log('PASS 22 real-geometry central brightness frames; old path pixel-identical; wrong mode/map rejected');
})().catch(e=>{console.error(e);process.exitCode=1});
