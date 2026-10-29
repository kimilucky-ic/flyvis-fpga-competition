"""CPU source/interface checks and frozen small-study registration."""
import collections
import time
import shutil
import numpy as np
import torch
from common import *
from cnn import HexCNN
from decoder_cpu import CPUDecoder

def main():
    types,u,v,p=source();identity=load(BUNDLE/'identity_manifest.json')
    assert sha(BUNDLE/'expanded_parameters.npz')==identity['expanded_parameters_sha256']
    assert sha(BUNDLE/'initial_state_full.npy')==identity['initial_state_sha256']
    assert sha(BUNDLE/'nodes_full.csv')==identity['nodes_full_sha256']
    h=np.isin(types,TYPES);r=np.flatnonzero(~h).astype(np.int64);H=np.flatnonzero(h).astype(np.int64)
    src,dst=p['source_global'],p['target_global'];mask=h[dst]
    field_types=list(dict.fromkeys(types[src[mask]].tolist()))
    grid_ids=[np.flatnonzero(types==t) for t in TYPES]
    grid_uv=np.array([u[grid_ids[0]],v[grid_ids[0]]])
    assert all(len(ids)==721 and np.array_equal(np.array([u[ids],v[ids]]),grid_uv) for ids in grid_ids)
    ids=np.stack(grid_ids).astype(np.int64);assert np.array_equal(ids.reshape(-1),H)
    field_ids=np.full((len(field_types),721),-1,np.int64)
    look={(int(a),int(b)):i for i,(a,b) in enumerate(grid_uv.T)}
    for ci,t in enumerate(field_types):
        for i in np.flatnonzero(types==t):field_ids[ci,look[(int(u[i]),int(v[i]))]]=i
    distance=np.maximum.reduce([abs(u[src]-u[dst]),abs(v[src]-v[dst]),abs(u[src]+v[src]-u[dst]-v[dst])])
    assert distance[mask].max()==7
    offsets=np.array([(du,dv) for du in range(-7,8) for dv in range(-7,8) if max(abs(du),abs(dv),abs(du+dv))<=7],np.int64)
    neighbors=np.array([[look.get((int(a+du),int(b+dv)),-1) for du,dv in offsets] for a,b in grid_uv.T],np.int64)
    np.savez(HERE/'mapping.npz',H=H,R=r,H_grid_ids=ids,grid_uv=grid_uv,field_ids=field_ids,
        field_types=np.array(field_types),h_channels=np.array([field_types.index(t) for t in TYPES]),offsets=offsets,neighbors=neighbors)
    keep=~h[dst];eid=np.flatnonzero(keep).astype(np.int64)
    partition={k:int(m.sum()) for k,m in dict(HH=h[src]&h[dst],RH=~h[src]&h[dst],HR=h[src]&~h[dst],RR=~h[src]&~h[dst]).items()}
    candidate={k:identity[k] for k in ['checkpoint_sha256','source_commit','expanded_parameters_sha256','nodes_full_sha256','n_nodes','n_edges','dt_s','dynamics_type','activation_type']}
    candidate.update(schema='flyvis-r-only-candidate/v1',h_global_node_indices=H.tolist(),
        h_indices_digest=array_sha(H),r_indices_digest=array_sha(r),partition_counts=partition,r_edge_indices_digest=array_sha(eid))
    dump(HERE/'R_CANDIDATE.json',candidate)
    rr=r_service();assert len(rr.r_indices)==39901 and rr.n_r_edges==1079351
    assert not np.isin(p['target_global'][rr.original_edge_ids],H).any()
    model=HexCNN(len(field_types),offsets,grid_uv,[field_types.index(t) for t in TYPES])
    rng=np.random.default_rng(6);fields=torch.from_numpy(rng.normal(size=(1,len(field_types),721)).astype(np.float32))
    with torch.no_grad():
        model.kernel.normal_(0,.002);model.recurrent.normal_(0,.002)
        out=model(fields)
        for pixel in [0,15,360,705,720]:
            ni=neighbors[pixel];patch=fields[0,:,np.maximum(ni,0)]*torch.from_numpy(ni>=0)[None]
            ref=fields[0,model.h_channels,pixel]+model.patch_delta(patch[None],fields[0,model.h_channels,pixel][None])[0]
            assert torch.allclose(out[0,:,pixel],ref,atol=2e-6,rtol=1e-5)
    decoder=CPUDecoder()
    cached=LANE/'t4t5_confirm_20261011/artifacts/gpu_r1/ON60/Full'
    samples=np.array([0,160,200,240,285,400,484])
    activity=np.load(cached/'activities_full.npy',mmap_mode='r')[0,samples]
    expected=np.load(cached/'flow.npy')[0,samples]
    actual=decoder.decode(activity)
    maxerr=float(abs(actual-expected).max())
    assert np.allclose(actual,expected,atol=1e-5,rtol=1e-5),maxerr
    dump(HERE/'PREFLIGHT.json',dict(status='PASS_CPU_INTERFACES',neural_steps=0,new_official_decoder_frames=7,
        torch=torch.__version__,device='cpu',gpu_calls=0,WSL='sandbox access denied; not required for CPU route',
        H=5768,R=39901,partition_counts=partition,field_types=field_types,field_channels=len(field_types),
        radius=7,hex_taps=len(offsets),edges_to_H=int(mask.sum()),all_H_edge_offsets_covered=True,
        radius_edge_counts={str(i):int((mask&(distance==i)).sum()) for i in range(8)},
        R_targets_exclude_H=True,patch_conv_alignment=True,decoder_original_class_bodies=True,
        decoder_cpu_vs_accepted_GPU_max_abs=maxerr,decoder_tolerance=dict(atol=1e-5,rtol=1e-5),
        decoder_state_unchanged=True,free_bytes=shutil.disk_usage(HERE).free))
    # Training data are accepted Full caches. Never read their trajectories in
    # replacement execution. Labels allowed ONLY in training/offline scoring.
    training=[]
    for condition in TRAIN:
        folder=LANE/'t4t5_confirm_20261011/artifacts/gpu_r1'/condition/'Full'
        training.append(dict(condition=condition,path=str(folder/'activities_full.npy'),sha256=sha(folder/'activities_full.npy')))
    # Four fresh direction/polarity baselines, plus prespecified speed/position
    # transforms, all drawn from original frozen official retinal stimulation.
    raw_path=LANE/'phase4_direction_extension_20261010/prepared_inputs/stimulus24_fp32.npy'
    if not raw_path.exists():
        candidates=list(raw_path.parent.glob('stimulus*.npy'));assert len(candidates)==1
        raw_path=candidates[0]
    raw=np.load(raw_path,mmap_mode='r');assert raw.shape==(24,485,1,721)
    tests=[]
    for c,sample,angle in [('ON0',1,0),('ON180',13,180),('OFF0',0,0),('OFF180',12,180)]:
        frame=np.array(raw[sample,:,0],copy=True)
        variants=[('base',frame)]
        if c in ['ON0','OFF0']:
            slow=frame.copy();slow[200:]=frame[200+np.arange(285)//2];variants.append(('half_speed',slow))
            shifted=np.empty_like(frame);inverse=np.array([look.get((int(a-4),int(b)),-1) for a,b in grid_uv.T])
            shifted[:]=np.float32(0 if c.startswith('ON') else 1)
            shifted[:,inverse>=0]=frame[:,inverse[inverse>=0]];variants.append(('shift_u4',shifted))
        for variant,stimulus in variants:
            name=c+'_'+variant;path=HERE/'inputs'/(name+'.npy');path.parent.mkdir(exist_ok=True)
            np.save(path,stimulus)
            tests.append(dict(id=name,polarity='ON' if c.startswith('ON') else 'OFF',angle=angle,
                group=variant,original_sample=sample,path=str(path),sha256=sha(path)))
    assert len(tests)==8
    dump(HERE/'TEST_CASES.json',tests)
    pins={str(path):sha(path) for path in [HERE/'common.py',HERE/'cnn.py',HERE/'decoder_cpu.py',HERE/'prepare.py',HERE/'experiment.py',HERE/'mapping.npz',HERE/'R_CANDIDATE.json',HERE/'TEST_CASES.json',
        BUNDLE/'initial_state_full.npy',BUNDLE/'expanded_parameters.npz',BUNDLE/'nodes_full.csv',BUNDLE/'identity_manifest.json',CHECKPOINT,
        FLY/'gpu_phase2/r_only.py',SUPPORT/'FULL_DECODER_CONTRACT.json',UPSTREAM/'task/decoder.py',UPSTREAM/'utils/activity_utils.py',UPSTREAM/'utils/nn_utils.py',UPSTREAM/'utils/hex_utils.py',
        LANE/'t4t5_criticality_20261011/metrics.py',LANE/'t4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy',raw_path]}
    dump(HERE/'PREREGISTRATION.json',dict(schema='T4T5-CNN-closed-loop-feasibility/v1',date='2026-10-16',pins=pins,
        neural_model=identity['checkpoint_sha256'],initial=identity['initial_state_sha256'],dt=.005,
        split='four accepted Full training movies ON60/240 OFF90/270; eight new Full references never used to fit/select CNN',training=training,
        test='ON/OFF0/180 plus predeclared half-speed and u+4 translation of ON/OFF0; not 24-condition benchmark or natural video',
        CNN='HexCNN-AR1: shared learned radius7 169tap23channel→8 convolution of ReLU old inputs, learned raw-own-H8×8 recurrent map and learned offset; output is ownOldH plus learned normalized increment. No originalH weights/bias/tau/edge scatter in production.',
        memory='old live R input fields plus CNN own previous5768 activity are sufficient state inputs for this first-order source model; no teacher corrections after a0',
        training_method=dict(seed=2026101604,updates=700,batch_spatial_points=1024,Adam_lr_first500=.005,Adam_lr_last200=.001,
            weight_decay=1e-6,pre_step_probability=.25,active_step_probability=.75,loss='per-type normalized deltaH MSE; teacher forcing for training only',
            no_test_checkpoint_selection=True,no_automatic_retry=True),
        comparison='new Full original dynamics, exact-H plus live R-only Sham first base condition, CNN replacement all8, H-hold controls four base conditions; original H updates0 in CNN path',
        interface='all H and R candidates read same immutable a[k]; validate both then atomic complete a[k+1] commit; errors no partial commit/fallback',
        gate=dict(numerical_sham_atol=1e-5,numerical_sham_rtol=1e-5,max_abs_activity=100,
            functional='all8 complete485 steps finite, H baseline-subtracted relativeL2<=.20 over200:485, original fixed331ROI flow E<=.20, M in[.8,1.2], field_angle<=15deg over primary200:286 and allpost200:485; weak reference ineligible, not automatic pass'),
        metrics='allH/R per-step RMSE/max/nRMSE, final state, 8subtypes and central56, fixed optical E/M/Q/field angle; Full is model reference not ground truth optical-flow accuracy',
        resource_budget=dict(device='CPU only',threads=1,training_wall_s=600,rollout_wall_s=900,new_disk_GiB_max=3,GPU=0,board=0),
        stop='one bounded pilot and report; retain negatives; no architecture sweep, quantization, GUI or hardware changes'))
    dump(HERE/'FREEZE.json',dict(sha256=sha(HERE/'PREREGISTRATION.json'),time_ns=time.time_ns()))
    print('PASS_CPU_PREPARATION_FROZEN',maxerr,field_types)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        dump(HERE/f'FAILURE_PREPARE_{time.time_ns()}.json',dict(error=repr(exc),neural_steps=0));raise
