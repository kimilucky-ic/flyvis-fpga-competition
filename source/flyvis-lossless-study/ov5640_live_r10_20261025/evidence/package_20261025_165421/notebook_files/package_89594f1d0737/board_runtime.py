"""Operator-only concrete PYNQ binding; import does not access hardware."""
import hashlib,importlib,platform,time
import step_profile as prof
from pathlib import Path
from camera_diagnostic import CallTiming,source_inventory,source_excerpts
from capture_binding import save_json
from official_bridge import start_official
from ddr_control import DdrControl,BASE
from camera_memory import CameraMemory
from ddr_memory import OwnedDdr,pynq_allocator_and_barrier
from official_iic21 import register_official_iic21
from ps_preflight import inspect as inspect_hp

DRIVER_SHA={
 'pynq.lib.iic':'f1f9bd414aa027d5f9ddfd7a8468e91c0972f8fa7166dee0bb6eb75914e08991',
 'pynq.lib.ov5640.ov5640':'4657ba5aff963c847f5397cdc28672211ef7a36fb1802c38b749fb1e44e7b172',
 'pynq.lib.video2lcd':'98d57467e452272cd234279789bdb5549e7854025abbdfb798de15e0bb19d0fe'}

def clocks(raw):
    pll=int(raw['IO_PLL_CTRL'])
    if pll&0x1b or not int(raw['PLL_STATUS'])&4:raise RuntimeError('IO PLL not normal/locked; no clock writes')
    fdiv=(pll>>12)&127
    results={}
    for name in ('FPGA0_CLK_CTRL','FPGA1_CLK_CTRL'):
        value=int(raw[name]);d0=(value>>8)&63;d1=(value>>20)&63
        if ((value>>4)&3)!=0 or not d0 or not d1:raise RuntimeError('Unexpected FCLK source/dividers')
        mhz=33.333333*fdiv/d0/d1
        if abs(mhz-100)>0.01:raise RuntimeError('Nominal FCLK is not100MHz; no clock writes')
        results[name]=mhz
    return results

class CheckedVideo:
    def init__(self,video,memory,barrier,out,diagnostics=False):
        self.video,self.memory,self.barrier,self.out=video,memory,barrier,Path(out)
        self.held=None;self.readout_count=0;self.diagnostics=diagnostics
    def readframe(self):
        t=prof.tick()
        if self.diagnostics and self.readout_count in (4,16):
            diagnostic=CallTiming();f=diagnostic.call(self.video.readframe)
            # Keep timing scope separate; writes occur after call returns.
            call_report=diagnostic.report()
        else:f=self.video.readframe();call_report=None
        self.held=f
        prof.add('camera_vendor_readframe',t)
        if call_report is not None:save_json(self.out/('CAMERA_CALLTREE_%06d.json'%self.readout_count),call_report,durable=False)
        t=prof.tick()
        start=int(f.physical_address);end=start+int(f.nbytes)
        name='CAMERA_BUFFER.json' if self.readout_count==0 else 'CAMERA_BUFFER_%06d.json'%self.readout_count
        prof.add('camera_buffer_metadata',t);t=prof.tick()
        if prof.ENABLED:
            save_json(self.out/name,dict(address=start,bytes=int(f.nbytes),coherent=bool(f.coherent),
                neural_base=self.memory.base,neural_bytes=self.memory.size,calltree_profiled=call_report is not None),durable=False)
        prof.add('camera_buffer_record',t);t=prof.tick()
        if start<0x100000 or end>0x40000000 or not (end<=self.memory.base or start>=self.memory.base+self.memory.size):
            raise RuntimeError('Camera buffer outside DDR or overlaps neural allocation')
        if f.coherent is not False or not f.flags.c_contiguous:raise RuntimeError('Unexpected camera cache/layout')
        prof.add('camera_ownership_checks',t);t=prof.tick()
        self.barrier();prof.add('camera_barrier_before',t);t=prof.tick()
        f.invalidate();prof.add('camera_cache_invalidate',t);t=prof.tick()
        self.barrier();prof.add('camera_barrier_after',t)
        self.readout_count+=1
        return f
    def close(self):
        self.video.close();self.held=None
        if getattr(self,'allocation_binding',None) is not None:self.allocation_binding.close()

