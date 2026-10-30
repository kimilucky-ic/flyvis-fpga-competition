/* DOM-only interaction test. No browser, HTTP listener or devices. */
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map(),requests=[],transitions=[],loadingPages=[],ready=[];
class Element{
 constructor(){this.attrs={};this.classes=new Set();this.classList={add:x=>this.classes.add(x),toggle:(x,on)=>on?this.classes.add(x):this.classes.delete(x)};this.value='';this.hidden=false;this.disabled=false;this.events={};this.children=[];}
 set innerHTML(text){this.html=text;for(const match of text.matchAll(/id="([^"]+)"/g))elements.set(match[1],new Element());}
 append(child){this.children.push(child);if(this.value===''&&child.value)this.value=child.value;}
 prepend(child){this.children.unshift(child);}
 setAttribute(k,v){this.attrs[k]=v;}
 addEventListener(name,fn){this.events[name]=fn;}
 click(){if(this.events.click)return this.events.click();if(this.onclick)return this.onclick();}
}
elements.set('competitionWorkspace',new Element());
const meta={managed:true,selection:null,catalogue:{conditions:[{condition_id:'EDGE_ON_RIGHT',stationary:false},{condition_id:'EDGE_OFF_LEFT_STATIC',stationary:true}]}};
const context={document:{body:new Element(),readyState:'loading',addEventListener:(name,fn)=>{if(name==='DOMContentLoaded')ready.push(fn);},createElement:()=>new Element(),getElementById:id=>elements.get(id)||null,querySelector:()=>null},
 Blob:class{constructor(parts){this.text=parts.join('');}},
 URL:{createObjectURL:blob=>{loadingPages.push(blob.text);return 'blob:http://127.0.0.1/CPU_TRANSITION';}},
 location:{origin:'http://127.0.0.1:8771',replace:url=>transitions.push(url)},
 setTimeout:()=>0,setInterval:()=>0,window:{addEventListener:()=>{}},navigator:{sendBeacon:()=>true},
 fetch:async(url,options)=>{requests.push({url,options});return {ok:true,json:async()=>options?{status:'SWITCH_AFTER_NORMAL_CLOSE'}:url==='/api/operator-selection'?meta:{ready_to_start:true,can_start:true,preparation_id:'CPU_PREP_ONLY',workbench_phase:'READY_TO_START'}};}};
vm.createContext(context);vm.runInContext(fs.readFileSync('../viewer/operator_selection.js','utf8'),context);
(async()=>{
 await new Promise(setImmediate);
 const get=id=>elements.get(id);
 const oldTools=new Element();elements.set('cpLiveTools',oldTools);
 const oldOptions=new Element();elements.set('cpOptions',oldOptions);
 const oldPreview=new Element();elements.set('cpStimuli28Controls',oldPreview);
 elements.set('cpStimuli28Open',new Element());elements.set('cpStimuli28Condition',new Element());
 ready.shift()();
 assert.equal(get('opAdvanced').children[0],oldTools);
 assert.equal(get('opReplay').children[0],oldPreview);
 assert.equal(get('opCondition').children.length,2);
 assert(context.document.body.classes.has('operator-unified'));
 assert(!context.document.body.classes.has('operator-settings'));
 assert(!elements.has('opDisplayTab'));
 assert(get('opPrimary').children[0].html.includes('纯FPGA · 全45669节点'));
 assert.equal(context.document.body.children[0].id,'opDrawer');
 const css=fs.readFileSync('../viewer/competition.css','utf8');
 assert(!css.includes('body.operator-settings main'));
 assert(css.includes('width:100%;max-width:none'));
 for(const input of ['camera','scientific28'])for(const backend of ['GPU_FPGA','FULL_FPGA']){
  get('opInput').value=input;get('opBackend').value=backend;get('opCondition').value='EDGE_ON_RIGHT';
  get('opInput').events.change();assert.equal(get('opConditionLabel').hidden,input==='camera');
  await get('opSelect').events.click();
  const body=JSON.parse(requests.at(-1).options.body);
  assert.equal(body.input,input);assert.equal(body.backend,backend);
  assert.equal(body.condition,input==='camera'?null:'EDGE_ON_RIGHT');
 }
 assert.equal(transitions.length,0);
 assert.equal(get('competitionWorkspace').hidden,true);
 assert(get('opHint').textContent.includes('正在准备'));
 assert(!fs.readFileSync('../viewer/operator_selection.js','utf8').includes('createObjectURL'));
 assert.equal(loadingPages.length,0);
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
 console.log('PASS DOM_ONLY: inline settings above original full-size stage, no page tabs, visible pure-FPGA choice, original tools relocated, four selections, inline bounded handoff without blob navigation, visibility, POST payloads, both Start/Stop routes and original joint button delegation. No GUI/device execution.');
})().catch(e=>{console.error(e);process.exitCode=1;});
