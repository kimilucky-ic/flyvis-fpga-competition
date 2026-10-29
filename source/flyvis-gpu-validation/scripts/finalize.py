"""Summarize measured GPU validation results without changing the CPU baseline."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WORK = Path(__file__).resolve().parents[1]
BASE = Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1')
ART = WORK / 'artifacts'
DOC = WORK / 'docs'
DOC.mkdir(exist_ok=True)

def load(name):
    path = ART / name / 'result.json'
    return json.loads(path.read_text()) if path.exists() else None

def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

manifest = json.loads((BASE / 'manifest.json').read_text())
preserved = []
for item in manifest:
    p = BASE / item['path'].replace('\\', '/')
    preserved.append({'path': item['path'], 'matches': p.stat().st_size == item['bytes'] and hash_file(p) == item['sha256']})

names = ['hexeye_cuda_t1_r1', 'hexeye_cpu_t1_r1', 'flash_cuda_t1_r1',
         'flash_cpu_t1_r1', 'flash_cuda_t1_r2', 'moving_edge_cuda_t1_r1', 'moving_edge_full_cuda_t1_r1']
results = {name: load(name) for name in names}
gpu = results['flash_cuda_t1_r1']
cpu = results['flash_cpu_t1_r1']
hex_gpu = results['hexeye_cuda_t1_r1']
hex_cpu = results['hexeye_cpu_t1_r1']
speedup = {}
if gpu and cpu:
    speedup['flash'] = cpu['inference']['elapsed_s'] / gpu['inference']['elapsed_s']
if hex_gpu and hex_cpu:
    speedup['hexeye_three_offsets'] = hex_cpu['render_three_offsets']['elapsed_s'] / hex_gpu['render_three_offsets']['elapsed_s']
    speedup['hexeye_construction'] = hex_cpu['construction']['elapsed_s'] / hex_gpu['construction']['elapsed_s']
summary = {'evidence_level': 'original-model software simulation on local GPU',
           'cpu_baseline_manifest_verified': all(p['matches'] for p in preserved),
           'cpu_baseline_files_checked': len(preserved), 'manifest_checks': preserved,
           'measured_speedups': speedup, 'results': results,
           'not_validated': ['complete DSI', 'all moving-edge conditions vs CPU', 'second clean environment installation',
                             'subcircuit boundary activity', 'FPGA', 'cloud GPU execution']}
(ART / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

lines = ['# FlyVis RTX 5060 GPU 验证报告', '', '日期：2026-10-09。证据级别：本地原模型软件仿真。', '',
         '本次为独立的 FlyVis 视觉模型 GPU 验证，未修改模型动力学、权重或连接，未训练，也未进行 FPGA 或板级操作。', '',
         '## 环境与身份', '',
         '- GPU：NVIDIA GeForce RTX 5060 Laptop GPU，约 8 GiB 显存；Windows 驱动 596.21，WSL 能识别。',
         '- 系统：WSL2 Ubuntu 24.04.5；独立 Python 环境 `/opt/flyvis-gpu-venv`。',
         '- 数据/缓存：`/opt/flyvis-gpu-data`，与原 CPU 缓存 `/opt/flyvis-data` 分开。',
         '- GPU 依赖：PyTorch 2.7.1+cu128、torchvision 0.22.1+cu128；完整版本见 `../artifacts/requirements-gpu-lock.txt`。',
         '- CPU 基准原环境 PyTorch 2.5.1+cpu 保留；本次配对 CPU 性能测试使用新环境的 PyTorch 2.7.1，禁用 CUDA、单线程。',
         '- CUDA 时间均在计时前后同步；显存峰值为 PyTorch allocated/reserved，不是整机显存占用。',
         '- 为数值比较开启确定性算法、关闭 TF32，没有使用混合精度推理。HexEye 保持上游默认 float16 几何计算。', '']
if gpu:
    lines += [f"- 官方源码 commit：`{gpu['source_commit']}`；FlyVis {gpu['flyvis_version']}。",
              f"- 权重 SHA256：`{gpu['checkpoint_sha256']}`；加载前后张量均与官方 checkpoint 完全一致。",
              f"- 全网络：{gpu['n_neurons']:,} 神经元、{gpu['n_connections']:,} 条模型连接；导出 65 个中心细胞。", '']
lines += ['## HexEye 小规模渲染', '',
          '使用原始 `HexEye(721,25)`，与移动边缘相同的 width/height=80，angle=0、intensity=1；只测 -10、0、10 三个偏移。构造与渲染分开计时，未把首次安装算入性能。', '']
for title, r in [('GPU', hex_gpu), ('CPU 单线程', hex_cpu)]:
    if r:
        lines += [f"- {title}：构造 {r['construction']['elapsed_s']:.4f} 秒；3 张渲染 {r['render_three_offsets']['elapsed_s']:.4f} 秒。"]
        if title == 'GPU':
            lines += [f"  渲染峰值 allocated={r['render_three_offsets'].get('peak_allocated_MiB', 0):.1f} MiB，reserved={r['render_three_offsets'].get('peak_reserved_MiB', 0):.1f} MiB。"]
if hex_cpu and 'comparison_to_cuda' in hex_cpu:
    lines += [f"- CPU/GPU 刺激最大绝对误差：{hex_cpu['comparison_to_cuda']['max_abs_error']:.9g}；逐位相同：{hex_cpu['comparison_to_cuda']['bitwise_equal']}。"]
if 'hexeye_three_offsets' in speedup:
    lines += [f"- 此配对测试的渲染提速：{speedup['hexeye_three_offsets']:.2f} 倍；仅适用于测过的 3 个偏移。"]
lines += ['', '## 闪光推理与 Golden Reference', '',
          '通过原始 `compute_responses` API 重新加载官方 checkpoint，直接重放已验收的输入数组。4 组、600 帧、dt=5 ms；整网参与计算。这样把输入渲染差异与网络计算差异分开，结果缓存被绕过。', '',
          '数值验收条件在运行前写入脚本：`np.allclose(atol=1e-5,rtol=1e-5)`。数值接近通过不等于逐位相同；报告同时保存准确误差。', '']
for title, r in [('GPU 第一次', gpu), ('CPU 新环境', cpu), ('GPU 独立进程重跑', results['flash_cuda_t1_r2'])]:
    if r:
        c = r['activity_vs_cpu_golden']
        lines += [f"- {title}：{r['inference']['elapsed_s']:.4f} 秒；与原 CPU Golden 最大绝对误差 {c['max_abs_error']:.9g}，RMSE={c['rmse']:.9g}；状态 {r['status']}。"]
        if title.startswith('GPU'):
            lines += [f"  峰值 allocated={r['inference'].get('peak_allocated_MiB',0):.1f} MiB，reserved={r['inference'].get('peak_reserved_MiB',0):.1f} MiB。"]
        if 'activity_vs_first_device_run' in r:
            replay = r['activity_vs_first_device_run']
            lines += [f"  与第一次 GPU 运行逐位相同：{replay['bitwise_equal']}，最大绝对误差 {replay['max_abs_error']:.9g}。"]
if 'flash' in speedup:
    lines += [f"- 相同新环境配对 CPU/GPU 的闪光提速：{speedup['flash']:.2f} 倍。"]

edge = results['moving_edge_cuda_t1_r1']
lines += ['', '## 单条件移动边缘', '']
if edge:
    lines += [f"- 1 个方向、1 种亮度、21 个偏移；其余参数保持官方示例设置。首次刺激构建 {edge['stimulus_first_build']['elapsed_s']:.4f} 秒，缓存构建 {edge['stimulus_cached_build']['elapsed_s']:.4f} 秒。",
              f"- 原模型推理 {edge['inference']['elapsed_s']:.4f} 秒；输出 {edge['activity_shape']}，均为有限值。",
              f"- 构建峰值 allocated={edge['stimulus_first_build'].get('peak_allocated_MiB',0):.1f} MiB；推理峰值 allocated={edge['inference'].get('peak_allocated_MiB',0):.1f} MiB。",
              '- 本条件证明 GPU 渲染与推理链路可运行；没有计算完整方向选择性指标。']
else:
    lines += ['- 尚未验收；检查对应日志和 failure.json。']
full_edge = results['moving_edge_full_cuda_t1_r1']
lines += ['', '## 官方完整移动边缘配置 GPU 验证', '']
if full_edge:
    lines += [f"- 12 个方向（0..330，间隔30度）×2 种亮度×21 偏移，共504张位置图像。原始 MovingEdge API，speed=19、height=80、dt=5 ms、前后各1秒。",
              f"- 首次刺激构建 {full_edge['stimulus_first_build']['elapsed_s']:.4f} 秒；缓存构建 {full_edge['stimulus_cached_build']['elapsed_s']:.4f} 秒；整网推理 {full_edge['inference']['elapsed_s']:.4f} 秒。",
              f"- 输入 {full_edge['stimulus_shape']}，输出 {full_edge['activity_shape']}；全部有限，权重运行前后与 checkpoint 一致。",
              f"- 构建峰值 allocated={full_edge['stimulus_first_build'].get('peak_allocated_MiB',0):.1f} MiB、reserved={full_edge['stimulus_first_build'].get('peak_reserved_MiB',0):.1f} MiB；推理峰值 allocated={full_edge['inference'].get('peak_allocated_MiB',0):.1f} MiB、reserved={full_edge['inference'].get('peak_reserved_MiB',0):.1f} MiB。",
              '- 活动、输入、样本条件和时间轴已另存；这证明全部配置 GPU 渲染与推理可运行。尚未做全部条件的 CPU 对照或完整 DSI 验收。']
    folder = ART / 'moving_edge_full_cuda_t1_r1'
    edge_values = np.load(folder / 'activity_central.npy')
    edge_types = np.load(folder / 'cell_types.npy').astype(str)
    edge_times = np.load(folder / 'time.npy')
    conditions = pd.read_csv(folder / 'samples.csv',index_col='sample')
    pd.concat([pd.DataFrame({'sample': s,'frame':np.arange(len(edge_times)),'time_s':edge_times,
                             **{name:edge_values[s,:,i] for i,name in enumerate(edge_types)}})
               for s in range(len(edge_values))],ignore_index=True).to_csv(folder / 'activity_central.csv',index=False,float_format='%.9g')
    fig, axes = plt.subplots(2,4,figsize=(14,7.5),sharex=True)
    palette = plt.cm.turbo(np.linspace(0,1,12))
    for ax,name in zip(axes.flat,['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']):
        ci = list(edge_types).index(name)
        intensity = 0 if name.startswith('T5') else 1
        for sample,row in conditions[conditions.intensity == intensity].iterrows():
            ax.plot(edge_times,edge_values[sample,:,ci],label=f'{int(row.angle)} deg',lw=.85,
                    color=palette[int(row.angle)//30])
        ax.set_title(f'{name} | intensity={intensity}')
        ax.set_xlabel('Time from onset (s)')
        ax.set_ylabel('Model activity')
        ax.axvline(0,color='gray',lw=.5)
    handles,labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.95),fontsize=8,ncol=6)
    fig.suptitle('Original FlyVis | 12 directions x ON/OFF | RTX 5060 GPU | dt=5 ms')
    fig.tight_layout(rect=[0,0,1,.86])
    fig.savefig(ART / 'moving_edge_full_t4_t5.png',dpi=150)
    plt.close(fig)
    lines += ['', '![T4/T5 完整移动边缘活动](../artifacts/moving_edge_full_t4_t5.png)', '']
else:
    summary['not_validated'].append('full 24-condition moving edge')
    lines += ['- 尚未验收；不能根据单条件推断全部配置成功。']

if gpu and cpu:
    ref = np.load(BASE / 'flash/activity_central.npy')
    values = np.load(ART / 'flash_cuda_t1_r1/activity_central.npy')
    types = np.load(BASE / 'flash/cell_types.npy').astype(str)
    t = np.arange(ref.shape[1]) * .005 - 1
    fig, axes = plt.subplots(2,4,figsize=(13,6),sharex=True)
    for ax, name in zip(axes.flat, ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']):
        i = list(types).index(name)
        ax.plot(t, ref[3,:,i], label='CPU Golden', lw=1.5)
        ax.plot(t, values[3,:,i], '--',label='GPU',lw=1)
        ax.set_title(name)
        ax.set_xlabel('Time from onset (s)')
        ax.set_ylabel('Model activity')
    axes.flat[0].legend(fontsize=8)
    fig.suptitle('Original FlyVis | identical flash input | CPU / RTX 5060 GPU')
    fig.tight_layout()
    fig.savefig(ART / 'flash_cpu_gpu_comparison.png',dpi=150)
    plt.close(fig)
    lines += ['', '![CPU/GPU 闪光响应对照](../artifacts/flash_cpu_gpu_comparison.png)', '']

lines += ['## 保留与复现边界', '',
          f"- 原 CPU manifest 中 {len(preserved)} 个文件逐个校验：{'全部保持一致' if all(p['matches'] for p in preserved) else '存在不同，详见 summary.json'}。",
          '- 原 CPU 软件基准没有被 GPU 输出替换；GPU 文件全部保存在本验证目录。',
          '- 安装步骤见 `../scripts/setup_gpu.sh`，运行命令见 `../README.md`；日志在 `../logs/`，测量 JSON/NPY 在 `../artifacts/`。',
          '- 官方源代码没有修改；没有训练、裁剪、连接更改或板级操作。',
          '- 完整 DSI、全部移动条件的 CPU 对照、候选子回路边界活动及云端 GPU 尚未验证。',
          '- 本次 GPU 环境安装已完成一次；没有在第二个全新环境重复安装，因此不宣称干净环境安装流程已被重复验证。', '',
          '## 下一步', '',
          '在保持原 CPU Golden 的前提下，验收完整移动边缘方向响应与 CPU 对照，随后单独定义并导出候选子回路边界活动。', '',
          '官方依据：[PyTorch Blackwell/CUDA 12.8 支持](https://pytorch.org/blog/pytorch-2-7/)、[FlyVis 源码](https://github.com/TuragaLab/flyvis/tree/92b3845cc426dd309a1a0e1b3890156c42e14021)。', '']
(DOC / 'flyvis_gpu_validation_report.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps({'speedups': speedup, 'cpu_preserved': summary['cpu_baseline_manifest_verified'],
                  'report': str(DOC / 'flyvis_gpu_validation_report.md')}, indent=2))
