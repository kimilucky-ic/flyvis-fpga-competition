/* DOM-only interaction test. No browser, HTTP listener or devices. */
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map(),requests=[],transitions=[],loadingPages=[];
class Element{
 constructor(){this.value='';this.hidden=false;this.disabled=false;this.events={};this.children=[];}
 set innerHTML(text){this.html=text;for(const match of text.matchAll(/id="([^"]+)"/g))elements.set(match[1],new Element());}
 append(child){this.children.push(child);if(this.value===''&&child.value)this.value=child.value;}
 prepend(child){this.children.unshift(child);}
 addEventListener(name,fn){this.events[name]=fn;}
 click(){if(this.events.click)return this.events.click();if(this.onclick)return this.onclick();}
}
elements.set('competitionWorkspace',new Element());
const meta={managed:true,selection:null,catalogue:{conditions:[{condition_id:'EDGE_ON_RIGHT',stationary:false},{condition_id:'EDGE_OFF_LEFT_STATIC',stationary:true}]}};
const context={document:{createElement:()=>new Element(),getElementById:id=>elements.get(id)||null,querySelector:()=>null},
 Blob:class{constructor(parts){this.text=parts.join('');}},
 URL:{createObjectURL:blob=>{loadingPages.push(blob.text);return 'blob:http://127.0.0.1/CPU_TRANSITION';}},
 location:{origin:'http://127.0.0.1:8771',replace:url=>transitions.push(url)},
 setTimeout:()=>0,setInterval:()=>0,window:{addEventListener:()=>{}},navigator:{sendBeacon:()=>true},
 fetch:async(url,options)=>{requests.push({url,options});return {ok:true,json:async()=>options?{status:'SWITCH_AFTER_NORMAL_CLOSE'}:url==='/api/operator-selection'?meta:{ready_to_start:true,can_start:true,preparation_id:'CPU_PREP_ONLY',workbench_phase:'READY_TO_START'}};}};
vm.createContext(context);vm.runInContext(fs.readFileSync('../viewer/operator_selection.js','utf8'),context);
(async()=>{
 await new Promise(setImmediate);
 const get=id=>elements.get(id);
 assert.equal(get('opCondition').children.length,2);
 for(const input of ['camera','scientific28'])for(const backend of ['GPU_FPGA','FULL_FPGA']){
  get('opInput').value=input;get('opBackend').value=backend;get('opCondition').value='EDGE_ON_RIGHT';
  get('opInput').events.change();assert.equal(get('opConditionLabel').hidden,input==='camera');
  await get('opSelect').events.click();
  const body=JSON.parse(requests.at(-1).options.body);
  assert.equal(body.input,input);assert.equal(body.backend,backend);
  assert.equal(body.condition,input==='camera'?null:'EDGE_ON_RIGHT');
 }
 assert.equal(transitions.length,4);
 assert(loadingPages.every(page=>page.includes('/api/operator-selection')&&page.includes('location.replace(target)')));
 for(const backend of ['GPU_FPGA','FULL_FPGA']){
  elements.clear();elements.set('competitionWorkspace',new Element());
  let originalStarts=0;const legacy=new Element();legacy.onclick=()=>originalStarts++;elements.set('cpJointStart',legacy);
  meta.selection={backend,input:'scientific28',condition:'EDGE_ON_RIGHT'};
  vm.runInContext(fs.readFileSync('../viewer/operator_selection.js','utf8'),context);
  await new Promise(setImmediate);await new Promise(setImmediate);
  assert.equal(get('opStart').hidden,false);assert.equal(get('opStart').disabled,false);
  await get('opStart').events.click();
  if(backend==='GPU_FPGA')assert.equal(originalStarts,1);
  else {assert.equal(requests.at(-1).url,'/api/full-pl-stream/camera-start');assert.equal(JSON.parse(requests.at(-1).options.body).preparation_id,'CPU_PREP_ONLY');}
  await get('opStop').events.click();
  assert.equal(requests.at(-1).url,backend==='GPU_FPGA'?'/api/joint-camera/stop':'/api/full-pl-stream/camera-stop');
 }
 console.log('PASS DOM_ONLY: four selections, same-tab loading handoff, visibility, POST payloads, both Start/Stop routes and original joint button delegation. No GUI/device execution.');
})().catch(e=>{console.error(e);process.exitCode=1;});
