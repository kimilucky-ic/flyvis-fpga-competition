"""Integration boundaries. Offline v1 deliberately has no device implementation."""
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    execution_kind: Literal["offline_replay", "new_inference", "board_execution"]
    device: str
    model: str
    source_commit: str
    checkpoint_sha256: str
    input_sha256: str
    output_sha256: str
    simulated_dt_s: float
    elapsed_s: float


class GPUAdapter(Protocol):
    def status(self) -> dict: ...
    def submit(self, *, dataset_id: str, sample_ids: list[int], input_sha256: str) -> str: ...
    def poll(self, run_id: str) -> dict: ...
    def result(self, run_id: str) -> RunIdentity: ...


class AdapterUnavailable(RuntimeError):
    pass


class DisconnectedGPUAdapter:
    """Safe default until a service owner's formal contract is available."""
    def status(self):
        return {"status": "not_connected", "label": "GPU 服务未连接", "device": None, "current_run": None,
                "reason": "GPU 在线推理服务尚未交付；当前没有正式服务接口，未创建计算任务"}

    def submit(self, **request):
        raise AdapterUnavailable(self.status()["reason"])

    def poll(self, run_id):
        raise AdapterUnavailable(self.status()["reason"])

    def result(self, run_id):
        raise AdapterUnavailable(self.status()["reason"])


class CameraAdapter(Protocol):
    """Delegate exclusively to camera_pipeline; no second VideoCapture in GUI.

    Standard A is native BoxEye(15,13), with no resize/crop/mirror/rotation.
    The full-field policy is an explicit separate experiment, never a default.
    """
    def devices(self) -> list[dict]: ...
    def open_camera(self, device: int, *, backend: str = "dshow", width: int = 640, height: int = 480, fps: int = 30): ...
    def read_frame(self, camera): ...
    def record_clip(self, camera, output_directory: str, duration_s: float): ...
    def video_to_flyvis_stimulus(self, recording_id: str, *, spatial_policy: str = "native", method: str = "zoh", dt_s: float = 0.005): ...
    def save_stimulus(self, bundle, output_directory: str): ...


class ReplacementAdapter(Protocol):
    def status(self) -> dict: ...
    def compare(self, *, reference_run_id: str, replacement_run_id: str) -> dict: ...


def statuses(camera_imported=False) -> dict:
    return {
        "schema": "flyvis-adapters-v1",
        "execution_kind": "offline_replay",
        "gpu": DisconnectedGPUAdapter().status(),
        "camera": {"status": "verified_recorded_result" if camera_imported else "unavailable", "label": "已验证录制结果 / 采集器未开启" if camera_imported else "录制结果不可用", "devices": None, "fps": None},
        "modes": [
            {"id": "original", "name": "Full", "label": "原始完整网络", "available": True, "status": "verified_software_replay"},
            {"id": "disabled", "name": "Ablation", "label": "回路关闭", "available": False, "status": "unavailable"},
            {"id": "python", "name": "Python Replacement", "label": "Python 替换", "available": False, "status": "unavailable"},
            {"id": "fpga", "name": "FPGA Replacement", "label": "FPGA 替换", "available": False, "status": "unavailable"}
        ],
        "fpga": {"status": "not_connected", "label": "Zynq-7020 未连接 / 未验证", "bitstream_sha256": None,
                 "resources": None, "cycles": None, "communication_latency_ms": None, "error": None,
                 "board_identity": None, "device_identity": None, "clock_hz": None, "model_identity": None, "circuit_identity": None,
                 "activity_error": None, "pl_cycles": None,
                 "latency_ms": {"gpu_compute": None, "ps_compute": None, "pl_compute": None,
                                "gpu_ps_transfer": None, "ps_pl_transfer": None}, "acceptance_evidence_level": None},
        "comparison": {"reference": None, "replacement": None, "time_series_error": None,
                       "functional_metric_delta": None}
    }
