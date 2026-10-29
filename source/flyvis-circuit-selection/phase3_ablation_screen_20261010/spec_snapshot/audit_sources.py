"""Read-only architecture audit and frozen ID sets; no neural inference."""
from pathlib import Path
import csv, hashlib, itertools, json
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path(r'C:\Users\hzy72\Documents\ChatGPT')
BUNDLE = ROOT / 'fly/gpu_phase2/artifacts/reference_bundle_gpu_native_v1'
FULL_DIR = ROOT / 'fpga/flyvis-circuit-selection/phase2_20261010/artifacts/full_gpu_reference_a'
DIRECTION = ROOT / 'fly/artifacts/direction_tuning_20261010/direction_metrics_T4_T5.json'
CIDS = ['B_T5c', 'A_T4c', 'C_T4T5_all_centers']

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def arr_digest(a):
    return hashlib.sha256(str(a.dtype).encode() + str(a.shape).encode() + a.tobytes()).hexdigest()

def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def write_json(p, obj):
    if p.exists():
        raise RuntimeError('Preserve existing output: ' + str(p))
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def save_ids(name, ids):
    p = HERE / name
    if p.exists():
        raise RuntimeError('Preserve existing output: ' + str(p))
    a = np.asarray(ids, dtype=np.int64)
    np.save(p, a, allow_pickle=False)
    return {'path': str(p), 'n': len(a), 'sha256': sha(p), 'array_digest': arr_digest(a)}

files = [BUNDLE / x for x in ['identity_manifest.json', 'stimulus_manifest.json', 'stimulus.npy',
         'time.npy', 'conditions.csv', 'initial_state_full.npy', 'expanded_parameters.npz',
         'nodes_full.csv', 'central_node_indices.npy', 'cell_types.npy']]
files += [BUNDLE / 'candidates' / c / f for c in CIDS
          for f in ['candidate_manifest.json', 'node_map.csv', 'edge_partition_ids.npz']]
files += [FULL_DIR / 'run_identity.json', FULL_DIR / 'artifact_manifest.json', FULL_DIR / 'activities_full.npy', DIRECTION]
before = {str(p): sha(p) for p in files}
identity = read_json(BUNDLE / 'identity_manifest.json')
stim_meta = read_json(BUNDLE / 'stimulus_manifest.json')
full_id = read_json(FULL_DIR / 'run_identity.json')
for key in ['checkpoint_sha256', 'source_commit', 'expanded_parameters_sha256', 'initial_state_sha256']:
    assert full_id[key] == identity[key], key
assert sha(BUNDLE / 'expanded_parameters.npz') == identity['expanded_parameters_sha256']
assert sha(BUNDLE / 'initial_state_full.npy') == identity['initial_state_sha256']
assert sha(FULL_DIR / 'activities_full.npy') == full_id['source_full_sha256']
assert sha(BUNDLE / 'stimulus.npy') == full_id['stimulus_sha256'] == stim_meta['stimulus_sha256']
assert sha(BUNDLE / 'time.npy') == full_id['time_axis_sha256'] == stim_meta['time_sha256']
assert sha(BUNDLE / 'conditions.csv') == full_id['conditions_sha256'] == stim_meta['conditions_sha256']
time = np.load(BUNDLE / 'time.npy', allow_pickle=False)
stim = np.load(BUNDLE / 'stimulus.npy', mmap_mode='r', allow_pickle=False)
full = np.load(FULL_DIR / 'activities_full.npy', mmap_mode='r', allow_pickle=False)
assert stim.shape == (4, 485, 1, 721) and stim.dtype == np.float32
assert full.shape == (4, 485, 45669) and full.dtype == np.float32
assert np.array_equal(time, np.arange(485) * 0.005 - 1)
conditions = list(csv.DictReader((BUNDLE / 'conditions.csv').open(encoding='utf-8-sig', newline='')))
assert [(int(x['intensity']), int(x['angle'])) for x in conditions] == [(0, 0), (1, 0), (0, 180), (1, 180)]
nodes = list(csv.DictReader((BUNDLE / 'nodes_full.csv').open(encoding='utf-8-sig', newline='')))
types = np.array([x['cell_type'] for x in nodes])
assert [int(x['global_node_index']) for x in nodes] == list(range(45669))
with np.load(BUNDLE / 'expanded_parameters.npz', allow_pickle=False) as p:
    src, dst, weight = p['source_global'], p['target_global'], p['effective_weight']
    for k in p.files:
        assert arr_digest(p[k]) == identity['expanded_parameter_digests'][k], k
