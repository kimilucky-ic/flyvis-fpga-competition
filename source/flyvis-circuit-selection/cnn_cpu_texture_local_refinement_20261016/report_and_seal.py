"""Report saved CPU results and seal files. No Torch, training or inference."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import cv2

HERE=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for x in iter(lambda:f.read(4*1024**2),b''):h.update(x)
    return h.hexdigest()

summary=load(HERE/'SUMMARY.json');gate=load(HERE/'TRAINING_GATE.json');fit=load(HERE/'training/FIT.json')
short=load(HERE/'training/SHORT_GATE.json');freeze=load(HERE/'MODEL_FREEZE.json');audit=load(HERE/'FINAL_AUDIT.json')
plan=load(HERE/'PREREGISTRATION.json');execution=load(HERE/'TEST_EXECUTION.json');data=load(HERE/'training/DATA.json')
assert audit['status']=='PASS_SAVED_SAME_SIZE_CPU_REFINEMENT_EVIDENCE'
m=dict(np.load(HERE.parent/'cnn_t4t5_replacement_20261016/mapping.npz'))
cases=load(HERE/'testing/INPUTS.json');records=summary['records']
motion=[r for r in records if r['group']=='motion'];static=[r for r in records if r['group']=='static']
flows=[];hrel=[];foreground=[]
for r in motion:
    for w in r['windows'].values():
        hrel.append(w['H_response_relative_L2'])
        flows.append(w['flow'])
        if 'foreground_flow' in w:foreground.append(w['foreground_flow']);flows.append(w['foreground_flow'])
flow_valid=[f for f in flows if f['reference_eligible']]
e=[f['field_error_E'] for f in flow_valid];angles=[f['angle_deg'] for f in flow_valid];magnitudes=[f['magnitude_ratio'] for f in flow_valid]
static_max={key:max(w[key] for r in static for w in r['windows'].values()) for key in ['H_RMSE','R_RMSE','flow_RMSE']}
range_stats=dict(motion_passed=sum(r['pass_gate'] for r in motion),motion_total=len(motion),
    static_passed=sum(r['pass_gate'] for r in static),static_total=len(static),
    flow_E_range=[min(e),max(e)],flow_M_range=[min(magnitudes),max(magnitudes)],field_angle_range=[min(angles),max(angles)],
    H_response_relative_L2_range=[min(hrel),max(hrel)],static_max_RMSE=static_max,
    all_motion_references_eligible=len(flow_valid)==len(flows))
timing_median={mode:float(np.median([r['wall_s'] for r in execution['records'] if r['mode']==mode])) for mode in ['Full','CNN']}
range_stats['per_5s_video_CPU_median_wall_s']=timing_median
write('REPORT_DATA.json',range_stats)

# Every-step all-H/all-R errors have already been computed; summarize, do not rerun.
state_max=0.;last_max=0.;state_violations=0;flow_violations=0;flow_max=0.
for case in cases:
    root=HERE/'testing/runs'/case['id'];f=np.load(root/'Full/states_raw.npy',mmap_mode='r');c=np.load(root/'CNN/states_raw.npy',mmap_mode='r')
    maximum=0.
    for k in range(1000):
        delta=abs(c[k].astype(np.float64)-f[k]);maximum=max(maximum,float(delta.max()))
        state_violations+=int(np.count_nonzero(delta>1e-5+1e-5*abs(f[k])))
    last=float(abs(c[-1].astype(np.float64)-f[-1]).max());state_max=max(state_max,maximum);last_max=max(last_max,last)
    ff=np.load(root/'Full/flow.npy');cf=np.load(root/'CNN/flow.npy');delta=abs(cf.astype(np.float64)-ff)
    flow_max=max(flow_max,float(delta.max()));flow_violations+=int(np.count_nonzero(delta>1e-5+1e-5*abs(ff)))
write('ALL_NODE_DIFFERENCE_SUMMARY.json',dict(max_all_nodes_all_steps=state_max,max_final_state=last_max,
    max_official_flow_abs=flow_max,state_violations_at_existing_atol_rtol_1e5=state_violations,
    flow_violations_at_existing_atol_rtol_1e5=flow_violations,
    role='supplementary descriptive comparison at existing1e-5atol/rtol, not a replacement functional gate',
    official_FP32_operation_order_bitwise_equivalence_claim=False,new_neural_steps=0))
write('STEP_ERROR_COLUMNS.json',['H_RMSE','R_RMSE','flow_component_RMSE_on331ROI'])

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
values=[]
for r in motion:
    values.append(max(f['field_error_E'] for w in r['windows'].values() for f in [w['flow']]+([w['foreground_flow']] if 'foreground_flow' in w else [])))
axs[0].bar(np.arange(6),np.maximum(values,1e-10),color='#347fa2');axs[0].set_yscale('log');axs[0].axhline(.2,color='#aa453e',ls='--',label='Unchanged E gate .20')
axs[0].set_xticks(np.arange(6),[r['case'].replace('TEST_','').replace('_','\n') for r in motion],fontsize=8)
axs[0].set_title('Six unseen motion movies: worst frozen-window flow E');axs[0].set_ylabel('Relative field error (log scale)');axs[0].legend(fontsize=8)
for j,(key,label) in enumerate([('H_RMSE','T4/T5 activity'),('R_RMSE','Other neurons'),('flow_RMSE','Official flow')]):
    vals=[max(w[key] for w in r['windows'].values()) for r in static]
    axs[1].bar(np.arange(4)+(j-1)*.23,np.maximum(vals,1e-12),width=.23,label=label)
axs[1].set_yscale('log');axs[1].axhline(.002,color='#aa453e',ls='--',label='Unchanged gate .002')
axs[1].set_xticks(np.arange(4),['New texture\nlow contrast','New texture\nmedium','New texture\nhigh contrast','Gray'])
axs[1].set_title('Unseen static movies: worst of adapted / late');axs[1].set_ylabel('Absolute RMSE (model units, log scale)');axs[1].legend(fontsize=8)
fig.suptitle('Frozen 31,168-parameter CNN / actual CPU closed loops / no teacher correction')
fig.savefig(HERE/'new_test_gates.png',dpi=170);plt.close(fig)

center=np.maximum.reduce([abs(m['grid_uv'][0]),abs(m['grid_uv'][1]),abs(m['grid_uv'].sum(0))])<=1
first=HERE/'testing/runs'/cases[0]['id'];f=np.load(first/'Full/states_raw.npy',mmap_mode='r');c=np.load(first/'CNN/states_raw.npy',mmap_mode='r')
fig,axs=plt.subplots(2,4,figsize=(12,5),layout='constrained')
for j,ax in enumerate(axs.flat):
    ids=m['H_grid_ids'][j,center];ax.plot(np.arange(1000)*.005+.005,f[:,ids].mean(1),color='#253944',label='Full')
    ax.plot(np.arange(1000)*.005+.005,c[:,ids].mean(1),color='#d8833d',ls='--',label='CNN')
    ax.set_title(['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d'][j]);ax.set_xlabel('Model time (s)');ax.set_ylabel('Activity (model units)')
axs[0,0].legend();fig.suptitle('First preregistered unseen movie: 8 types, mean of fixed 7 central positions / type')
fig.savefig(HERE/'eight_type_activity.png',dpi=170);plt.close(fig)

fig,axs=plt.subplots(3,3,figsize=(10,10),layout='constrained')
uv=m['grid_uv'];xx=np.sqrt(3)/2*uv[1];yy=uv[0]+uv[1]/2
for row,index in enumerate([0,2,7]):
    case=cases[index];step=900 if case['group']=='static' else 500
    cap=cv2.VideoCapture(case['video_path']);cap.set(cv2.CAP_PROP_POS_FRAMES,step//2);okay,img=cap.read();cap.release();assert okay
    axs[row,0].imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB));axs[row,0].set_title(case['id']+'\nactual decoded input',fontsize=9);axs[row,0].axis('off')
    root=HERE/'testing/runs'/case['id'];f=np.load(root/'Full/flow.npy')[step];c=np.load(root/'CNN/flow.npy')[step]
    maximum=max(np.hypot(*f).max(),np.hypot(*c).max(),1e-12)
    for col,(field,label) in enumerate([(f,'Original Full'),(c,'CNN replacement')],1):
        hue=(np.arctan2(field[1],field[0])/(2*np.pi)+1)%1
        rgb=hsv_to_rgb(np.stack([hue,np.ones(721)*.8,np.clip(np.hypot(*field)/maximum,0,1)*.85+.15],axis=1))
        axs[row,col].scatter(xx,yy,c=rgb,s=9)
        ids=np.arange(0,721,9);norm=np.maximum(np.hypot(*field[:,ids]),1e-12)
        axs[row,col].quiver(xx[ids],yy[ids],field[0,ids]/norm,-field[1,ids]/norm,color='#222b33',scale=27,width=.003)
        axs[row,col].set_aspect('equal');axs[row,col].invert_yaxis();axs[row,col].axis('off');axs[row,col].set_title(label+' official flow')
fig.suptitle('Saved new-test results (offline figure); shared Full/CNN magnitude scale in each row\nStatic raw decoder output can be nonzero in both models; not scene flow ground truth',fontsize=11)
fig.savefig(HERE/'new_stimuli_and_flow.png',dpi=160);plt.close(fig)

base=fit['baseline']['groups']['sensory'];val=fit['validation']['groups']['sensory'];aug=fit['validation']['groups']['augmented']
short_values=[r for r in short['records'] if 'H_nRMSE' in r]
short_h=max(r['H_nRMSE'] for r in short_values);short_r=max(r['R_nRMSE'] for r in short_values)
newmotion=range_stats['motion_passed'];newstatic=range_stats['static_passed']
report=f"""# 同规模CNN补充纹理/局部目标训练与全新视频CPU验证

