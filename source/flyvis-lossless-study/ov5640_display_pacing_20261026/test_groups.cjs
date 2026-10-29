const fs=require('fs'),path=require('path'),assert=require('assert');
const E=__dirname,P=path.resolve(E,'../ov5640_live_v261_20261026');
const {groupSample,GroupHistory,DisplayCursor}=require(path.join(P,'assets/ui.js'));
const cases=JSON.parse(fs.readFileSync(path.join(E,'fixtures.json'))),h=new GroupHistory(),cursor=new DisplayCursor();
for(const {packet,expected} of cases){const r=h.add(packet);assert.deepStrictEqual(r.raw,expected);assert.deepStrictEqual(r.values,expected.map(x=>Math.max(0,x)));assert(cursor.commit(packet));assert(!cursor.commit(packet));}
assert.equal(h.samples.size,3);h.add(cases[2].packet);assert.equal(h.samples.size,3);
assert.throws(()=>groupSample({...cases[0].packet,spatial:{...cases[0].packet.spatial,map_sha256:'wrong'}}));
let bad=JSON.parse(JSON.stringify(cases[0].packet));bad.spatial.values[270]=NaN;assert.throws(()=>groupSample(bad));
assert.throws(()=>cursor.accepts({...cases[2].packet,session_id:'foreign'}));h.add({...cases[0].packet,run_id:'other'});assert.equal(h.samples.size,1);
global.window={FlyVisFullPLGroups:{groupSample}};require(path.join(P,'assets/fixed_skeleton.js'));
(async()=>{const health=JSON.parse(fs.readFileSync(path.join(P,'assets/projection.json'))),bytes=fs.readFileSync(path.join(P,'assets/projection.bin'));
 const projection=await window.FlyVisFixedSkeleton.decode(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),health);
 for(const {packet,expected} of cases){const r=await projection.render(packet,'test','CENTRAL_ROI37_T4T5');assert.deepStrictEqual(r.receipt.central_roi_signed,expected);assert.equal(r.receipt.brightness_source,'CENTRAL_ROI37_MEAN_RECTIFIED');}
 const result={status:'PASS_SAVED_FRAME_CENTRAL37_GROUPS_AND_SKELETON_BINDING',saved_frame_ids:[0,200,1089],types:8,nodes_per_type:37,group_values_exact:true,negative_cases:3,duplicate_ignored:true,new_run_history_reset:true,board_actions:0};fs.writeFileSync(path.join(E,'CPU_RESULT.json'),JSON.stringify(result,null,2));console.log(result);
})().catch(e=>{console.error(e);process.exit(1)});
