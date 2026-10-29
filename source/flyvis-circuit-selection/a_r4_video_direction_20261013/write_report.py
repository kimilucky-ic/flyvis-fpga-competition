"""Render scientific figures and a bounded report from sealed CPU results."""
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'runtime/matplotlib')
import csv
import json
import zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from video_io import sha

load=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
summary=load(HERE/'SUMMARY.json');rows=load(HERE/'PREDICTIONS.json');audit=load(HERE/'FINAL_AUDIT.json')
labels=['Full + shared readout','a_r4 + shared readout','a_r4 + own readout']
colors=['#333333','#0072B2','#D55E00']
fig,axs=plt.subplots(1,2,figsize=(12,4.7),layout='constrained')
xs=np.arange(3)
for i,s in enumerate(summary['summaries']):
    hit=[s['by_speed'][str(v)]['direction_hit_30']*100 for v in [6,12,24]]
    err=[s['by_speed'][str(v)]['accepted_MAE_deg'] for v in [6,12,24]]
    bars=axs[0].bar(xs+(i-1)*.25,hit,width=.23,color=colors[i],label=labels[i])
    axs[0].bar_label(bars,fmt='%.1f',fontsize=8,padding=2)
    axs[1].plot(xs,err,'o-',color=colors[i],label=labels[i])
axs[0].set(ylabel='Direction hit within 30 degrees (%)',ylim=(0,112),title='Heldout motion: 16 clips per speed')
axs[0].axhline(75,color='gray',linestyle='--',linewidth=1)
axs[1].set(ylabel='Accepted circular angle MAE (degrees)',title='Coverage: Full 47/48; a_r4 48/48')
for ax in axs:
    ax.set_xticks(xs,['6 (half)','12 (design speed)','24 (double)'])
    ax.set_xlabel('Speed (retinal neighbour spacings / second)')
    ax.spines[['top','right']].set_visible(False)
axs[1].legend(fontsize=8,loc='upper right')
fig.suptitle('New MP4 heldout benchmark: 8 unseen angles x ON/OFF x 3 speeds',fontsize=12)
fig.savefig(HERE/'direction_benchmark.png',dpi=160);plt.close(fig)

fig,axs=plt.subplots(1,3,figsize=(16,5.7),layout='constrained')
angles=np.arange(22.5,360,45);rowlabels=[f'{p} v{v}' for v in [6,12,24] for p in ['ON','OFF']]
for ax,s,label in zip(axs,summary['summaries'],labels):
    data=np.zeros((6,8));reject=np.zeros((6,8),bool)
    for ri,(v,p) in enumerate([(v,p) for v in [6,12,24] for p in ['ON','OFF']]):
        for ci,a in enumerate(angles):
            r=next(r for r in rows if r['branch']==s['branch'] and r['split']=='heldout' and r['kind']=='motion' and r['speed_hex_s']==v and r['polarity']==p and r['truth_angle_deg']==a)
            data[ri,ci]=r['penalized_error_deg'];reject[ri,ci]=not r['accepted']
    im=ax.imshow(data,vmin=0,vmax=60,cmap='magma_r',aspect='auto')
    for ri in range(6):
        for ci in range(8):
            ax.text(ci,ri,'REJ' if reject[ri,ci] else f'{data[ri,ci]:.0f}',ha='center',va='center',fontsize=8,color='white' if data[ri,ci]>28 else 'black')
    ax.set_xticks(np.arange(8),[f'{a:g}' for a in angles],rotation=60)
    ax.set_yticks(np.arange(6),rowlabels);ax.set_xlabel('Ground-truth motion direction (degrees)');ax.set_title(label,fontsize=11)
fig.colorbar(im,ax=axs,label='Circular error (degrees); color clipped at 60; REJ penalty=180')
fig.suptitle('All 48 heldout motions per readout; no failed case removed',fontsize=13)
fig.savefig(HERE/'all_direction_errors.png',dpi=160);plt.close(fig)

