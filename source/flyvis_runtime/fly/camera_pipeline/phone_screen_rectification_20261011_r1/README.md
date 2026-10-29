# 手机屏幕录像：显式固定校正方案 B

2026-10-11 用户明确选择：电脑摄像头拍摄手机屏幕；从录像开头标定发光正方形，整段使用同一组裁剪、透视校正和重采样参数。历史标准 A（原尺寸/BoxEye15,13/无几何变换）和已冻结输入保持不变。本目录只交付独立 B 路径；不修改 GUI/GPU/RTL/原模型或权重，不占用板卡。

当前完成软件实现和两次独立软件验证。**本目录尚未接收本次用户实拍文件；不存在已验收的新实拍输入、神经曲线或 FPGA 结果。** 合成验证材料全部位于 validation，身份为 digital_rectB，不能作为摄像头证据。

## 最少操作：直接给录像

1. 手机继续使用原交互网页，OFF、向右、320、移动2秒，前后保持各1秒；“准备本次刺激”→“全屏待机”。录像开始前，整个白色发光正方形已经清楚位于镜头内。只需拍全发光正方形，手机机身不必完整入镜，也不必在原图中达到403×403。
2. 用 Windows 相机应用开始录像，再轻触手机播放。让手机固定不动，录完完整运动和最终黑画面，再保持1–2秒。第一条录8–12秒即可。不要改变位置来追随边缘。
3. 保留相机应用生成的原始视频，不转码、不裁剪。将本地文件路径交给本工作线。由本工作线完成开头白屏标定、整段复核和冻结，不要求用户填写坐标。

继续使用当前已启动的原手机页面；不另造播放器。普通 MP4 的时间依据是解码器报告的视频呈现时间，不能恢复系统相机没有导出的逐帧主机接收时刻、传感器曝光时刻或 UTC；这些字段明确为空。新输入有独立的 camera_rectB_* comparison_id，手机网页/原动画的数字身份与它不同。可将明确属于本次拍摄的原页面 presentation.json 和 events.jsonl 一并归档；没有对应日志时如实标记 missing，不从别的会话借用。

## 可选：自己掌握开始键，并保留真实接收时钟

在资源管理器双击 [record_phone_screen.cmd](record_phone_screen.cmd)，或者运行 [PowerShell入口](record_phone_screen.ps1)。先关闭 Windows 相机应用，保持唯一采集器。

预览打开后：

1. 手机白色正方形已完整、清楚地出现在画面中，保持固定。
2. 聚焦电脑预览窗口，按 **R**。预览等待不算正式录像。
3. 看到绿色 **RECORDING — TAP PHONE NOW** 后再轻触手机。提示出现前已经由原 capture.record_clip 保存第一张原始 PNG，不依赖聊天消息或进程启动速度。
4. 动画结束且保持最终画面后按 **Q**；也可等12秒上限自动结束。控制台打印保存目录。预览等待最多180秒，退出始终释放相机。

这个入口只包装已有 capture.open_camera/read_frame/record_clip；没有第二个 OpenCV 摄像头采集器，没有403像素覆盖门槛，也没有自动启动手机。原帧、frames.npy、接收时间戳 CSV/npy、属性读回、原页面播放日志（找到正确待机会话时）保存在 recordings/camera_*。新入口尚未进行真实硬件录制验收；用户实际运行后需要查看完整原始序列。此前首拍失败数据继续保留。

## 固定校正的实际行为

- 从录像开头稳定的白色发光正方形选取一个原始帧。自动亮区轮廓检测只提出候选；执行者查看原图后确定四角。标定的是**发光正方形**，不是手机外框，也不是页面上下灰色留白。
- 四点按屏幕逻辑左上、右上、右下、左下排列。计算一次 raw→640×640 的四点透视矩阵。原始四角、目标四角、正逆矩阵、标定帧索引及 SHA 全部记录。反射/交叉/退化点排列拒绝处理。
- 整段每一帧使用完全相同的矩阵和 OpenCV INTER_LINEAR。明确存在裁剪和几何重采样；没有每帧重新定位、运动跟踪、光流补偿、隐藏填边、亮度增强或归一化。源矩形视场被改变，不能与历史 A 曲线混作同一实验。
- 校正后640×640对应网页逻辑画布；官方 BoxEye(15,13)实际采样中间的六边形区域，13×13窗口的包围范围是403×403，占正方形边长403/640。它不会计算整块屏幕所有像素。原图反投影覆盖图显示实际721个中心和每个窗口，CSV保存浮点位置。
- BoxEye仍执行官方均值卷积和721六边形采样；RGB→Pillow L→float32/255沿用已有官方兼容方法。BoxEye采用 native，不再进行额外尺寸变换。官方卷积零边界行为如实记录；校正有效性检查保证实际采样窗口不使用原图外的零填充值。
- [sampling_overlay_raw.png](validation/software_01966e847d38403499deeb32b8605d2d/calibration/sampling_overlay_raw.png) 是**合成软件说明图**，黄色是屏幕边界，绿色是原图中的实际输入窗口；不是真实手机拍摄图。
- 放大只改善摆放便利性，不恢复缺失的细节、曝光信息或准确物理速度。手机显著移动、遮挡、失焦、屏幕不全、频闪都必须从实际原始片段检查并报告；固定校正不会自动解决这些问题。

