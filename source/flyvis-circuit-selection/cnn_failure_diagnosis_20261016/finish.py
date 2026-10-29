"""Saved-data scientific report and figures; no neural inference or hardware."""
from pathlib import Path
import hashlib, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'cnn_t4t5_mp4_holdout_20261016'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()

s=load(HERE/'SUMMARY.json');a=load(HERE/'FINAL_AUDIT.json');ex=load(HERE/'EXECUTION.json')
pr=load(HERE/'PROBE_SUMMARY.json');op=load(HERE/'OPERATOR_AUDIT.json')
assert a['status']=='PASS_SAVED_CPU_DIAGNOSIS_EVIDENCE'
by={r['case']:r for r in s['records']}
motion='OFF345_local_moving_background';static='STATIC_TEXTURE5s'
m=dict(np.load(HERE.parent/'cnn_t4t5_replacement_20261016/mapping.npz'))
z=dict(np.load(HERE/(static+'_PROBES.npz')));steps=z['steps'];chosen=steps>=800
f=np.load(OLD/'runs'/static/'Full/states_raw.npy',mmap_mode='r')
c=np.load(OLD/'runs'/static/'CNN/states_raw.npy',mmap_mode='r')
k=steps[chosen];H=m['H']
fd=f[k][:,H].astype(np.float64)-f[k-1][:,H]
cd=c[k][:,H].astype(np.float64)-c[k-1][:,H]
official_at_CNN_old_delta=cd-z['own_defect'][chosen]
error=c[k-1][:,H].astype(np.float64)-f[k-1][:,H]
rms=lambda x:float(np.sqrt(np.mean(np.asarray(x,dtype=np.float64)**2)))
stationary=dict(sampled_late_steps=k.tolist(),Full_actual_increment_RMS=rms(fd),CNN_actual_increment_RMS=rms(cd),
    official_same_old_increment_at_CNN_RMS=rms(official_at_CNN_old_delta),
    teacher_one_step_defect_RMS=rms(z['teacher_defect'][chosen]),
    cosine_native_increment_toward_Full=float(np.sum(official_at_CNN_old_delta*(-error))/(np.linalg.norm(official_at_CNN_old_delta)*np.linalg.norm(error))),
    interpretation='Reconstructed solely from previously computed/saved same-old probes; no new native or CNN forward. A biased fixed point in this case, not a claim of global stability.',new_forward_calls=0)
write('STATIONARY_MECHANISM.json',stationary)

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,3,figsize=(13,4.5),layout='constrained')
names=[motion,'OFF345_BG_FROZEN','OFF345_BG_GRAY','OFF345_BG_ONLY']
labels=['Moving BG\n+ target','Frozen BG\n+ target','Gray BG\n+ target','Moving BG\nonly']
vals=[by[n]['windows']['active']['foreground_flow']['field_error_E']*100 for n in names]
bars=axs[0].bar(labels,vals,color=['#bd5044','#d18046','#d9a653','#4d9f88'])
axs[0].axhline(20,ls='--',color='black',label='Frozen E gate 20%');axs[0].set_ylabel('Foreground flow E (%)')
axs[0].set_title('Same OFF345 / speed / position');axs[0].set_ylim(0,28);axs[0].legend(fontsize=8)
for b,v in zip(bars,vals):axs[0].text(b.get_x()+b.get_width()/2,v+.4,f'{v:.2f}',ha='center')
for ax,key,title in [(axs[1],'H_RMSE','Static H activity'),(axs[2],'flow_RMSE','Static official flow')]:
    names=[static,'TEXTURE_EXACT_HOLD','TEXTURE_SPATIAL_MEAN']
    vals=[by[n]['windows']['late'][key]*1000 for n in names]
    bars=ax.bar(['Original\ntexture','Exact frame\nhold','Spatial\nmean'],vals,color=['#bd5044','#d18046','#4d9f88'])
    ax.axhline(2,ls='--',color='black',label='Frozen absolute gate .002')
    ax.set_ylabel('Late absolute RMSE (x 0.001 model units)');ax.set_title(title);ax.set_ylim(0,max(vals)*1.25);ax.legend(fontsize=8)
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.07,f'{v:.3f}',ha='center')
fig.suptitle('Frozen CNN: paired CPU diagnostics (no training; original failures retained)',fontsize=13)
fig.savefig(HERE/'paired_causes.png',dpi=170);plt.close(fig)

