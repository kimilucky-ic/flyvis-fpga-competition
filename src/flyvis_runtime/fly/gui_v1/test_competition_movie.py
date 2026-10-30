"""One bounded pass over the actual 485-frame pack, plus rejection/clock checks."""
import unittest
from collections import Counter
from types import SimpleNamespace
from data_store import DataStore
from scientific_pilot import ScientificPilot
from competition_replay import LazyCompetition, RUN, ACTIVITY_SHA
from competition_frames import CompetitionFrames, validate_encoding
from competition_movie import video_source_indices, CompetitionMovie


class MovieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store=DataStore()
        cls.replay=LazyCompetition(ScientificPilot(cls.store))
        cls.pack=CompetitionFrames(cls.replay).get()

    def test_all_485_real_frames_and_55_conditions(self):
        self.assertEqual(len(self.pack.receipts),485)
        self.assertEqual(sum(len(d['conditions']) for d in self.store.catalog()['datasets']),55)
        self.assertEqual(self.pack.metadata()['render_process_required'],False)

    def test_saved_state_video_clock_and_no_interpolation(self):
        indices=video_source_indices('C');counts=Counter(indices)
        self.assertEqual(len(indices),1200)
        self.assertEqual(sorted(counts),list(range(485)))
        self.assertTrue(set(counts.values())<={2,3})
        self.assertEqual(1200/30,40)
        self.assertEqual(indices[0],0);self.assertEqual(indices[-1],484)

    def test_cache_identity_and_reject_mixed_sources(self):
        k=213
        body=dict(run_id=RUN,activity_sha256=ACTIVITY_SHA,frame_index=k,
                  activity_time_s=float(self.replay.get().pilot.activity_time[k]),request_id='bounded-test',
                  type_filter='all',selected_type='T4a',presentation_profile='light')
        value=self.pack.render(body)
        self.assertEqual(value['receipt']['frame_source'],'VERIFIED_PRERENDERED_FRAME')
        for bad in ({'run_id':'wrong'},{'frame_index':True},{'activity_time_s':1},
                    {'camera':{'rotate':[.2,.2]}},{'type_filter':'T4'},{'presentation_profile':'standard'}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):self.pack.render(dict(body,**bad))
        with self.assertRaises(ValueError):self.pack.image(k,'wrong-hash')

    def test_reject_variable_colour_scale_and_incomplete_movie(self):
        encoding=dict(self.pack.manifest['color_encoding'],intensity_domain=[0,1])
        with self.assertRaises(ValueError):validate_encoding(encoding,self.replay.get().means)
        movie=CompetitionMovie(self.pack);movie.id='bounded-test';movie.state={'status':'CAPTURING_GUI'};movie.rows=[]
        with self.assertRaisesRegex(ValueError,'Incomplete'):movie.finish({'export_id':movie.id})
        self.assertIsNone(movie.process)

    def test_C_raw_and_delta_domains_and_signed_values(self):
        import copy
        from competition_frames import validate_encoding
        from competition_response import validate_c_states
        e=self.pack.manifest['color_encoding'];means=self.replay.get().means
        validate_encoding(e,means,'C')
        self.assertNotEqual(e['raw_activity_domain'][1],e['intensity_domain'][1])
        bad=copy.deepcopy(self.pack.receipts[213]['type_states']);bad[0]['delta_signed']=-bad[0]['delta_signed']
        with self.assertRaises(ValueError):validate_c_states(bad,e,means[213])
        bad=copy.deepcopy(e);bad['raw_activity_domain'][1]=e['intensity_domain'][1]
        with self.assertRaises(ValueError):validate_encoding(bad,means,'C')
        self.assertEqual(self.pack.metadata()['brightness_variant'],'C')

    def test_capture_retry_is_same_bytes_only_and_does_not_append(self):
        import tempfile
        import struct
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            movie=CompetitionMovie(self.pack);movie.pack=self.pack;movie.id='test-retry'
            movie.folder=Path(temp);(movie.folder/'frames').mkdir()
            movie.state={'status':'CAPTURING_GUI','captured':0};movie.rows=[]
            source=self.pack.manifest['frames'][0]
            headers={'X-Run-ID':RUN,'X-Frame-Pack':self.pack.manifest_sha,
                     'X-Skeleton-SHA256':source['png_sha256'],
                     'X-Color-Encoding':self.pack.manifest['color_encoding']['encoding_sha256'],
                     'X-Activity-Time':str(source['activity_time_s'])}
            # Protocol fixture only; no success movie is created from these bytes.
            png=b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',1920,1080)
            movie.capture(movie.id,0,png,headers)
            before=(movie.folder/'gui_frames.jsonl').read_bytes()
            ack=movie.capture(movie.id,0,png,headers)
            self.assertEqual(ack['duplicate_frame_ack'],0)
            self.assertEqual(ack['captured'],1)
            self.assertEqual((movie.folder/'gui_frames.jsonl').read_bytes(),before)
            for identity,k,data,h in [('wrong',0,png,headers),(movie.id,2,png,headers),
                                      (movie.id,0,png+b'different',headers),
                                      (movie.id,0,png,dict(headers,**{'X-Run-ID':'wrong'}))]:
                with self.assertRaises(ValueError):movie.capture(identity,k,data,h)
            (movie.folder/'frames/frame_0000.png').write_bytes(png+b'corrupt')
            with self.assertRaises(ValueError):movie.capture(movie.id,0,png,headers)


if __name__=='__main__':unittest.main(verbosity=2)
