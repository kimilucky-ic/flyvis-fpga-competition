# Human-run, exact Jupyter Shutdown. No killall, signal, FPGA load/reset/MMIO/DMA.
# Preserve current PID20446/kernel7be4...; never rerun an initialization cell here.
import json
import os
from pathlib import Path
from ipykernel.connect import get_connection_file
from IPython.display import Javascript, display

assert os.getpid() == 20446, '当前PID已变化，停止；未关闭任何内核'
assert Path(get_connection_file()).name == 'kernel-7be4b7e7-8afb-4c32-a1d6-090a4ccb28a1.json', '当前内核已变化，停止'
assert 'line2_fresh_initialized' not in globals(), '当前已存在初始化对象，先保留现场；未关闭内核'
assert not any(n.endswith('_service_instance') and hasattr(v, 'driver') for n,v in list(globals().items())), '当前已有板端服务，停止'
target_proc = Path('/proc/18092')
if not target_proc.exists():
    print('FLYVIS_KERNEL_CLOSE ' + json.dumps(dict(status='TARGET_ALREADY_ABSENT_READ_ONLY', target_pid=18092, current_pid=os.getpid())))
else:
    target_args = (target_proc/'cmdline').read_bytes().split(b'\0')
    target_status = dict(line.split(':',1) for line in (target_proc/'status').read_text().splitlines() if ':' in line)
    assert int(target_status['PPid'].strip()) == 415, '目标父进程变化，停止'
    assert any(a in (b'ipykernel_launcher',b'ipykernel_launcher.py') or a.endswith(b'/ipykernel_launcher.py') for a in target_args), '目标进程类型变化，停止'
    assert any(a.endswith(b'kernel-8b653b8e-22a4-4c6c-87b3-2992def6e543.json') for a in target_args), '目标PID身份变化，停止'
    display(Javascript(r'''
(async () => {
 const out=element[0]||element;
 const CURRENT='7be4b7e7-8afb-4c32-a1d6-090a4ccb28a1',TARGET='8b653b8e-22a4-4c6c-87b3-2992def6e543';
 const show=v=>out.textContent='FLYVIS_KERNEL_CLOSE '+JSON.stringify(v);
 try {
  const nb=window.Jupyter&&window.Jupyter.notebook;
  if(!nb||!nb.kernel||nb.kernel.id!==CURRENT||CURRENT===TARGET)throw Error('CURRENT_NOTEBOOK_IDENTITY_CHANGED');
  const base=nb.base_url||document.body.getAttribute('data-base-url');
  if(typeof base!=='string'||!base.startsWith('/')||base.startsWith('//'))throw Error('JUPYTER_BASE_URL_UNAVAILABLE');
  const api=new URL(base.replace(/\/?$/,'/')+'api/',window.location.href);
  if(api.origin!==window.location.origin)throw Error('CROSS_ORIGIN_REFUSED');
  const cookie=document.cookie.split(';').map(s=>s.trim()).find(s=>s.startsWith('_xsrf='));
  if(!cookie)throw Error('XSRF_COOKIE_UNAVAILABLE');
  const xsrf=decodeURIComponent(cookie.slice(6)),url=new URL('kernels/'+TARGET,api);
  const once=async(method,address=url)=>{const control=new AbortController(),timer=setTimeout(()=>control.abort(),15000);
   try{return await fetch(address.href,{method,credentials:'same-origin',headers:{'X-XSRFToken':xsrf},signal:control.signal});}
   finally{clearTimeout(timer);}};
  const before=await once('GET');
  if(before.status===404){show({status:'TARGET_NOT_REGISTERED_NO_SHUTDOWN',target_kernel:TARGET,current_kernel:CURRENT});return;}
  if(before.status!==200)throw Error('KERNEL_LOOKUP_HTTP_'+before.status);
  const model=await before.json();
  if(model.id!==TARGET)throw Error('TARGET_KERNEL_IDENTITY_CHANGED');
  if(model.execution_state!=='idle')throw Error('TARGET_NOT_IDLE_'+model.execution_state);
  const sessionsReply=await once('GET',new URL('sessions',api));
  if(sessionsReply.status!==200)throw Error('SESSION_LOOKUP_HTTP_'+sessionsReply.status);
  const sessions=await sessionsReply.json();
  if(!Array.isArray(sessions))throw Error('SESSION_REPLY_INVALID');
  const names=sessions.filter(s=>s.kernel?.id===TARGET).map(s=>s.path||s.notebook?.path||'(无文件名)');
  const name=names.join('、')||'当前服务登记了内核，但没有Notebook会话映射';
  out.textContent='PID18092：'+name+'；Jupyter状态idle。等待你确认任务已经结束。';
  if(!window.confirm('仅关闭 PID18092 / 内核8b653b8e…\nNotebook：'+name+'\nidle并不保证板端后台线程已结束。\n请仅在你确认它的任务已结束、允许关闭时点确定。\n当前20446保留；不加载或复位FPGA。')){
   show({status:'CANCELLED_NO_SHUTDOWN',target_kernel:TARGET,current_kernel:CURRENT});return;
  }
  // Recheck the exact registered target immediately before its ONE DELETE.
  const checked=await once('GET');
  if(checked.status!==200)throw Error('TARGET_CHANGED_BEFORE_SHUTDOWN');
  const latest=await checked.json();
  if(latest.id!==TARGET||latest.execution_state!=='idle')throw Error('TARGET_BECAME_BUSY_OR_CHANGED');
  const ended=await once('DELETE');
  if(ended.status!==204)throw Error('KERNEL_SHUTDOWN_HTTP_'+ended.status);
  const after=await once('GET');
  if(after.status!==404)throw Error('KERNEL_REMOVAL_NOT_CONFIRMED_HTTP_'+after.status);
  show({status:'JUPYTER_KERNEL_SHUTDOWN_CONFIRMED',target_pid:18092,target_kernel:TARGET,current_pid:20446,current_kernel:CURRENT,
   direct_FPGA_operations:0,note:'Normal kernel exit may release resources owned by that kernel; no board-ready claim.'});
 } catch(error){show({status:'STOP_NO_RETRY',error:error.message,target_kernel:TARGET,current_kernel:CURRENT});}
})();
'''))
