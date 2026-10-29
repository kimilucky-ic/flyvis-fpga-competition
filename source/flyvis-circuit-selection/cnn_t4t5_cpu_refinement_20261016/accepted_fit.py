"""Reproduce only the accepted CG+short-check path; never run BPTT prototype.

This helper reuses the exact functions executed in train.py. It is a new
syntax-checked handoff entry, NOT a second independent scientific training run.
"""
from train import *

def accepted_main():
    freezecheck(deep=True);(HERE/'training').mkdir();model=fresh_model();x,y=build_training_data(model)
    rng=np.random.default_rng(2026101610);valid_times=np.flatnonzero(np.arange(485)%5==4)
    vi=(rng.integers(0,4,4096)*485+rng.choice(valid_times,4096),rng.integers(0,721,4096))
    dump(HERE/'training/BASELINE_VALIDATION.json',validation(model,x,y,vi))
    val=fit_linear(model,x,y,vi);short=short_validation(model,'ridge');path=HERE/'training/ridge.pt'
    passed=bool(val['pass_gate'] and short['pass_gate'])
    dump(HERE/'TRAINING_GATE.json',dict(status='PASS_TRAINING_GATES' if passed else 'TRAINING_GATES_NOT_PASS',
        pass_gate=passed,one_step=val,short_label=short['label'],short_pass=short['pass_gate'],model_path=str(path),
        old_test_cases_used=False,new_holdout_opened=False,parameters=31168,GPU=0))
    if passed:dump(HERE/'MODEL_FREEZE.json',dict(path=str(path),sha256=sha(path),time_ns=time.time_ns(),gate_sha=sha(HERE/'TRAINING_GATE.json')))
    print('ACCEPTED_PATH_TRAINING_GATE',passed)

if __name__=='__main__':accepted_main()
