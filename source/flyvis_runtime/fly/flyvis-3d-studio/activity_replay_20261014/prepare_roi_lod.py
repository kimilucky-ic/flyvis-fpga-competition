"""Offline data adapter: official ROI meshes -> existing VTK quadric LOD.

Uses two already installed isolated environments; installs nothing. The derived
ROI is an approximate spatial reference, never a replacement segmentation.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'roi_lod_20261015'
def sha(path):
    with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def worker(source,target,budget):
    import numpy as np
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
    vtk.vtkSMPTools.Initialize(1)
    with np.load(source) as data: vertices,faces=data['vertices_um'],data['faces']
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(vertices.astype(np.float64),deep=True))
    cells=vtk.vtkCellArray()
    cells.SetCells(len(faces),numpy_to_vtkIdTypeArray(np.column_stack([np.full(len(faces),3),faces]).astype(np.int64).ravel(),deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    reduction=max(0.,1-budget/len(faces))
    decimator=vtk.vtkQuadricDecimation()
    decimator.SetInputData(poly);decimator.SetTargetReduction(reduction)
    decimator.VolumePreservationOn();decimator.Update()
    result=decimator.GetOutput()
    vertices_out=vtk_to_numpy(result.GetPoints().GetData()).copy()
    faces_out=vtk_to_numpy(result.GetPolys().GetConnectivityArray()).reshape(-1,3).copy()
    if not len(faces_out) or len(faces_out)>len(faces)/50:
        raise RuntimeError('ROI reduction did not meet the light geometry budget')
    np.savez_compressed(target,vertices_um=vertices_out,faces=faces_out)
    summary=dict(source_vertices=len(vertices),source_faces=len(faces),derived_vertices=len(vertices_out),
                 derived_faces=len(faces_out),source_bounds_um=[vertices.min(0).tolist(),vertices.max(0).tolist()],
                 derived_bounds_um=[vertices_out.min(0).tolist(),vertices_out.max(0).tolist()],
                 algorithm='vtkQuadricDecimation',vtk_version=vtk.vtkVersion.GetVTKVersion(),
                 target_face_budget=budget,target_reduction=reduction,volume_preservation=True)
    target.with_suffix('.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--vtk-worker',nargs=2,type=Path);ap.add_argument('--budget',type=int,default=1200)
    args=ap.parse_args()
    if args.vtk_worker:
        worker(*args.vtk_worker,args.budget);return
    import numpy as np
    import psutil
    from cloudvolume import Mesh
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    os.environ['OMP_NUM_THREADS']='1';os.environ['VTK_SMP_MAX_THREADS']='1'
    OUT.mkdir(parents=True,exist_ok=True)
    model=json.loads((ROOT/'model.json').read_text(encoding='utf-8'))
    vtk_python=ROOT.parent/'evaluation_20261013/.venv/Scripts/python.exe'
    items=[]
    for roi in model['rois']:
        if sha(roi['path'])!=roi['sha256']: raise ValueError('Raw ROI SHA mismatch')
        mesh=Mesh.from_precomputed(Path(roi['path']).read_bytes(),segid=roi['segment_id'])
        source=OUT/'conversion_input.npz'
        np.savez(source,vertices_um=np.asarray(mesh.vertices,dtype=np.float64)/1000,faces=np.asarray(mesh.faces,dtype=np.int64))
        target=OUT/f"roi_{roi['segment_id']}_lod.npz"
        subprocess.run([str(vtk_python),'-B',str(Path(__file__)), '--vtk-worker',str(source),str(target),
                        '--budget',str(args.budget)],check=True,timeout=90)
        summary=json.loads(target.with_suffix('.json').read_text(encoding='utf-8'))
        items.append(dict(name=roi['name'],segment_id=roi['segment_id'],source_path=roi['path'],source_sha256=roi['sha256'],
                          derived_file=target.name,derived_sha256=sha(target),**summary))
    manifest=dict(schema='line10.roi_lod.v1',source='Janelia Optic Lobe v1.1 official ROI ngmesh',
                  source_coordinate_units='nm',derived_coordinate_units='um',coordinate_transform='uniform nm/1000 only; original coordinate frame retained',
                  purpose='Simplified spatial reference only; not for quantitative anatomical measurements',
                  created_utc=datetime.now(timezone.utc).isoformat(),rois=items)
    temp=OUT/'manifest.tmp';temp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(OUT/'manifest.json')
    print(json.dumps(dict(source_faces=sum(i['source_faces'] for i in items),derived_faces=sum(i['derived_faces'] for i in items),
                          manifest_sha256=sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