fig,axs=plt.subplots(2,1,figsize=(10,7),layout='constrained')
for ax,name,title in zip(axs,[static,motion],['Static texture','Local OFF345 + moving background']):
    rows=load(HERE/(name+'_PROBE_STEPS.json'));t=[r['time_s'] for r in rows]
    for key,label in [('total_H_error_RMS','Closed-loop H error'),('teacher_defect_RMS','One-step defect on Full old state'),('R_input_effect_RMS','Current R-input contribution'),('H_history_effect_RMS','Own H-history contribution')]:
        ax.plot(t,[r[key] for r in rows],label=label)
    ax.set_yscale('symlog',linthresh=1e-7);ax.set_ylabel('RMS (model units)');ax.set_title(title);ax.grid(alpha=.2);ax.legend(fontsize=8,ncol=2)
axs[-1].set_xlabel('Model time (s)')
fig.suptitle('Saved-state probes: contributions follow a fixed path, not additive RMS percentages')
fig.savefig(HERE/'one_step_and_history.png',dpi=170);plt.close(fig)

b=s['conclusions']['background'];st=s['conclusions']['static'];stat=pr['cases'][static];mot=pr['cases'][motion]
def fgm(name):return by[name]['windows']['active']['foreground_flow']
lines=[]
for name,label in zip([motion,'OFF345_BG_FROZEN','OFF345_BG_GRAY','OFF345_BG_ONLY'],['原移动背景＋目标','同一目标＋冻结背景','同一目标＋灰背景','只有原移动背景']):
    q=fgm(name);lines.append(f"- {label}：局部E **{q['field_error_E']*100:.3f}%**，M {q['magnitude_ratio']:.6f}，场角 {q['angle_deg']:.3f}°；原判据{'通过' if by[name]['pass_gate'] else '未通过'}。")
