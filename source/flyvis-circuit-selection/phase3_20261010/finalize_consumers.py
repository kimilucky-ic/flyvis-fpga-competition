"""Seal actual animation vectors and read-only GUI outputs after acceptance."""
import csv,shutil
from common import *


def copy_new(source,target):
    if target.exists():assert file_hash(source)==file_hash(target),'preserve existing consumer evidence'
    else:shutil.copyfile(source,target)


def mem(path,array):
    values=np.ascontiguousarray(array,dtype=np.float32).reshape(-1)
    path.write_text(''.join(f'{int(word):08x}\n' for word in values.view(np.uint32)),encoding='ascii')
    back=np.loadtxt(path,dtype=np.uint32,converters=lambda word:int(word,16),ndmin=1).view(np.float32)
    assert np.array_equal(back.view(np.uint32),values.view(np.uint32)),'hex must reproduce every float32 bit'


def main():
    meta,model,h,inputs,stimulus,initial,t,after,_=read_input()
    source=HERE/'artifacts/python_source_raw_800_r2';audit=load(HERE/'artifacts/audit_800_r1/result.json')
    assert audit['status']=='PASS_INDEPENDENT_800_STATE_CHAIN_AND_VECTOR_AUDIT'
    causal=load(HERE/'artifacts/live_feedback_r1/result.json');assert causal['status']=='PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS'
    ri=load(source/'run_identity.json');ref=host_path(load(HERE/'A_FULL_800_RECEIPT.json')['A_reference_path'])
    full_id=load(ref/'run_identity.json');vectors=np.load(source/'SOURCE_RAW_step_io.npz')
    c=HERE/'c_reference'
    copy_new(source/'SOURCE_RAW_step_io.npz',c/'SOURCE_RAW_step_io.npz')
    copy_new(source/'step_status.jsonl',c/'state_chain.jsonl')
    for name in ['numeric_profile.json','metric_profile.json','time.npy','activity_time.npy','initial_state_full.npy']:
        copy_new(BUNDLE/name,c/name)
    for name in ['old_H','x_H','boundary_before','new_H_expected']:
        mem(c/(name+'_ieee754.mem'),vectors[name])
    edge_rows=list(csv.DictReader((c/'edges_HH_RH_original_order.csv').open(encoding='utf-8')))
    mem(c/'weights_hh_rh_ieee754.mem',np.array([np.float32(row['weight_float32']) for row in edge_rows]))
    desc=load(c/'C_REFERENCE_HANDOFF.json');desc.update(status='PASS_ACTUAL_ANIMATION_800_FLOAT32_REFERENCE',
        expected_vectors_path=str(c/'SOURCE_RAW_step_io.npz'),vectors_sha256=file_hash(c/'SOURCE_RAW_step_io.npz'),
        actual_source_run_id=ri['run_id'],Full_reference_run_id=full_id['run_id'],
        state_chain_sha256=file_hash(c/'state_chain.jsonl'),all800_recomputed_bitwise=True,
        execution_evidence_level='ACTUAL_GPU_R_AND_INDEPENDENT_PYTHON_H_CLOSED_LOOP',
        mem_encoding='IEEE754 FP32 bit-pattern hex, one32bit word per line, flat address=step*local_count+local_id; encoding only, not hardware numeric decision',
        mem_roundtrip_all_words_bitwise=True,FPGA_execution=False)
    dump(c/'C_REFERENCE_HANDOFF.json',desc);seal(c)
    gui=HERE/'gui_bundle'
    if gui.exists():raise SystemExit('Existing GUI evidence preserved; choose new namespace')
    gui.mkdir();states=dict(FullGPU=np.load(ref/'activities_full.npy',mmap_mode='r'),PythonReplacement=np.load(source/'activities_full.npy',mmap_mode='r'))
    central=np.load(BUNDLE/'central_node_indices.npy');types=np.load(BUNDLE/'cell_types.npy')
    tt=central[np.isin(types,['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'])]
    np.save(gui/'central_global_ids.npy',central);np.save(gui/'T4T5_global_ids.npy',tt);np.save(gui/'H_global_ids.npy',h.h_ids)
    np.save(gui/'central_cell_types.npy',types)
    for name in ['stimulus.npy','time.npy','activity_time.npy']:copy_new(BUNDLE/name,gui/name)
    input_receipt=HERE.parents[1].parent/'fly/camera_pipeline/phase3_input_20261010_r1'
    for name in ['source_model_activity_alignment.csv','INPUT_SINGLE_VIDEO_IDENTITY.json']:
        if (input_receipt/name).exists():copy_new(input_receipt/name,gui/name)
    modes={}
    for name,array in states.items():
        folder=gui/name;folder.mkdir()
        for key,ids in [('central',central),('T4T5',tt),('H',h.h_ids)]:np.save(folder/('activity_'+key+'.npy'),np.ascontiguousarray(array[0,:,ids].T))
        from_run=ref if name=='FullGPU' else source
        copy_new(from_run/'run_identity.json',folder/'run_identity.json');copy_new(from_run/'result.json',folder/'result.json')
        modes[name]=dict(available=True,run_id=full_id['run_id'] if name=='FullGPU' else ri['run_id'],
            execution_kind='actual_new_computation',display_mode='offline_replay_of_actual_computation',
            source_all_nodes_path=str(from_run/'activities_full.npy'),source_all_nodes_sha256=file_hash(from_run/'activities_full.npy'))
    for name in ['step_errors.csv','per_node_max_abs.npy']:copy_new(source/name,gui/name)
    modes['FPGAReplacement']=dict(available=False,status='NOT_RUN',reason='C reviewed actual PL backend/board800 evidence not delivered',fallback=False)
    dump(gui/'GUI_READONLY_HANDOFF.json',dict(schema='B_GUI_ANIMATION_RESULTS/v1',status='PASS_SOFTWARE_RESULTS_READY_FOR_GUI_READ_ONLY_INTEGRATION',
        condition_id='01_off_right',comparison_id=meta['comparison_id'],steps=800,dt_s=.005,
        array_shapes=dict(stimulus=[1,800,1,721],central=[800,65],H=[800,67],T4T5=[800,8]),
        input_time='k*.005',activity_time='(k+1)*.005',video_path=meta['source_mp4'],video_sha256=meta['source_mp4_sha256'],
        provenance='FullGPU and PythonReplacement computed anew; this package is offline display only, no live execution claim',
        mode_status=modes,GUI_browser_verified=False,FPGA_execution=False))
    seal(gui);print('C_VECTOR_AND_GUI_EXPORT_PASS',desc['vectors_sha256'])

if __name__=='__main__':main()
