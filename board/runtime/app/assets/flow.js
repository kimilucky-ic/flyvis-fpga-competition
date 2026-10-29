/* Official decoder readout only: no estimated arrows from labels or images. */
const FlowUI=(()=>{
 const MODEL='ecb7bcd5a47e64900fe27ca4cd5f980099c4877e8aaab5581ad510bebe11c216';
 const CK='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f';
 const check=(ok,msg)=>{if(!ok)throw Error(msg);};
 async function decode(p){
  const f=p.flow;if(!f||f.status!=='READY')return {ready:false,reason:'光流未就绪；不影响神经状态显示'};
  check(f.schema==='line11-official-flow/v1'&&f.decoder_sha256===MODEL&&f.checkpoint_sha256===CK,'光流模型不符');
  check(f.step_id===p.step_id&&f.state_sha256===p.state_token,'光流与输入步号不符');
  check(JSON.stringify(f.axes)==='["right_positive","up_positive"]','光流坐标不符');
  check(Array.isArray(f.values)&&f.values.length===2&&f.values.every(a=>Array.isArray(a)&&a.length===721&&a.every(Number.isFinite)),'光流数据无效');
  const b=new ArrayBuffer(2*721*4),view=new DataView(b);f.values.flat().forEach((x,i)=>view.setFloat32(i*4,x,true));
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('');check(hash===f.values_sha256,'光流校验不符');
  return {ready:true,values:f.values,step:p.step_id,state:p.state_token,decode_ms:f.decode_ms};
 }
 function vector(x,y,scale){const n=Math.hypot(x,y),gain=Math.min(3,24/Math.max(n,1e-9));return [x*gain*scale,-y*gain*scale];}
 function start(){const canvas=document.getElementById('flowCanvas'),caption=document.getElementById('flowCaption');let saved=null;
  function draw(){const w=canvas.width=Math.max(100,canvas.clientWidth),h=canvas.height=Math.max(100,canvas.clientHeight),ctx=canvas.getContext('2d');ctx.clearRect(0,0,w,h);if(!saved)return;
   const {f,image}=saved;if(!f.ready){caption.textContent=f.reason;canvas.dataset.step='';return;}
   const size=Math.min(w,h),left=(w-size)/2,top=(h-size)/2,scale=size/417;ctx.globalAlpha=.4;ctx.drawImage(image,left,top,size,size);ctx.globalAlpha=1;ctx.lineWidth=1.5;let count=0;
   HeatmapUI.xy.forEach(([px,py],i)=>{const v=Math.round((px-208)/13),u=Math.round((py-208)/13-v/2);if(u%3||v%3)return;
    const x=left+px*scale,y=top+py*scale,dxdy=vector(f.values[0][i],f.values[1][i],scale),dx=dxdy[0],dy=dxdy[1],n=Math.hypot(dx,dy);ctx.fillStyle='#7ef5d3';ctx.strokeStyle='#7ef5d3';
    if(n<1.5){ctx.beginPath();ctx.arc(x,y,1,0,Math.PI*2);ctx.fill();return;}
    const a=Math.atan2(dy,dx),head=Math.min(5,n*.5);ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+dx,y+dy);ctx.moveTo(x+dx-head*Math.cos(a-.55),y+dy-head*Math.sin(a-.55));ctx.lineTo(x+dx,y+dy);ctx.lineTo(x+dx-head*Math.cos(a+.55),y+dy-head*Math.sin(a+.55));ctx.stroke();count++;
   });
   canvas.dataset.step=String(f.step);canvas.dataset.state=f.state;canvas.dataset.arrowCount=String(count);
   caption.textContent='第'+(f.step+1)+'步 · PC官方解码 '+f.decode_ms.toFixed(2)+' ms · 箭头表示估计方向，速度未标定';
  }
  window.addEventListener('resize',draw);return {set:(p,f,image)=>{if(f.ready)check(f.step===p.step_id&&f.state===p.state_token,'光流绘制身份不符');saved={f,image};draw();}};
 }
 return {decode,vector,start,MODEL};
})();
if(typeof module!=='undefined')module.exports=FlowUI;
