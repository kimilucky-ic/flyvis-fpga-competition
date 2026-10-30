// Software protocol validation in Node VM; no browser, GUI, network or board.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const crypto=require('crypto').webcrypto;
const root=__dirname,viewer=path.resolve(root,'../../../viewer/competition_full_pl.js');
const sandbox={window:{},document:{getElementById:()=>null},crypto,Uint8Array,Float32Array,Number,Math,Error};
vm.runInNewContext(fs.readFileSync(viewer,'utf8'),sandbox);
const p=sandbox.window.FlyVisFullPLProtocol;
const f=JSON.parse(fs.readFileSync(path.join(root,'CPU_BROWSER_FIXTURE.json'),'utf8'));
async function rejects(value){let failed=false;try{await p.validateStream(value,f.status,f.anchor,f.health);}catch(e){failed=true;}assert(failed);}
(async()=>{
 await p.validateStream(f.packet,f.status,f.anchor,f.health);
 await rejects({...f.packet,run_id:'WRONG'});
 await rejects({...f.packet,flow_binding:{...f.packet.flow_binding,frame_id:484}});
 await rejects({...f.packet,input_time_s:0});
 await rejects({...f.packet,display_kind:'CURRENT_FULL_PL_STATE_PENDING_AUDIT'});
 const camera=JSON.parse(fs.readFileSync(path.join(root,'CPU_BROWSER_CAMERA_FIXTURE.json'),'utf8'));
 const ca={...f.anchor,plan_metadata:camera.plan_metadata};
 const cp={...camera,display_kind:'FINISHED_FULL_PL_LAST_STATE'};
 const before=JSON.stringify(f.anchor.plan_metadata);f.anchor.plan_metadata=ca.plan_metadata;
 await p.validateStream(cp,f.status,ca,f.health);
 assert.notEqual(before,JSON.stringify(ca.plan_metadata));
 const result={status:'PASS',checks:6,evidence:'NODE_VM_PROTOCOL_ONLY_NOT_BROWSER',
   cases:['ON60 negative time same-state replay','wrong run rejected','wrong flow step rejected','wrong timeline rejected',
          'replay/live label mismatch rejected','recorded camera zero-offset same-state packet']};
 fs.writeFileSync(path.join(root,'UI_PROTOCOL_RESULT.json'),JSON.stringify(result,null,2)+'\n');
 process.stdout.write(JSON.stringify(result)+'\n');
})().catch(e=>{console.error(e);process.exitCode=1;});
