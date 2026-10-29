"""Fixed, hash-bound plans only. No inference, device imports or discovery."""
import hashlib
import json
from pathlib import Path

PLAN32_SHA='bfb2e1665634026101d67c4a73f4b7326732943678fe808820a26e6337c83963'
PLAN485_SHA='181f26ee30371043a22565136ad01d7606ace8799ea6fd6e7767d7ab1b9a25db'
STARTUP_FILES=('line11_ddr_board.py','line11_ddr_bridge.py','line11_display_client.py','line11_ddr_plan.py')


def plan_directory(here,release,steps):
    if steps==3:return Path(release)
    if steps==32:return Path(here)/'evidence/line11_ddr32_20261018/plan'
    if steps==485:return Path(here)/'evidence/line11_ddr485_on60_20261018/plan'
    raise ValueError('DDR_ONLY_VERIFIED_3_32_OR_485_STEP_PLANS')


def plan_metadata(root,steps):
    if steps==3:return dict(plan_id='ACCEPTED_DDR3_FRAME0_1_0',input_time_offset_s=0.)
    return json.loads((Path(root)/'RUN_PLAN.json').read_bytes())


def load_plan(root,steps,expected_sha=None):
    root=Path(root)
    if steps==3:
        inp=(root/'inputs.bin').read_bytes();state=(root/'expected_states.bin').read_bytes()
        plan_id='ACCEPTED_DDR3_FRAME0_1_0'
    elif steps in (32,485):
        raw=(root/'RUN_PLAN.json').read_bytes()
        pin={32:PLAN32_SHA,485:PLAN485_SHA}[steps]
        if expected_sha is not None:pin=expected_sha
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('DDR_PLAN_MANIFEST_CHANGED')
        m=json.loads(raw)
        if m['steps']!=steps or m['dt_s']!=.005:raise ValueError('DDR_PLAN_SCOPE')
        if pin not in (PLAN32_SHA,PLAN485_SHA):
            if steps!=485 or m.get('input_kind')!='recorded_camera_flyvis' or m['initial_state']['sha256']!='d276601573420bf787a81ffa8c81f2da3499a20df2bb858f6082c2e449ff564f':
                raise ValueError('DDR_CAMERA_PLAN_SCOPE')
            if m['reference']['checkpoint_sha256']!='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f' or m['input_time_offset_s']!=0. or len(m['source_frames'])!=485:
                raise ValueError('DDR_CAMERA_MODEL_OR_TIMELINE')
        blobs={}
        for name in ('plan_inputs.bin','plan_expected_states.bin'):
            b=(root/name).read_bytes();info=m['files'][name]
            if len(b)!=info['bytes'] or hashlib.sha256(b).hexdigest()!=info['sha256']:
                raise ValueError('DDR_PLAN_DATA_CHANGED '+name)
            blobs[name]=b
        inp=blobs['plan_inputs.bin'];state=blobs['plan_expected_states.bin'];plan_id=m['plan_id']
    else:raise ValueError('DDR_ONLY_VERIFIED_3_32_OR_485_STEP_PLANS')
    if len(inp)!=steps*2884 or len(state)!=steps*182676:raise ValueError('DDR_PLAN_COMPLETE_ARRAYS_REQUIRED')
    return inp,state,plan_id
