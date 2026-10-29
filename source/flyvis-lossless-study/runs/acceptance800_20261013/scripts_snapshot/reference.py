"""Pinned upstream CPU reference; the only replacement is connectome storage."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import numpy as np

COMMIT = "92b3845cc426dd309a1a0e1b3890156c42e14021"
GRAPH_SHA = "6779065467f70cef14e8f2f1005efd4830fd29c00795c103756a6af60607f825"
CHECKPOINT_SHA = "d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f"
N, E = 45669, 1513231


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_sources(fly_root):
    repo = fly_root / "upstream/flyvis"
    graph = repo / "flyvis/connectome/fib25-fib19_v2.2.json"
    checkpoint = fly_root / "data_cpu/results/flow/0000/000/chkpts/chkpt_00000"
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    assert head == COMMIT, head
    changed = subprocess.check_output(["git", "-C", str(repo), "diff", "HEAD", "--name-only", "--", "flyvis"], text=True).strip()
    assert not changed, changed
    assert sha(graph) == GRAPH_SHA
    assert sha(checkpoint) == CHECKPOINT_SHA
    paths = [graph, checkpoint, repo / "license", repo / "flyvis/network/network.py",
             repo / "flyvis/network/dynamics.py", repo / "flyvis/network/initialization.py",
             repo / "flyvis/connectome/connectome.py",
             fly_root / "artifacts/golden_reference_v1/network.json",
             fly_root / "artifacts/golden_reference_v1/checkpoint_network_parameters.npz",
             fly_root / "artifacts/golden_reference_v1/structure/nodes.csv",
             fly_root / "artifacts/moving_edge_minimal_cpu_v1/stimulus.npy"]
    return {str(p): {"sha256": sha(p), "bytes": p.stat().st_size} for p in paths}


def build_reference(fly_root: Path):
    import torch
    import pandas as pd
    sys.path.insert(0, str(fly_root / "upstream/flyvis"))
    import flyvis
    from datamate import Namespace
    from flyvis.connectome.connectome import add_nodes, add_edges
    from flyvis.network.network import Network

    assert flyvis.device.type == "cpu"
    assert not torch.cuda.is_initialized()
    spec = json.loads((fly_root / "upstream/flyvis/flyvis/connectome/fib25-fib19_v2.2.json").read_text())
    nodes = []
    add_nodes(nodes, spec["nodes"], 15)
    assert len(nodes) == N
    # The sink implements the original append/len contract without retaining 1.5M Python objects.
    class EdgeSink:
        def init__(self):
            self.count = 0
            self.src = np.empty(E, dtype=np.int64)
            self.dst = np.empty(E, dtype=np.int64)
            self.sign = np.empty(E, dtype=np.float32)
            self.nsyn = np.empty(E, dtype=np.float32)
        def __len__(self):
            return self.count
        def append(self, edge):
            if self.count >= E or edge.id != self.count:
                raise ValueError("Original graph edge overflow or nonsequential ID")
            i = self.count
            self.src[i], self.dst[i] = edge.source.id, edge.target.id
            self.sign[i], self.nsyn[i] = edge.sign, edge.n_syn
            self.count += 1
    sink = EdgeSink()
    add_edges(sink, nodes, spec["edges"], 1)
    assert len(sink) == E
    types = np.array([n.type for n in nodes], dtype="S")
    us = np.array([n.u for n in nodes], dtype=np.int32)
    vs = np.array([n.v for n in nodes], dtype=np.int32)
    names = [n["name"] for n in spec["nodes"]]
    roles = np.array(["input" if n.type in spec["input_units"] else "output" if n.type in spec["output_units"] else "intermediate" for n in nodes], dtype="S")
    node_table = Namespace(index=np.arange(N, dtype=np.int64), type=types, u=us, v=vs, role=roles,
                           layer_index={name: np.flatnonzero(types == name.encode()) for name in names})
    edge_table = Namespace(source_index=sink.src, target_index=sink.dst, sign=sink.sign, n_syn=sink.nsyn,
                           source_type=types[sink.src], target_type=types[sink.dst],
                           du=us[sink.dst] - us[sink.src], dv=vs[sink.dst] - vs[sink.src])
    connectome = Namespace(nodes=node_table, edges=edge_table, unique_cell_types=np.array(names, dtype="S"),
                          input_cell_types=np.array(spec["input_units"], dtype="S"),
                          output_cell_types=np.array(spec["output_units"], dtype="S"),
                          central_cells_index=np.flatnonzero((us == 0) & (vs == 0)))
    info = json.loads((fly_root / "artifacts/golden_reference_v1/network.json").read_text())
    config = info["network_config"]["network"]
    module = importlib.import_module("flyvis.network.network")
    with patch.object(module, "init_connectome", return_value=connectome):
        network = Network(**config)
    chkpt = fly_root / "data_cpu/results/flow/0000/000/chkpts/chkpt_00000"
    state_dict = torch.load(chkpt, map_location="cpu", weights_only=True)["network"]
    network.load_state_dict(state_dict, strict=True)
    network.eval().requires_grad_(False)
    network.clamp()
    assert all(torch.equal(network.state_dict()[k], v) for k, v in state_dict.items())
    params = network._param_api()
    weight = params.edges.weight.detach().numpy().copy()
    bias = params.nodes.bias.detach().numpy().copy()
    tau = params.nodes.time_const.detach().numpy().copy()
    inv = (1 / torch.maximum(params.nodes.time_const, torch.tensor(0.005).float())).numpy().copy()
    assert all(x.dtype == np.float32 and np.isfinite(x).all() for x in [weight, bias, tau, inv])
    archived_nodes = pd.read_csv(fly_root / "artifacts/golden_reference_v1/structure/nodes.csv")
    for key, actual in [("node_index", node_table.index), ("u", us), ("v", vs), ("cell_type", types.astype(str))]:
        assert np.array_equal(archived_nodes[key].to_numpy(), actual), key
    node_types = np.array([names.index(n.type) for n in nodes], dtype=np.uint8)
    return network, params, spec, dict(src=sink.src, dst=sink.dst, weight=weight, bias=bias, tau=tau,
                                     inv=inv, types=node_types, u=us, v=vs, central=connectome.central_cells_index)


def export_shared(spec, arrays, path):
    """Validate sharing across every expanded edge before exporting compact parameter keys."""
    src_type = arrays["types"][arrays["src"]]
    dst_type = arrays["types"][arrays["dst"]]
    du = arrays["u"][arrays["dst"]] - arrays["u"][arrays["src"]]
    dv = arrays["v"][arrays["dst"]] - arrays["v"][arrays["src"]]
    keys = np.stack([src_type, dst_type, du, dv], axis=1).astype(np.int16)
    unique, first, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    bits = arrays["weight"].view(np.uint32)
    assert np.array_equal(bits[first][inverse], bits), "Weight-sharing assumption failed"
    params = []
    for t in range(len(spec["nodes"])):
        ids = np.flatnonzero(arrays["types"] == t)
        row = []
        for name in ["bias", "tau", "inv"]:
            values = arrays[name][ids]
            assert np.all(values.view(np.uint32) == values[:1].view(np.uint32)), name
            row.append(values[0])
        params.append(row)
    np.savez(path, keys=unique, weight_bits=bits[first], node_params=np.array(params, dtype="<f4"))
    return {"edge_parameter_groups": len(unique), "node_parameter_groups": len(params),
            "sharing_checked_edges": len(keys), "weight_bits_exact_within_every_group": True}
