"""Independent static export checks. Does not execute neural dynamics."""
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / 'artifacts'
PRIOR = HERE.parent / 'round1_20261010/artifacts'

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

summary = json.loads((OUT / 'alignment_summary.json').read_text(encoding='utf-8'))
manifest = json.loads((OUT / 'artifact_manifest.json').read_text(encoding='utf-8'))
assert all(sha(OUT / item['path']) == item['sha256'] for item in manifest)
snapshots = summary['input_snapshots_sha256']
snapshot_checks = {path: sha(Path(path)) == digest for path, digest in snapshots.items()}
assert all(snapshot_checks.values()), snapshot_checks

partition_checks = []
for partition in summary['partitions']:
    candidate = partition['candidate']
    rows = list(csv.DictReader((OUT / candidate / 'node_map.csv').open(encoding='utf-8')))
    assert len(rows) == 45669
    assert [int(row['global_node_index']) for row in rows] == list(range(45669))
    h_global = np.array([int(row['global_node_index']) for row in rows if row['partition'] == 'H'])
    for label in ['H', 'R']:
        domain = [row for row in rows if row['partition'] == label]
        assert [int(row['local_index']) for row in domain] == list(range(len(domain)))
        assert len(domain) == partition[label + '_nodes']
    with np.load(PRIOR / candidate / 'static_boundary.npz', allow_pickle=False) as static:
        assert np.array_equal(h_global, static['global_node_id'])
        with np.load(OUT / candidate / 'edge_partition_ids.npz', allow_pickle=False) as edges:
            joined = np.concatenate([edges[label] for label in ['HH', 'RH', 'HR', 'RR']])
            assert np.array_equal(np.sort(joined), np.arange(1513231))
            for label, key in [('HH', 'internal'), ('RH', 'incoming'), ('HR', 'outgoing')]:
                assert np.array_equal(edges[label], static[key + '_edge_id'])
            assert {label: len(edges[label]) for label in edges.files} == partition['edge_counts']
    partition_checks.append(dict(candidate=candidate, full_node_map=True, local_indices_contiguous=True,
        original_edge_ids_exhaustive_and_unique=True, incident_edges_match_original_export=True))

profile_checks = []
csv_rows = list(csv.DictReader((OUT / 'boundary_profiles.csv').open(encoding='utf-8')))
assert len(csv_rows) == len(summary['profiles']) == 9
for row, exported in zip(summary['profiles'], csv_rows):
    n, hh, rh, sources = [row[key] for key in ['H_nodes', 'HH_edges', 'RH_edges', 'incoming_sources']]
    layout = row['layout']
    boundary_scalars = {'CURRENT_AGG': n, 'SOURCE_RAW': sources, 'EDGE_CURRENT': rh}[layout]
    total = 4 * (boundary_scalars + 2 * n)
    extra = {'CURRENT_AGG': 8 * n, 'SOURCE_RAW': 8 * rh + 4 * sources + 4 * n,
        'EDGE_CURRENT': 8 * rh + 4 * n}[layout]
    logical_bytes = 8 * hh + 20 * n + extra
    assert row['request_bytes'] == 4 * (boundary_scalars + n)
    assert row['response_bytes'] == 4 * n
    assert row['total_payload_bytes_per_step'] == total
    assert row['profile_core_logical_bytes'] == logical_bytes
    assert row['ideal_BRAM36_bit_capacity_floor'] == math.ceil(logical_bytes / 4608)
    assert row['external_x_scalars'] == n and row['header_bytes_included'] == 0
    for key, value in exported.items():
        assert str(row[key]) == value, (key, row[key], value)
    profile_checks.append(dict(candidate=row['candidate'], layout=layout, payload_and_storage_formula_match=True))

result = dict(status='PASS_STATIC_EXPORT_ONLY', artifact_entries_verified=len(manifest),
    input_snapshot_checks=snapshot_checks, partition_checks=partition_checks, profile_checks=profile_checks,
    neural_dynamics_executed=False, closed_loop_replacement='NOT_RUN', hardware_validation='NOT_RUN')
(OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(dict(status=result['status'], partitions=len(partition_checks), profiles=len(profile_checks),
    input_hashes_unchanged=all(snapshot_checks.values())), ensure_ascii=False))
