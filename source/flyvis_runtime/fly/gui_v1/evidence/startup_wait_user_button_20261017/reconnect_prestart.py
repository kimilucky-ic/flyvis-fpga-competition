"""Manual software clock reattachment of the still-unused current service.

No overlay, MMIO, DMA, load, reset, allocation, STEP, START or COMMIT call.
The existing scope end is never extended. Old proof remains in the journal.
"""
import json,sys,time,urllib.request

def reconnect(bundle,service,expected_run,request=None):
    c=service.config;d=service.driver
    def clean():
        assert c['run_id']==expected_run and bundle.driver is d and bundle.config==c,'RECONNECT_IDENTITY'
        assert service.state=='BOARD_PREPARED' and service.error is None and service.identity is None,'RECONNECT_NOT_PRESTART'
        assert d.requests==d.commits==0 and d.pending is None and not d.poisoned and not d.committed,'RECONNECT_ACTIVITY'
        assert service.connections==0 and not service.inflight and service.listener is service.connection is service.neural_thread is None,'RECONNECT_CONNECTION'
        assert service.thread.is_alive() and not d.evidence.journal.closed,'RECONNECT_SERVICE_CLOSED'
    with service.lock:
        clean();old=service.clock_guard;prior=old.receipt(c)
    m=sys.modules[type(old).__module__]
    if request is None:
        ep=c['pc_authority_endpoint']
        def request(path,packet):
            req=urllib.request.Request('http://'+ep['host']+':'+str(ep['port'])+path,
                data=json.dumps(packet).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=4) as response:raw=response.read(65537)
            assert len(raw)<=65536,'RECONNECT_RESPONSE_BOUND'
            return json.loads(raw)
    handshake=m.BoardClockHandshake(c)
    clock=handshake.accept(request('/clock',handshake.challenge()))
    receipt=clock.receipt(c)
    assert clock.fixed==old.fixed and receipt['pc_clock_id']!=prior['pc_clock_id'],'RECONNECT_SCOPE_OR_NEW_PC'
    record=dict(schema='flyvis-prestart-PC-reconnect/v1',run_id=expected_run,
        prior_clock=prior,new_clock=receipt,scope_end_unchanged=c['end_utc'],requests=0,commits=0,
        new_loads=0,new_resets=0,new_allocations=0,MMIO=0,DMA=0)
    with service.lock:
        clean();assert service.clock_guard is old,'RECONNECT_CHANGED'
        old.check(c);clock.check(c)
        d.evidence.journal.add('PC_PRESTART_RECONNECT.json',json.dumps(record,sort_keys=True).encode())
        d.evidence.journal.checkpoint('PC_PRESTART_RECONNECT')
        service.clock_guard=bundle.clock_guard=d.clock_guard=clock
        service.clock_receipt=receipt
        service.idle_deadline=min(service.idle_deadline,time.monotonic()+clock.remaining_s(c))
        d.session_deadline=min(d.session_deadline,service.idle_deadline)
        packet=m.sign(dict(schema='flyvis-camera-retained-prepared/v1',binding=clock.fixed,
            preparation_receipt=bundle.receipt,clock_receipt=receipt,status=service.status('00'*16),
            PC_prestart_reconnect=record),c['control_key'])
    ack=m.verified(request('/prepared',packet),c['control_key'])
    assert ack.get('ok') is True and ack['binding']==clock.fixed,'RECONNECT_PC_ACK'
    print('CAMERA_BOARD_PREPARED same run; PC reconnected; 0 MMIO/DMA/START/COMMIT',flush=True)

