"""Saved-data audit/report only. No neural rollout, CUDA or decoder calls."""
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ.update(MPLBACKEND='Agg',MPLCONFIGDIR=str(HERE/'runtime/matplotlib'),OMP_NUM_THREADS='1')
import csv
import hashlib
import json
import math
import numpy as np


def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def array_sha(array):return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()
def dump(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
def table(path,rows):
    with Path(path).open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    prereg=load(HERE/'PREREGISTRATION.json');screen=load(HERE/'SCREEN_RESULTS.json');validation=load(HERE/'VALIDATION_RESULTS.json')
    for path,digest in prereg['source_pins'].items():assert sha(path)==digest,path
    by_name={r['name']:r for r in validation['selected']}
    metrics=screen['metrics']+validation['metrics']
    output=[]
    for row in metrics:
        output.append({key:row[key] for key in ['name','condition','stage','E','M','Q','correlation','reference_RMS','baseline_offset_RMS','raw_trajectory_RMS_error','tail_abs_slope_max','trace_pass']})
    table(HERE/'LOCAL_NEURAL_METRICS.csv',output)
    directions=[];polarity=[]
    for result in validation['selected']:
        directions.extend([dict(name=result['name'],**r) for r in result['opposite_direction']])
        polarity.extend([dict(name=result['name'],**r) for r in result['polarity']])
    table(HERE/'PAIRED_DIRECTION.csv',directions);table(HERE/'ON_OFF_SAME_ANGLE.csv',polarity)
    resources=[];models={}
    for name in prereg['candidates']:
        manifest=load(HERE/f'models/{name}/manifest.json');models[name]=manifest
        r=manifest['resources'];verdict=by_name.get(name)
        resources.append(dict(name=name,n_neurons=manifest['n_nodes'],n_synapses=manifest['n_edges'],
            n_retina_pixels=manifest['n_input_pixels'],deleted_incoming=manifest['boundary_incoming_deleted'],
            nodes_reduction_percent=100*(1-manifest['n_nodes']/45669),edges_reduction_percent=100*(1-manifest['n_edges']/1513231),
            fp32_edge_table_bytes=r['float32_edge_records_bytes'],working_state_parameter_buffer_bytes=r['working_bytes'],
            estimated_total_bytes=r['estimated_all_onchip_bytes'],estimated_BRAM36_nominal_blocks=r['estimated_BRAM36_raw_blocks'],
            estimated_32bit_payload_blocks=math.ceil(r['estimated_all_onchip_bytes']/4096),
            edge_only_bandwidth_MBps_at_200_model_steps_s=r['edge_stream_MBps_at_200_model_steps_s'],
            optimistic_one_edge_per_cycle_100MHz_step_ms=r['optimistic_100MHz_one_edge_per_cycle_ms'],
            screen_pass=next(s['screen_pass'] for s in screen['scores'] if s['name']==name),
            heldout_status='NOT_SELECTED' if verdict is None else 'PASS_LOCAL_FUNCTION' if verdict['functional_acceptance'] else 'FAIL_FIXED_FUNCTION_GATE',
            evidence='CPU_SIMULATION_AND_ANALYTICAL_ESTIMATE_ONLY'))
    table(HERE/'RESOURCE_ESTIMATES.csv',resources)
    accepted=[];run_records=[];audits=[]
    for result_path in sorted((HERE/'artifacts').glob('*/*/*/result.json')):
        record=load(result_path)
        if record.get('status')!='PASS_INDEPENDENT_CPU_MULTI_STEP':continue
        folder=result_path.parent;name=record['name'];model_file=HERE/f'models/{name}/model.npz'
        p=np.load(model_file,allow_pickle=False);n=len(p['bias'])
        nodes=p['global_node_index'];eid=p['original_edge_index']
        source=np.load(HERE.parent/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle/expanded_parameters.npz',allow_pickle=False)
        assert np.array_equal(p['bias'],source['bias'][nodes])
        assert np.array_equal(p['time_const'],source['time_const'][nodes])
        assert np.array_equal(p['weight'],source['effective_weight'][eid])
        assert np.array_equal(nodes[p['source']],source['source_global'][eid])
        assert np.array_equal(nodes[p['target']],source['target_global'][eid])
        states=np.load(folder/'states.npy',mmap_mode='r');warm=np.load(folder/'warmup_states.npy',mmap_mode='r')
        frames=np.load(folder/'local_input.npy');initial=np.load(folder/'initial_state.npy')
        journal=[json.loads(line) for line in (folder/'steps.jsonl').read_text().splitlines()]
        assert len(journal)==685 and np.array_equal(initial,warm[-1])
        for phase,array,inputs,offset,previous in [('gray_warmup',warm,np.full((200,len(p['input_hex_global_index'])),.5,np.float32),0,p['bias']),('movie',states,frames,200,initial)]:
            for k,row in enumerate(array):
                event=journal[offset+k]
                assert event['phase']==phase and event['step_id']==k and event['status']=='COMMITTED'
                assert event['old_state_digest']==array_sha(previous)
                assert event['new_state_digest']==array_sha(row) and event['input_digest']==array_sha(inputs[k])
                assert event['n_updated']==n and event['external_neural_inputs']==0
                previous=row
        assert record['states_sha256']==sha(folder/'states.npy')
        assert np.isfinite(states).all() and np.isfinite(warm).all()
        assert np.array_equal(np.load(folder/'final_state.npy'),states[-1])
        audits.append(dict(case=f"{record['stage']}/{name}/{record['condition']}",ordered_own_state_chain=True,
            original_retained_parameter_and_edge_identity=True,no_external_neural_inputs=True,all_finite=True))
        run_records.append(record)
    portable=HERE/'standalone_package/a_r4/portable_check';portable_record=load(portable/'result.json')
    full_case=HERE/'artifacts/holdout/a_r4/ON240'
    assert sha(portable/'states.npy')==sha(full_case/'states.npy')
    assert sha(portable/'initial_state.npy')==sha(full_case/'initial_state.npy')
    dump(HERE/'PORTABILITY_CHECK.json',dict(status='PASS_ISOLATED_CANDIDATE_ONLY_MULTI_STEP',
        model='a_r4',actual_run=portable_record,isolated_python=True,
        package_dependencies=['Python','NumPy','independent_model.py','standalone_run.py','model.npz','local_input.npy'],
        requires_original_FlyVis_installation=False,requires_full_model_or_saved_network_states=False,
        trajectories_bitwise_match_accepted_own_state_case=True,
        rejected_first_launcher_record='PORTABLE_LAUNCH_FAILURE.json',neural_steps_in_rejected_launch=0))
    dump(HERE/'INDEPENDENCE_AUDIT.json',dict(status='PASS_SAVED_MODEL_AND_OWN_STATE_CHAINS',
        audited_cases=len(audits),audited_commits=685*len(audits),checks=audits,
        original_step_code_sha256=sha(HERE/'independent_model.py'),source_pins_unchanged=True,
        parameter_tuning=False,heldout_selection_unchanged=True,scope='saved-data audit, no neural recomputation'))
    time_file=HERE.parent/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle/time.npy'
    time_axis=np.load(time_file);np.save(HERE/'input_time.npy',time_axis);np.save(HERE/'activity_time.npy',time_axis+.005)
    selected=[]
    for name in load(HERE/'selection.json')['selected']:
        verdict=by_name[name];manifest=models[name]
        selected.append(dict(name=name,nodes=manifest['n_nodes'],edges=manifest['n_edges'],
            retina_pixels=manifest['n_input_pixels'],model_sha256=sha(HERE/f'models/{name}/model.npz'),
            functional_acceptance=verdict['functional_acceptance'],independent_recursion=True,
            direction_subtypes_passed=verdict['opposite_direction_subtypes_preserved'],
            polarity_combinations_passed=verdict['polarity_combinations_preserved'],
            worst_heldout_neural_E=max(verdict['heldout_neural_E'].values()),resources=manifest['resources']))
        if verdict['functional_acceptance']:accepted.append(name)
    extra_results=[load(p) for p in sorted((HERE/'artifacts/extra_reference').glob('*/result.json'))]
    calibration=load(HERE/'CALIBRATION.json')
    counts=dict(candidate_runs=len(run_records),candidate_commits=sum(r['warmup_steps']+r['movie_steps'] for r in run_records),
        portable_runs=1,portable_commits=685,
        calibration_full_movie_steps=485,extra_full_reference_steps=sum(r['actual_steps'] for r in extra_results),
        prior_unregistered_timing_probe_full_steps=1,new_GPU_runs=0,new_decoder_frames=0)
    timings=dict(calibration_CPU_s=calibration['wall_s'],candidate_rollout_record_s=sum(r['wall_s'] for r in run_records),
        extra_full_reference_CPU_s=sum(r['wall_s'] for r in extra_results),portable_CPU_s=portable_record['wall_s'],
        screen_phase_wall_s=screen['wall_s'],holdout_phase_wall_s=validation['wall_s'],
        scope='phase times include recording; summed case times exclude process startup and preparation; no pure GPU timing')
    result=dict(status='PASS_FIRST_CPU_PRUNING_BATCH_WITH_TWO_LOCAL_FUNCTION_CANDIDATES',
        preregistration_id=prereg['identity_id'],accepted_local_function_candidates=accepted,
        smallest_accepted_in_tested_set='a_r4',global_minimum_size_proven=False,
        recommended_for_user_hardware_review='a_r4',selected=selected,counts=counts,timings=timings,
        official_optical_flow_provided=False,official_12_direction_DSI_provided=False,
        biological_visual_function_proven=False,RTL_or_board_evidence=False,
        results_stop_boundary='no further candidate, stimulus, tuning, GPU or hardware runs',
        source_dataset_identity=prereg['model_identity'],data_bytes_current=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()))
    dump(HERE/'RESULT.json',result)
    plots(screen,validation,time_axis)
    report(result,resources,by_name)
    file_list=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(HERE.rglob('*')) if p.is_file() and 'runtime' not in p.parts and '__pycache__' not in p.parts]
    dump(HERE/'DELIVERY_MANIFEST.json',dict(schema='whole-network-pruning-delivery/v1',preregistration_id=prereg['identity_id'],
        scope='new lane results only; manifest does not include itself',files=file_list))
    print(json.dumps(dict(status=result['status'],accepted=accepted,counts=counts,timings=timings,
        manifest_sha256=sha(HERE/'DELIVERY_MANIFEST.json'),file_count=len(file_list)),ensure_ascii=False))


