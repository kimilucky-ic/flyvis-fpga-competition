from pathlib import Path
import json
import numpy as np
from numeric_profile_sweep import load_graph, qencode
from prepare_hls_fixtures import sha256

HERE = Path(__file__).resolve().parent
B = HERE.parents[1] / 'flyvis-circuit-selection/phase3_20261010'


def write_hex(path, values, bits):
    digits = (bits + 3) // 4
    mask = (1 << bits) - 1
    with path.open('w', encoding='ascii', newline='\n') as f:
        for value in values:
            f.write(f'{int(value) & mask:0{digits}x}\n')


def main():
    manifest = json.loads((HERE / 'testdata_animation_q22/fixture_manifest.json').read_text())
    s, t, eid, src, dst, weights, boundary = load_graph(
        B / 'input_bundle/static_boundary_gpu_native.npz', B / 'c_reference/SOURCE_RAW_step_io.npz')
    rom = HERE / 'rom'
    rom.mkdir(exist_ok=True)
    coded = np.where(boundary, src, src | (1 << 11))
    wq = qencode(weights, 20)
    packed = [(int(a) << 29) | (int(b) << 22) | (int(w) & ((1 << 22) - 1))
              for a, b, w in zip(coded, dst, wq)]
    neurons = [(int(inv) & ((1 << 29) - 1)) << 29 | (int(bias) & ((1 << 29) - 1))
               for inv, bias in zip(qencode(s['inv_max_tau_dt'], 22), qencode(s['bias'], 22))]
    write_hex(rom / 'edges_q22.mem', packed, 41)
    write_hex(rom / 'neurons_q22.mem', neurons, 58)
    for prefix, leaf in [('requests', 'requests_i32le.bin'), ('expected', 'expected_i32le.bin')]:
        p = HERE / 'testdata_animation_q22' / leaf
        key = 'request_sha256' if prefix == 'requests' else 'expected_sha256'
        if sha256(p) != manifest[key]:
            raise ValueError(f'Fixture changed: {p}')
        write_hex(rom / f'animation_{prefix}_q22.mem', np.fromfile(p, dtype='<i4'), 32)
    result = {'evidence_level': 'ROM_DATA_PREPARATION', 'edge_records': 6537,
              'edge_width_bits': 41, 'edge_order': 'ascending original global edge ID',
              'neuron_records': 67, 'neuron_width_bits': 58,
              'requests': 801, 'words_per_request': 1498,
              'comparison_id': manifest['comparison_id'],
              'files': {p.name: sha256(p) for p in sorted(rom.glob('*.mem'))}}
    (rom / 'manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
