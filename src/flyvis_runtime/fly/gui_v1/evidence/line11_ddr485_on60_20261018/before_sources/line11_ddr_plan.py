"""Two fixed, hash-bound plans only. No inference, device imports or discovery."""
import hashlib
import json
from pathlib import Path

PLAN32_SHA='bfb2e1665634026101d67c4a73f4b7326732943678fe808820a26e6337c83963'
STARTUP_FILES=('line11_ddr_board.py','line11_ddr_bridge.py','line11_display_client.py','line11_ddr_plan.py')


def load_plan(root,steps):
    root=Path(root)
    if steps==3:
        inp=(root/'inputs.bin').read_bytes();state=(root/'expected_states.bin').read_bytes()
        plan_id='ACCEPTED_DDR3_FRAME0_1_0'
    elif steps==32:
        raw=(root/'RUN_PLAN.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=PLAN32_SHA:raise ValueError('DDR32_PLAN_MANIFEST_CHANGED')
        m=json.loads(raw)
        if m['steps']!=32 or m['dt_s']!=.005:raise ValueError('DDR32_PLAN_SCOPE')
        for name in ('plan_inputs.bin','plan_expected_states.bin'):
            b=(root/name).read_bytes();info=m['files'][name]
            if len(b)!=info['bytes'] or hashlib.sha256(b).hexdigest()!=info['sha256']:
                raise ValueError('DDR32_PLAN_DATA_CHANGED '+name)
        inp=(root/'plan_inputs.bin').read_bytes();state=(root/'plan_expected_states.bin').read_bytes();plan_id=m['plan_id']
    else:raise ValueError('DDR_ONLY_VERIFIED_3_OR_32_STEP_PLANS')
    if len(inp)!=steps*2884 or len(state)!=steps*182676:raise ValueError('DDR_PLAN_COMPLETE_ARRAYS_REQUIRED')
    return inp,state,plan_id
