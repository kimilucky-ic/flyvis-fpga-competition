"""Checked PYNQ 2.7 AxiIIC API adapter. No imports or construction of hardware.

Deadline checks detect late returns; they cannot interrupt blocking vendor C.
Read pointer uses STOP then START, matching supplied vendor SCCB implementation.
"""
import threading
import time

class SensorIic:
    def init__(self, axi_iic, timeout=.1, clock=time.monotonic):
        if timeout<=0: raise ValueError('positive deadline required')
        self.bus,self.timeout,self.clock=axi_iic,timeout,clock
        self.failed=False
        self.lock=threading.Lock()

    def _call(self, fn, *args):
        start=self.clock()
        result=fn(*args)
        if self.clock()-start>self.timeout: raise TimeoutError('late IIC return; reconcile without retry')
        return result

    def _send(self, payload):
        if self._call(self.bus.send,0x3c,bytearray(payload),len(payload),0)!=len(payload):
            raise RuntimeError('short IIC send')
        self._call(self.bus.wait)

    def _transaction(self, register, value=None):
        if type(register) is not int or not 0<=register<=65535: raise ValueError('16 bit register required')
        if value is not None and (type(value) is not int or not 0<=value<=255): raise ValueError('8 bit data required')
        with self.lock:
            if self.failed: raise RuntimeError('failed IIC session; no retry')
            try:
                address=[register>>8,register&255]
                if value is not None:
                    self._send(address+[value]);return True
                self._send(address)
                data=bytearray(1)
                if self._call(self.bus.receive,0x3c,data,1,0)!=1: raise RuntimeError('short IIC receive')
                self._call(self.bus.wait)
                return data[0]
            except BaseException:
                self.failed=True
                raise

    def read16(self,register): return self._transaction(register)
    def write16(self,register,value): return self._transaction(register,value)
