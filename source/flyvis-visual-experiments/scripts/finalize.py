"""Freeze accepted continuation data and build an evidence report, no installation."""
import hashlib,json,shutil,subprocess
from pathlib import Path
import numpy as np
WORK=Path(__file__).resolve().parents[1];ART=WORK/'artifacts';DOC=WORK/'docs';DOC.mkdir(exist_ok=True)
BASE=Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly')
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def result(name):return read(ART/name/'result.json')
cpu=result('cross_cpu_cpu_r1');gpu=result('cross_gpu_cuda_r1')
mini=result('minimal_cuda_r1');flash=result('flash_cuda_r1')
bar=result('bar_cuda_r1');bar_cpu=result('bar_replay_cpu_r1')
dec=result('decoder_cuda_r3');dec_cpu=result('decoder_cpu_r2');boundary=result('boundary_cuda_r1')
dsi=read(ART/'analysis/direction_analysis.json');audit=read(ART/'analysis/boundary_euler_audit.json')
render=read(ART/'rendering_cache_audit.json')
for info in [mini,flash,bar,bar_cpu,dec,dec_cpu,boundary,dsi,audit]:assert info['status']=='PASS',info
assert gpu['activity_vs_new_cpu']['allclose'] and gpu['activity_vs_prior_gpu']['bitwise_equal']
assert np.array_equal(np.load(ART/'cross_cpu_cpu_r1/stimulus.npy'),np.load(ART/'cross_gpu_cuda_r1/stimulus.npy'))
assert dec['flow_vs_cpu']['allclose'] and dec['flow_vs_first_eval_gpu']['bitwise_equal']
checks=[]
sets=[(BASE/'artifacts/golden_reference_v1','manifest.json'),(BASE/'artifacts/moving_edge_minimal_cpu_v1','manifest.json'),(WORK.parent/'flyvis-gpu-validation','artifacts/validation_manifest.json')]
for root,manifest in sets:
    entries=read(root/manifest);bad=[]
    for entry in entries:
        path=root/entry['path'].replace('\\','/')
        if sha(path)!=entry['sha256']:bad.append(entry['path'])
    checks.append(dict(root=str(root),checked_files=len(entries),mismatches=bad,passed=not bad))
assert all(c['passed'] for c in checks)
dump(ART/'protected_references_after.json',checks)
source_changes=subprocess.check_output(['git','-C',str(BASE/'upstream/flyvis'),'status','--porcelain','--untracked-files=no'],text=True).strip()
assert not source_changes,source_changes
dump(ART/'fixed_input_acceptance.json',dict(status='PASS',atol=1e-5,rtol=1e-5,
    same_actual_float32_input=True,full24_activity_cpu_gpu=gpu['activity_vs_new_cpu'],
    full24_independent_gpu_replay=gpu['activity_vs_prior_gpu'],
    minimal_cpu_input_replay=mini['activity_vs_cpu_reference'],flash_cpu_input_replay=flash['activity_vs_cpu_reference'],
    independently_rendered_input_acceptance='FAIL',rendering_evidence='rendering_cache_audit.json',
    interpretation='Same-input neural inference accepted. Independent CPU/GPU render equivalence failed. Original failed composite records retained.'))
gold=ART/'golden_reference_v2';gold.mkdir(exist_ok=True)
for name in ['stimulus.npy','cell_types.npy','samples.csv','time.npy']:
    shutil.copy2(ART/'cross_gpu_cuda_r1'/name,gold/name)
shutil.copy2(ART/'cross_cpu_cpu_r1/activity_central.npy',gold/'activity_central_cpu.npy')
shutil.copy2(ART/'cross_gpu_cuda_r1/activity_central.npy',gold/'activity_central_gpu.npy')
for name in ['activity_T4_T5.npy','activity_T4_T5.csv','direction_metrics_all_65.csv','direction_metrics_T4_T5.csv']:
    shutil.copy2(ART/'analysis'/name,gold/name)
