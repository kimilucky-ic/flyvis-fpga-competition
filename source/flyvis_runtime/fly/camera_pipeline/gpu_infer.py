"""Offline original full-network inference. Existing accepted WSL GPU environment only."""
from __future__ import annotations
import argparse
import csv
import gc
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from camera_pipeline.common import ROOT,new_directory,sha256,utc_now,write_json

CHECKPOINT_SHA='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'
SOURCE_COMMIT='92b3845cc426dd309a1a0e1b3890156c42e14021'

def run(dataset,destination,*,device='cuda'):
    destination=new_directory(destination)
    status_path=destination/'gpu_status.json'
    job_id=destination.name
    write_json(status_path,{'schema':'flyvis-camera-gpu-status-v1','job_id':job_id,'state':'queued',
                           'input':str(dataset),'output':str(destination),'pid':os.getpid()})
    # All persistent results in this lane; Linux-native scratch isolates HDF5 metadata caches.
    scratch=Path(tempfile.mkdtemp(prefix='flyvis-camera-'))
    model_path=scratch/'results/flow/0000/000'
    original=Path('/opt/flyvis-gpu-data/results/flow/0000/000')
    shutil.copytree(original,model_path,ignore=shutil.ignore_patterns('__cache__'))
    os.environ.update(CUDA_VISIBLE_DEVICES='0' if device=='cuda' else '-1',FLYVIS_ROOT_DIR=str(scratch),
                      MPLBACKEND='Agg',MPLCONFIGDIR=str(ROOT/'runtime/matplotlib_wsl'),
                      NUMBA_CACHE_DIR=str(scratch/'numba'),TIMEZONE='Asia/Shanghai',CUBLAS_WORKSPACE_CONFIG=':4096:8')
    import numpy as np
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    torch.manual_seed(0);np.random.seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    import flyvis
    from flyvis import NetworkView
    from flyvis.utils.nn_utils import simulation
    from camera_pipeline.adapter import load_stimulus
    record={'schema':'flyvis-camera-inference-v1','created_utc':utc_now(),'device':device,
            'job_id':job_id,
            'model':'flow/0000/000','execution_kind':'new_inference','source_commit':SOURCE_COMMIT,
            'python':sys.version,'torch':torch.__version__,'cuda_version':torch.version.cuda,
            'flyvis':flyvis.__version__,'os':platform.platform(),'linux_native_scratch':str(scratch),
            'input_directory':str(Path(dataset).resolve()),'initialization':'one independent clip, 1 s grey 0.5 once before movie',
            'network_mode':'original full continuous clip; no frame/window resets','decoder_executed':False,
            'weights_modified':False,'dt_s':.005,'real_time_claim':False}
    write_json(status_path,{'schema':'flyvis-camera-gpu-status-v1','job_id':job_id,'state':'running','input':str(dataset),'output':str(destination),'pid':os.getpid()})
    def sync():
        if device=='cuda':torch.cuda.synchronize()
    def timed(function):
        sync()
        if device=='cuda':torch.cuda.reset_peak_memory_stats()
        start=time.perf_counter();value=function();sync()
        metrics={'elapsed_s':time.perf_counter()-start}
        if device=='cuda':metrics.update(peak_allocated_MiB=torch.cuda.max_memory_allocated()/2**20,
                                       peak_reserved_MiB=torch.cuda.max_memory_reserved()/2**20)
        return value,metrics
    try:
        assert flyvis.device.type==device
        if device=='cuda':
            record.update(gpu=torch.cuda.get_device_name(0),compute_capability=torch.cuda.get_device_capability(0))
            actual=torch.arange(1024,device='cuda');assert int(actual.sum())==523776
            del actual
        actual_commit=subprocess.check_output(['git','-C',str(ROOT.parent/'upstream/flyvis'),'rev-parse','HEAD'],text=True).strip()
        assert actual_commit==SOURCE_COMMIT
        stimulus,grid,coordinates,metadata=load_stimulus(dataset)
        # These first acceptance runs are A only; alternative geometry cannot silently enter them.
        assert metadata['spatial_transform']['policy']=='native'
        assert metadata['dt_s']==.005
        record.update(input_sha256=sha256(Path(dataset)/'stimulus.npy'),input_shape=list(stimulus.shape),
                      input_source_kind=metadata['source']['source_kind'],temporal_method=metadata['temporal_method'],
                      dt_s=metadata['dt_s'],camera_measured_delivery_fps=metadata['source'].get('measured_delivery_fps'),
                      simulation_fps=1/metadata['dt_s'])
        view=NetworkView(model_path)
        checkpoint=Path(view.get_checkpoint('best'))
        record['checkpoint_sha256']=sha256(checkpoint)
        assert record['checkpoint_sha256']==CHECKPOINT_SHA
        expected=torch.load(checkpoint,map_location='cpu',weights_only=False)['network']
        def restore():
            wrapper=view.network(checkpoint='best',lazy=True);wrapper.recover();return wrapper
        wrapper,record['model_load']=timed(restore)
        network=wrapper.network
        network.eval()
        for param in network.parameters():param.requires_grad_(False)
        def unchanged():
            actual=network.state_dict()
            return set(actual)==set(expected) and all(torch.equal(actual[key].detach().cpu(),value) for key,value in expected.items())
        assert unchanged()
        record.update(neurons=network.n_nodes,edges=network.n_edges,weights_exact_before=True)
        assert (network.n_nodes,network.n_edges)==(45669,1513231)
        central=network.connectome.central_cells_index[:]
        types=network.connectome.unique_cell_types[:].astype(str)
        u=np.array([int(c['u']) for c in coordinates]);v=np.array([int(c['v']) for c in coordinates])
        for input_index in network.stimulus.input_index:
            np.testing.assert_array_equal(network.connectome.nodes.u[:][input_index],u)
            np.testing.assert_array_equal(network.connectome.nodes.v[:][input_index],v)
        record['coordinate_order_verified_against_network']=True
        movie,record['host_to_device']=timed(lambda:torch.tensor(np.array(stimulus),dtype=torch.float32,device=flyvis.device))
        with simulation(network):
            initial,record['initialization_timing']=timed(lambda:network.steady_state(1,.005,len(movie),value=.5))
            activity,record['inference']=timed(lambda:network.simulate(movie,dt=.005,initial_state=initial))
        assert unchanged()
        record['weights_exact_after']=True
        assert torch.isfinite(activity).all()
        central_activity,record['device_to_host']=timed(lambda:activity[:,:,central].detach().cpu().numpy())
        record['full_activity_shape']=list(activity.shape)
        del activity,movie,initial;gc.collect()
        if device=='cuda':torch.cuda.empty_cache()
        targets=[f'T{n}{suffix}' for n in (4,5) for suffix in 'abcd']
        target_index=[list(types).index(name) for name in targets]
        target_activity=central_activity[:,:,target_index]
        with (destination/'neurons.csv').open('w',newline='',encoding='utf-8') as handle:
            writer=csv.writer(handle);writer.writerow(['cell_type_axis','cell_type','original_node_index','u','v'])
            for index,(cell_type,node_index) in enumerate(zip(types,central)):
                writer.writerow([index,cell_type,int(node_index),0,0])
        for name,value in [('activity_central',central_activity),('activity_T4_T5',target_activity),
                           ('cell_types',types),('central_node_indices',central),('time',grid),('activity_time',grid+.005)]:
            np.save(destination/f'{name}.npy',value,allow_pickle=False)
        with (destination/'activity_T4_T5.csv').open('w',newline='',encoding='utf-8') as handle:
            writer=csv.writer(handle);writer.writerow(['sample','input_time_s','activity_after_update_time_s',*targets])
            for sample in range(len(central_activity)):
                for frame,t in enumerate(grid):writer.writerow([sample,t,t+.005,*target_activity[sample,frame]])
        shutil.copyfile(Path(dataset)/'time_alignment.csv',destination/'time_alignment.csv')
        record.update(status='PASS',activity_shape=list(central_activity.shape),activity_dtype=str(central_activity.dtype),
                      activity_axes=['sample','frame','central_cell_type'],activity_spatial_scope='one center neuron (u=v=0) for each of 65 types',
                      target_axes=['sample','frame','central_T4_T5_cell_type'],target_types=targets,
                      simulated_steps_per_sample=len(grid),simulation_compute_steps_per_s=len(grid)/record['inference']['elapsed_s'],
                      central_activity_range=[float(central_activity.min()),float(central_activity.max())],
                      result_time_semantics='time.npy is input presentation grid; activity_time.npy is post-update time',
                      limitations=['camera FOV/physical speed uncalibrated','ordinary real scene, not controlled motion stimuli',
                                   'offline continuous clip; live capture-to-output latency not tested'])
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
        for panel,n in zip(axes,(4,5)):
            for suffix in 'abcd':
                name=f'T{n}{suffix}';panel.plot(grid+.005,central_activity[0,:,list(types).index(name)],label=name,linewidth=1)
            panel.set_ylabel('central model activity (a.u.)');panel.legend(ncol=4);panel.grid(alpha=.2)
        axes[-1].set_xlabel('model post-update time from first captured frame (s)')
        fig.suptitle(f"Actual {record['input_source_kind']} -> original full FlyVis | {device} | {record['temporal_method']} | dt=5 ms")
        fig.tight_layout();fig.savefig(destination/'activity_T4_T5.png',dpi=150);plt.close(fig)
        record['data_sha256']={p.name:sha256(p) for p in destination.iterdir() if p.suffix in ('.npy','.csv','.png')}
        write_json(destination/'result.json',record)
        write_json(status_path,{'schema':'flyvis-camera-gpu-status-v1','job_id':job_id,'state':'complete','input':str(dataset),'output':str(destination),'result':'result.json'})
        print(json.dumps(record),flush=True)
        return record
    except BaseException as error:
        record.update(status='FAIL',error=str(error),error_type=type(error).__name__)
        write_json(destination/'failure.json',record)
        write_json(status_path,{'schema':'flyvis-camera-gpu-status-v1','job_id':job_id,'state':'failed','error':str(error),'error_type':type(error).__name__})
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('dataset',type=Path);p.add_argument('destination',type=Path)
    p.add_argument('--device',choices=['cuda','cpu'],default='cuda');a=p.parse_args()
    run(a.dataset,a.destination,device=a.device)
