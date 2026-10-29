"""One bounded CPU preparation: frozen ON60, original bias, original reference.
Never a new GPU/PL result. Refuses to overwrite the prepared plan.
"""
import hashlib,json,os,sys,time
from pathlib import Path

OUT=Path(__file__).resolve().parent
GUI=OUT.parents[1];FLY=GUI.parent;STUDY=FLY.parent/'fpga/flyvis-lossless-study'
sys.path.insert(0,str(GUI))
from line11_ddr_flow import CPUDecoder,digest

def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main():
    plan=OUT/'plan';plan.mkdir(exist_ok=False)
    started=time.perf_counter()
    decoder=CPUDecoder(OUT/'cpu_reference_cache')
    import numpy as np
    import torch
    os.environ['NUMBA_NUM_THREADS']='1'
    sys.path.insert(0,str(STUDY))
    from reference import verify_sources,build_reference
    from codec import read_template
    from engine import Engine
    pins=verify_sources(FLY)
    source=FLY.parent/'fpga/flyvis-circuit-selection/t4t5_criticality_20261011/cpu_preparation_r1/ON60_stimulus.npy'
    assert digest(source.read_bytes())=='67e490d4790a7bec5ad90dabd6ced7747c797a720a9e197d2750903b48350fa7'
    raw=np.load(source,allow_pickle=False);x=raw.reshape(485,721).astype('<f4')
    assert digest(x.tobytes())=='4a93b817b8aef54e4c1a1ead8c6f913b4270912059db8f9d296922e930638ab8'
    template_path=STUDY/'runs/acceptance800_20261013/flyvis_template.bin'
    assert digest(template_path.read_bytes())=='1d52e7dea2d244f69398cff81e14c120626f3f9a61694b84ad0259839acfd574'
    template=read_template(template_path);engine=Engine(template)
    initial=engine.activity.tobytes()
    assert digest(initial)=='d276601573420bf787a81ffa8c81f2da3499a20df2bb858f6082c2e449ff564f'
    print('CPU original reference construction; CUDA initialized:',torch.cuda.is_initialized(),flush=True)
    net,params,spec,arrays=build_reference(FLY)
    assert np.array_equal(arrays['bias'].view('u4'),engine.activity.view('u4'))
    state=net._initial_state(params,1);reference=np.empty((485,45669),dtype='<f4')
    rows=[];warm=Engine(template);warm.advance(x[0]);del warm
    begin=time.perf_counter()
    with torch.inference_mode():
        for k,frame in enumerate(x):
            net.stimulus.zero(1,1);net.stimulus.add_input(torch.from_numpy(frame.copy()).reshape(1,1,1,721))
            state=net._next_state(params,state,net.stimulus()[:,0],.005)
            original=state.nodes.activity[0].numpy();got=engine.advance(frame)
            mismatches=int(np.count_nonzero(original.view('u4')!=got.view('u4')))
            assert mismatches==0 and np.isfinite(got).all(),(k,mismatches)
            reference[k]=got;rows.append(dict(step=k,bit_mismatches=mismatches,state_sha256=digest(got.tobytes())))
            if k in (0,31,199,399,484):print('CPU complete-state comparison',k+1,'/485 PASS',flush=True)
    recurrence_s=time.perf_counter()-begin
    flow=np.empty((485,2,721),dtype='<f4');begin=time.perf_counter()
    for k in range(0,485,32):flow[k:k+32]=decoder.decode(reference[k:k+32])
    decoder_s=time.perf_counter()-begin
    single=decoder.decode(reference[[0,200,484]])
    assert np.allclose(single,flow[[0,200,484]],atol=1e-5,rtol=1e-5)
    assert not torch.cuda.is_initialized()
    x.tofile(plan/'plan_inputs.bin');reference.tofile(plan/'plan_expected_states.bin')
    np.save(OUT/'CPU_REFERENCE_FLOW.npy',flow,allow_pickle=False)
    save(OUT/'PER_STEP_CPU_COMPARISON.json',rows)
    manifest=dict(schema='flyvis-line2-ddr-fixed-plan/v1',plan_id='ON60_485_ORIGINAL_BIAS_FP32',
        steps=485,dt_s=.005,nodes=45669,edges=1513231,condition_id='ON60',polarity='ON',angle_deg=60,
        input_time_offset_s=-1.,onset_step=200,model_duration_s=2.425,
        input_source=dict(path=str(source),sha256=digest(source.read_bytes()),source_dtype=str(raw.dtype),
            conversion='Explicit FP32 cast matching original stimulus assignment'),
        initial_state=dict(kind='ORIGINAL_PER_TYPE_BIAS',sha256=digest(initial),
            limitation='NOT the gray-adapted a0 from historical ON60 science; first200 steps adapt'),
        reference=dict(evidence='CPU_ONLY_ORIGINAL_NETWORK_AND_TEMPLATE_BIT_EXACT',
            template=str(template_path),template_sha256=digest(template_path.read_bytes()),
            compared_values=485*45669,bit_mismatches=0,atol=0,rtol=0,
            checkpoint_sha256='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'),
        files={n:dict(bytes=(plan/n).stat().st_size,sha256=digest((plan/n).read_bytes()))
               for n in ('plan_inputs.bin','plan_expected_states.bin')},
        decoder=decoder.identity,board_result=False,GPU_execution=False)
    save(plan/'RUN_PLAN.json',manifest)
    save(OUT/'CPU_REFERENCE_RESULT.json',dict(status='PASS_CPU_REFERENCE_AND_OFFICIAL_DECODER',
        evidence_level='CPU_ONLY_NO_BOARD_NO_GPU',steps=485,compared_state_words=485*45669,mismatch_words=0,
        input_words=485*721,initial_state_sha256=digest(initial),plan_sha256=digest((plan/'RUN_PLAN.json').read_bytes()),
        flow_sha256=digest((OUT/'CPU_REFERENCE_FLOW.npy').read_bytes()),flow_shape=list(flow.shape),
        decoder_state_unchanged=True,recursive_eval=True,cuda_initialized=torch.cuda.is_initialized(),
        batch_vs_selected_frame_max_abs=float(np.max(np.abs(single-flow[[0,200,484]]))),
        timing=dict(reference_and_template_s=recurrence_s,official_decoder_s=decoder_s,total_s=time.perf_counter()-started),
        original_sources=pins,reference_implementation_sha256={n:digest((STUDY/n).read_bytes()) for n in ('reference.py','engine.py','codec.py')},
        board_result=False,notes='Prepared references only. Actual flow must use current received board states, never this saved flow.'))
    print('CPU485 preparation complete; plan SHA',digest((plan/'RUN_PLAN.json').read_bytes()),flush=True)

if __name__=='__main__':main()
