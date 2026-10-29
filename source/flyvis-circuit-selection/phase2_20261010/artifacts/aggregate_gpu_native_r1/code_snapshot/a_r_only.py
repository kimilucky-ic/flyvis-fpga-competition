"""Stateless original-dynamics R-only update. No FlyVis import or Full updater.

All parameters originate from an independently exported official checkpoint.
Only original edges whose TARGET lies in R are evaluated. No H next state exists.
Caller owns the old complete state and the atomic merge with an independent H.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib, json
import numpy as np
import torch

class InterfaceError(ValueError):
    """Invalid identity/state/input: no candidate is returned and no state advances."""

def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def array_sha(a):
    return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()

@dataclass(frozen=True)
class RStepResult:
    global_node_indices: torch.Tensor
    activity: torch.Tensor
    step_id: int
    run_id: str
    condition_id: str
    candidate_sha256: str
    checkpoint_sha256: str
    status: str = "CANDIDATE_NOT_COMMITTED"

class RStepService:
    """B=1, float32, fixed manifest dt; explicit device; no stored trajectory.

    step(old_full[N], hex_frame[721], *, step_id, run_id, condition_id)
      returns activity[N_R] and global_node_indices[N_R] in ascending global order.
    old_full is the immutable logical snapshot a[k], with both H and R from k.
    The returned candidate is NOT committed. An independent H service and the
    caller's barrier must validate and merge both candidates before next k.
    """
    def init__(self, parameter_path, identity_path, candidate_path, *, device="cpu"):
        self.device=torch.device(device)
        if self.device.type not in ("cpu","cuda"):
            raise InterfaceError("only cpu or cuda devices are supported")
        if self.device.type=="cuda":
            if not torch.cuda.is_available():raise InterfaceError("CUDA unavailable")
            self.device=torch.device("cuda",self.device.index if self.device.index is not None else torch.cuda.current_device())
        self.identity=json.loads(Path(identity_path).read_text())
        manifest=json.loads(Path(candidate_path).read_text())
        self.candidate_sha256=file_sha(candidate_path)
        self.checkpoint_sha256=self.identity["checkpoint_sha256"]
        self.n_nodes=int(self.identity["n_nodes"])
        self.dt=float(self.identity["dt_s"])
        if self.identity["dynamic_state_keys"]!=["nodes.activity"] or self.identity["dynamic_edge_state_keys"]!=[]:
            raise InterfaceError("unsupported dynamic state schema")
        if manifest.get("schema")!="flyvis-r-only-candidate/v1":
            raise InterfaceError("unsupported candidate manifest schema")
        for key in ("checkpoint_sha256","source_commit","expanded_parameters_sha256","nodes_full_sha256","n_nodes","n_edges","dt_s","dynamics_type","activation_type"):
            if manifest.get(key)!=self.identity.get(key):
                raise InterfaceError("candidate/model identity mismatch: "+key)
        if self.identity.get("dynamics_type")!="PPNeuronIGRSynapses" or self.identity.get("activation_type")!="ReLU":
            raise InterfaceError("unsupported original dynamics")
        if self.dt!=0.005:raise InterfaceError("this tested profile requires dt=0.005")
        if file_sha(parameter_path)!=self.identity["expanded_parameters_sha256"]:
            raise InterfaceError("expanded parameter file hash mismatch")
        with np.load(parameter_path,allow_pickle=False) as z:
            p={k:np.ascontiguousarray(z[k]) for k in z.files}
        if set(p)!=set(self.identity["expanded_parameter_digests"]):
            raise InterfaceError("parameter schema mismatch")
        for key,a in p.items():
            if array_sha(a)!=self.identity["expanded_parameter_digests"][key]:
                raise InterfaceError("expanded array digest mismatch: "+key)
        for key in ("bias","time_const"):
            if p[key].shape!=(self.n_nodes,) or p[key].dtype!=np.float32 or not np.isfinite(p[key]).all():
                raise InterfaceError("invalid node parameter: "+key)
        if np.any(p["time_const"]<=0):raise InterfaceError("nonpositive time constant")
        ne=int(self.identity["n_edges"])
        for key in ("effective_weight","sign","syn_count","syn_strength"):
            if p[key].shape!=(ne,) or p[key].dtype!=np.float32 or not np.isfinite(p[key]).all():
                raise InterfaceError("invalid edge parameter: "+key)
        for key in ("source_global","target_global","original_edge_index"):
            if p[key].shape!=(ne,) or p[key].dtype!=np.int64:
                raise InterfaceError("invalid edge indexing")
        if not np.array_equal(p["original_edge_index"],np.arange(ne)):
            raise InterfaceError("edge order has changed")
        if np.any(p["source_global"]<0) or np.any(p["target_global"]<0) or np.any(p["source_global"]>=self.n_nodes) or np.any(p["target_global"]>=self.n_nodes):
            raise InterfaceError("edge node index out of range")
        if not np.array_equal(p["effective_weight"],p["sign"]*p["syn_count"]*p["syn_strength"]):
            raise InterfaceError("actual derived edge weights differ")
        h=np.asarray(manifest["h_global_node_indices"])
        if h.ndim!=1 or h.dtype.kind not in "iu" or not 0<len(h)<self.n_nodes:
            raise InterfaceError("H must be a nonempty proper integer subset")
        h=h.astype(np.int64)
        if np.any(h<0) or np.any(h>=self.n_nodes) or np.any(np.diff(h)<=0):
            raise InterfaceError("H indices must be unique, ascending and in range")
        if array_sha(h)!=manifest["h_indices_digest"]:
            raise InterfaceError("H index digest mismatch")
        mask=np.zeros(self.n_nodes,dtype=bool);mask[h]=True
        r=np.flatnonzero(~mask).astype(np.int64)
        if array_sha(r)!=manifest["r_indices_digest"]:
            raise InterfaceError("R indices/order mismatch")
        keep=~mask[p["target_global"]]
        ids=np.flatnonzero(keep).astype(np.int64)
        local=np.full(self.n_nodes,-1,dtype=np.int64);local[r]=np.arange(len(r))
        self.h_indices=h.copy()
        self.r_indices=r.copy()
        self.original_edge_ids=ids
        self.partition_counts={k:int(v.sum()) for k,v in dict(
            HH=mask[p["source_global"]]&mask[p["target_global"]],
            RH=~mask[p["source_global"]]&mask[p["target_global"]],
            HR=mask[p["source_global"]]&~mask[p["target_global"]],
            RR=~mask[p["source_global"]]&~mask[p["target_global"]]).items()}
        if self.partition_counts!=manifest["partition_counts"]:
            raise InterfaceError("partition counts mismatch")
        if array_sha(ids)!=manifest["r_edge_indices_digest"]:
            raise InterfaceError("R edge identities/order mismatch")
        def t(a):return torch.from_numpy(np.array(a,copy=True)).to(self.device)
        self._r=t(r)
        self._source=t(p["source_global"][keep])
        self._target=t(local[p["target_global"][keep]])
        self._weight=t(p["effective_weight"][keep])
        self._bias=t(p["bias"][r])
        self._tau=t(p["time_const"][r])
        self._inv_tau=1/torch.maximum(self._tau,torch.tensor(self.dt,dtype=torch.float32,device=self.device))
        inp=p["input_node_index"]
        if inp.shape!=(8,721) or inp.dtype!=np.int64 or len(np.unique(inp))!=inp.size or np.any(inp<0) or np.any(inp>=self.n_nodes):
            raise InterfaceError("invalid official input-node map")
        flat=inp.reshape(-1)
        in_r=local[flat]>=0
        self._input_r=t(local[flat[in_r]])
        self._hex_index=t(np.tile(np.arange(721,dtype=np.int64),8)[in_r])
        self.n_r=len(r)
        self.n_r_edges=len(ids)

    def _check(self,x,size,name):
        if not isinstance(x,torch.Tensor):raise InterfaceError(name+" must be an explicit torch Tensor")
        if x.dtype!=torch.float32 or x.shape!=(size,):raise InterfaceError(name+" requires float32 shape ["+str(size)+"]")
        if x.device!=self.device:raise InterfaceError(name+" device mismatch")
        if x.requires_grad:raise InterfaceError(name+" must be detached; inference only")
        if not bool(torch.isfinite(x).all()):raise InterfaceError(name+" contains NaN/Inf")

    def external_r(self,hex_frame):
        self._check(hex_frame,721,"hex_frame")
        if bool(((hex_frame<0)|(hex_frame>1)).any()):raise InterfaceError("hex_frame outside [0,1]")
        x=torch.zeros(self.n_r,dtype=torch.float32,device=self.device)
        x[self._input_r]=hex_frame.index_select(0,self._hex_index)
        return x

    @torch.no_grad()
    def step(self,old_full,hex_frame,*,step_id,run_id,condition_id):
        self._check(old_full,self.n_nodes,"old_full")
        if type(step_id) is not int or step_id<0:raise InterfaceError("step_id must be a nonnegative integer")
        if not isinstance(run_id,str) or not run_id or not isinstance(condition_id,str) or not condition_id:
            raise InterfaceError("run_id and condition_id must be nonempty strings")
        x=self.external_r(hex_frame)
        # Only HR/RR original edges, in original global edge order.
        edge_current=self._weight*torch.relu(old_full.index_select(0,self._source))
        current=torch.zeros(self.n_r,dtype=torch.float32,device=self.device)
        current.scatter_add_(0,self._target,edge_current)
        old_r=old_full.index_select(0,self._r)
        # Official PPNeuronIGRSynapses floating-point operation order.
        velocity=self._inv_tau*(-old_r+self._bias+current+x)
        new_r=old_r+velocity*self.dt
        if not bool(torch.isfinite(new_r).all()):raise InterfaceError("nonfinite R candidate")
        return RStepResult(self._r.clone(),new_r,step_id,run_id,condition_id,
                           self.candidate_sha256,self.checkpoint_sha256)
