"""Graphics-only resource policy. Does not import or launch neural computation."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path


def process_names():
    if os.name!='nt':return set()
    class Entry(ctypes.Structure):
        _fields_=[('size',wintypes.DWORD),('usage',wintypes.DWORD),('pid',wintypes.DWORD),
                  ('heap',ctypes.c_size_t),('module',wintypes.DWORD),('threads',wintypes.DWORD),
                  ('parent',wintypes.DWORD),('priority',wintypes.LONG),('flags',wintypes.DWORD),('exe',wintypes.WCHAR*260)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
    kernel.Process32FirstW.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.CreateToolhelp32Snapshot(2,0)
    if handle==ctypes.c_void_p(-1).value:raise OSError('Cannot read process table')
    names=set();row=Entry();row.size=ctypes.sizeof(row)
    try:
        ok=kernel.Process32FirstW(handle,ctypes.byref(row))
        while ok:
            names.add(row.exe.lower());ok=kernel.Process32NextW(handle,ctypes.byref(row))
    finally:kernel.CloseHandle(handle)
    return names


def busy_reasons(root,names=None):
    reasons=[]
    folder=Path(root).parent/'fpga/flyvis-autorunner/runtime'
    for name in ('EXTERNAL_GPU_BUSY.json','RESOURCE_QUARANTINE.json','BOARD_RESERVED.json'):
        if (folder/name).exists():reasons.append('resource marker: '+name)
    try:
        for name in sorted((process_names() if names is None else names)&{'wsl.exe','vivado.exe','vitis.exe'}):
            reasons.append('reserved process: '+name)
    except OSError:reasons.append('resource status unavailable; conservative CPU graphics')
    return reasons


def presentation_policy(profile='light',busy=False):
    if profile not in ('light','standard'):raise ValueError('Unknown presentation profile')
    if busy:
        return dict(profile='light',renderer='cpu',width=640,height=400,max_fps=2,step_stride=25,
                    background_rois=True,background_style='simplified_mesh',degraded=True,reason='COMPUTE_PRIORITY_KEYFRAMES')
    if profile=='light':
        return dict(profile='light',renderer='cpu',width=800,height=500,max_fps=10,step_stride=5,
                    background_rois=True,background_style='simplified_mesh',degraded=False,reason='LIGHT_OFFLINE_GRAPHICS')
    return dict(profile='standard',renderer='gpu',width=880,height=520,max_fps=15,step_stride=1,
                background_rois=True,background_style='full_mesh',degraded=False,reason='STANDARD_GRAPHICS_YIELDS_TO_COMPUTE')
