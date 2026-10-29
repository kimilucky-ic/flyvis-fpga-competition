"""Seal this new first-delivery folder only; no experiment or other-lane edit."""
import ast
import json
from service import HERE, host_path, load_json, sha


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main():
    tests = load_json(HERE / 'TEST_RESULTS.json')
    assert tests['status'] == 'PASS_CPU_CONTRACT_CACHE_READOUT' and tests['checks'] == 42
    assert tests['neural_steps'] == tests['decoder_forward_calls'] == tests['CUDA_operations'] == 0
    adapter = load_json(HERE / 'AUTORUNNER_ADAPTER.json')
    for key in ('adapter_module', 'readout_module'):
        adapter[key]['sha256'] = sha(adapter[key]['path'])
    b_source = HERE.parents[1] / 'flyvis-circuit-selection/t4t5_criticality_20261011/intervention_adapter.py'
    tree = ast.parse(b_source.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'InterventionAdapter')
    functions = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    assert {'init__', 'step', 'assert_weights_unchanged'} <= set(functions)
    assert {'old_full', 'hex_frame', 'step_id'} <= {a.arg for a in functions['step'].args.args}
    adapter['B_intervention_adapter'] = dict(path=str(b_source), sha256=sha(b_source),
        status='AST_PUBLIC_METHODS_CHECKED; B_REPORTED_SYNTHETIC_CPU_PASS; ACTUAL_ORIGINAL_GPU_BINDING_NOT_RUN_BY_A')
    adapter['pending'][0] = 'B InterventionAdapter supplied; 8 invokes under valid scope; actual original-network GPU hook smoke remains NOT_RUN'
    write(HERE / 'AUTORUNNER_ADAPTER.json', adapter)
    budget = load_json(HERE / 'RESOURCE_BUDGET.json')
    prior_path = HERE.parents[1] / 'flyvis-visual-experiments/artifacts/decoder_cuda_r3/result.json'
    prior = load_json(prior_path)
    budget['historical_evidence']['decoder_historical_stats'] = {k: prior[k] for k in ('model_load', 'inference', 'decode')}
    write(HERE / 'RESOURCE_BUDGET.json', budget)
    # No source/data file from another lane is written, copied or restaged.
    for path in HERE.rglob('*.py'):
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    manifest = dict(schema='flyvis-interface-delivery-manifest/v1', status='PASS_FIRST_DELIVERY_CPU_ONLY',
                    tests=42, new_neural_steps=0, new_decoder_forward_calls=0,
                    CUDA_computation=False, board_operations=0, evidence_level='SOURCE_CHECKPOINT_CPU_UNIT_TEST_AND_ACCEPTED_CACHE_REPLAY',
                    GPU_chunk_equivalence='NOT_RUN', AutoRunner_decoder_plugin='NOT_INTEGRATED',
                    files={str(p.relative_to(HERE)).replace('\\', '/'): sha(p) for p in sorted(HERE.rglob('*'))
                           if p.is_file() and p.name != 'DELIVERY_MANIFEST.json' and '__pycache__' not in p.parts})
    write(HERE / 'DELIVERY_MANIFEST.json', manifest)
    print('PASS_FIRST_DELIVERY_CPU_ONLY', len(manifest['files']), 'files sealed; no GPU/609 rerun')


if __name__ == '__main__':
    main()
