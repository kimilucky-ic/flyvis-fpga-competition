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
from presentation import scale_info, sha, color_encoding, type_activity_colors

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
    def init__(self, model_path=ROOT / 'model.json', offscreen=False, size=(960,720), max_fps=20, profile='standard'):
        import navis
        import octarine as oc
        import octarine_navis_plugin
        self.model_path = Path(model_path)
        self.model = json.loads(self.model_path.read_text(encoding='utf-8'))
        with np.load(Path(model_path).parent / self.model['activity_file']) as data:
            self.activity, self.time = data['activity'], data['time']
        self.objects = self.model['objects']
        assert self.activity.shape == (len(self.time),len(self.objects))
        self.scale = scale_info(self.activity)
        self.color_encoding = color_encoding(self.objects,self.activity)
        self.type_filter = 'all'
        self.frame = 0
        self.v = v = oc.Viewer(offscreen=offscreen, show=False, size=size, max_fps=max_fps, headlight=True,
                               title='FlyVis Anatomy Replay')
        v.renderer.pixel_ratio = 1
        v.set_bgcolor('#091320')
        self.neurons, self.neuron_points = [], []
        for item in self.objects:
            n = navis.read_swc(item['swc'], units=item['swc_units']).convert_units('um')
            n.id, n.name = item['body_id'], item['name']
            self.neurons.append(n)
            self.neuron_points.append(n.nodes[['x','y','z']].to_numpy(dtype=np.float64))
            v.add_neurons(n, color='#a8e3ff', linewidth=3.5, radius=False, soma=False, center=False, name=n.name)
        self._background_names = {'light':[], 'standard':[]}
        self._background_geometry = {'light':[], 'standard':[]}
        self.background_manifest_sha256 = None
        self.lod_manifest = None
        manifest_path = self.model_path.parent / self.model.get('roi_lod_manifest','roi_lod_20261015/manifest.json')
        if manifest_path.exists():
            self.lod_manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            self.lod_folder = manifest_path.parent
            self.background_manifest_sha256 = sha(manifest_path)
        self.profile = None
        v.set_scalebar(25, units='um', color='#b9c8d9')
        v.on_hover = None
        v.on_double_click = None
        v.objects_pickable = True
        self.set_profile(profile)
        self.bounds = navis.NeuronList(self.neurons).bbox
        self.detail_view()
        v.render_trigger = 'reactive'
        self.set_frame(0)
        v.show()

    @property
    def rois_visible(self):
        names=self._background_names[self.profile]
        return bool(names and all(visual.visible for name in names for visual in self.v.objects[name]))

    @property
    def background_style(self):
        return 'simplified_mesh' if self.profile=='light' else 'full_mesh'

    @property
    def background_geometry(self):
        return self._background_geometry[self.profile]

    def _load_background(self, profile):
        import trimesh
        if self._background_names[profile] or not self.model['rois']: return
        lods={item['name']:item for item in self.lod_manifest['rois']} if self.lod_manifest else {}
        for item in self.model['rois']:
            if profile=='light':
                if item['name'] not in lods: raise ValueError('Missing source-derived ROI LOD; run prepare_roi_lod.py')
                source=lods[item['name']]
                if source['source_sha256']!=item['sha256']: raise ValueError('ROI LOD source identity mismatch')
                path=self.lod_folder/source['derived_file']
                if sha(path)!=source['derived_sha256']: raise ValueError('Derived ROI SHA mismatch')
                with np.load(path) as data: vertices,faces=data['vertices_um'],data['faces']
                if len(vertices)!=source['derived_vertices'] or len(faces)!=source['derived_faces']:
                    raise ValueError('Derived ROI geometry count mismatch')
                name=item['name']+' [LOD]'
                info=dict(name=item['name'],segment_id=item['segment_id'],source_sha256=item['sha256'],
                          source_vertices=source['source_vertices'],source_faces=source['source_faces'],
                          rendered_vertices=len(vertices),rendered_faces=len(faces),rendered_sha256=source['derived_sha256'],
                          rendered_path=str(path),units='um',source_units='nm',algorithm=source['algorithm'],
                          vtk_version=source['vtk_version'],target_reduction=source['target_reduction'],
                          volume_preservation=source['volume_preservation'],approximate_spatial_reference=True)
            else:
                from cloudvolume import Mesh
                raw=Mesh.from_precomputed(Path(item['path']).read_bytes(),segid=item['segment_id'])
                vertices,faces=np.asarray(raw.vertices)/1000,raw.faces
                name=item['name']
                info=dict(name=item['name'],segment_id=item['segment_id'],source_sha256=item['sha256'],
                          source_vertices=len(vertices),source_faces=len(faces),rendered_vertices=len(vertices),
                          rendered_faces=len(faces),rendered_sha256=item['sha256'],rendered_path=item['path'],
                          source_units='nm',units='um',algorithm='none',approximate_spatial_reference=False)
            self.v.add_mesh(trimesh.Trimesh(vertices=vertices,faces=faces,process=False),name=name,
                            color=item['color'],alpha=.075,silhouette=1,center=False)
            for visual in self.v.objects[name]:
                if hasattr(visual,'material'): visual.material.pick_write=False
            self._background_names[profile].append(name)
            self._background_geometry[profile].append(info)

    def set_profile(self, profile):
        """Switch full/source-derived ROI reference; retain original coordinates."""
        if profile not in ('light','standard'):
            raise ValueError('Unknown rendering profile: ' + str(profile))
        if profile == self.profile: return
        self._load_background(profile)
        for key,names in self._background_names.items():
            if names:
                if key==profile: self.v.unhide_objects(names)
                else: self.v.hide_objects(names)
        self.profile = profile
        self.v.render_trigger = 'reactive'
        self.v.canvas.request_draw()

    def detail_view(self):
        shown = [n.bbox for n,o in zip(self.neurons,self.objects) if self.type_filter in ('all',o['type'],o['type'][:2])]
        bounds = np.stack([np.min([b[:,0] for b in shown],axis=0),np.max([b[:,1] for b in shown],axis=0)],axis=1)
        center = bounds.mean(axis=1)
        radius = float(np.linalg.norm(bounds[:,1] - bounds[:,0])/2)
        with self.v.controller.pause():  # Cancel pending gestures before a programmatic reset.
            self.v.camera.show_object((*center,radius),view_dir=(1,-.4,.5),up=(0,-1,0),scale=1.22)
            self.fit_before = self.projection_info()
            # Fit the real node projection, rather than its conservative 3-D sphere.
            factor=max(self.fit_before['width_fraction'],self.fit_before['height_fraction'])/.86
            if factor>0:
                self.v.camera.width *= factor
                self.v.camera.height *= factor
            self.sync_camera_controller()
            info=self.projection_info()
            x0,y0,x1,y1=info['bbox_px'];width,height=self.v.size
            self.v.controller.pan((width/2-(x0+x1)/2,height/2-(y0+y1)/2),
                                  (0,0,width,height),animate=False)
            self.sync_camera_controller()
        self.v.canvas.request_draw()

    def sync_camera_controller(self):
        # pygfx 0.17.0 gesture helpers merge partial updates into cached state.
        # Copy the complete state after direct camera changes, or a later pan/
        # rotate can restore stale orientation/width. This is a thin API binding.
        self.v.controller._set_camera_state(self.v.camera.get_state())

    def projection_info(self):
        """Measure real skeleton vertices using the mature camera's projection."""
        width,height=self.v.size
        camera=self.v.camera
        camera.set_view_size(width,height)
        points=np.concatenate([p for p,o in zip(self.neuron_points,self.objects)
                               if self.type_filter in ('all',o['type'],o['type'][:2])])
        clip=np.column_stack([points,np.ones(len(points))]) @ camera.camera_matrix.T
        ndc=clip[:,:3]/clip[:,3,None]
        pixel=np.column_stack([(ndc[:,0]+1)*width/2,(1-ndc[:,1])*height/2])
        low,high=pixel.min(0),pixel.max(0)
        cropped=np.any((ndc[:,:2]<-1-1e-7)|(ndc[:,:2]>1+1e-7),axis=1)|(ndc[:,2]<-1e-7)|(ndc[:,2]>1+1e-7)
        return dict(strategy='projected_visible_skeleton_bbox',target_max_fill=.86,
                    bbox_px=[float(low[0]),float(low[1]),float(high[0]),float(high[1])],
                    width_fraction=float((high[0]-low[0])/width),height_fraction=float((high[1]-low[1])/height),
                    cropped_node_count=int(cropped.sum()),projected_node_count=len(points),
                    measurement='Original SWC nodes in um through pygfx camera_matrix; no geometry transform',
                    viewport=dict(width=int(width),height=int(height)),
                    before_default_fit={k:self.fit_before[k] for k in ('bbox_px','width_fraction','height_fraction','cropped_node_count')}
                    if hasattr(self,'fit_before') else None)

    def overview(self):
        with self.v.controller.pause():
            self.v.center_camera()
            self.v.set_view('XY')
            self.sync_camera_controller()

    def set_frame(self, index):
        index = int(np.clip(index,0,len(self.time)-1))
        if index==self.frame and hasattr(self,'colors'): return False
        self.frame = index
        self.colors,self.intensity,self.normalized_intensity,self.brightness = type_activity_colors(
            self.objects,self.activity[self.frame],self.color_encoding)
        self.v.set_colors({o['name']:tuple(c) for o,c in zip(self.objects,self.colors)})
        self.v.canvas.request_draw()
        return True

    def filter_types(self, value, focus=True):
        valid = ['all','T4','T5'] + [o['type'] for o in self.objects]
        if value not in valid:
            raise ValueError('Unknown type filter: ' + str(value))
        self.type_filter = value
        shown, hidden = [], []
        for o in self.objects:
            (shown if value in ('all',o['type'],o['type'][:2]) else hidden).append(o['name'])
        if hidden: self.v.hide_objects(hidden)
        self.v.unhide_objects(shown)
        if focus: self.detail_view()
        self.v.canvas.request_draw()
