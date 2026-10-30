"""Read-only Line11 -> Line2 preparation. No GPU/PYNQ/socket/board execution."""
import ast,hashlib,importlib.util,json,sys
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import numpy as np

OUT=Path(__file__).resolve().parent;GUI=OUT.parents[1];FPGA=GUI.parent.parent/'fpga'
sys.path.insert(0,str(GUI))
from live_protocol import load,sha,write,host_path
from spatial_state import SpatialRegistry

candidate=FPGA/'flyvis-lossless-study/hole_pipeline_20261016'
baseline=FPGA/'flyvis-lossless-study/pipeline100_20261015/delivery_100mhz'
seal=load(candidate/'FINAL_MANIFEST_SHA256.json');audit=load(candidate/'AUDIT_soc_r2.json')
base_seal=load(baseline/'release_manifest.json')
source_names=['AUDIT_soc_r2.json','flyvis_driver.py','frame_stepper.py',
              'soc_r2/release/flyvis_full.bit','soc_r2/release/flyvis_full.hwh']
source_names += [n for n in seal if n.startswith('images/')]
assert len([n for n in source_names if n.startswith('images/')])==50
for name in source_names:assert sha(candidate/name)==seal[name]['sha256'],name
assert audit['status']=='PASS_FULL_SOC_100MHZ_ROUTE_LOCAL_ARTIFACTS_ONLY' and audit['board_operations']==0
assert audit['nodes']==45669 and audit['edges']==1513231 and audit['clock_MHz']==100
for name in ('flyvis_driver.py','frame_stepper.py'):
    ast.parse((candidate/name).read_text(encoding='utf-8'),feature_version=(3,8))
for name in ('PROVENANCE.json','input_frame0.bin','expected_state1.bin'):
    assert sha(baseline/name)==base_seal[name]['sha256'],name
for name in [n for n in source_names if n.startswith('images/')]:
    assert sha(candidate/name)==base_seal['sources/'+name]['sha256'],name

provenance=load(baseline/'PROVENANCE.json');gui=load(GUI/'live_registry.json')
assert provenance['commit']==gui['model']['source_commit']
assert provenance['checkpoint_sha256']==gui['model']['checkpoint_sha256']
tree=ET.parse(candidate/'soc_r2/release/flyvis_full.hwh')
mods={m.get('MODTYPE'):m for m in tree.iter('MODULE') if m.get('MODTYPE') in ('processing_system7','flyvis_soc_ip')}
params=lambda m:{p.get('NAME'):p.get('VALUE') for p in m.iter('PARAMETER')}
assert params(mods['flyvis_soc_ip'])['C_BASEADDR']=='0x43C30000'
assert params(mods['processing_system7'])['PCW_FPGA0_PERIPHERAL_FREQMHZ']=='100'

frame=(baseline/'input_frame0.bin').read_bytes();expected=(baseline/'expected_state1.bin').read_bytes()
inputs=np.frombuffer(frame,dtype='<f4');full=np.frombuffer(expected,dtype='<f4')
assert inputs.shape==(721,) and full.shape==(45669,) and np.isfinite(full).all()
assert np.isfinite(inputs).all() and np.all((inputs>=0)&(inputs<=1))
hex_bits=lambda p:np.array([int(x,16) for x in p.read_text().split()],dtype='<u4')
assert np.array_equal(hex_bits(candidate/'images/stimulus.hex'),np.frombuffer(frame,dtype='<u4'))
initial_bits=hex_bits(candidate/'images/initial.hex')
with np.load(host_path(gui['pins']['parameters']['path']),allow_pickle=False) as p:
    assert np.array_equal(initial_bits,p['bias'].astype('<f4').view('<u4'))
camera_initial=np.load(host_path(gui['pins']['initial']['path']),allow_pickle=False)
mapping=SpatialRegistry();spatial=mapping.extract(full)
assert spatial.shape==(5768,) and np.array_equal(spatial,full[mapping.ids])

