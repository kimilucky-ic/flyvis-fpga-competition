"""Conservative recovery of an orphaned managed launch; no device/process starts."""
from contextlib import contextmanager
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import time
import uuid

from live_protocol import HERE,load,require,sha,utc,write


def process_alive(pid):
    require(type(pid) is int and pid>0,'LAUNCH_PROCESS_ID')
    if os.name!='nt':
        try:os.kill(pid,0)
        except ProcessLookupError:return False
        return True
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
    kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x100000|0x1000,False,pid)
    if not handle:
        error=ctypes.get_last_error()
        if error==87:return False
        raise ctypes.WinError(error)
    try:
        status=kernel.WaitForSingleObject(handle,0)
        require(status in (0,258),'LAUNCH_PROCESS_STATUS_UNKNOWN')
        return status==258
    finally:kernel.CloseHandle(handle)


def gui_port_available():
    # Bind without listen/connect: no server, request, or firewall-dependent wait.
    with socket.socket() as probe:
        if os.name=='nt':probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        try:probe.bind(('127.0.0.1',8771))
        except OSError as error:
            raise ValueError('8771端口不可用；请关闭原FlyVis窗口后重试。未启动新GPU任务。') from error
    return True


@contextmanager
def launch_guard():
    """One managed launcher per workspace; OS releases the mutex on a crash."""
    if os.name!='nt':
        # Native desktop is Windows only. Tests call pure inspection functions.
        yield;return
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateMutexW.argtypes=[ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR]
    kernel.CreateMutexW.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
    kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.ReleaseMutex.argtypes=[wintypes.HANDLE];kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    name='Local\\FlyVisManagedLauncher_'+hashlib.sha256(str(HERE).lower().encode()).hexdigest()[:24]
    handle=kernel.CreateMutexW(None,False,name)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    acquired=False
    try:
        status=kernel.WaitForSingleObject(handle,0)
        require(status in (0,0x80,258),'LAUNCH_MUTEX_STATUS_UNKNOWN')
        require(status!=258,'FlyVis启动器仍在运行；请先关闭原窗口。没有启动第二个GPU任务。')
        acquired=True;yield
    finally:
        if acquired:kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


def inspect_stale_launch(active,*,base=None,alive=process_alive,port_free=gui_port_available,now=None):
    active=Path(active);base=Path(base or HERE/'runtime/live').resolve()
    if not active.exists():return None
    raw=active.read_bytes();original_digest=hashlib.sha256(raw).hexdigest();state=json.loads(raw.decode('utf-8-sig'))
    if state['state'] in ('STOPPED','START_FAILED'):return None
    sid=state['session_id'];require(re.fullmatch('[a-f0-9]{32}',sid) is not None,'RECOVERY_SESSION_ID')
    root=Path(state['root']).resolve()
    require(root.parent==base and root.name==sid,'RECOVERY_WRITE_SCOPE')
    session=load(root/'session.json');require(session['session_id']==sid,'RECOVERY_SESSION_IDENTITY')
    require(type(state.get('gpu_enabled')) is bool and session.get('gpu_enabled') is state['gpu_enabled'],'RECOVERY_GPU_SCOPE_IDENTITY')
    controller=load(root/'controller.json')
    require(controller['session_id']==sid and controller['pid']==state['pid'],'RECOVERY_CONTROLLER_IDENTITY')
    age=(time.time() if now is None else now)-controller['unix_time']
    require(age>30,'原FlyVis启动器仍有新心跳；请先关闭原窗口。')
    children=state.get('children',[]);require(isinstance(children,list),'RECOVERY_CHILDREN_SCHEMA')
    ids=[state['pid']]+[child['pid'] for child in children]
    require(all(type(pid) is int and pid>0 for pid in ids) and len(ids)==len(set(ids)),'RECOVERY_PROCESS_IDS')
    require(all(not alive(pid) for pid in ids),'原FlyVis进程仍在运行；请先关闭原窗口。')
    proof={}
    if state.get('gpu_enabled'):
        beat=load(root/'heartbeat.json');exit_info=load(root/'worker_exit.json');release=load(root/'worker_shutdown.json')
        require(beat['session_id']==sid and beat['state']=='STOPPED' and beat.get('device') is None
                and not beat.get('error'),'RECOVERY_GPU_FINAL_STATE_UNKNOWN')
        require(exit_info['session_id']==sid and exit_info['exit_code']==0,'RECOVERY_WORKER_EXIT_UNKNOWN')
        require(release.get('CUDA_synchronized') is True and release.get('shared_lock_closed') is True,'RECOVERY_CUDA_RELEASE_UNKNOWN')
        proof={n:sha(root/n) for n in ('heartbeat.json','worker_exit.json','worker_shutdown.json')}
    require(port_free() is True,'RECOVERY_PORT_UNKNOWN')
    require(sha(active)==original_digest,'RECOVERY_MARKER_CHANGED')
    return dict(session_id=sid,root=str(root),original_marker_sha256=original_digest,original_state=state['state'],
        absent_pids=ids,controller_age_s=age,gpu_release_sha256=proof,port_8771_available=True,
        device_operations=0,processes_killed=0)


def recover_stale_launch(active,**checks):
    """Caller holds launch_guard. Never converts unknown release into STOPPED."""
    proof=inspect_stale_launch(active,**checks)
    if proof is None:return None
    active=Path(active);state=load(active);root=Path(proof['root'])
    require(sha(active)==proof['original_marker_sha256'],'RECOVERY_MARKER_CHANGED')
    backup=root/'launcher_recovery'/uuid.uuid4().hex;backup.mkdir(parents=True,exist_ok=False)
    (backup/'demo_active.before.json').write_bytes(active.read_bytes())
    write(backup/'recovery.json',dict(proof,recovered_utc=utc(),exit_codes_not_observed='UNKNOWN'))
    require(sha(active)==proof['original_marker_sha256'],'RECOVERY_MARKER_CHANGED')
    state.update(state='STOPPED',recovered_utc=utc(),recovery_reason='ORPHANED_LAUNCH_ALL_PROCESSES_GONE_GPU_RELEASE_VERIFIED',
        recovery_evidence=str(backup/'recovery.json'))
    write(active,state)
    return proof
