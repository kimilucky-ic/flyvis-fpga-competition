# 摄像头 / FlyVis 视觉输入模块

第一轮在 2026-10-10 已通过：Windows 真实摄像头采集与回放、官方 BoxEye 721 点输入、四方向合成边缘映射、5 ms 时间重采样、真实视频原完整 FlyVis GPU 推理及独立 CPU/GPU 复算。

唯一实现目录为本目录。GUI、神经回路提取、RTL、其他实验和既有 Golden 均保持独立。只在 Windows 打开摄像头。没有重新训练或修改权重/神经动力学。连续实时模式仍未验收。

- [当前状态](STATUS.md)
- [接口契约](API_CONTRACT.md)
- [完整验收报告](results/validation/REPORT.md)、[机器验收](results/validation/acceptance.json)
- [GUI 交接身份](results/validation/gui_handoff.json)、[文件校验清单](results/validation/manifest.json)
- [采样范围叠加](results/real_camera_native_zoh_r1/camera_receptor_overlay.png)、[真实六边形输入](results/real_camera_native_zoh_r1/hex_input.png)
- [四方向映射](results/direction_mapping_validation/result.json)、[方向图](results/direction_mapping_validation/direction_validation.png)
- [真实视频 T4/T5 曲线](results/real_camera_gpu_zoh_r1/activity_T4_T5.png)、[重采样影响](results/validation/temporal_effect.png)

## 已验证环境

Windows 用现有 `fly/.venv/Scripts/python.exe`：Python3.12.14、NumPy1.26.4、torch2.5.1+cpu、torchvision0.20.1+cpu。OpenCV4.10.0.84 隔离到 `camera_pipeline/_vendor`，不修改共享虚拟环境。标准视觉预处理运行CPU。

GPU 用既有 WSL `FlyVisCPU`：`/opt/flyvis-gpu-venv/bin/python`、torch2.7.1+cu128、RTX5060 Laptop；CPU复算用 `/opt/flyvis-venv/bin/python`。原 checkpoint 从 `/opt/flyvis-gpu-data/results/flow/0000/000` 只读复制到每个进程独立Linux原生临时缓存，所有持久结果写回本目录。该临时缓存不作为新数据或Golden。固定官方源码commit `92b3845cc426dd309a1a0e1b3890156c42e14021`。

## Windows 操作

在 `C:\Users\hzy72\Documents\ChatGPT\fly` 中运行。已有环境本轮已经安装OpenCV；无需重复安装。新环境可执行 `camera_pipeline/setup_camera.ps1`。所有新的录制和结果目录必须未存在，已有资料不会被覆盖。

```powershell
$cameraPython = '.\.venv\Scripts\python.exe'
& $cameraPython camera_pipeline/camera_test.py scan --max-devices 4
& $cameraPython camera_pipeline/camera_test.py preview --device 0 --seconds 10
& $cameraPython camera_pipeline/camera_test.py record --device 0 --seconds 6 --preview --output camera_pipeline/recordings/new_clip_01
& $cameraPython camera_pipeline/camera_test.py replay --video camera_pipeline/recordings/new_clip_01/clip.avi
```

预览按Q/Esc停止。录制可以不带 `--preview`。`--width/--height/--fps` 是摄像头协商请求，实际结果必须看日志/recording.json，不保证驱动接受。默认DirectShow；若当前驱动不支持，可以显式 `--backend msmf`。按测得可用编号选择，不把USB PnP名称当作固定OpenCV编号。

录制包含无损PNG、精确BGR `frames.npy`、实测 `frame_times.npy`、带UTC/单调纳秒时间的 `frame_timestamps.csv`、MJPG回放AVI、配置/哈希和任务状态。AVI有损且固定播放FPS；转换优先使用原始录制目录，避免用AVI替代原始像素和时间戳。

## 官方映射与导出

用户确认标准A：摄像头原尺寸、Pillow RGB→L /255、原始 `BoxEye(15,13,mean)`；不裁剪/缩放/镜像/旋转。图像小于官方最小391×391时标准模式直接报错，避免官方内部自动缩放未被察觉。当前640×480无需内部尺寸转换，所有实际13×13采样窗口均落在原图内部。原始位置、官方u/v、显示坐标、实际处理参数都已导出。

