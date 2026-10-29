/* Original fixed SWC projection, CPU typed-array brightness composition.
   No neural values, geometry or intermediate neural states are synthesized. */
(() => {
 'use strict';
 const fail=(ok,message)=>{if(!ok)throw Error(message);};
 const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 class Projection {
  static async decode(buffer,health){
   fail(buffer instanceof ArrayBuffer&&buffer.byteLength>4&&buffer.byteLength<=16000000,'PROJECTION_CACHE_BOUND');
   fail(await sha(buffer)===health.projection_cache.sha256,'PROJECTION_CACHE_FILE_SHA');
   const n=new DataView(buffer).getUint32(0,true);fail(n>0&&n<65536&&n+4<buffer.byteLength,'PROJECTION_CACHE_HEADER');
   const m=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(buffer,4,n))),data=buffer.slice(4+n);
   fail(m.schema==='flyvis-fixed-cpu-cache/v1'&&m.projection_sha256===health.fixed_cpu_projection_sha256,'PROJECTION_CACHE_IDENTITY');
   fail(m.width===health.viewport.width&&m.height===health.viewport.height&&m.width<=1280&&m.height<=640,'PROJECTION_CACHE_VIEW');
   fail(await sha(data)===m.payload_sha256,'PROJECTION_CACHE_PAYLOAD_SHA');
   fail(m.arrays.length===10&&m.boxes.length===8,'PROJECTION_CACHE_LAYERS');
   const arrays={};let end=0;
   for(const a of m.arrays){
    fail(a.offset===end&&!Object.hasOwn(arrays,a.name)&&Number.isSafeInteger(a.length)&&a.length>0&&end+a.length<=data.byteLength,'PROJECTION_CACHE_ARRAY');
    fail(['<f4','|u1'].includes(a.dtype)&&a.shape.every(v=>Number.isSafeInteger(v)&&v>0),'PROJECTION_CACHE_DTYPE');
    const value=a.dtype==='<f4'?new Float32Array(data.slice(end,end+a.length)):new Uint8Array(data.slice(end,end+a.length));
    fail(value.length===a.shape.reduce((x,y)=>x*y,1),'PROJECTION_CACHE_SHAPE');
    for(const x of value)fail(Number.isFinite(x),'PROJECTION_CACHE_FINITE');
    arrays[a.name]=value;end+=a.length;
   }
   fail(end===data.byteLength&&arrays.base.length===m.width*m.height*3&&arrays.alpha.length===m.width*m.height,'PROJECTION_CACHE_LAYOUT');
   const result=new Projection();Object.assign(result,{health,meta:m,base:arrays.base,alpha:arrays.alpha});
   result.layers=m.boxes.map(([y0,y1,x0,x1],i)=>{
    fail([y0,y1,x0,x1].every(Number.isSafeInteger)&&y0>=0&&y0<y1&&y1<=m.height&&x0>=0&&x0<x1&&x1<=m.width,'PROJECTION_CACHE_BOX');
    const weight=arrays['weight'+i];fail(weight?.length===(y1-y0)*(x1-x0),'PROJECTION_CACHE_WEIGHT_SHAPE');
    for(const x of weight)fail(x>=0&&x<=1,'PROJECTION_CACHE_WEIGHT');
    return {y0,y1,x0,x1,weight};
   });
   result.work=new Float32Array(result.base.length);result.pixels=new Uint8ClampedArray(m.width*m.height*4);
   for(let i=0;i<result.alpha.length;i++)result.pixels[i*4+3]=result.alpha[i];
   return result;
  }
  static async load(health){
   fail(health.projection_cache.url==='/api/competition-live/cache','PROJECTION_CACHE_LOCAL_URL');
   const response=await fetch(health.projection_cache.url);if(!response.ok)throw Error('PROJECTION_CACHE_HTTP_'+response.status);
   return Projection.decode(await response.arrayBuffer(),health);
  }
  async render(p,requestID){
   const begin=performance.now(),h=this.health,types=h.expected_binding.types,encoding=h.color_encoding,M=encoding.intensity_domain[1];
   fail(p.spatial.values.length===5768&&p.spatial.map_sha256===h.projection_cache.upstream_map_sha256,'PROJECTION_SPATIAL_MAP');
   const means=types.map((_,i)=>{let sum=0;for(let j=i*721;j<(i+1)*721;j++){const v=p.spatial.values[j];fail(Number.isFinite(v),'PROJECTION_ACTIVITY_FINITE');sum+=v;}return sum/721;});
   const brightness=means.map(v=>.25+.75*Math.pow(Math.min(1,Math.abs(v)/M),.45));
   const colors=types.map((t,i)=>[1,3,5].map(k=>Math.fround(parseInt(encoding.palette[t].slice(k,k+2),16)/255*brightness[i])));
   this.work.set(this.base);const f=Math.fround,w=this.meta.width;
   for(let i=0;i<8;i++){
    const l=this.layers[i],c=colors[i].map(x=>f(x*255));let q=0;
    for(let y=l.y0;y<l.y1;y++)for(let x=l.x0;x<l.x1;x++){
     const weight=l.weight[q++];if(!weight)continue;const index=(y*w+x)*3;
     this.work[index]=f(this.work[index]+f(weight*c[0]));this.work[index+1]=f(this.work[index+1]+f(weight*c[1]));this.work[index+2]=f(this.work[index+2]+f(weight*c[2]));
    }
   }
   for(let i=0,j=0;i<this.work.length;i+=3,j+=4){this.pixels[j]=Math.max(0,Math.min(255,Math.floor(f(this.work[i]+.5))));this.pixels[j+1]=Math.max(0,Math.min(255,Math.floor(f(this.work[i+1]+.5))));this.pixels[j+2]=Math.max(0,Math.min(255,Math.floor(f(this.work[i+2]+.5))));}
   const pixels=new Uint8ClampedArray(this.pixels),rawSHA=await sha(pixels),elapsed=performance.now()-begin;
   const receipt={...Object.fromEntries(['run_id','session_id','serial','step_id','state_token','activity_time_s','input_time_s'].map(k=>[k,p[k]])),
    request_id:requestID,service_id:h.service_id,means,types,color_encoding:encoding,
    type_states:types.map((type,i)=>({type,value:means[i],activity_signed:means[i],brightness_factor:brightness[i],saturated:Math.abs(means[i])>M})),
    source_sequence:p.source.sequence,spatial_values_sha256:p.spatial.values_sha256,upstream_map_sha256:p.spatial.map_sha256,
    rendering_method:'fixed_SWCs_CPU_projection_composite',fixed_cpu_projection_sha256:h.fixed_cpu_projection_sha256,
    projection_cache_sha256:h.projection_cache.sha256,raw_sha256:rawSHA,total_render_raw_ms:elapsed,
    PL_execution:false,source_evidence_level:p.evidence_level,source_code_sha256:h.source_code_sha256};
   return {receipt,pixels,width:this.meta.width,height:this.meta.height,composeMs:elapsed};
  }
 }
 window.FlyVisFixedSkeleton=Projection;
})();
