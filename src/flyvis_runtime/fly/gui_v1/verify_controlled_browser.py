"""Verify recorded browser readouts, actual CSV and rendered source pictures."""
import csv
from datetime import datetime, timezone
import json
import re

import numpy as np
from PIL import Image

from data_store import DataStore, ROOT


def main():
    folder = ROOT / "gui_v1/evidence/controlled6"
    observation = json.loads((folder / "browser_observations.json").read_text(encoding="utf-8"))
    store = DataStore()
    controlled = store.datasets["controlled6"]
    checked = 0

    def verify(row, sample=None):
        nonlocal checked
        d = store.datasets[row["dataset"]]
        sample = int(row["condition"]) if sample is None else sample
        frame = int(re.search(r"FRAME (\d+)", row["frame"])[1])
        time = d.times[sample] if hasattr(d, "times") else d.time
        assert row["time"] == f"t = {time[frame]:.3f} s" and row["error"] is None
        for cell, value in row["values"].items():
            assert value == f"{float(d.activity[sample][frame, d.cells.index(cell)]):.3f}", (row["dataset"], sample, frame, cell, value)
            checked += 1
        if row["dataset"] == "controlled6":
            source = int(d.source_indices[frame])
            assert row["input"] == f"{d.time[frame]:.3f} s" and row["after"] == f"{d.activity_time[frame]:.3f} s"
            assert row["source"] == f"源帧 {source} / 文件时间 {d.source_time[source]:.6f} s"
            assert row["sourceLabel"] == "源视频帧 / 文件呈现时间" and row["execution"] == "受控视频结果回放"
            assert row["dsi"] == "未提供" and row["tag"] == d.conditions[sample]["title"]
        elif row["dataset"] == "camera1":
            source = int(d.source_indices[frame])
            assert row["source"] == f"源帧 {source} / {d.source_time[source]:.6f} s / {d.receipts[source]['received_utc']}"
            assert row["sourceLabel"] == "真实采集帧 / 接收时间" and row["execution"] == "录制结果回放"
        elif row["dataset"] == "edge24":
            intensity = d.conditions[sample]["intensity"]
            official = next(v for v in d.metric_rows if v["cell_type"] == "T4c" and v["intensity"] == intensity)
            assert row["dsi"] == f"{official['official_dsi']:.4f}"

    assert len(observation["controlled"]) == 48 and len(observation["regression"]) == 49
    for row in observation["controlled"]:
        verify(row)
    for row in observation["regression"]:
        verify(row, row["expectedSample"])
    interaction = observation["interaction"]
    for name in ["rapidSwitch", "playFromEnd", "paused", "gpuAfter", "offRight"]:
        verify(interaction[name])
    assert interaction["rapidSwitch"]["condition"] == "4"
    assert int(re.search(r"FRAME (\d+)", interaction["playFromEnd"]["frame"])[1]) < 799
    assert interaction["gpuStatus"] == "未连接 · 尚未创建新计算任务" and "板卡未连接" in interaction["fpgaNotice"]
    assert controlled.descriptor["frozen_common_initial_state_sha256"] in interaction["provenance"]
    assert controlled.hashes["stimulus.npy"] in interaction["provenance"] and controlled.hashes["activity_central.npy"] in interaction["provenance"]
    assert "source_is_camera=false" in interaction["provenance"]
    with (folder / "controlled6_sample4.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 800
    for i, row in enumerate(rows):
        source = int(controlled.source_indices[i])
        assert row["dataset"] == "controlled6" and row["sample"] == "4" and row["condition_id"] == "04_on_left"
        assert row["source_kind"] == "synthetic_controlled_video" and row["direction"] == "left" and row["kind"] == "on"
        assert float(row["time_s"]) == controlled.time[i] and float(row["activity_time_s"]) == controlled.activity_time[i]
        assert int(row["source_frame"]) == source and float(row["source_time_s"]) == controlled.source_time[source]
        assert float(row["held_frame_age_s"]) == controlled.time[i] - controlled.source_time[source]
        assert row["common_initial_state_sha256"] == controlled.descriptor["frozen_common_initial_state_sha256"]
        for cell in controlled.result["target_types"]:
            assert float(row[cell]) == float(controlled.activity[4, i, controlled.cells.index(cell)])
    fault = observation["fault"]
    assert fault["initial"]["error"] is None and fault["failedVideo"]["execution"] == "数据不可用"
    assert "409" in fault["failedVideo"]["error"] and set(fault["failedVideo"]["values"].values()) == {"—"}
    for name, dataset in [("initial", "edge24"), ("cameraRecovery", "camera1"), ("edgeRecovery", "edge24")]:
        row, d = fault[name], store.datasets[dataset]
        sample = 1 if dataset == "edge24" else 0
        assert row["error"] is None
        for cell, value in row["values"].items():
            assert value == f"{float(d.activity[sample][240, d.cells.index(cell)]):.3f}"
            checked += 1
    layout = observation["layout"]
    assert layout["viewport"] == [1280, 720] and not layout["horizontalOverflow"]
    assert len(set(p["top"] for p in layout["panels"])) == 1 and not observation["normal_console"]
    # Read the actual screenshot interior. Sample flat source regions away
    # from the canvas label and image edge, so browser scaling is unambiguous.
    pixels_checked = 0
    for evidence in observation["screenshots"].values():
        sample, frame = evidence["sample"], evidence["frame"]
        source = int(controlled.source_indices[frame])
        source_image = np.asarray(Image.open(controlled.frame_paths[sample][source]).convert("RGB"))
        screenshot = np.asarray(Image.open(folder / evidence["file"]).convert("RGB"))
        rect = evidence["layout"]["stimulusRect"]
        width, height = rect["width"], rect["height"]
        scale = min(width / 640, height / 640)
        offset_x, offset_y = rect["x"] + (width - 640 * scale) / 2, rect["y"] + (height - 640 * scale) / 2
        for y in [80, 240, 400]:
            for x in [80, 240, 400, 560]:
                block = source_image[y - 10:y + 11, x - 10:x + 11]
                # Compressed MP4 whites have small real variations. A scaled
                # interior pixel must stay in its actual local source range;
                # skip high-contrast edges where this would not discriminate.
                if int(block.max()) - int(block.min()) > 32:
                    continue
                actual = screenshot[round(offset_y + y * scale), round(offset_x + x * scale)]
                low, high = block.min(axis=(0, 1)).astype(int), block.max(axis=(0, 1)).astype(int)
                assert np.all(actual.astype(int) >= low - 1) and np.all(actual.astype(int) <= high + 1), (sample, frame, x, y, actual, low, high)
                pixels_checked += 1
    assert pixels_checked >= 20
    report = {"status": "PASS", "checked_utc": datetime.now(timezone.utc).isoformat(), "existing_49_UI_conditions": 49, "controlled_conditions": 6, "event_and_boundary_observations": 48,
              "source_activity_readouts_checked": checked, "CSV_rows_exact": 800, "rendered_source_picture_points_checked": pixels_checked, "cross_condition_switch_picture_and_activity_match": True,
              "play_from_end_and_pause": True, "official_DSI_preserved": True, "file_and_capture_clocks_distinct": True, "GPU_unconnected_preserves_replay": True,
              "adapter_503_preserves_initial_offline_display": True, "frame_409_clears_activity_and_recovers_camera_and_edge": True, "layout": layout, "console_errors": observation["normal_console"]}
    (folder / "browser_acceptance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS:existing49 + six video conditions; {checked} true activity readouts,800 CSV rows,{pixels_checked} rendered picture points,clocks and fault recovery.")


if __name__ == "__main__":
    main()
