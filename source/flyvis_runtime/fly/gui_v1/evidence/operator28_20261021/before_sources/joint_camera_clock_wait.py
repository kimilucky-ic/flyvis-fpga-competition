"""Explicit human-wait budget; original clock algorithm in an isolated module.

Only the administrative proof age changes for the new declared profile. Clock
jump/rate/boot checks, authenticated proofs, numerical steps and COMMIT/ACK stay
unchanged. The compute worker starts its separate 300-second budget on Start.
"""
import importlib.util,json,sys,uuid

PROFILE='HUMAN_WAIT_1800S_COMPUTE_300S/v1'
WAIT_S=1800

def scoped_clock(original,config,scope):
    if not config.get('clock_wait_profile'):
        if scope.get('clock_wait_profile'):raise ValueError('CLOCK_WAIT_CONFIG_MISMATCH')
        return original
    if not (config.get('clock_wait_profile')==scope.get('clock_wait_profile')==PROFILE
        and config.get('clock_wait_s')==scope.get('clock_wait_s')==WAIT_S
        and config['max_worker_s']==scope['max_worker_s']==300
        and config.get('run_duration_s')==scope.get('run_duration_s')
        and (scope.get('run_duration_s') is None or (type(scope['run_duration_s']) is int and 1<=scope['run_duration_s']<=60))
        and config['max_steps']==scope['max_steps'] and 1<=scope['max_steps']<=(12000 if scope.get('run_duration_s') else 100 if
            config.get('live_response_hz')==scope.get('live_response_hz')==5 else 32)
        and config['automatic_retry'] is scope['automatic_retry'] is False):
        raise ValueError('CLOCK_WAIT_PROFILE_OR_COMPUTE_BOUND')
    # Do not modify any old helper module or service instance. Relative imports
    # keep using the already pinned control helpers; this clock has new globals.
    name=original.__package__+'._human_wait_clock_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,original.__file__)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    if module.MAX_AGE_NS!=300_000_000_000:raise ValueError('CLOCK_WAIT_ORIGINAL_POLICY_CHANGED')
    module.MAX_AGE_NS=WAIT_S*1_000_000_000
    return module

def compute_alive(started,now,limit=300):
    """Preparation is scope-bounded; compute is separately bounded after Start."""
    return started is None or 0<=now-started<limit
