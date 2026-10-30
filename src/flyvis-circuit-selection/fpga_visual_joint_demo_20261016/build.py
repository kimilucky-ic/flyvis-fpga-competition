"""Prepare one owned GPU/FPGA/video run. CPU/files only; no board connection."""
import ast, difflib, hashlib, json, pathlib, secrets, shutil, sys, uuid, zipfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
source = ROOT/'flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_handoff3_20261016'
assert not (HERE/'PLAN.json').exists(), 'NEW_DIRECTORY_ONLY'
sys.path.insert(0, str(ROOT.parent/'fly/gui_v1'))
from hybrid_full485 import Full485Contract
c = Full485Contract()
initial, h_words, _ = c.initial()
import numpy as np
np.save(HERE/'initial_full.npy', initial)
(HERE/'initial_H.bin').write_bytes(h_words)
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
previous = json.loads((HERE.parent/'cnn_t4t5_gpu_visual_stream_20261016/PLAN.json').read_text(encoding='utf-8'))
oldplan = json.loads((source/'PLAN.json').read_text(encoding='utf-8'))
run, session = uuid.uuid4().hex, uuid.uuid4().hex
count = 1000
package = HERE/'line4board'
package.mkdir(exist_ok=True)
changes = []
for src in (source/'a3handoff3').glob('*.py'):
    text = src.read_text(encoding='utf-8')
    updated = text
    if src.name == 'driver.py':
        updated = updated.replace('MAX_REQUESTS = 3', 'MAX_REQUESTS = 1000')
        updated = updated.replace('Only model steps0..2 epoch0, strictly sequential', 'Only this plan steps0..999 epoch0, strictly sequential')
    if src.name in ('neural_session.py', 'manual_transport.py', 'evidence.py', 'light_evidence.py'):
        replacements = {
            'driver.commits < 3:':'driver.commits < 1000:',
            'time.monotonic() + 60':'time.monotonic() + 600',
            'self.driver.requests == self.driver.commits == 3':'self.driver.requests == self.driver.commits == 1000',
            "requests=3, commits=3":"requests=1000, commits=1000",
            'self.requests != 3':'self.requests != 1000',
            'self.acks != 3':'self.acks != 1000',
            "record.get('requests') != 3":"record.get('requests') != 1000",
            "record.get('commits') != 3":"record.get('commits') != 1000",
            'self.requests!=3':'self.requests!=1000',
            'self.acks!=3':'self.acks!=1000',
            "record.get('requests')!=3":"record.get('requests')!=1000",
            "record.get('commits')!=3":"record.get('commits')!=1000",
            'requests=3,acks=3':'requests=1000,acks=1000',
            'requests=3, acks=3':'requests=1000, acks=1000',
        }
        for before, after in replacements.items(): updated = updated.replace(before, after)
    if src.name == 'prepare.py':
        continue
    ast.parse(updated)
    if updated == text:
        (package/src.name).write_bytes(src.read_bytes())
    else:
        (package/src.name).write_text(updated, encoding='utf-8', newline='\n')
    if updated != text:
        changes.extend(difflib.unified_diff(text.splitlines(True), updated.splitlines(True), fromfile='accepted/'+src.name, tofile='line4board/'+src.name))
# Keep the full numerical transaction body unchanged; only quota constants differ.
def run_body(text):
    tree=ast.parse(text)
    return ast.dump(next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='run'),include_attributes=False)
assert run_body((package/'driver.py').read_text(encoding='utf-8')) == run_body((source/'a3handoff3/driver.py').read_text(encoding='utf-8'))
assert sha(package/'protocol.py') == sha(source/'a3handoff3/protocol.py')
(HERE/'BOARD_SCOPE_ONLY.diff').write_text(''.join(changes), encoding='utf-8')
plan = dict(schema='line4-actual-FPGA-visual/v1', run_id=run, server_session=session,
    condition='MP4_ON75', max_requests=count, max_commits=count, dt=.005,
    model_seconds=5, source_frames=500, source_fps=100, decoder_interval=10,
    numerical_profile='H_A3R1_Q24_R_ORIGINAL_FP32', Full_comparator='ORIGINAL_FP32_SAME_CANONICAL_A0',
    CNN='NOT_EXECUTED_THIS_RUN', initial_full_sha256=hashlib.sha256(initial.tobytes()).hexdigest(),
    initial_H_sha256=hashlib.sha256(h_words).hexdigest(), initial_file_sha256=sha(HERE/'initial_full.npy'),
    bit_sha256=c.wire.BIT_SHA, hwh_sha256=c.wire.HWH_SHA, mapping_sha256=c.mapping_sha,
    expected_boot_id=oldplan['expected_boot_id'], kernel_id=oldplan['kernel_id'],
    source_run=oldplan['run_id'], source_session=oldplan['server_session'], source_requests=3,
    board_host='192.168.2.99', pc_host='192.168.2.89', control_port=5781, neural_port=5768,
    new_loads=0,new_resets=0,new_allocations=0,new_kernels=0,automatic_retry=False,
    max_compute_seconds=600,max_worker_seconds=900, max_session_seconds=900,
    max_queue_seconds=15, GPU_processes=1,
    assets={k:previous['assets'][k] for k in ['video','sampler','full','r_only','decoder','decoder_contract','runner_lease','identity','parameters']},
    runtime=previous['runtime'], H_global_ids=c.h.tolist(),R_global_ids=c.r.tolist(),
    preparation_MMIO_reads=oldplan['preparation_MMIO_reads'],
    acceptance=dict(PL_max_integer_error=0,native_H_updates=0,teacher_correction=0,
        R_atol=1e-5,R_rtol=1e-5,chemical_atol=1e-5,chemical_rtol=1e-5,
        visual_visible_running_ACK_min=5, all_steps_and_feedback_checked=True,
        Full_functional_comparison='REPORT_DIFFERENCE_NO_EQUIVALENCE_CLAIM',
        new_board_fault_injection='NOT_PERFORMED; only owned CPU malformed-input tests'),
    user_authorization='请加入fpga的板卡…结合出来后跑通一次然后检测可靠性…视频要展示',
    board_reuse='known healthy completed3 service, fresh identity and own files; preserve source and buffer ownership',
    control_key=secrets.token_hex(32))
# This control key is a local run-only HMAC identity, never a board login credential.
for key in ['control_key']:
    assert plan[key]
def write(name,value): (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('PLAN.json',plan)
write('BUILD_CHECKS.json',dict(PL_run_AST_unchanged=True,wire_protocol_byte_identical=True,
    counts=count,new_GPU_computations=0,new_board_operations=0,initial_H_quantized_once=True))
print(json.dumps(dict(run_id=run,server_session=session,initial_full_sha256=plan['initial_full_sha256'],
    initial_H_sha256=plan['initial_H_sha256'],model_steps=count,board_loads=0,board_resets=0)))
