import dataclasses, json, time
from .control2 import require

def neural_session(conn, driver, evidence, config):
    # Same v2 frames and unchanged Full485Driver.run/finish, no alternate compute.
    from .protocol import HELLO, ATTEST, STEP, COMMIT, digest, recv_frame, send_frame
    def receive():
        driver.check_deadline(); bounds = [time.monotonic() + 5, driver.session_deadline]
        if driver.compute_deadline is not None: bounds.append(driver.compute_deadline)
        return recv_frame(conn, evidence.wire, deadline=min(bounds))
    header, payload = receive(); require(header.op == HELLO, 'HELLO_REQUIRED')
    raw = json.dumps(driver.attest(header), sort_keys=True).encode('utf-8')
    driver.bound_asid = header.asid.hex()
    send_frame(conn, dataclasses.replace(header, op=ATTEST, payload_bytes=len(raw), payload_sha=digest(raw)), raw, evidence.wire)
    while driver.commits < 1000:
        header, payload = receive(); require(header.asid.hex() == driver.bound_asid, 'UNATTESTED_ASID')
        if header.op == STEP:
            if driver.compute_deadline is None:
                driver.compute_deadline = time.monotonic() + 600
                evidence.event('COMPUTE_WINDOW_STARTED')
            result, candidate, timing = driver.run(header, payload)
            driver.check_deadline(); send_frame(conn, result, candidate, evidence.wire)
            evidence.event('CANDIDATE_SENT', step=header.step, **timing)
        elif header.op == COMMIT:
            ack = driver.finish(header, True); driver.check_deadline(); send_frame(conn, ack, observer=evidence.wire)
            evidence.event('ACK_SENT', step=header.step)
        else: raise ValueError('Only STEP/COMMIT allowed; no recovery')
