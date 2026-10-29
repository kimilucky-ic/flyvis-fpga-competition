"""Frozen-input protocol tests; saved real input only, no neural/device runs."""
from copy import deepcopy
import csv
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np

from live_protocol import HERE,load,sha
from science_input import FrozenScienceInput,SCHEMA

OUT=HERE/'evidence/science_input_interface_20261019'


class ScienceInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=HERE.parent.parent/'fpga/flyvis-circuit-selection/phase3_20261010/input_bundle'
        cls.camera=HERE.parent/'camera_pipeline/controlled_video_20261010_r1'
        cls.registry=load(HERE/'live_registry.json')
        cls.real_input=np.load(cls.source/'stimulus.npy',allow_pickle=False)

    def setUp(self):
        (OUT/'cpu_cases').mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=OUT/'cpu_cases');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('stimulus.npy','time.npy','activity_time.npy','initial_state_full.npy','numeric_profile.json','metric_profile.json'):
            shutil.copyfile(self.source/name,self.root/name)
        for role,name in (('coordinates','coordinates.npy'),('input_map','input_node_ids.npy')):
            shutil.copyfile(self.registry['pins'][role]['path'],self.root/name)
        shutil.copyfile(self.camera/'sources/01_off_right.mp4',self.root/'preview.mp4')
        shutil.copyfile(self.camera/'prepare.py',self.root/'generator.py')
        shutil.copyfile(self.camera/'input/source_time.npy',self.root/'video_pts.npy')
        with (self.camera/'input/time_alignment.csv').open(encoding='utf-8',newline='') as f:
            rows=[row for row in csv.DictReader(f) if row['sample']=='1']
        np.save(self.root/'frame_index.npy',np.array([int(row['source_left_frame']) for row in rows],dtype='<i8'))
        model=load(self.source/'identity_manifest.json')
        self.json('model.json',{k:model[k] for k in ('model_id','source_commit','checkpoint_sha256','expanded_parameters_sha256','n_nodes','n_edges')})
        self.json('parameters.json',dict(seed=0,fixture_only=True,source='old deterministic OFF-right input; seed is protocol metadata, no generator was run'))
        self.json('preregistration.json',dict(evidence='CPU_INTERFACE_FIXTURE_ONLY_NOT_A_NEW_STUDY'))
        self.desc=dict(schema=SCHEMA,status='INPUT_FROZEN',experiment_id='CPU_SAVED_OFF_RIGHT_PROTOCOL_FIXTURE',
            source_kind='digital_direct',source_is_camera=False,
            assets=dict(generator='generator.py',parameters='parameters.json',preregistration='preregistration.json',
                coordinates='coordinates.npy',input_node_ids='input_node_ids.npy',model_identity='model.json',
                initial_state='initial_state_full.npy',numeric_profile='numeric_profile.json',metric_profile='metric_profile.json'),
            conditions=[dict(condition_id='saved_OFF_right',family='on_off',steps=800,dt_s=.005,
                control_role='protocol fixture using a previously recorded real condition',parameters=dict(polarity='OFF',direction='right'),
                video=dict(relation='CONVERSION_SOURCE',resampling='CAUSAL_ZOH',frame_count=240,duration_s=4.),
                files=dict(stimulus='stimulus.npy',input_time='time.npy',activity_time='activity_time.npy',
                    video='preview.mp4',video_pts='video_pts.npy',frame_index='frame_index.npy'))])
        self.c=self.desc['conditions'][0]

    def json(self,name,value):
        (self.root/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

    def seal(self,edit=None):
        self.json('GUI_HANDOFF.json',self.desc)
        files=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in self.root.iterdir()
            if p.is_file() and p.name!='DELIVERY_MANIFEST.json']
        if edit:edit(files)
        self.json('DELIVERY_MANIFEST.json',dict(files=files))
        return dict(handoff_sha256=sha(self.root/'GUI_HANDOFF.json'),manifest_sha256=sha(self.root/'DELIVERY_MANIFEST.json'))

    def open(self):
        b=FrozenScienceInput(self.root,**self.seal())
        self.addCleanup(b.close)
        return b

    def test_saved_real_input_readonly_and_no_neural_results(self):
        b=self.open();s=b.step('saved_OFF_right',799)
        self.assertTrue(np.array_equal(b.conditions['saved_OFF_right']['input'],self.real_input[0,:,0]))
        self.assertFalse(s['input_721'].flags.writeable)
        self.assertEqual(s['input_time_s'],3.995);self.assertEqual(s['activity_time_s'],4.)
        self.assertEqual(s['source_frame_index'],239)
        self.assertEqual(b.describe()['neural_results'],'NOT_AVAILABLE')
        self.assertEqual(b.describe()['FPGA_status'],'NOT_CONNECTED')
        self.assertFalse(b.describe()['media_decode_verified'])
        for step in (0,199,200,484,799):
            self.assertTrue(np.array_equal(b.step('saved_OFF_right',step)['input_721'],self.real_input[0,step,0]))

    def test_two_dimensional_input_and_declared_non485_length(self):
        n=739;self.c['steps']=n
        np.save(self.root/'stimulus.npy',self.real_input[0,:n,0])
        for name in ('time.npy','activity_time.npy','frame_index.npy'):
            np.save(self.root/name,np.load(self.root/name,allow_pickle=False)[:n])
        b=self.open();self.assertEqual(b.conditions['saved_OFF_right']['input'].shape,(739,721))
        with self.assertRaisesRegex(ValueError,'STEP_RANGE'):b.step('saved_OFF_right',739)

    def test_explicit_pins_and_missing_package_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'EXPLICIT_PINS'):FrozenScienceInput(self.root,handoff_sha256=None,manifest_sha256=None)
        pins=self.seal();pins['manifest_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'SHA256'):FrozenScienceInput(self.root,**pins)

    def test_result_wrong_input_initial_or_numeric_not_compared(self):
        b=self.open();binding=b.binding('saved_OFF_right')
        self.assertIn('IDENTITY_MATCH_ONLY',b.check_result_identity('saved_OFF_right',dict(run_id='CPU_SIDE_CAR_ONLY',binding=binding)))
        for part,key in (('state_binding','numeric_profile_sha256'),('state_binding','initial_state_array_digest'),('input_binding','condition_id')):
            wrong=deepcopy(binding);wrong[part][key]='other'
            with self.assertRaisesRegex(ValueError,'BINDING_MISMATCH'):
                b.check_result_identity('saved_OFF_right',dict(run_id='different',binding=wrong))

    def test_post_admission_source_change_invalidates_preview_and_results(self):
        b=self.open();(self.root/'preview.mp4').write_bytes(b'CPU_CORRUPTED_MEDIA')
        with self.assertRaisesRegex(ValueError,'source changed'):b.step('saved_OFF_right',0)
        with self.assertRaisesRegex(ValueError,'source changed'):b.describe()

    def test_wrong_model_rejected(self):
        m=load(self.root/'model.json');m['checkpoint_sha256']='0'*64;self.json('model.json',m)
        with self.assertRaisesRegex(ValueError,'MODEL_IDENTITY'):self.open()

    def test_reordered_hex_mapping_rejected(self):
        p=self.root/'coordinates.npy';x=np.load(p,allow_pickle=False).copy();x[[0,1]]=x[[1,0]];np.save(p,x)
        with self.assertRaisesRegex(ValueError,'ORDERED_INPUT_MAP'):self.open()

    def test_false_camera_identity_rejected(self):
        self.desc['source_is_camera']=True
        with self.assertRaisesRegex(ValueError,'INPUT_SOURCE'):self.open()

    def test_wrong_euler_time_rejected(self):
        p=self.root/'activity_time.npy';x=np.load(p,allow_pickle=False).copy();x[200]+=.005;np.save(p,x)
        with self.assertRaisesRegex(ValueError,'EULER_TIME'):self.open()

    def test_nonfinite_input_rejected(self):
        x=self.real_input.copy();x[0,0,0,0]=np.nan;np.save(self.root/'stimulus.npy',x)
        with self.assertRaisesRegex(ValueError,'INPUT_ARRAY'):self.open()

    def test_bad_initial_state_rejected(self):
        np.save(self.root/'initial_state_full.npy',np.load(self.root/'initial_state_full.npy',allow_pickle=False)[:,:67])
        with self.assertRaisesRegex(ValueError,'INITIAL_STATE'):self.open()

    def test_future_video_frame_rejected(self):
        p=self.root/'frame_index.npy';x=np.load(p,allow_pickle=False).copy();x[0]=1;np.save(p,x)
        with self.assertRaisesRegex(ValueError,'STEP_ALIGNMENT'):self.open()

    def test_preview_only_relation_explicit_not_input_source_claim(self):
        self.c['video']['relation']='GENERATOR_PREVIEW_ONLY'
        self.assertEqual(self.open().step('saved_OFF_right',0)['video_relation'],'GENERATOR_PREVIEW_ONLY')

    def test_duplicate_condition_rejected(self):
        self.desc['conditions'].append(deepcopy(self.c))
        with self.assertRaisesRegex(ValueError,'CONDITION_ID'):self.open()

    def test_unlisted_file_and_path_escape_rejected(self):
        pins=self.seal(lambda rows:rows.pop(next(i for i,r in enumerate(rows) if r['path']=='preview.mp4')))
        with self.assertRaisesRegex(ValueError,'UNLISTED_FILE'):FrozenScienceInput(self.root,**pins)
        self.c['files']['video']='../outside.mp4'
        with self.assertRaisesRegex(ValueError,'escapes'):self.open()

    def test_duplicate_manifest_file_rejected(self):
        pins=self.seal(lambda rows:rows.append(dict(rows[0])))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_MANIFEST'):FrozenScienceInput(self.root,**pins)

    def test_close_releases_files_and_prevents_stale_steps(self):
        b=self.open();b.close();b.close()
        with self.assertRaisesRegex(ValueError,'INPUT_CLOSED'):b.step('saved_OFF_right',0)
        # Windows must permit normal file replacement after reader close.
        (self.root/'stimulus.npy').write_bytes(b'CPU_TEST_CLOSED_FILE')


if __name__=='__main__':unittest.main()
