"""GUI Full-only input guard adapter: three scalar CUDA waits -> one flag copy.

No neuron/synapse implementation is copied. The actual update still calls the
original stimulus API, state API and Network._next_state with oracle.params/dt.
All three original input predicates remain required. With proof reuse disabled,
their booleans are copied together on every step. In a private continuous session,
an unchanged input tensor and the exact checked/committed prior candidate can
reuse their existing predicates; identity or mutation-version changes revalidate.
The caller must also retain the candidate-finite check and its COMMIT gate.
"""
from live_protocol import require


class CombinedCheckedFull:
    def init__(self,oracle,torch,timing,cache_validated_tensors=False):
        self.oracle=oracle;self.torch=torch;self.timing=timing;self.steps=0;self.guard_copies=0
        self.net=oracle.net;self.params=oracle.params;self.dt=oracle.dt
        require(self.net.n_nodes==45669 and self.net.n_edges==1513231 and not self.net._state_hooks,'COMBINED_GUARD_FULL_ONLY')
        self.target_sum=self.net.target_sum
        self.cache_validated_tensors=cache_validated_tensors;self.input_proof=None;self.committed_proof=None;self.candidate_proof=None
        self.reused_old=0;self.reused_input=0;self.candidate_checks=0;self.commits=0
        self.original_input_index=None
        if cache_validated_tensors:
            # Official add_input otherwise converts the same NumPy index table to
            # CUDA for advanced indexing on every call. Cache the identical IDs.
            self.original_input_index=self.net.stimulus.input_index
            cached=torch.as_tensor(self.original_input_index.copy(),device=oracle.device,dtype=torch.int64)
            require(bool(torch.equal(cached.cpu(),torch.as_tensor(self.original_input_index,device='cpu'))),'INPUT_INDEX_CACHE_IDENTITY')
            self.net.stimulus.input_index=cached
    @staticmethod
    def proof(tensor):return (tensor,tensor._version)
    @staticmethod
    def matches(proof,tensor):return proof is not None and proof[0] is tensor and proof[1]==tensor._version
    def step(self,old_full,hex_frame):
        torch=self.torch;oracle=self.oracle;net=self.net
        require(oracle.params is self.params and oracle.dt==self.dt and not net._state_hooks
                and net.target_sum==self.target_sum,'COMBINED_GUARD_MODEL_OR_MODE_CHANGED')
        require(old_full.shape==(net.n_nodes,) and old_full.dtype==torch.float32 and old_full.device==oracle.device,'invalid Full old state')
        require(hex_frame.shape==(721,) and hex_frame.dtype==torch.float32 and hex_frame.device==oracle.device,'invalid Full input')
        old_known=self.cache_validated_tensors and self.matches(self.committed_proof,old_full)
        input_known=self.cache_validated_tensors and self.matches(self.input_proof,hex_frame)
        with torch.no_grad():
            if not(old_known and input_known):
                with self.timing.measure('input_predicates_cuda_submit'):
                    flags=[]
                    if not old_known:flags.append(torch.isfinite(old_full).all())
                    if not input_known:flags.extend((torch.isfinite(hex_frame).all(),((hex_frame<0)|(hex_frame>1)).any()))
                    packed=torch.stack(flags)
                with self.timing.measure('input_predicates_one_D2H_wait'):
                    checked=iter(packed.cpu().tolist());self.guard_copies+=1
                old_ok=True if old_known else next(checked)
                input_ok,outside=(True,False) if input_known else (next(checked),next(checked))
                require(old_ok and input_ok,'nonfinite Full input');require(not outside,'Full hex input outside [0,1]')
                self.input_proof=self.proof(hex_frame)
            self.reused_old+=int(old_known);self.reused_input+=int(input_known)
            with self.timing.measure('original_stimulus_and_state_API'):
                net.stimulus.buffer.zero_()
                net.stimulus.add_input(hex_frame.reshape(1,1,1,721))
                state=net._state_api(oracle.AutoDeref(nodes=oracle.AutoDeref(activity=old_full.reshape(1,-1)),edges=oracle.AutoDeref()))
            with self.timing.measure('original_next_state_host'):
                new=net._next_state(self.params,state,net.stimulus()[:,0],self.dt)
            require(list(new.nodes.keys())==['activity'] and len(new.edges)==0,'Full state schema changed')
            self.steps+=1
            return new.nodes.activity[0].detach()
    def candidate_predicate(self,candidate):
        return self.torch.isfinite(candidate).all()
    def validate_candidate(self,candidate):
        self.candidate_proof=None
        require(candidate.shape==(self.net.n_nodes,) and candidate.dtype==self.torch.float32 and candidate.device==self.oracle.device,'INVALID_CANDIDATE_SCHEMA')
        with self.timing.measure('candidate_predicate_host_submit'):flag=self.candidate_predicate(candidate)
        with self.timing.measure('candidate_flag_host_wait'):valid=bool(flag)
        require(valid,'NONFINITE_CANDIDATE_NO_COMMIT')
        self.candidate_checks+=1;self.candidate_proof=(self.proof(candidate),self.steps)
    def commit(self,candidate):
        require(self.candidate_proof is not None and self.candidate_proof[1]==self.steps
                and self.matches(self.candidate_proof[0],candidate),'CANDIDATE_PROOF_MISSING_OR_MUTATED')
        self.committed_proof=self.proof(candidate);self.candidate_proof=None;self.commits+=1
        return candidate
    def info(self):
        return dict(adapter='COMBINED_ORIGINAL_FULL_INPUT_CHECKS',actual_original_updates=self.steps,input_flag_copies=self.guard_copies,
            predicates_per_step=['old_full_finite','hex_frame_finite','hex_frame_outside_0_1'],
            input_validation_host_waits_per_step=None if self.cache_validated_tensors else 1,max_input_validation_host_waits_per_step=1,
            original_input_validation_host_waits_per_step=3,input_index_cached_on_GPU=self.original_input_index is not None,
            candidate_check='REQUIRED_SEPARATE_BEFORE_COMMIT',neural_update='original Network._next_state',
            arithmetic_precision_changed=False,node_or_edge_reduction=False,
            private_tensor_proof_reuse=self.cache_validated_tensors,reused_old_finite_steps=self.reused_old,reused_input_steps=self.reused_input,
            candidate_checks=self.candidate_checks,accepted_commits=self.commits,
            proof_rule='same owned Tensor object and unchanged PyTorch mutation version; otherwise revalidate; no external CUDA writers')
    def close(self):
        self.torch.cuda.synchronize()
        if self.original_input_index is not None:self.net.stimulus.input_index=self.original_input_index


