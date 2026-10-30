/* One page, distinct presentation/input/run identities. No camera or compute start. */
(() => {
  const el=id=>document.getElementById(id);
  let session=null,caps=null,busy=false,requestToken=0;
  async function api(path,body){const r=await fetch(path,{cache:'no-store',...(body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})});const value=await r.json();return {ok:r.ok,value};}
  function identity(name,value){const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value==null?'NOT_AVAILABLE':typeof value==='object'?JSON.stringify(value):String(value);row.append(dt,dd);el('flowIdentity').append(row);}
  function render(){
    if(!session)return;const ref=session.input_reference,ready=Boolean(ref),digital=session.source_kind==='digital_verified_p0';
    el('flowSource').value=session.source_kind;el('flowSource').disabled=busy;el('flowPresenter').disabled=busy||!caps?.presentation.url;el('flowMode').disabled=busy;
    el('flowState').textContent=`${session.state} · ${digital?'已验收数字输入':session.source_kind==='phone_camera'?'手机刺激实际相机采集':'交互数字预览'}`;
    el('flowCamera').classList.toggle('hidden',session.source_kind!=='phone_camera');
    el('flowInput').disabled=!digital||busy;el('flowFreeze').disabled=!digital||busy||!el('flowInput').value;el('flowSubmit').disabled=!ready||busy;el('flowReplay').disabled=!ready||busy;
    el('flowTask').textContent=`新任务：${session.backend_status} · job_id：${session.job_id||'NOT_AVAILABLE'} · run_id：${session.run_id||'NOT_AVAILABLE'} · 真板：NOT_CONNECTED`;
    el('flowNotice').textContent=session.error||(ready?'输入身份已冻结；可查看同身份的历史实际计算。请求新计算需要正式后端；不会生成新曲线。':digital?'冻结引用已验收的原始 800×721 输入及文件 SHA256；不会改写或重新生成数据。':'播放器只提供软件预览。新 721 输入／真实相机冻结包未提供，当前不关联旧神经活动。');
    const stage=ready?session.state==='WAITING_COMPUTE'?2:1:0;Array.from(el('flowSteps').children).forEach((x,i)=>{if(i===stage)x.setAttribute('aria-current','step');else x.removeAttribute('aria-current');});
    el('flowIdentity').replaceChildren();identity('输入来源',session.source_kind);identity('GUI选择会话',session.session_id);identity('选择版本',session.revision);identity('输入引用（非run）',ref?.reference_id);identity('原comparison_id',ref?.comparison_id);identity('手机presentation_id',ref?.presentation_id);identity('新采集／新推理',ref?{new_capture:ref.new_capture,new_inference:ref.new_inference}:null);identity('输入／初态／模型SHA',ref?.identity_fingerprint);identity('输入时间范围',ref?.input_time_s);identity('Euler后时间范围',ref?.activity_time_s);identity('参考文件SHA',ref?.reference_sha256);identity('原始数据目录',ref?.source_directory);identity('当前所选计算模式',el('flowMode').value);
    identity('最近软件预览（未绑定输入）',caps?.presentation.latest_software_presentation?.presentation_id);identity('预览播放状态（非采集）',caps?.presentation.latest_software_presentation?.state);identity('预览参数SHA（非输入SHA）',caps?.presentation.latest_software_presentation?.settings_sha256);identity('真实采集状态',caps?.camera.status);identity('新相机input_id',caps?.camera.input_id);identity('新采集帧／721映射',null);
  }
  async function action(name,fields={}){
    if(!session||busy)return;busy=true;render();const mine=++requestToken;
    try{const {value}=await api(`/api/flow/sessions/${session.session_id}/${name}`,{revision:session.revision,...fields});if(mine!==requestToken)return;if(value.session_id)session=value;else throw new Error(value.error||'未知响应');render();if(value.error)el('flowNotice').textContent=value.error;}
    catch(e){el('flowNotice').textContent='NOT_AVAILABLE · '+e.message;}finally{busy=false;render();}
  }
  function cameraReference(){const selector=el('dataset');if(!Array.from(selector.options).some(o=>o.value==='camera1'))return;selector.value='camera1';selector.dispatchEvent(new Event('change',{bubbles:true}));el('flowNotice').textContent='下方为已验收的历史摄像头样例及721映射 · offline replay；不是本次手机新采集。';selector.scrollIntoView({behavior:'smooth',block:'center'});}
  el('flowSource').onchange=async()=>{await action('select',{source_kind:el('flowSource').value});el('flowPlayer').removeAttribute('src');el('flowPlayerBox').classList.add('hidden');window.dispatchEvent(new CustomEvent('flyvis-flow-input-changed'));};
  el('flowInput').onchange=async()=>{await action('select',{source_kind:'digital_verified_p0'});window.dispatchEvent(new CustomEvent('flyvis-flow-input-changed'));};
  el('flowMode').onchange=render;
  el('flowFreeze').onclick=()=>action('freeze',{comparison_id:el('flowInput').value});
  el('flowSubmit').onclick=()=>action('submit',{reference_id:session?.input_reference?.reference_id,mode:el('flowMode').value});
  el('flowReplay').onclick=()=>{const ref=session?.input_reference;if(!ref)return;window.dispatchEvent(new CustomEvent('flyvis-workbench-open',{detail:{comparison_id:ref.comparison_id,mode:el('flowMode').value}}));el('evidenceWorkbench').scrollIntoView({behavior:'smooth',block:'start'});};
  el('flowPresenter').onclick=async()=>{if(!caps?.presentation.url)return;await action('select',{source_kind:el('flowSource').value==='phone_camera'?'phone_camera':'interactive_digital'});el('flowSource').value=session.source_kind;window.dispatchEvent(new CustomEvent('flyvis-flow-input-changed'));el('flowPlayerBox').classList.remove('hidden');if(!el('flowPlayer').getAttribute('src'))el('flowPlayer').src=caps.presentation.url;};
  el('flowCameraReference').onclick=cameraReference;
  el('flowRefresh').onclick=async()=>{try{const response=await api('/api/flow');if(!response.ok)throw new Error(response.value.error);caps=response.value;render();}catch(e){el('flowNotice').textContent='NOT_AVAILABLE · '+e.message;}};
  const initialize=async()=>{try{const status=await api('/api/flow');if(!status.ok)throw new Error(status.value.error);caps=status.value;el('flowPresenter').disabled=!caps.presentation.url;el('flowInput').replaceChildren();for(const input of caps.verified_p0){const o=document.createElement('option');o.value=input.comparison_id;o.textContent=input.title;el('flowInput').append(o);}const created=await api('/api/flow/sessions',{});if(!created.ok)throw new Error(created.value.error);session=created.value;render();}catch(e){el('flowState').textContent='NOT_AVAILABLE';el('flowNotice').textContent=e.message+'；原55条件与P0仍可用。';el('flowFreeze').disabled=el('flowPresenter').disabled=true;}};
  if(window.FlyVisStartup)FlyVisStartup.onPanel('flowPanel',initialize);else initialize();
})();
