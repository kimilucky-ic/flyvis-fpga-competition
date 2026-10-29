/* CPU transport fault injection; no browser, camera, server or inference. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('viewer/live_camera.js','utf8');
const fn=source.slice(source.indexOf(' async function request('),source.indexOf(' function clear()'));
async function scenario(fetch,body){const metrics={};const ctx={fetch,performance,requestMetrics:metrics,setTimeout:callback=>callback(),Promise};vm.createContext(ctx);vm.runInContext(fn+';this.request=request;',ctx);return {call:()=>ctx.request('/api/stream/latest?after=-1',body),metrics};}
(async()=>{
 let n=0,s=await scenario(async()=>{if(++n===1)throw TypeError('transport interrupted');return {ok:true,json:async()=>({status:'ACTUAL_TEST_ONLY'})};});
 assert.equal((await s.call()).status,'ACTUAL_TEST_ONLY');assert.equal(n,2);assert.equal(s.metrics['/api/stream/latest'].transport_retries,1);
 n=0;s=await scenario(async()=>{n++;throw TypeError('transport interrupted');},{});await assert.rejects(s.call());assert.equal(n,1);
 n=0;s=await scenario(async()=>{n++;return {ok:false,json:async()=>({error:'IDENTITY_REJECTED'})};});await assert.rejects(s.call(),/IDENTITY_REJECTED/);assert.equal(n,1);
 n=0;s=await scenario(async()=>{n++;throw TypeError('persistent disconnect');});await assert.rejects(s.call(),/persistent disconnect/);assert.equal(n,3);
 n=0;s=await scenario(async()=>{n++;return {ok:true,json:async()=>{throw SyntaxError('invalid data');}};});await assert.rejects(s.call(),/invalid data/);assert.equal(n,1);
 console.log('PASS: GET transient recovery; POST/identity/invalid data not retried; disconnect bounded');
})().catch(e=>{console.error(e);process.exitCode=1;});