def plots(screen,validation,time_axis):
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    colors={'A_R3':'#d18a25','a_r4':'#1c78a5','A_R6':'#36795b'}
    figure,axes=plt.subplots(1,2,figsize=(11,4.5))
    conditions=['ON60','OFF90','ON240','OFF270','OFF60','ON90'];x=np.arange(len(conditions))
    for row in validation['selected']:
        name=row['name'];values=[]
        for c in conditions:
            values.append(next(m['E'] for m in screen['metrics']+validation['metrics'] if m['name']==name and m['condition']==c))
        axes[0].plot(x,values,'o-',label=f"{name}: {len(np.load(HERE/f'models/{name}/model.npz')['bias'])} neurons",color=colors[name])
    axes[0].axhline(.35,color='#666666',ls='--',label='Frozen neural-error threshold 0.35')
    axes[0].set_xticks(x,conditions,rotation=25);axes[0].set_ylabel('Relative local neural response error (unitless)')
    axes[0].set_xlabel('Fixed input condition');axes[0].set_title('Screen inputs + four unseen validation inputs');axes[0].legend(fontsize=8)
    for row in validation['selected']:
        name=row['name'];d=row['opposite_direction'];axes[1].plot(np.arange(8),[v['candidate_D'] for v in d],'o-',label=name,color=colors[name])
    axes[1].plot(np.arange(8),[v['reference_D'] for v in validation['selected'][0]['opposite_direction']],'k--',label='Original Full reference')
    axes[1].set_xticks(np.arange(8),['T4'+s for s in 'abcd']+['T5'+s for s in 'abcd'],rotation=35)
    axes[1].set_xlabel('Fixed T4/T5 subtype');axes[1].set_ylabel('Local opposite-direction contrast D (unitless)')
    axes[1].set_ylim(-1.08,1.08);axes[1].set_title('ON 60/240; OFF 90/270 (not official DSI)');axes[1].legend(fontsize=8)
    figure.suptitle('Independent cropped FlyVis models | CPU simulation | 2026-10-13',fontsize=13)
    figure.text(.5,.01,'Source: frozen PREREGISTRATION + saved candidate trajectories. ROI radius 1: 56 neurons; k200-285; own pre-baselines.',ha='center',fontsize=8)
    figure.tight_layout(rect=(0,.05,1,.94));figure.savefig(HERE/'function_comparison.png',dpi=170);plt.close(figure)
    figure,axes=plt.subplots(2,1,figsize=(10,6.5),sharex=True)
    ids=np.load(HERE/'models/a_r4/readout_global_ids.npy')
    for ax,condition,global_id,title in [(axes[0],'ON60',25841,'Central T4c / ON60'),(axes[1],'OFF270',27283,'Central T5a / OFF270')]:
        ref=np.load(HERE.parent/f't4t5_criticality_20261011/artifacts/pilot_gpu_r1/{condition}/Full/activities_full.npy',mmap_mode='r')[0,:,global_id]
        ax.plot(time_axis+.005,ref-ref[160:200].mean(),'k--',label='Original Full reference')
        for name in colors:
            model=np.load(HERE/f'models/{name}/model.npz');local=int(np.flatnonzero(model['global_node_index']==global_id)[0])
            stage='screen' if condition=='ON60' else 'holdout'
            own=np.load(HERE/f'artifacts/{stage}/{name}/{condition}/states.npy',mmap_mode='r')[:,local]
            ax.plot(time_axis+.005,own-own[160:200].mean(),color=colors[name],label=name)
        ax.axvspan(.005,.43,color='#ededed');ax.set_title(title);ax.set_ylabel('Signed activity - own baseline (model units)');ax.legend(fontsize=8)
    axes[1].set_xlabel('Euler output activity time (s)')
    figure.text(.5,.01,'Actual saved traces. Shaded region: fixed main window; no external neural states in candidate calculation.',ha='center',fontsize=8)
    figure.tight_layout(rect=(0,.05,1,1));figure.savefig(HERE/'time_dynamics.png',dpi=170);plt.close(figure)