def validate_rejections(adapter,initial,frame):
    """Actual CUDA input-boundary tests, never published as experimental activities."""
    torch=adapter.torch;tests=[];before=adapter.steps
    with torch.no_grad():
        cases=[]
        for name,value,old in [('old_nan',float('nan'),True),('old_inf',float('inf'),True),
                               ('input_nan',float('nan'),False),('input_inf',float('inf'),False),
                               ('input_negative',-.01,False),('input_gt_one',1.01,False)]:
            x=frame.clone();a=initial.clone();(a if old else x)[0]=value;cases.append((name,a,x))
        cases.extend([('old_wrong_shape',initial[:-1],frame),('input_wrong_shape',initial,frame[:-1]),
                      ('old_wrong_dtype',initial.double(),frame),('input_wrong_dtype',initial,frame.double())])
        for name,a,x in cases:
            try:adapter.step(a,x)
            except ValueError as e:tests.append(dict(case=name,rejected=True,reason=str(e)))
            else:raise ValueError('INVALID_INPUT_ACCEPTED '+name)
    require(adapter.steps==before,'INVALID_INPUT_REACHED_NEURAL_UPDATE')
    return tests


def validate_proof_rejections(adapter,initial,frame):
    """CUDA faults use private test tensors, never alter weights or frozen files."""
    from live_protocol import checked_commit
    torch=adapter.torch;tests=[]
    def rejected(name,call):
        try:call()
        except ValueError as e:tests.append(dict(case=name,rejected=True,reason=str(e)))
        else:raise ValueError('BAD_PROOF_ACCEPTED '+name)
    a=initial.clone();x=frame.clone();candidate=adapter.step(a,x)
    rejected('unchecked_candidate',lambda:adapter.commit(candidate))
    adapter.validate_candidate(candidate)
    n=adapter.commits
    def revoked(*args):raise ValueError('TEST_SCOPE_REVOKED')
    rejected('cancel_before_commit',lambda:checked_commit(candidate,revoked,adapter.commit))
    require(adapter.commits==n,'CANCEL_COMMITTED')
    a=adapter.commit(candidate)
    rejected('duplicate_commit',lambda:adapter.commit(candidate))
    x[0]=1.1
    rejected('changed_validated_input',lambda:adapter.step(a,x))
    x=frame.clone();a[0]=float('nan')
    rejected('changed_committed_state',lambda:adapter.step(a,x))
    candidate=adapter.step(initial.clone(),frame.clone());adapter.validate_candidate(candidate);candidate[0]=float('nan')
    rejected('candidate_mutated_after_check',lambda:adapter.commit(candidate))
    rejected('nonfinite_candidate',lambda:adapter.validate_candidate(candidate))
    adapter.input_proof=None;adapter.committed_proof=None;adapter.candidate_proof=None
    return tests