failures=[r for r in rows if r['split']=='heldout' and ((r['kind']=='motion' and not r['direction_hit_30']) or (r['kind']!='motion' and r['false_motion']))]
(HERE/'FAILURE_CASES.json').write_text(json.dumps(failures,indent=2),encoding='utf-8')
scientific=[]
for split in ['DESIGN','HELDOUT']:scientific+=load(HERE/f'{split}_EXECUTION.json')['results']
timings={n:dict(case_wall_sum_s=sum(r['wall_s'] for r in scientific if r['model']==n),
    median_clip_s=float(np.median([r['wall_s'] for r in scientific if r['model']==n])),
    max_abs_state=max(r['max_abs_state'] for r in scientific if r['model']==n)) for n in ['Full','a_r4']}
(HERE/'TIMINGS.json').write_text(json.dumps(dict(scope='CPU decode + own neural rollout + SHA journals + files; excludes initial adaptation and process startup; not kernel-only or live-camera timing',models=timings,stage_times=audit['times']),indent=2),encoding='utf-8')

lines=['# a_r4 独立视频输入与局部运动方向读出 · CPU首批报告 · 2026-10-13','',
'**结论：已实现真正的MP4解码→61点视觉输入→3865节点自身递推→单片段方向输出。冻结留出测试通过本批工程门槛。主比较使用同一个Full校准读出：a_r4的±30°命中44/48（91.67%），原完整网络45/48（93.75%）；四方向分类两者均43/48（89.58%）。这不是官方光流或任意自然视频验收。**','',
'## 实验边界与输入','',
'本批76个新生成并实际编码/解码的224×224、100fps、2s MP4。原65类型连续神经方程、原展开float32权重/bias/tau及5ms Euler均保留；Full45669/1513231，a_r4 3865/110794。原模型计算采用上一轮已对官方GPU全状态校准的独立CPU更新器（最大误差1.4305115e-6）；本轮未重新调用官方Torch更新器，也未使用DecoderGAVP。Full是原完整神经网络加新增局部读出，不能把其本轮分数当作原官方decoder光流精度。','',
'每个模型从自身bias做200步0.5灰屏适应，所得各自a0固定复用于全部视频；a_r4初态不从Full裁切。每视频再计算400步，旧态完全来自本次自己的提交。CPU代码没有Full未来状态或被删神经元补算入口。相同MP4独立解码，a_r4的61点逐位等于Full721点的固定原索引子集。新3×3采样器沿原hex坐标方向、邻距6图像像素，不冒充此前官方HexEye刺激逐位等价。','',
'视频前0.5s静止，运动从0.5s开始，边缘在1.25s通过中心；亮度0.2/0.8，边缘平滑尺度1px。方向0°向右、90°向上、180°向左、270°向下。6/12/24视网膜邻距每秒对应36/72/144图像像素每秒；没有生物视角角度/秒标定。每个100fps帧因果保持两个5ms步，不用未来帧插值。','',
'设计集20条：0/45/.../315°×ON/OFF、速度12，共16运动，加4静止校准。留出56条：22.5/67.5/.../337.5°×ON/OFF×速度6/12/24，共48运动；6静止（含新边缘方向/位置/灰屏）和2全场亮度阶跃。留出方向全部未参与本轮读出设计；两个新速度未用于拟合，属于有限网格内插/速度迁移，未随机抽样自然视频。','',
'## 读出与预注册','',
'固定中心r1七位置×八类T4/T5=56节点。状态索引[60:100]平均作为每神经元基线；[100:400]相对基线的正响应峰值，再按类型平均七位置得到八维特征。标准化后以固定ridge λ=0.1拟合cosθ/sinθ；只用16设计运动，4设计静止决定运动门槛。神经权重没有训练。方向预测函数只接受八维活动特征和已冻结参数，不读取刺激标签。','',
'主比较Full/shared与a_r4/shared共用Full设计集校准的同一组权重/标准化/门槛。另在预注册中固定a_r4/own：同样算法、同样16+4设计视频，校准a_r4自己的读出；始终作为独立次级结果报告，没有从留出结果中择优替代主结论。两个读出均在首个留出神经运行之前封存。','',
'拒绝条件：特征RMS不足max(0.001,1.25×设计静止最大RMS,0.1×设计运动最小RMS)，或预测二维向量模长<0.25。NO_CONFIDENT_MOTION只表示弃权，不证明场景静止；向量模长不是概率。角度误差使用圆周最短差。主命中为误差≤30°，弃权计错；四方向为最接近的右/上/左/下，弃权计错。另报有效输出覆盖、有效输出MAE/中位/P95及弃权按180°计的全样本MAE。','',
'提前固定门槛：总体±30°命中≥80%、各速度及各极性≥75%、覆盖≥90%、有效角度MAE≤20°、6静止误报0。两阶跃是附加控制。门槛仅本批小规模工程标准；结果后未修改或调参。设计集中45°边界本身位于四分类分界，其训练四分类分数保留在JSON但不作为泛化结论。','',
'## 实际留出结果','']
for s in summary['summaries']:
    m=s['overall'];lines += [f"- **{s['branch']}**：±30°命中{round(m['direction_hit_30']*48)}/48（{m['direction_hit_30']*100:.2f}%）；四方向{round(m['four_way_accuracy']*48)}/48（{m['four_way_accuracy']*100:.2f}%）；覆盖{round(m['coverage']*48)}/48；有效输出角度MAE {m['accepted_MAE_deg']:.3f}°、中位{m['accepted_median_deg']:.3f}°、P95 {m['accepted_p95_deg']:.3f}°；弃权180°惩罚MAE {m['penalized_MAE_deg']:.3f}°。静止误报{s['static_false_motion']}，全场阶跃误报{s['flash_false_motion']}，本批门槛{'PASS' if s['engineering_gate_pass'] else 'FAIL'}。"]
