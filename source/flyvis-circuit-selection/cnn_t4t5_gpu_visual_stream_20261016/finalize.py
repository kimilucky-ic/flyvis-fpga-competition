"""Summarize existing execution evidence and seal immutable delivery files.

No torch, neural inference, UI manipulation, or GPU operation.
"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(file):
    h = hashlib.sha256()
    with file.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


plan = load("PLAN.json")
audit = load("FINAL_AUDIT.json")
source = load("host/SOURCE_RESULT.json")
assert audit["status"] == "PASS_ACTUAL_GPU_AND_VISIBLE_VIDEO_COEXECUTION"
assert load("host/EXIT.json")["exit_code"] == 0
result = audit["CUDA_result"]
events = (HERE / "host/events.jsonl").read_bytes()
(HERE / "SEALED_EVENTS.jsonl").write_bytes(events)
rows = [json.loads(line) for line in events.splitlines()]
acks = [r for r in rows if r["kind"] == "BROWSER_RENDER_ACK" and r["visible"] and r["phase_when_received"] == "RUNNING"]
published = {r["render_id"]: r for r in rows if r["kind"] == "VISUAL_PUBLISHED"}
assert len(acks) == 100
for ack in acks:
    actual = published[ack["render_id"]]
    assert ack["steps"] == actual["steps"] and ack["host_monotonic"] >= actual["host_monotonic"]
milestones = {r["kind"]: r for r in rows if r["kind"] in ["GPU_READY", "VISUAL_STREAM_START", "SOURCE_COMPLETE", "GPU_COMPLETE", "WORKER_EXIT"]}
timing = dict(
    model_seconds=5.0,
    incremental_decode_and_two_backend_commits_s=source["wall_s"],
    model_steps_per_second_per_backend=1000 / source["wall_s"],
    source_frames_per_second=500 / source["wall_s"],
    rendered_updates_per_second=100 / source["wall_s"],
    speed_relative_to_model_time=5 / source["wall_s"],
    target_model_steps_per_second=100,
    strict_realtime_model_steps_per_second=200,
    CUDA_preload_s=milestones["GPU_READY"]["preload_s"],
    waiting_for_browser_start_s=milestones["VISUAL_STREAM_START"]["host_monotonic"] - milestones["GPU_READY"]["host_monotonic"],
    stream_plus_final_identity_and_flush_s=result["stream_wall_s"],
    post_source_until_worker_complete_s=milestones["GPU_COMPLETE"]["host_monotonic"] - milestones["SOURCE_COMPLETE"]["host_monotonic"],
    total_worker_s=result["total_worker_s"],
    notes="End-to-end dual-backend diagnostic with per-step CPU transfers, hashes, state writes, IPC and browser publication; not kernel-only speed or a production performance benchmark.",
)
save("UI_EVIDENCE.json", dict(run_id=plan["run_id"], running_visible_ack_count=len(acks),
    first_model_step=acks[0]["steps"], last_model_step=acks[-1]["steps"],
    all_ACK_steps_match_actual_publications=True, all_ACKs_after_publication=True,
    milestones=milestones, ACKs=acks,
    screenshot="COMPLETED_VIEW.jpg", screenshot_phase="COMPLETED_RESULT_REVIEW_NOT_RUNNING"))
save("TIMING.json", timing)
maximum = audit["numerical_CPU_comparison"]
report = f"""# GPU计算与视觉输入同步联调：实际执行通过

2026-10-16；④独立目录；run `{plan['run_id']}`。

本次实际接通受控MP4逐帧输入、原Full GPU与CNN Replacement GPU两条独立递推轨迹、官方DecoderGAVP和计算期间浏览器显示。最终状态 `{audit['status']}`。没有调用实体FPGA、摄像头，没有修改②正式GUI或⑦工程，没有训练或扩大CNN。

## 实际运行范围与闭环语义

