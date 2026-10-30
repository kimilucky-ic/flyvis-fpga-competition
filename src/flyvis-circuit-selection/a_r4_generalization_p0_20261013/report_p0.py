"""Saved-result P0 boundary report and scientific figures; no neural run."""
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib')
import json
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from p0_study import load,source
from video_io import sha

summary=load(HERE/'SUMMARY.json');audit=load(HERE/'FINAL_AUDIT.json');execution=load(HERE/'EXECUTION.json')
rows=load(HERE/'PREDICTIONS.json');protocol=load(HERE/'PREREGISTRATION.json')
group_names=['reference_timing','start_early','start_late','cross_early','cross_late','local_center','local_minus2','local_plus2','baseline_overlap']
group_labels=['Reference','Start 0.1s','Start 0.9s','Cross 0.75s','Cross 1.8s','Local center','Local -2','Local +2','Baseline overlap']
labels=['Full + shared','a_r4 + shared','a_r4 + own'];colors=['#333333','#0072B2','#D55E00']
fig,axs=plt.subplots(2,1,figsize=(13,8),layout='constrained',sharex=True)
x=np.arange(9)
for i,s in enumerate(summary['summaries']):
    hit=[s['groups'][g]['hit30']*100 for g in group_names]
    coverage=[s['groups'][g]['coverage']*100 for g in group_names]
    axs[0].bar(x+(i-1)*.25,hit,.23,label=labels[i],color=colors[i])
    axs[1].bar(x+(i-1)*.25,coverage,.23,label=labels[i],color=colors[i])
axs[0].axhline(75,color='gray',linestyle='--',linewidth=1,label='Group hit gate 75%')
axs[1].axhline(90,color='gray',linestyle='--',linewidth=1,label='Coverage gate 90%')
axs[0].set(ylabel='Direction hit within 30 degrees (%)',ylim=(0,110))
axs[1].set(ylabel='Accepted direction coverage (%)',ylim=(0,110))
for ax in axs:
    ax.spines[['top','right']].set_visible(False);ax.legend(fontsize=8,loc='lower left')
    ax.axvline(7.5,color='gray',linestyle=':',linewidth=1)
axs[1].set_xticks(x,group_labels,rotation=25,ha='right')
fig.suptitle('Frozen P0: 8 motion clips per group; rejected predictions count as misses\nLast group is a predeclared boundary challenge, not part of the core gate',fontsize=12)
fig.savefig(HERE/'generalization_groups.png',dpi=160);plt.close(fig)

fig,axs=plt.subplots(1,4,figsize=(11,3.3),layout='constrained')
sampler=dict(np.load(source/'models/a_r4/sampler.npz'))
radius=np.maximum.reduce([abs(sampler['u']),abs(sampler['v']),abs(sampler['u']+sampler['v'])]);roi=radius<=1
for ax,g in zip(axs,['reference_timing','local_center','local_minus2','local_plus2']):
    cap=cv2.VideoCapture(str(HERE/'videos'/f'{g}_a0_ON.mp4'));cap.set(cv2.CAP_PROP_POS_FRAMES,125)
    ok,frame=cap.read();cap.release();assert ok
    ax.imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    ax.scatter(sampler['x_pixel'],sampler['y_pixel'],s=5,c='#00A6A6')
    ax.scatter(sampler['x_pixel'][roi],sampler['y_pixel'][roi],s=20,marker='+',c='#D55E00')
    ax.set_title(g,fontsize=10);ax.set_xticks([]);ax.set_yticks([])
fig.suptitle('Actual decoded frame at 1.25s; teal: 61 inputs, orange: central 7 spatial positions',fontsize=10)
fig.savefig(HERE/'stimulus_examples.png',dpi=160);plt.close(fig)

