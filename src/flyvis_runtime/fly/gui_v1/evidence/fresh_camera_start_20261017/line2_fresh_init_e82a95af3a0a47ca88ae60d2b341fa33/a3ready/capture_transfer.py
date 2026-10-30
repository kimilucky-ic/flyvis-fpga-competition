"""Original bounded capture retrieval after an authenticated normal CLOSE."""
import base64,hashlib
from .control2 import require
CHUNK=1024*1024
def handle_capture(service,path,body):
    journal=service.evidence.journal
    require(service.state=='FINISHED_PENDING_AUDIT' and journal.closed,'CAPTURE_NOT_COMPLETE')
    file=journal.path
    if path=='/evidence_begin':
        require(not hasattr(service,'capture_cursor'),'CAPTURE_ALREADY_BEGUN')
        size=file.stat().st_size;require(0<size<=512*1024*1024,'CAPTURE_SIZE')
        service.capture_cursor=0;service.capture_size=size;digest=hashlib.sha256()
        with file.open('rb') as stream:
            for block in iter(lambda:stream.read(CHUNK),b''):digest.update(block)
        service.capture_sha=digest.hexdigest()
        require(service.capture_sha==service.finish_receipt['PS_capture_sha256'],'FINISHED_CAPTURE_CHANGED')
        return dict(capture_bytes=size,capture_sha256=service.capture_sha,chunk_bytes=CHUNK)
    require(path=='/evidence_chunk' and hasattr(service,'capture_cursor'),'BEGIN_REQUIRED')
    offset=body.get('offset');require(type(offset) is int and offset==service.capture_cursor<service.capture_size,'CAPTURE_ORDER')
    require(file.stat().st_size==service.capture_size,'CAPTURE_CHANGED')
    count=min(CHUNK,service.capture_size-offset);service.capture_cursor+=count
    with file.open('rb') as stream:stream.seek(offset);data=stream.read(count)
    require(len(data)==count,'CAPTURE_SHORT')
    return dict(offset=offset,bytes=count,capture_bytes=service.capture_size,chunk_sha256=hashlib.sha256(data).hexdigest(),data_b64=base64.b64encode(data).decode('ascii'))