- 输入为既有 `ON75_v12_full.mp4`，224×224、100fps、5秒、500帧，使用既有721点3×3均值采样。每帧因果保持2个5ms模型步，严格按frame_id 0…499、step_id 0…999前进，无丢帧、补帧或预录神经状态驱动。本片已用于CPU测试，本次是集成验证，不能重新称为未知刺激功能验证。
- 一个共享GPU锁、一个RTX 5060 Laptop GPU工作进程。Full和CNN分别保有自己的完整45,669节点状态；同一当前视频输入，CUDA计算在同一进程内顺序调用。并排显示/共同运行不等于两个CUDA内核并行。
- Full每步执行原始完整更新。CNN路径的39,901个R节点执行原规则，5,768个H节点由冻结31,168参数CNN计算；两部分均读自己这一条轨迹的旧状态，统一组成下一状态。CNN结果参与下一步R更新；Full状态不传入CNN。
- CNN路径运行时将三个Full/native更新入口置为报错护栏，原T4/T5更新调用0、teacher correction 0。两条轨迹各1000次真实提交。没有先算Full再覆盖CNN状态。
- 每10步分别调用官方DecoderGAVP，共各100帧光流。模型与decoder结束时参数/缓冲身份保持一致；同一CNN检查点，没有训练更新、静默CPU回退或板卡回退。

## 可见同步证据

`host/visual_001.json`…`visual_100.json`保存运行中实际发布的输入JPEG和两路新计算光流。浏览器在canvas绘制后经过两次动画帧回传ACK，服务端收到时检查仍处于RUNNING。实际获得100个可见ACK，覆盖模型第10…1000步，100个不同显示编号；每个ACK的步号与实际发布步号一致，时间不早于发布。

实际浏览器观察过第900步的运行画面，随后确认第1000步完成页。交付截图 `COMPLETED_VIEW.jpg` 是完成后的实际结果页，页面明确显示“当前为结果回看，GPU已退出”，不能当作运行中录屏。`SEALED_EVENTS.jsonl`和`UI_EVIDENCE.json`封存计算期间同步证据。显示是约10模型步一次，未声称展示每个5ms状态或无延迟屏幕采集。

## 保存结果核对

本次仅运行一次GPU推理。随后只读取保存数据执行一次 `audit.py`，审计新增神经步0。

- 1000×721实际解码输入与GPU收到输入、既有CPU基准输入逐位一致。
- 各1000×45,669状态均完成自身旧态→新态哈希链、时间与frame_id核对。
- Full GPU对同片CPU Full：全节点最大绝对误差 {maximum['Full']['state_max_abs']:.9g}；100帧官方光流最大绝对误差 {maximum['Full']['flow_max_abs']:.9g}。
- CNN GPU对同片CPU CNN：全节点最大绝对误差 {maximum['CNN']['state_max_abs']:.9g}；100帧官方光流最大绝对误差 {maximum['CNN']['flow_max_abs']:.9g}。
- 固定容差 `abs(delta) <= 1e-5 + 1e-5*abs(CPU_reference)`，两模式状态及光流超限数均为0。CNN光流最大绝对误差略大于单独atol，但满足预先固定的含rtol判据。
- 上述是GPU与各自CPU结果一致性，不是CNN与原Full逐位等价，也不是新增方向准确率结论。此前MP4批次运动7/8、静止1/2的两项失败仍保留，本轮没有解决移动背景前景误差或静止纹理偏移。

## 时间、资源与退出

- 500源帧解码、两条轨迹各1000步并发布结果：{source['wall_s']:.3f}秒；每条轨迹{timing['model_steps_per_second_per_backend']:.2f}模型步/秒，约{timing['speed_relative_to_model_time']:.3f}倍模型时间速度。两条轨迹都在这段时间完成，不能把两者计数相加作为单模型帧率。
- 原目标100模型步/秒也没有达到；dt=5ms严格实时需要200模型步/秒。本次证明同步联通，不证明实时视频处理。
- CUDA模型和decoder预加载{timing['CUDA_preload_s']:.3f}秒；GPU就绪后等待浏览器开始{timing['waiting_for_browser_start_s']:.3f}秒。worker的stream_wall_s={result['stream_wall_s']:.3f}秒还包含源帧结束后的参数身份检查和文件收尾；总worker {result['total_worker_s']:.3f}秒包含加载及等待。不得混用这三个时间口径。
- PyTorch峰值allocated {result['peak_allocated_bytes']/2**20:.2f}MiB、reserved {result['peak_reserved_bytes']/2**20:.2f}MiB，仅为本进程PyTorch统计，不等于整机显存占用。
- GPU工作进程退出码0，CUDA同步完成，共享lease已释放。临时localhost只读查看服务从创建起最多600秒，完成后不再触发GPU；端口58352过期后截图和原始数据仍有效。

