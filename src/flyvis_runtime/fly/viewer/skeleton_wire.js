/* Raw pixels only. A complete same-run receipt gates publication of each canvas. */
(() => {
 'use strict';
 async function decode(buffer,p,requestID,health){
  if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<5||buffer.byteLength>4000000)throw Error('RAW_BOUND');
  const n=new DataView(buffer).getUint32(0,true);if(n<1||n>100000||n+4>=buffer.byteLength)throw Error('RAW_HEADER');
  const r=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(buffer,4,n)));
  const a=new Uint8ClampedArray(buffer,4+n),w=r.image_width,h=r.image_height;
  if(!Number.isInteger(w)||!Number.isInteger(h)||w!==health.viewport.width||h!==health.viewport.height||a.length!==w*h*4||r.byte_length!==a.length||r.row_stride!==w*4||r.wire_format!=='json32le+rgba8-v1'||r.pixel_format!=='RGBA8'||r.channel_order!=='RGBA'||r.row_order!=='top-down')throw Error('RAW_LAYOUT');
  for(const key of ['run_id','session_id','step_id','state_token','serial','activity_time_s'])if(r[key]!==p[key])throw Error('RAW_RUN_STEP_'+key);
  if(r.request_id!==requestID||r.service_id!==health.service_id||r.spatial_values_sha256!==p.spatial.values_sha256||r.source_sequence!==p.source.sequence||r.upstream_map_sha256!==p.spatial.map_sha256||r.PL_execution!==false||r.source_evidence_level!=='ACTUAL_CONTINUOUS_FULL_GPU_STATE'||r.evidence_level!=='EXTERNAL_ACTIVITY_RENDER_ONLY')throw Error('RAW_SOURCE_IDENTITY');
  if(r.color_encoding.encoding_sha256!==health.color_encoding.encoding_sha256||r.type_filter!=='all'||r.type_states.length!==8)throw Error('RAW_COLOR_CONTRACT');
  if((r.fixed_cpu_projection_sha256||null)!==(health.fixed_cpu_projection_sha256||null))throw Error('RAW_FIXED_PROJECTION');
  for(let i=0;i<8;i++){
   const expected=p.spatial.values.slice(i*721,(i+1)*721).reduce((a,b)=>a+b,0)/721;
   if(!Number.isFinite(r.means[i])||Math.abs(r.means[i]-expected)>1e-12||r.type_states[i].value!==r.means[i]||r.types[i]!==health.expected_binding.types[i])throw Error('RAW_MEANS');
  }
  const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',a)),v=>v.toString(16).padStart(2,'0')).join('');
  if(sha!==r.raw_sha256)throw Error('RAW_SHA');
  return {receipt:r,pixels:a,width:w,height:h};
 }
 window.FlyVisSkeletonWire={decode};
})();
