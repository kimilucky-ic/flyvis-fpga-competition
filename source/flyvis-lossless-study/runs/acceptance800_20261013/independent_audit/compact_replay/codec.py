"""Versioned, little-endian template format and a decoder independent of add_edges."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import numpy as np

HEADER = struct.Struct("<8sHH8I32s32s20s")
NODE = np.dtype([("base", "<u2"), ("count", "<u2"), ("su", "u1"), ("sv", "u1"),
                 ("layout", "u1"), ("input", "u1"), ("reserved", "<u4", (2,))])
RULE = np.dtype([("src", "u1"), ("dst", "u1"), ("n_offsets", "<u2"),
                 ("first", "<u4"), ("first_eid", "<u4"), ("n_edges", "<u4")])
OFFSET = np.dtype([("du", "i1"), ("dv", "i1"), ("active", "<u2"), ("weight", "<u4")])
MAGIC = b"FVLT0001"


def compile_template(spec, shared_path, binary_path, graph_sha, checkpoint_sha):
    # Freeze exactly the pinned upstream fill result offline. No hull computation occurs at runtime.
    from flyvis.connectome.connectome import fill_hull
    names = [n["name"] for n in spec["nodes"]]
    with np.load(shared_path, allow_pickle=False) as z:
        weights = {tuple(map(int, k)): int(w) for k, w in zip(z["keys"], z["weight_bits"])}
        params = z["node_params"].copy()
    extent, side, base = 15, 31, 0
    layouts, strides = [], []
    nodes = np.zeros(len(names), dtype=NODE)
    for i, node in enumerate(spec["nodes"]):
        pattern, args = node["pattern"]
        if pattern != "stride":
            raise ValueError("This pinned format supports verified strided populations only")
        su, sv = map(int, args)
        if (su, sv) not in strides:
            grid = np.full((side, side), 65535, dtype="<u2")
            count = 0
            for u in range(-extent, extent + 1):
                for v in range(-extent, extent + 1):
                    if -extent <= u + v <= extent and u % su == 0 and v % sv == 0:
                        grid[u + extent, v + extent] = count
                        count += 1
            layouts.append(grid)
            strides.append((su, sv))
        layout = strides.index((su, sv))
        count = int(np.count_nonzero(layouts[layout] != 65535))
        if base + count > 65535:
            raise ValueError("Node ID overflow")
        nodes[i] = (base, count, su, sv, layout, int(node["name"] in spec["input_units"]), [0, 0])
        base += count
    rules = np.zeros(len(spec["edges"]), dtype=RULE)
    offsets = []
    edge_count, candidates, zero_templates = 0, 0, 0
    for r, rule in enumerate(spec["edges"]):
        s, t = names.index(rule["src"]), names.index(rule["tar"])
        filled = fill_hull(rule["offsets"], 1) if len(rule["offsets"]) >= 3 else rule["offsets"]
        first, start_eid = len(offsets), edge_count
        source_coords = np.argwhere(layouts[int(nodes[s]["layout"])] != 65535)
        target_map = layouts[int(nodes[t]["layout"])]
        for (du, dv), _ in filled:
            du, dv = int(du), int(dv)
            if not (-128 <= du <= 127 and -128 <= dv <= 127):
                raise ValueError("Offset overflow")
            valid = 0
            for u, v in source_coords:
                ut, vt = int(u) + du, int(v) + dv
                if 0 <= ut < side and 0 <= vt < side and target_map[ut, vt] != 65535:
                    valid += 1
            key = (s, t, du, dv)
            if valid and key not in weights:
                raise ValueError(f"Missing effective weight {key}")
            offsets.append((du, dv, int(valid > 0), weights[key] if valid else 0))
            candidates += len(source_coords)
            edge_count += valid
            zero_templates += int(valid == 0)
        rules[r] = (s, t, len(filled), first, start_eid, edge_count - start_eid)
    offsets = np.array(offsets, dtype=OFFSET)
    dt_bits = int(np.array([0.005], dtype="<f4").view("<u4")[0])
    header = HEADER.pack(MAGIC, 1, HEADER.size, extent, base, edge_count, len(nodes), len(rules),
                         len(offsets), len(layouts), dt_bits, bytes.fromhex(graph_sha),
                         bytes.fromhex(checkpoint_sha), bytes(20))
    blob = header + nodes.tobytes() + rules.tobytes() + offsets.tobytes() + params.tobytes() + np.array(layouts, dtype="<u2").tobytes()
    blob += hashlib.sha256(blob).digest()
    Path(binary_path).write_bytes(blob)
    return {"binary_bytes": len(blob), "header_bytes": HEADER.size, "checksum_bytes": 32,
            "node_bytes": nodes.nbytes, "rule_bytes": rules.nbytes, "offset_bytes": offsets.nbytes,
            "node_parameter_bytes": params.nbytes, "layout_bytes": len(layouts) * side * side * 2,
            "nodes": base, "edges": edge_count, "rules": len(rules), "filled_offsets": len(offsets),
            "zero_edge_templates": zero_templates, "candidate_source_tests": candidates,
            "sha256": hashlib.sha256(blob).hexdigest()}


def read_template(path):
    blob = Path(path).read_bytes()
    if len(blob) < HEADER.size + 32 or hashlib.sha256(blob[:-32]).digest() != blob[-32:]:
        raise ValueError("Template length/checksum failure")
    magic, version, hsize, extent, n, e, nt, nr, no, nl, dt_bits, graph, checkpoint, reserved = HEADER.unpack_from(blob)
    if magic != MAGIC or version != 1 or hsize != HEADER.size or reserved != bytes(20):
        raise ValueError("Unsupported template header")
    if (extent, n, e, nt, nr, no, nl) != (15, 45669, 1513231, 65, 605, 2378, 2):
        raise ValueError("Template is outside the frozen model contract")
    expected = HEADER.size + nt * NODE.itemsize + nr * RULE.itemsize + no * OFFSET.itemsize + nt * 12 + nl * (2 * extent + 1)**2 * 2 + 32
    if len(blob) != expected:
        raise ValueError("Unexpected payload size")
    pos = HEADER.size
    def take(dtype, count):
        nonlocal pos
        result = np.frombuffer(blob, dtype=dtype, count=count, offset=pos).copy()
        pos += count * np.dtype(dtype).itemsize
        return result
    nodes, rules, offsets = take(NODE, nt), take(RULE, nr), take(OFFSET, no)
    params = take("<f4", nt * 3).reshape(nt, 3)
    maps = take("<u2", nl * (2 * extent + 1)**2).reshape(nl, 2 * extent + 1, 2 * extent + 1)
    if not np.isfinite(params).all() or not np.isfinite(offsets["weight"].copy().view("<f4")).all():
        raise ValueError("Nonfinite frozen parameters")
    if np.any(nodes["layout"] >= nl) or np.any(nodes["reserved"]) or np.any(nodes["input"] > 1):
        raise ValueError("Invalid node descriptor")
    next_base = 0
    for node in nodes:
        ranks = maps[int(node["layout"])]; ranks = ranks[ranks != 65535]
        if int(node["base"]) != next_base or not np.array_equal(ranks, np.arange(int(node["count"]))):
            raise ValueError("Invalid node layout rank")
        next_base += int(node["count"])
    if next_base != n or np.any(rules["src"] >= nt) or np.any(rules["dst"] >= nt) or np.any(offsets["active"] > 1):
        raise ValueError("Invalid IDs or flags")
    next_offset, next_edge = 0, 0
    for rule in rules:
        if int(rule["first"]) != next_offset or int(rule["first_eid"]) != next_edge:
            raise ValueError("Nonsequential rule descriptor")
        next_offset += int(rule["n_offsets"]); next_edge += int(rule["n_edges"])
    if (next_offset, next_edge) != (no, e):
        raise ValueError("Descriptor totals differ")
    dt = np.array([dt_bits], dtype="<u4").view("<f4")[0]
    if dt_bits != int(np.array([0.005], dtype="<f4").view("<u4")[0]):
        raise ValueError("Unsupported dt")
    return dict(nodes=nodes, rules=rules, offsets=offsets, params=params, maps=maps, n=n, e=e,
                dt=dt, graph_sha256=graph.hex(), checkpoint_sha256=checkpoint.hex())


def iter_edges(template):
    """Original global edge order. Does not read a source graph or expanded edge file."""
    nodes, maps = template["nodes"], template["maps"]
    eid = 0
    for rule in template["rules"]:
        if eid != int(rule["first_eid"]):
            raise ValueError("Decoded rule start differs")
        src, dst = nodes[int(rule["src"])], nodes[int(rule["dst"])]
        sm, tm = maps[int(src["layout"])], maps[int(dst["layout"])]
        start_eid = eid
        for offset in template["offsets"][int(rule["first"]):int(rule["first"] + rule["n_offsets"])]:
            count = 0
            for u in range(sm.shape[0]):
                for v in range(sm.shape[1]):
                    if sm[u, v] == 65535:
                        continue
                    ut, vt = u + int(offset["du"]), v + int(offset["dv"])
                    if 0 <= ut < tm.shape[0] and 0 <= vt < tm.shape[1] and tm[ut, vt] != 65535:
                        yield eid, int(src["base"]) + int(sm[u, v]), int(dst["base"]) + int(tm[ut, vt]), int(offset["weight"])
                        eid += 1; count += 1
            if bool(count) != bool(offset["active"]):
                raise ValueError("Empty-template flag differs from geometry")
        if eid - start_eid != int(rule["n_edges"]):
            raise ValueError("Decoded rule edge count differs")
    if eid != template["e"]:
        raise ValueError("Decoded total edge count differs")