lines+=['','按速度，以下各组均16条：','']
for s in summary['summaries']:
    lines.append('- '+s['branch']+'：'+'；'.join(f"v{v} 命中{round(s['by_speed'][str(v)]['direction_hit_30']*16)}/16，有效MAE {s['by_speed'][str(v)]['accepted_MAE_deg']:.2f}°" for v in [6,12,24])+'。')
lines+=['','![速度与方向误差](direction_benchmark.png)','','![所有留出方向误差](all_direction_errors.png)','',
'a_r4/shared比Full/shared少命中一条、有效MAE约增加1.11°；两者统计覆盖不同，故同时报告全样本弃权惩罚指标。a_r4/own达到45/48并不证明优于Full；只是本批经过预登记独立校准的局部读出结果。48条有规律合成组合不是独立随机样本，不能声称总体识别率或显著优越性。','',
'## 失败和未验证范围','',
'全部主要失败见[FAILURE_CASES.json](FAILURE_CASES.json)，逐例预测包括没有超过30°但跨越四分类边界的情况，见[PREDICTIONS.csv](PREDICTIONS.csv)。a_r4/shared四个角误差超限例：','']
for r in failures:
    if r['branch']=='a_r4/shared':lines.append(f"- {r['clip']}：真值{r['truth_angle_deg']:.1f}° → {r['angle_deg']:.3f}°，误差{r['angle_error_deg']:.3f}°。")