2026-10-16；④独立科研。最终状态 **{summary['status']}**。本轮使用CPU，GPU0、板卡0；未修改②GUI、⑦硬件、上游原模型或任何旧验收结果。

## 当前到底实现了多少功能

数量上，正式替代路径已由CNN提供全部 **5,768个T4/T5节点、8类** 的下一状态，其余39,901节点继续真实递推。CNN每步读自己旧H和当前旧R，原H更新停用；不是只预测中心曲线，也不是视频标签分类。

功能上，本次模型冻结后的 **{summary['passed']}/{summary['total']}条全新受控MP4** 按原判据通过，其中运动 **{newmotion}/6**，静态纹理/灰屏 **{newstatic}/4**。这代表所列刺激下与原FlyVis活动/官方光流读出的保真度，不代表“恢复了原神经元百分之多少的全部功能”，也不是方向分类准确率。

新运动覆盖ON/OFF、135°/315°、速度8/9/11/13/15/16、全场和中心偏移(-2,-4)/(2,4)/(-4,-2)/(4,2)、灰/静态纹理/移动背景。新静止纹理含三个未参与训练的随机种子、对比度.06/.12/.18与平滑尺度2.5/5.5/8，另灰屏。网络全部5,768 H、全部39,901 R及完整官方光流均逐步保存，不靠56中心节点曲线宣称完整等价。

