"""CPU-only checks of diagnostic capture and unchanged saved JSON semantics."""
import json
import tempfile
import time
import unittest
from pathlib import Path
import numpy as np
from live_protocol import write
from realtime_timing import Timings,StepTrace


class StallTraceTests(unittest.TestCase):
    def test_vector_percentiles_equal_previous_three_calls(self):
        timing=Timings()
        values=np.random.default_rng(721).random(10000)/1000
        for value in values:timing.add('saved_host_timing',value)
        result=timing.summary()['saved_host_timing']
        for p in (50,95,99):
            self.assertEqual(result[f'p{p}_ms'],float(np.percentile(values,p)*1000))
        self.assertEqual(result['max_ms'],float(values.max()*1000))
        self.assertEqual(result['count'],10000)

    def test_trace_defers_io_and_binds_each_step(self):
        trace=StepTrace(2);timing=Timings();timing.trace=trace
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'runtime') as directory:
            target=Path(directory)/'step_timing.jsonl'
            trace.begin(0,0.,0.,True)
            with timing.measure('CPU_protocol_wait'):time.sleep(.005)
            trace.finish(1,0)
            self.assertFalse(target.exists())
            trace.begin(1,.01,.002,False);trace.finish(2,2)
            with self.assertRaisesRegex(ValueError,'BOUND'):trace.begin(2,.02,0,False)
            trace.save(target,'session_CPU_PROTOCOL','run_CPU_PROTOCOL')
            rows=[json.loads(s) for s in target.read_text().splitlines()]
            self.assertEqual([row['step_id'] for row in rows],[0,1])
            self.assertEqual(rows[0]['durable_steps'],0)
            self.assertGreater(rows[0]['stages']['CPU_protocol_wait']['wall_s'],.004)
            self.assertEqual(rows[1]['run_id'],'run_CPU_PROTOCOL')

    def test_compact_atomic_record_preserves_values_and_rejects_nonfinite(self):
        source=Path(__file__).parent/'runtime/live/f1fe7afff451461fbbc77603a540cc0d/stream/snapshots/000001.json'
        original=json.loads(source.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'runtime') as directory:
            normal=Path(directory)/'pretty.json';compact=Path(directory)/'compact.json'
            write(normal,original);write(compact,original,compact=True)
            self.assertEqual(json.loads(compact.read_text(encoding='utf-8')),original)
            self.assertLess(compact.stat().st_size,normal.stat().st_size)
            with self.assertRaises(ValueError):write(compact,dict(value=float('nan')),compact=True)
            self.assertEqual(json.loads(compact.read_text(encoding='utf-8')),original)


if __name__=='__main__':unittest.main()
