# USER MANUAL ACTION: normal Jupyter Shutdown of exactly the ended extra kernel.
# Keep current START_DDR / PID14354. No FPGA programming/reset/neural operation.
import json
import os
from pathlib import Path
from ipykernel.connect import get_connection_file
from IPython.display import Javascript, display

assert os.getpid() == 14354, 'Current PID changed; stop'
assert Path(get_connection_file()).name == 'kernel-6d2164da-ea0c-4ba0-9a53-78d12155a98b.json', 'Current kernel changed; stop'
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip() == '444b7e27-5868-4454-af51-dd62b69c3212', 'Board boot changed; stop'
assert 'line2_fresh_initialized' not in globals(), 'Current initialization state changed; stop'
assert 'line2_init_root' in globals() and not (Path(line2_init_root)/'INITIALIZATION_ATTEMPT.json').exists(), 'Initialization already attempted or context lost; stop'
line2_extra_proc = Path('/proc/15160/cmdline')
if not line2_extra_proc.exists():
    print('LINE2_EXTRA_KERNEL_SHUTDOWN ' + json.dumps(dict(status='TARGET_PROCESS_ALREADY_ABSENT_READ_ONLY',current_pid=os.getpid(),target_pid=15160)))
else:
    line2_extra_args = line2_extra_proc.read_bytes().split(b'\0')
    assert any(b'ipykernel_launcher' in a for a in line2_extra_args) and any(a.endswith(b'kernel-7f9bb52c-5add-480b-b15d-2a4b30a6b634.json') for a in line2_extra_args), 'Extra PID identity changed; stop'
    display(Javascript(r'''
(async () => {
 const out=element[0]||element;
 const CURRENT='6d2164da-ea0c-4ba0-9a53-78d12155a98b',TARGET='7f9bb52c-5add-480b-b15d-2a4b30a6b634';
 const show=v=>out.textContent='LINE2_EXTRA_KERNEL_SHUTDOWN '+JSON.stringify(v);
 try {
  const nb=window.Jupyter&&window.Jupyter.notebook;
  if(!nb||!nb.kernel||nb.kernel.id!==CURRENT||CURRENT===TARGET)throw Error('CURRENT_NOTEBOOK_IDENTITY_CHANGED');
  const base=nb.base_url||(document.body&&document.body.getAttribute('data-base-url'));
  if(typeof base!=='string'||!base.startsWith('/')||base.startsWith('//'))throw Error('JUPYTER_BASE_URL_UNAVAILABLE');
  const url=new URL(base.replace(/\/?$/,'/')+'api/kernels/'+encodeURIComponent(TARGET),window.location.href);
  if(url.origin!==window.location.origin)throw Error('CROSS_ORIGIN_REFUSED');
  const cookie=document.cookie.split(';').map(s=>s.trim()).find(s=>s.startsWith('_xsrf='));
  if(!cookie)throw Error('XSRF_COOKIE_UNAVAILABLE');
  const xsrf=decodeURIComponent(cookie.slice(6));
  const once=async(method)=>{const control=new AbortController(),timer=setTimeout(()=>control.abort(),20000);
   try{return await fetch(url.href,{method,credentials:'same-origin',headers:{'X-XSRFToken':xsrf},signal:control.signal});}
   finally{clearTimeout(timer);}};
  out.textContent='正在核对额外内核7f9bb52c…，当前START_DDR保持运行';
  const before=await once('GET');
  if(before.status===404){show({status:'TARGET_NOT_REGISTERED_NO_SHUTDOWN',target_kernel:TARGET,current_kernel:CURRENT});return;}
  if(before.status!==200)throw Error('KERNEL_LOOKUP_HTTP_'+before.status);
  const model=await before.json();
  if(model.id!==TARGET)throw Error('TARGET_KERNEL_IDENTITY_CHANGED');
  out.textContent='正在通过Jupyter正常关闭额外内核7f9bb52c…，不操作FPGA';
  const ended=await once('DELETE');
  if(ended.status!==204)throw Error('KERNEL_SHUTDOWN_HTTP_'+ended.status);
  const after=await once('GET');
  if(after.status!==404)throw Error('KERNEL_REMOVAL_NOT_CONFIRMED_HTTP_'+after.status);
  show({status:'JUPYTER_KERNEL_SHUTDOWN_CONFIRMED',target_kernel:TARGET,current_kernel:CURRENT,FPGA_operations:0});
 } catch(error) {show({status:'STOP_NO_RETRY',error:error.message,target_kernel:TARGET,current_kernel:CURRENT});}
})();
'''))
