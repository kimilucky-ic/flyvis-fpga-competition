"""Read-only physical/commit headroom and actual Windows hard-page input rates.

GetPerformanceInfo gives system commit, not pagefile size. PDH Pages Input/sec
counts hard-fault disk reads (also memory-mapped files), not just swap traffic.
"""
import ctypes as C
from ctypes import wintypes as W

class PerformanceInfo(C.Structure):
    _fields_=[('cb',W.DWORD)]+[(n,C.c_size_t) for n in (
        'CommitTotal','CommitLimit','CommitPeak','PhysicalTotal','PhysicalAvailable',
        'SystemCache','KernelTotal','KernelPaged','KernelNonpaged','PageSize')]+[
        ('HandleCount',W.DWORD),('ProcessCount',W.DWORD),('ThreadCount',W.DWORD)]
class CounterValue(C.Structure):
    _fields_=[('status',W.DWORD),('value',C.c_double)]
class HostMemory:
    def init__(self):
        self.psapi=C.WinDLL('psapi',use_last_error=True)
        self.psapi.GetPerformanceInfo.argtypes=[C.POINTER(PerformanceInfo),W.DWORD]
        self.psapi.GetPerformanceInfo.restype=W.BOOL
        self.pdh=C.WinDLL('pdh');self.query=C.c_void_p();self.counters={}
        self.pdh.PdhOpenQueryW.argtypes=[W.LPCWSTR,C.c_size_t,C.POINTER(C.c_void_p)]
        self.pdh.PdhAddEnglishCounterW.argtypes=[C.c_void_p,W.LPCWSTR,C.c_size_t,C.POINTER(C.c_void_p)]
        self.pdh.PdhCollectQueryData.argtypes=[C.c_void_p]
        self.pdh.PdhGetFormattedCounterValue.argtypes=[C.c_void_p,W.DWORD,C.c_void_p,C.POINTER(CounterValue)]
        self.pdh.PdhCloseQuery.argtypes=[C.c_void_p]
        self._check(self.pdh.PdhOpenQueryW(None,0,C.byref(self.query)))
        for key,path in [('pages_input_per_sec',r'\Memory\Pages Input/sec'),('page_reads_per_sec',r'\Memory\Page Reads/sec')]:
            counter=C.c_void_p();self._check(self.pdh.PdhAddEnglishCounterW(self.query,path,0,C.byref(counter)))
            self.counters[key]=counter
        self._check(self.pdh.PdhCollectQueryData(self.query))
    @staticmethod
    def _check(code):
        if code!=0:raise OSError(f'Windows performance counter error 0x{code&0xffffffff:08x}')
    def sample(self):
        pi=PerformanceInfo();pi.cb=C.sizeof(pi)
        if not self.psapi.GetPerformanceInfo(C.byref(pi),pi.cb):raise C.WinError(C.get_last_error())
        scale=pi.PageSize/2**20
        result=dict(available_MiB=pi.PhysicalAvailable*scale,total_MiB=pi.PhysicalTotal*scale,
            commit_headroom_MiB=(pi.CommitLimit-pi.CommitTotal)*scale,commit_used_MiB=pi.CommitTotal*scale,
            commit_limit_MiB=pi.CommitLimit*scale)
        self._check(self.pdh.PdhCollectQueryData(self.query))
        for key,counter in self.counters.items():
            value=CounterValue();code=self.pdh.PdhGetFormattedCounterValue(counter,0x200,None,C.byref(value))
            self._check(code)
            if value.status not in (0,1):raise OSError(f'Invalid {key} counter status: {value.status}')
            result[key]=value.value
        return result
    def close(self):
        if self.query.value:self.pdh.PdhCloseQuery(self.query);self.query=C.c_void_p()

def pressure_reason(sample,elapsed,slow_samples_seconds):
    if sample['available_MiB']<1024:return 'AVAILABLE_PHYSICAL_BELOW_1024_MIB'
    if sample['commit_headroom_MiB']<2048:return 'COMMIT_HEADROOM_BELOW_2048_MIB'
    if slow_samples_seconds>=3:return 'SUSTAINED_HARD_PAGING_WITH_LOW_MEMORY'
    if elapsed>=600:return 'WALL_BUDGET_600_SECONDS'
    return None
