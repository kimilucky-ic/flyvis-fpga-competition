# Run manually in a NEW cell in the ORIGINAL retained PYNQ notebook.
# Pure Python object inspection: no network, PYNQ import, register/DMA or start.
import sys, json
camera_check_module = sys.modules.get('a3ready.prepare')
assert camera_check_module is not None, 'Not the original prepared kernel; stop and report'
camera_check_matches = [o for o in camera_check_module.PINNED
    if getattr(o, 'config', {}).get('run_id') == 'e13f6d0e6bc04fcaa4e5051cb0b37391'
    and hasattr(o, 'neural_thread') and hasattr(o, 'driver')]
assert len(camera_check_matches) == 1, 'Prepared owner missing or ambiguous; stop and report'
camera_check_service = camera_check_matches[0]
with camera_check_service.lock:
    camera_check_driver = camera_check_service.driver
    camera_check_result = dict(
        run_id=camera_check_service.config['run_id'],
        state=camera_check_service.state, error=camera_check_service.error,
        requests=camera_check_driver.requests, commits=camera_check_driver.commits,
        pending=camera_check_driver.pending is not None, poisoned=camera_check_driver.poisoned,
        inflight=camera_check_service.inflight, connections=camera_check_service.connections,
        start_identity=camera_check_service.identity,
        neural_thread_alive=bool(camera_check_service.neural_thread and camera_check_service.neural_thread.is_alive()),
        neural_listener_present=camera_check_service.listener is not None,
        neural_connection_present=camera_check_service.connection is not None,
        control_thread_alive=bool(camera_check_service.thread and camera_check_service.thread.is_alive()),
        evidence_closed=camera_check_service.evidence.journal.closed,
        last_event=camera_check_service.evidence.last_event,
        operation='PYTHON_OBJECT_INSPECTION_ONLY_NO_DEVICE_IO')
print(json.dumps(camera_check_result, indent=2))
