"""PC-owned transport/storage adapters; no device creation or neural arithmetic.

The pinned v2 Client and JournalWriter remain unchanged. All byte checks,
deadlines, durable checkpoints and poison behavior still belong to them.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import socket

from live_protocol import require,sha
from joint_diagnostics import NONE

TRANSPORT='TCP_NODELAY_QUICKACK_WHEN_SUPPORTED/v1'
STORAGE='WSL_NATIVE_DURABLE_EXPORT/v1'


class LowLatencySocket:
    def init__(self,sock,diagnostics=NONE):
        self.socket=sock;self.diagnostics=diagnostics
        self.bytes_sent=self.bytes_received=self.send_calls=self.receive_calls=0
        self.quickack_calls=0
        self.quickack=hasattr(socket,'TCP_QUICKACK')
        sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        require(sock.getsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY)==1,'JOINT_NODELAY_NOT_APPLIED')
    def __getattr__(self,name):return getattr(self.socket,name)
    def sendall(self,data):
        self.diagnostics.call('wire.socket_sendall',self.socket.sendall,data)
        self.bytes_sent+=len(data);self.send_calls+=1
    def recv(self,n):
        data=self.diagnostics.call('wire.socket_receive_wait',self.socket.recv,n)
        self.bytes_received+=len(data);self.receive_calls+=1
        if data and self.quickack:
            try:
                self.socket.setsockopt(socket.IPPROTO_TCP,socket.TCP_QUICKACK,1)
                self.quickack_calls+=1
            except OSError as error:
                if error.errno not in (errno.ENOPROTOOPT,errno.EINVAL,errno.ENOTSUP):raise
                self.quickack=False
        return data
    def summary(self):
        return dict(policy=TRANSPORT,TCP_NODELAY=1,TCP_QUICKACK_available=self.quickack,
            quickack_calls=self.quickack_calls,send_calls=self.send_calls,receive_calls=self.receive_calls,
            bytes_sent=self.bytes_sent,bytes_received=self.bytes_received,
            scope='POST_ATTESTATION_SOCKET_ONLY_NO_PROTOCOL_OR_DEADLINE_CHANGE')


def tune_client(client,diagnostics=NONE):
    require(client.sock is not None and not client.poisoned and client.pending is None,'JOINT_SOCKET_NOT_CLEAN')
    require(not isinstance(client.sock,LowLatencySocket),'JOINT_SOCKET_ALREADY_TUNED')
    try:client.sock=LowLatencySocket(client.sock,diagnostics)
    except BaseException:
        client.poisoned=True;client.close();raise
    return client.sock


def sync_directory(path):
    fd=os.open(str(path),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


class NativePCJournal:
    """Same synchronous journal on WSL disk; verified export only after close.

    Native source is retained on success and failure. Export failure cannot be
    promoted to a clean result; no return to direct Windows writes mid-run.
    """
    def init__(self,root,run_id,session_id,*,diagnostics=NONE,native_base=None):
        require(os.name=='posix','NATIVE_JOURNAL_REQUIRES_WSL')
        require(all(re.fullmatch('[a-f0-9]{32}',v) for v in (run_id,session_id)),'NATIVE_JOURNAL_IDENTITY')
        self.root=Path(root);self.diagnostics=diagnostics
        base=Path(native_base) if native_base is not None else Path.home()/'.local/state/flyvis/joint'
        require(base.is_absolute() and base.resolve().parts[1:2]!=('mnt',),'NATIVE_JOURNAL_MUST_BE_NATIVE_PATH')
        self.session=base/session_id
        self.session.mkdir(parents=True,exist_ok=False)
        sync_directory(self.session.parent)
        self.directory=self.session/'pc';self.source=self.directory/'evidence.fvej'
        self.writer=None;self.export_attempted=False
        self.identity=dict(policy=STORAGE,run_id=run_id,session_id=session_id,native_path=str(self.source),
            export_path=str(self.root/'pc/evidence.fvej'),source_retained=True,
            durability='ORIGINAL_CHECKPOINT_FSYNC_ON_WSL_FILESYSTEM; NO_POWER_LOSS_TEST_CLAIM')
        marker=self.root/'PC_JOURNAL_LOCATION.json'
        with marker.open('x',encoding='utf8') as f:
            json.dump(self.identity,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        sync_directory(self.root)

    def attach(self,writer):
        require(self.writer is None and Path(writer.path)==self.source,'NATIVE_JOURNAL_WRITER_PATH')
        self.writer=writer

    def export_closed(self):
        require(not self.export_attempted,'NATIVE_JOURNAL_EXPORT_ALREADY_ATTEMPTED')
        self.export_attempted=True
        require(self.writer is not None and self.writer.closed,'NATIVE_JOURNAL_NOT_CLOSED')
        destination=self.root/'pc'
        destination.mkdir(exist_ok=False)
        partial=destination/'evidence.fvej.partial';final=destination/'evidence.fvej'
        with self.diagnostics.measure('PC_journal.export_closed_copy'):
            checksum=hashlib.sha256();size=0
            with self.source.open('rb') as src,partial.open('xb') as dst:
                for block in iter(lambda:src.read(1024*1024),b''):
                    require(dst.write(block)==len(block),'NATIVE_JOURNAL_EXPORT_SHORT_WRITE')
                    checksum.update(block);size+=len(block)
                dst.flush();os.fsync(dst.fileno())
            require(sha(self.source)==checksum.hexdigest() and sha(partial)==checksum.hexdigest(),'NATIVE_JOURNAL_EXPORT_SHA')
            os.replace(partial,final);sync_directory(destination);sync_directory(self.root)
        return dict(self.identity,status='EXPORTED_CLOSED_BYTES_SHA_VERIFIED',bytes=size,sha256=checksum.hexdigest(),
            writer_poisoned=self.writer.poisoned,journal_acceptance='PENDING_INDEPENDENT_PC_PS_AUDIT')
