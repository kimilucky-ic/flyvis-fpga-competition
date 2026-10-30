"""Minimal-compute branch of the EXISTING managed GPU worker.

Startup/admission and CUDA lease belong to joint_camera_worker. This module
does not launch a process/device, create a model, or implement neuron updates.
"""
import base64
import csv
import dataclasses
import io
import json
import threading
import time
import uuid
import numpy as np
from live_protocol import load, write, sha, require
from joint_minimal_core import AsyncRecords, MinimalEngine, POLICY, EVIDENCE, transport_residual
from joint_camera_protocol import LIVE, POLICY as INPUT_POLICY, digest, validate_snapshot


def snapshot(last, scope, identity, c, client, decoder, engine, logging):
    live5=scope.get('live_response_hz')==5
    k=last['step_id'];full=last['full'];w=c.wire;header=w.Header.unpack(last['header'])
    flow=np.asarray(decoder.decode(full[None,None],chunk_frames=1)[0,0],dtype='<f4')
    spatial=c.spatial.extract(full)
    tx=dict(status='ACK_MATCHED_AND_PUBLISHED',step_id=k,ASID=client.asid.hex(),txn=header.txn.hex(),
        old_full_sha256=header.old_sha.hex(),full_after_sha256=engine.barrier.hmod.array_hash(full),
        old_H_sha256=digest(last['payload'][:w.WORD_BYTES]),request_sha256=digest(last['header']+last['payload']),
        candidate_sha256=digest(last['candidate']),ACK_sha256=digest(last['ack']),
        unified_commit_sha256=last['decision'],integer_error=None,numerical_check='DEFERRED_OFFLINE',
        core_cycles=last['core_cycles'],adapter_cycles=last['adapter_cycles'])
    packet=dict(identity,schema='flyvis-camera-joint-output/v1',serial=k+1,step_id=k,state_token=k+1,
        input_time_s=k*.005,activity_time_s=k*.005+.005,execution_kind=LIVE,source_kind='real_windows_camera',
        actual_new_computation=True,numerical_profile=scope['numerical_profile'],evidence_level=EVIDENCE,
        display_kind='LIVE_LOW_RATE_LATEST_COMMITTED_STATE' if live5 else 'POST_COMPUTE_SAME_RUN_NOT_REALTIME',input_hex=last['frame'].tolist(),preview_png=last['item']['png'],
        source=last['item']['source'],conversion=last['item']['conversion'],flow=flow.tolist(),flow_sha256=digest(flow.tobytes()),
        temporal_mapping=dict(policy=INPUT_POLICY,capture_relative_s=last['item']['source']['relative_s'],
            model_input_s=k*.005,meaning='Latest physical sample held per actual model step; not wall-time200Hz'),
        wall_elapsed_s=last['compute_elapsed_ns']/1e9,transaction=tx,
        spatial=dict(run_id=scope['run_id'],step_id=k,state_token=k+1,map_sha256=c.spatial.digest,
            values=spatial.tolist(),values_sha256=digest(spatial.tobytes())),
        PL_participating_global_ids=c.spatial.ids.tolist(),PL_proven_global_ids=[],
        durable=dict(barrier='NOT_SYNCHRONOUS',recording=logging),whole_run_acceptance='PENDING',REALTIME_STREAM_PASS='NOT_CLAIMED')
    if live5:
        packet.update(live_response_hz=5,compute_pacing='UNTHROTTLED_COMMIT_DRIVEN')
    validate_snapshot(packet,identity,c.spatial)
    return packet


