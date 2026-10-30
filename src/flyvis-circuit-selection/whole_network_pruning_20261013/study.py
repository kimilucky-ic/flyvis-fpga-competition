"""Bounded CPU study. Commands prepare/calibrate/screen/validate/report are explicit.

No scheduler, Torch, official-network callback, CUDA, decoder or board access.
Reference trajectories are opened by analysis AFTER an independent rollout.
"""
import os
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import ast
import csv
import hashlib
import json
import platform
import time
import uuid
from collections import Counter
from pathlib import Path
import numpy as np
from independent_model import IndependentModel

HERE = Path(__file__).resolve().parent
LANE = HERE.parent
ROOT = LANE.parent
FLY = ROOT.parent / 'fly'
BUNDLE = LANE / 'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle'
OLD = LANE / 't4t5_criticality_20261011'
TYPES = [f'T{n}{c}' for n in [4, 5] for c in 'abcd']
SCREEN = ['ON60', 'OFF90']
HOLDOUT = ['ON240', 'OFF270', 'OFF60', 'ON90']
SAMPLES = dict(ON60=5, OFF90=6, ON240=17, OFF270=18, OFF60=4, ON90=7)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(block)
    return h.hexdigest()


def array_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def table(path, records):
    path = Path(path)
    with path.open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def source_data():
    rows = list(csv.DictReader((BUNDLE/'nodes_full.csv').open(encoding='utf-8-sig')))
    ids = np.array([int(r['global_node_index']) for r in rows], np.int64)
    assert np.array_equal(ids, np.arange(45669))
    types = np.array([r['cell_type'] for r in rows])
    u = np.array([int(r['u']) for r in rows], np.int64)
    v = np.array([int(r['v']) for r in rows], np.int64)
    radius = np.maximum.reduce([abs(u), abs(v), abs(u+v)])
    with np.load(BUNDLE/'expanded_parameters.npz', allow_pickle=False) as data:
        params = {key: data[key] for key in data.files}
    return rows, types, radius, params


def export_model(name, mask, rows, types, radius, p):
    folder = HERE/'models'/name
    folder.mkdir(parents=True)
    ids = np.flatnonzero(mask).astype(np.int64)
    inverse = np.full(45669, -1, np.int64)
    inverse[ids] = np.arange(len(ids))
    src, dst = p['source_global'], p['target_global']
    internal = mask[src] & mask[dst]
    eid = np.flatnonzero(internal).astype(np.int64)
    imap = p['input_node_index']
    channel, pixel = np.where(mask[imap])
    retained_pixels = np.unique(pixel).astype(np.int64)
    pixel_inverse = np.full(721, -1, np.int64)
    pixel_inverse[retained_pixels] = np.arange(len(retained_pixels))
    np.savez(folder/'model.npz', global_node_index=ids, original_edge_index=eid,
        source=inverse[src[eid]], target=inverse[dst[eid]], weight=p['effective_weight'][eid],
        bias=p['bias'][ids], time_const=p['time_const'][ids],
        input_local_index=inverse[imap[channel, pixel]], input_pixel_index=pixel_inverse[pixel],
        input_hex_global_index=retained_pixels)
    mapped = [dict(local_node_index=i, **rows[g]) for i, g in enumerate(ids)]
    table(folder/'node_map.csv', mapped)
    readout = np.flatnonzero(mask & (radius <= 1) & np.isin(types, TYPES)).astype(np.int64)
    assert len(readout) == 56
    np.save(folder/'readout_global_ids.npy', readout)
    np.save(folder/'readout_local_ids.npy', inverse[readout])
    incoming = (~mask[src]) & mask[dst]
    outgoing = mask[src] & (~mask[dst])
    np.save(folder/'deleted_incoming_original_edge_ids.npy', np.flatnonzero(incoming).astype(np.int64))
    np.save(folder/'deleted_outgoing_original_edge_ids.npy', np.flatnonzero(outgoing).astype(np.int64))
    counts = Counter(types[ids].tolist())
    # All graph edges, including original zero-weight edges, are counted.
    n, e = len(ids), len(eid)
    # Engineering layouts, not a frozen numeric profile or synthesized design.
    packed_edge_bytes = e * 8  # 32-bit weight + 16-bit source +16-bit target.
    state_param_bytes = n * 20  # old/new/chemical + bias/inverse-tau, 32 bits each.
    ptr_input_bytes = (n+1)*4 + len(retained_pixels)*8
    working_bytes = state_param_bytes + ptr_input_bytes
    manifest = dict(name=name, n_nodes=n, n_edges=e, n_input_pixels=len(retained_pixels),
        cell_type_counts=dict(counts), original_nodes=45669, original_edges=1513231,
        boundary_incoming_deleted=int(incoming.sum()), boundary_outgoing_deleted=int(outgoing.sum()),
        nonzero_incoming_deleted=int((incoming & (p['effective_weight'] != 0)).sum()),
        parameters_unchanged=True, edges_source='induced original graph in original-edge order',
        boundary_policy='deleted structure; no boundary current, surrogate or external neural states',
        readout='LOCAL_NEURAL_ROI_R1_56; not official optical flow',
        resources=dict(float32_edge_records_bytes=packed_edge_bytes,
            state_parameter_bytes=state_param_bytes, rowptr_input_bytes=ptr_input_bytes,
            working_bytes=working_bytes, estimated_all_onchip_bytes=working_bytes+packed_edge_bytes,
            BRAM36_nominal_total_bytes=140*4608, BRAM32_data_payload_total_bytes=140*4096,
            estimated_BRAM36_raw_blocks=int(np.ceil((working_bytes+packed_edge_bytes)/4608)),
            edge_ops_per_step=e, neuron_updates_per_step=n, edge_stream_MBps_at_200_model_steps_s=e*8*200/1e6,
            optimistic_100MHz_one_edge_per_cycle_ms=(e+6*n)/1e5,
            stage='ANALYTICAL_ESTIMATE_NO_SYNTHESIS_NO_BOARD', LUT_estimate=None, DSP_estimate=None),
        files={str(f.name):dict(sha256=sha(f), bytes=f.stat().st_size) for f in sorted(folder.iterdir())})
    dump(folder/'manifest.json', manifest)
    return manifest