centers = np.load(BUNDLE / 'central_node_indices.npy', allow_pickle=False)
center_types = np.load(BUNDLE / 'cell_types.npy', allow_pickle=False)
assert np.array_equal(types[centers], center_types)
candidate_data, hsets, masks = {}, {}, {}
for cid in CIDS:
    folder = BUNDLE / 'candidates' / cid
    m = read_json(folder / 'candidate_manifest.json')
    h = np.array(m['h_global_node_indices'], dtype=np.int64)
    assert np.all(np.diff(h) > 0) and arr_digest(h) == m['h_indices_digest']
    for k in ['checkpoint_sha256', 'source_commit', 'expanded_parameters_sha256', 'initial_state_sha256']:
        if k in m:
            assert m[k] == identity[k], k
    mask = np.zeros(45669, dtype=bool)
    mask[h] = True
    partition = {'HH': mask[src] & mask[dst], 'RH': ~mask[src] & mask[dst],
                 'HR': mask[src] & ~mask[dst], 'RR': ~mask[src] & ~mask[dst]}
    with np.load(folder / 'edge_partition_ids.npz', allow_pickle=False) as z:
        for k in partition:
            assert np.array_equal(z[k], np.flatnonzero(partition[k]))
            assert len(z[k]) == m['partition_counts'][k]
    hr = np.flatnonzero(partition['HR']).astype(np.int64)
    targets = np.unique(dst[hr])
    names, count = np.unique(types[h], return_counts=True)
    hrw = weight[hr]
    candidate_data[cid] = {
        'n_H': len(h), 'n_R': 45669 - len(h), 'partition_counts': m['partition_counts'],
        'cell_type_counts': dict(zip(names.tolist(), count.tolist())),
        'n_direct_R_targets': len(targets), 'n_unique_incoming_R_sources': len(np.unique(src[partition['RH']])),
        'HR_weight_counts': {'positive': int((hrw > 0).sum()), 'negative': int((hrw < 0).sum()), 'zero': int((hrw == 0).sum())},
        'candidate_manifest': {'path': str(folder / 'candidate_manifest.json'), 'sha256': sha(folder / 'candidate_manifest.json')},
        'H_ids': save_ids(cid + '_H_ids.npy', h),
        'HR_edge_ids': save_ids(cid + '_HR_edge_ids.npy', hr),
        'direct_R_targets': save_ids(cid + '_direct_R_targets.npy', targets),
        'T4_T5_centers_membership': [{'cell_type': str(ct), 'global_node_index': int(i), 'partition': 'H' if mask[i] else 'R'}
                                    for i, ct in zip(centers, center_types) if str(ct).startswith(('T4', 'T5'))],
    }
    hsets[cid], masks[cid] = h, partition
union_h = np.unique(np.concatenate(list(hsets.values())))
common_r = np.setdiff1d(np.arange(45669), union_h).astype(np.int64)
common_downstream = np.intersect1d(np.unique(np.concatenate([dst[np.flatnonzero(masks[c]['HR'])] for c in CIDS])), common_r)
all_t45 = np.flatnonzero(np.char.startswith(types, 'T4') | np.char.startswith(types, 'T5')).astype(np.int64)
outside_t45 = np.intersect1d(all_t45, common_r)
rois = {
    'common_R': save_ids('common_R_ids.npy', common_r),
    'common_direct_downstream_R': save_ids('common_direct_downstream_R_ids.npy', common_downstream),
    'all_T4_T5': save_ids('all_T4_T5_ids.npy', all_t45),
    'common_R_T4_T5': save_ids('common_R_T4_T5_ids.npy', outside_t45),
    'all_65_centers': save_ids('all_65_center_ids.npy', centers),
    'all_8_T4_T5_centers': save_ids('all_8_T4_T5_center_ids.npy', centers[np.char.startswith(center_types, 'T4') | np.char.startswith(center_types, 'T5')]),
}
overlap = []
for a, b in itertools.combinations(CIDS, 2):
    overlap.append({'a': a, 'b': b, 'H_intersection': len(np.intersect1d(hsets[a], hsets[b])),
                    'H_union': len(np.union1d(hsets[a], hsets[b])), 'a_H_subset_b_H': bool(np.isin(hsets[a], hsets[b]).all())})
