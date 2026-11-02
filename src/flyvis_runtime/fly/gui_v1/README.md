# FlyVis GUI v1 · 第二阶段

2026-10-10。在已验收的离线 GUI v1 上增加真实摄像头录制结果、独立十条件 MovingBar，以及用户授权的六条件合成受控视频。当前七套55条件，原界面、原38条件和此前49条件入口与验收文件保留。当前仍为真实计算结果回放；启动不加载 FlyVis、不运行 GPU、不打开摄像头或 FPGA。摄像头阶段见 [PHASE2.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-124)，最新六条件接入、独立初态和文件时间语义见 [CONTROLLED_VIDEO.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-125)。原实验、预训练权重和其他工作线源码保持只读。

## 双击桌面入口

第三阶段固定动画闭环交接已经增量接入：页面显示 `01_off_right` 冻结输入身份及本次三模式状态。已经独立验证并接入B正式交接的同身份800步Full/Python实际结果，页面按离线回放显示；FPGA继续unavailable。此状态不改变已有55条件的历史回放验收。只读接口、交接要求与当前证据范围见 [PHASE3.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-126)。

双击 `C:\Users\hzy72\Documents\ChatGPT\fly\FlyVis.exe`，即可打开独立Windows窗口，自动校验数据并启动自己的本机后台；关闭窗口时后台一起退出。原界面和七套55条件保留，桌面依赖位于GUI专属环境，不修改其他工作线。使用、恢复与验收范围见 [DESKTOP.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-127)。

## 原网页入口（一条命令启动）

在任意 PowerShell 工作目录执行：

```powershell
& 'C:\Users\hzy72\Documents\ChatGPT\fly\start_gui.ps1'
```

脚本使用已有 `fly/.venv/Scripts/python.exe`，自动打开 `http://127.0.0.1:8771`。前置要求为 Python 3.10+ 和 NumPy；本机已具备。无需 WSL、GPU、FPGA、互联网、前端构建或额外安装。保持这个终端运行；按 Ctrl+C 停止本次 GUI。

端口被占用时使用 `-Port 8772`；只启动服务、不打开系统浏览器时加 `-NoOpen`。也可以直接执行 `.venv/Scripts/python.exe gui_v1/server.py --port 8771`。

## 使用

1. 默认选择 24 条件 MovingEdge，ON、0°，停在 frame 240 / t=0.200 s，首屏可看到运动中的输入。开始播放、首帧、逐帧、循环和 0.25/0.5/1/2 倍回放均可用。
2. 选择 0°–330°（30°间隔）与 ON/OFF。条件对应原 `samples.csv`，不是重新渲染刺激。两个输入图直接读取同一帧的 721 个真实亮度。
3. T4/T5 八条曲线默认同时显示，游标和输入使用相同帧号。切到代表细胞 L1/L2/Mi1/Tm3，或在 65 类中心节点中搜索、多选。点击曲线或拖动时间滑块可定位；空格播放/暂停，左右方向键逐帧。
4. 方向区选择一个 T4/T5 细胞，最多同时比较四个方向的原始活动。极坐标图使用已验收的官方整流峰值；正式 DSI 和偏好方向只在指标身份匹配的 `edge24` 数据中显示。
5. 可切到 Flash Golden（全视野/中心半径6、ON/OFF）、MovingBar（四方向×ON/OFF）和最小 CPU MovingEdge（0/180、只有 ON）。不存在的条件不开放。
6. 曲线 CSV 导出包含实验、样本、方向、亮度、范围、帧号、原始时间及所选细胞数值。来源面板给出绝对路径、模型、权重 SHA256、数据 SHA256 和原始文件链接。

宽度达到 1200 px 时使用视觉输入 / 活动 / 方向三栏布局，主要图表同屏；较窄窗口自动改为两栏或单栏，运行信息紧随图表。

## 真实数据与语义

原38条件的精确来源仍由未改动的 [datasets.json — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-128) 指定，启动时验证对应 manifest 的所有文件：

- `edge24`：`team_distribution/acceptance/item_213a4eed/flyvis_team_v1/outputs/motion_directions_cuda_20261009t142329_684402z`，24×485 帧。
- `flash`：`artifacts/golden_reference_v1/flash`，4×600 帧。
- `bar`：`team_distribution/acceptance/item_213a4eed/flyvis_team_v1/outputs/moving_bar_cuda_20261009t142415_972483z`，8×485 帧。
- `minimal`：`artifacts/moving_edge_minimal_cpu_v1`，2×485 帧，只验收两个 ON 方向。

原四套数据共38个条件，加上一个真实摄像头录制条件和独立十条件 MovingBar，构成此前验收的49条件；本次新增六条件独立合成视频后共55条件。三套新增实验的固定路径和文档 SHA256 在 [integrations.json — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-129)，通过专用读取器验证后才加入目录；不扫描新文件夹。完整网络为 45,669 节点、1,513,231 连接；导出的活动为每类一个中心节点，共65类。活动是连续 `nodes.activity` 模型单位，可以为负，不是脉冲、Hz 或已标定毫伏。

