const assert=require('node:assert/strict'),fs=require('node:fs');
const {snapshot}=require('../viewer/demo_guide.js');
const cases=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let checked=0;const examples=[];
for(const s of cases){
  for(let k=0;k<s.dataset.n_frames;k++){
    s.frame=k;const v=snapshot(s);assert(v);
    for(const cell of v.values){assert.equal(cell.value,s.activity[k*s.dataset.cell_types.length+s.dataset.cell_types.indexOf(cell.cell)]);checked++;}
    assert.equal(v.inputTime,s.dataset.time_s[k]);
    assert.equal(v.metric.dsi,s.directions.official_metric.official_dsi);
    assert.equal(v.metric.direction,s.directions.official_metric.preferred_direction_deg);
  }
  s.frame=250;examples.push({sample:s.sample.sample_id,condition:s.sample.conditions,...snapshot(s)});
}
const s=cases[0];let negatives=0;
for(const patch of [{loading:true},{activity:null},{stimulus:null},{frame:-1},{frame:9999},{frame:NaN},{sample:{...s.sample,dataset_id:'another'}}]){assert.equal(snapshot({...s,...patch}),null);negatives++;}
const bad=[...s.activity];bad[s.frame*s.dataset.cell_types.length+s.dataset.cell_types.indexOf('T4a')]=NaN;
assert.equal(snapshot({...s,activity:bad}),null);negatives++;
for(const patch of [{dataset_id:'other'},{intensity:0},{official_peaks:[]},{official_metric:null},{official_metric:{...s.directions.official_metric,cell_type:'wrong'}},{official_metric:{...s.directions.official_metric,official_dsi:NaN}}]){assert.equal(snapshot({...s,directions:{...s.directions,...patch}}).metric,null);negatives++;}
assert.equal(snapshot({...s,comparison:{}}).metric,null);negatives++;
assert.equal(snapshot({...s,dataset:{...s.dataset,id:'flash'},sample:{...s.sample,dataset_id:'flash'}}).metric,null);negatives++;
console.log(JSON.stringify({status:'PASS',actual_activity_values_checked:checked,actual_frames_checked:970,negative_cases:negatives,examples}));
