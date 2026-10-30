"""CPU-only actual saved Python wrapper with fake native library, no PYNQ IO."""
from pathlib import Path
from types import ModuleType,SimpleNamespace as NS
import sys,importlib.util,json,hashlib
import numpy as np
root=Path(__file__).resolve().parent
from official_iic21 import register_official_iic21
source=root.parent/'ov5640_official_flyvis_20261024/baseline/pynq_lib_iic.py'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='f1f9bd414aa027d5f9ddfd7a8468e91c0972f8fa7166dee0bb6eb75914e08991'
class FakeIP:
 def init__(self,description):self.description=description;self.mmio=NS(array=np.zeros(512,np.uint32))
pynq=ModuleType('pynq');pynq.DefaultIP=FakeIP;sys.modules['pynq']=pynq
spec=importlib.util.spec_from_file_location('saved_vendor_iic',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Native:
 def init__(self):self.calls=[];self.fail=False
 def XIic_Send(self,*args):self.calls.append(('send',args));return 0 if self.fail else args[3]
 def XIic_Recv(self,*args):self.calls.append(('recv',args));return 0 if self.fail else args[3]
 def XIic_WaitBusFree(self,*args):self.calls.append(('wait',args));return int(self.fail)
n=Native();m.AxiIIC._lib=n
cls=register_official_iic21(m.AxiIIC)
for name in ['init__','send','receive','wait','_initialise_lib']:
 assert getattr(cls,name) is getattr(m.AxiIIC,name),name
obj=cls({'type':'xilinx.com:ip:axi_iic:2.1','phys_addr':0x41600000})
assert obj.send(0x3c,b'\x30\x08\x82',3)==3
buf=bytearray(1);assert obj.receive(0x3c,buf,1)==1;obj.wait()
assert n.calls[0][1][1:]==(0x3c,b'\x30\x08\x82',3,0)
assert n.calls[1][1][1:]==(0x3c,buf,1,0)
n.fail=True
for f in [lambda:obj.send(0x3c,b'\x30',1),lambda:obj.receive(0x3c,buf,1),obj.wait]:
 try:f()
 except RuntimeError:pass
 else:raise AssertionError('vendor failure did not propagate')
assert m.AxiIIC.bindto==['xilinx.com:ip:axi_iic:2.0']
assert cls.bindto==['xilinx.com:ip:axi_iic:2.1']
try:register_official_iic21(cls)
except ValueError:pass
else:raise AssertionError('unknown base accepted')
result=dict(status='PASS_CPU_VENDOR_WRAPPER_ABI_AND_INHERITANCE_ONLY',methods_overridden=0,old_registration_preserved=True,send_receive_wait_and_errors=True,
 source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),board_operations=0,native_library_executed=False,physical_IIC_verified=False,
 limitation='Fake native library, not ARM/MMIO/SCCB proof; does not use ignore_version=True')
(root/'evidence/IIC_DRIVER_CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
