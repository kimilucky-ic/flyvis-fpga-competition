"""Produce handoff only after live runs, all-state audit and all frozen metrics pass."""
import csv,shutil
from common import *

def main():
    output=HERE/'B_ABLATION_SCREEN_4CONDITIONS.json'
    if output.exists():raise SystemExit('Preserve completed delivery')
    audit=load(HERE/'artifacts/formal_audit/result.json');analysis=load(HERE/'artifacts/formal_analysis/result.json');reg=load(HERE/'PRE_RUN_REGISTRATION.json');spec=load(HERE/'spec_snapshot/spec_config.json')
    assert audit['status']=='PASS_SOFTWARE_ABLATION_IMPLEMENTATION' and analysis['status']=='PASS_PRE_REGISTERED_METRIC_ANALYSIS'
    names=['B_T5c','A_T4c','C_T4T5_all_centers'];ap=HERE/'artifacts/formal_analysis';rows=list(csv.DictReader((ap/'direction_metrics.csv').open()));summary=analysis['candidates']
    def metric(name,pop,pol,mode,rep='formal_r1'):return next(r for r in rows if r['candidate']==name and r['population']==pop and r['polarity']==pol and r['mode']==mode and r['repeat']==rep)
    comparisons=[]
    for name in names:
        for pop in spec['primary_metric']['populations']:
            for pol in ['OFF','ON','JOINT']:
                a,b=metric(name,pop,pol,'Ablation'),metric(name,pop,pol,'Ablation','formal_r2')
                assert abs(float(a['S'])-float(b['S']))<=.01 and abs(float(a['E'])-float(b['E']))<=.01
                comparisons.append(dict(candidate=name,population=pop,polarity=pol,S_repeat_abs_delta=abs(float(a['S'])-float(b['S'])),E_repeat_abs_delta=abs(float(a['E'])-float(b['E']))))
    newdir=HERE/'artifacts/final_delivery';newdir.mkdir()
    allmetrics=[]
    for filename in ['direction_metrics.csv','signed_response_and_normalization_metrics.csv','two_angle_contrast_metrics.csv','all_condition_population_differences.csv','live_feedback_summary.csv','prebaseline_drift.csv']:
        allrows=list(csv.DictReader((ap/filename).open(encoding='utf-8')))
        left=[{k:v for k,v in row.items() if k!='repeat'} for row in allrows if row['repeat']=='formal_r1']
        right=[{k:v for k,v in row.items() if k!='repeat'} for row in allrows if row['repeat']=='formal_r2']
        assert left==right,filename
        allmetrics.append(dict(file=filename,rows_per_repeat=len(left),all_values_identical=True))
    dump(newdir/'metric_reproduction.json',dict(status='PASS_ALL_PRESET_METRICS_REPRODUCED',primary_rows=comparisons,all_metric_tables=allmetrics))
    response=list(csv.DictReader((ap/'signed_response_and_normalization_metrics.csv').open()));centers=[]
    for name in names:
        for c in range(4):
            for center in spec['candidates'][name]['T4_T5_centers_membership']:
                group='center_'+str(center['global_node_index'])+'_'+center['cell_type'];item=dict(candidate=name,condition=c,polarity=reg['conditions'][c]['polarity'],angle=reg['conditions'][c]['angle'],**center)
                for mode in ['Full','Sham','Ablation']:
                    row=next(r for r in response if r['repeat']=='formal_r1' and r['candidate']==name and r['condition']==str(c) and r['population']==group and r['mode']==mode and r['window']=='primary')
                    for key in ['signed_mean_response','signed_AUC','absolute_AUC','max_excitation_shift','min_inhibition_shift','baseline_mean']:item[mode+'_'+key]=float(row[key])
                item['A_minus_S_signed_mean']=item['Ablation_signed_mean_response']-item['Sham_signed_mean_response'];centers.append(item)
    with (newdir/'all_8_centers_four_conditions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(centers[0]));w.writeheader();w.writerows(centers)
    dump(HERE/'artifacts/signed_all_node_differences_r1/result.json',dict(status='PASS_ALL_SIGNED_NODE_DIFFERENCES_EXACT_FLOAT64',shape=[4,485,45669],candidates=names,
        axes=['bundle_condition OFF0/ON0/OFF180/ON180','step k with activity_after=a[k+1]','global_node_id 0..45668'],verification= audit['status'],
        repeat2_raw_preserved=True,repeat2_reproduced_bitwise=all(r['bitwise_equal'] for r in audit['reproductions']),code_sha256=file_hash(HERE/'export_signed_differences.py')))
    seal(HERE/'artifacts/signed_all_node_differences_r1')
    runtime=[load(HERE/'artifacts'/repeat/'result.json') for repeat in ['formal_r1','formal_r2']]
    prepare_timing=[]
    for repeat in ['formal_r1','formal_r2']:
        for name in names:
            for mode in ['Sham','Ablation']:
                events=[json.loads(line) for line in (HERE/'artifacts'/repeat/name/mode/'step_status.jsonl').read_text().splitlines()]
                durations=[r['wall_prepare_ms'] for r in events if r['status']=='PREPARED']
                prepare_timing.append(dict(repeat=repeat,candidate=name,mode=mode,n_prepared=len(durations),sum_prepare_s=sum(durations)/1000,median_prepare_ms=float(np.median(durations)),
                    timing_scope='GPU R + CPU H + snapshot/hash/validation; excludes commit/comparison/disk export; not pure neural kernel timing'))
    dump(newdir/'timing.json',dict(process_results=runtime,prepare=prepare_timing,pure_neural_compute_s=None,isolated_comparison_s=None,isolated_export_s=None,
        performance_claim='NONE; actual whole batch and prepare timings only'))
    sources=HERE/'source_snapshot';sources.mkdir()
    for p in sorted(HERE.glob('*.py')):shutil.copy2(p,sources/p.name)
    shutil.copytree(HERE/'dependencies',sources/'dependencies');seal(sources)
    handoff=dict(status='PASS_SOFTWARE_ABLATION_IMPLEMENTATION',campaign_id=reg['campaign_id'],spec_sha256=reg['spec_sha256'],spec_config_sha256=reg['spec_config_sha256'],spec_manifest_sha256=reg['spec_manifest_sha256'],
        registration_sha256=file_hash(HERE/'PRE_RUN_REGISTRATION.json'),operator='BLOCK_HR_RELEASE',onset_step=200,modes=['reused_verified_original_GPU_Full','new_live_Sham','new_live_Ablation'],
        n_conditions=4,steps_per_condition=485,dt_s=.005,n_nodes=45669,n_original_edges=1513231,actual_new_condition_runs=48,actual_closed_loop_steps=23280,independent_process_ids=audit['process_ids'],
        comparison_ids=reg['comparison_ids'],model=spec['model'],fixture=spec['fixture'],Full_reference=reg['Full_reference'],candidate_results=summary,
        gates=dict(G_AB0='PASS',G_AB1='PASS',G_AB2='PASS'),all_23k_H_recomputed_bitwise=True,all_repeat_trajectories=audit['reproductions'],all_primary_metric_repeat_checks=comparisons,all_metric_tables_reproduced=allmetrics,
        best_four_condition_function_demonstration=dict(candidate='C_T4T5_all_centers',basis='largest fixed shared V OFF and ON direction trace change E; main Full-axis response mostly retained',
            interpretation='direction-related temporal/structural change; not loss of all motion function; no optical-flow accuracy claim'),
        extension_effect_branch_candidates=[s['candidate'] for s in summary if s['effect_branch']],extension_24_conditions_executed=False,extension_execution_list='REQUIRES_ARCHITECT_AND_USER_REVIEW',
        existing_67_FPGA_work_unchanged=True,hardware_candidate_not_frozen=True,FPGA_execution=False,FPGA_restoration_proven=False,
        evidence_level='ACTUAL_SOFTWARE_CLOSED_LOOP_AND_POST_RUN_NUMERICAL_ANALYSIS',code_manifest_sha256=file_hash(sources/'artifact_manifest.json'),
        artifact_refs=dict(report='REPORT.md',comparison='artifacts/formal_analysis/three_candidate_function_comparison.csv',direction_metrics='artifacts/formal_analysis/direction_metrics.csv',
            all_step_population_differences='artifacts/formal_analysis/{repeat}/{candidate}/all_population_step_differences.csv',all_full_trajectories='artifacts/{formal_r1,formal_r2}/{candidate}/{Sham,Ablation}/activities_full.npy',
            all_node_float64_differences='artifacts/signed_all_node_differences_r1/{candidate}_A_minus_S_float64.npy',raw_H_boundary='artifacts/{repeat}/{candidate}/{mode}/condition_{c}/SOURCE_RAW_step_io.npz',
            status='artifacts/{repeat}/{candidate}/{mode}/step_status.jsonl',request_identity='artifacts/{repeat}/{candidate}/{mode}/request_bindings.jsonl',gate_current='artifacts/{repeat}/{candidate}/{mode}/gate_steps.csv',
            center_summary='artifacts/final_delivery/all_8_centers_four_conditions.csv',feedback='artifacts/formal_analysis/live_feedback_summary.csv',faults='artifacts/formal_hook_tests/result.json',conflicts='artifacts/formal_conflict_tests/result.json',
            audit='artifacts/formal_audit/result.json',metric_reproduction='artifacts/final_delivery/metric_reproduction.json',semantic_interface='H_STEP_AND_ABLATION_SEMANTICS.md'),
        limitations=['Only four MovingEdge conditions; no official 12-angle DSI/PD','One pretrained checkpoint; no biological or decoding accuracy test','Full reused according to spec, not newly executed',
            'Timeout is software exception injection; real PL/network/DMA fail recovery untested','Pure kernel/comparison/export timing not separately measured; no real-time claim','No RTL/fixed-point/board change or functional restoration claim'],
        next_owner='③(2) architecture review',next_action='Review all candidates and approve at most 1-2 candidates/slot for 24 conditions; ⑥ current67 work continues independently')
    dump(output,handoff)
    lines=['# 三候选四条件正式软件消融筛选','', '**PASS_SOFTWARE_ABLATION_IMPLEMENTATION**。③规范v1的G-AB0/1/2全部通过。实际新执行Sham/Ablation各三候选四条件，并用第二个独立进程完整复算，共48个485步condition-runs、23,280次统一提交。Full复用已验收官方GPU全网参考，不称本轮新执行。','',
        '本轮最有方向相关功能展示价值的是**联合298节点候选**：固定共同R中的1,057个下游T4/T5读出上，OFF/ON方向差结构变化均最大。但其沿Full方向轴仍保留约93%，不能把47.7%的相对方向差改变写成47.7%的功能丧失。软件筛选不改变⑥原67节点SOURCE_RAW硬件工作，不证明FPGA功能恢复。','',
        '## 实际结果与公平读出','', '主读出V=1,057、支持读出D=3,312，均严格位于三候选H并集之外；没有根据消融结果挑节点。所有数值使用原signed activity，float64分析，按各模式160..199步基线校正，主响应200..484步。S是沿Full方向差轴的保留系数，E是方向差轨迹相对L2改变；不是DSI、偏好方向或光流精度。','']
    for s in summary:
        lines.append(f"- **{s['candidate']}**：H={s['n_H']}，HH={s['HH']}，阻断HR={s['HR']}。V OFF S={s['V_OFF_S']:.9f}、E={s['V_OFF_E']:.9f}；ON S={s['V_ON_S']:.9f}、E={s['V_ON_E']:.9f}；联合S={s['V_joint_S']:.9f}、E={s['V_joint_E']:.9f}。R全程最大状态变化={s['R_max_abs_change']:.9f} activity units，四条件中最多{s['R_changed_nodes_max']}个R节点超过Full定义的数值floor。效果扩展分支={s['effect_branch']}。")
    lines+=['', '[三候选完整功能影响对照表](artifacts/formal_analysis/three_candidate_function_comparison.csv)；[V/D及ON/OFF/联合全部主指标](artifacts/formal_analysis/direction_metrics.csv)；[全部条件/人口差异](artifacts/formal_analysis/all_condition_population_differences.csv)；[ signed响应、AUC与归一化变化](artifacts/formal_analysis/signed_response_and_normalization_metrics.csv)；[两方向对比](artifacts/formal_analysis/two_angle_contrast_metrics.csv)。','',
        '![固定V方向指标](artifacts/formal_figures/fixed_V_direction_comparison.png)','', '## 阻断与真实反馈证据','',
        '从第200步起，仅原始HR边电流在target scatter前乘零；原边全部保留，正/负/零权均纳入mask。H、HH/RH/RR及所有原权重继续计算。Sham使用相同全长mask和乘法路径，gain均为1。每步H/R读取同一a[k]，候选检查后统一提交a[k+1]。没有Full先运行再覆盖，没有录制R作边界，没有最终输出置零。','',
        '全部Sham的45,669节点逐步误差在atol=rtol=1e-5门限内，最大9.5367431640625e-7。Ablation在0..199步与本候选Sham逐位一致；首次阻断步200的H新状态仍逐位相同。之后真实R状态与RH驱动变化使H产生反馈偏离。全部23,280次H输出与chemical，用各自实际旧R边界重新计算，逐位一致；原生H生产更新为0。两独立进程全部模式、全部节点、全部步逐位复现，最大差0，主S/E复算差0。','',
        '[真实反馈时间定位及原边权数](artifacts/formal_analysis/live_feedback_summary.csv)、逐步live_feedback CSV、[新hook37项/候选负测试](artifacts/formal_hook_tests/result.json)、[追加冲突重复prepare及失败后commit测试](artifacts/formal_conflict_tests/result.json)、[全部状态链/原边/复算审计](artifacts/formal_audit/result.json)提供原始证据。人工old_H单步扰动在Sham改变R，在Ablation对R的直接效应严格为零；独立原始全边电流门控R单步对照逐位一致。','',
        '## 阴性结果、解释与下一步','',
        '67候选虽明显改变R状态，但V的两极性E均低于预设0.20效果扩展门槛；不能根据全网大误差宣称明显方向功能损失。其ON沿Full方向轴略增强（S>1），OFF仅小幅弱化。92候选ON E超过门槛，但沿轴仅弱化约3.8%。联合候选OFF/ON沿轴仅弱化约6.9%/7.2%，较大的E表明结构/时间成分改变。三个候选均非整组T4/T5简单同类型集合，HR阻断集合也不嵌套，不能推断规模单调效应或协同。','',
        '92和298满足规范效果分支，67保留历史目标偏好方向覆盖不足的扩展理由。建议③优先评审298作为功能变化研究对象；第二名额由③在92的已检出ON结构变化与67的硬件衔接/方向覆盖之间选择。尚未运行24条件，也未冻结新硬件回路。四条件不能估计官方12方向DSI/PD，不能证明真实视觉行为或光流精度下降。','',
        '8个中心逐一标H/R归属，联合候选全部8中心属于H，它们仍计算不等于阻断失败。查看[全部8中心四条件signed响应](artifacts/final_delivery/all_8_centers_four_conditions.csv)及65中心/T4/T5类型完整轨迹，不裁抑制响应。','',
        '## 数据、身份与复算','',
        f"规范SHA `{reg['spec_sha256']}`；配置SHA `{reg['spec_config_sha256']}`；规范manifest SHA `{reg['spec_manifest_sha256']}`。首次正式运行前已登记[PRE_RUN_REGISTRATION](PRE_RUN_REGISTRATION.json)。完整a0、GPU-native参数、刺激、time、condition及H/HR节点边表全部SHA前后不变。共同campaign `{reg['campaign_id']}`；每候选comparison和每模式独立run UUID见机器交接/各run_identity。两个进程PID分别为{audit['process_ids']}。",'',
        '原始轨迹在 `artifacts/formal_r1|formal_r2/{候选}/{Sham|Ablation}/activities_full.npy`，shape=[4,485,45669] float32；`signed_all_node_differences_r1`内三份完整A−S为float64，同shape，已逐元素核验。H/R列由冻结全局节点映射选择。每条件SOURCE_RAW_step_io含old_H/真实旧R边界/x_H/chemical/new_H、节点ID和时间；日志含PREPARED、COMMITTED、请求身份、gain、电流。原Full轨迹链接及SHA在机器交接中，没有重复拷贝。','',
        '保持原官方输入time标签k*0.005-1；activity_after[k]=a[k+1]；另明确before_time=原标签、after_time=原标签+0.005。485步包含200个实际preframes，每条件每模式从相同完整a0重置，无额外warmup或跨条件继承。','',
        '[机器交接](B_ABLATION_SCREEN_4CONDITIONS.json)、[完整源码快照与SHA](source_snapshot/artifact_manifest.json)、[H.step及消融语义](H_STEP_AND_ABLATION_SEMANTICS.md)、[时间日志](artifacts/final_delivery/timing.json)。`run_formal.py`拒绝覆盖已有run；复算须先复制已冻结输入/spec/代码/依赖到本工作线的新空目录，再以两个新进程分别执行`--repeat formal_r1`与`--repeat formal_r2`。`export_signed_differences.py`可无损生成任一模式对比的逐步全节点float64差分，只允许新文件且输出位于本线。','',
        f"进程r1/r2的实测批处理时间分别为{runtime[0]['wall_s']:.3f}s和{runtime[1]['wall_s']:.3f}s（包含加载、计算、比较与多数写盘，末尾根清单seal另计）。PREPARED日志有GPU R+Python H+快照/校验联合计时；纯神经核、比较及导出未独立计时，未知值null，不据此声称实时性能。",'',
        '首个input_bundle因A/B数组摘要格式不同在准备阶段失败，已保留[failure.json](input_bundle/failure.json)及原文件；经原定义摘要验证的input_bundle_r2才进入正式实验。故障用例的timeout为异常注入，真实PL/DMA/网络恢复未测。未做RTL、定点、综合、bitstream、板操作或FPGA功能恢复。','',
        '本次可复算软件流程已由两个新进程验证，文档与代码快照作为证据保留；没有增加通用硬件Skill或泛化恢复声明。下一具体动作是③(2)审核本机器交接、效果/覆盖分支并决定24条件名单和时段；⑥原67硬件工作不受本筛选阻塞。','']
    (HERE/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8');seal(newdir);seal(HERE)
    print(json.dumps(dict(status=handoff['status'],root_manifest_sha256=file_hash(HERE/'artifact_manifest.json'),artifact_bytes=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()),best_candidate='C_T4T5_all_centers'),ensure_ascii=False))

if __name__=='__main__':main()