def old3752_audit():
    base = LANE/'t4t5_sparse_recovery_20261011'
    spec = load(base/'EXPERIMENT_B.json')
    node_map = list(csv.DictReader((OLD/'cpu_preparation_r1/H_node_map.csv').open(encoding='utf-8-sig')))
    by_id = {int(r['global_node_index']): r for r in node_map}
    keep = np.load(base/'keep_3752.npy', allow_pickle=False)
    inactive = np.load(base/'inactive_3752.npy', allow_pickle=False)
    assert len(keep) == 3752 and len(inactive) == 2016 and not np.intersect1d(keep, inactive).size
    actual = [by_id[int(g)] for g in keep]
    counts = Counter(r['cell_type'] for r in actual)
    radii = [max(abs(int(r['u'])), abs(int(r['v'])), abs(int(r['u'])+int(r['v']))) for r in actual]
    for filename in ['keep_3752.npy', 'inactive_3752.npy']:
        assert sha(base/filename) == spec['source_pins'][str(base/filename)]
    source = (LANE/'t4t5_confirm_20261011/science_worker.py').read_text()
    operator = (LANE/'t4t5_confirm_20261011/sparse_operator.py').read_text()
    assert 'shape=(1,485,45669)' in source and 'state=initial.clone()' in source
    assert 'self.oracle.step(read,frame)' in operator
    from importlib.util import spec_from_file_location, module_from_spec
    ms = spec_from_file_location('historical_metrics', OLD/'metrics.py')
    module = module_from_spec(ms);ms.loader.exec_module(module)
    roi = np.load(OLD/'cpu_preparation_r1/flow_ROI_hex_indices.npy')
    previous = list(csv.DictReader((base/'sparsity_curve.csv').open(encoding='utf-8-sig')))
    recomputed = []
    for condition in SCREEN:
        flow_path = base/f'artifacts/gpu_r1/{condition}/KEEP_3752/flow.npy'
        sham_path = OLD/f'artifacts/pilot_gpu_r1/{condition}/Sham/flow.npy'
        flow = np.load(flow_path); sham = np.load(sham_path)
        values = module.vector_metrics(sham[0], flow[0], roi)
        row = next(r for r in previous if r['condition'] == condition and r['n_retained'] == '3752')
        for key in ['Q', 'magnitude_ratio', 'field_error_E', 'angle_deg']:
            assert abs(values[key]-float(row[key])) < 1e-12
        states_path = base/f'artifacts/gpu_r1/{condition}/KEEP_3752/activities_full.npy'
        states = np.load(states_path, mmap_mode='r')
        assert states.shape == (1,485,45669)
        record = load(base/f'artifacts/gpu_r1/{condition}/KEEP_3752/result.json')
        assert record['old_state_source'] == 'OWN_LIVE_COMMITTED_STATE'
        recomputed.append(dict(condition=condition, **values, original_result=record,
            sampled_R_state_variation=float(np.max(np.abs(states[0,210,0:100]-states[0,250,0:100]))),
            inactive_H_zero_at_k200_250_484=bool(np.all(states[0,[200,250,484]][:,inactive] == 0)),
            activity_shape=list(states.shape), flow_sha256=sha(flow_path)))
    audit = dict(status='PASS_SOURCE_SET_AND_ORIGINAL_FLOW_RECOMPUTATION',
        keep_n=3752, keep_per_type=dict(counts), radius_max=max(radii), positions_per_type=469,
        inactive_H=2016, R_still_recursively_computed=39901, n_state_variables=45669,
        effective_unclamped_nodes=3752+39901,
        structural_pruning=False, independent_3752_network_demonstrated=False,
        conditions=SCREEN, metrics=recomputed,
        conclusion='T4/T5 retention inside the full graph; cannot transfer its optical-flow figures to whole-network pruning',
        script_pins={str(p):sha(p) for p in [LANE/'t4t5_confirm_20261011/science_worker.py',LANE/'t4t5_confirm_20261011/sparse_operator.py',OLD/'metrics.py']})
    dump(HERE/'OLD_3752_AUDIT.json', audit)