reclassified = {cid: int((masks[cid]['HR'] & masks['C_T4T5_all_centers']['HH']).sum()) for cid in CIDS[:2]}

# Full-only descriptive checks; primary statistics are specified in the spec,
# and will be computed by the experiment owner. No ablation data is read.
baseline = np.asarray(full[:, 160:200, :], dtype=np.float64).mean(axis=1)
full_readout_check = {}
for name, ids in [('common_direct_downstream_R', common_downstream), ('common_R_T4_T5', outside_t45)]:
    vals = np.asarray(full[:, 200:, ids], dtype=np.float64)
    z = vals - baseline[:, ids][:, None, :]
    eta = 1e-5 + 1e-5 * np.max(np.abs(np.asarray(full[:, :, ids], dtype=np.float64)), axis=(0, 1))
    floor = float(np.sqrt(np.mean((4 * eta) ** 2)))
    polarity = {}
    for pol, c0, c180 in [('OFF', 0, 2), ('ON', 1, 3)]:
        v = z[c0] - z[c180]
        rms = float(np.sqrt(np.mean(v ** 2)))
        polarity[pol] = {'Full_direction_trace_RMS': rms, 'predeclared_tolerance_floor_RMS': floor,
                         'resolved_by_10x_floor_rule': rms > 10 * floor}
    full_readout_check[name] = polarity
historical = [r for r in read_json(DIRECTION) if r['cell_type'] in ['T4c', 'T5c']]
after = {str(p): sha(p) for p in files}
assert before == after
output = {
    'schema': 'flyvis-architect-ablation-source-audit/v1', 'date': '2026-10-10',
    'status': 'PASS_READONLY_SOURCE_AND_IDENTITY_AUDIT', 'evidence_level': 'READONLY_SOURCE_AND_SAVED_FULL_ARRAY_CHECK',
    'new_neural_inference': False, 'new_ablation_executed': False, 'board_operation': False,
    'source_files_unchanged': True, 'source_files_checked': len(files),
    'sources': [{'path': p, 'sha256_before': before[p], 'sha256_after': after[p]} for p in before],
    'model_identity': identity, 'stimulus_shape': list(stim.shape), 'full_shape': list(full.shape),
    'Full_provenance': full_id, 'conditions': conditions,
    'time_windows_zero_based_inclusive': {'prebaseline': [160, 199], 'intervention': [200, 484],
                                         'primary_response': [200, 484], 'motion': [200, 285], 'post_motion': [286, 484]},
    'candidates': candidate_data, 'H_overlap': overlap, 'small_HR_reclassified_joint_HH': reclassified,
    'readout_sets': rois, 'Full_only_direction_readout_check': full_readout_check,
    'historical_24_condition_T4c_T5c': historical,
    'historical_metrics_usage': 'coverage rationale only; not this new ablation result and not a matching a0 Full reference for extension',
}
write_json(HERE / 'source_audit.json', output)
print(json.dumps({'status': output['status'], 'source_files_checked': len(files),
                  'candidates': {c: {k: v for k, v in d.items() if k in ['n_H', 'n_direct_R_targets', 'cell_type_counts', 'T4_T5_centers_membership']} for c, d in candidate_data.items()},
                  'H_overlap': overlap, 'reclassified_HR': reclassified,
                  'readout_counts': {k: v['n'] for k, v in rois.items()}, 'Full_only_check': full_readout_check}, ensure_ascii=False, indent=2))
