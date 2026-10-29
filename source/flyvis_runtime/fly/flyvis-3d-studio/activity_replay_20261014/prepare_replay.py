"""Read-only adapter: saved FlyVis arrays -> explicitly labelled type means."""
from pathlib import Path
import csv, hashlib, json
from datetime import datetime, timezone
import numpy as np

ROOT = Path(__file__).resolve().parent
STUDIO = ROOT.parent
ANATOMY = STUDIO / 'anatomy_trial_20261013'
def sha(p):
    return hashlib.file_digest(open(p, 'rb'), 'sha256').hexdigest()

def main():
    meta = json.loads((STUDIO / 'evaluation_20261013/models/flyvis_full/metadata.json').read_text())
    sources = {Path(s['path']).name: s for s in meta['sources']}
    used = ['nodes_full.csv', 'activities_full.npy', 'activity_time.npy', 'run_identity.json']
    for name in used:
        assert sha(sources[name]['path']) == sources[name]['sha256'], name
    rows = list(csv.DictReader(open(sources['nodes_full.csv']['path'])))
    raw = np.load(sources['activities_full.npy']['path'], mmap_mode='r')
    assert raw.ndim == 3 and raw.shape[0] == 1 and raw.shape[2] == len(rows)
    values = raw[0]
    time = np.load(sources['activity_time.npy']['path'])
    assert values.shape[0] == len(time) and np.all(np.diff(time) > 0)
    selected = json.loads((ANATOMY / 'source/selection.json').read_text(encoding='utf-8-sig'))
    columns, objects = [], []
    for item in selected:
        indices = [i for i, r in enumerate(rows) if r['cell_type'] == item['type']]
        assert indices and all(int(rows[i]['global_node_index']) == i for i in indices)
        mean = values[:, indices].mean(axis=1, dtype=np.float64)
        assert np.isfinite(mean).all()
        swc = ANATOMY / 'data/swc' / (item['body_id'] + '.swc')
        objects.append(dict(type=item['type'], body_id=item['body_id'], name=f"{item['type']} | {item['body_id']}",
                            swc=str(swc), swc_sha256=sha(swc), swc_units='8 nm',
                            mapping='type_mean_not_individual_correspondence', model_node_ids=[int(rows[i]['global_node_index']) for i in indices],
                            count=len(indices), color_min=float(mean.min()), color_max=float(mean.max())))
        columns.append(mean)
    np.savez(ROOT / 'replay.npz', activity=np.stack(columns, axis=1), time=time)
    rois = [dict(name=name, path=str(ANATOMY / 'data/roi' / f'{name}.ngmesh'), segment_id=seg, color=color)
            for name, seg, color in [('ME(R)',48,'#689baa'),('LO(R)',44,'#9694b9'),('LOP(R)',46,'#c0ad7e')]]
    for roi in rois:
        roi['sha256'] = sha(roi['path'])
    config = dict(title='FlyVis · ON60', anatomy='Janelia Optic Lobe v1.1',
                  source_url='https://www.janelia.org/node/69305', activity_file='replay.npz',
                  units='original_model_units', mapping_label='同类型模型活动均值 · 非个体对应',
                  scientific_boundary='保存的软件计算结果回放；非生物测量，非 FPGA 实板计算',
                  color_rule='Fixed type identity hue. Shared full-record magnitude domain [0,M]. b=0.38+0.62*clip(abs(type_mean)/M,0,1); rendered sRGB=b*identity sRGB. Signed values and zero baseline retained in overview/curves. No per-frame/per-type normalization or time interpolation.',
                  frame_count=len(time), dt_s=float(np.median(np.diff(time))), objects=objects, rois=rois,
                  sources=[sources[n] for n in used], model=meta['original_metadata'],
                  created_utc=datetime.now(timezone.utc).isoformat(), replay_sha256=sha(ROOT / 'replay.npz'))
    (ROOT / 'model.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(frames=len(time), types=[o['type'] for o in objects], time_range=time[[0,-1]].tolist(),
                          range_by_type=[[o['color_min'],o['color_max']] for o in objects], source_hashes_verified=True), indent=2))

if __name__ == '__main__':
    main()
