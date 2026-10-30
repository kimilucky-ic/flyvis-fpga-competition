"""Thin data binding to NAVis/Octarine. No renderer or morphology implementation."""
from pathlib import Path
import json, os

ROOT = Path(__file__).resolve().parent
for key, name in [('MPLCONFIGDIR','matplotlib'),('PYGFX_DATA_DIR','pygfx'),('XDG_CACHE_HOME','other')]:
    p = ROOT / 'runtime_cache' / name
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ['OCTARINE_CHECK_LOOP'] = '0'
os.environ['RENDERCANVAS_BACKEND'] = 'qt'
os.environ['QT_API'] = 'pyside6'
os.environ['WGPU_BACKEND_TYPE'] = 'D3D12'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['LP_NUM_THREADS'] = '2'

import numpy as np
import wgpu
from wgpu.utils import preconfigure_default_device

def research_guard():
    """Observe other lanes only; never stop or modify their work."""
    import psutil
    busy = []
    for p in psutil.process_iter(['name','cmdline']):
        try:
            name = (p.info['name'] or '').lower()
            cmd = ' '.join(p.info['cmdline'] or [])
            if name in ('wsl.exe','vivado.exe','vitis.exe') or (name.startswith('python') and any(x in cmd for x in ('--worker','single_controller.py --execute','live_worker.py','camera_stream_worker.py'))):
                busy.append({'pid':p.pid,'name':name})
        except psutil.Error:
            continue
    markers_dir = ROOT.parents[2] / 'fpga/flyvis-autorunner/runtime'
    markers = [n for n in ('EXTERNAL_GPU_BUSY.json','BOARD_RESERVED.json','RESOURCE_QUARANTINE.json') if (markers_dir/n).exists()]
    return dict(busy=busy,markers=markers,free_bytes=psutil.virtual_memory().available)

def configure_renderer(mode='gpu'):
    if mode == 'gpu':
        state = research_guard()
        if state['busy'] or state['markers']:
            raise RuntimeError('②⑦科研任务正在使用资源，GPU 演示暂缓打开。可使用 openreplay_cpu.cmd。\n'+json.dumps(state,ensure_ascii=False))
    adapters = wgpu.gpu.enumerate_adapters_sync()
    kinds = ('DiscreteGPU','IntegratedGPU') if mode=='gpu' else ('CPU',)
    adapter = next((a for kind in kinds for a in adapters if a.info['adapter_type']==kind and a.info['backend_type']=='D3D12'),None)
    if adapter is None:
        raise RuntimeError(f'未找到所选绘制设备：{mode}。不会静默切换到其它设备。')
    preconfigure_default_device('line10 '+mode+' display only', adapter=adapter)
    return dict(adapter.info)

def configure_cpu():
    return configure_renderer('cpu')

class AnatomyScene:
    def init__(self, model_path=ROOT / 'model.json', offscreen=False, size=(960,720), max_fps=20):
        import navis
        import octarine as oc
        import octarine_navis_plugin
        import trimesh
        from cloudvolume import Mesh
        self.model = json.loads(Path(model_path).read_text(encoding='utf-8'))
        with np.load(Path(model_path).parent / self.model['activity_file']) as data:
            self.activity, self.time = data['activity'], data['time']
        self.objects = self.model['objects']
        assert self.activity.shape == (len(self.time),len(self.objects))
        self.low = np.array([o['color_min'] for o in self.objects])
        self.high = np.array([o['color_max'] for o in self.objects])
        self.frame = 0
        self.v = v = oc.Viewer(offscreen=offscreen, show=False, size=size, max_fps=max_fps, headlight=True,
                               title='FlyVis Anatomy Replay')
        v.renderer.pixel_ratio = 1
        v.set_bgcolor('#091320')
        self.neurons = []
        for item in self.objects:
            n = navis.read_swc(item['swc'], units=item['swc_units']).convert_units('um')
            n.id, n.name = item['body_id'], item['name']
            self.neurons.append(n)
            v.add_neurons(n, color='#a8e3ff', linewidth=3.5, radius=False, soma=False, center=False, name=n.name)
        for item in self.model['rois']:
            m = Mesh.from_precomputed(Path(item['path']).read_bytes(), segid=item['segment_id'])
            v.add_mesh(trimesh.Trimesh(vertices=np.asarray(m.vertices)/1000, faces=m.faces,process=False),
                       name=item['name'], color=item['color'], alpha=.075, silhouette=1, center=False)
        v.set_scalebar(25, units='um', color='#b9c8d9')
        v.on_hover = None
        v.on_double_click = None
        v.objects_pickable = True
        # Brain regions remain visible but cannot intercept neuron selections.
        for roi in self.model['rois']:
            for visual in v.objects[roi['name']]:
                if hasattr(visual,'material'):
                    visual.material.pick_write = False
        self.bounds = navis.NeuronList(self.neurons).bbox
        self.detail_view()
        v.render_trigger = 'reactive'
        self.set_frame(0)
        v.show()

    def detail_view(self):
        center = self.bounds.mean(axis=1)
        radius = float(np.linalg.norm(self.bounds[:,1] - self.bounds[:,0])/2)
        self.v.camera.show_object((*center,radius),view_dir=(1,-.4,.5),up=(0,-1,0),scale=1.22)
        self.v.canvas.request_draw()

    def overview(self):
        self.v.center_camera()
        self.v.set_view('XY')

    def set_frame(self, index):
        self.frame = int(np.clip(index,0,len(self.time)-1))
        self.level = np.divide(self.activity[self.frame]-self.low,self.high-self.low,
                               out=np.zeros_like(self.low),where=(self.high!=self.low))
        # Fixed, monotonic-luminance palette, shared by UI and the mature renderer.
        stops = np.array([[.09,.23,.34],[.08,.58,.75],[.52,.88,.91],[1.,.91,.53],[1.,.99,.91]])
        self.colors = np.stack([np.interp(self.level,np.linspace(0,1,len(stops)),stops[:,j]) for j in range(3)],axis=1)
        self.v.set_colors({o['name']:tuple(c) for o,c in zip(self.objects,self.colors)})
        self.v.canvas.request_draw()