```powershell
& $cameraPython camera_pipeline/convert_video.py camera_pipeline/recordings/new_clip_01 camera_pipeline/results/new_native_zoh_01 --spatial-policy native --method zoh
& $cameraPython camera_pipeline/visualize_hex.py camera_pipeline/results/new_native_zoh_01
& $cameraPython camera_pipeline/resample_recorded.py camera_pipeline/results/new_native_zoh_01 camera_pipeline/results/new_native_linear_01 --method linear
```

标准输出 `stimulus.npy` 为float32 `[sample,frame,1,721]`，范围 `[0,1]`；`time.npy` 为秒、步长0.005；`input_hex_coordinates.csv` 保留固定顺序；`metadata.json`记录配置和哈希。额外保留来源帧六边形值、来源真实时间和每步对应表、原始绝对接收时间。

`full-field` 保留方案B：整图等比例缩放到417×417内、0.5灰填边，再真实执行BoxEye。该配置已做独立静态/范围正确性检查；不作为标准A，也没有参与本轮神经活动比较。

ZOH使用最近已到达帧；linear仅离线，明确使用相邻未来帧。都重新生成1202个真实输入时间步，没有只改时间戳。空间图依据官方 `hex_to_pixel`；摄像头图像行向下、官方显示y向上，与镜像/图像翻转不同。

## 完整模型 GPU 对接

先完成输入验证并确认没有其他GPU重型实验。启动的是原完整模型，一段视频连续运行，只在片段开始前初始化一次。保存中心65类神经元及T4/T5中心8类，未运行解码器。该离线入口不声明实时服务。

```powershell
wsl -d FlyVisCPU -- bash /mnt/c/Users/hzy72/Documents/ChatGPT/fly/camera_pipeline/run_gpu.sh new_native_zoh_01 new_gpu_zoh_01
```

GPU推理任务状态在结果目录 `gpu_status.json`，包含job_id和queued/running/complete/failed；结果身份在 `result.json`，包含设备、原模型/checkpoint/输入/输出SHA256、节点边数、前后权重一致性和同步计时。`activity_central.npy` 的轴为 `[sample,frame,central_cell_type]`，`cell_types.npy`/`neurons.csv`与最后一轴对应。`time.npy`是输入呈现时间，`activity_time.npy=time+dt`是Euler更新后活动时间。`time_alignment.csv`仍指向真实录像帧。

CPU对照可调用同一 `gpu_infer.py --device cpu`，使用既有CPU解释器。不得同时运行GPU重型任务，也不得把独立窗口结果拼成连续神经状态。连续分块/状态保存、端到端延迟与实时采集GPU测试留待后续阶段。

## 验证与故障

```powershell
& $cameraPython camera_pipeline/test_pipeline.py
& $cameraPython camera_pipeline/seal_manifest.py --verify
```

六个检查覆盖官方灰度/独立区域平均、已有Golden坐标顺序、官方分批渲染一致、禁止隐藏缩放、声明的填边变换、不规则时间的ZOH因果性与真正插值、无效时间拒绝。独立方向验证脚本 `validate_directions.py` 使用新的结果目录；首次已完成，重跑前需将脚本结果名改为新的编号，不能覆盖现有方向资料。

无设备或权限冲突会产生CAMERA_UNAVAILABLE；同模块已有会话会产生CAMERA_BUSY。`runtime/camera.lock`记录占用PID。先关闭所属会话；若进程被硬中断，确认该PID已退出后再由用户清理遗留锁。不要终止其他窗口的摄像头或GPU进程。摄像头断连/读取失败时保留已采原始PNG和失败状态。所有异常/纠错日志保留，不把错误诊断或合成数据当作真实摄像头验收。

官方依据：[自定义刺激教程](https://turagalab.github.io/flyvis/examples/07_flyvision_providing_custom_stimuli/)、[固定版BoxEye/HexEye源码](https://github.com/TuragaLab/flyvis/blob/92b3845cc426dd309a1a0e1b3890156c42e14021/flyvis/datasets/rendering/eye.py)、[固定版灰度入口](https://github.com/TuragaLab/flyvis/blob/92b3845cc426dd309a1a0e1b3890156c42e14021/flyvis/datasets/sintel_utils.py)。BoxEye是官方自定义自然图像方法；HexEye的六边形区域平均/官方刺激渲染与本路径数值不等价。这里不声称摄像头FOV/物理速度或完整光流已经标定。
