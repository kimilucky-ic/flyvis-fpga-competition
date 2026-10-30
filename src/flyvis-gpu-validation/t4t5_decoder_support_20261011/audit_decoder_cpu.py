"""Checkpoint/type audit only. No neural step, decoder forward or CUDA call."""
import csv
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = REPO.parent / 'fly'
os.environ.update(CUDA_VISIBLE_DEVICES='-1', FLYVIS_ROOT_DIR='/opt/flyvis-phase3-data',
                  MPLBACKEND='Agg', MPLCONFIGDIR='/tmp/flyvis-decoder-audit-mpl',
                  NUMBA_CACHE_DIR='/tmp/flyvis-decoder-audit-numba', PYTHONDONTWRITEBYTECODE='1')
import numpy as np
import torch
torch.set_num_threads(1)
import flyvis
from flyvis import NetworkView


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str) + '\n', encoding='utf-8')


def main():
    dest = HERE / 'cpu_audit_r1'
    dest.mkdir(exist_ok=False)
    assert flyvis.device.type == 'cpu'
    model = Path('/opt/flyvis-visual-experiments-data/results/flow/0000/000')
    view = NetworkView(model)
    checkpoint = Path(view.get_checkpoint('best'))
    checkpoint_sha = sha(checkpoint)
    assert checkpoint_sha == 'd0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'
    expected = torch.load(checkpoint, map_location='cpu', weights_only=False)['decoder']['flow']
    decoder = view.init_decoder(checkpoint='best')['flow']
    decoder.eval()
    flags = {name: module.training for name, module in decoder.named_modules()}
    assert not any(flags.values())
    assert all(torch.equal(decoder.state_dict()[k].cpu(), v) for k, v in expected.items())
    before = {k: v.detach().cpu().clone() for k, v in decoder.state_dict().items()}
    types = view.connectome.output_cell_types[:].astype(str).tolist()
    ids = np.asarray(decoder.dvs_channels.output_indices, dtype=np.int64)
    all_types = view.connectome.nodes.type[:].astype(str)
    u = view.connectome.nodes.u[:].astype(np.int64)
    v = view.connectome.nodes.v[:].astype(np.int64)
    assert ids.shape == (34, 721)
    assert len(all_types) == 45669
    for ch, ct in enumerate(types):
        assert np.array_equal(ids[ch], np.flatnonzero(all_types == ct))
        assert np.array_equal(u[ids[ch]], decoder.u - decoder.u.min() - 15)
        assert np.array_equal(v[ids[ch]], decoder.v - decoder.v.min() - 15)
    # Exercise original LayerActivity gather, not the decoder forward.
    sentinel = torch.arange(45669, dtype=torch.float32).reshape(1, 1, -1)
    decoder.dvs_channels.update(sentinel)
    assert np.array_equal(decoder.dvs_channels.output.numpy()[0, 0], ids)
    target_types = [f'T{n}{s}' for n in (4, 5) for s in 'abcd']
    target = np.flatnonzero(np.isin(all_types, target_types)).astype(np.int64)
    assert len(target) == 5768
    np.save(dest / 'decoder_input_global_ids.npy', ids)
    np.save(dest / 't4t5_global_ids.npy', target)
    np.save(dest / 'hex_coordinates_uv.npy', np.column_stack([u[ids[0]], v[ids[0]]]))
    with (dest / 'decoder_input_nodes.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['decoder_channel', 'cell_type', 'hex_index', 'global_id', 'u', 'v'])
        for ch, ct in enumerate(types):
            writer.writerows((ch, ct, j, int(g), int(u[g]), int(v[g])) for j, g in enumerate(ids[ch]))
    first_conv = decoder.base[0]
    weights = first_conv.weight.detach().cpu().numpy()
    channels = []
    for ch, ct in enumerate(types):
        w = weights[:, ch]
        channels.append(dict(channel=ch, cell_type=ct, count=721,
                             global_id_min=int(ids[ch].min()), global_id_max=int(ids[ch].max()),
                             directly_reads_T4_T5=ct in target_types,
                             first_conv_nonzero_taps=int(np.count_nonzero(w)),
                             first_conv_abs_weight_sum=float(np.abs(w.astype(np.float64)).sum())))
    b_map = REPO / 'flyvis-circuit-selection/t4t5_criticality_20261011/cpu_preparation_r1/decoder_type_global_ids.npy'
    b_ids = np.load(b_map, allow_pickle=False)
    # B stores eight T4/T5 channels rather than the full 34 if appropriate.
    b_equal = np.array_equal(b_ids, ids) or np.array_equal(b_ids, ids[4:12])
    assert b_equal, ('B decoder map', b_ids.shape)
    state_digest = hashlib.sha256()
    for k, a in sorted(before.items()):
        state_digest.update(k.encode() + b'\0')
        state_digest.update(str(a.dtype).encode() + b'\0')
        state_digest.update(json.dumps(list(a.shape)).encode() + b'\0')
        state_digest.update(a.contiguous().numpy().tobytes())
    assert all(torch.equal(decoder.state_dict()[k].cpu(), a) for k, a in before.items())
    source_names = ['task/decoder.py', 'utils/activity_utils.py', 'datasets/sintel_utils.py',
                    'datasets/sintel.py', 'datasets/rendering/eye.py', 'datasets/rendering/utils.py']
    source = BASE / 'upstream/flyvis/flyvis'
    result = dict(status='PASS_CPU_DECODER_CHECKPOINT_TYPE_AUDIT', execution_kind='actual_CPU_structure_audit',
                  neural_steps=0, decoder_forward_calls=0, CUDA_operations=0, board_operations=0,
                  command=[sys.executable, *sys.argv], python=sys.version, torch=torch.__version__,
                  numpy=np.__version__, platform=platform.platform(), flyvis=flyvis.__version__,
                  source_commit='92b3845cc426dd309a1a0e1b3890156c42e14021',
                  checkpoint_path=str(checkpoint), checkpoint_sha256=checkpoint_sha,
                  decoder_class=type(decoder).__name__, decoder_state_digest_algorithm='sorted key+NUL+torch.dtype+NUL+JSON shape+NUL+C-order bytes',
                  decoder_state_sha256=state_digest.hexdigest(), decoder_equals_checkpoint_before_after=True,
                  module_training_flags=flags, decoder_config=view.dir.config.task.decoder.flow.to_dict(),
                  task_config=view.dir.config.task.to_dict(), channels=channels, input_shape=[None, None, 45669],
                  decoder_spatial_input_shape=[None, None, 34, 721], output_shape=[None, None, 2, 721],
                  square_storage_shape=[int(decoder.H), int(decoder.W)],
                  T4_T5_count=len(target), T4_T5_channels=list(range(4, 12)),
                  B_decoder_map_equal=True, B_decoder_map_shape=list(b_ids.shape),
                  node_type_counts={ct: int(np.count_nonzero(all_types == ct)) for ct in np.unique(all_types)},
                  source_files={name: dict(path=str(source / name), sha256=sha(source / name)) for name in source_names},
                  artifacts={p.name: sha(p) for p in dest.iterdir() if p.is_file()})
    dump(dest / 'result.json', result)
    print(json.dumps({k: result[k] for k in ('status', 'decoder_class', 'T4_T5_count', 'square_storage_shape',
                                           'decoder_state_sha256', 'neural_steps', 'CUDA_operations')}), flush=True)


if __name__ == '__main__':
    main()
