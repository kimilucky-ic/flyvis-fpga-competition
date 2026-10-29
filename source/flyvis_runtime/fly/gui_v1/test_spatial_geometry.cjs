// Compare actual canvas command streams against the preserved implementation.
// Existing actual GPU row only; no browser launch and no fabricated activity.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const data=JSON.parse(fs.readFileSync('evidence/realtime_prepare_20261012/node_test_fixture.json'));
function create(file){
 const calls=[],stats={trig:0};
 class Element{
  constructor(){this.children=[];this.handlers={};this.dataset={};this.value='';this.classList={toggle(){}};
   this.ctx=new Proxy({}, {get:(o,k)=>k in o?o[k]:(...a)=>calls.push([k,...a]),set:(o,k,v)=>{calls.push(['set',k,v]);o[k]=v;return true;}});}
  set innerHTML(x){this.roles={};for(const m of x.matchAll(/data-role="([^"]+)"/g))this.roles[m[1]]=new Element();this.roles.limit.value='1';}
  querySelector(x){return this.roles[x.match(/"([^"]+)"/)[1]];}
  append(...v){this.children.push(...v);}insertBefore(x){this.children.push(x);}replaceChildren(...v){this.children=v;this.value=v[0]?.value||'';}
  addEventListener(k,f){this.handlers[k]=f;}setAttribute(){}getContext(){return this.ctx;}getBoundingClientRect(){return {left:0,top:0,width:760,height:420};}
 }
 const math=Object.create(Math);for(const name of ['sin','cos'])math[name]=x=>{stats.trig++;return Math[name](x);};
 const root=new Element(),c={document:{getElementById:()=>root,createElement:()=>new Element()},window:{},Math:math,Option:class{constructor(t,v){this.value=v;}},console};
 vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);const view=new c.window.FlyVisSpatialView('test');view.setMetadata(data.metadata);
 calls.length=0;stats.trig=0;return {view,calls,stats};
}
const old=create('evidence/hybrid_prepare_20261012/spatial_view_before.js'),next=create('../viewer/spatial_view.js');
old.view.accept(data.packet);next.view.accept(data.packet);
assert.deepStrictEqual(next.calls,old.calls);assert.equal(next.stats.trig,0);assert.equal(old.stats.trig,(5768+721)*6*2);
old.calls.length=next.calls.length=0;
for(const x of [old,next]){x.view.mini[7].button.handlers.click();x.view.$('plan').value='H67';x.view.draw();x.view.point({clientX:x.view.visible[360].x,clientY:x.view.visible[360].y},true);}
assert.deepStrictEqual(next.calls,old.calls);assert.equal(next.view.selected,old.view.selected);
for(const x of [old,next]){x.calls.length=0;x.view.clear();}
assert.deepStrictEqual(next.calls,old.calls);
console.log(JSON.stringify({status:'PASS_CPU_CANVAS_COMMAND_EQUIVALENCE',checks:4,per_draw_trigonometry_before:77868,per_draw_trigonometry_after:0,
 geometry_only_cache:true,numeric_activity_unchanged:true,browser_FPS:'NOT_MEASURED',GPU_run:false}));