spec=importlib.util.spec_from_file_location('line2_line11_original_frame_stepper',candidate/'frame_stepper.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
class SavedReferenceDriver:
    """Only replays the frozen CPU first-state bytes to test callback shape."""
    def init__(self):self.operations=[]
    def load_frame_bits(self,data):assert data==frame;self.operations.append('input')
    def run_steps(self,n,timeout=None):
        assert n==1;self.operations.append('software_fixture_step')
        return dict(completed_steps=1,last_cycles=audit['cycle_projection']['cycles'])
    def read_state_bits(self):self.operations.append('read_saved_reference');return expected
shown=[];driver=SavedReferenceDriver();stepper=module.FrameStepper(driver,shown.append)
packet=stepper.advance(frame)
assert packet.frame_id==0 and packet.completed_steps==1 and packet.state_bits==expected
assert len(shown)==1 and driver.operations==['input','software_fixture_step','read_saved_reference']
before=list(driver.operations)
try:stepper.advance(b'bad')
except ValueError:pass
else:raise AssertionError('short frame accepted')
assert driver.operations==before
bad=SavedReferenceDriver();bad.read_state_bits=lambda:b'short';rejected=[]
broken=module.FrameStepper(bad,rejected.append)
try:broken.advance(frame)
except RuntimeError:pass
else:raise AssertionError('short state accepted')
assert broken.failed and not rejected

requirements=dict(
    schema='flyvis-line11-to-line2-readiness/v1',status='STATIC_CPU_READY_AWAITING_LINE11_REAL_FIRST_STEP',
    requested_operations='PREPARATION_ONLY_NO_EXECUTION_AUTHORITY',
    backend='FULL_NETWORK_FPGA',neural_partition=dict(PL_nodes=45669,PL_edges=1513231,GPU_neural_nodes=0,GPU_role='OFFICIAL_DECODER_AND_OPTIONAL_REFERENCE_ONLY'),
    numeric_profile='LINE11_STRICT_FP32_RNE_NO_FMA_NO_FTZ',model_dt_s=.005,
    model=dict(source_commit=provenance['commit'],checkpoint_sha256=provenance['checkpoint_sha256'],graph_sha256=provenance['graph_sha256']),
    selected_local_candidate=str(candidate),candidate_evidence='ROUTED_LOCAL_ONLY_NOT_BOARD_PASS',
    bit=dict(path=str(candidate/'soc_r2/release/flyvis_full.bit'),**audit['artifacts']['flyvis_full.bit']),
    hwh=dict(path=str(candidate/'soc_r2/release/flyvis_full.hwh'),**audit['artifacts']['flyvis_full.hwh']),
    interface=dict(base_address='0x43C30000',span=4096,ABI='0x00110002',configured_clock_hz=100000000,
        producer_class='FrameStepper',producer_packet_fields=['frame_id','input_bits','state_bits','completed_steps','compute_cycles','elapsed_seconds'],
        input_bytes=2884,state_bytes=182676,byte_order='little_endian_FP32',state_order='global_node_id_0_through_45668',
        A3R1_H5768_wire_compatible=False,A3R1_COMMIT_ACK_not_applicable_to_full_PL=True,
        completion='FINITE_STEP_COMPLETE_FAULT_ZERO_THEN_IDLE_FULL_STATE_READBACK; no fabricated A3R1 ACK'),
    initial=dict(kind='LINE11_RESTORE_FULL_TYPE_BIAS_FP32',bits_sha256=hashlib.sha256(initial_bits.tobytes()).hexdigest(),
        same_as_current_camera_GPU_a0=bool(np.array_equal(initial_bits,camera_initial.astype('<f4').view('<u4'))),
        cross_profile_Q24_camera_result_is_not_first_step_oracle=True),
    first_step_reference=dict(input_path=str(baseline/'input_frame0.bin'),input_sha256=sha(baseline/'input_frame0.bin'),
        expected_path=str(baseline/'expected_state1.bin'),expected_sha256=sha(baseline/'expected_state1.bin'),
        evidence='FROZEN_CPU_EXPECTED_BYTES_ONLY_NOT_NEW_BOARD_STATE',comparison='all_45669_uint32_words_exact',
        input_label='LINE11_FIXED_FRAME0_DO_NOT_RELABEL_ON60'),
    consumer=dict(existing_spatial_mapping=str(GUI/'spatial_registry.json'),spatial_mapping_sha256=mapping.digest,
        T4T5_types=8,nodes_per_type=721,T4T5_total=5768,means='signed_mean_of_each_721_global_ID_set',
        decoder='EXISTING_OFFICIAL_DecoderGAVP_FROM_COMPLETE_45669_STATE_AFTER_BOARD_ACCEPTANCE',
        display='EXISTING_GUI_FIXED_CAMERA_BRIGHTNESS_AND_OFFICIAL_FLOW; not connected by this preparation'),
    required_run_identity=['new_run_id','physical_board_id','boot_id','bit_sha256','hwh_sha256','model_and_node_map_identity','initial_identity'],
    required_each_result=['frame_id','completed_steps','input_sha256','full_state_sha256','faults','actual_compute_cycles',
        'actual_clock_configuration','input_upload_ms','compute_wait_ms','full_state_readback_ms','elapsed_seconds'],
    source_frame_time=dict(model_input_s='frame_id*0.005',model_activity_s='(frame_id+1)*0.005',physical_and_playback_time='SEPARATE_CLOCK_DOMAINS'),
    next_line11_delivery=['Confirm selected candidate or provide replacement BIT/HWH and matching driver identities',
        'Use Line11 own current-boot preparation; do not run Line2 old A3R1 preparation cell',
        'Return one actually computed complete first-step state, exact frozen-input identity, all-state comparison and separated timings',
        'Provide bounded one-input/one-step/result callable or saved package; Line2 reuses original GUI/decoder after first-step PASS'],
    simultaneous_A3R1_session_allowed=False,physical_board_status='NOT_CONNECTED',new_GPU_operations=0,
    new_board_operations=0,new_camera_operations=0,new_GUI_operations=0,
    CPU_checks=['55_sealed_candidate_files','50_identical_memory_images','3_frozen_baseline_files',
        'model_checkpoint_and_HWH_profile','FP32_initial_equals_GUI_model_bias','saved_frame_full_state_to_5768_mapping',
        'original_FrameStepper_one_saved_reference_callback','short_input_no_operation','short_state_no_display_fail_stop'],
    no_new_neural_activity_generated=True,remaining='CURRENT_BOARD_BOOT_AND_EXCLUSIVE_OWNERSHIP_UNKNOWN; new first-step hardware result and actual GUI backend integration pending')
write(OUT/'READINESS.json',requirements)
write(OUT/'CPU_CALLBACK_REFERENCE.json',dict(evidence='CPU_FROZEN_REFERENCE_ONLY',frame_id=packet.frame_id,
    full_state_sha256=hashlib.sha256(expected).hexdigest(),spatial_sha256=hashlib.sha256(spatial.tobytes()).hexdigest(),
    signed_means=spatial.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),physical_board_operations=0))
files={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}
write(OUT/'DELIVERY_MANIFEST.json',dict(files=files))
print(json.dumps(dict(status=requirements['status'],candidate_BIT_verified=True,candidate_HWH_verified=True,
    initial_same_as_camera_a0=requirements['initial']['same_as_current_camera_GPU_a0'],
    callback='PASS_CPU_SAVED_REFERENCE_ONLY',GPU=0,board=0,camera=0,GUI=0)))
