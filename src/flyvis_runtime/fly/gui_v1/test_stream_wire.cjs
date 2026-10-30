const fs=require('fs'),assert=require('assert'),crypto=require('crypto');
const {decode}=require('../viewer/stream_wire.js');
const {LatestFrame}=require('../viewer/stream_wire.js');
const packet=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),out=decode(packet);
for(const key of ['spatial','input_hex','flow']){
 const a=key==='spatial'?out.spatial.values:key==='flow'?Float32Array.from([...out.flow[0],...out.flow[1]]):out.input_hex;
 assert.equal(crypto.createHash('sha256').update(Buffer.from(a.buffer)).digest('hex'),packet.wire_arrays[key].sha256);
}
for(const mutation of [p=>p.wire_format='wrong',p=>p.wire_arrays.flow.shape=[1442],p=>p.wire_arrays.spatial.dtype='<f8',p=>p.wire_arrays.input_hex.base64='AAAA']){
 const p=structuredClone(packet);mutation(p);assert.throws(()=>decode(p));
}
console.log(JSON.stringify({status:'PASS',real_float32_values_checked:7931,negative_cases:4,lossless:true,source:'existing actual arrays as transport-only fixture'}));
const scheduled=[],shown=[],slot=new LatestFrame(f=>scheduled.push(f),v=>shown.push(v));
for(let i=0;i<100;i++)slot.offer({run:'CPU_PROTOCOL_ONLY',serial:i});
assert.equal(scheduled.length,1);scheduled.shift()();assert.deepEqual(shown,[{run:'CPU_PROTOCOL_ONLY',serial:99}]);
slot.offer({run:'revoked',serial:100});slot.clear();slot.offer({run:'new',serial:0});
scheduled.shift()();assert.equal(shown.length,1);scheduled.shift()();assert.equal(shown.at(-1).run,'new');
console.log(JSON.stringify({status:'PASS_LATEST_DISPLAY_SLOT',offered:100,queued_callbacks:1,stale_after_clear_rejected:true,fields_kept_together:true}));