尚未验证：新模型完整12方向DSI、任意自然视频、真实光流真值准确率、自由交互起始时间、分钟级稳定性、相同模型GPU或FPGA。旧模型曾有10秒测试，不能自动转移成新模型10秒证据。当前结果是原模型的计算/读出替代，非真实果蝇行为恢复。

## 1. 训练、内部检查与独立测试的隔离

[预注册](PREREGISTRATION.json) SHA `{sha(HERE/'PREREGISTRATION.json')}`。保持原HexCNN结构与 **31,168参数**、原节点映射、共同完整a0、5ms、原R-only及DecoderGAVP；模型不扩容、不改变科学门槛。

训练包含原四方向缓存、先前两个失败Full轨迹（明确转为训练/开发资料）、4条新训练视频，以及128个仅训练用的独立高斯神经状态，由原H下一态监督。扰动是神经状态覆盖，不是自然视觉样本；除监督标签外未把原H权重、bias、tau直接写进CNN系数。实际方法为有监督更新算子辨识，而非图像分类。

感官训练抽样排除k%5==4，内部检查使用这些留出时间点；扰动0:96训练、96:128验证，索引互斥。但相邻时间仍有关联，内部检查不能冒充独立视频泛化。静态晚期样本和共同初态在损失中固定加权，作为稳态约束；没有使用原式参数构造解析CNN。

