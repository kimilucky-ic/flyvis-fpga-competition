# 第一条真实手机—电脑摄像头输入

2026-10-11。实际采集和离线视觉预处理验收通过，带拍摄质量限制。尚未执行本输入的神经网络或 FPGA 计算。

本目录属于⑤摄像头与视觉输入工作线。原始录像、原方案 A、预训练模型及 Golden Reference 均保留。

## 本次输入

电脑摄像头实际拍摄了 iPhone 上已有交互网页的 OFF 向右移动边缘。完整录像为640×480、351帧、12.0063139秒，实际帧交付速率29.15132845 FPS。手机日志为同一 armed session 的一次 start→complete，设置为 OFF、0°向右、320逻辑像素/秒、静止1秒+移动2秒+保持1秒。网页未成功进入全屏，但发光正方形已拍到。网页回调及服务器收到日志的时刻不是相机曝光时刻。

完整原始输入在：

`../recordings/camera_2dfba194ca2849a6802c22dc3e8f08d5/`

其中 lossless PNG / frames.npy 和 frame_timestamps.csv 是证据主体；CFR clip.avi 仅供回放。完整录像前段有手指遮挡、后段有手机移位。用户明确选择原帧100–190（两端包含），即3.4294444–6.4699407秒，91帧、跨度3.0404963秒；12秒原片未修改或删除。选段包含采样区由白变黑的边缘通过及最后暗保持，不是整个4秒手机播放。

## 固定空间变换和实际输入

按照用户新授权的方案 B，从原录像帧0的发光正方形确定 TL/TR/BR/BL 四角：`(312,177),(481,184),(479,358),(304,351)`。对整个选段复用同一个 raw→640×640 矩阵，采用 OpenCV INTER_LINEAR，然后官方 Pillow RGB.convert(L)/255 和原 BoxEye(15,13) mean 采样。无逐帧重定标、跟踪稳定、亮度增强、镜像或旋转。640画面足够大，官方 BoxEye 未再缩放；采样足迹没有使用原画面外的补边值。

`selected_calibration_initial_frame0/parent_calibration_reference.json` 是原帧0的标定证据，**不能作为可执行校准配置**。`selected_calibration/calibration.json` 使用选段的首帧作像素绑定，但显式继承原帧0四角坐标和完全相同的矩阵；不是重新寻找帧100手机四角。矩阵来源和两个帧号均可复查。

手机晃动留在输入中。诊断跟踪只评估采样足迹覆盖，不参与实际图像校正；估计选段91帧足迹均在发光正方形内，最少36个跟踪内点。这个估计不是精确光学校准。曝光读取为-6，自动曝光/对焦读数-1不能证明已锁定；自动白平衡读数1，物理曝光、频闪和 ISP 状态仍未完全验证。

标准 A 与本次 B 的几何意义不同，不能混作同一输入或与旧结果直接作数值差异结论。

冻结输入：`frozen_selected_100_190/input/`

- comparison_id：`camera_rectB_c5689ab635cc425ea672029502d0d402`
- stimulus.npy：float32 `[1,609,1,721]`，实际范围0.0844180584–0.9960783720。
- 原91帧接收时间：source_time.npy；保留原帧号、UTC和单调纳秒时间。
- time.npy：609个因果 ZOH 输入步，0–3.040秒，dt=0.005秒。
- activity_time.npy：每步更新后活动时间，0.005–3.045秒；末输入在真实选段范围内，末状态是最后一次5ms更新后的状态，不是额外采集帧。
- input_hex_coordinates.csv、raw_sampling_coordinates.csv、calibration.json、metadata.json、原始手机日志、INPUT_IDENTITY.json、manifest.json。

每步和完整原录像的关联见 `handoff_selected_100_190/original_frame_alignment.csv`。模拟时间重置到片段起点，但原接收时刻不变。神经实验需从一个新的共同 a0 开始；未运行整段12秒，因此不能声称恢复了原录像第100帧之前的神经状态。

## 实际验收与复查

`acceptance.json`：22项输入验收通过，包括全部91帧无损切片、同一矩阵逐帧复现、65,611个独立整数像素和/169/255与官方感受器输出的比较、609步因果值及原帧/三时钟对应、重复读回逐位一致。均值最大误差9.015314899e-7，低于已有非负float32求和理论上界1.025210037e-5；这不是修改刺激或模型以消除误差。

`selected_input_evidence.png` 显示4个原始帧采样叠加和对应721路输入。图上的显示裁剪不用于网络输入。721点半亮度跨越时刻与横坐标相关r=0.98606119，支持实际输入中的右向暗边缘通过；没有据此宣称神经方向选择性或物理速度。

`raw_quality_report.json` 和 `frame_quality.*` 保留最初整段审核，历史 pending 字段不代表本次选段最终状态；本次最终状态以 `acceptance.json` / `STATUS.md` 为准。历史 window_proposal.json 保留提案状态，实际用户授权在 selected_source_100_190/selection_authorization.json。

独立复查命令（PowerShell）：

```powershell
& 'C:\Users\hzy72\Documents\ChatGPT\fly\.venv\Scripts\python.exe' 'C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\phone_screen_rectification_20261011_r1\real_capture_review_camera_2dfba194_20261011_r1\verify_selected.py'
```

只验证已冻结内容，不重新预处理，复查结果写入新的 verification_runs/UUID 目录，不覆盖当前验收。acceptance.json的原验收脚本快照保存在 accepted_audit_source.py.txt，其SHA与报告一致。不要重跑 prepare_selected.py 去覆盖现有身份和产物；它故意拒绝已存在输出目录。

Windows及现有WSL只读加载已实际通过，见 [平台核验 — 历史依赖未随包提供](../../../../../../report/archive_dependencies.md#missing-121) 和 [消费者API — 历史依赖未随包提供](../../../../../../report/archive_dependencies.md#missing-122)。①/④交接消息已送达，[送达记录 — 历史依赖未随包提供](../../../../../../report/archive_dependencies.md#missing-123)；实际后端结果仍待返回。

完整原始录像仍本地保留。本线给①/④发送本地交接路径、哈希及计算要求，不传送原始视频数据。相机已释放，未使用⑥板卡。自助录制实际成功一次属于 observed / not independently reproduced；没有因此发布通用硬件 Skill。