原四套官方刺激的时间是 `frame × 0.005 − 1` 秒，保存的活动是对应输入帧 Euler 更新之后的状态。本 GUI 保留原记录的时间标签和逐帧配对，不添加一帧错位、不对活动做插值。屏幕刷新可能跳过显示帧，但定位使用真实帧号。200步/秒指模拟时间基准，回放倍率及绘图刷新率均不代表网络推理吞吐。

输入的灰度显示仅将保存的亮度映射到 0–255；左图是六边形采样的填充重建，右图显示采样单元。坐标采用原 `input_hex_coordinates.csv` 和官方 `hex_to_pixel(mode='default')`，翻转显示 y 以适应浏览器向下的屏幕坐标。没有生成新的刺激数据，也没有拿65个中心节点拼空间神经网络。

## 正式指标

读取另一个独立实验工作线已有的 `fpga/flyvis-visual-experiments/artifacts/analysis`，不修改它：

- `direction_metrics_T4_T5.csv`、`angular_peak_responses.csv`、`direction_analysis.json` 的 SHA256 已固定在配置中。
- 展示用活动 NPY 与 `golden_reference_v2/activity_central_gpu.npy` 的文件 SHA256 相同。
- 721输入按原分析的 float32 转换后逐位一致，时间、细胞顺序、方向/亮度/速度条件及权重身份匹配。
- 直接展示官方 `peak_responses`、`direction_selectivity_index` 和 `preferred_direction` 已验收结果。DSI 分母跨两种亮度取更大的角度峰值总和，不把双方向差异或自算统计量标为官方 DSI。
- 验收范围只有单个预训练模型、MovingEdge、speed=19 和完整12方向；不是模型集群或真实果蝇的生物学验证。

指标源缺失或身份不匹配时回放仍可运行，正式指标显示未提供。Flash、MovingBar和最小CPU条件不显示正式 DSI。

## 运行与后续集成边界

当前执行始终标为 `offline_replay`。原设备和历史整批 `inference_s` 来自 metadata；本次数据加载和回放墙钟时间独立记录。旧 Flash/最小CPU记录未单列推理时间时，显示未提供，不用其他计时替代。

GPU、摄像头和 FPGA 适配契约见 [API_CONTRACT.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-130)；协议定义见 [adapters.py](adapters.py)。当前没有执行适配器，相关 POST 返回503且结果为空。回路关闭、Python替换及FPGA替换只显示未验证/未连接，原网络曲线不会变成虚构替换结果。

摄像头唯一采集实现归 `camera_pipeline` 工作线；GUI 不创建第二个采集器。已按固定交接文件与清单导入其已验收的真实录制结果。选择“真实摄像头 · 录制结果”可播放无损原帧、721点输入与T4/T5，并分别显示实收帧时间、输入时间和 Euler 更新后时间。摄像头时间从0开始，活动时间为输入+0.005秒；不使用官方刺激的−1秒规则。标准 A 为原尺寸 BoxEye(15,13)和因果帧保持。在线采集及正式GPU服务未连接。

## 验证和交付文件

在 GUI 已运行时验证：

```powershell
& 'C:\Users\hzy72\Documents\ChatGPT\fly\.venv\Scripts\python.exe' 'C:\Users\hzy72\Documents\ChatGPT\fly\gui_v1\verify_gui.py'
```

[evidence/data_acceptance.json — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-131) 验证全部38条件的原始输入和活动二进制传输、方向曲线、正式指标、不可用适配器及文件访问范围；临时损坏清单会被拒绝，指标身份不匹配会隐藏正式指标。[evidence/csv_export_acceptance.json — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-132) 独立核对浏览器实际导出的485帧CSV与原始NPY。[evidence/browser_acceptance.json — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-133) 保存24条件交互检查、默认1280×720窗口的三栏同屏布局以及无控制台错误结果。[evidence/startup_acceptance.json — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-134) 记录从fpga目录独立启动的第二进程，四套数据验收和HTTP200通过。最终界面见 [evidence/gui_v1_desktop.jpg — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-135)。验收结束后测试服务已停止，用户运行启动命令即可建立自己的服务实例。

第一阶段原始交付新增：`viewer/index.html`、`viewer/styles.css`、`viewer/app.js`、`start_gui.ps1` 和 `gui_v1/`。未修改原 FlyVis 模型、实验脚本、Golden Reference、分发包、摄像头源码或其他工作线检查点。没有 Git 提交、外部发布、FPGA编程或新神经推理。

归属与许可沿用原实验和官方 FlyVis 的来源说明：[distribution notices — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-136)；原始模型和数据不因GUI展示而改变许可。

## 第二阶段新增操作与验收

