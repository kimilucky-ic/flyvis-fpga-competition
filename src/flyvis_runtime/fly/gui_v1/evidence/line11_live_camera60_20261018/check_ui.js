// No browser, Canvas renderer, socket or physical hardware is opened.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto').webcrypto;
const root=path.resolve(__dirname,'../../..');
const source=fs.readFileSync(path.join(root,'viewer/competition_full_pl.js'),'utf8');
const context={window:{},document:{getElementById:()=>null},crypto,Float32Array,Uint8Array,Number,Math,console};
vm.runInNewContext(source,context);
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'UI_PROTOCOL_FIXTURE.json'),'utf8'));
(async()=>{
 const {frame,status,anchor,health}=fixture,validate=context.window.FlyVisFullPLProtocol.validateStream;
 await validate(frame,status,anchor,health);
 let rejected=0;
 for(const change of [p=>p.source.run_id='wrong',p=>p.source.hex_values_sha256='0'.repeat(64),p=>p.flow_binding.full_state_sha256='0'.repeat(64)]){
  const bad=JSON.parse(JSON.stringify(frame));change(bad);
  try{await validate(bad,status,anchor,health);throw Error('Bad source unexpectedly accepted');}
  catch(e){if(e.message==='Bad source unexpectedly accepted')throw e;rejected++;}
 }
 const result={status:'PASS_CPU_FRONTEND_PROTOCOL_ONLY',positive:1,rejected,GUI:0,browser:0,board:0};
 fs.writeFileSync(path.join(__dirname,'JS_PROTOCOL_RESULT.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1;});
