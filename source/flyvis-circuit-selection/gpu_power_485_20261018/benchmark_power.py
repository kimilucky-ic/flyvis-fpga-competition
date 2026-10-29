"""Bounded original FlyVis GPU benchmark; telemetry is a separate CPU process.

No upstream/RTL/board writes. All generated evidence lives next to this file.
"""
import argparse
import ctypes as C
import fcntl
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
FPGA = HERE.parents[1]
FLY = FPGA.parent / 'fly'
OLD = FPGA / 'flyvis-gpu-validation/artifacts/moving_edge_cuda_t1_r1'


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


class Value(C.Union):
    _fields_ = [('d', C.c_double), ('ui', C.c_uint), ('ul', C.c_ulong),
                ('ull', C.c_ulonglong), ('sll', C.c_longlong)]


class Field(C.Structure):
    _fields_ = [('fieldId', C.c_uint), ('scopeId', C.c_uint),
                ('timestamp', C.c_longlong), ('latencyUsec', C.c_longlong),
                ('valueType', C.c_int), ('nvmlReturn', C.c_int), ('value', Value)]


class NVML:
    def init__(self):
        self.lib = C.CDLL('/usr/lib/wsl/lib/libnvidia-ml.so.1')
        self.ok(self.lib.nvmlInit_v2())
        self.handle = C.c_void_p()
        self.ok(self.lib.nvmlDeviceGetHandleByIndex_v2(C.c_uint(0), C.byref(self.handle)))

    @staticmethod
    def ok(code):
        if code:
            raise RuntimeError('NVML return code ' + str(code))

    def sample(self):
        begin = time.monotonic_ns()
        fields = (Field * 2)()
        fields[0].fieldId, fields[1].fieldId = 185, 186
        code = self.lib.nvmlDeviceGetFieldValues(self.handle, 2, fields)
        powers = []
        for f in fields:
            # nvmlValueType: double=0, uint=1, ulong=2, ulonglong=3, longlong=4.
            attr = ['d', 'ui', 'ul', 'ull', 'sll'][f.valueType] if 0 <= f.valueType <= 4 else None
            powers.append(dict(field_id=int(f.fieldId), scope_id=int(f.scopeId),
                return_code=int(f.nvmlReturn) if code == 0 else code,
                sensor_timestamp_us=int(f.timestamp), latency_us=int(f.latencyUsec),
                value_type=int(f.valueType),
                watts=float(getattr(f.value, attr)) / 1000 if code == 0 and f.nvmlReturn == 0 and attr else None))
        legacy = C.c_uint()
        rc = self.lib.nvmlDeviceGetPowerUsage(self.handle, C.byref(legacy))
        temp, clock = C.c_uint(), C.c_uint()
        trc = self.lib.nvmlDeviceGetTemperature(self.handle, 0, C.byref(temp))
        crc = self.lib.nvmlDeviceGetClockInfo(self.handle, 0, C.byref(clock))
        energy = C.c_ulonglong()
        erc = self.lib.nvmlDeviceGetTotalEnergyConsumption(self.handle, C.byref(energy))
        end = time.monotonic_ns()
        return dict(request_begin_ns=begin, request_end_ns=end, midpoint_ns=(begin + end) // 2,
            epoch_ns=time.time_ns(), fields=powers,
            legacy_average_W=legacy.value / 1000 if rc == 0 else None, legacy_rc=rc,
            temperature_C=temp.value if trc == 0 else None,
            graphics_clock_MHz=clock.value if crc == 0 else None,
            energy_counter_mJ=energy.value if erc == 0 else None, energy_counter_rc=erc)

    def close(self):
        self.lib.nvmlShutdown()


def sample_process(stop, ready, dest):
    nvml = None
    try:
        nvml = NVML()
        first = nvml.sample()
        if first['fields'][1]['watts'] is None:
            raise RuntimeError('INSTANT_POWER_UNAVAILABLE: preserve evidence, no numerical substitution')
        with open(dest, 'x', encoding='utf-8') as stream:
            stream.write(json.dumps(first) + '\n'); stream.flush()
            ready.send(dict(status='READY', sample=first, pid=os.getpid()))
            deadline = time.monotonic() + .1
            started = time.monotonic()
            while not stop.wait(max(0, deadline - time.monotonic())):
                stream.write(json.dumps(nvml.sample()) + '\n'); stream.flush()
                deadline += .1
                if time.monotonic() - started > 360:
                    raise TimeoutError('SAMPLER_DEADLINE')
    except BaseException:
        error = traceback.format_exc()
        write('SAMPLER_FAILURE.json', dict(error=error))
        try:
            ready.send(dict(status='FAILED', error=error))
        except Exception:
            pass
        raise
    finally:
        if nvml:
            nvml.close()


