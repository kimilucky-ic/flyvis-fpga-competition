"""Strict FP32 CPU prototype: streams topology each step; never materializes all edges."""
from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=False, fastmath=False)
def step(activity, current, stimulus, nodes, rules, offsets, weights, params, maps, dt):
    current[:] = np.float32(0)
    edge_count = 0
    for r in range(len(rules)):
        rule = rules[r]
        sn, tn = nodes[rule["src"]], nodes[rule["dst"]]
        sm, tm = maps[sn["layout"]], maps[tn["layout"]]
        for k in range(rule["first"], rule["first"] + rule["n_offsets"]):
            off = offsets[k]
            for u in range(sm.shape[0]):
                for v in range(sm.shape[1]):
                    srank = sm[u, v]
                    if srank == 65535:
                        continue
                    ut, vt = u + off["du"], v + off["dv"]
                    if ut < 0 or vt < 0 or ut >= tm.shape[0] or vt >= tm.shape[1]:
                        continue
                    trank = tm[ut, vt]
                    if trank == 65535:
                        continue
                    source, target = int(sn["base"]) + int(srank), int(tn["base"]) + int(trank)
                    release = activity[source] if activity[source] > np.float32(0) else np.float32(0)
                    term = np.float32(weights[k] * release)
                    current[target] = np.float32(current[target] + term)
                    edge_count += 1
    # Global barrier: every source read above has finished before any activity is overwritten.
    for t in range(len(nodes)):
        node = nodes[t]
        bias, inv_tau = params[t, 0], params[t, 2]
        for j in range(node["count"]):
            i = int(node["base"]) + j
            drive = np.float32(-activity[i] + bias)
            drive = np.float32(drive + current[i])
            x = stimulus[j] if node["input"] else np.float32(0)
            drive = np.float32(drive + x)
            velocity = np.float32(inv_tau * drive)
            delta = np.float32(velocity * dt)
            activity[i] = np.float32(activity[i] + delta)
    return edge_count


class Engine:
    def init__(self, template):
        self.t = template
        self.activity = np.empty(template["n"], dtype=np.float32)
        self.current = np.zeros_like(self.activity)
        self.weights = template["offsets"]["weight"].copy().view(np.float32)
        for i, node in enumerate(template["nodes"]):
            self.activity[int(node["base"]):int(node["base"]) + int(node["count"])] = template["params"][i, 0]
        self.steps = 0
    def advance(self, stimulus):
        stimulus = np.asarray(stimulus)
        if stimulus.dtype != np.float32 or stimulus.shape != (721,) or not np.isfinite(stimulus).all():
            raise ValueError("A finite FP32 stimulus[721] is required")
        t = self.t
        count = step(self.activity, self.current, stimulus, t["nodes"], t["rules"], t["offsets"], self.weights, t["params"], t["maps"], t["dt"])
        if count != t["e"] or not np.isfinite(self.activity).all():
            raise ValueError("Step count or finite-state check failed")
        self.steps += 1
        return self.activity