上述四点透视与插值使用 [OpenCV 官方几何变换接口](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html)。文件时间戳来自 [CAP_PROP_POS_MSEC](https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html)，支持范围依赖实际解码后端；本环境4.10.0/FFMPEG在已知30FPS软件片段上核验通过，尚未验证用户实际文件或所有可变帧率编码。

## 执行者命令

```powershell
$py = 'C:\Users\hzy72\Documents\ChatGPT\fly\.venv\Scripts\python.exe'
$tool = 'C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\phone_screen_rectification_20261011_r1\screen_import.py'
# 所有输出必须为不存在的新目录；不会覆盖原数据。
& $py $tool ingest '实际相机视频.mp4或原录制目录' '新的source目录' --source-kind camera_recapture --provenance-note '实际拍摄来源说明'
# 有明确本次手机会话时，ingest可增加 --phone-session '本次presentation.json'，保留原日志。
& $py $tool calibrate '新的source目录' '新的calibration目录' --frame-index 0
# 检查候选、原图和实际方向后，可用 --corners xTL yTL xTR yTR xBR yBR xBL yBL 重新标定到另一个新目录。
& $py $tool freeze '新的source目录' '已检查calibration目录\calibration.json' '新的frozen目录' --reviewed --review-note '整段原录像、屏幕固定、四角方向和完整动画的实际检查结果'
```

ingest保存原始压缩文件及SHA、逐帧解码 PNG、frames.npy和解码后端/尺寸/方向属性/逐帧呈现时钟；原 recorder目录则校验并引用原始lossless数据，沿用真实接收时钟。缺失/重复/逆序时间戳拒绝处理，不默默套用30FPS。视频解码与模拟端均不按800步强制截断/延长。因果ZOH真正保持已出现的721强度直到下一源帧；只生成不晚于最后实际源帧的5ms输入网格，不补最后一帧时长。活动时钟为 input_time+0.005，初态a0另存。

每个 frozen/input 包含 stimulus.npy（[1,N,1,721] float32 [0,1]）、time.npy、activity_time.npy、source_time.npy、source_hex.npy、source_times.csv、input_hex_coordinates.csv、raw_sampling_coordinates.csv、calibration.json、sampling_overlay_raw.png、time_alignment.csv、three_clock_alignment.csv、metadata.json、INPUT_IDENTITY.json、manifest.json。其父目录保留精确 rectified_frames.npy 和整包封存。SOURCE和校正、原数据、派生数据均通过SHA引用；如有播放日志/属性快照则拷入provenance并封存。

## 最小对接 API

```python
from camera_pipeline.phone_screen_rectification_20261011_r1.screen_import import load_input
identity, stimulus, input_time, activity_time = load_input(frozen_input_directory)
# stimulus为只读float32[1,N,1,721]；activity_time == input_time + 0.005
```

沿用原摄像头open_camera/read_frame/record_clip API。新增B读取器严格区分方案和来源；旧A的phase4 handoff有不同schema，不能假称已兼容。①/④收到真实冻结输入后应使用上述读取器或核验同一manifest，建立同一个新 comparison_id、a0/完整45,669状态、展开参数/节点映射/数值配置，处理实际N步。后端活动仍使用统一full_gpu/python_replacement结果身份；FPGA未来另补实板证据。输入工作线不开发GPU或RTL，也不会用旧活动填充新实验。

## 验证及当前限制

[最新软件结果](validation/software_01966e847d38403499deeb32b8605d2d/result.json)：30项PASS；左右/上下已知OFF边缘、较小倾斜屏幕、721投影、反射/交叉/坏时钟拒绝、因果输入值、完整冻结/只读重复加载、三时钟、文件不伪造UTC。两次使用独立新目录复现。完整输出的合成片段shape为[1,107,1,721]，不是实拍、更不是新神经活动。

实际新摄像头视频、曝光/对焦/ISP状态、频闪、全段固定位置、对应手机日志以及Full GPU/Python对照都未验收。可复用软件流程已在独立输出上复现；自助录制硬件流程尚未运行，不发布为通用硬件Skill。
