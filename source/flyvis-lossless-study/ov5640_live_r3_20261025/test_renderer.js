const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
global.crypto=require('crypto').webcrypto;global.window={};
const root=__dirname,output=fs.readFileSync(path.join(root,'evidence/latest_cpu.txt'),'utf8').trim();
const read=f=>fs.readFileSync(path.join(root,f));
vm.runInThisContext(read('assets/fixed_skeleton.js').toString());
const {DisplayCursor}=require('./assets/ui.js');
(async()=>{
 const h=JSON.parse(read('assets/projection.json')),b=read('assets/projection.bin');
 const renderer=await window.FlyVisFixedSkeleton.decode(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),h);
 const packets=JSON.parse(fs.readFileSync(path.join(output,'display_packets.json'),'utf8')),cursor=new DisplayCursor();
 const hashes=[];
 for(const p of packets){assert(cursor.accepts(p));const r=await renderer.render(p,'cpu-test-'+p.step_id);
  assert.equal(r.receipt.state_token,p.state_token);assert.equal(r.receipt.source_sequence,p.step_id);
  assert.equal(r.pixels.length,960*480*4);hashes.push(r.receipt.raw_sha256);cursor.commit(p);
  fs.writeFileSync(path.join(output,'render_'+p.step_id+'.rgba'),Buffer.from(r.pixels));
  fs.writeFileSync(path.join(output,'render_'+p.step_id+'.json'),JSON.stringify(r.receipt,null,2));
 }
 assert(!cursor.commit(packets[1]));assert(!cursor.accepts(packets[0]));assert.equal(cursor.shown,2);assert.equal(cursor.skipped,30);
 assert.throws(()=>cursor.accepts({...packets[1],session_id:'other'}));
 await assert.rejects(()=>renderer.render({...packets[0],spatial:{...packets[0].spatial,map_sha256:'wrong'}},'bad'));
 const altered=Buffer.from(b);altered[altered.length-1]^=1;
 await assert.rejects(()=>window.FlyVisFixedSkeleton.decode(altered.buffer.slice(altered.byteOffset,altered.byteOffset+altered.byteLength),h));
 assert.notEqual(hashes[0],hashes[1]);
 const result={status:'PASS_NODE_CPU_ORIGINAL_RENDERER_AND_DISPLAY_CURSOR',displayed_steps:[0,31],display_skips:30,
  retained_neural_records:32,duplicate_and_old_frames_ignored:true,wrong_session_and_map_rejected:true,
  geometry_hash_checked:true,pixel_hashes:hashes,browser_native_DOM_tested:false,board_operations:0};
 fs.writeFileSync(path.join(output,'RENDER_RESULT.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1;});
