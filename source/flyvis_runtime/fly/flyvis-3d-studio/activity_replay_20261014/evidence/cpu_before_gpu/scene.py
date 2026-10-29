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

def configure_cpu():
    # Explicit CPU adapter; fail rather than silently borrow the research GPU.
    adapters = wgpu.gpu.enumerate_adapters_sync()
    adapter = next((a for a in adapters if a.info['adapter_type'] == 'CPU' and a.info['backend_type'] == 'D3D12'), None)
    if adapter is None:
        raise RuntimeError('未找到 Windows CPU 软件绘制后端；为避让科研 GPU，本程序不会自动改用独立显卡。')
    preconfigure_default_device('line10 software-only replay', adapter=adapter)
    return dict(adapter.info)

class AnatomyScene:
    def init__(self, model_path=ROOT / 'model.json', offscreen=False, size=(960,720)):
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
        self.v = v = oc.Viewer(offscreen=offscreen, show=False, size=size, max_fps=20, headlight=True,
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
