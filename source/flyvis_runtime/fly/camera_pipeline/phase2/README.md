# FlyVis 摄像头第二阶段

工作根目录：`C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\phase2`。
更新于 2026-10-10。当前验收范围为**完整连续状态验证与真实录像 GUI 交接工具**。
用户本轮无法布置黑白卡片/另一块屏幕，已选择先完成这两项，受控真实视频与实时性能试验保留待办。

第一阶段的 324 个封存文件、API_CONTRACT.md、录像、输入、输出和 manifest 均未改写，保持 GUI 固定 SHA256 导入有效。
`camera_pipeline/STATUS.md` 是第一阶段封存快照；当前进展看本目录 [STATUS.md](STATUS.md)。
只更新 FPGA 仓库的摄像头工作线 checkpoint，不修改 GUI、GPU 实验、回路提取或 RTL 工作线的源码和状态文档。

## 已验收的完整状态

原始 `flow/0000/000`、FlyVis 1.2.0、固定源码 commit
`92b3845cc426dd309a1a0e1b3890156c42e14021`，checkpoint SHA256
`d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f`。
设备为既有 WSL `FlyVisCPU` 的 RTX 5060 Laptop GPU，PyTorch 2.7.1+cu128。

当前原始 `PPNeuronIGRSynapses` 的独立动态状态为 `nodes.activity [1,45669]`；`edges` 动态字段为空。
`sources.activity` 与 `targets.activity` 是节点状态按照全部 1,513,231 条边索引得到的派生视图。
保存全部独立字段、模型/拓扑/输入/坐标身份、dt 和下一步索引，恢复后由官方 `_state_api` 重建派生视图。
不能把 `network.state_dict()` 当作运行中的神经系统状态，也不能只保存 65 个中心节点。
适配器遇到其他动力学、额外状态字段、批量大小或不完整节点数会明确拒绝。

同一段第一阶段真实录像的原始 A/ZOH 输入，一次性连续运行 1202 步与
`1/36/91/201/183/265/247/178` 步的 8 个分块逐步逐节点相同，最大绝对误差 0，最终状态相同。
每个块都实际写入磁盘并恢复。另一个冷启动模型进程从第 1 步的 checkpoint 恢复，后续 1201 步也逐值相同。
初始灰度 0.5 适应 1 秒只执行一次；新进程与各分块均无额外 warmup。
一次性中央活动也与第一阶段已验收结果逐值相同，前后权重与模型 buffer 均保持原 checkpoint 数值。

详细证据：[state_validation.json](results/continuous_state_r2/state_validation.json)、
[逐步比较](results/continuous_state_r2/step_comparison.csv)、
[新进程逐步比较](results/continuous_state_r2/fresh_process_step_comparison.csv)、
[完整节点轨迹](results/continuous_state_r2/activity_all_nodes_monolithic.npy)。
完整节点轨迹约 219.6 MB；失败的 r1 证据保留，不删除或伪装为成功。

重跑必须使用一个新的结果名称，脚本拒绝覆盖已有目录：

```powershell
Set-Location C:\Users\hzy72\Documents\ChatGPT\fly
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/phase2/run_state_validation.sh continuous_state_NEW
```

运行前只读检查 GPU 无其他重型实验；该测试有 240 秒总超时和 120 秒恢复子进程超时。
所有持久结果在本目录；Linux HDF5 缓存使用该任务专属 `/tmp/flyvis-camera-phase2-*`。

## GUI 交接

正式本地描述文件：[experiment.json](results/gui_real_video_r1/experiment.json)，schema 为
`flyvis-camera-experiment-v2`，GUI 类型为 `recorded_camera_flyvis`。
描述文件是 21 个本地文件的只读引用及 SHA256/大小清单，不嵌入像素或活动序列，不上传视频。
它引用原来的真实录像、A/ZOH 输入、实际完整模型活动和本轮状态验收；条件明确为 `ordinary_real_scene`。

```python
from camera_pipeline.phase2.gui_handoff import load_experiment
experiment = load_experiment(r"C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\phase2\results\gui_real_video_r1\experiment.json")
status = experiment.describe()   # 元数据
frame = experiment.read_step(600)  # 本地读取，不获取摄像头
# frame['bgr']: 对应实收源帧；frame['hex_input']: 该输入步721值
# frame['activity_central']: 同一输入步更新后的65类中心活动
# frame['source_received_utc'], frame['source_received_monotonic_ns']
# frame['source_time_s'], frame['input_time_s'], frame['activity_time_s']
```

