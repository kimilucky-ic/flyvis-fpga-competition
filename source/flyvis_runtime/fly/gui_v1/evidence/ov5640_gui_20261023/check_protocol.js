/* CPU-only browser protocol functions. No server, GPU, camera or board. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const base=__dirname,root=fs.readdirSync(base).filter(n=>n.startsWith('cpu_')&&fs.existsSync(path.join(base,n,'RESULT.json'))).sort().at(-1);
const dir=path.join(base,root),read=n=>JSON.parse(fs.readFileSync(path.join(dir,n),'utf8'));
const sandbox={window:{},document:{getElementById:()=>null},location:{search:''},URLSearchParams,crypto:require('crypto').webcrypto,Float32Array,Uint8Array,console};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(base,'../../..','viewer/competition_full_pl.js'),'utf8'),sandbox);
const validate=sandbox.window.FlyVisFullPLProtocol.validateOV;
const p=read('DISPLAY.json'),s=read('STATUS.json'),h=read('PROJECTION.json');
(async()=>{
 await validate(p,s,h);
 const cases=[['state_identity',q=>q.full_state_sha256='0'.repeat(64)],['input_corruption',q=>q.input_hex[0]+=.1],['wrong_image',q=>q.hardware.bit_sha256='0'.repeat(64)],['wrong_flow',q=>q.flow[0][0]+=1],['false_live_evidence',q=>q.evidence_level='PHYSICAL_BOARD_PASS'],['wrong_source',q=>q.source.kind='real_windows_camera']];
 for(const [name,mutate] of cases){const q=structuredClone(p);mutate(q);await assert.rejects(()=>validate(q,s,h),undefined,name);}
 const report={status:'PASS_JS_PROTOCOL_ONLY',positive:1,rejected:cases.map(x=>x[0]),actual_browser_visualization:'NOT_RUN',board_operations:0};
 fs.writeFileSync(path.join(base,'JS_RESULT.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