## 身份、入口与后续边界

`PLAN.json` SHA256 `{digest(HERE/'PLAN.json')}`，固定25份模型/源码/输入/CPU基准文件。CNN `ridge.pt` SHA256 `{plan['pins'][plan['assets']['CNN_weights']]}`。原始网络参数、共同初态、节点顺序、5ms与官方decoder合同沿用并检查。

`viewer.py`是隔离联调入口；`worker.py`负责单共享锁CUDA推理；`audit.py`只核查本次保存数据；`reproduce.txt`写明不可覆盖本次结果及重新使用GPU前的资源检查要求。`DELIVERY_MANIFEST.json`封存交付文件；仍可追加浏览器回看ACK的 `host/events.jsonl` 不参与静态清单，以 `SEALED_EVENTS.jsonl` 为截止快照。

本轮到此停止。⑦实体FPGA尚未结合；已有共同H节点/时间语义可复用，但⑦原Euler硬件不能通过加载CNN参数执行本CNN。后续若进行真实GPU–FPGA实验，仍须单独确认具体后端、板卡身份/占用及授权，不以这次GPU视觉联动代替板级证据。若继续当前软件集成，下一项应单独界定单后端视频吞吐和交互输入范围，再决定是否接正式GUI。

复用了项目 `flyvis-gpu-reference` 与 `flyvis-decoder-inference` 工作流。本次新增实现只在本线目录；未创建通用Skill，未宣称跨环境复用通过。
"""
(HERE / "REPORT.md").write_text(report, encoding="utf-8")
(HERE / "reproduce.txt").write_text("""Evidence-only (no GPU, existing completed run):
  python -B flyvis-circuit-selection\\cnn_t4t5_gpu_visual_stream_20261016\\audit.py

Do not rerun viewer.py in this completed directory. It deliberately refuses if host/ exists.
For a separately authorized new execution, create a NEW owned directory and run identity,
resource/lease checks and prepare a NEW run_id/PLAN; preserve all results here. The original
call was Windows python -B ...\\viewer.py, which launches FlyVisCPU WSL CUDA Python
/opt/flyvis-gpu-venv/bin/python and a one-shot localhost page with the actual start button.
No GPU step is started by audit.py/finalize.py. Do not load a bitstream or access a board.

The temporary localhost page expires after 600 seconds. COMPLETED_VIEW.jpg and
SEALED_EVENTS.jsonl/UI_EVIDENCE.json remain the permanent display evidence.
""", encoding="utf-8")
manifest_files = []
for file in sorted(HERE.rglob("*")):
    relative = file.relative_to(HERE).as_posix()
    if not file.is_file() or relative in ["DELIVERY_MANIFEST.json", "host/events.jsonl"]:
        continue
    manifest_files.append(dict(path=relative, bytes=file.stat().st_size, sha256=digest(file)))
save("DELIVERY_MANIFEST.json", dict(run_id=plan["run_id"], evidence="ACTUAL_CUDA_AND_VISIBLE_VIDEO_COEXECUTION",
    file_count=len(manifest_files), total_bytes=sum(x["bytes"] for x in manifest_files), files=manifest_files,
    excluded=["DELIVERY_MANIFEST.json (self)", "host/events.jsonl (temporary viewer appendable; immutable cutoff SEALED_EVENTS.jsonl included)"]))
print(json.dumps(dict(status=audit["status"], files=len(manifest_files),
    bytes=sum(x["bytes"] for x in manifest_files), manifest_sha256=digest(HERE/"DELIVERY_MANIFEST.json"), timing=timing), indent=2))
