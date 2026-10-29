const fs=require('fs'),assert=require('assert');
const root='../ov5640_live_v261_20261026';
const ui=require(root+'/assets/monitor.js');
const labels=[],coords=[];
const ctx=new Proxy({fillText:(s)=>labels.push(s),moveTo:(...p)=>coords.push(p),lineTo:(...p)=>coords.push(p),arc:(...p)=>coords.push(p)}, {get:(o,k)=>k in o?o[k]:()=>{}});
const canvas={clientWidth:1800,clientHeight:900,dataset:{},getContext:()=>ctx};
const rows=[0,1,2].map((step)=>({step,time:step*.005,means:[Array(14).fill(step===0?12:.04),Array(14).fill(-.03)],reference:[Array(14).fill(0),Array(14).fill(0)]}));
const original=JSON.stringify(rows);
for(const common of [.5,1])for(const d of [.05,.1,.25,.5,1,2]){
 ui.draw(canvas,rows,[6,7,8,9,10,11,12,13],['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'],common,0,false,4,d);
 assert.deepStrictEqual(JSON.parse(canvas.dataset.chartDomains),[common,common,common,d,common,common,common,common]);
}
assert.strictEqual(JSON.stringify(rows),original);
assert(labels.some(s=>s.includes('超出刻度')));
assert(labels.some(s=>s.includes('独立纵轴')));
assert(coords.flat().every(Number.isFinite));
assert.strictEqual(ui.chartDomain(9,1,NaN),1);
assert.strictEqual(ui.chartDomain(9,1,0),1);
const html=fs.readFileSync(root+'/assets/index.html','utf8');
for(const id of ['curveScale','t4dScale','t4dScaleControl'])assert.strictEqual(html.split('id="'+id+'"').length,2);
const result={status:'PASS_CPU_FIXED_CURVE_SCALE',cases:12,raw_values_unchanged:true,startup_spike_does_not_expand_axis:true,clipping_label:true,t4d_independent:true,browser:'NOT_VERIFIED_CONNECTION_REFUSED',board_operations:0};
fs.writeFileSync('CPU_RESULT.json',JSON.stringify(result,null,2));console.log(result);