一次float64残差ridge/共轭梯度拟合，ridge1e-8、最多400轮、上限360秒。本次实际 **{fit['iterations']}轮**、{fit['wall_s']:.3f}秒，正规方程相对残差 {fit['residual_last']:.9g}，{'达到了预注册1e-8停止条件' if fit['converged_normal_equation'] else '达到了轮数上限而非残差条件'}；最终系数转float32。没有额外SGD、BPTT、调参重试或模型选择扫参。覆盖与优化同时改变，本轮无法单独归因其贡献。

正确状态上的单步内部检查（同一8192检查点分两组）：感官增量nRMSE由本轮原检查点基线 **{base['increment_nRMSE']*100:.6f}%** 降至 **{val['increment_nRMSE']*100:.6f}%**，绝对增量RMSE {val['absolute_increment_RMSE']:.9g}；独立扰动状态增量nRMSE {aug['increment_nRMSE']*100:.6f}%。沿用整体≤10%、每类型≤20%门禁。

31个训练条件短窗共{short['commits']}次真实闭环提交；每窗仅开始时取一次Full旧态，之后128步都用自身H/真实R，无中途纠正。H状态nRMSE最大{short_h*100:.7f}%、R最大{short_r*100:.7f}%；所有旧H≤5%/R≤1%/类型≤10%门槛通过。静态窗另保持原H/R/光流绝对.002界限，灰屏H控制通过。30窗共3840完整状态及摘要链独立读取验收；额外128灰屏仅保存汇总，未称其全部中间状态封存。

门禁通过才写[MODEL_FREEZE.json](MODEL_FREEZE.json)，模型SHA **`{freeze['sha256']}`**；随后才实际生成10条新测试MP4。冻结时间与视频生成时间均验收，测试期间0训练更新。没有依据新测试成绩重新挑模型、改阈值或改ROI。

## 2. 新刺激中的活动与功能结果

- 六运动条件，全部命名窗口及适用前景ROI：官方场误差E范围 **{min(e)*100:.9f}%–{max(e)*100:.9f}%**，幅度比M **{min(magnitudes):.9f}–{max(magnitudes):.9f}**，场角 **{min(angles):.9f}°–{max(angles):.9f}°**。所有参考有效性为 {range_stats['all_motion_references_eligible']}。
- 全H响应相对L2范围 **{min(hrel)*100:.9f}%–{max(hrel)*100:.9f}%**；全45,669节点跨全部新条件/时间步最大绝对差 **{state_max:.9g}**，最终态最大绝对差 {last_max:.9g}。不宣称FP32逐位等价。
- 新静止纹理和灰屏，adapted/late中最坏H绝对RMSE **{static_max['H_RMSE']:.9g}**、R **{static_max['R_RMSE']:.9g}**、官方流 **{static_max['flow_RMSE']:.9g}**，原门槛均为.002。
- 补充描述性核对沿用既有数值容差atol=rtol=1e-5：全节点超限{state_violations}、官方光流超限{flow_violations}，光流最大绝对差{flow_max:.9g}；不改变本次预注册功能判据，也不宣称逐位一致或所有输入等价。
- 首个新刺激另执行1000步Sham，与Full全部状态逐位一致：**{summary['Sham_all_states_bitwise_equal']}**。CNN生产原H更新0、真值纠正0；其余R不使用预录Full状态，CNN输出持续进入下一步反馈。

完整逐例、每时间窗、局部/全场及静态判据见[METRICS.csv](METRICS.csv)和[SUMMARY.json](SUMMARY.json)；全部H/R逐步RMSE见各 `testing/runs/<case>/STEP_ERRORS.npy`。中心56节点活动图只是展示，验收覆盖所有H/R。

原模型静态输入时的原始decoder输出可非零，所以不能把静态流场的颜色当作运动误报。运动场角是CNN对Full的场夹角，不是刺激方向分类误差；未计算或宣称自然光流EPE准确率。

## 3. 与之前失败的关系

此前CNN在静止空间纹理上的正确旧态一步预测有偏，闭环收敛到有偏活动；局部OFF345在灰背景也已失败。当前训练有针对性地补充这些开发条件及更独立的状态覆盖，训练窗通过，并在新种子/方向/速度/位置/纹理上验证。