shutil.copy2(ART/'fixed_input_acceptance.json',gold/'acceptance.json')
dump(gold/'metadata.json',dict(evidence_level='original full-network software simulation; fixed stimulus CPU/GPU replay',
    commit=gpu['source_commit'],checkpoint_sha256=gpu['checkpoint_sha256'],model='flow/0000/000',
    neurons=45669,connections=1513231,dt_s=.005,stimulus_shape=[24,485,1,721],activity_shape=[24,485,65],
    stimulus_dtype='float32; canonical cast of previously GPU-rendered original official MovingEdge input',
    stimulus_source='../cross_gpu_cuda_r1/stimulus.npy',
    original_uncast_stimulus='../../../flyvis-gpu-validation/artifacts/moving_edge_full_cuda_t1_r1/stimulus.npy',
    initialization='1 s original grey 0.5 steady state, then all 485 input frames including 1 s dataset preperiod',
    time_semantics='time=frame*dt-1; each saved activity is AFTER the corresponding Euler update',
    activity_units='continuous nodes.activity model units; not spikes, Hz or calibrated mV',
    axes={'stimulus':['sample','frame','channel','hex_pixel'],'activity':['sample','frame','central_cell_type']},
    parameter_source=str(BASE/'artifacts/golden_reference_v1/checkpoint_network_parameters.npz'),
    environment={'cpu_python':'/opt/flyvis-venv/bin/python','gpu_python':'/opt/flyvis-gpu-venv/bin/python','cpu_torch':cpu['torch'],'gpu_torch':gpu['torch']},
    limitations=['One model and one MovingEdge speed; independently generated CPU/GPU pixels are not equivalent within declared tolerance']))
