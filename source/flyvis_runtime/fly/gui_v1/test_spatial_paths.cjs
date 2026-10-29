// Compare actual canvas command streams against the preserved implementation.
// Existing actual GPU row only; no browser launch and no fabricated activity.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const data=JSON.parse(fs.readFileSync('evidence/realtime_prepare_20261012/node_test_fixture.json'));
function create(file,usePath=false){
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
 if(usePath)c.Path2D=class{constructor(){this.commands=[];}moveTo(...p){this.commands.push(['moveTo',...p]);}lineTo(...p){this.commands.push(['lineTo',...p]);}closePath(){this.commands.push(['closePath']);}};
 vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);const view=new c.window.FlyVisSpatialView('test');view.setMetadata(data.metadata);
 calls.length=0;stats.trig=0;return {view,calls,stats};
}
function canonical(calls){let path=[];const out=[];for(const c of calls){if(c[0]==='beginPath')path=[];else if(['moveTo','lineTo','closePath'].includes(c[0]))path.push(c);else if(['fill','stroke'].includes(c[0]))out.push([c[0],c[1]?.commands||path.map(p=>p.slice())]);else out.push(c);}return out;}
const old=create('evidence/live_refresh_20261014/before/spatial_view.js'),next=create('../viewer/spatial_view.js',true);
for(const v of [old,next]){v.view.accept(data.packet);v.view.mini[7].button.handlers.click();v.view.$('plan').value='H67';v.view.draw();v.view.point({clientX:v.view.visible[360].x,clientY:v.view.visible[360].y},true);}
assert.deepStrictEqual(canonical(next.calls),canonical(old.calls));
console.log(JSON.stringify({status:'PASS',scenarios:4,path2d_geometry_colors_layers_and_traces_equal:true,source:'existing actual GPU sample',numeric_values_changed:false}));
