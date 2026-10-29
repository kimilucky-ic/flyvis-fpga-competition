"""Create the B handoff from accepted artifacts, without rerunning a network."""
from pathlib import Path
import csv, json, math, shutil
import numpy as np
from h_step import file_hash

HERE=Path(__file__).resolve().parent
ART=HERE/'artifacts'
BUNDLE=HERE.parents[2]/'fly/gpu_phase2/artifacts/reference_bundle_gpu_native_v1'


def load(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def main():
    audit=load(ART/'final_native_audit/result.json')
    assert audit['status']=='PASS_SOFTWARE_CLOSED_LOOP'
    source=load(ART/'source_gpu_native_r1/result.json')
    aggregate=load(ART/'aggregate_gpu_native_r1/result.json')
    feedback=load(ART/'live_feedback_native_r1/result.json')
    io=load(ART/'native_gpu_step_io/result.json')
    assert io['status']=='PASS_EXPORTED_LIVE_H_STEP_IO'
    pair=load(ART/'final_native_audit/aggregate_vs_source.json')
    node_map=list(csv.DictReader((BUNDLE/'candidates/B_T5c/node_map.csv').open(encoding='utf-8')))
    center_t5c=next(int(row['global_node_index']) for row in node_map
        if row['cell_type']=='T5c' and row['u']=='0' and row['v']=='0')
    hsource=node_map[feedback['feedback']['H_source_global']]
    rsource=node_map[feedback['feedback']['R_intermediate_global']]
    full=np.load(ART/'full_gpu_reference_a/activities_full.npy',mmap_mode='r',allow_pickle=False)
    central=np.load(BUNDLE/'central_node_indices.npy',allow_pickle=False)
    t4t5=[int(i) for i in central if node_map[int(i)]['cell_type'].startswith(('T4','T5'))]
    rows=[];readout_rows=[]
    for run,result in [('source_gpu_native_r1',source),('aggregate_gpu_native_r1',aggregate)]:
        actual=np.load(ART/run/'activities_full.npy',mmap_mode='r',allow_pickle=False)
        for c,record in enumerate(result['conditions']):
            per_step=list(csv.DictReader((ART/run/f'condition_{c:02d}/step_errors.csv').open()))
            row=dict(mode=result['run_identity']['mode'],condition=c,original_sample=record['condition']['original_sample'],
                polarity=record['condition']['polarity'],angle_deg=record['condition']['angle'],steps=485)
            for group in ['H','R','full','central','T4T5']:
                row[group+'_max_abs']=record['max_abs'][group]
                row[group+'_trajectory_mae']=sum(float(r[group+'_mae']) for r in per_step)/485
                row[group+'_trajectory_rmse']=math.sqrt(sum(float(r[group+'_rmse'])**2 for r in per_step)/485)
                row[group+'_max_step_mae']=max(float(r[group+'_mae']) for r in per_step)
                row[group+'_max_step_rmse']=max(float(r[group+'_rmse']) for r in per_step)
                row[group+'_final_max_abs']=record['final'][group]['max_abs']
                row[group+'_violations']=record['violations'][group]
            rows.append(row)
            for global_id in t4t5:
                delta=actual[c,:,global_id].astype(np.float64)-full[c,:,global_id].astype(np.float64)
                readout_rows.append(dict(mode=row['mode'],condition=c,polarity=row['polarity'],angle_deg=row['angle_deg'],
                    cell_type=node_map[global_id]['cell_type'],global_node_index=global_id,
                    max_abs=float(np.abs(delta).max()),mae=float(np.abs(delta).mean()),
                    rmse=float(np.sqrt((delta*delta).mean())),final_abs=float(abs(delta[-1]))))
    for name,values in [('condition_error_summary.csv',rows),('central_T4T5_error_summary.csv',readout_rows)]:
        with (ART/'final_native_audit'/name).open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
    snapshot=HERE/'dependencies/controller_received_software_confirmation'
    snapshot.mkdir(exist_ok=True)
    docs=HERE.parents[1]/'docs/flyvis_visual_hybrid'
    for name in ['DECISION_LOG.md','PYTHON_REPLACEMENT_GATE.md','INTERFACE_CONTRACT.md','PHASE1_REVIEW_20261010.md']:
        target=snapshot/name
        if target.exists():assert file_hash(target)==file_hash(docs/name)
        else:shutil.copyfile(docs/name,target)
    gpu_summary=[]
    for row in rows:
        gpu_summary.append('| '+ ' | '.join([row['mode'],row['polarity']+' '+str(row['angle_deg'])+'°',
            f"{row['H_max_abs']:.9e}",f"{row['R_max_abs']:.9e}",f"{row['full_final_max_abs']:.9e}",
            f"{row['central_max_abs']:.9e}",f"{row['T4T5_max_abs']:.9e}"])+' |')
    identity=source['run_identity']
    summary=dict(status='PASS_SOFTWARE_CLOSED_LOOP',phase='2',candidate='B_T5c67',
        software_candidate_user_confirmed=True,final_FPGA_candidate_frozen=False,evidence_level='SOFTWARE_CLOSED_LOOP',
        protocol_version='0.1',controller_state='DRAFT_NOT_FROZEN',comparison_id=audit['comparison_id'],
        identity={key:audit[key] for key in ['model_id','source_commit','checkpoint_sha256','connectome_sha256',
            'expanded_parameters_sha256','initial_state_sha256','stimulus_sha256','time_axis_sha256',
            'H_ids_hash','node_map_sha256','edge_partition_sha256','numeric_profile_sha256','metric_profile_sha256']},
        conditions=[dict(original_sample=i,polarity=p,angle=a) for i,p,a in [(0,'OFF',0),(1,'ON',0),(12,'OFF',180),(13,'ON',180)]],
        nodes=45669,H_nodes=67,R_nodes=45602,partition_counts=dict(HH=970,RH=5567,HR=8159,RR=1498535),
        steps_per_condition=485,dt_s=.005,source_H_max=max(r['H_max_abs'] for r in rows if r['mode']=='SOURCE_RAW'),
        aggregate_H_max=max(r['H_max_abs'] for r in rows if r['mode']=='CURRENT_AGG'),
        full_max=max(r['full_max_abs'] for r in rows),final_full_max=max(r['full_final_max_abs'] for r in rows),
        tolerance=dict(atol=1e-5,rtol=1e-5,violations=0),native_H_production_updates=0,
        H_commits_per_mode=1940,actual_GPU_negative_tests=15,live_feedback=feedback['feedback'],
        center_T5c_global_id=center_t5c,all_H_initial_state_exact=True,step_io_export='PASS_EXPORTED_LIVE_H_STEP_IO',
        fresh_process_reproduction='OFF0 first32 steps; all45669 nodes bitwise equal to SOURCE_RAW run',
        artifacts=dict(report='REPORT.md',execution='EXECUTION_RECORD.md',interface='H_STEP_INTERFACE.md',
            ablation='ABLATION_PROPOSALS.md',main_acceptance='artifacts/final_native_audit/result.json',
            CPU_baseline_acceptance='artifacts/final_audit/result.json',metrics='artifacts/final_native_audit/condition_error_summary.csv',
            step_io='artifacts/native_gpu_step_io',source_run='artifacts/source_gpu_native_r1',
            aggregate_run='artifacts/aggregate_gpu_native_r1',faults='artifacts/live_feedback_native_r1/result.json'),
        four_mode_status=dict(Full='PASS_REFERENCE_FROM_A',Ablation='PROPOSED_NOT_RUN',PythonReplacement='PASS',FPGAReplacement='NOT_RUN'),
        pending_architecture_decisions=['final H','FPGA boundary profile','finite-width profile and acceptance',
            'PS-PL transport/register/commit model','network header','ablation operator/start step'],
        scope_limits=audit['stage2_scope_limits']+['Only four MovingEdge conditions, not 24 directions/camera/decoder validation'],
        next_action='Architecture review of G2 evidence and ablation/boundary proposals before authorizing next-stage numerical/hardware work')
    dump(HERE/'handoff.json',summary)
    text=f'''# 第二阶段：T5c 独立 Python 真闭环

2026-10-10；模块 B；**PASS_SOFTWARE_CLOSED_LOOP**，范围为用户确认的 T5c 67 节点、四条件、每条件 485 步、dt=5 ms。最终 FPGA 回路/位宽/PS–PL/报头仍未冻结。机器验收见 [final_native_audit/result.json](artifacts/final_native_audit/result.json)，交接见 [handoff.json](handoff.json)。

## 结论与生产路径

独立 H 已在正在运行的完整网络中取代原 H 更新，原生 H 生产更新次数为 0。A 的真实 GPU R-only 服务只计算 HR/RR 的 R 目标；NumPy H 计算 HH/RH 和连续 Euler 更新。每步固定旧完整状态 a[k]，双方分别产生候选，身份/排序/有限值检查全部通过后统一构造并提交 a[k+1]。本步新 H 只在下一步供 R 读取。完整图仍为 45,669 节点、1,513,231 条原边：HH970、RH5,567、HR8,159、RR1,498,535。

`coordinator.py` 和 `gpu_adapter.py` 不读取 Full 活动数组；运行驱动只在提交后读取 Full 用于误差。R-only 不调用官方 Full 更新，也不计算 H 的下一活动。替换生产区的 `Network.forward`、`Network._next_state`、`PPNeuronIGRSynapses.write_state_velocity` 均被改为立即报错的护栏；四条件各 485 个独立 H 步和提交均完成，禁止调用计数均为 0。另一个故意调用护栏的负实验确实被拒绝（1 次），不计入生产路径。

## 独立动力学与同源输入

[h_step.py](h_step.py) 只使用 NumPy；原展开 sign×syn_count×syn_strength 权重、bias、time_const、原边及负活动原样保留。ReLU 只作用于突触前活动，状态不截零。计算顺序：`inverse_tau=ones/maximum(tau,float32(dt))`；`velocity=inverse_tau*(((-old+bias)+chemical)+x_H)`；`new=old+velocity*dt`。SOURCE_RAW 按原边 ID 合并 HH/RH 后 float32 累加；CURRENT_AGG 用独立 RH 汇总加到 HH 之上。两种顺序分别验收，未声称与 CUDA 逐位等价。

共享初态是 A 从 bias 经 200 个灰度 warmup 步产生的全部 45,669 节点活动；每条件独立从同一文件重置。刺激本身 200 帧前灰段仍执行。冻结 stimulus[4,485,1,721]、time、photoreceptor 8×721 映射一致；原样使用 sample 0 OFF0、1 ON0、12 OFF180、13 ON180。time[k]=k×0.005−1 标签关联该帧更新后的状态，整数 step_id 管理同步。

## 主验收：官方 GPU 原生参数

A 最终交付中，CPU 与 CUDA 的 `syn_count.exp()` 展开存在少量 float32 差异。本线保存了两套独立 comparison；CPU 基线不能与 GPU 原生参数混用。主验收从 [GPU-native H 提取](artifacts/native_gpu_inputs/extraction.json) 绑定官方 GPU 实际展开参数，H/R/Full 全部一致。HH 中 124 个权重不同于 CPU 展开，最大差 1.1920929e-7；这些是原参数展开差异，不是量化或重新训练。

主 Full 是 A 的官方 GPU Full 全节点轨迹，经文件 SHA、输入/参数身份和 A 独立重放证据核验后复制到 [full_gpu_reference_a](artifacts/full_gpu_reference_a)。B 没有把它作为在线 R 或边界来源，也没有在本轮重新执行这份 GPU Full；它是独立参考路径。来源文件 SHA 为 `1b8a684c18225100bd4b34e3ba61e8f55b3bf97a15eaecb4aca311932ab9ac80`。A 的 R 单步对照证据自身不是 B 闭环证据；下述两个 live H/R 运行才是本阶段验收。

误差按每个节点、每一时间步计算，使用事先规定 `abs(actual−Full) <= 1e-5 + 1e-5×abs(Full)`。没有事后放宽。SOURCE_RAW 和 CURRENT_AGG 都有 1,940 步、每步全部 H67/R45,602 的比较；各模式 88,597,860 个活动值比较，全部无超限。初态 H 及每步 H_before 与实际旧状态逐项一致。以下值为绝对活动误差，无物理单位。

| 模式 | 条件 | 全时段 H 最大 | 全时段 R 最大 | 最后完整状态最大 | 全时段中心65最大 | 全时段中心T4/T5八节点最大 |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(gpu_summary)}

全时段整网最大 9.536743165e-7；SOURCE_RAW H 最大 3.576278687e-7，CURRENT_AGG H 最大 3.874301910e-7。两种布局彼此的整网最大差 9.536743165e-7、H 最大差 3.576278687e-7。中心 T5c global ID={center_t5c} 的四条件及所有中心 T4/T5 单节点结果另存 [central_T4T5_error_summary.csv](artifacts/final_native_audit/central_T4T5_error_summary.csv)。

各条件完整逐步 max_abs/MAE/RMSE/超限数见 source/aggregate 各 `condition_00..03/step_errors.csv`；[condition_error_summary.csv](artifacts/final_native_audit/condition_error_summary.csv) 补充全轨迹 MAE/RMSE、最坏逐步 MAE/RMSE、最终误差。全状态时序、H_before_after、每节点全时段最大误差及最终完整差向量均保存。独立 [audit_results.py](audit_results.py) 重算每步所有分组指标，并核验每次 PREPARED/COMMITTED 的旧状态、live 入界源、下一状态摘要和令牌；101 个验收文件哈希通过。

![四条件逐步 H/R 最大误差](artifacts/final_native_audit/step_error_comparison.png)

CURRENT_AGG 的 RH 汇总本轮在主机 NumPy 上由 live R 计算。这证明当前聚合语义/数值顺序，不接受尚未实现的 GPU RH 汇总或 PL 归约，也不冻结最终 FPGA 边界。

## 反馈与故障证据

[live_feedback_native_r1](artifacts/live_feedback_native_r1/result.json) 从正常 Replacement 自身在 frame220 前的已提交状态分出对照与 +0.25 扰动分支，后续 8 步均实际调用 R-only，未使用录制 R 边界。选中原反馈边：H {hsource['cell_type']} global{hsource['global_node_index']}/local{hsource['local_index']} → R {rsource['cell_type']} global{rsource['global_node_index']}/local{rsource['local_index']} → 同一 H。HR edge1170891、权重1.3080332279；RH edge236452、权重−0.3807086945。

- H +0.25 后下一步对应 R 差 +0.08198165894，证明 H→R 实际输入依赖。
- R +0.25 后下一步对应 H 差 −0.02385851741，证明 R→H live 输入依赖。
- 保持后一步旧 H 不变，只在诊断 H 计算中恢复该 R 源为对照值，返回路径对 H 的贡献为 −0.007823854685；诊断 live H 与生产分支 H 逐位一致，证明新 R 真正返回 H。扰动身份与正常等价试验分开。

15 项真实 GPU 服务负测试全部通过：错请求/结果 step、错 epoch、NaN H/R、H 报错、独立子进程提前退出、注入 TimeoutError、H/source/R 排序错乱、旧请求摘要错配、同一步偷用未来 H、重复 commit、原生 Full 护栏正控。对尚未提交的失败步，完整状态及 next_step_id 保持不变，R 候选被丢弃；重复提交只保留第一次提交，未推进第二步。无补零或软件切换。TimeoutError 当前统一归类 CORE_ERROR，是同步适配器异常注入；未验收真实网络/PL 超时、卡死中止或持久后端恢复。

新 Python 进程、新 R 服务从同一 a0 重跑 OFF0 的前32步，全部45,669节点与 SOURCE_RAW 主运行逐位相同：[独立短段复现](artifacts/reproduce_native_prefix_r1/result.json)。未把此短段宣称为第二次完整四条件复现。

## 可运行交付与边界

- 独立 H：[h_step.py](h_step.py)；原子协调：[coordinator.py](coordinator.py)；A 对接：[gpu_adapter.py](gpu_adapter.py)；运行驱动：[run_closed_loop.py](run_closed_loop.py)。A 实现按原 SHA 保存在本线 dependencies/a_snapshot，归属 A，未改写 A 文件。
- [H_STEP_INTERFACE.md](H_STEP_INTERFACE.md) 定义显式 old_H、SOURCE_RAW/CURRENT_AGG 输入及未提交候选输出。后端可替换 `backend.step(HRequest)->HResult`，协调器仍持有提交权。
- [native_gpu_step_io](artifacts/native_gpu_step_io/result.json) 导出实际旧 H、x_H、入界输入和预期新 H 四条件逐步数组、global/local IDs、初态、时间、映射、边表和参数。独立再次计算全部 1,940 H 步与各自生产输出逐位相同。这是浮点软件样本，没有冻结 RTL 数据格式。
- [CPU-canonical 基线](artifacts/final_audit/result.json) 另行通过：本线官方 CPU Full 对 GPU R+NumPy H；整网最大1.430511475e-6，H SOURCE_RAW最大3.203749657e-7，AGG最大3.576278687e-7。它与主 GPU comparison 分开保存。
- [ABLATION_PROPOSALS.md](ABLATION_PROPOSALS.md) 提出冻结 H、阻断所有 HR 释放和选择性 HR 阻断。完整标准 Ablation 尚未运行或选定；67节点 H 含上游/反馈，不等于仅 T5c 类型。

## 身份及本轮界限

主 comparison_id：`{audit['comparison_id']}`。

- checkpoint：`{audit['checkpoint_sha256']}`
- GPU expanded parameters：`{audit['expanded_parameters_sha256']}`
- shared full a0：`{audit['initial_state_sha256']}`
- shared stimulus：`{audit['stimulus_sha256']}`
- time：`{audit['time_axis_sha256']}`
- H ID order：`{audit['H_ids_hash']}`
- node map：`{audit['node_map_sha256']}`
- HH/RH/HR/RR edge IDs：`{audit['edge_partition_sha256']}`

数值/指标 profile、run UUID、完整命令、代码与 A 依赖哈希见每个 run_identity 及总交接。运行环境 WSL FlyVisCPU、GPU venv Python3.12.3/PyTorch2.7.1+cu128/NumPy1.26.4、RTX5060 Laptop；独立 H 运行在主机 NumPy。SOURCE_RAW 包含记录/逐步核验的墙钟46.32s、CURRENT_AGG50.02s，不能由逻辑dt=5ms声称实时200Hz。峰值 CUDA allocated 147,830,272 B，只是软件测量，不是 Zynq 资源报告。

只验收四个 MovingEdge 条件；24方向、摄像头闭环、decoder、正式消融、定点、RTL、综合、bitstream和板级运行均不在本次 PASS。总架构仍需决定最终 H、FPGA profile、量化门槛/位宽、PS–PL 提交/物理接口、报头及消融语义。没有修改上述总控决策文件。

下一步建议：总架构先评审本 G2 证据与消融/边界提案，再明确下一阶段授权；本线不自行冻结硬件方案。
'''
    (HERE/'REPORT.md').write_text(text,encoding='utf-8')
    execution='''# 执行、复建与证据记录

2026-10-10；模块 B。所有正式输出在 `fpga/flyvis-circuit-selection/phase2_20261010`；唯一额外项目检查点为 `docs/workstreams/flyvis-circuit-selection.md`。A 的 `fly/gpu_phase2`、原 FlyVis/Golden 和总控均只读。

## 授权与规程

用户确认本轮 T5c 软件闭环；不冻结最终 FPGA。已读项目愿景、工作线索引/本线检查点及总控四文档。初始总控快照保存 dependencies/controller_snapshot；收到明确软件确认后的当前只读快照另存 dependencies/controller_received_software_confirmation。不要从旧快照的 PENDING 状态覆盖用户的新确认。

采用 [flyvis-gpu-reference Skill](../../.agents/skills/flyvis-gpu-reference/SKILL.md) 的既有 WSL 环境、同步 GPU 测量和身份边界原则；本任务并未重复刺激渲染或 decoder 验证，也没有新增跨板 Skill。

## 已执行顺序

1. 核验 CPU-canonical bundle 的25个文件，并与用户 init_cpu_r2 a0 对照。保存 A r_only/full_oracle 的确切 SHA 副本。实现 NumPy H、事务屏障及 stateless A 适配。
2. 单独录制边界局部回放只作为局部验证，输出 local_replay_r2，未标闭环。合成 R stub 的 negative_tests 只证明协议组件，不替代真实服务。
3. 本线单独运行官方 CPU Full（full_cpu_r2），再独立运行 source_gpu_r1 和 aggregate_gpu_r1。实际 GPU 反馈/15故障、32步新进程复现和 final_audit 通过。
4. A 完成 GPU-native 参数及官方 GPU Full 交付后，prepare_native_profile.py 核验原包/Full/A 重放证明，导出 H 原生参数和 Full 比较副本。CPU/GPU profiles 分开。
5. 用 GPU-native 包分别完成 source_gpu_native_r1、aggregate_gpu_native_r1；每个生产路径原生 Full/H 护栏禁用。verify_live_feedback.py 完成15个实际 GPU 服务负实验及双向8步因果分支；reproduce_live_prefix.py 完成独立32步短段。
6. seal_artifacts.py 按 run 记录的 SHA 保存实际执行代码，不把后来的代码改动混入旧 run。audit_results.py 独立复算全部45,669节点每步误差、H before/after及 live旧状态链；export_step_io.py 输出实际输入/结果并逐步再计算 H，所有输出匹配。render_stage2.py 的原生 GPU 图已目视检查。

## 可复建调用

在 WSL FlyVisCPU 的 `/opt/flyvis-gpu-venv/bin/python` 运行。所有 --run 必须新名字，程序不会覆盖已有目录。已有固定来源由 SHA 绑定；B 没有改变官方网络参数。

```text
python prepare_native_profile.py
python run_closed_loop.py --run NEW_source --mode SOURCE_RAW --device cuda --bundle /mnt/c/Users/hzy72/Documents/ChatGPT/fly/gpu_phase2/artifacts/reference_bundle_gpu_native_v1 --static-path <本线>/artifacts/native_gpu_inputs/static_boundary_gpu_native.npz --reference <本线>/artifacts/full_gpu_reference_a
python run_closed_loop.py --run NEW_aggregate --mode CURRENT_AGG --device cuda --bundle <同一包> --static-path <同一H参数> --reference <同一Full比较目录>
python verify_live_feedback.py --run NEW_feedback --bundle <同一包> --static-path <同一H参数> --source-run <本线>/artifacts/NEW_source
python reproduce_live_prefix.py --run NEW_prefix --bundle <同一包> --static-path <同一H参数> --source-run <本线>/artifacts/NEW_source
python seal_artifacts.py NEW_source NEW_aggregate NEW_feedback NEW_prefix
python audit_results.py --run NEW_audit --profile OFFICIAL_NATIVE_GPU_EXPANDED --bundle <同一包> --static-path <同一H参数> --full-run full_gpu_reference_a --source-run NEW_source --aggregate-run NEW_aggregate --feedback-run NEW_feedback --reproduce-run NEW_prefix
```

以上是说明式命令，尖括号需替换；已实际执行的无占位绝对命令在 run_identity.json 和 feedback/prefix result.json。prepare_native_profile.py 若准备目录已存在会拒绝覆盖，可直接用已经验收的准备产物。主机 H/export/audit 无 CUDA 依赖，GPUAdapter 与运行器需要 A 的 GPU环境和 FlyVis护栏。

## 错误、修复与未复现界限

- 最初 Full 使用 Windows 挂载盘作为 FLYVIS_ROOT_DIR，HDF5 构图缓存出现 `bad object header version number`，full_cpu_r1仅留下身份记录，未得到参考或 PASS。随后将临时构图缓存限定为 Linux原生 `/tmp/flyvis-circuit-selection-phase2-20261010` 后完整运行成功。未做干净环境交叉实验，不能把挂载盘认定为已复现普遍根因。正式结果没有存进临时缓存。
- 首次局部回放传入了非 C-contiguous 输入切片，严格向量检查拒绝；改为显式连续副本后 local_replay_r2通过。没有改变动力学/容差。
- 原生 H 护栏的故意调用属于独立负测试；生产路径计数仍为0。H独立子进程退出使用本任务自己创建的子进程，未终止其他工作线服务。
- TimeoutError是异常注入，当前记 CORE_ERROR；没有真实网络超时/PL挂死中止证明。逻辑原子提交是无状态 H/R 候选下的主机状态提交，不证明远端有状态 PL 的分布式提交。

## 可复用经验的处理

显式 old_H/old_R、候选未提交、统一 commit、身份摘要和参数展开设备隔离的程序及验收样本已可复用，保存在本线接口/代码/执行记录。新进程复现已验证 OFF0前32步全部节点；完整四条件第二次闭环重跑及其他候选尚未验证。本轮不新增通用 Skill，也不把一次 HDF5观察打包成恢复 Skill。后续扩候选/不同任务复用后再决定是否提炼项目 Skill。

本轮未执行 RTL、Vivado、量化、板编程或外部发布；未修改 MaleCNS/SNN状态文件或其他工作线检查点。源码只读 Git 检查为空；参数包前后哈希一致；精确产物由各 run manifest 与最终本线 manifest 校验。
'''
    (HERE/'EXECUTION_RECORD.md').write_text(execution,encoding='utf-8')
    (HERE/'README.md').write_text('''# FlyVis B：第二阶段独立 H / 真实闭环

**PASS_SOFTWARE_CLOSED_LOOP**（T5c67、四条件×485步、5ms、float32），最终 FPGA 方案未冻结。

- [完整报告](REPORT.md)、[机器交接](handoff.json)、[原生GPU主验收](artifacts/final_native_audit/result.json)。
- [H.step语义接口](H_STEP_INTERFACE.md)、[独立实现](h_step.py)、[统一提交](coordinator.py)、[A服务对接](gpu_adapter.py)。
- [逐条件误差](artifacts/final_native_audit/condition_error_summary.csv)、[中心T4/T5逐节点指标](artifacts/final_native_audit/central_T4T5_error_summary.csv)、[逐步误差图](artifacts/final_native_audit/step_error_comparison.png)。
- [浮点软件输入输出](artifacts/native_gpu_step_io/result.json)、[实际GPU负测试/反馈](artifacts/live_feedback_native_r1/result.json)、[新进程32步复现](artifacts/reproduce_native_prefix_r1/result.json)。
- [CPU-canonical独立基线](artifacts/final_audit/result.json)、[消融提案待评审](ABLATION_PROPOSALS.md)、[执行/复建记录](EXECUTION_RECORD.md)。

Full比较目录只是独立官方参考；生产R从本运行完整已提交状态计算。SOURCE_RAW与CURRENT_AGG各自单独验收；后者使用主机NumPy RH归约，尚未接受GPU RH/PL归约。所有关键数据/代码SHA在run_identity及manifest，历史失败输出保留。
''',encoding='utf-8')
    print(json.dumps(dict(status=summary['status'],center_T5c=center_t5c,feedback_cell_types=[hsource['cell_type'],rsource['cell_type']],
        metrics_rows=len(rows),central_rows=len(readout_rows))),flush=True)


if __name__=='__main__':main()