lines+=['','慢速6的三路读出均只达到13/16；该弱点同时存在于原完整神经网络+本读出，不能全归因为裁剪。a_r4专用校准仍有三条慢速超30°，没有消除问题。Full还有一条慢速ON202.5°被预定模长门槛拒绝；未把它从命中率分母删掉。','',
'6静止和2阶跃零误报只覆盖这些控制；其他静止纹理/闪烁频率、多个运动物体、旋转、遮挡、噪声、低对比、自然场景与相机晃动未测。仅固定中央ROI、固定物体尺度、固定开始时刻与2s片段；不是任意帧率/任意运动起始/连续摄像头跟踪，更不能推定官方光流、速度估计、长时稳定性或生物视觉行为。相较原全网的空间覆盖、删界连接和T5a调谐损失仍成立，本批任务PASS不撤销旧负面结果。','',
'## 独立软件入口与证据','',
'可复制[portable_a_r4](portable_a_r4/readme.txt)到单独目录，只有3MB量级模型、采样映射、两个已拟合读出及Python代码/示例MP4；依赖Python、NumPy、OpenCV，无FlyVis/Torch/Full/GPU依赖。程序只读前2秒；输入须满足固定前0.5秒基线契约。输出目录必须不存在：','',
'```powershell','python -I -B predict_video.py --video demo.mp4 --output result_001','python -I -B predict_video.py --video your_clip.mp4 --output result_002 --profile own','```','',
'默认shared使用Full校准的冻结线性读出参数，但运行时不读取或计算Full神经网络；own使用预注册a_r4校准参数，无自动回退。输出result.json含角度/弃权、模长/特征RMS、视频/模型/读出SHA及完整采样时间映射，states.npy含400×3865自身状态，initial_state.npy与input.npy可审计。','',
f"隔离Python真实MP4入口已运行首个留出例T_ON_022.5_v12，输出{audit['portable_result']['angle_deg']:.6f}°，对应误差{abs(audit['portable_result']['angle_deg']-22.5):.6f}°。该例按原名单顺序固定，不是挑选最佳效果；其a0、输入、400步全候选状态及预测与正式结果逐位一致。全部76条a_r4轨迹及60800条科学提交链输入/时序核对完成；Full仅保存56ROI、完整a0/final以及逐步状态摘要，没有声称保存其全部中间45669态。",'',
'核心代码/参数/两个读出均哈希未变。报表组装在执行前发现真值角和预测角字段同名，另建analyze_results.py区分truth_angle_deg和angle_deg；原冻结实验源码保留，特征/预测/评价公式直接复用冻结模块，未重跑神经计算、未重拟合或改阈值。记录见[ANALYSIS_FIELD_CORRECTION.json](ANALYSIS_FIELD_CORRECTION.json)。','',
'## 实际成本、复现与停止','',
f"设计阶段{audit['times']['design_s']:.3f}s、留出阶段{audit['times']['heldout_s']:.3f}s；两阶段合计{audit['times']['design_s']+audit['times']['heldout_s']:.3f}s。独立MP4包检查{audit['times']['portable_s']:.3f}s。共152条模型视频运行×400步=60800电影神经步，公共初始化400步，加便携600步，总61800新CPU神经步。不是整轮编程/审计/报告耗时。",'',
f"a_r4每条2s片段的CPU解码+递推+SHA日志+保存中位{timings['a_r4']['median_clip_s']:.3f}s，Full {timings['Full']['median_clip_s']:.3f}s；不是纯算子性能，也没有真实摄像头端到端实时验收。所有科学轨迹有限，a_r4最大绝对活动{timings['a_r4']['max_abs_state']:.3f}，Full {timings['Full']['max_abs_state']:.3f}。GPU运行0、官方decoder帧0、硬件操作0。",'',
'复现整批请把代码复制到本线新的同级目录，保留原whole_network_pruning_20261013只读源；依次执行test_contract.py、experiment.py prepare、experiment.py design、experiment.py heldout、analyze_results.py。仅运行视频则直接使用便携包，不需要重复整批。数据与身份见PREREGISTRATION.json、FREEZE_RECEIPT.json、FROZEN_READOUTS.json、VIDEO_MANIFEST.json、SUMMARY.json、FINAL_AUDIT.json和DELIVERY_MANIFEST.json。','',
'本批完成后停止，不自动加刺激或迁移硬件。若继续软件研究，优先预登记独立的新速度/对比/运动起始与位置扰动，针对慢速失败和泛化范围验证；不能在这48条已看过测试上改读出后继续称留出验证。']
(HERE/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
with zipfile.ZipFile(HERE/'A_R4_independent_video_cpu.zip','x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((HERE/'portable_a_r4').iterdir()):
        if p.is_file():z.write(p,'A_R4_video/'+p.name)
manifest=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file() and 'runtime' not in p.relative_to(HERE).parts and '__pycache__' not in p.parts and p.name!='DELIVERY_MANIFEST.json':
        manifest.append(dict(path=str(p.relative_to(HERE)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)))
(HERE/'DELIVERY_MANIFEST.json').write_text(json.dumps(dict(schema='a_r4-video-direction-delivery/v1',file_count=len(manifest),bytes=sum(r['bytes'] for r in manifest),files=manifest),indent=2),encoding='utf-8')
print(json.dumps(dict(status='REPORT_AND_MANIFEST_COMPLETE',files=len(manifest),bytes=sum(r['bytes'] for r in manifest),manifest_sha=sha(HERE/'DELIVERY_MANIFEST.json'),timings=timings)))
