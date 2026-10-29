"""Camera orchestration around the ORIGINAL Coordinator/GPU candidates/A3 Client.

No model, transport protocol, neuron equation or hardware implementation here.
Import is CPU-only. Device factories are called by the explicit scoped worker.
"""
import copy
import dataclasses
import io
import json
import threading
import time
import uuid

import numpy as np
from hybrid_a3 import _CoordinatorBarrier
from live_protocol import canonical, require
from joint_camera_protocol import DT, LIVE, TEST, POLICY, PROFILE, digest, frame_check


class JointCameraEvidence:
    """Reuse ⑦'s accepted append-only writer and its COMMIT durability order."""
    def init__(self, writer, expected_steps):
        self.writer, self.expected = writer, expected_steps
        self.wire_index = self.completed = 0
        self.failed = False

    def blob(self, name, value):
        return self.writer.add(name, value)

    def array(self, name, value):
        b = io.BytesIO()
        np.save(b, value, allow_pickle=False)
        return self.blob(name, b.getvalue())

    def json(self, name, value):
        return self.blob(name, json.dumps(value, sort_keys=True, allow_nan=False).encode())

    def event(self, value):
        self.writer.add('transactions.jsonl', (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode(), kind='line')
        if value['event'] not in ('COMMIT_INTENT', 'COMMIT_ACK'):
            self.failed = True
        self.writer.checkpoint(value['event'])

    def observe(self, direction, wire):
        self.blob('wire_%04d_%s.bin' % (self.wire_index, direction), wire)
        self.wire_index += 1
        if direction == 'tx_intent':
            self.writer.checkpoint('BEFORE_SEND')
        elif direction != 'rx':
            self.failed = True
            self.writer.checkpoint('INCOMPLETE_RECEIVE')

    def published(self):
        self.writer.checkpoint('STEP_PUBLISHED')
        self.completed += 1
        return dict(barrier='STEP_PUBLISHED', sequence=self.writer.sequence - 1,
                    batch_sha256=self.writer.previous, end_offset=self.writer.stream.tell())

    def close(self, reason):
        if not self.writer.closed:
            self.writer.close('FAILED_OR_INCOMPLETE' if self.failed else 'CAPTURE_STOPPED_PENDING_PS_AUDIT',
                              completed=self.completed, max_steps=self.expected, reason=reason)


class CameraJointEngine:
    """One original Coordinator owns all state. GUI has no commit authority."""
    def init__(self, c, client, produce, decode, evidence, identity, gate, publication, read_publication,
                 check_reference, *, execution_kind=TEST):
        require(execution_kind in (TEST, LIVE), 'JOINT_EXECUTION_KIND')
        self.c, self.client, self.produce, self.decode, self.evidence = c, client, produce, decode, evidence
        self.identity, self.gate, self.read_publication, self.check_reference = copy.deepcopy(identity), gate, read_publication, check_reference
        self.kind = execution_kind
        self.owner = threading.Lock()
        self.failed = False
        self.started = time.monotonic()
        self.last_source_sequence = -1
        self.progress = lambda phase, step: None
        initial, words, _ = c.initial()
        self.barrier = _CoordinatorBarrier(c, initial, words, identity['run_id'], identity['comparison_id'],
            identity['condition_id'], client.asid, evidence.event, execution_kind=execution_kind,
            publication_factory=publication)
        evidence.array('initial_full.npy', initial)
        evidence.blob('initial_H.bin', words)
        evidence.json('session_identity.json', identity)
        evidence.json('firmware_session.json', client.attestation)
        evidence.writer.checkpoint('SESSION_IDENTITY')

    def step(self, item):
        require(self.owner.acquire(blocking=False), 'JOINT_STEP_ALREADY_IN_PROGRESS')
        b, c, w = self.barrier, self.c, self.c.wire
        try:
            k = b.state_token
            require(not self.failed and k < self.identity['max_steps'], 'JOINT_STEP_LIMIT_OR_FAILED')
            self.gate()
            source_kind = 'recorded_protocol_fixture' if self.kind == TEST else 'real_windows_camera'
            source = frame_check(item, self.identity['run_id'], source_kind)
            require(source['sequence'] >= self.last_source_sequence, 'JOINT_SOURCE_REVERSED')
            frozen = copy.deepcopy(item)
            x721 = np.asarray(frozen['values'], dtype='<f4')
            old = b.state
            old_sha = b.hmod.array_hash(old)
            require(np.array_equal(self.read_publication(b.publication), old), 'JOINT_VISIBLE_OLD_MISMATCH')
            self.progress('GPU_CHEMICAL_R', k)
            output = self.produce(b.publication, x721, k)
            require(b.hmod.array_hash(b.state) == old_sha, 'JOINT_OLD_MUTATED')
            reference = self.check_reference(old, x721, output, k)
            x, chemical, rr, rids = (output[n] for n in ('x_full', 'chemical_H', 'new_R', 'r_ids'))
            cb = dict(b.binding(x), chemical_digest=b.hmod.array_hash(chemical))
            rb = dict(b.binding(x), r_candidate_digest=b.hmod.array_hash(rr), r_ids_digest=b.hmod.array_hash(rids))
            header_raw, payload = b.prepare(uuid.uuid4().bytes, x, chemical, cb)
            h = w.Header.unpack(header_raw)
            for name, value in (('old_full', old), ('input_721', x721), ('chemical', chemical), ('R_candidate', rr)):
                self.evidence.array(f'{name}_{k}.npy', value)
            self.evidence.blob(f'source_{k}.png', __import__('base64').b64decode(frozen['png']))
            self.evidence.json(f'source_{k}.json', frozen['source'])
            self.evidence.json(f'conversion_{k}.json', frozen['conversion'])
            self.evidence.blob(f'request_{k}.bin', header_raw + payload)
            self.gate()
            tick = time.perf_counter_ns()
            self.progress('STEP_EXCHANGE_WAIT_CANDIDATE', k)
            names = ('asid', 'txn', 'step', 'old_sha', 'epoch', 'config', 'parent_commit', 'previous_txn')
            n = w.WORD_BYTES
            candidate, receipt = self.client.step(payload[:n], payload[n:2*n], payload[2*n:], {v: getattr(h, v) for v in names})
            step_ns = time.perf_counter_ns() - tick
            self.progress('VERIFYING_PL_AND_R_CANDIDATES', k)
            check = c.validate_H(payload, candidate)
            self.evidence.blob(f'candidate_{k}.bin', candidate)
            self.evidence.blob(f'RESULT_{k}.bin', receipt.pack())
            staged = b.accept_candidates(receipt.pack(), candidate, rr, rids, rb)
            self.evidence.array(f'proposed_full_{k}.npy', b.pending['staged'].state)
            self.evidence.json(f'validation_{k}.json', dict(integer_check=check, reference=reference, **staged))
            self.gate()
            commit = b.commit_frame()
            self.evidence.blob(f'COMMIT_{k}.bin', commit)
            tick = time.perf_counter_ns()
            self.progress('COMMIT_EXCHANGE_WAIT_ACK', k)
            ack = self.client.commit(bytes.fromhex(staged['unified_commit_sha256']))
            commit_ns = time.perf_counter_ns() - tick
            self.evidence.blob(f'ACK_{k}.bin', ack.pack())
            require(ack == dataclasses.replace(w.Header.unpack(commit), op=w.ACK), 'JOINT_EXACT_COMMIT_ACK')
            full = b.acknowledge(ack.pack())  # Original durable ACK then ONE publication.
            self.progress('ACK_MATCHED_DECODING_COMMITTED_STATE', k)
            self.evidence.array(f'committed_full_{k}.npy', full)
            self.gate()  # STOP/expired after ACK preserves commit but revokes display.
            flow = np.asarray(self.decode(full), dtype='<f4')
            require(flow.shape == (2, 721) and np.isfinite(flow).all(), 'JOINT_OFFICIAL_FLOW')
            spatial = c.spatial.extract(full)
            self.evidence.array(f'spatial_{k}.npy', spatial)
            self.evidence.array(f'flow_{k}.npy', flow)
            tx = dict(status='ACK_MATCHED_AND_PUBLISHED', step_id=k, ASID=self.client.asid.hex(), txn=h.txn.hex(),
                old_full_sha256=old_sha, full_after_sha256=b.hmod.array_hash(full),
                old_H_sha256=digest(payload[:n]), request_sha256=digest(header_raw + payload),
                candidate_sha256=digest(candidate), ACK_sha256=digest(ack.pack()),
                unified_commit_sha256=staged['unified_commit_sha256'], integer_error=0,
                core_cycles=receipt.compute_cycles, adapter_cycles=receipt.transfer_cycles,
                PC_STEP_roundtrip_ns=step_ns, PC_COMMIT_roundtrip_ns=commit_ns)
            packet = dict(schema='flyvis-camera-joint-output/v1', **self.identity,
                serial=k+1, step_id=k, state_token=k+1, input_time_s=k*DT, activity_time_s=k*DT+DT,
                execution_kind=self.kind, source_kind=source_kind, actual_new_computation=self.kind == LIVE,
                evidence_level='CPU_PROTOCOL_REPLAY_ONLY' if self.kind == TEST else 'ACK_MATCHED_DURABLE_PENDING_PS_AUDIT',
                numerical_profile=PROFILE, input_hex=x721.tolist(), preview_png=frozen['png'],
                source=frozen['source'], conversion=frozen['conversion'],
                temporal_mapping=dict(policy=POLICY, capture_relative_s=source['relative_s'], model_input_s=k*DT,
                    held_previous_source=source['sequence'] == self.last_source_sequence,
                    meaning='variable physical sampling mapped to fixed model steps; not wall-time 200Hz'),
                wall_elapsed_s=time.monotonic()-self.started, flow=flow.tolist(), flow_sha256=digest(flow.tobytes()),
                spatial=dict(run_id=self.identity['run_id'], step_id=k, state_token=k+1,
                    map_sha256=c.spatial.digest, values=spatial.tolist(), values_sha256=digest(spatial.tobytes())),
                transaction=tx, PL_participating_global_ids=[] if self.kind == TEST else c.spatial.ids.tolist(),
                PL_proven_global_ids=[], whole_run_acceptance='PENDING', REALTIME_STREAM_PASS='NOT_CLAIMED')
            # Snapshot metadata itself and original arrays are durable BEFORE notification.
            self.evidence.json(f'committed_step_{k}.json', {key: value for key, value in packet.items()
                if key not in ('preview_png', 'input_hex', 'flow', 'spatial')})
            packet['durable'] = self.evidence.published()
            self.progress('STEP_PUBLISHED_DURABLE', k)
            self.last_source_sequence = source['sequence']
            return packet
        except BaseException as error:
            self.failed = True
            b.fail(error)
            try:
                self.evidence.event(dict(event='DISPLAY_REVOKED', error=str(error), state_token=b.state_token, phase=b.phase))
            except Exception as secondary:
                self.secondary_evidence_error = str(secondary)
            try:self.client.close()
            except Exception as secondary:self.secondary_close_error = str(secondary)
            raise
        finally:
            self.owner.release()

    def close(self, reason):
        try:
            self.client.close()
        finally:
            self.evidence.close(reason)