report=f"""# 冻结CNN两项失败的CPU原因诊断

2026-10-16，④独立科研；状态 **DIAGNOSIS_COMPLETE_NOT_MODEL_RECOVERY**。本轮没有训练、扩大/更换模型、GPU计算或板卡操作，没有修改原阈值或封存失败。

本轮已把近端失败机制定位到：当前学到的T4/T5更新映射在局部目标和静态空间纹理状态上存在系统偏差，闭环形成有偏活动。它不是主要由背景运动或视频编码时间抖动造成；没有发现必须增加时间记忆或空间范围的证据。尚未拆分训练数据覆盖、正则化及优化未充分收敛各自的责任，不能声称最终训练原因已被唯一确定。

## 1. 固定配对与运行范围

运行前[预注册](PREREGISTRATION.json) SHA `{sha(HERE/'PREREGISTRATION.json')}`。相同31,168参数/`ridge.pt` SHA `{s['records'] and load(HERE/'PREREGISTRATION.json')['model_SHA']}`，相同45,669节点初态、展开参数、721采样和5ms。旧两个失败例直接复用原Full/CNN完整状态及官方光流。

新增3条实际编码/解码MP4，固定失败例OFF345、速度12、中心(4,0)、局部半径4.5，只改变背景为冻结、灰色或移除前景目标；另2条是在原解码后视网膜输入上施加明确干预：从step220固定真实解码帧110，或逐帧将721点替换为同帧均值。后两条不能称为新MP4。所有新增数据是诊断对照，已见且非独立留出集。

每条件Full/CNN各1000步，共 **{ex['commits']}次新生产提交**；每条CNN生产路径都只读取自身旧H和实时旧R。原H入口拒绝护栏违规0、原H生产更新0、真值纠正0。另设每5步一次的旧保存状态探针，共400个时间点，CNN {pr['CNN_diagnostic_calls']}次、原H {pr['original_H_diagnostic_calls']}次诊断调用，全部在生产之外，不计为新闭环或恢复。

沿用331点ROI，局部前景为中心(4,0)半径3的30点；active320:720、allpost200:1000、stopped840:1000，静态adapted400:1000、late800:1000。运动E≤20%、M[0.8,1.2]、场角≤15°及H响应误差≤20%；静止H/R/光流绝对RMSE≤.002，均未改变。弱参考不能算通过。

## 2. “移动背景失败”主要并不是背景在运动

{chr(10).join(lines)}

冻结背景只使局部E下降 **{b['moving_minus_frozen_E']*100:.3f}个百分点**，未达到事先规定的2个百分点“本配对有实质影响”界限。去掉背景纹理，目标在灰背景上仍超过20%门槛；而单独移动背景通过。因此，这个局部OFF345目标本身已足以触发失败，不能把失败命名直接当成原因。

原失败M=1.1715、场角7.21°均仍在单项范围内，E是幅度与场形差异的综合。结果更接近响应偏强/场形误差，而非运动方向反转。E/场角都相对同输入Full，不是实际场景真值方向错误或分类准确率。

本配对固定了方向、位置、速度和极性，足以排除“仅移动背景才失败”。尚未进一步拆分局部形状、位置、OFF极性、345°方向及其交互，所以不能扩大为所有局部刺激或所有OFF方向失败。

## 3. 静止纹理主要是空间图样下的稳态偏差

- 原纹理late H RMSE {st['original_late']['H_RMSE']:.9f}、光流 {st['original_late']['flow_RMSE']:.9f}，失败。
- 固定解码帧后H {st['locked_late']['H_RMSE']:.9f}、光流 {st['locked_late']['flow_RMSE']:.9f}，仍失败；分别只改善 {st['relative_error_reductions']['H_RMSE']*100:.2f}%/{st['relative_error_reductions']['flow_RMSE']*100:.2f}%。视频解码时间微扰不是此例主要来源。
- 去掉空间纹理、保留每帧平均亮度后，late H {st['spatial_mean']['windows']['late']['H_RMSE']:.9f}、光流 {st['spatial_mean']['windows']['late']['flow_RMSE']:.9f}；adapted和late均按原.002界限通过。空间结构相关状态才是这组对照的关键差别，不能据此断言某一个纹理频率或对比度单独负责。

晚期Full真实H每步变化RMS仅 {stationary['Full_actual_increment_RMS']:.9g}，CNN在这个正确旧态上的一步预测偏差却有 **{stationary['teacher_one_step_defect_RMS']:.9g}**。也就是原网络已经接近稳定时，CNN仍会把它推离正确状态。CNN自身最后也接近稳定，但稳定到了有偏状态；这不是数值发散。

在CNN自己的晚期旧态上，官方原式所给的一步变化RMS为 {stationary['official_same_old_increment_at_CNN_RMS']:.9g}，与指向Full状态差的余弦为 {stationary['cosine_native_increment_toward_Full']:.6f}。这是保存探针的代数重建，不是把官方H送回生产网络“修好”CNN。

## 4. 单步映射偏差确实存在，不只是闭环跑久才出错

400个诊断时间点，原H更新与保存Full的对应下一态最大差0，CNN重算与保存CNN对应下一态最大差0；时间/节点索引在这些探针上吻合。错误分解闭合差仅 {max(stat['decomposition_closure_max_abs'],mot['decomposition_closure_max_abs']):.9g}。

- 静止late：正确Full旧态上的一步H偏差RMS {stat['windows']['late']['teacher_defect']:.9g}；自身H历史影响 {stat['windows']['late']['H_history_effect']:.9g}、R输入变化影响 {stat['windows']['late']['R_input_effect']:.9g}；完整H误差 {stat['windows']['late']['saved_total_error']:.9g}。
- 局部运动active：正确Full旧态上的一步H偏差RMS {mot['windows']['active']['teacher_defect']:.9g}；自身H历史影响 {mot['windows']['active']['H_history_effect']:.9g}、R输入变化影响 {mot['windows']['active']['R_input_effect']:.9g}；完整H误差 {mot['windows']['active']['saved_total_error']:.9g}。

分解按固定路径 `正确旧态 → 仅替换R为CNN旧R → 再替换H为自身旧H`。它是受控函数探针，顺序和非线性会影响解释；各项RMS不能相加成贡献百分比。它支持“单步已学偏，H历史保留偏差”的机制，不支持单靠重置状态或增加运行时长就会正确。

官方decoder直接读取全部8类T4/T5。静止late仅混入CNN的H、保持Full的R，就产生光流RMSE {stat['decoder_counterfactual']['CNN_H_Full_R_RMSE']:.9f}，完整误差为 {stat['decoder_counterfactual']['total_RMSE']:.9f}；只混入CNN的R为 {stat['decoder_counterfactual']['Full_H_CNN_R_RMSE']:.9f}。运动active对应为 {mot['decoder_counterfactual']['CNN_H_Full_R_RMSE']:.9f} / {mot['decoder_counterfactual']['total_RMSE']:.9f} / {mot['decoder_counterfactual']['Full_H_CNN_R_RMSE']:.9f}。这些是decoder离线混合读出，未改变任何生产轨迹；说明偏差主要随H已经进入读出，不能归咎于其余网络或decoder未正确加载。

## 5. 是否一定要CNN，以及本结构是否先天做不到

不一定要CNN，局部共享MLP、图网络或带记忆网络均可作为候选。但本轮补充的[静态算子检查](OPERATOR_AUDIT.json)给出更具体的判断：全部433,880条H目标边的源节点都在23输入类型中，169个半径7偏移覆盖全部实际依赖，原边ID映射的邻居全匹配；所有有效位置的原式卷积系数、同类型自身衰减和bias跨度均为0，H没有外部刺激直接注入。

因此，在实数代数意义下，原H一步更新可以写成现有结构所包含的“ReLU空间卷积＋自身旧态的线性项＋bias”。**没有证据表明这两项失败必须靠更大模型或额外长时间记忆解决。** 这只是表达能力证明条件检查，不表示当前训练已经学到正确参数、不表示FP32运算顺序逐位等价，也没有用原参数改造或替换CNN。

静态分析是预注册后的补充结构研究，0前向/0训练，没有增加功能条件或更改原判据。当前更值得检查的是训练状态覆盖和拟合方法；此前训练CG达到400轮上限而非残差收敛，但本轮没有单独操控优化轮数、正则或训练样本，不能把它指定为唯一原因。

## 6. 建议与停止边界

下一步若继续，优先维持同规模模型，用训练专用的静态空间纹理和局部边缘状态检查拟合，并加入正确稳态应保持不变的约束；先过单步/短闭环门禁，再冻结参数，用完全新的纹理种子、方向与位置做独立验收。当前诊断数据只能作为已见诊断/后续训练素材，不能调参后继续称为留出测试。

换成共享MLP可以作为以后有界的同数据/同预算对照，而非当前先行结论。GRU/更大CNN不应作为没有依据的第一步。本轮没有启动任何再训练或新架构实验。**CNN上板等待②、⑦主线做好，并由用户在软件闭环和功能结果明确后决定。** 中途的板卡准备目录已标停止，不再继续。

## 7. 证据与实际资源

新生产计算 {ex['wall_s']:.3f}秒；独立旧态探针 {pr['wall_s']:.3f}秒；补充静态结构检查 {op['wall_s']:.3f}秒。前两项合计 {ex['wall_s']+pr['wall_s']:.3f}秒，不含进程导入、视频生成、分析、绘图和文件检查。CPU单线程；GPU0、板卡0、训练0。新五条件全部1000步稳定完成，诊断不是新模型功能PASS。

[最终保存数据检查](FINAL_AUDIT.json)核对10,000完整提交的全部状态、旧/新/输入摘要链、时间和原H禁用；新增神经步0。没有重复旧大规模审计或重新运行原失败。源/模型SHA保持一致。完整结果在 `runs/`、`inputs/`、`videos/`，逐步及全H探针在 `*_PROBES.npz`、`*_PROBE_STEPS.json`，官方光流混合读出在 `*_DECODER_PROBES.npz`，指标在[METRICS.csv](METRICS.csv)。最终SHA文件清单见 `DELIVERY_MANIFEST.json`。

![配对原因对照](paired_causes.png)

![单步与历史误差](one_step_and_history.png)

本次复用原CPU/decoder推理和旧生产闭环，没有新增通用Skill。报告中的结论只适用于本批受控刺激与保存状态；不宣称自然视频能力、真实果蝇功能损伤、FPGA恢复或最终硬件实现。
"""
(HERE/'REPORT.md').write_text(report,encoding='utf-8')
(HERE/'reproduce.txt').write_text("""CPU-only; all original accepted results are read-only.
Completed one bounded run; do NOT repeat production calculations in this directory.
For a separately scoped reproduction, first create a NEW sibling directory.
Existing command order was:
  python -B diagnostic.py prepare
  python -B diagnostic.py run
  python -B diagnostic.py analyze
  python -B operator_audit.py
  python -B diagnostic.py audit
  python -B finish.py
No training, CUDA, WSL or board call occurs. Python3.14 / NumPy / CPU PyTorch /
OpenCV and Matplotlib from the existing environment. Torch one thread and CUDA
hidden by the accepted CPU-only common module.
Five paired counterfactuals are diagnostic data, NOT independent holdout cases.
Teacher/same-old probes are offline diagnostics, NOT production CNN recovery.
The original model, original failures, threshold/ROI and GUI/FPGA source are preserved.
""",encoding='utf-8')
files=[]
for f in sorted(HERE.rglob('*')):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json':files.append(dict(path=f.relative_to(HERE).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
write('DELIVERY_MANIFEST.json',dict(evidence='ACTUAL_CPU_DIAGNOSIS_NOT_MODEL_RECOVERY',file_count=len(files),
    total_bytes=sum(x['bytes'] for x in files),files=files))
print(json.dumps(dict(status=a['status'],files=len(files),bytes=sum(x['bytes'] for x in files),
    manifest_SHA256=sha(HERE/'DELIVERY_MANIFEST.json'),stationary=stationary),indent=2))
