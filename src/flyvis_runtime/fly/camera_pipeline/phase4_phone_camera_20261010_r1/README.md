# 第四阶段：手机交互刺激 → Windows 相机重拍

本目录是摄像头输入工作线的独立准备包。复用已验收的 `camera_pipeline/capture.py` 和 `adapter.py`；不开发第二个采集器，不改 GUI、GPU、RTL、权重、动力学或 Golden Reference。

**当前只完成软件准备和离线验证。还没有拍摄本阶段真实手机输入，也没有对新输入运行神经网络。用户完成手机摆放并明确确认前，执行者不得打开摄像头。** 摄像头脚本还设置了确认参数门槛；脚本参数不能代替用户的实际授权。

标准 A 固定：原始相机尺寸、官方 BoxEye(extent=15,kernel_size=13)、Pillow RGB→L/255、mean filter、721 点、无镜像/旋转/裁剪/缩放、因果 ZOH、dt=0.005s。没有使用方案 B。手机页逻辑画面按手机视口显示，这是被相机拍摄的外部刺激呈现，不是相机预处理的几何变换；实际视口和 canvas 尺寸另存播放日志。

## 手机播放

电脑与手机连接同一可信局域网。本服务无需安装手机 App。仅提供三个刺激静态文件和两种日志接口，没有目录浏览、录制数据下载或摄像头接口。不要配置公网端口转发；启动后终端保留，结束按 Ctrl+C 停止。若 Windows 询问网络访问，操作员仅对本次可信私有网络作决定；本包不会修改防火墙。

PowerShell：

```powershell
$flyCameraPython = 'C:\Users\hzy72\Documents\ChatGPT\fly\.venv\Scripts\python.exe'
$phoneCameraLane = 'C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\phase4_phone_camera_20261010_r1'
& $flyCameraPython "$phoneCameraLane\serve_phone.py" --bind 0.0.0.0 --port 8766
```

启动输出包含带临时 token 的 URL。电脑用 `http://127.0.0.1:8766/?token=...`；手机将 `PC_IPV4` 替换为电脑当前局域网 IPv4。手机连不上时先检查 Wi-Fi 隔离、地址和私有网络访问；不要关闭防火墙或开启公网暴露来绕过问题。`--validation-only` 只供软件测试，正式摄像头录制会拒绝这类会话。

可改变的刺激：

- ON/OFF 边缘：右、右下、下、左下、左、左上、上、右上。方向以画面坐标定义，0°向右、90°向下。OFF 为已越过区域由白变黑，ON 相反。
- 黑点：自动按方向移动，或手指拖动。拖动坐标和客户端时间记录在日志中；手、反光或触摸遮挡也会成为真实相机输入，必须检查原始录制。
- 明暗闪烁：0.25–4Hz，每周期两次明暗转换。
- 全画面亮度渐变：黑→白→黑；空间灰阶渐变移动：正弦灰度条纹，支持方向、速度和周期。
- 速度 1–1200 逻辑像素/秒，变化时间 0.5–20秒；前后各保持1秒。过快或过长可能使边缘/黑点离开画面，是实际呈现行为，不是隐藏重置。正式总录制最长30秒，至少覆盖本次刺激的前后保持和操作余量。

每次点“准备本次刺激”产生新手机会话；修改参数会使旧准备状态失效。先点“全屏待机”，待电脑开始录制后轻触刺激画面开始。画面内部没有文字，运动结束后持续保持最后一帧，**电脑结束录制后才点“返回参数”**。浏览器系统全屏不可用时使用固定视口画面；必须在实际手机上确认校准和正式呈现的画面位置一致。竖屏固定方向方便将返回按钮放在正方形画面外；若没有足够外部空间，该按钮隐藏，可用浏览器退出全屏操作返回。

## 手机摆放、曝光与视场

