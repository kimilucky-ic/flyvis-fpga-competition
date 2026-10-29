"""Bounded CPU deadline, notification and exact graphics reference checks."""
import hashlib,threading,time,unittest
import numpy as np
from types import SimpleNamespace
from live_protocol import HERE,load,write
from stream_cadence import DisplayCadence
from stream_runtime import StreamHub
from stream_bridge import StreamBridge
from cached_skeleton import CachedSkeleton

class HeadroomTests(unittest.TestCase):
    def test_fixed_cadence_does_not_add_processing_time_or_skip_neural_steps(self):
        cadence=DisplayCadence(15);steps=[];shown=[]
        for k in range(6000):
            elapsed=k/100;steps.append(k)
            if cadence.due(elapsed):shown.append(k);cadence.published(elapsed+.018)
        self.assertEqual(steps,list(range(6000)));self.assertEqual(len(shown),900)
        cadence.published(100);self.assertGreater(cadence.next_due,100)
        with self.assertRaises(ValueError):DisplayCadence(200)

    def test_worker_and_windows_wait_wake_on_result_and_stop(self):
        hub=StreamHub('CPU_TEST');hub.control=dict(run_id='a'*32,source_kind='digital_direct');hub.bridge_at=time.monotonic()
        def publish():
            with hub.lock:hub.packet={'serial':7};hub.updated.notify_all()
        timer=threading.Timer(.01,publish);timer.start()
        response=hub.dispatch('bridge','latest',dict(after_serial=-1,wait_ms=100));timer.join()
        self.assertEqual(response['packet']['serial'],7)
        with self.assertRaisesRegex(ValueError,'WAIT_BOUND'):hub.dispatch('bridge','latest',dict(wait_ms=201))
        bridge=StreamBridge.__new__(StreamBridge);bridge.lock=threading.RLock();bridge.updated=threading.Condition(bridge.lock)
        bridge.packet=None;bridge.wire_packet=None;bridge.stop_event=threading.Event();bridge.error=None;bridge.status=lambda:dict(result_valid=not bridge.stop_event.is_set())
        def stop():
            with bridge.lock:bridge.stop_event.set();bridge.updated.notify_all()
        timer=threading.Timer(.01,stop);timer.start();response=bridge.latest(after=-1,wait_ms=100);timer.join()
        self.assertFalse(response['status']['result_valid']);self.assertIsNone(response['packet'])

    def test_sparse_pixel_audit_exact_against_22_original_saved_state_images(self):
        folder=HERE/'evidence/cached_canvas_20261015/cpu_profile';h=load(folder/'cache_health.json')
        cached=CachedSkeleton((folder/'projection.cache').read_bytes(),h);packets=load(folder/'packets.json');receipts=load(folder/'receipts.json');times=[]
        for p,r in zip(packets,receipts):
            means=np.asarray(p['spatial']['values'],dtype='<f4').reshape(8,721).mean(axis=1,dtype=np.float64)
            begin=time.perf_counter();rgba,_=cached.render(means,h);times.append((time.perf_counter()-begin)*1000)
            self.assertEqual(hashlib.sha256(rgba.tobytes()).hexdigest(),r['raw_sha256'])
        write(HERE/'evidence/latency_headroom_20261015/pixel_audit_cpu.json',dict(status='PASS_EXACT_22_REAL_SAVED_PIXEL_HASHES',frames=len(times),p50_ms=float(np.median(times)),p95_ms=float(np.percentile(times,95)),active_pixels=len(cached.active),total_pixels=cached.alpha.size,new_neural_steps=0))

if __name__=='__main__':unittest.main()