failures=[r for r in rows if (r['kind']=='motion' and not r['direction_hit_30']) or (r['kind']=='static' and r['false_motion'])]
(HERE/'FAILURES.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),encoding='utf-8')
primary=next(s for s in summary['summaries'] if s['branch']=='a_r4/shared')
passed=[g for g in group_names if primary['groups'][g]['pass']]
failed=[g for g in group_names if not primary['groups'][g]['pass']]
input_diagnostics=[]
for name in ['Full','a_r4']:
    for group in ['start_early','start_late','cross_early','cross_late','baseline_overlap']:
        for ai in range(4):
            for polarity in ['ON','OFF']:
                ref=np.load(HERE/'runs'/name/f'reference_timing_a{ai}_{polarity}'/'input.npy')
                value=np.load(HERE/'runs'/name/f'{group}_a{ai}_{polarity}'/'input.npy')
                delta=abs(value.astype(np.float64)-ref)
                input_diagnostics.append(dict(model=name,group=group,angle_index=ai,polarity=polarity,
                    bitwise_equal=bool(np.array_equal(value,ref)),changed_values=int(np.count_nonzero(delta)),
                    changed_frames=int(np.count_nonzero(np.any(delta>0,axis=1))),
                    frames_with_delta_over_one_gray_level=int(np.count_nonzero(np.any(delta>1/255,axis=1))),
                    RMS_delta=float(np.sqrt(np.mean(delta**2))),max_delta=float(delta.max()),
                    interpretation='post hoc saved-input diagnostic only; no gate change'))
(HERE/'INPUT_PERTURBATION_DIAGNOSTICS.json').write_text(json.dumps(input_diagnostics,indent=2),encoding='utf-8')
early_equal=sum(r['bitwise_equal'] for r in input_diagnostics if r['model']=='a_r4' and r['group']=='start_early')
late_deltas=[r['RMS_delta'] for r in input_diagnostics if r['model']=='a_r4' and r['group']=='start_late']
lines=['# a_r4 固定模型：时间与空间泛化边界 · CPU P0 · 2026-10-13','',
f"**执行和身份审计PASS；a_r4共用读出的全部核心组泛化门槛{'PASS' if primary['core_generalization_pass'] else 'FAIL'}。这一判定仅覆盖下列离散新条件，不代表任意交互、自然摄像头或硬件演示就绪。**",'',
'本轮按用户“先完善功能验证，再决定能否和怎样演示”开展。原a_r4、原Full参数、两个方向读出、视觉采样、中心56神经元ROI、基线窗与分析窗全部冻结；没有训练、改窗、调阈值或挑选结果。仅改变新的受控MP4输入。GPU、GUI、RTL、板卡操作均为0。','',
'## 预注册与条件','',
f"预注册SHA `{sha(HERE/'PREREGISTRATION.json')}`。固定随机种子2026101304得到四个新方向：{', '.join(f'{a:.6f}°' for a in protocol['angles_deg'])}；每组四方向×ON/OFF=8条。方向在本轮结果出来前固定，所有组共享同一组方向以作配对比较；只有四个新方向，不能推断完整方向连续空间。",'',
'共80条新224×224、100fps、2s MP4，其中72运动、8静止。全部运动保持原亮度0.2/0.8、速度12邻距/s、边缘平滑尺度及采样。各模型复用上一批由自身bias灰屏200步所得的固定初态，只复用初态；400步电影活动全部在本轮从自己的旧态计算。','',
'- reference_timing：起始0.5s、过中心1.25s，作为本轮新方向匹配基线。',
'- start_early/start_late：起始改为0.1/0.9s，过中心仍1.25s；这会相应改变最初边缘位置，但实际过中心时间受控。',
'- cross_early/cross_late：起始仍0.5s，过中心改为0.75/1.8s。',
'- local_center/local_minus2/local_plus2：使用半径1.6邻距的固定圆形软窗口，窗口外0.5灰；窗口中心沿运动的垂直方向移0/-2/+2邻距（即0/±12px），起始和过窗口中心时刻仍0.5/1.25s。这是窗口内边缘运动，并非移动小圆球或多个物体。',
'- baseline_overlap：起始0.1s、过中心0.4s，故意侵入冻结基线。该组是事先登记的边界挑战，完整报告但不计入八个核心组门槛。',
'- 静止8条：局部窗口0/±2位置各ON/OFF，另两条全画面边缘静止；均为新方向的实际静止视频。','',
'先比较reference_timing与local_center检验形状/空间上下文变化，再比较local_center与两侧检验相同局部刺激的平移；不能把从长边缘变为局部窗口的全部损失说成位置损失。若中央局部刺激已失败，对两侧失败只能给出组合边界，不能单独归因于偏离中心。','',
'冻结门槛：每组±30°命中≥75%（至少6/8）、覆盖≥90%（8个样本下要求8/8有效输出）、有效输出MAE≤20°；全部八核心组通过且静止误报0/8才称本轮核心泛化通过。主比较仍Full/shared与a_r4/shared；a_r4/own是固定次级，禁止根据结果切换主读出。弃权计未命中，另报角度误差、四分类和180°弃权惩罚误差。','',
'## 全部实际结果','']
for s in summary['summaries']:
    lines += [f"### {s['branch']}",'',f"核心泛化门槛：{'PASS' if s['core_generalization_pass'] else 'FAIL'}；静止误报{s['static_false_motion']}。",'']
    for g in group_names:
        m=s['groups'][g];mae='无有效输出' if m['accepted_MAE'] is None else f"{m['accepted_MAE']:.3f}°"
        lines.append(f"- {g}：±30°命中{round(m['hit30']*8)}/8；四方向{round(m['four_way']*8)}/8；覆盖{round(m['coverage']*8)}/8；有效MAE {mae}；弃权180°惩罚MAE {m['penalized_MAE']:.3f}°；组门槛{'PASS' if m['pass'] else 'FAIL'}。")
    lines.append('')
lines+=['![全部组命中与覆盖](generalization_groups.png)','','![实际视频与输入位置](stimulus_examples.png)','',
'## 如何解释演示适用范围','',
f"a_r4/shared本批通过组：{', '.join(passed) or '无'}；未通过组：{', '.join(failed) or '无'}。完整科学结果保留于SUMMARY.json、PREDICTIONS.csv、FAILURES.json以及逐组配对PAIRED_SPATIAL_EFFECTS.json。",'',
f"**起始时间实验的有效扰动限制**：事后只读检查实际输入发现，start_early在a_r4的{early_equal}/8条61点输入与reference_timing逐位相同。边缘提前运动时仍在小视野之外，进入视野后的运动轨迹又相同，因此这一组不能作为a_r4对可见起始时间变化鲁棒的独立证据。start_late输入相对基线RMS差范围{min(late_deltas):.8f}–{max(late_deltas):.8f}，扰动大小也必须结合输入解释。cross_early/cross_late才是真正改变中心可见通过时间的主要证据。详见INPUT_PERTURBATION_DIAGNOSTICS.json；该诊断不改原计分与失败记录。",'',
'**局部刺激的实际失败**：共用读出下，中央窗口Full/a_r4均只命中5/8，向一侧平移均1/8、另一侧均2/8。a_r4专用读出也未通过局部三组门槛。因此，本批不支持“评委随意移动小目标仍可靠判断”的演示承诺。大量错例仍输出方向而非弃权，向量模长门槛不是可靠的域外错误检测器。中央局部窗口已失败，说明形状/上下文变化本身有影响；从中央窗口到相同窗口两侧的进一步下降才是位置敏感证据。', '',
'通过一个离散时刻或位置，不证明两点之间所有值或其他方向/速度都可靠。当前入口仍在2s片段结束后输出一次结果；基线状态[60:100]与响应[100:400]保持固定，没有自动检测运动开始，也没有实时连续分窗机制。基线侵入导致的错误不能靠在本批重新选择窗口来掩盖。','',
'如局部窗口或时间扰动失败，应将当前能力限定为已验证的标准化输入，或另立新读出研究并使用全新测试集；不把失败改为“演示模式”后继续引用本次泛化PASS。原网络在同组也失败时，说明问题至少涉及当前任务/ROI/读出组合，不能仅归因于裁剪；a_r4额外下降才是其相对原Full的任务差异证据。','',
'本轮暂缓对比度、噪声、进一步慢速扫描及连续视频分窗。上轮慢速弱点仍然有效；本批所有运动都是12邻距/s，不能据本轮否定慢速失败。没有CNN对照或自然场景准确率声明，也没有因结果而调整神经网络。','',
'## 真实计算与可复现数据','',
f"160条实际CPU模型运行×400步=64000个新神经步；共用原始保存的模型各自初态，未重新做灰屏。顺序CPU执行{execution['wall_s']:.3f}s。a_r4保存每条全部3865节点状态；Full保存中心56轨迹、最终完整状态、输入及每一步完整状态摘要链。Full不是预录状态回放。",'',
'固定预注册/source/readout SHA、所有视频SHA、本地输入与Full输入子集、80条a_r4全部状态及64000提交链/时序均完成保存数据审计，无神经重新计算。所有失败记录保留。原视频生成器的默认条件和新生成器默认条件解码后逐位一致；局部平移正交性、实际像素变化与静止不动等预检通过。','',
'复现入口：在新的同级目录复制p0_study.py，保留上一批a_r4_video_direction_20261013只读；依次执行`python -B p0_study.py prepare`、`run`、`analyze`。审计audit_p0.py和报告report_p0.py只读取结果。当前目录已封存，不在原输出目录重跑。','',
'身份：[PREREGISTRATION.json](PREREGISTRATION.json)、[FREEZE_RECEIPT.json](FREEZE_RECEIPT.json)、[CASES.json](CASES.json)、[VIDEO_MANIFEST.json](VIDEO_MANIFEST.json)、[EXECUTION.json](EXECUTION.json)、[FINAL_AUDIT.json](FINAL_AUDIT.json)、[DELIVERY_MANIFEST.json](DELIVERY_MANIFEST.json)。科学计算通过与功能门槛通过严格分开；本批完成后停止，不自动训练、增加刺激或移植硬件。']
(HERE/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
manifest=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file() and 'runtime' not in p.relative_to(HERE).parts and '__pycache__' not in p.parts and p.name!='DELIVERY_MANIFEST.json':
        manifest.append(dict(path=str(p.relative_to(HERE)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)))
(HERE/'DELIVERY_MANIFEST.json').write_text(json.dumps(dict(files=manifest,file_count=len(manifest),bytes=sum(r['bytes'] for r in manifest)),indent=2),encoding='utf-8')
print(json.dumps(dict(status='P0_REPORT_SEALED',files=len(manifest),bytes=sum(r['bytes'] for r in manifest),manifest_sha=sha(HERE/'DELIVERY_MANIFEST.json'))))