1. 固定手机位置、竖屏方向和屏幕亮度。可关闭的自动亮度、色温、夜间模式等由操作员检查并记录；未知设置不能写成“已关闭”。屏幕不要自动锁定。摄像头和手机屏幕尽量平行，避免反光、手部遮挡和明显摩尔纹。
2. 手机点“查看校准画面”。使用与正式播放一致的全屏/固定视口布局。8级灰阶从左到右变亮，左上1个白标记，右上2个黑标记，可观察镜像和方向。校准画面不进入正式神经比较。
3. 用户确认手机已摆放、允许开摄像头后，才运行下面的预览命令。默认640×480原图的实际721个13×13窗口范围为 x119..521、y39..441，正方形外接范围403×403。需要**有效刺激正方形**覆盖全部绿色窗口，不是仅手机外壳覆盖。
4. 在预览原图上按顺序点击有效画面的四角：左上、右上、右下、左下。C清空标记，Q/Esc结束。保存的 `placement_check.json` 包含四角、全部采样窗口是否在画面内、相机属性读回、灰阶统计和最后原图/叠加图。
5. 人工检查灰阶排序、暗亮区可分辨、焦点稳定、水平/垂直条纹、自动曝光在明暗切换后是否持续补偿。纯黑白内容的饱和像素比例本身不是失败判据。读回的 exposure/auto_exposure/gain/white balance/focus 是后端值，0也可能表示不支持；**不据通用数值宣布曝光已经锁定**。
6. 默认不额外修改曝光/自动曝光属性。若驱动已经确认具体编码，可显式使用 `--auto-exposure-value`、`--exposure-value`，脚本记录请求、set返回值、读回值；其物理含义仍须实际验证。无法锁定时如实保留自动模式，将其影响作为解释范围。

```powershell
# 仅在用户明确确认之后运行；8秒有界预览，不开始神经推理。
& $flyCameraPython "$phoneCameraLane\camera_session.py" preview --phone-ready-confirmed --device 0 --seconds 8
```

预览只用于摆放：保存最后原帧及叠加图、所有预览帧的统计与接收时间；没有归档全部预览像素。正式录制才保存每一帧原始像素。预览结束会释放相机；随后录制继续使用同一受锁保护的采集模块。GUI不能另开OpenCV采集器；不在Windows/WSL同时开USB相机。

## 录制和冻结新输入

录制器要求手机仍处于已准备/待机状态；已经开始播放的会话须重新准备。录制秒数至少等于前保持+变化+后保持+2秒操作余量，例如默认2秒运动需要至少6秒录制。人手启动仍可能延迟超过余量，实际是否覆盖完整播放必须复核原始录像；不根据要求时长自动宣布合格。

让评委选择本次参数，点“准备本次刺激”，记下手机会话路径，进入全屏待机。将下面占位符替换为实际会话路径和预览检查中的8个原图坐标，不能照抄示例坐标或虚构屏幕覆盖。

```powershell
# PHONE_SESSION_PATH：phone_sessions\<本次会话>\presentation.json
# X1 Y1 ... X4 Y4：实际预览得到的四角；用户已授权录制且人工复核覆盖后使用。
& $flyCameraPython "$phoneCameraLane\camera_session.py" record --phone-ready-confirmed --screen-coverage-confirmed --phone-session PHONE_SESSION_PATH --screen-corners X1 Y1 X2 Y2 X3 Y3 X4 Y4 --device 0 --seconds 8 --notes '填写手机亮度/方向/曝光检查及现场条件'
```

电脑提示 Recording now 后轻触手机画面。完成后保持手机不动、不要先返回参数页。电脑自动到时或Q结束，再退出手机播放。录制时绿色叠加仅显示，保存的PNG和frames.npy从未加点/文字。默认8秒、640×480、30FPS请求，原始 BGR 数组约211MiB，加上PNG、AVI等另需磁盘空间；实际帧数/FPS由交付时间测量，不能假定30FPS。

