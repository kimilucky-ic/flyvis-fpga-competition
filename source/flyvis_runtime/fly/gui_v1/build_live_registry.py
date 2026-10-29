"""Freeze the small existing input/core interface pins. Never compute neurons."""
import csv
import json
from pathlib import Path
from data_store import ROOT,read_json,sha256


def main():
    fpga=ROOT.parent/'fpga';pilot=fpga/'flyvis-circuit-selection/t4t5_criticality_20261011'
    bundle=fpga/'flyvis-circuit-selection/phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'
    decoder=fpga/'flyvis-gpu-validation/t4t5_decoder_support_20261011'
    python=fpga/'flyvis-circuit-selection/phase4_camera_replacement_20261011_r1/dependencies/b_core'
    camera=ROOT/'camera_pipeline/phone_screen_rectification_20261011_r1/real_capture_review_camera_2dfba194_20261011_r1'
    identity=read_json(pilot/'INPUT_IDENTITY.json');contract=read_json(decoder/'FULL_DECODER_CONTRACT.json')
    paths={'full':ROOT/'gpu_phase2/full_oracle.py','r_only':ROOT/'gpu_phase2/r_only.py',
        'decoder':decoder/'service.py','readout':decoder/'flow_readout.py','decoder_contract':decoder/'FULL_DECODER_CONTRACT.json',
        'readout_contract':decoder/'READOUT_CONTRACT.json','intervention':pilot/'intervention_adapter.py',
        'operators':pilot/'operators.py','metrics':pilot/'metrics.py',
        'sparse':fpga/'flyvis-circuit-selection/t4t5_confirm_20261011/sparse_operator.py',
        'runner_lease':fpga/'flyvis-autorunner/plugin_contract.py','runner_common':fpga/'flyvis-autorunner/autorunner.py',
        'runner_host':fpga/'flyvis-autorunner/plugin_host.py',
        'identity':bundle/'identity_manifest.json','initial':bundle/'initial_state_full.npy','parameters':bundle/'expanded_parameters.npz',
        'nodes':bundle/'nodes_full.csv','input_map':bundle/'input_node_indices.npy','time':bundle/'time.npy',
        'graph':pilot/'cpu_preparation_r1/graph_identity.npz','roi':pilot/'cpu_preparation_r1/flow_ROI_hex_indices.npy',
        'coordinates':Path(contract['coordinates']['path']),
        'h_step':python/'h_step.py','coordinator':python/'coordinator.py','gpu_adapter':python/'gpu_adapter.py',
        'closed_loop':python/'run_closed_loop.py',
        'h_static':fpga/'flyvis-gpu-validation/phase4_camera_rectb_20261011/common_bundle/static_boundary_gpu_native.npz',
        'candidate':bundle/'candidates/B_T5c/candidate_manifest.json',
        'camera_reader':camera/'input_reader.py','camera_identity':camera/'frozen_selected_100_190/input/INPUT_IDENTITY.json',
        'camera_manifest':camera/'frozen_selected_100_190/input/manifest.json',
        'controlled_reader':ROOT/'camera_pipeline/controlled_video_20261010_r1/gui_handoff.py',
        'science_contract':fpga/'flyvis-circuit-selection/online_science_contract_20261012/CONTRACT.json'}
    inputs={}
    for condition in identity['conditions']:
        if condition['condition_id'] not in ('ON60','OFF90'):continue
        name=condition['condition_id'];paths['stimulus_'+name]=pilot/'cpu_preparation_r1'/condition['filename']
        inputs[name]={**condition,'source_kind':'official_frozen_digital_stimulus','steps':485,'dt_s':.005}
        assert sha256(paths['stimulus_'+name])==condition['stimulus_sha256']
    with paths['nodes'].open(encoding='utf-8',newline='') as stream:
        centers={r['cell_type']:int(r['global_node_index']) for r in csv.DictReader(stream) if r['u']==r['v']=='0'}
    types=[f'T{n}{letter}' for n in (4,5) for letter in 'abcd']
    receipt_summary={}
    for stage in ('A','B'):
        root=fpga/f'flyvis-autorunner/runs/autorun_research{stage}_20261011_r1'
        seal=read_json(root/'plugin_seal.json')
        # Only scheduler essentials, not its multi-GB raw trajectories.
        for path,digest in seal['essential_sha256'].items():assert sha256(path)==digest
        paths['runner_'+stage+'_receipt']=root/'run_summary.json';paths['runner_'+stage+'_seal']=root/'plugin_seal.json'
        receipt_summary[stage]={'status':read_json(root/'run_summary.json')['status'],'host_exit':read_json(root/'host_exit.json')}
    registry={'schema':'flyvis-live-registry/v1','model':identity['model'],'inputs':inputs,'steps':485,'dt_s':.005,
        'onset_step':200,'chunk_frames':32,'types':types,'central_global_ids':[centers[t] for t in types],
        'modes':['Full','Sham','BLOCK_T4_RELEASE','BLOCK_T5_RELEASE','BLOCK_T4T5_RELEASE','CLAMP_T4T5','Python_Replacement'],
        'pins':{key:{'path':str(path.resolve()),'sha256':sha256(path)} for key,path in paths.items()},
        'runtime':{'python':'/opt/flyvis-gpu-venv/bin/python','model_path':'/opt/flyvis-visual-experiments-data/results/flow/0000/000'},
        'camera':{'folder':str(camera/'frozen_selected_100_190/input'),'status':'READ_API_AVAILABLE_SCIENTIFIC_PROFILE_NOT_BOUND','steps':609,'source_kind':'recorded_camera_frozen'},
        'runner_receipts':receipt_summary,'PL_execution':False,'GPU_execution_today':'NOT_RUN'}
    out=ROOT/'gui_v1/live_registry.json'
    if out.exists():raise ValueError('Registry already frozen; review a new revision instead of overwriting')
    out.write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'FROZEN_STATIC_INTERFACES','pins':len(paths),'conditions':list(inputs),'torch_imported':False,'GPU_calls':0}))


if __name__=='__main__':main()
