# ① 全T4/T5官方 Full / decoder 首批支撑

2026-10-11。只写本目录及 `docs/workstreams/flyvis-gpu.md`。统一任务书为 `docs/workstreams/FLYVIS_SPRINT_20261011_AUTORUN_T4T5.md` 的①章节。609步摄像头 Full GPU 通过成果完整保留，本轮没有重新运行。

当前验收是 **CPU checkpoint/输入结构审计 + 42项有界CPU接口与读出测试 PASS**。本轮神经更新0、decoder forward0、CUDA计算0、板操作0。GPU分块推理、四条件干预与⑧decoder插件运行均为 **NOT_RUN**。原环境、权重和上游源码未改；没有新增实验调度器或全量CPU交叉验证。

## 关键科学发现

官方 DecoderGAVP 直接读取34类、每类721位置，共24,514个节点。T4a–d通道4–7，T5a–d通道8–11；八类合计5,768节点，完整全局索引24039–29806。每类在第一层均有152个非零权重tap（8个输出通道×19个hex支撑tap），说明其读入通路实际存在。权重大小不能单独证明因果重要性。

出边释放阻断保留细胞自身活动，decoder仍直接读取它们。必须将释放阻断、decoder-only输入遮罩、完整活动钳制分开解释；保留的decoder响应不自动证明网络容错。原输入是带符号连续神经状态，decoder内部先执行ReLU，不能用中心65节点替代完整空间活动。

光流输出 `[B,T,2,721]` 的两分量为x向右、y向上。源码 `sample_flow()` 将Sintel原始帧对位移除以原图高度并反转y；模型训练配置确认为13×13 BoxEye，flow目标执行 **sum**，不是mean。原始预测保留该训练目标尺度；可另外显示 `raw/169` 的名义区域均值，但必须标为派生量。模型内部还有原始 `softplus(third)+1` 分母，完整保留。不能把raw当成像素/秒、每5ms位移，不能给每个消融模式独立max归一化。

原MovingBar/Edge增大水平offset再按正角度旋转，因此在上述坐标中刺激方向为 `[cos(theta),sin(theta)]`。0/60/90/180/240/270度的原Cartesian renderer小CPU探针验证了符号；没有重渲染原刺激或运行神经网络。合成edge没有真实光流标签，与Full/Sham的endpoint difference不是Sintel准确率。

## 交付文件与调用

- `FULL_DECODER_CONTRACT.json`：原checkpoint、完整共同初态、展开参数、全节点、时间及四条件文件身份；输入输出、单位、坐标、递归eval、权重/BatchNorm buffer不变规则。
- `TYPE_INPUT_AUDIT.json`：34类完整顺序与实际权重通路；`cpu_audit_r1/decoder_input_global_ids.npy` 为int64 `[34,721]`；`t4t5_global_ids.npy` 为int64 `[5768]`；`decoder_input_nodes.csv` 含channel/type/hex/global/u/v，坐标与④一致。
- `READOUT_CONTRACT.json`、`flow_readout.py`：直接调用④被冻结的 `metrics.py`，固定331点radius10 ROI、baseline160–199、primary200–285、tail286–484。Q/幅度/角差/弱响应门槛和v1科学阈值均不另造。官方loss公式另作CPU float64诊断，不称为生物功能百分比。
- `service.py`：导入不加载Torch/FlyVis/CUDA。`AcceptedReferenceCache.open()`按完整身份只读返回旧数据，错身份/cache miss/formal fresh明确拒绝；不会自动计算。`OfficialDecoderService`使用官方权重与forward，递归eval、前后状态完全核对，B=1/最多32帧分块，必须由⑧提供资源租约和能抛出拒绝的scope检查函数。
- `REFERENCE_REGISTRY.json`、`read_only_example.py`：旧数据只读示例；`RESOURCE_BUDGET.json`、`AUTORUNNER_ADAPTER.json`：预算、现有⑧键和最小插件接入要求。
- `TEST_RESULTS.json`、`DELIVERY_MANIFEST.json`：实际CPU验证与文件SHA。`tests_r1/failure.json`保留首次短输入校验开发失败；修复后`tests_r2/result.json`42项PASS。

