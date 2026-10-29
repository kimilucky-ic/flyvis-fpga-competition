/* Exact FP32 transport; no reconstruction/interpolation of neural activity. */
(function(root){
 'use strict';
 function decode(p){
  if(p.wire_format!=='float32-le-base64/v1')throw Error('WIRE_FORMAT');
  const shapes={spatial:[5768],input_hex:[721],flow:[2,721]},out={...p,spatial:{...p.spatial}};
  if(Object.keys(p.wire_arrays).sort().join(',')!==Object.keys(shapes).sort().join(','))throw Error('WIRE_ARRAYS');
  for(const [key,shape] of Object.entries(shapes)){
   const a=p.wire_arrays[key],count=shape.reduce((x,y)=>x*y,1);
   if(a.dtype!=='<f4'||JSON.stringify(a.shape)!==JSON.stringify(shape)||a.base64.length>count*6)throw Error('WIRE_SCHEMA');
   const bytes=Uint8Array.from(atob(a.base64),c=>c.charCodeAt(0));if(bytes.length!==count*4)throw Error('WIRE_LENGTH');
   const data=new DataView(bytes.buffer),values=new Float32Array(count);
   for(let i=0;i<count;i++){values[i]=data.getFloat32(i*4,true);if(!Number.isFinite(values[i]))throw Error('WIRE_NONFINITE');}
   if(key==='spatial')out.spatial.values=values;
   else out[key]=key==='flow'?[values.subarray(0,721),values.subarray(721)]:values;
  }
  delete out.wire_arrays;delete out.wire_format;return out;
 }
 class LatestFrame {
  constructor(schedule,consume){this.schedule=schedule;this.consume=consume;this.pending=null;this.queued=false;this.generation=0;}
  offer(value){this.pending=value;if(this.queued)return;this.queued=true;const generation=this.generation;this.schedule(()=>{if(generation!==this.generation)return;this.queued=false;const latest=this.pending;this.pending=null;if(latest)this.consume(latest);});}
  clear(){this.pending=null;this.queued=false;this.generation++;}
 }
 if(typeof module!=='undefined'&&module.exports)module.exports={decode,LatestFrame};else root.FlyVisStreamWire={decode,LatestFrame};
})(typeof window!=='undefined'?window:globalThis);
