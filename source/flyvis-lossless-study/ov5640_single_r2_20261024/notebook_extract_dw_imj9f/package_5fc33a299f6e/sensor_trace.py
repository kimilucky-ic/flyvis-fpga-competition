"""Bounded sensor transaction summaries; no extra diagnostic MMIO."""
import time
from bounded_io import Iic
class SensorBus(Iic):
    def init__(self,mmio,**kwargs):
        super().init__(mmio,**kwargs)
        self.operations=[];self.current=None;self.last_register_reads={};self.mmio=mmio
        self.io=self
    def read(self,offset):
        start=time.monotonic_ns()
        value=int(self.mmio.read(offset))
        self.last_register_reads[hex(offset)]=dict(value=value,start_ns=start,end_ns=time.monotonic_ns())
        return value
    def write(self,offset,value):return self.mmio.write(offset,value)
    def transaction(self,reg,value=None):
        event=dict(index=len(self.operations),operation='read' if value is None else 'write',sensor_register=hex(reg),write_value=value,start_ns=time.monotonic_ns())
        self.current=event
        try:
            result=super().transaction(reg,value)
            event['result']=result;return result
        except BaseException as exc:
            event['error']=repr(exc);raise
        finally:
            event['end_ns']=time.monotonic_ns()
            event['last_register_reads']=dict(self.last_register_reads)
            self.operations.append(event)
    def report(self):
        return dict(transport_revision='IIC21_R2',operations=self.operations,failed=self.failed,
          configuration_write_attempts=sum(e['operation']=='write' for e in self.operations),
          note='Host monotonic timing, sequential last reads; no extra post-failure MMIO; not waveform evidence')
