"""One actual bounded CPU batch; immutable old states, no native H in CNN."""
from core import *
import uuid


def main():
    registration = check(deep=True)
    assert not (HERE/'runs').exists(), 'Never retry over this output'
    assert memory()['available_bytes'] >= 2*1024**3
    assert shutil.disk_usage(HERE).free >= 10*1024**3
    start = time.perf_counter(); ident = str(uuid.uuid4()); m = ref.mapping()
    model = ref.model_from(MODEL); initial = torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    decoder = ref.CPUDecoder(); results = []; counter = dict(native_H_guard_violations=0)
    def forbidden(*args, **kwargs):
        counter['native_H_guard_violations'] += 1
        raise RuntimeError('FORBIDDEN_ORIGINAL_TARGET_UPDATE_IN_CNN')
    for ci, case in enumerate(load(HERE/'INPUTS.json')):
        assert sha(case['path']) == case['sha256']
        pixels = torch.from_numpy(np.load(case['path']))
        for mode in ['Full', 'CNN']+(['Sham'] if ci == 0 else []):
            if time.perf_counter()-start > 600: raise TimeoutError('TOTAL_CPU_BUDGET')
            assert sha(MODEL) == MODEL_SHA
            tick = time.perf_counter(); out = HERE/'runs'/case['id']/mode; out.mkdir(parents=True)
            n = case['steps']; state = initial.clone(); failure = None; count = 0; maximum = 0.
            cnn = CNNService(model, m); r = ref.r_service() if mode != 'Full' else None
            engine = ClosedLoop(r, cnn, initial, m, ident+case['id']) if mode == 'CNN' else None
            # Full and exactH objects are never created for the CNN run.
            _, _, _, params = ref.source() if mode != 'CNN' else (None, None, None, None)
            full = OriginalTargets(params, np.arange(45669)) if mode == 'Full' else None
            exact = OriginalTargets(params, m['H']) if mode == 'Sham' else None
            del params
            states = np.lib.format.open_memmap(out/'states_raw.npy', mode='w+', dtype=np.float32, shape=(n, 45669))
            original_step = OriginalTargets.step
            if mode == 'CNN': OriginalTargets.step = forbidden
            try:
                with (out/'chain.jsonl').open('x', encoding='utf-8') as stream:
                    for k in range(n):
                        if time.perf_counter()-start > 600: raise TimeoutError('TOTAL_CPU_BUDGET')
                        try:
                            if mode == 'CNN': candidate, chain = engine.step(pixels[k], k)
                            else:
                                old = state
                                if mode == 'Full': candidate = full.step(old, pixels[k])
                                else:
                                    rr = r.step(old, pixels[k], step_id=k, run_id=ident, condition_id=case['id'])
                                    hh = exact.step(old, pixels[k]); candidate = torch.empty_like(old)
                                    candidate[m['H']] = hh; candidate[m['R']] = rr.activity
                                if not torch.isfinite(candidate).all() or candidate.abs().max() > 100:
                                    raise ValueError('NO_COMMIT_STABILITY_ENVELOPE')
                                chain = dict(step=k, old=digest(old), input=digest(pixels[k]), new=digest(candidate),
                                    time=k*DT, next_time=(k+1)*DT, committed=True)
                        except (ValueError, RuntimeError) as exc:
                            failure = dict(step=k, error=repr(exc), committed=False); break
                        state = candidate; states[k] = state.numpy(); count += 1
                        maximum = max(maximum, float(state.abs().max())); stream.write(json.dumps(chain)+'\n')
                        if (k+1)%500 == 0:
                            print(json.dumps(dict(stage='PROGRESS', case=case['id'], mode=mode, committed=count,
                                total=n, wall_s=time.perf_counter()-tick)), flush=True)
            finally:
                OriginalTargets.step = original_step
                states.flush()
            np.save(out/'final.npy', state.numpy())
            valid = dict(allocated_rows=n, valid_rows=count, invalid_range=[count, n], failure=failure,
                         rule='Only states_raw[:valid_rows] are committed; never analyze unwritten tail')
            dump(out/'VALIDITY.json', valid)
            flow = decoder.decode(states[:count]) if count else np.empty((0, 2, 721), np.float32)
            np.save(out/'flow.npy', flow); del states
            result = dict(case=case['id'], group=case['group'], mode=mode, run_uuid=ident, valid_steps=count,
                expected_steps=n, complete=count == n, failure=failure, maximum_abs=maximum,
                native_H_updates=0 if mode == 'CNN' else full.calls if full is not None else exact.calls,
                CNN_calls=cnn.calls if mode == 'CNN' else 0, native_H_guard_active=mode == 'CNN',
                teacher_corrections=0, wall_s=time.perf_counter()-tick, actual_CPU=True)
            dump(out/'RESULT.json', result); results.append(result)
            print(json.dumps(result), flush=True)
    decoder.assert_unchanged(); assert sha(MODEL) == MODEL_SHA; check(deep=True)
    dump(HERE/'EXECUTION.json', dict(status='ACTUAL_FROZEN_CNN_CPU_BATCH_COMPLETE', records=results,
        valid_commits=sum(z['valid_steps'] for z in results), wall_s=time.perf_counter()-start,
        model_unchanged=True, decoder_recursive_eval_and_state_unchanged=True, training_updates=0,
        GPU=0, board=0, **counter))


if __name__ == '__main__':
    try: main()
    except BaseException as exc:
        dump(HERE/('FAILURE_run_'+str(time.time_ns())+'.json'), dict(error=repr(exc), retry=False)); raise
