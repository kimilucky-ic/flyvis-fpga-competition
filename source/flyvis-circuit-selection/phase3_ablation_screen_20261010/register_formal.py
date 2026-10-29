"""Freeze architect-issued norm and identities before inspecting ablation outcomes."""
import shutil,uuid,datetime
from common import *

def main():
    source=HERE.parent.parent/'docs/flyvis_visual_hybrid/architect_ablation_20261010'
    dest=HERE/'spec_snapshot'
    if dest.exists():raise SystemExit('Preserve existing registration')
    dest.mkdir();manifest=load(source/'manifest.json')
    for entry in manifest['files']:
        assert file_hash(source/entry['path'])==entry['sha256']
        shutil.copy2(source/entry['path'],dest/entry['path'])
    shutil.copy2(source/'manifest.json',dest/'manifest.json')
    spec=load(dest/'spec_config.json');meta=load(BUNDLE/'screen_manifest.json')
    for filename,sha in [('expanded_parameters.npz',spec['model']['expanded_parameters_sha256']),('initial_state_full.npy',spec['model']['initial_state_sha256']),
        ('stimulus.npy',spec['fixture']['stimulus_sha256']),('time.npy',spec['fixture']['time_sha256']),('conditions.csv',spec['fixture']['conditions_sha256'])]:
        assert file_hash(BUNDLE/filename)==sha
    for name,candidate in spec['candidates'].items():
        local=BUNDLE/'candidates'/name
        assert file_hash(local/'candidate_manifest.json')==candidate['candidate_manifest']['sha256']
        h=HUpdater(local/'static_boundary_gpu_native.npz')
        assert np.array_equal(h.h_ids,np.load(dest/Path(candidate['H_ids']['path']).name)) if os.name=='nt' else np.array_equal(h.h_ids,np.load(dest/host_path(candidate['H_ids']['path']).name))
        with np.load(local/'validated_partition_ids.npz') as z:
            assert np.array_equal(z['HR'],np.load(dest/(name+'_HR_edge_ids.npy')))
    campaign=digest(dict(spec=file_hash(dest/'ABLATION_SPEC_v1.md'),config=file_hash(dest/'spec_config.json'),manifest=file_hash(dest/'manifest.json'),common=meta['common_data_id']))
    reg=dict(status='PRE_REGISTERED_BEFORE_FORMAL_SHAM_ABLATION',registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),campaign_id=campaign,
        spec_sha256=file_hash(dest/'ABLATION_SPEC_v1.md'),spec_config_sha256=file_hash(dest/'spec_config.json'),spec_manifest_sha256=file_hash(dest/'manifest.json'),
        common_data_id=meta['common_data_id'],operator=spec['operator'],start_step=200,readouts=spec['readouts'],independent_processes=2,
        repeats=['formal_r1','formal_r2'],conditions=spec['fixture']['conditions'],modes=['Sham','Ablation'],
        comparison_ids={name:digest(dict(campaign=campaign,candidate=c['candidate_manifest']['sha256'],HR=c['HR_edge_ids']['sha256'])) for name,c in spec['candidates'].items()},
        Full_reference=spec['modes']['Full']['source_reference'],FPGA_execution=False,extension_24_conditions_authorized=False)
    dump(HERE/'PRE_RUN_REGISTRATION.json',reg);seal(dest);print(json.dumps(reg,ensure_ascii=False))

if __name__=='__main__':main()
