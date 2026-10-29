"""One admitted scientific run for all competition panels; read-only, no inference."""
import hashlib
import threading
import numpy as np
from scientific_pilot import require
from spatial_state import spatial_registry, TYPES

RUN = '2041849d-b1f8-46ad-a059-49b598c19ab2'
ACTIVITY_SHA = '6c0c41fb9162de306ab5c9bc1cdf0a16da0f354921ed7ecab4462161b3908234'


class CompetitionReplay:
    def init__(self, pilot):
        require(pilot is not None, 'Accepted scientific pilot unavailable')
        self.pilot = pilot
        pilot.assert_unchanged()
        require(pilot.identity['run_id'] == RUN, 'Competition run mismatch')
        self.spatial = spatial_registry()
        require(self.spatial.data['model'] == pilot.identity['model'], 'Spatial model mismatch')
        self.name = 'artifacts/pilot_gpu_r1/ON60/Full/activities_full.npy'
        require(pilot.checked[pilot.files[self.name]] == ACTIVITY_SHA, 'Competition activity identity')
        a = pilot.array(self.name)
        require(a.shape == (1, 485, 45669) and a.dtype == np.float32 and np.isfinite(a).all(), 'Complete original activity required')
        self.activity = a[0]
        self.values = np.ascontiguousarray(self.activity[:, self.spatial.ids])
        # Match ⑩'s exact original per-type FP64 mean, never normalize neural values.
        self.means = np.stack([self.activity[:, self.spatial.ids[i*721:(i+1)*721]].mean(axis=1, dtype=np.float64) for i in range(8)], axis=1)
        self.inputs = pilot.stimuli['ON60']
        self.flow = pilot.flows['ON60']['Full']
        self.array_bytes = {name: np.asarray(value, dtype='<f4').tobytes() for name, value in
                            [('input', self.inputs), ('flow', self.flow), ('spatial', self.values)]}
        self.binary_sha = {name: hashlib.sha256(value).hexdigest() for name,value in self.array_bytes.items()}

    def unchanged(self):
        self.pilot.assert_unchanged()
        self.spatial.unchanged()

    def metadata(self):
        self.unchanged()
        p = self.pilot
        return dict(schema='flyvis-competition-replay/v1', status='VERIFIED', run_id=RUN,
                    evidence_level='SOFTWARE_PILOT', display_kind='OFFLINE_REPLAY', backend='saved original FlyVis GPU + DecoderGAVP',
                    FPGA_status='NOT_CONNECTED', PL_execution=False, condition='ON60', mode='Full', frame_count=485,
                    activity_sha256=ACTIVITY_SHA, model=p.identity['model'], dt_s=.005,
                    input_time_s=p.time.tolist(), activity_time_s=p.activity_time.tolist(),
                    coordinates_uv=p.uv.tolist(), types=TYPES, means=self.means.tolist(),
                    type_mean_definition='FP64 mean over 721 original model nodes of each type; not individual biological measurement',
                    component_convention=p.contract['component_convention'], flow_units=p.contract['units'],
                    arrays={name:dict(url='/api/competition/'+name+'.bin?run='+RUN,sha256=digest,bytes=len(self.array_bytes[name])) for name,digest in self.binary_sha.items()},
                    spatial_metadata=self.spatial.public(),
                    source_files=[dict(path=str(p.files[name]),sha256=p.checked[p.files[name]]) for name in
                                  [self.name, 'artifacts/pilot_gpu_r1/ON60/Full/flow.npy',
                                   'artifacts/pilot_gpu_r1/time.npy', 'artifacts/pilot_gpu_r1/activity_time.npy',
                                   'artifacts/pilot_gpu_r1/run_identity.json',
                                   'cpu_preparation_r1/'+p.conditions['ON60']['filename']]],
                    manifest_sha256=p.config['manifest_sha256'],
                    actual_compute=p.json('artifacts/pilot_gpu_r1/ON60/Full/result.json'))

    def binary(self, name, run):
        self.unchanged()
        require(run == RUN, 'Explicit selected run required')
        return self.array_bytes[name]


class LazyCompetition:
    """Failure of optional 3D/data adapter never breaks the original GUI startup."""
    def init__(self, pilot):
        self.pilot = pilot
        self.value = None
        self.lock = threading.Lock()

    def get(self):
        with self.lock:
            if self.value is None:
                self.value = CompetitionReplay(self.pilot)
            return self.value