新目录 `recordings/camera_<UUID>/` 自动生成，禁止覆盖。里面有无损PNG、`frames.npy`、真实`frame_times.npy`和UTC/单调时钟CSV、AVI、原始录制元数据、逐帧灰阶统计、定期相机属性、手机初始参数快照、`capture_binding.json`及哈希。失败时保留root recorder的失败状态/已保存帧；`capture_requests/`记录发起参数。相机读取时间是host receipt，不是传感器曝光时间。

先重放**本次录制**检查方向、屏幕覆盖、条纹、手部遮挡及完整播放是否确实被拍到。AVI是有损等FPS预览，模型像素/时间权威为原始PNG/frames.npy和frame_times.npy。

```powershell
& $flyCameraPython 'C:\Users\hzy72\Documents\ChatGPT\fly\camera_pipeline\camera_test.py' replay --video '本次录制目录\clip.avi'
& $flyCameraPython "$phoneCameraLane\prepare_capture.py" '本次录制目录' --capture-reviewed
```

冻结器核对原始文件、全部PNG、源时钟、手机已完成的参数日志，调用原已验收的BoxEye适配器；输出新 `inputs/input_<UUID>/`：`stimulus.npy [1,N,1,721] float32 [0,1]`、`time.npy`、`source_hex.npy`、`source_time.npy`、坐标CSV、`metadata.json`、`activity_time.npy`、三时钟对齐CSV、provenance、`INPUT_IDENTITY.json`和manifest。

N从真实最后一帧接收时间得到，5ms输入网格不超过最后实测帧；不补时长、不用未来帧、不默认截断为800步。每个输入步实际选择最近已到达721值；源接收时间、input time、更新后activity time=t+dt逐步列明。手机客户端performance时间和服务器收件时间只用于播放诊断，不能据此把相机光学帧强行对齐；光学延迟未知为null。

手机会话只有 `presentation_id=phone_<UUID>` 和 `comparison_id=null`。相机重拍的 `capture_id=comparison_id=camera_<另一个UUID>`，冻结后的input_id又独立。直接手机动画和相机重拍绝不会共用comparison_id；已有P0固定800步输入完全保留。

## 后端和GUI

详见 [BACKEND_CONTRACT.md](BACKEND_CONTRACT.md) 和 [现场流程](DEMO_FLOW.md)。当前只交付输入，三个计算模式状态均not_run，activity_path=null。A①“FlyVis GPU · 视觉实验”负责原Full GPU；B④“FlyVis · 神经回路移植”负责67节点T5c Python Replacement及一致性分析；未来C⑥负责真实板卡模式。

A/B必须在这份新的冻结输入上建立共同初态、展开参数、节点表、数值配置和运行身份，按同一个N完成实际计算。不重新预处理、不独立做每块warmup、不读取旧动画活动。沿用已验收的独立实验初始化方案；改变初始化/截段策略需先说明并选择。⑥未提供本次真实板卡日志前，FPGA一直not_run。

Python输入接口 `handoff.load_input(folder)` 返回identity、只读输入、input_time、activity_time；`read_step(folder,i)` 返回三个时钟/721值及明确空activity。后端可用 `check_backend_identity(folder,result_manifest)` 检查新身份和时钟/模型/结果文件，但它只检查契约，不代替A/B数值验收或⑥真实板卡证据。GUI需正式接收新schema后使用；本线不修改其代码，不传送原始录像。

## 软件验证命令

```powershell
& $flyCameraPython "$phoneCameraLane\test_preparation.py"
node "$phoneCameraLane\test_renderer.js"
& $flyCameraPython "$phoneCameraLane\validate_delivery.py"
```

测试只包含本机回环服务、合成测试像素和协议检查，不开USB摄像头、不跑神经GPU、不访问板卡。详见 `validation/`、`acceptance.json` 和 `STATUS.md`。物理手机浏览器、屏幕曝光/频闪、正式新录制→冻结→Full/Python→GUI完整流程仍需要本次真实拍摄后验收。可复用经验是“独立呈现/采集身份、三个时钟、确认门槛”；目前没有把尚未实拍验证的流程声明为通用硬件Skill。
