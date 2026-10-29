"""Stage only this lane's immutable camera input and accepted software cores."""
from pathlib import Path
import csv, importlib.util, json, shutil, hashlib
import numpy as np

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'phase3_20261010'
E=Path(r'C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\phone_screen_rectification_20261011_r1\real_capture_review_camera_2dfba194_20261011_r1')
CID='camera_rectB_c5689ab635cc425ea672029502d0d402'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    if (HERE/'input_bundle').exists():raise SystemExit('Existing staged input preserved')
    spec=importlib.util.spec_from_file_location('frozen_camera_reader',E/'input_reader.py')
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    source=E/'frozen_selected_100_190/input'
    meta,x,t,a=reader.load_frozen_input(source)
    assert meta['comparison_id']==CID and x.shape==(1,609,1,721)
    assert sha(source/'stimulus.npy')=='273f4bf4df0ba7591a293b36f62b1f9f3c98e0031ce8b2cc70ba13b1d49e78b9'
    assert sha(source/'manifest.json')=='35d1f43b6461439ea52222914a24eeb30997adadb01979ec07eb2518bb455800'
    bundle=HERE/'input_bundle';bundle.mkdir()
    for name in ['stimulus.npy','time.npy','activity_time.npy','input_hex_coordinates.csv','INPUT_IDENTITY.json','three_clock_alignment.csv']:
        shutil.copyfile(source/name,bundle/name);assert sha(source/name)==sha(bundle/name)
    for name in ['expanded_parameters.npz','input_node_indices.npy','nodes_full.csv','central_node_indices.npy','cell_types.npy']:
        src=PREVIOUS/'input_bundle'/name;shutil.copyfile(src,bundle/name);assert sha(src)==sha(bundle/name)
    shutil.copytree(PREVIOUS/'input_bundle/candidates/B_T5c',bundle/'candidates/B_T5c')
    shutil.copyfile(PREVIOUS/'input_bundle/static_boundary_gpu_native.npz',bundle/'static_boundary_gpu_native.npz')
    shutil.copyfile(E/'input_reader.py',HERE/'input_reader.py')
    shutil.copyfile(E/'handoff_selected_100_190/experiment.json',HERE/'CAMERA_EXPERIMENT_SOURCE.json')
    reuse=[]
    for folder,names in [('b_core',['h_step.py','coordinator.py','gpu_adapter.py','run_closed_loop.py','run_negative_tests.py']),('a_snapshot',['r_only.py'])]:
        dst=HERE/'dependencies'/folder;dst.mkdir(parents=True)
        for name in names:
            src=PREVIOUS/'dependencies'/folder/name;shutil.copyfile(src,dst/name)
            assert sha(src)==sha(dst/name)
            reuse.append(dict(path=str((dst/name).relative_to(HERE)),source=str(src),sha256=sha(src)))
    with (bundle/'input_hex_coordinates.csv').open(encoding='utf-8') as f:coords=list(csv.DictReader(f))
    with (bundle/'nodes_full.csv').open(encoding='utf-8') as f:nodes=list(csv.DictReader(f))
    with np.load(bundle/'expanded_parameters.npz') as z:indices=z['input_node_index'].copy()
    assert indices.shape==(8,721) and np.array_equal(indices,np.load(bundle/'input_node_indices.npy'))
    for row in range(8):
        for pixel,global_id in enumerate(indices[row]):
            assert int(coords[pixel]['hex_pixel'])==pixel
            assert (nodes[global_id]['u'],nodes[global_id]['v'])==(coords[pixel]['u'],coords[pixel]['v'])
    report=dict(status='PASS_CAMERA_INPUT_CORE_STAGE_PENDING_A_MODEL_AND_FULL',comparison_id=CID,
        input_shape=list(x.shape),input_read_only=True,steps=609,dt_s=.005,
        input_time_range_s=[float(t[0]),float(t[-1])],after_time_range_s=[float(a[0]),float(a[-1])],
        stimulus_sha256=sha(source/'stimulus.npy'),input_manifest_sha256=sha(source/'manifest.json'),
        input_time_sha256=sha(source/'time.npy'),activity_time_sha256=sha(source/'activity_time.npy'),
        original_source=str(source),eight_receptor_rows_coordinate_order_verified=True,
        coordinate_mappings_checked=8*721,core_files_byte_identical=reuse,
        original_camera_package_modified=False,neural_updates=0,FPGA_execution=False,
        a0_status='NOT_BOUND_WAITING_FOR_A_CURRENT_EXPERIMENT',Full_status='WAITING_FOR_A_CURRENT_EXPERIMENT',
        pending='A common complete a0/model/Full and short GPU coordination')
    (HERE/'STAGE_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],shape=list(x.shape),reused_cores=len(reuse),coordinate_mappings=8*721,neural_updates=0)))

if __name__=='__main__':main()
