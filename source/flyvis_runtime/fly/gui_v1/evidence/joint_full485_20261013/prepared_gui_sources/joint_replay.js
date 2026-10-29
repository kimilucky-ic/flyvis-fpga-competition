'use strict';
(() => {
 const $=id=>document.getElementById(id),base='/api/hybrid/full485';
 const view=new FlyVisSpatialView('jointSpatial');let info=null,arrays=null,k=240,playing=false,recording=false,trace=[],generation=0;
 const pause=()=>{playing=false;$('jointPlay').textContent='播放离线结果';};
 async function json(url){const r=await fetch(url),j=await r.json();if(!r.ok)throw Error(j.error||j.status);return j;}
 async function binary(name,metadata){const r=await fetch(`${base}/${name}.bin?run=${metadata.run_id}`);if(!r.ok)throw Error('结果读取失败');const bytes=await r.arrayBuffer(),v=new Float32Array(bytes),pin=metadata.arrays[name];
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  if(hash!==pin.sha256||v.length!==pin.shape.reduce((a,b)=>a*b)||v.some(x=>!Number.isFinite(x)))throw Error('数组身份或维度不符');return v;}
 function field(id,isFlow){const el=$(id),c=el.getContext('2d'),w=el.width,h=el.height,s=7.2;c.fillStyle='#09121e';c.fillRect(0,0,w,h);
  info.coordinates_uv.forEach(([u,v],i)=>{const x=w/2+1.5*v*s,y=h/2+Math.sqrt(3)*(u+v/2)*s;c.beginPath();
   if(!isFlow){for(let j=0;j<6;j++){const a=j*Math.PI/3,px=x+Math.cos(a)*s*.98,py=y+Math.sin(a)*s*.98;j?c.lineTo(px,py):c.moveTo(px,py);}c.closePath();const q=Math.round(arrays.input[k*721+i]*255);c.fillStyle=`rgb(${q},${q},${q})`;c.fill();}
   else{const dx=arrays.flow[(k*2)*721+i]*8,dy=-arrays.flow[(k*2+1)*721+i]*8,angle=Math.atan2(dy,dx),head=Math.min(3,Math.hypot(dx,dy)*.4);c.strokeStyle='#6bded0';c.lineWidth=1;c.moveTo(x,y);c.lineTo(x+dx,y+dy);c.lineTo(x+dx-head*Math.cos(angle-.5),y+dy-head*Math.sin(angle-.5));c.moveTo(x+dx,y+dy);c.lineTo(x+dx-head*Math.cos(angle+.5),y+dy-head*Math.sin(angle+.5));c.stroke();}
  });c.font='17px sans-serif';c.fillStyle='#a9c4d1';c.fillText(isFlow?'Official DecoderGAVP | raw optical flow':'ON60 | original frozen 721 inputs',20,28);
 }
 function sample(step){return {run_id:info.run_id,step_id:step,state_token:step+1,activity_time_s:info.rows[step].activity_time_s,mode:'OFFLINE_REPLAY',map_sha256:info.spatial_metadata.map_sha256,
  acceptance_sha256:info.acceptance_sha256,values:arrays.spatial.subarray(step*5768,(step+1)*5768),layers:{FPGA_status:'NOT_CONNECTED',PL_proven_global_ids:info.PL_proven_global_ids,disabled_global_ids:[],release_blocked_global_ids:[],software_replaced_global_ids:[]}};}
 function render(){if(!info||!arrays)return;const row=info.rows[k];field('jointInput',false);field('jointFlow',true);view.accept(sample(k));$('jointStep').value=k;
  $('jointTime').textContent=`k${k}/484 · 输入 ${row.input_time_s.toFixed(3)} s → 活动 ${row.activity_time_s.toFixed(3)} s`;
  $('jointEvidence').textContent=`历史实体 PL：5768节点 | core ${row.core_cycles} cycles | adapter ${row.adapter_cycles} cycles | ${row.commit} | COMMIT ${row.unified_commit_sha.slice(0,16)}`;
  $('jointTiming').textContent=`当步实际耗时 ${(row.step_wall_ns/1e9).toFixed(3)} s；整次计算 ${info.compute_total_s.toFixed(2)} s。当前显示 OFFLINE REPLAY，当前板端 NOT_CONNECTED。`;
  $('jointExperiment').dataset.run=info.run_id;$('jointExperiment').dataset.step=k;$('jointExperiment').dataset.commit=row.unified_commit_sha;
 }
 async function load(){const token=++generation;pause();info=arrays=null;view.clear();$('jointView').classList.add('hidden');$('jointUnavailable').textContent='核验指定验收包、原始数组 SHA256 与每步身份…';
  try{const metadata=await json(base);if(metadata.status!=='VERIFIED_ACTUAL_JOINT_OFFLINE_REPLAY'||metadata.display_mode!=='OFFLINE_REPLAY'||metadata.steps!==485||metadata.FPGA_status!=='NOT_CONNECTED')throw Error('联合证据等级不符');
   const [input,spatial,flow]=await Promise.all(['input','spatial','flow'].map(name=>binary(name,metadata)));if(token!==generation)return;info=metadata;arrays={input,spatial,flow};view.setMetadata(info.spatial_metadata);view.admitOfflineProof(info);
   view.rows=Array.from({length:485},(_,step)=>sample(step));view.lastRun=info.run_id;view.selected=info.spatial_metadata.nodes.findIndex(n=>n.type==='T5c'&&n.u===0&&n.v===0);
   $('jointView').classList.remove('hidden');$('jointUnavailable').textContent='已核验真实485步 GPU–FPGA 结果 · OFFLINE REPLAY · 当前 NOT_CONNECTED';
   $('jointIdentity').textContent=JSON.stringify({...info,rows:undefined,spatial_metadata:undefined},null,2);render();
  }catch(e){if(token!==generation)return;info=arrays=null;view.clear();$('jointView').classList.add('hidden');$('jointUnavailable').textContent=`NOT_AVAILABLE · ${e.message} · 不显示未通过验收的活动`;}
 }
 async function tick(){while(playing){await new Promise(r=>setTimeout(r,50));if(!playing)break;k=Math.min(484,k+1);render();if(k===484)pause();}}
 function composite(){const c=$('jointRecordCanvas').getContext('2d');c.fillStyle='#07101b';c.fillRect(0,0,1600,1000);c.fillStyle='#eff6ff';c.font='bold 30px sans-serif';c.fillText('FlyVis | actual GPU + physical FPGA | ON60',30,42);
  c.font='20px sans-serif';c.fillStyle='#ffcc80';c.fillText('OFFLINE REPLAY | 0.1x model time | NOT a live FPGA stream',30,78);
  c.drawImage($('jointInput'),25,102,550,336);c.drawImage($('jointFlow'),595,102,550,336);c.fillStyle='#b7cddd';c.font='18px sans-serif';
  const r=info.rows[k];['GPU: chemical_H + R 39901','Physical PL: H 5768','Original full state: 45669',`step ${k} / 484 | token ${k+1}`,`input ${r.input_time_s.toFixed(3)} s`,`activity ${r.activity_time_s.toFixed(3)} s`,`PL core: ${r.core_cycles} cycles`,`adapter: ${r.adapter_cycles} cycles`,'COMMIT ACK matched',`Q24 integer error: 0`].forEach((t,i)=>c.fillText(t,1165,127+i*28));
  view.mini.forEach((m,i)=>{const x=24+(i%4)*390,y=470+Math.floor(i/4)*228;c.font='bold 19px sans-serif';c.fillStyle='#d9f1f2';c.fillText(m.typ,x+125,y-5);c.drawImage(m.canvas,x+44,y,280,206);});
  c.font='15px monospace';c.fillStyle='#92b8cc';c.fillText(`run ${info.run_id} | commit ${r.unified_commit_sha}`,24,958);c.fillText(`signed activity +/- ${view.$('limit').value} | no interpolated neuron values | actual compute ${info.compute_total_s.toFixed(2)} s`,24,983);
 }
 async function record(){if(!info||recording)return;pause();recording=true;$('jointRecord').disabled=$('jointPlay').disabled=$('jointStep').disabled=$('jointLoad').disabled=true;trace=[];
  let stream,recorder;
  try{const type=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(t=>MediaRecorder.isTypeSupported(t));if(!type)throw Error('WebM recorder unavailable');
   stream=$('jointRecordCanvas').captureStream(0);const track=stream.getVideoTracks()[0],chunks=[];recorder=new MediaRecorder(stream,{mimeType:type,videoBitsPerSecond:6000000});recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};const done=new Promise((resolve,reject)=>{recorder.onstop=resolve;recorder.onerror=e=>reject(Error(e.error?.message||'recording error'));});recorder.start();
   for(k=0;k<485;k++){if(document.hidden)throw Error('录制页面被隐藏；停止，不伪造完整视频');render();composite();track.requestFrame();trace.push({step:k,commit:info.rows[k].unified_commit_sha,browser_draw_ms:performance.now()});$('jointRecording').textContent=`录制实际离线帧 ${k+1}/485`;await new Promise(r=>setTimeout(r,50));}
   k=484;recorder.stop();await done;const body=new Blob(chunks,{type:'video/webm'}),response=await fetch(`${base}/recording?run=${info.run_id}`,{method:'POST',headers:{'Content-Type':'video/webm'},body});const receipt=await response.json();if(!response.ok)throw Error(receipt.error||'视频保存失败');
   $('jointRecording').textContent=`已保存实际离线视频：${receipt.path} | SHA256 ${receipt.sha256}`;window.flyvisJointRecording={receipt,trace};
  }catch(e){$('jointRecording').textContent=`NOT_COMPLETE · ${e.message}`;if(recorder?.state==='recording')recorder.stop();}
  finally{stream?.getTracks().forEach(t=>t.stop());recording=false;k=Math.min(484,k);$('jointRecord').disabled=$('jointPlay').disabled=$('jointStep').disabled=$('jointLoad').disabled=false;}
 }
 $('jointLoad').addEventListener('click',load);$('jointStep').addEventListener('input',()=>{pause();k=Number($('jointStep').value);render();});$('jointPlay').addEventListener('click',()=>{if(!arrays)return;if(playing){pause();return;}if(k===484)k=0;playing=true;$('jointPlay').textContent='暂停离线回放';tick();});$('jointRecord').addEventListener('click',record);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
})();