def main():
    with (HERE / 'RUN_STARTED.json').open('x', encoding='utf-8') as f:
        json.dump(dict(pid=os.getpid(), epoch_ns=time.time_ns(), command=[sys.executable, *sys.argv]), f)
    plan = json.loads((HERE / 'PLAN.json').read_text())
    started = time.monotonic()
    runtime = FPGA / 'flyvis-autorunner/runtime'
    lock = (runtime / 'gpu.lock').open('a+')
    sampler = None
    stop = mp.get_context('spawn').Event()
    windows, rounds, warmups = [], [], []

    def check():
        if time.monotonic() - started > 300:
            raise TimeoutError('BENCHMARK_300_SECOND_CAP')
        if (HERE / 'STOP.json').exists():
            raise RuntimeError('STOP_REQUESTED')
        if sampler is not None and not sampler.is_alive():
            raise RuntimeError('SAMPLER_NOT_RUNNING')

    def cmd(argv):
        r = subprocess.run(argv, text=True, capture_output=True, timeout=15, check=True)
        return dict(argv=argv, stdout=r.stdout, stderr=r.stderr)

    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        markers = ['RESOURCE_QUARANTINE.json', 'EXTERNAL_GPU_BUSY.json', 'BOARD_RESERVED.json']
        assert not any((runtime / n).exists() for n in markers), 'SHARED_RESOURCE_RESERVED'
        probe = cmd(['/usr/lib/wsl/lib/nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'])
        assert not probe['stdout'].strip(), 'OTHER_GPU_COMPUTE_PROCESS: no interrupt/retry'
        preflight = dict(compute_probe=probe, smi=cmd(['/usr/lib/wsl/lib/nvidia-smi', '-q']),
            processes=cmd(['ps', '-eo', 'pid,comm,args']),
            source_status=cmd(['git', '-C', str(FLY / 'upstream/flyvis'), 'status', '--porcelain', '--untracked-files=no']),
            source_commit=cmd(['git', '-C', str(FLY / 'upstream/flyvis'), 'rev-parse', 'HEAD']))
        write('PREFLIGHT.json', preflight)
        assert preflight['source_commit']['stdout'].strip() == plan['source_commit']
        assert not preflight['source_status']['stdout'].strip()
        for rel, digest in plan['pins'].items():
            assert sha(FPGA / rel) == digest, 'PIN_MISMATCH ' + rel
        ctx = mp.get_context('spawn')
        parent, child = ctx.Pipe(duplex=False)
        sampler = ctx.Process(target=sample_process, args=(stop, child, str(HERE / 'POWER_RAW.jsonl')))
        sampler.start()
        assert parent.poll(10), 'SAMPLER_READY_TIMEOUT'
        ready = parent.recv(); write('SAMPLER_READY.json', ready)
        assert ready['status'] == 'READY'

        def idle(name, seconds):
            a = time.monotonic_ns()
            for _ in range(int(seconds * 10)):
                check(); time.sleep(.1)
            windows.append(dict(kind=name, start_ns=a, end_ns=time.monotonic_ns(), steps=0))
            write('WINDOWS.json', windows)
            print('IDLE_DONE', name, flush=True)

        idle('idle_before_context', 15)
        os.environ.update(CUDA_VISIBLE_DEVICES='0', CUBLAS_WORKSPACE_CONFIG=':4096:8',
            OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
            FLYVIS_ROOT_DIR='/opt/flyvis-gpu-data', MPLBACKEND='Agg', PYTHONDONTWRITEBYTECODE='1')
        import numpy as np
        import torch
        torch.set_num_threads(1); torch.set_num_interop_threads(1)
        torch.manual_seed(0); np.random.seed(0)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        import flyvis
        from flyvis import NetworkView
        assert flyvis.device.type == 'cuda'
        view = NetworkView('/opt/flyvis-gpu-data/results/flow/0000/000')
        checkpoint = Path(view.get_checkpoint('best'))
        assert sha(checkpoint) == plan['checkpoint_sha256']
        expected = torch.load(checkpoint, map_location='cpu', weights_only=False)['network']
        wrapper = view.network(checkpoint='best', lazy=True); wrapper.recover()
        net = wrapper.network
        assert (net.n_nodes, net.n_edges) == (45669, 1513231)
        assert type(net.dynamics).__name__ == 'PPNeuronIGRSynapses'
        assert not net._state_hooks

        def weights_equal():
            return set(net.state_dict()) == set(expected) and all(
                torch.equal(v.detach().cpu(), expected[k]) for k, v in net.state_dict().items())

        assert weights_equal()
        stimulus_np = np.load(OLD / 'stimulus.npy')
        reference = np.load(OLD / 'activity_central.npy')
        assert stimulus_np.shape == (1, 485, 1, 721) and stimulus_np.dtype == np.float32
        movie = torch.as_tensor(stimulus_np, device='cuda')
        initial = net.steady_state(1., .005, 1, value=.5)
        assert initial.nodes.activity.dtype == torch.float32
        initial_copy = initial.nodes.activity.clone()
        np.save(HERE / 'INITIAL_STATE.npy', initial_copy.cpu().numpy())
        assert all(v.dtype == torch.float32 for v in net.state_dict().values())
        central = net.connectome.central_cells_index[:]
        identity = dict(n_nodes=net.n_nodes, n_edges=net.n_edges, dt_s=.005, torch=torch.__version__,
            cuda=torch.version.cuda, flyvis=flyvis.__version__, gpu=torch.cuda.get_device_name(),
            checkpoint_sha256=sha(checkpoint), initial_state_sha256=sha(HERE / 'INITIAL_STATE.npy'),
            original_result=json.loads((OLD / 'result.json').read_text()),
            initial_preparation='official 200-step 1-second grey adaptation; outside 485-step timed windows',
            calculation='unchanged official Network.simulate -> forward -> _next_state, every target and edge',
            dtype='float32', TF32=False, deterministic=True, decoder=False,
            timed_scope='B1 485 real steps, input-buffer preparation and full GPU trajectory materialization; no rendering, disk IO, decoder, or host trajectory transfer',
            script_sha256=sha(__file__), shared_lock=str(runtime / 'gpu.lock'))
        write('IDENTITY.json', identity)
        print('MODEL_READY', json.dumps(dict(nodes=net.n_nodes, edges=net.n_edges)), flush=True)

        with torch.no_grad():
            for i in range(3):
                check(); torch.cuda.synchronize(); a = time.monotonic_ns()
                out = net.simulate(movie, .005, initial_state=initial)
                torch.cuda.synchronize(); b = time.monotonic_ns()
                got = out.detach().cpu().numpy()
                compare = dict(max_abs=float(np.max(np.abs(got[:, :, central] - reference))),
                    allclose=bool(np.allclose(got[:, :, central], reference, atol=1e-5, rtol=1e-5)))
                assert np.isfinite(got).all() and compare['allclose']
                warmups.append(dict(index=i, start_ns=a, end_ns=b, steps=485, central_comparison=compare))
                del out
            write('WARMUP.json', warmups)
            # Context-resident idle is the primary baseline. Model remains loaded.
            idle('idle_model_resident', 15)
            checks = []
            for group in range(3):
                check(); torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                events = []
                start = time.monotonic_ns()
                for r in range(12):
                    check()
                    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                    a = time.monotonic_ns(); e0.record()
                    out = net.simulate(movie, .005, initial_state=initial)
                    e1.record(); torch.cuda.synchronize(); b = time.monotonic_ns()
                    events.append((e0, e1))
                    rounds.append(dict(group=group, round=r, steps=485, start_ns=a, end_ns=b))
                    if r != 11:
                        del out
                end = time.monotonic_ns()
                windows.append(dict(kind='compute', group=group, start_ns=start, end_ns=end, steps=12*485,
                    cuda_event_total_ms=sum(a.elapsed_time(b) for a, b in events),
                    peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                    peak_reserved_bytes=torch.cuda.max_memory_reserved()))
                # Numerical/reference checks intentionally outside power/timing windows.
                got = out.detach().cpu().numpy()
                assert np.isfinite(got).all()
                delta = got[:, :, central] - reference
                assert np.allclose(got[:, :, central], reference, atol=1e-5, rtol=1e-5)
                checks.append(dict(group=group, all_finite=True, central_max_abs=float(np.abs(delta).max()),
                    all_full_trajectory_sha256=hashlib.sha256(got.tobytes()).hexdigest()))
                if group == 0:
                    np.save(HERE / 'TRAJECTORY_FULL.npy', got)
                del out
                write('WINDOWS.json', windows); write('ROUNDS.json', rounds)
                print('GROUP_DONE', group, 'seconds', (end-start)/1e9, 'steps', 12*485, flush=True)
            torch.cuda.synchronize()
            idle('idle_after_compute', 15)
        assert weights_equal() and torch.equal(initial.nodes.activity, initial_copy)
        assert all(v['all_full_trajectory_sha256'] == checks[0]['all_full_trajectory_sha256'] for v in checks)
        write('NUMERICAL_CHECK.json', dict(groups=checks, weights_unchanged=True, initial_unchanged=True,
            original_central_atol=1e-5, original_central_rtol=1e-5,
            all_3_last_round_full_trajectories_bitwise_equal=True))
        write('RUN_RESULT.json', dict(status='COMPLETE_REAL_GPU_BENCHMARK', measured_steps=17460,
            warmup_steps=1455, initial_adaptation_steps=200, measured_rounds=36,
            wall_s=time.monotonic()-started, GPU=True, FPGA=False,
            command=[sys.executable, *sys.argv]))
    except BaseException:
        write('FAILURE.json', dict(error=traceback.format_exc(), wall_s=time.monotonic()-started))
        raise
    finally:
        stop.set()
        if sampler:
            sampler.join(10)
            write('SAMPLER_EXIT.json', dict(pid=sampler.pid, exitcode=sampler.exitcode, alive=sampler.is_alive()))
        fcntl.flock(lock, fcntl.LOCK_UN); lock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', action='store_true')
    args = parser.parse_args()
    if args.probe:
        nvml = NVML()
        try:
            print(json.dumps(nvml.sample()))
        finally:
            nvml.close()
    else:
        main()
