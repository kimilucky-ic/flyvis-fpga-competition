"""Bounded offline preparation; no PYNQ creation or runnable board entrypoint.
Caller supplies admitted bridge and display mailbox. Every step persists first.
"""
from snapshot_records import decode_record
from cycle_contract import check_cycles
from capture_binding import save_json

def next_committed_frame(bridge,latest):
    descriptor=bridge.step()
    verdict=check_cycles(descriptor.cycles)
    directory=bridge.output/'bound'/('%06d'%descriptor.frame_id)
    save_json(directory/'CYCLE_CHECK.json',verdict)
    if not verdict['matches']:
        bridge.failed=True;bridge.control.failed=True
        save_json(directory/'IN_DOUBT.json',dict(reason='cycle mismatch',actual=descriptor.cycles,automatic_retry=False))
        raise RuntimeError('DDR core-phase cycles actual=%s expected=%s'%(descriptor.cycles,verdict['expected_cycles']))
    # LatestDisplay publishes only an immutable, already durable complete record.
    # It neither invokes nor waits for a renderer; old display frames may be skipped.
    record=decode_record((directory/'record.bin').read_bytes(),descriptor.frame_id)
    latest.publish(record)
    return descriptor
