# 六条件黑白视频 → 原始 Full FlyVis

目录：`C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\controlled_video_20261010_r1`。
素材来源为用户提供的 `fly/artifacts/controlled_visual_animation_20261010_142528`，只读校验并复制到本目录。
本实验是**合成视频文件输入**；未打开摄像头。源文件、第一阶段和完整状态验证阶段的封存包均保留原哈希。

## 输入与模型

六个独立640×640、60FPS、4秒短片，按静止/OFF右/OFF左/ON右/ON左/明暗切换排序。
官方原尺寸BoxEye(15,13,mean)，官方Pillow灰度策略，float32/255；没有裁剪、缩放、填边、镜像或旋转。
MP4压缩造成的实际像素变化保留，不重新二值化或每帧归一化。

冻结共享输入：`input/stimulus.npy [6,800,1,721] float32`。
每条件另有标准单样本目录 `inputs/<condition_id>/`，包含 stimulus.npy、time.npy、721坐标和metadata。
`decoded_frames/` 保存1440张解码后无损PNG和带哈希的帧索引，避免后续GUI/不同模式重复解码或预处理。
首次审核失败后已生成的输入被复用，未重新计算；后续各模式消费同一份冻结输入字节。

源时钟是经过解码PTS检查的60Hz文件呈现时间，不是实收UTC或曝光时刻。
已知CFR最后一帧在[239/60,4)持续显示；实际ZOH输入为0..3.995秒共800步，更新后活动为0.005..4.000秒。
真实摄像头末帧不采用这一文件时长扩展策略。24秒合集只作媒体演示；本实验六条件分别重置到共同初态。

原始flow/0000/000、45669节点/1513231边、dt=.005，权重和动力学保持原版。
`gpu_full_r1/initial_state_full.npy [1,45669]` 是一次原始1秒0.5灰度初始化后冻结的完整状态。
每条件都从同一份初态开始，无每条件warmup；r2新进程直接恢复初态再运行，活动与完整最终状态逐值相同。
只保存真实65类中心活动及T4/T5中心8类；完整最终状态另存，未把中心65类图冒充全脑空间活动。

## 文件入口与命令

```powershell
Set-Location C:\Users\hzy72\Documents\ChatGPT\fly
& .\.venv\Scripts\python.exe camera_pipeline\controlled_video_20261010_r1\test_protocol.py
& .\.venv\Scripts\python.exe camera_pipeline\controlled_video_20261010_r1\gui_handoff.py --verify camera_pipeline\controlled_video_20261010_r1\gui\experiment.json
& .\.venv\Scripts\python.exe camera_pipeline\controlled_video_20261010_r1\seal.py --verify
```

原始Full GPU复跑（先确认没有其他GPU重型实验，使用新的输出名，拒绝覆盖）：

```powershell
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/controlled_video_20261010_r1/run_gpu.sh gpu_full_NEW replay
```

该命令恢复已验收冻结初态，不重新预处理。既有WSL GPU解释器为`/opt/flyvis-gpu-venv/bin/python`，每次240秒上限。
本轮r1与r2均为独立进程新推理；作图和GUI读取是离线回放，不能冒充实时推理。
`prepare.py`是已执行的生成程序；输入已经冻结，不需再次运行。失败/恢复过程保留在logs。

## GUI 与未来四模式

[gui/experiment.json — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-098) 为经过读取验证的本地引用描述文件。
schema=`flyvis-controlled-video-experiment-v1`，dataset_type=`controlled_video_flyvis`，source_kind=`synthetic_controlled_video`。
`source_is_camera=false`，`source_received_utc`和`source_received_monotonic_ns`为null。
不改变现有真实摄像头或官方刺激入口，GUI须显式加入这一新类型，不能自动扫描目录后宣称验收。

```python
from camera_pipeline.controlled_video_20261010_r1.gui_handoff import load_experiment
experiment = load_experiment(r"C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\controlled_video_20261010_r1\gui\experiment.json")
metadata = experiment.describe()
step = experiment.read_step(sample=3, step=400)
# 实际PNG帧、721输入、65中心活动，同一输入索引；源/输入/更新后时间分别保留。
```

摄像头所有权仍属于原有CameraSession；上述API不创建采集器。
Full模式已有实际数据；Ablation/Python Replacement/FPGA Replacement继续unavailable。
未来模式必须共用描述文件指向的相同stimulus和initial_state_full的SHA256，不能各自重新预处理或改变初态。

## 解释边界

对每个条件报告0.5..1秒输入窗口的baseline，以及1..3秒窗口的原始峰/谷、baseline差值、RMS和峰时刻。
所有8类T4/T5及正负活动均保留。原始节点活动可为负，是模型单位，不是生物放电频率Hz。
左右/ON/OFF响应确实不同；整场明暗变化也产生响应，不能仅凭活动峰声称识别运动物体。
这不是官方角度空间MovingEdge等价实验，也不是12方向正式DSI、物理速度标定或完整光流验收。
实际屏幕拍摄将形成新的真实输入，必须单独记录相机设置、采样覆盖和实收时间，再冻结/验收。

[详细报告 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-099)、[验收 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-100)、[数据与时序审核 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-101)、
[全部六条件曲线 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-102)、[方向/极性对照 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-103)、
[采样范围 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-104)、[峰值和响应指标 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-105)、[文件清单 — 历史依赖未随包提供](../../../../../report/archive_dependencies.md#missing-106)。

输入审核纠错：边缘在运动开始前处于画面外，均匀画面不能用梯度argmax定位边缘。
现在先检查可见边界，再拟合位置；四个移动条件的图像边缘速度约±320.998px/s，721个位置的阈值穿越时序确认方向。
此流程保留为当前版本的脚本与测试，不创建或声称通用跨模型Skill。