def report(result,resources,by_name):
    old=load(HERE/'OLD_3752_AUDIT.json');a=next(r for r in resources if r['name']=='a_r4');b=next(r for r in resources if r['name']=='A_R6')
    lines=[
      '# 第一轮：FlyVis整网结构裁剪与独立运行可行性 · 2026-10-13',
      '',
      '**结论：可将整网裁剪为完全自行递推的局部视觉模型。本批最小通过冻结局部功能门槛的是3865节点/110794边的a_r4；8051节点/246109边的A_R6更接近原网。未证明全局最小规模、官方光流或全部方向功能恢复。**',
      '',
      '本研究仅④新目录内CPU实验，原模型文件、参数及各主工程未改；GPU/decoder/RTL/BIT/板测为0。全部候选是原图诱导裁剪后的新模型，与原完整FlyVis不严格等价。',
      '',
      '## 3752旧实验的实际含义',
      '',
      '重新读取原keep/inactive列表、node map、EXPERIMENT_B、science_worker/sparse_operator和原flow，并以原metrics代码复算。3752为radius12、469位置×8类T4/T5；另外2016个H状态在k200起钳制0，39901个R仍由原整网真实计算。原活动数组仍是[1,485,45669]，未失活状态共43653。没有导出一个3752节点独立网络。',
      '',
      '只有ON60/OFF90，固定331点官方flow ROI、主窗200–285、Sham基线160–199及Full/完整钳制/七档保留对照。复算E为0.2329377146/0.2286116328、M0.8954301133/0.9192645004、Q0.8737675544/0.8963919716、场角12.62862653°/12.80793455°。未触发旧联合损伤规则不等于数值等价或完整功能恢复。空间覆盖和回路作用同时变化，中间档一次运行、无逐规模静止分解。',
      '',
      '本轮仅迁移其刺激来源、身份方法和边界审计经验，不能迁移其光流数值或“3752独立部署”结论。详见[原始复核](OLD_3752_AUDIT.json)。',
      '',
      '## 结构与固定实验',
      '',
      '原非零类型图有63类位于T4/T5祖先闭包，仅Mi11/Tm30不在闭包；最大的强连通类型组为61类。这是图论结果，不是每类型的因果重要性证明。最省空间的路线是缩小视觉空间并保留上游/反馈类型，而非假定T4/T5能脱离其余网络。',
      '',
      '六候选：全类型空间r2/r3/r4/r6；r4直接T4/T5输入类型+感光器/lamina；r4常见Mi/Tm运动主通路+感光器/lamina。所有原内部边、自连接和零权重边保留原ID/次序及参数，所有入界/出界边明确删除；没有外界神经状态、边界电流或简化上游模型。',
      '',
      '原方程包含1/max(tau,dt)、ReLU释放与Euler原运算顺序；候选从bias开始，用自身图灰屏200步得到a0，再独立运行485步。参数均来自原GPU-native展开包。独立NumPy更新器先在ON60原完整45669节点×485步校准，最大误差1.430511475e-6，固定atol=rtol=1e-5无超限。',
      '',
      '先用ON60/OFF90筛选，再冻结A_R3/a_r4/A_R6名单，才运行ON240/OFF270/OFF60/ON90。OFF60与ON90用于同角度极性对照，避免ON60与OFF90的角度混淆。原四条件参考复用封存Full；额外两条件参考是经校准的原方程独立CPU Full，未调用官方GPU，也未冒充新官方decoder结果。',
      '',
      '固定ROI为中心r1七位置×八类型=56神经元。各自扣160–199基线，主窗200–285；另报基线偏移、原轨迹误差及尾部斜率。局部神经E/Q/M不是旧官方光流E/Q/M。E≤0.35、相关≥0.90、幅度0.60–1.40等门槛提前冻结；方向与同角度ON/OFF为基线相减整流峰值的成对对比，不叫12方向DSI。',
      '',
      '## 实际候选结果',
      '']
    for name in ['A_R3','a_r4','A_R6']:
        r=next(v for v in resources if v['name']==name);v=by_name[name]
        lines.append(f"- **{name}：{r['n_neurons']}节点、{r['n_synapses']}边、{r['n_retina_pixels']}输入点**。完全独立多步递推通过；本轮功能{'PASS' if v['functional_acceptance'] else 'FAIL'}。留出神经E依次ON240/OFF270/OFF60/ON90为"+' / '.join(f'{v["heldout_neural_E"][c]:.6f}' for c in ['ON240','OFF270','OFF60','ON90'])+f"；方向亚型{v['opposite_direction_subtypes_preserved']}/8、同角度极性{v['polarity_combinations_preserved']}/4通过，一次ON240复跑逐位一致。")
    lines += ['',
      'A_R3的ON240 E=0.363846超过0.35，保留阴性并拒绝完整功能PASS，未放宽阈值。a_r4的T4a/b/c/d、T5b/c/d保留本轮方向对比；T5a仍同号但强度差过大（D原−0.998209，候选−0.247237），该亚型不通过。这说明总体轨迹接近不能掩盖特定亚型损失。A_R6八亚型均通过成对门槛。两者在60/90°都保留T4偏ON、T5偏OFF的家族读出。',
      '',
      'A_R2（1203/28904）筛选神经E为0.431639/0.455116；B_DIRECT_R4（2196/62093）为0.516323/0.542706；B_CANONICAL_R4（1769/30590）为2.051701/2.711753，且幅度2.576923/3.128613、基线偏移RMS5.396406，均失败。不能把组删实验归因给某一个被删细胞类型；此轮没有按权重阈值删边、重新拟合bias或调参救回结果。',
      '',
      '所有实际轨迹有限，选中模型最大绝对状态低于6（全筛选包含失败类型候选的最大状态约10.84，也未数值发散）；保持时间响应，独立冷启动重复逐位一致。仅证明3.425s模型时间的稳定及中心局部响应，未测长时扰动/噪声鲁棒性、边缘全部位置或生物行为。',
      '',
      '## 独立运行证据与读出限制',
      '',
      '模型state长度只有本候选节点数，step只能接受同长度old和裁剪后的感光器输入；source/target只引用本地保留节点。每条轨迹保存200步自适应、a0、485步全候选态、完整COMMIT旧/新态digest链及输入digest；引用Full只在rollout完成后的分析函数。27条科学轨迹的18495提交链、原参数/原边映射和有限性已保存数据审计通过，无神经重新计算。',
      '',
      'a_r4另在只含两份Python代码、model.npz和61点local_input的便携目录，以Python隔离模式冷启动200+485步；没有原FlyVis、全网数据或未来状态文件，结果与ON240科学轨迹逐位相同。首次隔离启动因Python -I不添加脚本目录而在模块导入前失败，神经步0；只修复便携启动器本目录import并保留失败记录，冻结的科学更新器/模型/门槛未改。',
      '',
      '保留全部65类型的较小空间层也缺少官方decoder所需34×721完整层，因此本轮官方光流、官方12方向DSI均NOT_RUN/NOT_APPLICABLE，绝不把缺失层补零后称官方光流。原12方向DSI记录仅作为基线背景；本轮是明确的局部方向/ON-OFF读出，不能继承旧DSI或旧flowPASS。',
      '',
      '## Zynq-7020价值及瓶颈',
      '',
      f"首选供用户决定的是a_r4：节点/边减少{a['nodes_reduction_percent']:.2f}%/{a['edges_reduction_percent']:.2f}%；相较A_R6资源更小，但接受其T5a方向强度损失和最大留出神经E0.249031。A_R6作为精度备选，不能以此冻结硬件规模。",
      '',
      'AMD DS190规定Z-7020为53,200 LUT、140个36Kb BRAM、220 DSP。名义140×4608=645120字节约630KiB；32bit数据payload保守按140×4096=573440字节约560KiB，物理端口配置/奇偶位/宽度碎片决定实际可用。来源：[AMD官方DS190](https://www.amd.com/content/dam/xilinx/support/documents/data_sheets/ds190-Zynq-7000-Overview.pdf)。',
      '',
      f"- a_r4：原float32权重+16bit本地source/target记录共{a['fp32_edge_table_bytes']}字节（约{a['fp32_edge_table_bytes']/1024**2:.3f}MiB）；双状态/电流/bias/tau系数及行指针/输入缓冲估{a['working_state_parameter_buffer_bytes']}字节（约{a['working_state_parameter_buffer_bytes']/1024:.1f}KiB），共{a['estimated_total_bytes']}字节。纯BRAM容纳不了全部表；可考虑片上状态+PL读取本机DDR静态突触表，PS只送输入/控制，不补算被删神经元。200模型步/s的8字节边表裸读需求{a['edge_only_bandwidth_MBps_at_200_model_steps_s']:.3f}MB/s；实际AXI/DDR效率、累加依赖与仲裁尚未测。",
      f"- A_R6：边表{b['fp32_edge_table_bytes']}字节（约{b['fp32_edge_table_bytes']/1024**2:.3f}MiB），工作存储约{b['working_state_parameter_buffer_bytes']/1024:.1f}KiB，裸边表需求{b['edge_only_bandwidth_MBps_at_200_model_steps_s']:.3f}MB/s，更依赖DDR吞吐。",
      '- A_R3：8字节边表+工作区名义合计562252字节，仅勉强低于32bit BRAM payload，几乎没有FIFO/其他逻辑空间，且其功能门槛已经失败，不能因为更易装入就选为成功模型。',
      '',
      f"假设100MHz每边一周期并加6次/神经元操作，a_r4/A_R6每步乐观下界{a['optimistic_one_edge_per_cycle_100MHz_step_ms']:.3f}/{b['optimistic_one_edge_per_cycle_100MHz_step_ms']:.3f}ms；不是实际时延或200Hz达成证据。float32乘加资源、BRAM banking/目标累加冲突、DDR随机/连续访问、LUT/DSP及全SoC空间均未综合。这里不选择定点格式，量化需后续另授权数值门槛。",
      '',
      '本轮独立CPU模型不依赖GPU；硬件若实现整个该候选的神经更新并使用本机DDR，其独立性在架构上成立。但真实FPGA部署性能/资源仍是待实现问题，不是本报告的PASS范围。',
      '',
      '## 运行、复现与停止',
      '',
      f"实际计数：27条候选冷启动实验={result['counts']['candidate_commits']}模型步（含灰屏）；便携冷启动685步；整网数值校准485步、额外两条件CPU Full参考970步。此前只为估时的未预注册整网单步1次另列，不作为功能结果。新GPU/decoder步0。候选计算含记录合计{result['timings']['candidate_rollout_record_s']:.3f}s，校准{result['timings']['calibration_CPU_s']:.3f}s，额外Full参考{result['timings']['extra_full_reference_CPU_s']:.3f}s，便携检查{result['timings']['portable_CPU_s']:.3f}s；筛选阶段{result['timings']['screen_phase_wall_s']:.3f}s、验证阶段{result['timings']['holdout_phase_wall_s']:.3f}s。进程启动/准备/报告写作不包含在case计算时间，不能称纯算子耗时。",
      '',
      '主要入口与数据：',
      '',
      '- [冻结协议](PREREGISTRATION.json)、[可读方案](PROTOCOL.md)、[结构图统计](STRUCTURE.json)、[旧3752复核](OLD_3752_AUDIT.json)。',
      '- [独立更新器](independent_model.py)、[有界阶段程序](study.py)、[单模型便携运行](standalone_run.py)、[a_r4便携包](standalone_package/a_r4/readme.txt)。',
      '- 每模型 `models/<name>/model.npz`、manifest.json、node_map.csv、读出global/local IDs及删除边ID。每条件 `artifacts/<screen|holdout|repeat>/<name>/<condition>/` 包含local_input、a0、warmup/states/final_state及step journal/result/metrics。',
      '- [逐条件局部神经指标](LOCAL_NEURAL_METRICS.csv)、[方向对比](PAIRED_DIRECTION.csv)、[同角度ON/OFF](ON_OFF_SAME_ANGLE.csv)、[资源估算](RESOURCE_ESTIMATES.csv)。',
      '- [独立状态链审计](INDEPENDENCE_AUDIT.json)、[便携检查](PORTABILITY_CHECK.json)、[总结果](RESULT.json)、[本轮SHA清单](DELIVERY_MANIFEST.json)。',
      '',
      '便携运行只需要Python+NumPy，在包目录执行 `python -I -B standalone_run.py --model model.npz --input local_input.npy --output <新的输出目录>`。输出目录已存在则拒绝覆盖。',
      '',
      '第一批研究完成后停止。建议用户先决定是否以a_r4的局部运动计算及DDR方案作为第二个FPGA实验；若要求八个方向亚型全部更接近原参考，则评估A_R6。尚未测试r5、更精细反馈类型裁剪、其他速度/空间位置/方向、长期稳定性或完整decoder功能，不能声称找到全局最小。任何后续科研/硬件均另立范围；不自动增跑或移植。',
      '']
    (HERE/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':main()
