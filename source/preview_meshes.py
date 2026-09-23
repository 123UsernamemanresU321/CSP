"""Create lighter visual-only meshes. The STEP remains authoritative geometry."""
from pathlib import Path
import json, numpy as np, vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'meshes/assembly_meshes.json').read_text())
for a in data:
    n=len(a['indices'])//3
    if n<15000:continue
    pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.array(a['vertices']).reshape(-1,3),deep=True))
    tris=np.array(a['indices'],dtype=np.int64).reshape(-1,3)
    cells=vtk.vtkCellArray();cells.SetCells(n,numpy_to_vtkIdTypeArray(np.c_[np.full(n,3),tris].reshape(-1),deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
    clean=vtk.vtkCleanPolyData();clean.SetInputData(poly);clean.Update()
    dec=vtk.vtkQuadricDecimation();dec.SetInputConnection(clean.GetOutputPort())
    target=12000 if a['group']=='Springs' else 7000
    dec.SetTargetReduction(1-target/n);dec.VolumePreservationOn();dec.Update();p=dec.GetOutput()
    a['vertices']=np.round(vtk_to_numpy(p.GetPoints().GetData()),4).reshape(-1).tolist()
    a['indices']=vtk_to_numpy(p.GetPolys().GetData()).reshape(-1,4)[:,1:].reshape(-1).tolist()
(ROOT/'meshes/preview_meshes.json').write_text(json.dumps(data,separators=(',',':')))
print('Preview triangles',sum(len(x['indices'])//3 for x in data))
