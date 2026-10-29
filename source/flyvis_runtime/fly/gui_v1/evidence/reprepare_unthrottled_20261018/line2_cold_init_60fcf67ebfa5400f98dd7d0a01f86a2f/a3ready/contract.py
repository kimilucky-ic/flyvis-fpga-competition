"""Pure validation for camera hardware configuration. No device/network activity."""
import re
from datetime import datetime, timezone
from .control2 import require, BIT_SHA, HWH_SHA, OLD_RUNS, OLD_SESSIONS

CONTRACT='flyvis-camera-joint/v1'
FINISH='finish_window/v1'
CONTRACT_SHA='1d09d7a1c4adb0f5430ccdd05164c10d7b50b97acf83a59d1df0a75e3c34f9ff'
HISTORICAL_RUNS=set(OLD_RUNS)|{'c708f1c9bac14c07ac8f56d59678b95a','90f57cb961f2490bb516426a250bcd8a','46b9591f18db48a193f8a63da688d08c','ac4db863a9e54192824049d82b209c27'}
REASONS=('STEP_LIMIT_COMPLETE','CAPTURE_WINDOW_COMPLETE','USER_STOP')
def hex_value(value,n):return isinstance(value,str) and re.fullmatch('[a-f0-9]{%d}'%n,value) is not None
def capabilities(c):return dict(camera_joint_contract=CONTRACT,normal_finish=FINISH,max_steps=c['max_steps'])
def window(c,now=None,clock=None):
    require(now is None and clock is not None,'AUTHENTICATED_MONOTONIC_CLOCK_REQUIRED')
    return clock.check(c)

def validate(c,*,cpu_fixture=False,now=None,clock=None):
    require(c.get('camera_joint_contract')==CONTRACT and c.get('normal_finish')==FINISH and c.get('contract_sha256')==CONTRACT_SHA,'CAMERA_CONTRACT')
    require(c.get('source_kind')=='real_windows_camera' and c.get('condition_id')=='CURRENT_CAMERA','CAMERA_INPUT_SCOPE')
    require(c.get('input_policy')=='LATEST_CONVERTED_AT_STEP_START_COMMIT_DRIVEN' and c.get('numerical_profile')=='H_A3R1_Q24_R_ORIGINAL_FP32' and c.get('dt_ns')==5000000,'CAMERA_NUMERIC_POLICY')
    require(type(c.get('max_steps')) is int and 1<=c['max_steps']<=60000,'CAMERA_STEP_BOUND')
    require(type(c.get('max_worker_s')) is int and 30<=c['max_worker_s']<=1800,'CAMERA_WORKER_BOUND')
    for key,n in (('run_id',32),('server_session',32),('listener_id',32),('plan_sha256',64),('scope_sha256',64),('initial_full_sha256',64),('initial_H_sha256',64),('mapping_sha256',64),('control_key',64)):
        require(hex_value(c.get(key),n),'CAMERA_CONFIG_'+key)
    require(c['run_id'] not in HISTORICAL_RUNS and c['server_session'] not in OLD_SESSIONS,'CONSUMED_HISTORICAL_IDENTITY')
    require(c.get('bit_sha256')==BIT_SHA and c.get('hwh_sha256')==HWH_SHA,'CAMERA_IMAGE')
    require(isinstance(c.get('boot_id'),str) and bool(c['boot_id']),'CAMERA_BOOT_REQUIRED')
    require(c.get('automatic_retry') is False and c.get('new_loads')==c.get('new_resets')==c.get('new_allocations')==0,'CAMERA_NO_REINITIALIZATION')
    if cpu_fixture:require(c.get('execution_authority')=='CPU_FIXTURE_ONLY' and c.get('test_fixture') is True,'EXPLICIT_CPU_FIXTURE')
    else:require(c.get('execution_authority')=='APPROVED_BY_HUMAN' and c.get('human_authorization_reference')=='EXACT_SCOPE_'+c['scope_sha256'] and c.get('prepared_status')=='PREPARED_FOR_THIS_CAMERA_RUN','NO_HARDWARE_EXECUTION_AUTHORITY')
    window(c,now,clock)
    return c
