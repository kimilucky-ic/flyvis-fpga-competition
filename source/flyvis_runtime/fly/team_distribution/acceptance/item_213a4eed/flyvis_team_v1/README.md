# FlyVis 队友运行包 v1.0.0

这是一个不需要 ChatGPT、Codex 或开发机原目录的实验包。你可以独立运行原版 FlyVis 官方预训练网络，得到真实的神经活动和展示数据。默认使用 CPU，有合适的 NVIDIA GPU 时可切换 CUDA。

**先解压整个 ZIP，再运行脚本。不要直接在压缩包窗口内双击。** 中文和带空格的解压路径支持；尽量选择自己有写入权限的普通文件夹。

不安装环境也可以先打开 `examples/` 查看三种实验的真实示例曲线和 Flash 展示 JSON。`examples/` 是随包示例；新的推理结果会单独写入 `outputs/`。

## 第一次使用：Windows + WSL2

前置环境是 Windows 的 **WSL2 Ubuntu 24.04 / Python 3.12**。本包不包含 Ubuntu 系统盘或 Python 虚拟环境。

如果电脑没有 Ubuntu，在管理员 PowerShell 中运行：

```powershell
wsl --install -d Ubuntu-24.04
```

按 Windows 提示重启，打开 Ubuntu，完成它自己的用户名和密码设置。然后在 Ubuntu 窗口中运行一次：

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip
```

已有合适的 WSL2 Ubuntu 时可以跳过上述安装。启动脚本自动寻找 Ubuntu / Python 3.12，不要求发行版叫某个固定名字。若装了多个环境，可在 `config.json` 的 `wsl_distribution` 中填你要用的名字；空字符串表示自动发现。

回到解压后的 Windows 文件夹，依次双击：

1. **`setup.bat`**：首次安装 CPU 环境及依赖，校验和加载随包的官方权重。需要联网下载 Python 依赖；耗时取决于网络，可能需要数分钟。安装成功后显示 `ENVIRONMENT PASS`。后续无需重复安装。
2. **`check_environment.bat`**：检查 Python、模型身份、权重和实际运行设备。GPU 模式还执行实际 CUDA 运算。
3. **`run_flash.bat`**：四组闪光刺激，导出 65 类中心神经元和 T4/T5 活动。
4. **`run_moving_edge.bat`**：0° / 180°，ON / OFF，两方向四组条件。

首次安装需要网络。安装完成后，以上实验使用随包源码、权重和刺激，可以离线运行。

## 更多已实现的实验

- **`run_motion_directions.bat`**：0° 到 330°、每隔 30°，ON / OFF，共 24 组移动边缘条件。
- **`run_moving_bar.bat`**：移动条纹，0° / 90° / 180° / 270°、两种亮度，共八组。条宽 2，条高 9，速度 19。速度单位为官方参数的 half ommatidia/s，不是像素/s。
- **`run_cpu_golden_edge.bat`**：专门复算原 CPU Golden Reference 的 0° / 180° 两组 ON 输入，固定使用 CPU。这与上面的 ON/OFF 完整边缘输入来源分别记录。

所有入口使用 **dt = 0.005 秒**。Flash 每组 600 帧，移动边缘和条纹每组 485 帧。每组推理前以灰度 0.5 初始化 1 秒，刺激自身另含 1 秒预刺激。输出时间轴为 `frame × dt − 1 秒`，活动值对应该帧 Euler 更新后的状态。

这些入口使用提前通过官方刺激生成器得到的固定输入帧，运行时重新加载官方权重并计算整个网络，不从参考活动文件读取运行结果。省去首次 HexEye 渲染，也不修改网络或模型。参考活动仅用于推理结束后的数值对照。Flash 的参考来自验收后的 CPU Golden Reference；完整移动边缘输入和对照来自独立 GPU 实验。GPU 与 CPU 生成的边缘输入不保证逐位相同，因此两套来源分别保存，不能把完整边缘对照宣称为原 CPU 两方向实验的逐位复算。

本包提供固定实验条件的推理入口。改速度、生成任意新刺激、完整 DSI 分析、光流解码、子回路边界提取和 FPGA 替代均不属于这个版本。

## 可选：使用 NVIDIA GPU

有支持 WSL CUDA 的 NVIDIA 驱动后，双击 **`setup_gpu.bat`**。它安装独立 CUDA 环境，不覆盖 CPU 环境；安装成功后将 `config.json` 的 `device` 改为 `cuda`。之后原来的运行按钮会使用 GPU。

该环境固定 PyTorch **2.7.1+cu128 / torchvision 0.22.1+cu128**，已在 RTX 5060 Laptop 上检查过实际运算和 FlyVis 推理。别的 GPU、驱动或云主机没有一并验收。CUDA 依赖下载与磁盘占用比 CPU 大很多；没有 GPU 时直接使用默认 CPU。

切回 CPU：在 `config.json` 中把 `device` 改为 `cpu`，或运行 `setup.bat`。可填 `auto`：已安装 GPU 环境且 CUDA 实际可用时用 GPU，否则使用 CPU。若未安装 GPU 环境则直接选择已安装的 CPU 环境。显式 `cuda` 模式失败时会报错并留下日志。

安装阶段所需磁盘空间请预留：CPU 环境约 2 GB，CUDA 环境约 8 GB，另加依赖下载缓存。磁盘紧张时只装 CPU。固定输入推理不构造 HexEye 的大型渲染张量，因此不要求队友有 8 GB 显存才能跑 CPU。

## 结果在哪里，给展示组哪些文件

每次运行在 **`outputs/<实验>_<设备>_<UTC时间>/`** 建立新目录，不覆盖上次结果。

- `T4_T5_traces.png`：八类目标神经元的真实活动曲线。
- `stimulus_frames.png`：输入刺激的几帧截图。
- `activity_T4_T5.csv` / `.npy`：T4a–d、T5a–d 八类活动。
- `activity_central.csv` / `.npy`：65 类中心神经元活动。
- `stimulus.npy`：本次使用的全部视觉输入，轴为 `[sample, frame, channel=1, hex_pixel=721]`。
- `time.npy`：以秒为单位的时间轴。`cell_types.npy` 与 `neurons.csv` 给出活动列、原网络节点索引及中心坐标。
- `samples.csv`：每个样本的方向、亮度等实验条件；亮度 1 表示 ON，0 表示 OFF，背景为 0.5。
- `demo_payload.json`：展示组可直接读取的八类活动；每个样本的活动轴为 `[frame, cell_type]`，时间和条件一并提供。
- `metadata.json`：实际设备、耗时、版本、源码 commit、权重校验、参考数值误差与 PASS/FAIL。
- `requirements-lock.txt` 与 `manifest.json`：本次依赖记录和输出校验和。

展示组可先拿 `demo_payload.json` 和两张 PNG；科研复核还应保留刺激、活动 NPY、条件表和 metadata。**活动单位是模型单位，可为负值，不是脉冲、Hz 或已标定毫伏。** 完整网络为 45,669 神经元、1,513,231 条连接；导出的是其 65 类中心节点，不表示只运行了 65 个神经元。

## 出错时

不要重复同时启动多个实验。包内串行锁会提示已有任务；它不控制包外其他实验进程。

启动窗口错误会保存在 `logs/`。把最近的日志和失败输出目录中的 `metadata.json` 交给负责软件的队友。

- 找不到 Ubuntu / Python 3.12：按首次使用步骤安装 Ubuntu-24.04，或检查 `config.json` 的发行版名称。
- 提示 WSL1：运行 `wsl --set-version "你的发行版名称" 2`。
- 缺少 `ensurepip` / `venv`：在 Ubuntu 内安装 `python3-venv`，再运行 setup。
- 安装下载失败：检查网络和 WSL 的网络连接，恢复后重新运行 setup。不要把其他人的虚拟环境拷进来。
- CUDA 不可用：先使用 `cpu`；GPU 环境检查需要实际计算通过，单看显卡列表不够。
- 包校验失败：重新解压 ZIP，避免修改 `fixtures/` 或 `vendor/`。`config.json` 可编辑。

模型和 HDF5 缓存在 Linux 自己的磁盘 `~/.local/share/flyvis-team-v1/`，输出留在解压文件夹。这样规避本项目已观察到的原生 Windows / 跨文件系统 HDF5 文件锁问题。如果需要换 Linux 缓存位置，可设置 `FLYVIS_TEAM_STATE` 到 Linux 原生目录；不要指向 `/mnt/c`。

启动器显式关闭 python-dotenv 的自动查找，避免误读解压位置父目录的其他项目 `.env`。设备选择由 `config.json` 或启动参数控制；本包不需要 `.env`。

## Linux 直接运行

Ubuntu 24.04 / Python 3.12 安装 `python3-venv` 后，在解压目录执行：

```bash
python3 scripts/bootstrap.py --action setup --device cpu
python3 scripts/bootstrap.py --action check --device cpu
python3 scripts/bootstrap.py --action flash --device cpu
python3 scripts/bootstrap.py --action moving_edge --device cpu
python3 scripts/bootstrap.py --action motion_directions --device cpu
python3 scripts/bootstrap.py --action moving_bar --device cpu
```

## 来源和验收

源码为官方 FlyVis 1.2.0，commit `92b3845cc426dd309a1a0e1b3890156c42e14021`。官方模型 `flow/0000/000` 的权重 SHA256、官方预训练 ZIP 的 SHA256 均在 `VERSION.json`。安装从本包的官方运行源码归档建立环境；不从 main 分支拉取可变版本。源码归档保留原始文件内容，构建时用 setuptools_scm 的版本覆盖参数补充 Git 归档缺少的版本信息。

官方仓库、论文署名、MIT 许可证和原始预训练归档的说明见 `third_party_notices.md` 和 `vendor/license-FlyVis.txt`。没有重新训练、改成 LIF、剪枝、改连接或设计 FPGA。这个包的证据等级是软件推理及数值对照。

实际安装、运行和迁移验收结果见 `ACCEPTANCE.md`。首次联网安装已在开发机 WSL 内新建的独立环境测试；这不等于所有队友电脑都已验收。