`load_experiment` 在返回数据前验证全部身份、数组范围和轴、细胞顺序、T4/T5 子集、
1202 个实际 ZOH 选择和输入值、输入/活动时间、原始验收与状态验证候选的一致性。
摄像头采集仍只由 `camera_pipeline.capture.CameraSession` 所有；此读取器不导入 OpenCV 或 FlyVis。

三个时间不能合并：

- 源帧：177 个真实实收时间，非均匀，0..6.0062629 秒；不是传感器曝光时间。
- 输入：1202 个 5 ms 时间步，0..6.005 秒，每步保持当时已到达的最近源帧。
- 活动：同一索引输入经过 Euler 更新后的状态，输入时间+0.005，0.005..6.010 秒。

例：第 600 步使用源帧 87，源时间 2.983640 秒，输入时间 3.000 秒，活动时间 3.005 秒。
不存在为适配旧 reader 而人为减去 1 秒的变换。离线播放不用 AVI 恒定帧率时间代替实测时间。

GUI 工作线已确认契约，并通过自己的第一阶段录像导入和本地 HTTP 校验；证据位于
`fly/gui_v1/evidence/phase2/import_acceptance.json`。该证据范围由 GUI 工作线负责。
GUI 当前仍明确锁定第一阶段 handoff；v2 描述文件不自动切换进入 GUI。
本轮摄像头工作线只发送接口路径与字段，未发送视频像素或活动数据，未修改 GUI 文件。

```powershell
& .\.venv\Scripts\python.exe camera_pipeline\phase2\gui_handoff.py verify camera_pipeline\phase2\results\gui_real_video_r1\experiment.json
& .\.venv\Scripts\python.exe camera_pipeline\phase2\test_handoff.py
& .\.venv\Scripts\python.exe camera_pipeline\phase2\test_state_contract.py
& .\.venv\Scripts\python.exe camera_pipeline\phase2\finalize_phase2.py
& .\.venv\Scripts\python.exe camera_pipeline\phase2\seal_phase2.py --verify
& .\.venv\Scripts\python.exe camera_pipeline\seal_manifest.py --verify
```

第一条读取命令独立进程已通过。6 个时序测试覆盖未来帧、错一帧、旧 -1 秒偏移、
实际输入值与延展边界错误；10 个状态测试覆盖模型/输入/坐标/dt/步号不匹配、缺字段、
新增未审核状态、截断节点、非有限值，以及真实已保存全状态。

## 时延与证据范围

本轮一次性 GPU 仿真 4.800500 秒，约 250.39 步/秒；分块 GPU 仿真合计 4.268560 秒，
约 281.59 步/秒，后者不含磁盘保存/恢复、对照计算及数据传输。
测试观察钩子还包含全节点非有限值检查。两项是离线单次计时，未做稳定吞吐统计；不能把差异解释为普遍的分块加速。
摄像头实测约 29.30 FPS、200 仿真步/秒和上述计算吞吐是不同量。
没有新增相机采集、BoxEye、重采样、输出队列或端到端实时延迟测量，本轮处理模式标为 `offline`。

受控物理实验待用户可以布置时再执行，继续使用唯一采集器与标准 A：
静止高对比、左/右高对比边缘、明暗切换，条件允许时上下移动。
每条件独立保存，固定相机位置/分辨率/光照，并记录曝光、自动曝光、白平衡、自动白平衡、
自动对焦、增益、亮度/对比/伽马/饱和度等后端可读控制值、设置返回值与回读结果。
后端不支持或语义无法验证的设置记为 unknown，不把原始数值当作自动处理关闭证明。
源图上保存实际721位置/13×13采样范围；不添加未记录缩放、镜像、旋转。
先从实际图像/721输入确认边缘运动方向、对比和明暗变化，再分析 T4/T5 的条件差异。
若视频未形成预期条件则记录未通过，不通过改权重或筛曲线补救。

## 修复与可复用范围

r1 的同进程磁盘分块已一致，但新进程在第二块报 `KeyError: sources`。
原因是官方 hook 位于 `_state_api` 构造 `sources/targets` 之前；只拿 hook 状态传给下一块不完整。
`simulate_block` 现在移除只读 hook 后调用原 `_state_api`，返回完整可连续传递状态。
r2 冷启动恢复及多块内存延续已独立验证，错误与修复证据保留在 [日志](logs/continuous_state_r1.log)。
此经验固化为本目录脚本和协议，只覆盖当前固定候选与版本，没有新增通用 Skill 或跨动力学支持声明。