- “MovingBar · 新十条件”通过完整参数选择，分别保留各条件原始时间轴（485或739帧），0.25/0.75亮度不标成ON/OFF。旧八条件入口保留。
- “提交当前固定输入”只调用预留GPU接口；服务未交付时明确返回未连接，不创建任务、不替换现有曲线。用户已确认 `gpu_phase2/r_only.py` 是闭环计算接口，不是GUI服务。
- Full可回放；Ablation、Python Replacement、FPGA Replacement继续unavailable。板卡、回路、误差、PL周期和各阶段延迟为null。
- 原38条件回归：`verify_gui.py --output gui_v1/evidence/phase2/offline_regression.json`。新增导入验收：`verify_phase2.py`（验证脚本使用本机已有Pillow解码PNG；启动服务仍只需要NumPy）。两者均先运行GUI服务，工作目录为fly。
- 摄像头与十条件MovingBar的历史验收在 [evidence/phase2 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-137)；本次六条件及旧49条件回归证据在 [evidence/controlled6 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-138)。旧验收JSON和图片保持原SHA256。可选导入损坏/缺失被隔离，原离线实验仍可启动。

## 第四阶段运行证据工作台

原七套55条件与P0软件对照保留，页面下方新增独立工作台：四模式、真实run/backend/模型身份、历史参考或COMMIT步骤、721输入和活动/误差、源日志及真实CSV。当前仅已验收Full/Python记录，全部标offline replay；Sham/Ablation、FPGA及新计算服务NOT_AVAILABLE，不创建虚拟任务。启动入口不变。

交付、实际验收和⑥/④/⑤精确交接要求见 [PHASE4.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-139)，GUI消费端格式及状态语义见 [WORKBENCH_CONTRACT.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-140)。真板准入目前锁定，须按⑥正式原报告另做独立验证；3D打包仍冻结。新增验收记录位于 [evidence/phase4 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-141)，旧证据不覆盖。

## 第四阶段统一输入流程（2026-10-11）

顶部“本次实验”把输入选择、冻结身份、四模式请求和证据查看接到同一页面。⑤原播放器按SHA校验后内嵌，保留原渲染器；数字预览与手机实际相机采集分别标识。当前能冻结P0真实输入引用、明确拒绝未连接的新任务，并查看同输入的原Full/Python结果。工作台可多选65中心细胞，原方向/DSI与55条件继续使用。

新交互动画的721导出、新手机采集和新计算服务尚未交付，因此预览不能冻结成新神经输入，摄像头/FPGA继续NOT_CONNECTED。未来采集/运行/失败状态与准确交接说明见 [UNIFIED_FLOW_CONTRACT.md — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-142)。新软件/浏览器和旧功能回归单独保存于 [evidence/phase4_unified_20261011 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-143)。入口仍为原start_gui.ps1；桌面exe沿用现有Python后端与viewer，无本轮新打包或原生窗口验收。
# 已验收科研先导可视化（2026-10-11）

原启动入口与55条件不变。页面顶部“查看 T4/T5 科研先导对照”跳至同页全宽科研区：ON60/OFF90五模式原光流、冻结721输入、同步步号、④保存的投影/幅度曲线和主窗口指标。所有新结果标记SOFTWARE_PILOT、offline replay，FPGA NOT_CONNECTED。

来源显式固定在scientific_pilot.json，校验原163文件清单与①decoder坐标/时间/分量契约；不能自动认领新目录。⑧已完成camera609任务按job/seal/summary/计时SHA只读显示，缓存Full与当次新Python运行分别标识。科研B未交付时不画数量—效果曲线。[接口与证据边界 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-144)，[本轮有限验收 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-145)，[实际浏览器核对 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-146)。仅新增GUI消费者/显示/测试，其他工作线源码及原始数据保持不变；3D打包仍冻结。

## 已完成科研 B 交互可视化（2026-10-12）

原8771/start_gui.ps1/桌面入口不变；点击顶部“查看科研 B 节点数量对照”进入原科研区新增部分。ON60/OFF90、0/488/1016/1736/2648/3752/5768实际集合：四图显示节点数—E、场角、M、Q；选择或点击规模后，同步查看冻结721输入、原Full、完整钳制失活和部分保留的原官方光流。模型步输入/滑块/离线播放共享双时间，原集合文件/global IDs/运行及数值SHA可追溯。

科研B按固定清单89文件及原参考只读核验，显示SOFTWARE_SPARSE_RETAIN / OFFLINE_REPLAY；当前FPGA NOT_CONNECTED。历史6790步/224.935s是已完成14例的整批GPU记录，不是GUI新运行。3752较接近Full，E仍约0.23，不称为板上或数值等价恢复。原55条件/P0/五模式先导/AutoRunner保持；无新GPU/decoder/训练/摄像头/板操作。详情见 [消费契约与下一步硬件要求 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-147)，[软件验收 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-148)、[有限实际浏览器验收 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-149)、[最终清单 — 历史依赖未随包提供](../../../../report/archive_dependencies.md#missing-150)。3D仍冻结，原生桌面本轮未重新验收。