本轮没有重算旧版本的旧失败来追求PASS，也没有将被用于训练的旧失败再称留出测试。旧7/8运动、1/2静态是旧模型/旧测试集；本轮新模型/新测试集的通过率不能直接作为同基准提升幅度。当前有监督辨识表现接近浮点误差尺度，支持“现有架构先前没拟合准确”，但不证明所有输入均等价。

## 4. 实际资源、证据及停止

- 新训练Full监督4000完整步，另128原H标签调用；训练数据产生{data['wall_s']:.3f}秒。
- 拟合{fit['wall_s']:.3f}秒；训练短窗{short['wall_s']:.3f}秒；训练全过程{gate['wall_s']:.3f}秒。区间有包含关系，不重复相加。
- 新正式Full/CNN/首例Sham共 **{execution['commits']}** 次完整态提交，计算及官方解码/保存 **{execution['wall_s']:.3f}秒**，非纯神经内核性能。单线程CPU，没有GPU或板卡操作。
- 每5秒视频本机CPU整段中位耗时Full {timing_median['Full']:.3f}秒、CNN {timing_median['CNN']:.3f}秒，CNN约为Full的{timing_median['CNN']/timing_median['Full']:.3f}倍耗时；含构造、记录、保存和官方解码，不是纯核基准。当前只证明功能替代，没有CPU加速或更适合FPGA的结论。
- [保存结果验收](FINAL_AUDIT.json)覆盖全部正式状态、输入旧新时间链、训练/验证索引、冻结早于测试生成、模型和依赖身份；新增神经计算0。没有重复旧故障大审计。
- 初次准备内存门禁拒绝保留在 `PREPARATION_REJECTION.md`；恢复后同门槛通过，未降门槛或终止其他工作线。源/模型/初态/参数旧文件保持不变。全部新数据和代码仅在本目录，未新增通用Skill。

按用户要求，本批完整结果后停止，不自行新增训练、架构或24条件研究。**CNN上板仍等待②、⑦主线完成以及用户决定**；现有原式FPGA成果不能当成CNN硬件证据。本线当前可交付受控视频的CPU人工回路替代演示；自然场景、长时及硬件仍另列验证范围。

![所有新条件门槛](new_test_gates.png)

![八类中心活动](eight_type_activity.png)

![全新输入和官方读出](new_stimuli_and_flow.png)
"""
(HERE/'REPORT.md').write_text(report,encoding='utf-8')
(HERE/'reproduce.txt').write_text("""Same-size CNN CPU refinement, completed one bounded training and test batch.
Do NOT overwrite or rerun this accepted directory. Use a NEW owned sibling for
a separately scoped reproduction; retain exact prior prerequisites read-only.
Original command order:
  python -B prepare.py
  python -B train.py
  python -B audit_short_saved.py
  python -B test.py
  python -B analyze.py
  python -B audit.py
  python -B report_and_seal.py
Test entry requires TRAINING_GATE pass and frozen model SHA; new MP4 encoding
occurs only after freeze. Test never trains or reads teacher future neural states.
Current frozen model: training/model.pt, identity in MODEL_FREEZE.json.
CPU only, existing Python3.14/NumPy/CPU PyTorch/OpenCV/Matplotlib, one thread.
No installation, GPU, WSL, board, GUI, RTL or original-model edits.
Fields/delta.npy and training/teacher/ are supervision, not production playback.
Previous two failed videos are now development/train data. Current new tests
are seen after this batch and cannot be reused as independent tests after tuning.
""",encoding='utf-8')
files=[]
for f in sorted(HERE.rglob('*')):
    if f.is_file() and f.name!='DELIVERY_MANIFEST.json':files.append(dict(path=f.relative_to(HERE).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
write('DELIVERY_MANIFEST.json',dict(file_count=len(files),total_bytes=sum(x['bytes'] for x in files),
    evidence='ACTUAL_CPU_TRAINING_AND_NEW_STIMULUS_CLOSED_LOOPS_NOT_HARDWARE',files=files))
print(json.dumps(dict(status=summary['status'],motion=[newmotion,6],static=[newstatic,4],ranges=range_stats,
    max_all_node_error=state_max,files=len(files),bytes=sum(x['bytes'] for x in files),
    manifest_SHA256=sha(HERE/'DELIVERY_MANIFEST.json')),indent=2))