manifest=[dict(path=str(f.relative_to(gold)),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(gold.rglob('*')) if f.is_file() and f.name!='manifest.json']
dump(gold/'manifest.json',manifest)
features=[
    dict(function='Flash fixed-input GPU validation',status='PASS',data='artifacts/flash_cuda_r1',log='logs/flash_cuda_r1.log'),
    dict(function='ON/OFF MovingEdge 12 directions, speed=19',status='PASS',data='artifacts/golden_reference_v2',log='logs/cross_gpu.log'),
    dict(function='Official DSI / preferred direction',status='PASS',data='artifacts/analysis/direction_metrics_T4_T5.csv',log='logs/analysis.log'),
    dict(function='Independent CPU/GPU rendered input identity',status='FAIL',data='artifacts/rendering_cache_audit.json',log='logs/rendering_audit.log'),
    dict(function='MovingBar ten finite conditions and CPU replay',status='PASS',data='artifacts/bar_cuda_r1',log='logs/bar_replay_cpu_r1.log'),
    dict(function='Official pretrained flow decoder synthetic-input inference',status='PASS',data='artifacts/decoder_cuda_r3',log='logs/decoder_cuda_r3.log'),
    dict(function='Optic flow accuracy on real labelled naturalistic data',status='NOT_RUN',data=None,log=None),
    dict(function='Visual assets / prerecorded animation',status='PASS',data='artifacts/analysis',log='logs/analysis.log'),
    dict(function='T4c/T5c internal and boundary data + software Euler audit',status='PASS',data='artifacts/boundary_cuda_r1',log='logs/boundary_cuda_r1.log'),
    dict(function='Teammate distribution / independent install / FPGA',status='NOT_RUN',data=None,log=None)]
dump(ART/'functional_acceptance.json',dict(features=features,optic_flow_overall='PARTIAL',evidence_level='software simulation only',packaging_lane_untouched=True))
bar_build=sum(c['stimulus_build']['elapsed_s'] for c in bar['conditions']);bar_infer=sum(c['inference']['elapsed_s'] for c in bar['conditions'])
bar_replay=sum(c['inference']['elapsed_s'] for c in bar_cpu['conditions'])
max_bar_error=max(c['activity_vs_gpu']['max_abs_error'] for c in bar_cpu['conditions'])
max_boundary_error=max(c['recurrence_max_abs_error'] for c in audit['checks'])
durations=dict(full_edge_cpu_s=cpu['inference']['elapsed_s'],full_edge_gpu_s=gpu['inference']['elapsed_s'],bar_build_sum_s=bar_build,
               bar_inference_sum_s=bar_infer,bar_cpu_replay_sum_s=bar_replay,decoder_gpu_network_s=dec['inference']['elapsed_s'],
               decoder_gpu_readout_s=dec['decode']['elapsed_s'],decoder_cpu_network_s=dec_cpu['inference']['elapsed_s'],decoder_cpu_readout_s=dec_cpu['decode']['elapsed_s'])
dump(ART/'summary.json',dict(features=features,timings=durations,full_edge_comparison=gpu['activity_vs_new_cpu'],
    decoder_comparison=dec['flow_vs_cpu'],bar_max_abs_error=max_bar_error,boundary_max_abs_error=max_boundary_error,
    source_tracked_changes=source_changes,protected_reference_checks=checks))
lines=['# FlyVis 原始视觉模型：追加实验报告','',
       '日期：2026-10-09。全部证据为本机原始模型的软件仿真。沿用既有 CPU/GPU 环境；本任务没有重新安装环境，也没有改动队友运行包目录。','',
       '## 环境、模型和验收口径','',
       f'- FlyVis 1.2.0，commit `{gpu["source_commit"]}`，模型 `flow/0000/000`，checkpoint SHA256 `{gpu["checkpoint_sha256"]}`。',
       '- 全部 45,669 个神经元、1,513,231 条连接都参与仿真。原 PPNeuronIGRSynapses、连续状态和 Euler 更新保留；没有训练、剪枝、LIF 替换或硬件设计。',
       '- WSL FlyVisCPU / Ubuntu 24.04 / Python 3.12.3；CPU torch 2.5.1+cpu，GPU torch 2.7.1+cu128，RTX 5060 Laptop。现有解释器 `/opt/flyvis-venv/bin/python` 与 `/opt/flyvis-gpu-venv/bin/python`。',
       '- 独立实验缓存 `/opt/flyvis-visual-experiments-data`，模型副本来自原官方 checkpoint；原 CPU/GPU 缓存只读。所有重型渲染和仿真串行运行。',
       '- 固定随机种子，单 CPU 线程，确定性算法，关闭 TF32。数值阈值在运行前确定：`atol=rtol=1e-5`，没有扩大阈值。相对误差同时记录 L2 和近零分母带 1e-12 下限的逐点值；验收用绝对+相对混合容差。',
       '- 所有合格网络运行前后参数均与原 checkpoint 完全一致；合格解码器的参数和 BatchNorm 缓冲量也逐项一致。',
       '', '## 功能结果','']
for feature in features:lines.append(f'- **{feature["status"]}** — {feature["function"]}'+(f'：[数据]({"../"+feature["data"]})；[日志]({"../"+feature["log"]})。' if feature['data'] and feature['log'] else '。'))
lines += ['', '光流整体为 PARTIAL：原预训练解码器的合成输入推理通过，Sintel/真实视频精度尚未测量。打包、独立安装验收和 FPGA 属于其他范围。','',
          '## Golden Reference v2 与数值对照','',
          '- [数据目录](../artifacts/golden_reference_v2/) 包含固定刺激、CPU/GPU 各自活动、65 类顺序、条件、时间、T4/T5 CSV/NPY、官方方向指标、metadata、acceptance 和 SHA256 manifest。旧版 Golden Reference 保留。',
          '- MovingEdge 为 12 方向 × ON/OFF，速度 19；输入 `(24,485,1,721)`，中心活动 `(24,485,65)`，dt=0.005 秒，时间 -1.000 到 1.420 秒。先用灰度 0.5 建立 1 秒初态，再运行包含 1 秒数据集前期的输入。活动为对应帧 Euler 更新后的值，单位为模型连续活动。',
          f'- 固定同一份 float32 输入的 CPU/GPU 活动最大绝对误差 {gpu["activity_vs_new_cpu"]["max_abs_error"]:.9g}，RMSE {gpu["activity_vs_new_cpu"]["rmse"]:.9g}；独立 GPU 复算与此前 GPU 活动逐位相同。',
          f'- 直接读取已验收 CPU 两方向输入后，GPU 活动最大误差 {mini["activity_vs_cpu_reference"]["max_abs_error"]:.9g}；Flash 为 {flash["activity_vs_cpu_reference"]["max_abs_error"]:.9g}。',
          '- 24 条件使用此前官方 GPU 渲染的输入，明确保留这一来源；输入 float64 保存值规范转换为 float32 后，CPU/GPU 使用完全相同的数组。它不证明独立 CPU/GPU 渲染等价。','',
          '## 官方方向分析与 MovingBar','',
          '- 直接调用 `flyvis.analysis.moving_bar_responses.peak_responses`、`direction_selectivity_index`、`preferred_direction`；全部 12 个方向齐备。峰值为官方时间窗口内整流原始活动的最大值，没有用双方向差冒充 DSI，也没有自行扣基线后替代官方度量。',
          '- 官方 DSI 分母为两种亮度中更大的角度峰值总和。只验证单模型、单速度的指标；弱响应的偏好角须结合 DSI/峰值解释，不能当作真实动物或模型集群的结论。',
          f'- 65 类 DSI 的 CPU/GPU 最大差 {dsi["dsi_max_abs_cpu_gpu_error"]:.9g}；[T4/T5 指标](../artifacts/analysis/direction_metrics_T4_T5.csv)，[全部 65 类](../artifacts/analysis/direction_metrics_all_65.csv)，[曲线趋势对照](../artifacts/analysis/cpu_gpu_target_trends.csv)。',
          '- MovingBar 十个明确条件：0/180 度和强 ON/OFF 的四组；0 度速度 4.8 的 ON/OFF 两组；宽度 4 的 ON/OFF 两组；亮度 0.25/0.75 两组。其余参数保持官方；速度 19 为 485 帧，4.8 为 739 帧。没有展开完整参数笛卡尔积。',
          f'- 十组保存输入均用原 CPU 环境复算，最大活动误差 {max_bar_error:.9g}；每组的原始输入、时间、65 类活动、配置和计时单独保存。','',
          '![角度调谐](../artifacts/analysis/angular_tuning.png)','',
          '![ON/OFF 响应](../artifacts/analysis/on_off_opposed_traces.png)','',
          '![MovingBar 速度响应](../artifacts/analysis/moving_bar_speed_traces.png)','',
          '## 原始光流解码器与纠错记录','',
          '- 官方 checkpoint 包含 flow 解码器 DecoderGAVP：34 类输出细胞空间活动 → 六边形卷积 34→8→2，kernel=5。输入为全网络活动，不是只有中心 T4/T5。四组原始 ON/OFF 相反方向输入得到 `(4,485,2,721)`。',
          f'- 正确 eval 模式 CPU/GPU 光流最大误差 {dec["flow_vs_cpu"]["max_abs_error"]:.9g}，RMSE {dec["flow_vs_cpu"]["rmse"]:.9g}；第二个独立 GPU eval 进程逐位复现。',
          '- 首次脚本只使用官方 simulation()；本版本该帮助函数只修改父模块 training，未递归关闭子模块 Dropout/BatchNorm，导致运行中 BatchNorm 缓冲量变化。首次 GPU/CPU r1 均拒绝验收。曾怀疑卷积掩码，审计证实本 checkpoint 的掩码已经满足、投影改变量为 0，故该猜测被否定。',
          '- 外部实验脚本显式执行 decoder.eval()，逐个子模块检查 training=False，并验证全部 state_dict 不变。GPU r2 是首次正确 eval 输出，但旧脚本仍把失败的训练模式输出作为对照，因此该复合记录也保留为 FAIL；GPU r3 与 CPU r2 是正式通过的比较。原始源码与 checkpoint 文件没有修改。',
          '- 仅为合成边缘的解码功能验收。未下载大型 Sintel 数据、未报告 EPE、未标定物理速度；component_0/1 保留原模型输出单位。矢量图每面板自动缩放，仅用于观察。','',
          '![实际预训练解码器预测](../artifacts/analysis/decoded_flow_vectors.png)','',
          '## 候选子回路数据接口','',
          '- 所有轨迹都从完整原网络提取。四个条件是 OFF/ON × 0/180 度；没有裁剪网络再仿真。内部节点表含原 node_index、type、u/v、bias、time_const；内部、跨界入、跨界出连接表保留原 edge_index 和 sign/syn_count/syn_strength/weight。',
          '- 每个候选/条件导出 initial_internal、internal_activity_after、boundary_incoming_activity_before、boundary_outgoing_target_activity_after、external_node_input、stimulus 和 time。每个入界源节点逐帧值都保留。',
          '- Euler：`a_after=a_before+dt/max(tau,dt)*(-a_before+bias+sum(weight*relu(a_source_before))+external_input)`。边界输入使用同一步更新之前的状态；连续模型没有独立突触状态。',
          f'- 原方程以记录的外部边界进行 float32 软件复核，八组候选/条件都通过同一容差，累计最大误差 {max_boundary_error:.9g}；[审计](../artifacts/analysis/boundary_euler_audit.json)。这验证数据接口的时间语义，不能证明无需外部输入的自治子回路或 FPGA 等价。','']
for c in boundary['candidates']:lines.append(f'- {c["target"]}：{c["neurons"]} 个内部节点，{c["edges"]["internal"]} 条内部边，{c["edges"]["incoming"]} 条跨界入边/{c["incoming_sources"]} 个外部源，{c["edges"]["outgoing"]} 条跨界出边。边界规模仍大，当前不推荐把它视为可直接独立替换的回路。')
lines += ['', '## 计时与资源','']
for key,value in durations.items():lines.append(f'- `{key}`：{value:.6f} 秒。')
lines += [f'- 完整边缘同输入复算：GPU allocated peak {gpu["inference"]["peak_allocated_MiB"]:.2f} MiB，reserved {gpu["inference"]["peak_reserved_MiB"]:.2f} MiB。',
          f'- 本次 MovingBar 冷渲染 allocated 最大 {max(c["stimulus_build"]["peak_allocated_MiB"] for c in bar["conditions"]):.2f} MiB，reserved 最大 {max(c["stimulus_build"]["peak_reserved_MiB"] for c in bar["conditions"]):.2f} MiB。这些是 PyTorch allocator 计数，不是整机物理显存用量；reserved 在该 WSL/WDDM 运行中高于板载容量，不能当作无需共享内存的保证。后续脚本在每次新渲染前清空未使用 allocator cache；本轮 cold run 的上述历史计数保留。',
          f'- 合格解码器 GPU 网络 allocated {dec["inference"]["peak_allocated_MiB"]:.2f} MiB；readout allocated {dec["decode"]["peak_allocated_MiB"]:.2f} MiB；GPU 进程主机 max RSS {dec["process_host_max_rss_MiB"]:.2f} MiB，CPU 解码进程 {dec_cpu["process_host_max_rss_MiB"]:.2f} MiB。max RSS 是进程运行至该点的高水位，不是每相位独立内存峰值。',
          '- 早期 cross/Flash/MovingBar 主机 RSS 没有采集，不回填猜测值。所有 GPU 数值均通过 CUDA synchronize 包围计时，不包含环境安装；构建、网络、解码分别记时，启动/导出/等待不计入这些阶段。','',
          '## 保留和未解决项','',
          '- 按原 manifest 逐一核验 CPU Golden 36 文件、最小 MovingEdge 33 文件、此前 GPU 包 49 文件，全部哈希不变；[前](../artifacts/protected_references_before.json)/[后](../artifacts/protected_references_after.json)。这些数量是 manifest 条目数，不含 manifest 自身或包外文件。上游 tracked source git status 为空。',
          '- 独立 CPU/GPU 21 偏移渲染缓存配置匹配，但像素输出最大差约 8.82e-4。失败已在 resampling 前的 HDF5 缓存复现。原 HexEye 使用 float16 几何/掩码是源码观察，尚未隔离为数值差异的确定原因。此前三位置小基准的位相等结论不能扩大到全部 MovingEdge 位置。',
          '- 最稳妥的已验证路径是保存并冻结同一份官方刺激，CPU/GPU 都读取这份输入；独立渲染等价仍为 FAIL。',
          '- 下一项具体实验：隔离 CPU/GPU HexEye 几何掩码差异，同时在已冻结刺激路径上扩展多速度方向分析；之后再对官方标注数据评估光流误差。','',
          '## 运行命令与交接','',
          '在 PowerShell 运行（现有 WSL 环境，重复编号选择未使用的新编号）：','',
          '```powershell',
          'wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh minimal cuda 2',
          'wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh cross_gpu cuda 2',
          'wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh bar cuda 2',
          'wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-visual-experiments/scripts/run_phase.sh decoder cuda 4',
          '```','',
          '已有 result.json 的目录会拒绝覆盖；MovingBar 中断时保留已完成条件并续跑尚未完成条件。新实验脚本位于本目录 scripts，实际命令在每个 result.json 和日志中。','',
          '展示资产包括帧对应的灰度输入、活动热力图、ON/OFF/角度/速度曲线、真实解码矢量图以及 [GIF 回放](../artifacts/analysis/stimulus_activity_playback.gif)。GIF 标注 prerecorded software simulation，按 8 个 5ms 帧采样、40ms 显示间隔回放，不代表实时系统或 FPGA 执行。',
          '- [交接清单](../handoff.json) 可由打包任务读取；本任务不修改其包、安装器、CPU 环境或已验收文件。',
          '- 解码器评估模式失败已在独立 CPU/GPU 进程恢复并复算；可复用经验记录于项目单独 Skill，未改此前供打包读取的 GPU Skill。新环境安装、其他 GPU、Sintel 精度与板上复用仍未验证。','']
(DOC/'flyvis_experiments_report.md').write_text('\n'.join(lines),encoding='utf-8')
dump(WORK/'handoff.json',dict(scope='experiment artifacts only; packaging handled separately',report='docs/flyvis_experiments_report.md',
    accepted_golden='artifacts/golden_reference_v2',display_assets='artifacts/analysis',decoder='artifacts/decoder_cuda_r3',
    boundary='artifacts/boundary_cuda_r1',features=features,
    exclude_from_display=['artifacts/decoder_cuda_r1','artifacts/decoder_cpu_r1','artifacts/decoder_cuda_r2'],
    evidence_label='Original FlyVis pretrained full-network SOFTWARE SIMULATION; prerecorded playback where shown'))
print('FINALIZED',json.dumps({'timings':durations,'bar_max_abs_error':max_bar_error,'boundary_max_abs_error':max_boundary_error,'protected':checks}),flush=True)