def execute(root, scope, session, c, producer, decoder, torch, hub, control,
            gpu_ready, Journal, gate, stop_monitor, finish_budget, final_audit):
    while hub.control is None:
        gate()
        time.sleep(.02)
    while hub.inputs.freeze_for_step() is None:
        gate()
        time.sleep(.01)
    stop_monitor()  # No source/clock audit competes with the timed neural loop.
    control.prepared()
    engine=client=recorder=writer=None
    live5=scope.get('live_response_hz')==5
    display_rows=[]
    latest_committed_packet=None
    last_published_at=None
    recording_window_closed = threading.Event()
    try:
        writer = Journal(root/'pc', dict(role='PC', run_id=scope['run_id'],
            runtime_policy=POLICY, evidence_level=EVIDENCE))

        def array(name, value):
            stream = io.BytesIO()
            np.save(stream, value, allow_pickle=False)
            writer.add(name, stream.getvalue())

        def save(record):
            k = record['step_id']
            for name, value in [('old_full',record['old']), ('input_721',record['frame']),
                ('chemical',record['output']['chemical_H']), ('R_candidate',record['output']['new_R']),
                ('committed_full',record['full'])]:
                array('%s_%d.npy' % (name,k), value)
            if 'live_flow' in record:array('official_flow_%d.npy'%k,record['live_flow'])
            for name,value in [('request',record['header']+record['payload']),('candidate',record['candidate']),
                ('RESULT',record['receipt']),('COMMIT',record['commit']),('ACK',record['ack'])]:
                writer.add('%s_%d.bin' % (name,k),value)
            writer.add('source_%d.png' % k,base64.b64decode(record['item']['png']))
            writer.add('source_%d.json' % k,json.dumps(record['item']['source']).encode())
            writer.add('conversion_%d.json' % k,json.dumps(record['item']['conversion']).encode())
            writer.add('timing_%d.json' % k,json.dumps({n:v for n,v in record.items()
                if n.endswith('_ns') or n in ('step_id','core_cycles','adapter_cycles','decision')}).encode())
            writer.add('events_%d.json' % k,json.dumps(record['events']).encode())
            writer.checkpoint('ASYNC_AFTER_ACK')

        def deferred_save(record):
            recording_window_closed.wait()  # Recorder waits; computation never does.
            save(record)
        recorder = AsyncRecords(deferred_save, capacity=scope['max_steps'])
        endpoint = load(root/'hardware_handoff.json')['endpoint']
        control.start(gpu_ready, min(1500,session['end_unix']-time.time()))
        client = c.wire.Client(endpoint['host'],endpoint['port'])  # No journal observer.
        from joint_camera_io import tune_client
        tune_client(client)  # NODELAY/QUICKACK; no per-call diagnostics/I/O.
        att = client.attestation
        require(all(att[k]==scope[k] for k in ('boot_id','server_session','bit_sha256','hwh_sha256')),
                'MINIMAL_ATTESTATION_IDENTITY')
        probe_roundtrips=[]
        for probe in range(scope.get('transport_probe_count',0)):
            payload=bytes(c.wire.INPUT_BYTES)
            h=c.wire.Header(c.wire.STEP,client.asid,uuid.uuid4().bytes,0,
                c.wire.digest(b'MINIMAL_TRANSPORT_ONLY_PROBE_V1'),c.wire.digest(payload),len(payload),epoch=1)
            begin=time.perf_counter_ns()
            c.wire.send_frame(client.sock,h,payload)
            reply,echo=c.wire.recv_frame(client.sock,deadline=time.monotonic()+5)
            probe_roundtrips.append(time.perf_counter_ns()-begin)
            require(reply.identity()==h.identity() and reply.op==c.wire.RESULT and not reply.compute_cycles
                and echo==payload[:c.wire.WORD_BYTES],'MINIMAL_TRANSPORT_PROBE_REPLY')
        identity = dict(run_id=scope['run_id'],session_id=scope['session_id'],comparison_id=scope['comparison_id'],
            condition_id='CURRENT_CAMERA',max_steps=scope['max_steps'],model=scope['model'],mapping_sha256=c.mapping_sha,
            runtime_policy=POLICY,validation_policy='SAME_OLD_CPU_POST_RUN',
            hardware=dict(ASID=client.asid.hex(),**{k:att[k] for k in ('boot_id','server_session','bit_sha256','hwh_sha256')}))
        if live5:identity['live_response_hz']=5
        hub.identity = identity
        events = []
        def produce(old,frame,k):
            begin,end = torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
            begin.record()
            output=producer.produce(old,torch.as_tensor(frame,device='cuda'),run_id=scope['run_id'],
                                    step_id=k,condition_id='CURRENT_CAMERA')
            end.record()
            events.append((begin,end))
            return output
        engine=MinimalEngine(c,client,produce,
            lambda full:torch.as_tensor(full.copy(),device='cuda',dtype=torch.float32),identity,recorder)
        hub.minimal_engine=engine
        started=time.monotonic()
        deadline=min(started+scope['max_worker_s'],started+scope['capture_duration_s'])
        while hub.committed<scope['max_steps']:
            if (root/'STOP_REQUEST.json').exists():hub.stopping=True
            if hub.stopping:
                break
            if hub.error:
                raise RuntimeError(hub.error)
            if time.monotonic()>=deadline:
                raise TimeoutError('MINIMAL_COMPUTE_BOUND_EXCEEDED')
            item=hub.inputs.freeze_for_step()
            if item is None:
                raise RuntimeError('MINIMAL_INPUT_MISSING')
            finish_budget.exchange_started()
            sample=engine.step(item)
            hub.committed=engine.barrier.state_token
            hub.update_progress('MINIMAL_COMPUTE_ONLY',sample['step_id'])
            if live5:
                hub.update_progress('ACK_MATCHED_DECODING_COMMITTED_STATE',sample['step_id'])
                decode_at=time.perf_counter_ns()
                packet=snapshot(sample,scope,identity,c,client,decoder,engine,
                    dict(complete=False,state='PENDING_ASYNC_AFTER_ACK'))
                latest_committed_packet=packet
                sample['live_flow']=np.asarray(packet['flow'],dtype='<f4')
                published=False
                with hub.changed:
                    hub.check(allow_stop=True)
                    now=time.monotonic()
                    if not hub.stopping and (last_published_at is None or now-last_published_at>=.2):
                        hub.packet=packet
                        hub.state='RUNNING_LOW_RATE_LATEST_COMMITTED_STATE'
                        hub.changed.notify_all()
                        last_published_at=now
                        published=True
                display_rows.append(dict(step_id=sample['step_id'],source_sequence=item['source']['sequence'],
                    decode_snapshot_ns=time.perf_counter_ns()-decode_at,
                    decoded_elapsed_s=now-started,published=published,
                    published_elapsed_s=now-started if published else None))
                # A publication deadline can only skip a display update, never
                # delay a model step. All step evidence and flows are retained.
        compute_finished=time.monotonic()
        recording_window_closed.set()
        reason='STEP_LIMIT_COMPLETE' if hub.committed==scope['max_steps'] else 'USER_STOP'
        require(hub.committed>0,'MINIMAL_NO_COMMITS')
        # Source closure and PS finish precede optional post-run work.
        hub.capture_close_requested=True
        closed=finish_budget.wait_source_closed(root/'camera_capture.json',scope['run_id'])
        finish_budget.require_send_margin()
        finish_budget.finish_started_at=finish_budget.clock()
        ending=control.finish(hub.committed,engine.barrier._visible[2].hex(),
                              engine.barrier._visible[3].hex(),reason)
        finish_budget.finish_returned_at=finish_budget.clock()
        write(root/'PS_FINISH.json',ending)
        logging=recorder.close(timeout=5)
        if logging['closed']:
            writer.close('ASYNC_CAPTURE_FINISHED' if logging['complete'] else 'ASYNC_CAPTURE_INCOMPLETE',
                         completed=hub.committed,recording=logging)
        ps={row['step_id']:row for row in ending['minimal_compute']['timing_rows']}
        rows=[]
        for k,sample in enumerate(engine.samples):
            events[k][1].synchronize()
            measured=dict(step_id=k,GPU_produce_wall_ns=sample['GPU_produce_wall_ns'],
                CUDA_stream_interval_ms=events[k][0].elapsed_time(events[k][1]),
                compute_step_wall_ns=sample['compute_step_wall_ns'],core_cycles=sample['core_cycles'],
                PL_core_ms_at_configured_100MHz=sample['core_cycles']/100000,
                STEP=transport_residual(sample['STEP_socket_roundtrip_ns'],ps[k]['STEP_ps_residence_ns']),
                COMMIT=transport_residual(sample['COMMIT_socket_roundtrip_ns'],ps[k]['COMMIT_ps_residence_ns']),
                PS_dma_observed_ns=ps[k]['ps_dma_roundtrip_observed_ns'])
            rows.append(measured)
        report=dict(schema='flyvis-minimal-compute-performance/v1',runtime_policy=POLICY,
            run_id=scope['run_id'],session_id=scope['session_id'],steps=hub.committed,
            total_compute_wall_s=compute_finished-started,
            total_engine_wall_s=engine.samples[-1]['compute_elapsed_ns']/1e9,
            model_time_s=hub.committed*.005,rows=rows,recording=logging,
            evidence_level=EVIDENCE,independent_numerical_audit='PENDING',
            REALTIME_STREAM_PASS='NOT_CLAIMED',
            timing_semantics='GPU wall and CUDA stream interval are not pure kernel times. Transport is PC socket RTT minus PS residence, not one-way/PHY latency. No cross-host epochs subtracted.',
            no_inline=['file_audit','reference_oracle','fsync','evidence_array_JSON_serialization','decoder','GUI_render','recording_wait'])
        probe_ps=ending['minimal_compute']['transport_probes']
        report['transport_only_probes']=[dict(index=i,**transport_residual(value,probe_ps[i]['ps_residence_ns']),
            input_bytes=probe_ps[i]['input_bytes'],output_bytes=probe_ps[i]['output_bytes'],PL_calls=0,GPU_calls=0)
            for i,value in enumerate(probe_roundtrips)]
        report['transport_only_definition']='Two same-size request/reply exchanges before neural computation; zero PL/GPU execution. Includes real TCP/protocol/host handling, not an identified physical one-way latency.'
        if live5:
            report.update(live_response_hz=5,display_rows=display_rows,
                compute_pacing='UNTHROTTLED_COMMIT_DRIVEN',display_consumer_limit_hz=5,
                publication_policy='LATEST_COMMITTED_SLOT_5HZ_NONBLOCKING_FINAL_FLUSH',
                display_rows_semantics='Per-step decode; published marks live slot refresh. Final-COMMIT flush is draw-throttled by browser. Actual draws are browser receipts.',
                actual_commit_rate_hz=hub.committed/(compute_finished-started) if compute_finished>started else None,
                model_speed_fraction=hub.committed*.005/(compute_finished-started) if compute_finished>started else None,
                no_inline=['file_audit','reference_oracle','fsync','recording_wait'])
        write(root/'MINIMAL_PERFORMANCE.json',report)
        with (root/'MINIMAL_TIMINGS.csv').open('x',newline='',encoding='utf-8-sig') as stream:
            fields=['step','GPU_host_ms','CUDA_stream_interval_ms','STEP_roundtrip_ms','STEP_transport_residual_ms',
                    'COMMIT_roundtrip_ms','COMMIT_transport_residual_ms','PL_cycles','PL_ms_at_configured_100MHz',
                    'PS_DMA_ms','total_step_ms']
            table=csv.DictWriter(stream,fieldnames=fields);table.writeheader()
            for row in rows:
                residual=lambda part:row[part]['transport_residual_ns']/1e6 if row[part]['valid'] else None
                table.writerow(dict(step=row['step_id'],GPU_host_ms=row['GPU_produce_wall_ns']/1e6,
                    CUDA_stream_interval_ms=row['CUDA_stream_interval_ms'],STEP_roundtrip_ms=row['STEP']['pc_socket_roundtrip_ns']/1e6,
                    STEP_transport_residual_ms=residual('STEP'),COMMIT_roundtrip_ms=row['COMMIT']['pc_socket_roundtrip_ns']/1e6,
                    COMMIT_transport_residual_ms=residual('COMMIT'),PL_cycles=row['core_cycles'],
                    PL_ms_at_configured_100MHz=row['PL_core_ms_at_configured_100MHz'],PS_DMA_ms=row['PS_dma_observed_ns']/1e6,
                    total_step_ms=row['compute_step_wall_ns']/1e6))
        # Legacy benchmark decodes after the run; live5 already decoded each COMMIT.
        packet=latest_committed_packet if live5 else snapshot(engine.samples[-1],scope,identity,c,client,decoder,engine,logging)
        require(packet is not None,'MINIMAL_FINAL_PACKET_MISSING')
        if live5:packet['durable']['recording']=logging
        write(root/'final_snapshot.json',packet)
        with hub.changed:
            hub.packet=packet
            hub.state='STOPPED_LAST_COMMITTED_STATE' if live5 else 'POST_COMPUTE_SAME_RUN_DISPLAY'
            hub.changed.notify_all()
        producer.check_unchanged();decoder.assert_weights_unchanged();engine.original_unchanged()
        write(root/'runtime_validation.json',dict(runtime_policy=POLICY,independent_CPU_reference='PENDING_OFFLINE_AUDIT',
            file_audit=final_audit(),whole_run_acceptance='PENDING'))
        write(root/'result.json',dict(status='STOPPED_PENDING_PS_AUDIT',reason=reason,run_id=scope['run_id'],
            committed_steps=hub.committed,runtime_policy=POLICY,numerical_profile=scope['numerical_profile'],
            native_H_GPU_updates=producer.native_H_update_count,recording=logging,
            independent_CPU_reference='PENDING_OFFLINE_AUDIT',whole_run_acceptance='PENDING',REALTIME_STREAM_PASS='NOT_CLAIMED'))
        return engine,reason
    except BaseException:
        recording_window_closed.set()
        logging=recorder.close(timeout=.1) if recorder else None
        if writer and (logging is None or logging["closed"]):
            writer.abandon()
        if engine:engine.close()
        elif client:client.close()
        raise
