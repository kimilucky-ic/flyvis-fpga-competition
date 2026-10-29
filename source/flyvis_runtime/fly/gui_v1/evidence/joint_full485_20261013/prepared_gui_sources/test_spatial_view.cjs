// DOM/canvas behavior using an existing actual GPU sample; no synthetic activities.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
class Element {
 constructor(){this.children=[];this.handlers={};this.dataset={};this.value='';this.classList={toggle(){}};this.ctx=new Proxy({fills:0,fill(){this.fills++;}},{get:(o,k)=>o[k]||(()=>{})});}
 set innerHTML(x){this.roles={};for(const m of x.matchAll(/data-role="([^"]+)"/g))this.roles[m[1]]=new Element();this.roles.limit.value='1';}
 querySelector(x){return this.roles[x.match(/"([^"]+)"/)[1]];}
 append(...v){this.children.push(...v);} insertBefore(x){this.children.push(x);} replaceChildren(...v){this.children=v;this.value=v[0]?.value||'';}
 addEventListener(k,f){this.handlers[k]=f;}setAttribute(){}getContext(){return this.ctx;}getBoundingClientRect(){return {left:0,top:0,width:760,height:420};}
}
const root=new Element(),context={document:{getElementById:()=>root,createElement:()=>new Element()},window:{},Option:class{constructor(t,v){this.value=v;this.textContent=t;}},console};
vm.createContext(context);vm.runInContext(fs.readFileSync('../viewer/spatial_view.js','utf8'),context);
const data=JSON.parse(fs.readFileSync('evidence/realtime_prepare_20261012/node_test_fixture.json','utf8'));
const view=new context.window.FlyVisSpatialView('test');view.setMetadata(data.metadata);view.accept(data.packet);
assert.equal(view.mini.length,8);assert(view.mini.every(m=>m.canvas.dataset.nodeCount==='721'&&m.canvas.dataset.run===data.packet.run_id));
view.mini[7].button.handlers.click();assert.equal(view.$('type').value,'T5d');assert.equal(view.visible.length,721);
view.$('plan').value='H67';view.draw();assert(view.$('status').textContent.includes('67 个，其中 T4/T5 11'));
view.point({clientX:view.visible[360].x,clientY:view.visible[360].y},true);assert.notEqual(view.selected,null);
view.accept({...data.packet,run_id:'new_test_run'});assert.equal(view.rows.length,1);assert.equal(view.selected,null);
assert.throws(()=>view.accept({...data.packet,layers:{...data.packet.layers,PL_proven_global_ids:[1]}}));
assert.throws(()=>view.admitOfflineProof({status:'SOFTWARE_PILOT',PL_proven_global_ids:[]}));
const fixtureProof={status:'VERIFIED_ACTUAL_JOINT_OFFLINE_REPLAY',display_mode:'OFFLINE_REPLAY',run_id:'CPU_PROTOCOL_FIXTURE_NOT_ACTUAL_PL',acceptance_sha256:'a'.repeat(64),spatial_metadata:data.metadata,PL_proven_global_ids:data.metadata.nodes.map(n=>n.global_id)};
view.admitOfflineProof(fixtureProof);
const fixturePacket={...data.packet,run_id:fixtureProof.run_id,mode:'OFFLINE_REPLAY',acceptance_sha256:fixtureProof.acceptance_sha256,layers:{...data.packet.layers,PL_proven_global_ids:fixtureProof.PL_proven_global_ids}};
view.accept(fixturePacket);assert(view.$('status').textContent.includes('历史 PL 5768'));
assert.throws(()=>view.accept({...fixturePacket,run_id:'other_run'}));
assert.throws(()=>view.accept({...fixturePacket,acceptance_sha256:'b'.repeat(64)}));
assert.throws(()=>view.accept({...fixturePacket,mode:'LIVE'}));
assert.throws(()=>view.accept({...fixturePacket,layers:{...fixturePacket.layers,PL_proven_global_ids:fixtureProof.PL_proven_global_ids.map(()=>1)}}));
view.clear();assert.equal(view.sample,null);assert.equal(view.rows.length,0);
console.log(JSON.stringify({status:'PASS_DOM_BEHAVIOR_TEST_ONLY',checks:15,overview_maps:8,nodes_per_map:721,source:data.label,PL_labels:'CPU_PROTOCOL_FIXTURES_ONLY_NO_NEW_PL_PROOF'}));