无需安装，现有WSL只读查看609旧Full：

```powershell
wsl -d FlyVisCPU -- /opt/flyvis-gpu-venv/bin/python /mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-gpu-validation/t4t5_decoder_support_20261011/read_only_example.py --reference camera609_Full
```

同一命令将reference改为 `G2_edge0_180_Full` 或 `edge0_180_decoder_preview` 可查看旧四条件数据。此操作返回 `accepted_cache_replay`，无新神经/decoder计算。

受⑧管理的未来Python调用入口：

```python
# 8先验证完整身份/有效scope并取得其GPU锁，配置CUDA0/deterministic/TF32关闭。
# 本目录加入sys.path；check_scope(operation)须在过期/冲突/身份变化时抛异常。
from service import OfficialDecoderService
decoder = OfficialDecoderService(model_path, contract_path,
                                 device="cuda:0", check_scope=window_check)
flow = decoder.decode(saved_full_spatial_activity, chunk_frames=32)
# 阳性控制：仅复制输入送decoder，不更改神经轨迹。
mask_flow = decoder.decode(saved_full_spatial_activity, chunk_frames=32,
                          mask_types=("T4a","T4b","T4c","T4d",
                                      "T5a","T5b","T5c","T5d"),
                          mask_start_step=200)
decoder.assert_weights_unchanged()
```

上述GPU示例**未执行**。Full单步继续复用原 `fly/gpu_phase2/full_oracle.py::FullNetworkOracle.step(old_full,hex_frame)` / `assert_weights_unchanged()`；caller传入明确a[k]及721帧，返回a[k+1]，不自动灰适应。④现提供自己的 `InterventionAdapter` 包裹该核心；本线只核对公开方法，实际GPU绑定仍需烟测。Full与干预使用独立标记，不将被干预对象当作原Full。

## 缓存范围、预算与精确依赖

609缓存是 `[1,609,45669]`，使用GPU灰适应a0哈希 `4e09f6…`。G2旧完整Full是 `[4,485,45669]`，只覆盖原sample0/1/12/13（OFF/ON的0°/180°），使用CPU共同a0 `e1ca6d…`。旧decoder preview也只覆盖0°/180°，但没有封存全部decoder输入/a0，不能冒充新的严格G2读出基准。本轮CPU仅只读核验这些文件及原验收。

④新四条件原sample **5/17/6/18 = ON60/ON240/OFF90/OFF270** 的冻结输入逐字节一致。它们的完整空间Full缓存目前 **MISS**；已有24条件中心65结果无法供decoder推理。必须在获授权的对应新研究窗口补这四条件Full，不需重复609。

④预注册v1计划6神经模式×4×485=11,640更新，另7读出模式共13,580帧；完整轨迹原始约1.98GiB，全部flow约74.7MiB，建议存储预算4GiB、启动前空闲8GiB。串行B1/T32的显存500–1500MiB、计算60–180s为规划估计，尚未实测；旧整批decoder曾累计保留约7,978MiB，不能直接用于新串行配置的承诺。没有HexEye任务。

④提出18:05–18:20 CST研究窗口，**用户未批准**。A本轮不启动任何GPU任务，既有摄像头旧窗及旧90分钟授权不适用于新研究；文档不签发排他资源租约。⑥优先，⑧须核验冲突和scope。

下一项由④/⑧提供：将④的 `InterventionAdapter` 与本decoder接口接入单一Runner，绑定v1预注册身份和新的runtime sidecar；⑧当前validate只允许609/no-ablation/decoder-disabled，需以插件扩展，不能伪报已经支持。获得对应短窗后，先做实际原网络hook和decoder分块烟测，核验eval/状态不变/有限值/分块数值；通过再执行已批准四条件先导。无需再次跑609或全量CPU。

本任务复用了既有 `flyvis-decoder-inference` Skill。新单位与坐标判断已由官方源码和小CPU探针验证，暂写入本交付合同；本轮没有实际复现新GPU分块，未新建通用GPU Skill，亦不声明PL闭环通过。
