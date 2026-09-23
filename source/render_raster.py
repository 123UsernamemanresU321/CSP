"""Depth-buffered CAD render in NumPy. No external display or image generator."""
from pathlib import Path
import json,math,time,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
DATA=json.loads((ROOT/'meshes/preview_meshes.json').read_text())
def rgb(s):return np.array([int(s[i:i+2],16) for i in (1,3,5)],dtype=float)
def render(name,mode):
    aa,ee=(-54,29) if mode!='cartridge' else (-59,23)
    a,e=map(math.radians,(aa,ee));eye=np.array([math.cos(a)*math.cos(e),math.sin(a)*math.cos(e),math.sin(e)])
    right=np.array([-math.sin(a),math.cos(a),0]);up=np.cross(eye,right);basis=np.array([right,up,eye]).T
    faces=[];colors=[]
    for p in DATA:
        code=p['code'];group=p['group']
        if group=='Wiring':continue
        if mode=='inside' and (group=='Cover' or code.startswith('F01') or code=='E03'):continue
        if mode=='cartridge' and not(code.endswith('_1') and code.startswith(('P01','H0','H1','F03','F04','F05'))):continue
        v=np.array(p['vertices']).reshape(-1,3);t=np.array(p['indices']).reshape(-1,3)
        if mode=='exploded':v[:,2]+=.92*p['explode']
        f=v[t]
        if code in ('A01','A02') and mode in ('inside','exploded'):
            ctr=f.mean(axis=1);f=f[(ctr[:,1]>0)|(ctr[:,2]<5.1)|(np.hypot(ctr[:,0],ctr[:,1])<92)]
        normal=np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-10)
        normal[normal@eye<0]*=-1
        light=np.array([-.5,-.4,1]);light/=np.linalg.norm(light)
        light2=np.array([.7,.6,.4]);light2/=np.linalg.norm(light2)
        shade=.58+.42*np.maximum(normal@light,0)+.14*np.maximum(normal@light2,0)
        col=np.clip(rgb(p['color'])[None,:]*shade[:,None],0,255)
        faces.append(f@basis);colors.append(col)
    f=np.concatenate(faces);cols=np.concatenate(colors)
    vw,vh=2000,1400
    mi=f[:,:,:2].min(axis=(0,1));ma=f[:,:,:2].max(axis=(0,1));scale=min((vw-180)/(ma[0]-mi[0]),(vh-170)/(ma[1]-mi[1]))
    centre=(mi+ma)/2;f[:,:,0]=(f[:,:,0]-centre[0])*scale+vw/2;f[:,:,1]=vh/2-(f[:,:,1]-centre[1])*scale
    out=np.full((vh,vw,3),[241,245,247],dtype=np.uint8);depth=np.full((vh,vw),-np.inf,dtype=np.float32)
    # Front-to-back order improves early depth rejection, but pixel depth is authoritative.
    order=np.argsort(f[:,:,2].mean(axis=1))[::-1]
    for k in order:
        t=f[k];lo=np.maximum(np.floor(t[:,:2].min(0)).astype(int),0);hi=np.minimum(np.ceil(t[:,:2].max(0)).astype(int),[vw-1,vh-1])
        x0,y0=lo;x1,y1=hi
        if x0>x1 or y0>y1:continue
        dep=depth[y0:y1+1,x0:x1+1]
        if dep.min()>t[:,2].max():continue
        xa,ya,za=t[0];xb,yb,zb=t[1];xc,yc,zc=t[2]
        den=(yb-yc)*(xa-xc)+(xc-xb)*(ya-yc)
        if abs(den)<1e-8:continue
        xx=np.arange(x0,x1+1)[None,:]+.5;yy=np.arange(y0,y1+1)[:,None]+.5
        u=((yb-yc)*(xx-xc)+(xc-xb)*(yy-yc))/den
        v=((yc-ya)*(xx-xc)+(xa-xc)*(yy-yc))/den;w=1-u-v
        zz=u*za+v*zb+w*zc;mask=(u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8)&(zz>dep)
        if not mask.any():continue
        dep[mask]=zz[mask];out[y0:y1+1,x0:x1+1][mask]=cols[k].astype(np.uint8)
    im=Image.fromarray(out).resize((1800,1260),Image.Resampling.LANCZOS);im.save(OUT/f'{name}.png')
    print(name,flush=True)
for n,m in [('Tile_Inside','inside'),('Tile_Exploded','exploded'),('Tile_Assembled','assembled'),('Cantilever_Cartridge','cartridge')]:render(n,m)