def prepare():
    rows, types, radius, p = source_data()
    identity = load(BUNDLE/'identity_manifest.json')
    assert sha(BUNDLE/'expanded_parameters.npz') == identity['expanded_parameters_sha256']
    assert sha(BUNDLE/'initial_state_full.npy') == identity['initial_state_sha256']
    assert sha(BUNDLE/'nodes_full.csv') == identity['nodes_full_sha256']
    old3752_audit()
    unique = sorted(set(types.tolist())); ti = {t:i for i,t in enumerate(unique)}
    code = np.array([ti[t] for t in types], np.int64)
    src, dst, w = p['source_global'], p['target_global'], p['effective_weight']
    matrix = np.zeros((len(unique),len(unique)), np.int64)
    nonzero = w != 0
    np.add.at(matrix, (code[src[nonzero]], code[dst[nonzero]]), 1)
    htypes = {ti[t] for t in TYPES}
    direct = htypes | set(np.flatnonzero(matrix[:,sorted(htypes)].sum(axis=1)>0))
    closure = set(htypes); history=[]
    while True:
        nxt = closure | set(np.flatnonzero(matrix[:,sorted(closure)].sum(axis=1)>0))
        history.append([unique[i] for i in sorted(nxt)])
        if nxt == closure: break
        closure=nxt
    photo_lamina = [f'R{i}' for i in range(1,9)] + [f'L{i}' for i in range(1,6)]
    direct_types = sorted({unique[i] for i in direct} | set(photo_lamina))
    canonical_types = sorted(set(photo_lamina+TYPES+['Mi1','Mi4','Mi9','Tm1','Tm2','Tm3','Tm4','Tm9']))
    definitions = [(f'A_R{r}', radius <= r) for r in [2,3,4,6]]
    definitions += [('B_DIRECT_R4',(radius<=4)&np.isin(types,direct_types)),
                    ('B_CANONICAL_R4',(radius<=4)&np.isin(types,canonical_types))]
    manifests = [export_model(name,mask,rows,types,radius,p) for name,mask in definitions]
    export_model('CALIBRATION_FULL', np.ones(45669,bool),rows,types,radius,p)
    # Strongly connected type structure and predecessor closure are source analyses.
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    count, labels = connected_components(csr_matrix(matrix), directed=True, connection='strong')
    groups = [[unique[i] for i in np.flatnonzero(labels==g)] for g in range(count)]
    dump(HERE/'STRUCTURE.json',dict(type_matrix_nonzero_edge_counts=matrix.tolist(),ordered_types=unique,
        ancestor_type_closure=history,ancestor_closed_types=history[-1],
        excluded_nonancestor_types=sorted(set(unique)-set(history[-1])),
        strongly_connected_type_components=groups, direct_types=direct_types, canonical_types=canonical_types,
        models=manifests, data_source='original expanded graph; no activity-based structural selection'))
    stimuli=np.load(BUNDLE/'stimulus.npy',mmap_mode='r')
    assert stimuli.shape == (24,485,1,721)
    inputs=[]
    for condition in SCREEN+HOLDOUT:
        sample=SAMPLES[condition]
        path=HERE/f'inputs/{condition}.npy';path.parent.mkdir(exist_ok=True)
        np.save(path,np.array(stimuli[sample,:,0],copy=True))
        if condition in SCREEN+HOLDOUT[:2]:
            frozen=np.load(OLD/f'cpu_preparation_r1/{condition}_stimulus.npy')[0,:,0]
            assert np.array_equal(np.load(path),frozen)
        inputs.append(dict(condition=condition,sample=sample,shape=[485,721],sha256=sha(path)))
    pins={str(path):sha(path) for path in [HERE/'independent_model.py',HERE/'study.py',BUNDLE/'expanded_parameters.npz',BUNDLE/'initial_state_full.npy',BUNDLE/'nodes_full.csv',BUNDLE/'stimulus.npy',BUNDLE/'time.npy',FLY/'upstream/flyvis/flyvis/network/dynamics.py',FLY/'upstream/flyvis/flyvis/network/network.py',FLY/'upstream/flyvis/flyvis/network/stimulus.py']}
    protocol=dict(schema='whole-FlyVis-induced-pruning-study/v1',created_local_date='2026-10-13',
        status='FROZEN_BEFORE_CANDIDATE_FUNCTION_RUN',model_identity=identity,
        candidates=[m['name'] for m in manifests],screen_conditions=SCREEN,holdout_conditions=HOLDOUT,
        input_records=inputs,source_pins=pins,neural_dynamics='original continuous equations, original fp32 params, dt=.005',
        reduction='original edge order, np.add.at float32 target scatter; no CSR reorder, no quantization',
        initialization='candidate bias then 200 OWN gray .5 Euler warmup steps; save resulting candidate a0; movie has additional 200 presteps',
        boundary='induced graph; all cross-boundary edges removed, no replacement boundary or full-state input',
        ROI='all 8 T4/T5 types at radius<=1, 56 nodes with original global IDs',
        baseline_steps=[160,199],primary_steps=[200,285],tail_steps=[286,484],
        trace_metric='each candidate and reference subtract its OWN pre baseline; neural metrics distinct from original flow E/M/Q',
        thresholds=dict(reference_neural_RMS_floor=.001,trace_relative_error_max=.35,
            trace_correlation_min=.90,trace_amplitude_ratio_min=.60,trace_amplitude_ratio_max=1.40,
            reference_pair_contrast_min=.10,candidate_pair_contrast_min=.10,pair_contrast_delta_max=.20,
            direction_subtypes_required=3,polarity_family_angle_combinations_required=3,
            stability_abs_max=100,baseline_tail_slope_abs_max_per_step=.01),
        local_direction_readout='D=(positive-baseline-subtracted peak(direction)-peak(opposite))/(sum peaks+1e-12), per T4 ON and T5 OFF subtype',
        polarity_readout='same angle 60 and90: family (peak ON-peak OFF)/(sum+1e-12); T4 and T5 separately',
        official_DSI='not computed for candidates; four direction subsets are NOT full12direction DSI',
        decoder='NOT_RUN_NOT_APPLICABLE_MISSING_FULL_SPATIAL_INPUT; never zero-pad absent neurons to label official optical flow',
        selection='up to3 screen-passing models sorted by estimated edge+working bytes then neural E; heldout inputs closed until selection.json exists',
        fallback_if_no_screen_pass='validate smallest-E model as an explicit negative diagnostic; cannot mark functional PASS',
        validation='all4 heldout trace checks + opposite direction >=3 eligible subtypes + same-angle polarity >=3 combinations + stability + one deterministic OWN-state repeat ON240',
        limits=dict(max_CPU_wall_s_per_command=180,new_GPU_runs=0,max_candidate_count=6,max_final_count=3,
            threads=1,expected_new_storage_GiB_upper=1.0,no_new_RTL_or_BIT=True,no_parameter_tuning=True,no_24_condition_run=True),
        FPGA_estimation_source='AMD DS190 Z-7020: 53200 LUT, 140BRAM36,220DSP; no synthesis',
        fpga_source_url='https://www.amd.com/content/dam/xilinx/support/documents/data_sheets/ds190-Zynq-7000-Overview.pdf')
    protocol['identity_id']=hashlib.sha256(json.dumps(protocol,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    dump(HERE/'PREREGISTRATION.json',protocol)
    print(json.dumps(dict(status='PREPARED',models=[dict(name=m['name'],n=m['n_nodes'],e=m['n_edges']) for m in manifests],identity_id=protocol['identity_id']),ensure_ascii=False),flush=True)


def check_freeze():
    p=load(HERE/'PREREGISTRATION.json');body={k:v for k,v in p.items() if k!='identity_id'}
    assert hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()==p['identity_id']
    for path,expected in p['source_pins'].items():assert sha(path)==expected,path
    return p


def rollout(name,condition,stage):
    out=HERE/f'artifacts/{stage}/{name}/{condition}'
    out.mkdir(parents=True,exist_ok=False)
    model=IndependentModel(HERE/f'models/{name}/model.npz')
    input_global=np.load(HERE/f'inputs/{condition}.npy',allow_pickle=False)
    local=input_global[:,model.p['input_hex_global_index']].copy()
    np.save(out/'local_input.npy',local)
    initial=model.p['bias'].copy();state=initial.copy()
    start=time.perf_counter();journal=(out/'steps.jsonl').open('x',encoding='utf-8')
    warm=np.lib.format.open_memmap(out/'warmup_states.npy',mode='w+',dtype=np.float32,shape=(200,model.n))
    states=np.lib.format.open_memmap(out/'states.npy',mode='w+',dtype=np.float32,shape=(485,model.n))
    maximum=0.;row=0
    try:
        for phase,frames,dest in [('gray_warmup',np.full((200,model.n_pixels),.5,np.float32),warm),('movie',local,states)]:
            for k,frame in enumerate(frames):
                if time.perf_counter()-start>180:raise TimeoutError('CPU scope budget')
                old_hash=array_sha(state)
                candidate=model.step(state,frame)
                maximum=max(maximum,float(np.abs(candidate).max()))
                if maximum>100:raise FloatingPointError('predeclared divergence bound')
                state=candidate;dest[k]=state;row+=1
                journal.write(json.dumps(dict(phase=phase,step_id=k,status='COMMITTED',old_state_digest=old_hash,
                    new_state_digest=array_sha(state),input_digest=array_sha(frame),n_updated=model.n,
                    old_state_source='OWN_CANDIDATE_COMMITTED_STATE',external_neural_inputs=0))+'\n')
            if phase=='gray_warmup':np.save(out/'initial_state.npy',state)
        warm.flush();states.flush();journal.close()
        np.save(out/'final_state.npy',state)
        record=dict(status='PASS_INDEPENDENT_CPU_MULTI_STEP',run_id=str(uuid.uuid4()),name=name,condition=condition,
            stage=stage,warmup_steps=200,movie_steps=485,actual_neuron_updates=685*model.n,
            deleted_neuron_updates=0,external_neural_state_reads=0,full_network_calls=0,
            max_abs_state=maximum,all_finite=True,wall_s=time.perf_counter()-start,
            numpy=np.__version__,python=platform.python_version(),device='CPU_NUMPY_SINGLE_THREAD',
            candidate_model_sha256=sha(HERE/f'models/{name}/model.npz'),
            local_input_sha256=sha(out/'local_input.npy'),states_sha256=sha(out/'states.npy'),
            initial_state_sha256=sha(out/'initial_state.npy'),final_state_sha256=sha(out/'final_state.npy'),
            step_journal_sha256=sha(out/'steps.jsonl'),state_shape=[485,model.n],GPU_execution=False)
        dump(out/'result.json',record)
        print(json.dumps(dict(case=name,condition=condition,stage=stage,wall_s=record['wall_s'],max_state=maximum)),flush=True)
        return out
    except Exception as exc:
        warm.flush();states.flush();journal.close()
        dump(out/'FAILED.json',dict(status='FAILED_NO_RETRY',committed_steps=row,error=repr(exc)))
        raise


def reference(condition):
    existing=OLD/f'artifacts/pilot_gpu_r1/{condition}/Full/activities_full.npy'
    if existing.is_file():return np.load(existing,mmap_mode='r')[0]
    path=HERE/f'artifacts/extra_reference/{condition}/readout.npy'
    return np.load(path,mmap_mode='r')


def readout_ids():
    return np.load(HERE/'models/A_R2/readout_global_ids.npy')


def neural_metrics(candidate,ref,local_types):
    c=candidate.astype(np.float64);r=ref.astype(np.float64)
    cb=c[160:200].mean(axis=0);rb=r[160:200].mean(axis=0)
    cv=c[200:286]-cb;rv=r[200:286]-rb
    rms=float(np.sqrt(np.mean(rv**2)));energy=float(np.sum(rv**2))
    result=dict(reference_RMS=rms,baseline_offset_RMS=float(np.sqrt(np.mean((cb-rb)**2))),
        raw_trajectory_RMS_error=float(np.sqrt(np.mean((c-r)**2))),
        tail_abs_slope_max=float(np.max(np.abs(c[465:485].mean(axis=0)-c[445:465].mean(axis=0))/20)))
    if rms<.001 or energy==0:return dict(result,E=None,M=None,Q=None,correlation=None,trace_pass=False,reason='WEAK_REFERENCE')
    err=float(np.sqrt(np.sum((cv-rv)**2)/energy));mag=float(np.sqrt(np.sum(cv**2)/energy));q=float(np.sum(cv*rv)/energy)
    corr=float(np.corrcoef(cv.ravel(),rv.ravel())[0,1]) if np.std(cv)>1e-12 else None
    ok=bool(err<=.35 and corr is not None and corr>=.90 and .6<=mag<=1.4 and result['tail_abs_slope_max']<=.01)
    peaks_c={t:float(np.maximum(cv[:,local_types==t],0).max(axis=0).mean()) for t in TYPES}
    peaks_r={t:float(np.maximum(rv[:,local_types==t],0).max(axis=0).mean()) for t in TYPES}
    per_type=[]
    for typ in TYPES:
        select=local_types==typ;subref=rv[:,select];subval=cv[:,select];den=float(np.sum(subref**2))
        per_type.append(dict(type=typ,E=None if den<1e-12 else float(np.sqrt(np.sum((subval-subref)**2)/den)),
            candidate_peak=peaks_c[typ],reference_peak=peaks_r[typ]))
    return dict(result,E=err,M=mag,Q=q,correlation=corr,trace_pass=ok,
        candidate_type_peaks=peaks_c,reference_type_peaks=peaks_r,per_type=per_type)


def analyze_case(name,condition,stage):
    model=IndependentModel(HERE/f'models/{name}/model.npz')
    idx=np.load(HERE/f'models/{name}/readout_local_ids.npy')
    ids=readout_ids()
    mapping=list(csv.DictReader((HERE/f'models/{name}/node_map.csv').open(encoding='utf-8-sig')))
    types=np.array([mapping[i]['cell_type'] for i in idx])
    own=np.load(HERE/f'artifacts/{stage}/{name}/{condition}/states.npy',mmap_mode='r')[:,idx]
    ref=reference(condition)
    if ref.shape[-1]==45669:ref=ref[:,ids]
    values=neural_metrics(own,ref,types)
    dump(HERE/f'artifacts/{stage}/{name}/{condition}/metrics.json',values)
    return dict(name=name,condition=condition,stage=stage,**values)


def calibrate():
    check_freeze();model=IndependentModel(HERE/'models/CALIBRATION_FULL/model.npz')
    old=np.load(BUNDLE/'initial_state_full.npy').copy()
    frames=np.load(HERE/'inputs/ON60.npy')
    ref=np.load(OLD/'artifacts/pilot_gpu_r1/ON60/Full/activities_full.npy',mmap_mode='r')[0]
    errors=[];violations=0;start=time.perf_counter()
    for k,frame in enumerate(frames):
        old=model.step(old,frame)
        delta=np.abs(old-ref[k]);errors.append(float(delta.max()))
        violations+=int(np.count_nonzero(delta>1e-5+1e-5*np.abs(ref[k])))
    # Nonlinear memoryless step safety and explicit no-commit negative checks.
    small=IndependentModel(HERE/'models/A_R2/model.npz')
    state=small.p['bias'].copy();pixel=np.full(small.n_pixels,.5,np.float32)
    before=state.copy();one=small.step(state,pixel)
    assert np.array_equal(state,before)
    assert np.array_equal(one,small.step(state,pixel))
    negative=[]
    for label,s,x in [('nan_state',np.full(small.n,np.nan,np.float32),pixel),('nan_pixel',state,np.full(small.n_pixels,np.nan,np.float32)),('wrong_state_size',state[:-1],pixel),('out_of_range_pixel',state,np.full(small.n_pixels,2,np.float32))]:
        try:small.step(s,x)
        except ValueError:negative.append(label)
        else:raise AssertionError('negative accepted')
    np.save(HERE/'calibration_per_step_max_error.npy',np.array(errors,np.float64))
    dump(HERE/'CALIBRATION.json',dict(status='PASS' if violations==0 else 'FAIL_NUMERIC_GATE',
        original_full_movie_steps=485,all_nodes_checked=45669,max_error=max(errors),tolerance=dict(atol=1e-5,rtol=1e-5),
        violating_elements=violations,wall_s=time.perf_counter()-start,
        reference_path=str(OLD/'artifacts/pilot_gpu_r1/ON60/Full/activities_full.npy'),
        reference_sha256=sha(OLD/'artifacts/pilot_gpu_r1/ON60/Full/activities_full.npy'),
        original_old_state_not_modified=True,deterministic_single_step=True,negative_cases_rejected=negative,
        scope='one full CPU calibration; not candidate-independent function proof',GPU_execution=False))
    assert violations==0,'calibration failed; do not run scientific candidate screening'
    print(json.dumps(load(HERE/'CALIBRATION.json')),flush=True)


def screen():
    p=check_freeze();assert load(HERE/'CALIBRATION.json')['status']=='PASS'
    start=time.perf_counter();records=[];scores=[]
    for name in p['candidates']:
        results=[]
        for condition in SCREEN:
            rollout(name,condition,'screen');results.append(analyze_case(name,condition,'screen'))
        records.extend(results);manifest=load(HERE/f'models/{name}/manifest.json')
        scores.append(dict(name=name,screen_pass=all(r['trace_pass'] for r in results),
            mean_neural_E=float(np.mean([r['E'] for r in results])),
            resource_bytes=manifest['resources']['estimated_all_onchip_bytes'],n_nodes=manifest['n_nodes'],n_edges=manifest['n_edges']))
    passing=sorted([s for s in scores if s['screen_pass']],key=lambda s:(s['resource_bytes'],s['mean_neural_E']))
    selected=[s['name'] for s in passing[:3]]
    diagnostic=False
    if not selected:selected=[min(scores,key=lambda s:s['mean_neural_E'])['name']];diagnostic=True
    dump(HERE/'SCREEN_RESULTS.json',dict(status='COMPLETED_SCREEN_ONLY',scores=scores,metrics=records,wall_s=time.perf_counter()-start))
    dump(HERE/'selection.json',dict(status='FROZEN_BEFORE_HOLDOUT',selected=selected,diagnostic_only=diagnostic,
        selection_rule=p['selection'],screen_identity=p['identity_id'],screen_results_sha256=sha(HERE/'SCREEN_RESULTS.json')))
    print(json.dumps(load(HERE/'selection.json')),flush=True)


def extra_full_references():
    model=IndependentModel(HERE/'models/CALIBRATION_FULL/model.npz');ids=readout_ids()
    for condition in HOLDOUT[2:]:
        out=HERE/f'artifacts/extra_reference/{condition}';out.mkdir(parents=True,exist_ok=False)
        state=np.load(BUNDLE/'initial_state_full.npy').copy()
        frames=np.load(HERE/f'inputs/{condition}.npy');readout=[];maximum=0;start=time.perf_counter()
        for k,frame in enumerate(frames):
            state=model.step(state,frame);readout.append(state[ids].copy());maximum=max(maximum,float(abs(state).max()))
        np.save(out/'readout.npy',np.array(readout,np.float32));np.save(out/'final_state.npy',state)
        dump(out/'result.json',dict(status='ACTUAL_INDEPENDENT_FULL_EQUATION_CPU_REFERENCE',condition=condition,
            run_id=str(uuid.uuid4()),model_nodes=45669,model_edges=1513231,actual_steps=485,wall_s=time.perf_counter()-start,
            max_abs_state=maximum,calibration_sha256=sha(HERE/'CALIBRATION.json'),readout_global_ids=ids.tolist(),
            readout_sha256=sha(out/'readout.npy'),official_torch_update_called=False,GPU_execution=False))


def contrast(a,b):
    return float((a-b)/(a+b+1e-12))


def validate():
    check_freeze();selected=load(HERE/'selection.json');start=time.perf_counter()
    extra_full_references();results=[];summary=[]
    for name in selected['selected']:
        by_condition={condition:load(HERE/f'artifacts/screen/{name}/{condition}/metrics.json') for condition in SCREEN}
        for condition in HOLDOUT:
            rollout(name,condition,'holdout');metrics=analyze_case(name,condition,'holdout')
            results.append(metrics);by_condition[condition]=metrics
        opposite=[]
        for family,pos,neg in [('T4','ON60','ON240'),('T5','OFF90','OFF270')]:
            for subtype in 'abcd':
                typ=family+subtype
                pc=by_condition[pos]['candidate_type_peaks'][typ];nc=by_condition[neg]['candidate_type_peaks'][typ]
                pr=by_condition[pos]['reference_type_peaks'][typ];nr=by_condition[neg]['reference_type_peaks'][typ]
                ref=contrast(pr,nr);cand=contrast(pc,nc)
                eligible=bool(max(pr,nr)>=.001 and abs(ref)>=.1)
                kept=bool(eligible and np.sign(ref)==np.sign(cand) and abs(cand)>=.1 and abs(cand-ref)<=.2)
                opposite.append(dict(type=typ,positive_condition=pos,opposite_condition=neg,reference_D=ref,candidate_D=cand,
                    reference_eligible=eligible,direction_preserved=kept,metric='LOCAL_OPPOSITE_CONTRAST_NOT_OFFICIAL_DSI'))
        polarity=[]
        for angle in [60,90]:
            for family in ['T4','T5']:
                sums=[]
                for key in ['reference_type_peaks','candidate_type_peaks']:
                    on=np.mean([by_condition[f'ON{angle}'][key][family+s] for s in 'abcd'])
                    off=np.mean([by_condition[f'OFF{angle}'][key][family+s] for s in 'abcd'])
                    sums.append((float(on),float(off),contrast(on,off)))
                (on_r,off_r,ref),(on_c,off_c,cand)=sums
                eligible=bool(max(on_r,off_r)>=.001 and abs(ref)>=.1)
                kept=bool(eligible and np.sign(ref)==np.sign(cand) and abs(cand)>=.1 and abs(cand-ref)<=.2)
                polarity.append(dict(family=family,angle=angle,reference_P=ref,candidate_P=cand,
                    reference_ON_peak=on_r,reference_OFF_peak=off_r,candidate_ON_peak=on_c,candidate_OFF_peak=off_c,
                    reference_eligible=eligible,polarity_preserved=kept))
        # Exactly one fresh own-state repeat; no reference-driven rollout.
        out=rollout(name,'ON240','repeat')
        original=HERE/f'artifacts/holdout/{name}/ON240'
        repeat_equal=sha(out/'states.npy')==sha(original/'states.npy') and sha(out/'initial_state.npy')==sha(original/'initial_state.npy')
        all_trace=all(m['trace_pass'] for m in by_condition.values())
        functional=bool(not selected['diagnostic_only'] and all_trace and sum(r['direction_preserved'] for r in opposite)>=3 and sum(r['polarity_preserved'] for r in polarity)>=3 and repeat_equal)
        summary.append(dict(name=name,independent_recursion=True,all_6_trace_checks_pass=all_trace,
            opposite_direction_subtypes_preserved=sum(r['direction_preserved'] for r in opposite),
            polarity_combinations_preserved=sum(r['polarity_preserved'] for r in polarity),repeat_bitwise_equal=repeat_equal,
            functional_acceptance=bool(functional),opposite_direction=opposite,polarity=polarity,
            heldout_neural_E={c:by_condition[c]['E'] for c in HOLDOUT},
            repeat_run_id=load(out/'result.json')['run_id'],original_run_id=load(original/'result.json')['run_id']))
    dump(HERE/'VALIDATION_RESULTS.json',dict(status='COMPLETED_FIXED_FIRST_BATCH',selected=summary,
        metrics=results,wall_s=time.perf_counter()-start,thresholds_changed=False,new_GPU_runs=0))
    print(json.dumps(dict(status='COMPLETED_FIXED_FIRST_BATCH',summary=[{k:v for k,v in row.items() if k not in ['opposite_direction','polarity']} for row in summary])),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','calibrate','screen','validate'])
    globals()[parser.parse_args().stage]()
