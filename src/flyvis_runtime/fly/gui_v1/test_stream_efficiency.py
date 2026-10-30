"""No-device tests for bounded host optimizations; no generated neural activity."""
import sys
import unittest
from unittest.mock import Mock
from realtime_timing import Timings,SummaryCache,host_scheduling


class Efficiency(unittest.TestCase):
    def test_summary_throttles_without_dropping_samples(self):
        timing=Timings();cache=SummaryCache();timing.add('stage',.001)
        first,age=cache.get(timing,10.);self.assertEqual(age,0.)
        timing.add('stage',.003)
        old,age=cache.get(timing,10.05)
        self.assertIs(old,first);self.assertAlmostEqual(age,.05)
        self.assertEqual(old['stage']['count'],1)
        new,age=cache.get(timing,11.)
        self.assertEqual(new['stage']['count'],2)
        self.assertAlmostEqual(new['stage']['total_s'],.004)
        self.assertEqual(first['stage']['count'],1)
    def test_percentiles_called_only_at_refresh(self):
        timing=Mock();cache=SummaryCache()
        for n in range(20):cache.get(timing,n*.05)
        self.assertEqual(timing.summary.call_count,1)
    def test_host_scheduling_restores_after_error(self):
        old=sys.getswitchinterval()
        with self.assertRaisesRegex(RuntimeError,'fixture'):
            with host_scheduling(.001):
                self.assertEqual(sys.getswitchinterval(),.001)
                raise RuntimeError('fixture')
        self.assertEqual(sys.getswitchinterval(),old)
    def test_unapproved_interval_rejected(self):
        with self.assertRaisesRegex(ValueError,'PROFILE'):
            with host_scheduling(1.):pass


if __name__=='__main__':unittest.main()
