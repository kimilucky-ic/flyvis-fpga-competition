"""Optional explicit native checker; compilation only via authorized prepare/test.
No PYNQ import, MMIO, cache manipulation or hardware commands.
"""
from pathlib import Path
import ctypes,hashlib,json,platform,shutil,struct,subprocess
ABI=0x12110001
class PayloadChecker:
    def __init__(self,library):
        self.lib=ctypes.CDLL(str(Path(library).resolve()))
        abi=self.lib.line11_payload_abi;abi.argtypes=[];abi.restype=ctypes.c_uint32
        if abi()!=ABI:raise RuntimeError('native payload ABI mismatch')
        self.fn=self.lib.line11_payload_check
        self.fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint32)]
        self.fn.restype=ctypes.c_int
    def __call__(self,raw):
        if type(raw) is not bytes or len(raw)!=188416:raise ValueError('exact immutable record required')
        result=(ctypes.c_uint32*3)()
        if self.fn(ctypes.c_char_p(raw),len(raw),result)!=0:raise RuntimeError('native payload failure')
        return tuple(result)
    def self_test(self):
        def reference(blob):
            h=0;bad=0
            for i,(w,) in enumerate(struct.iter_unpack('<I',blob)):
                h=(((h<<1)|(h>>31)) ^ w ^ i)&0xffffffff
                bad|=(w&0x7f800000)==0x7f800000
            return h,int(bad)
        raw=bytearray(188416)
        for off,w in ((128,0x3f000000),(128+720*4,0x80000000),(4096,1),(4096+45668*4,0x7f7fffff)):
            struct.pack_into('<I',raw,off,w)
        for nonfinite in (False,True):
            if nonfinite:struct.pack_into('<I',raw,4096+123*4,0x7fc12345)
            blob=bytes(raw);a,ab=reference(blob[128:3012]);b,bb=reference(blob[4096:186772])
            if self(blob)!=(a,b,ab|bb):raise RuntimeError('native self-test mismatch')
        return dict(status='PASS_STARTUP_SYNTHETIC_CHECK_ONLY',cases=2,abi=ABI)

def build_checker(output,*,authorized=False,compiler=None):
    if not authorized:raise RuntimeError('native build not authorized')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    cc=compiler or shutil.which('cc') or shutil.which('gcc')
    if not cc:raise RuntimeError('native C compiler unavailable; no fallback')
    source=Path(__file__).with_name('payload_check.c')
    library=out/('payload_check.dll' if platform.system()=='Windows' else 'payload_check.so')
    cmd=[str(cc),'-std=c99','-shared','-O2','-Wall','-Wextra','-Werror']
    cmd+=['-static-libgcc'] if platform.system()=='Windows' else ['-fPIC']
    cmd += [str(source),'-o',str(library)]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    (out/'compile.log').write_bytes(result.stdout);result.check_returncode()
    checker=PayloadChecker(library);check=checker.self_test()
    identity=dict(command=cmd,machine=platform.machine(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),library_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),self_test=check,scope='payload checks only; no neural computation')
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    return checker,identity