class PynqRuntime:
    evidence='OPERATOR_PHYSICAL_RUN_UNATTESTED'
    def init__(self,root,out):
        self.root,self.out=Path(root),Path(out);self.owner={};self.pages={}
    def prepare(self):
        if platform.machine()!='armv7l':raise RuntimeError('ARMv7 Zynq required')
        if b'xlnx,zynq-7000' not in Path('/proc/device-tree/compatible').read_bytes():raise RuntimeError('Not Zynq7000')
        self.pynq=importlib.import_module('pynq')
        if not self.pynq.__version__.startswith('2.7.'):raise RuntimeError('PYNQ2.7 required')
        modules={};ident={}
        for name,expected in DRIVER_SHA.items():
            m=importlib.import_module(name);p=Path(m.__file__);sha=hashlib.sha256(p.read_bytes()).hexdigest()
            ident[name]=dict(path=str(p),sha256=sha)
            if sha!=expected:raise RuntimeError('Official driver baseline differs: '+name)
            modules[name]=m
        for parent in {Path(m.__file__).parent for m in modules.values()}:
            for p in sorted(parent.iterdir()):
                if p.is_file() and p.suffix in ('.py','.so'):
                    ident[str(p)]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pinned=False)
        save_json(self.out/'DRIVERS.json',ident)
        if getattr(self,'camera_diagnostics',False):
            sources=source_inventory(Path(modules['pynq.lib.video2lcd'].__file__).parent)
            save_json(self.out/'VIDEO_DRIVER_SOURCE.json',sources)
            save_json(self.out/'VIDEO_DRIVER_EXCERPTS.json',source_excerpts(sources))
        self.AxiIIC=register_official_iic21(modules['pynq.lib.iic'].AxiIIC)
        self.OV5640=modules['pynq.lib.ov5640.ov5640'].OV5640
        self.VideoMode=modules['pynq.lib.video2lcd'].VideoMode
        self.allocate,self.barrier=pynq_allocator_and_barrier(self.out/'native',operator_authorized=True)
    def load(self):
        ol=self.pynq.Overlay(str(self.root/'flyvis_official.bit'),download=False)
        self.owner['overlay']=ol;ol.download()
    def read(self,address):
        base=address&~4095
        if base not in self.pages:self.pages[base]=self.pynq.MMIO(base,4096)
        return int(self.pages[base].read(address-base))
    def inspect(self):
        raw={n:self.read(a) for n,a in [('IO_PLL_CTRL',0xf8000108),('PLL_STATUS',0xf800010c),('FPGA0_CLK_CTRL',0xf8000170),('FPGA1_CLK_CTRL',0xf8000180)]}
        save_json(self.out/'CLOCK.json',dict(raw=raw,reference_MHz=33.333333,
            pynq_reported_MHz=float(self.pynq.Clocks.fclk0_mhz),evidence='REGISTER_DERIVED_NOMINAL_NOT_MEASURED'))
        mhz=clocks(raw);hp=inspect_hp(self.read);save_json(self.out/'HP_WIDTH.json',hp)
        if not hp['HP0_HP1_64bit_verified']:raise RuntimeError('HP0/HP1 not64bit and released')
        return mhz
    def control(self):
        mmio=self.pynq.MMIO(BASE,4096)
        if not mmio.device.has_capability('MEMORY_MAPPED') or getattr(mmio.write,'__name__',None)!='write_mm':
            raise RuntimeError('bulk input requires memory-mapped official MMIO write_mm')
        c=DdrControl(mmio,bulk_input=True);self.owner['control']=c;return c
    def memory(self,slots=1):
        m=OwnedDdr(self.allocate,self.barrier,slots);self.owner['memory']=m;return m
    def start_camera(self,memory):
        ol=self.owner['overlay'];self.owner['video']=ol.video.video_in
        def bind(video):
            import inspect
            source=Path(inspect.getfile(type(video._vdma.readchannel)))
            if hashlib.sha256(source.read_bytes()).hexdigest()!='bb6e6e073819d0c813207556aaba39d35b94e98e0a3c7e90fb6558980a0ac2dc':
                raise RuntimeError('video driver differs from accepted R9; no adaptation')
            fix=CameraMemory(video._vdma.readchannel);self.owner['camera_memory']=fix
            save_json(self.out/'CAMERA_MEMORY_BINDING.json',fix.summary())
        sensor,video=start_official(ol,self.AxiIIC,self.OV5640,self.VideoMode,bind_cache=bind)
        self.owner['sensor']=sensor
        checked=CheckedVideo(video,memory,self.barrier,self.out,diagnostics=getattr(self,'camera_diagnostics',False));checked.allocation_binding=self.owner['camera_memory'];self.owner['checked_video']=checked
        return checked
