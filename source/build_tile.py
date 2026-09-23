"""HEX-200 revision A. Units: mm. CadQuery 2.7.0 / OpenCascade.

Educational engineering concept, not a released pedestrian-floor product.
Commercial piezos are mechanical envelopes; threads and PCB packages are
simplified. See the accompanying design report for validation boundaries.
Run from anywhere: python build_tile.py
"""
from pathlib import Path
import math, json, csv, gzip, struct
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'CAD'; MESH = ROOT / 'meshes'
CAD.mkdir(exist_ok=True); MESH.mkdir(exist_ok=True)
P = dict(width_across_flats=200., corner_width=200/math.cos(math.pi/6),
         height=50., base_t=5., wall_t=3., cover_af=192., cover_t=6.,
         cover_bottom=42., tread_t=2., travel=2., bumper_contact=1.5,
         piezo_l=63.5, piezo_w=31.8, piezo_t=.51, clamp_l=12.7,
         piezo_root_r=22., piezo_z=28., tip_limit=.60,
         spring_wire=2.5, spring_mean_d=18., spring_active_turns=5,
         spring_total_turns=7, spring_free_l=34., spring_installed_l=33.,
         guide_r=78., stop_r=83., guide_d=6., guide_bore=6.10,
         steel_density_g_mm3=.008, spring_G=79000.)
PARTS=[]
COL=dict(pan='#485a6a', plate='#a5b7c7', tread='#177b79', seal='#263743',
         spring='#e6b960', steel='#c8d3df', polymer='#41576a', piezo='#8272cb',
         mass='#ce9560', pcb='#258979', black='#273642', gold='#efc671',
         wire='#e87d6b', insulator='#e8c76b', clear='#bddedb')

def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z)).val()
def cyl(x,y,z,r,h):
    return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def cone(x,y,z,r1,r2,h):
    return cq.Solid.makeCone(r1,r2,h,cq.Vector(x,y,z))
def hexagon(af,z,h):
    r=af/math.sqrt(3)
    pts=[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)]
    return cq.Workplane('XY').polyline(pts).close().extrude(h).translate((0,0,z)).val()
def ring(x,y,z,ro,ri,h):
    return cyl(x,y,z,ro,h).cut(cyl(x,y,z-.01,ri,h+.02))
def rotate(s,a): return s.rotate((0,0,0),(0,0,1),a)
def pos(r,a): return (r*math.cos(math.radians(a)), r*math.sin(math.radians(a)))
def holes(shape,coords,r,z,h):
    for x,y in coords: shape=shape.cut(cyl(x,y,z,r,h))
    return shape
def entry(code,name,s,color,group,material,notes='',motion='fixed',explode=0,angle=0,export=False):
    assert s.isValid(), f'Invalid solid: {code}'
    b=s.BoundingBox()
    PARTS.append(dict(code=code,name=name,shape=s,color=COL.get(color,color),group=group,
      material=material,notes=notes,motion=motion,explode=explode,angle=angle,
      bbox=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],volume_mm3=s.Volume()))
    if export:
        cq.exporters.export(s,str(CAD/f'{code}.step'))
        cq.exporters.export(s,str(MESH/f'{code}.stl'),tolerance=.06,angularTolerance=.12)
    return s

def screw_up(x,y,z,d,length,head_d,head_h):
    # Flat-bottom socket head; nominal major-diameter thread envelope.
    s=cyl(x,y,z,d/2,length).fuse(cyl(x,y,z-head_h,head_d/2,head_h))
    recess=cq.Workplane('XY').polygon(6,head_d*.50).extrude(head_h*.60).translate((x,y,z-head_h-.001)).val()
    return s.cut(recess)
def screw_down(x,y,top,d,length,head_d,head_h):
    s=cyl(x,y,top-length,d/2,length-head_h).fuse(cone(x,y,top-head_h,d/2,head_d/2,head_h))
    recess=cq.Workplane('XY').polygon(6,d*.75).extrude(.9).translate((x,y,top-.8)).val()
    return s.cut(recess)

# A01: one-piece pan with integral structural stop pillars. Datum A: z=0.
pan=hexagon(200,0,50).cut(hexagon(194,5,46))
groove=hexagon(196,46,2).cut(hexagon(194,45.9,2.2))
pan=pan.cut(groove)
for a in range(30,360,60):
    x,y=pos(83,a);pan=pan.fuse(cyl(x,y,5,6,35))
for a in (60,180,300):
    x,y=pos(78,a)
    pan=pan.cut(cyl(x,y,-.01,2.2,5.02)).cut(cone(x,y,-.01,4.4,2.2,2.21))
for a in (90,210,330):
    x,y=pos(91,a);pan=pan.cut(cyl(x,y,-.01,1.5,5.02))
pan=pan.cut(cyl(0,-60,-.01,4,5.02))
pcb_xy=[(-18,-18),(-18,18),(18,-18),(18,18)]
pan=holes(pan,pcb_xy,1.05,1.5,3.51)
entry('A01','Housing and six structural stops',pan,'pan','Housing','6061-T6 aluminium',
      'CNC concept; six integral Ø12 stops finish at z40. Three Ø3 weeps; underside cable port.',export=True)
seal=hexagon(196,46.5,1).cut(hexagon(192,46.49,1.02))
entry('A02','Perimeter sliding wiper',seal,'seal','Seals','EPDM',
      'Nominal lip envelope in 2 mm groove; friction and water ingress unqualified.',explode=12,export=True)
for i,a in enumerate(range(30,360,60),1):
    x,y=pos(83,a)
    entry(f'A03_{i}','Stop bumper ring',ring(x,y,39.5,8,6,1),'seal','Stops','EPDM',
          'Contact at 1.50 mm stroke; compress 0.50 mm before metal stop.',explode=5)
entry('A04','Underside cable grommet',ring(0,-60,0,4,2,5),'seal','Seals','EPDM',
      'Cable exits underside into a receiving recess; cable itself excluded from rigid envelope.')

# A10: structural moving cover, all mounting bores modelled.
mounts=[]
for a in (0,120,240):
    for yy in (-19,19):
        x,y=pos(28.35,a);ang=math.radians(a);mounts.append((x-yy*math.sin(ang),y+yy*math.cos(ang)))
    for yy in (-25.5,25.5):
        x,y=pos(80.5,a);ang=math.radians(a);mounts.append((x-yy*math.sin(ang),y+yy*math.cos(ang)))
for a in (60,180,300):
    x,y=pos(78,a)
    for dx in (-9,9): mounts.append((x+dx,y))
plate=hexagon(192,42,6)
for x,y in mounts:
    plate=plate.cut(cyl(x,y,41.99,1.7,6.02)).cut(cone(x,y,46.3,1.7,3.4,1.71))
entry('A10','Moving load-spreading plate',plate,'plate','Cover','6061-T6 aluminium',
      '18 countersunk M3 fixing holes; 1.00 mm side clearance to pan.',motion='cover',explode=85,export=True)
tread=hexagon(192,48,2)
# Recessed tread channels are real 0.35 mm cuts, not a texture.
for yy in range(-80,81,16):
    for aa in (0,60):
        cutter=rotate(box(-130,yy-.55,49.65,260,1.1,.5),aa)
        tread=tread.cut(cutter)
entry('A11','Replaceable textured tread',tread,'tread','Cover','EPDM rubber',
      '2 mm nominal including adhesive allowance; grooves 0.35 mm deep. Slip resistance untested.',
      motion='cover',explode=105,export=True)
for i,(x,y) in enumerate(mounts,1):
    entry(f'F01_{i}','Cover mounting screw M3 x 10',screw_down(x,y,48,3,10,6.8,1.7),
          'steel','Fasteners','Stainless steel','Thread envelope; no helical threads.',motion='cover',explode=90)

def spring_shape(installed=33):
    d=2.5; h=installed-d; pts=[]
    # Two closed end coils and five active coils. The transition is spline-smoothed.
    for i in range(337):
        turns=7*i/336
        zz=2.5*turns if turns<=1 else (2.5+(turns-1)*(h-5)/5 if turns<=6 else h-2.5+(turns-6)*2.5)
        phi=2*math.pi*turns
        pts.append(cq.Vector(9*math.cos(phi),9*math.sin(phi),5+d/2+zz))
    path=cq.Wire.assembleEdges([cq.Edge.makeSpline(pts)])
    tangent=pts[1]-pts[0]
    plane=cq.Plane(origin=pts[0],normal=tangent)
    return cq.Workplane(plane).circle(d/2).sweep(path,isFrenet=True).val()

spring=spring_shape()
for i,a in enumerate((60,180,300),1):
    x,y=pos(78,a)
    rod=cyl(x,y,5,3,31).fuse(cyl(x,y,36,5,3)).cut(cyl(x,y,4.99,1.65,8.01))
    entry(f'G01_{i}','Captive guide and return retainer',rod,'steel','Guides','Stainless steel',
      'Ø6 shaft, Ø10 head; lower M4 female thread. Head underside at z36 sets rest height.',explode=10,export=i==1)
    cup=cyl(x,y,25,7,13).fuse(cyl(x,y,38,12,4))
    cup=cup.cut(cyl(x,y,24.99,4,11.01)).cut(cyl(x,y,36,5.3,6.01))
    cup=holes(cup,[(x-9,y),(x+9,y)],1.25,37.99,4.02)
    entry(f'G02_{i}','Sliding guide cup and spring seat',cup,'plate','Guides','6061-T6 aluminium',
      'Ø8 liner seat; Ø10.60 head pocket. Four-mm flange seats spring at z38.',
      motion='cover',explode=58,export=i==1)
    entry(f'G03_{i}','Replaceable guide liner',ring(x,y,25,4,3.05,11),'polymer','Guides','POM',
      'Ø8 outside / Ø6.10 inside / 11 long. Nominal mating fit; retention to be qualified.',
      motion='cover',explode=58,export=i==1)
    entry(f'S01_{i}','Return spring',spring.translate((x,y,0)),'spring','Springs','Spring steel',
      'Custom target: wire 2.5, mean Ø18, 5 active / 7 total turns, free 34, installed 33 mm.',motion='spring',explode=15,export=i==1)
    fast=cone(x,y,0,4.4,2,2.2).fuse(cyl(x,y,2.2,2,8.8))
    entry(f'F02_{i}','Guide anchor countersunk M4 x 11 envelope',fast,'steel','Fasteners','Stainless steel',
      'Custom nominal length envelope; engagement is 6 mm into guide. Threads simplified.',explode=-8)

# Three identical cantilever cartridges. Local x is radially outwards.
for i,a in enumerate((0,120,240),1):
    local=[]
    def E(code,name,s,color,group,mat,notes='',explode=45,motion='cover',exp=False):
        return entry(f'{code}_{i}',name,rotate(s,a),color,group,mat,notes,motion,explode,a,exp and i==1)
    root_xy=[(28.35,-19),(28.35,19)]
    tower=box(22,-22,28.355,12.7,44,13.645)
    tower=holes(tower,root_xy,1.25,28.35,6.0)
    tower=holes(tower,root_xy,1.25,37.9,4.2)
    E('H01','Cantilever root tower',tower,'polymer','Cantilevers','POM',
      'Top and bottom blind threaded bores stay separate. Clamp screws sit outside piezo width.',exp=True)
    shoe=holes(box(22,-22,24.645,12.7,44,3),root_xy,1.7,24.64,3.02)
    E('H02','Removable lower clamp',shoe,'polymer','Cantilevers','POM',exp=True)
    for j,z in enumerate((27.645,28.255),1):
        E(f'H03{j}','Root electrical isolation shim',box(22,-15.9,z,12.7,31.8,.1),
          'insulator','Cantilevers','Polyimide', '0.10 mm nominal; supplier must approve clamp construction.')
    E('P01','PZT 5A bimorph',box(22,-15.9,27.745,63.5,31.8,.51),'piezo','Piezos','PZT / brass laminate',
      'T220-A4BR-2513XB mechanical envelope. Free length 50.8 mm. Nominal flat, before gravity sag.',motion='beam',exp=True)
    # Tip fasteners straddle the ceramic: no holes through the piezo.
    tip_xy=[(80.5,-18),(80.5,18)]
    mass=holes(box(75.5,-20,24.645,10,40,3),tip_xy,.8,24.63,3.03)
    E('H04','Tip proof mass',mass,'mass','Tip masses','Stainless steel',
      '10 x 40 x 3 blank = 9.60 g before two tapped holes; actual CAD volume in BOM.',motion='tip',exp=True)
    cap=holes(box(75.5,-20,28.355,10,40,1.5),tip_xy,1.1,28.34,1.54)
    for x,y in tip_xy: cap=cap.cut(cone(x,y,28.855,1.1,2.1,1.01))
    E('H05','Insulated tip clamp cap',cap,'polymer','Tip masses','POM',motion='tip',exp=True)
    for j,z in enumerate((27.645,28.255),1):
        E(f'H06{j}','Tip electrical isolation shim',box(75.5,-15.9,z,10,31.8,.1),
          'insulator','Tip masses','Polyimide',motion='tip')
    for j,(x,y) in enumerate(root_xy,1):
        E(f'F03{j}','Root clamp M3 x 8',screw_up(x,y,24.645,3,8,5.5,2.5),'steel','Fasteners','Stainless steel')
    for j,(x,y) in enumerate(tip_xy,1):
        E(f'F04{j}','Tip clamp M2 x 5',screw_down(x,y,29.855,2,5,4.2,1),
          'steel','Fasteners','Stainless steel',motion='tip')
    # Moving cage follows the cover. It limits RELATIVE beam travel, not cover travel.
    cage=box(73.5,-27,39,14,54,3)
    for yy in (-27,24): cage=cage.fuse(box(73.5,yy,23.745,14,3,15.255))
    cage=cage.fuse(box(73.5,-24,30.755,14,48,.8))
    cage=holes(cage,[(80.5,-25.5),(80.5,25.5)],1.25,37.9,4.2)
    cage=holes(cage,[(80.5,-25.5),(80.5,25.5)],.8,23.73,3.8)
    E('H07','Relative travel limiter cage',cage,'polymer','Cages','POM',
      'Upper catch, two side walls, mounting flange. These move with the cover.',exp=True)
    closure=holes(box(73.5,-27,22.545,14,54,1.2),[(80.5,-25.5),(80.5,25.5)],1.1,22.53,1.23)
    for yy in (-25.5,25.5): closure=closure.cut(cone(80.5,yy,22.535,2.1,1.1,1.01))
    E('H08','Removable cage bottom',closure,'steel','Cages','Stainless steel',exp=True)
    E('H09','Lower tip stop pad',box(75.5,-16,23.745,10,32,.3),'seal','Cages','EPDM',
      '0.60 mm nominal gap from metal proof-mass underside.')
    E('H10','Upper tip stop pad',box(75.5,-16,30.455,10,32,.3),'seal','Cages','EPDM',
      '0.60 mm nominal gap above cap; pitch reduces usable edge clearance.')
    for j,yy in enumerate((-25.5,25.5),1):
        fast=cone(80.5,yy,22.545,2.1,1,1).fuse(cyl(80.5,yy,23.545,1,3.5))
        E(f'F05{j}','Cage closure M2 countersunk',fast,'steel','Fasteners','Stainless steel')

# Protected electronics bay: a mechanical enclosure and a reference PCB layout.
board=holes(box(-22,-22,8.5,44,44,1.6),pcb_xy,1.35,8.49,1.62)
entry('E01','Reference PCB',board,'pcb','Electronics','FR4',
      '44 x 44 x 1.6. Placement concept only: not routed, no Gerbers or component procurement claim.',explode=13,export=True)
for i,(x,y) in enumerate(pcb_xy,1):
    entry(f'E02_{i}','PCB standoff',ring(x,y,5,3,1.05,3.5),'polymer','Electronics','POM',explode=7)
    entry(f'F06_{i}','PCB screw M2 x 6',screw_down(x,y,10.1,2,6,3.8,1),'steel','Fasteners','Stainless steel',explode=14)
ecase=box(-26,-26,5,52,52,14).cut(box(-24.5,-24.5,4.99,49,49,12.51))
for x,y in [(-12,-10),(0,-10),(12,-10),(0,16)]:
    ecase=ecase.cut(cyl(x,y,17.49,1.2,1.52))
entry('E03','Electronics splash hood',ecase,'clear','Electronics enclosure','Polycarbonate',
      'Open bottom bonded to pan; four potted wire holes. Mechanical envelope, ingress performance untested.',explode=23,export=True)
for j,xx in enumerate((-12,0,12),1):
    entry(f'E04_{j}','Two-pin piezo connector envelope',box(xx-3,-14,10.1,6,5,4),
          'black','Electronics','Connector envelope', 'Package and board layout remain provisional.',explode=13)
    for k in range(4):
        entry(f'E05_{j}_{k}','Rectifier diode envelope',box(xx-1.5,-6+k*3.3,10.1,3,1.8,1.2),
          'black','Electronics','Semiconductor envelope',explode=13)
entry('E06','LTC3588-1 package envelope',box(-1.5,8,10.1,3,3,1),'black','Electronics','DFN envelope',explode=13)
entry('E07','10 uH inductor envelope',box(5,8,10.1,4,4,3),'black','Electronics','Inductor envelope',explode=13)
entry('E08','47 uF input capacitor envelope',cyl(-12,11,10.1,3.2,7),'steel','Electronics','Capacitor envelope',explode=13)
entry('E09','47 uF output capacitor envelope',cyl(14,12,10.1,2.5,5),'steel','Electronics','Capacitor envelope',explode=13)
entry('E10','Output connector envelope',box(-3,14,10.1,6,5,4),'black','Electronics','Connector envelope',explode=13)
for j,(xx,yy) in enumerate([(3,4),(7,3),(-6,8),(-6,12)],1):
    entry(f'E11_{j}','Passives envelope',box(xx,yy,10.1,2,1.25,1),'gold','Electronics','Passive envelope',explode=13)

# Curved silicone-insulated lead envelopes. Flex loops are conceptual routing.
def lead(points,r=.42):
    pts=[cq.Vector(*p) for p in points]
    path=cq.Wire.assembleEdges([cq.Edge.makeSpline(pts)])
    return cq.Workplane(cq.Plane(origin=pts[0],normal=pts[1]-pts[0])).circle(r).sweep(path,isFrenet=True).val()
for i,a in enumerate((0,120,240),1):
    for j,dy in enumerate((-.55,.55)):
        # terminate at exposed free electrode, beside root clamp; lift clear of root tower.
        th=math.radians(a)
        def polar_xy(x,y,z):return (x*math.cos(th)-y*math.sin(th),x*math.sin(th)+y*math.cos(th),z)
        dst=(-12+(i-1)*12,-10+dy,14.1)
        if j==0:
            route=[(36,0,28.70),(38,-25,34),(18,-25,36),(17,-3,34)]
        else:
            route=[(36,3,27.2),(38,20,27.2),(38,25,34),(18,25,36),(17,3,34)]
        pts=[polar_xy(*v) for v in route]+[(dst[0],dst[1],25),(dst[0],dst[1],19),dst]
        entry(f'W01_{i}_{j}','Flexible piezo lead',lead(pts), 'wire' if j==0 else 'gold','Wiring','Insulated fine wire',
              'Routing envelope; two electrode terminations and service-loop attachment need bench finalisation.',motion='wire',explode=30,angle=a)
entry('W02','Output cable routing',lead([(0,16,14),(0,16,22),(0,32,22),(34,32,18),(34,0,9),(32,-40,7),(0,-60,5)],1),
      'black','Wiring','Insulated cable','Schematic route; cable termination and strain relief to be finalised.',explode=0)

def export_all():
    assy=cq.Assembly(name='HEX_200_REV_A')
    for p in PARTS:
        col=p['color'].lstrip('#');rgb=[int(col[i:i+2],16)/255 for i in (0,2,4)]
        assy.add(p['shape'],name=p['code']+'_'+p['name'].replace(' ','_').replace('/','_'),color=cq.Color(*rgb))
    assy.export(str(CAD/'HEX_200_Assembly.step'))
    # glTF is a visual interchange; the STEP uses millimetres.
    assy.export(str(ROOT/'HEX_200_Assembly.glb'),tolerance=.1,angularTolerance=.18)
    # OCCT emits source coordinates in mm; glTF world units are metres.
    glbpath=ROOT/'HEX_200_Assembly.glb';raw=glbpath.read_bytes()
    n,kind=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+n])
    for scene in doc['scenes']:
        for node in scene['nodes']:doc['nodes'][node]['scale']=[.001,.001,.001]
    chunk=json.dumps(doc,separators=(',',':')).encode();chunk+=b' '*((-len(chunk))%4)
    tail=raw[20+n:]
    glbpath.write_bytes(struct.pack('<III',0x46546c67,2,20+len(chunk)+len(tail))+struct.pack('<II',len(chunk),kind)+chunk+tail)
    manifest=[];meshes=[]
    for p in PARTS:
        q={k:v for k,v in p.items() if k!='shape'};manifest.append(q)
        verts,faces=p['shape'].tessellate(.10,.16)
        meshes.append(dict(**q,vertices=[round(v,4) for vv in verts for v in vv.toTuple()],indices=[v for f in faces for v in f]))
    (ROOT/'parameters.json').write_text(json.dumps(P,indent=2))
    (ROOT/'parts_manifest.json').write_text(json.dumps(manifest,indent=2))
    (ROOT/'meshes'/'assembly_meshes.json').write_text(json.dumps(meshes,separators=(',',':')))
    with (ROOT/'BOM.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['ID','Component','Material','Motion','Volume mm^3','Notes'])
        for p in manifest:w.writerow([p['code'],p['name'],p['material'],p['motion'],round(p['volume_mm3'],3),p['notes']])
    print(json.dumps({'parts':len(PARTS),'valid':all(p['shape'].isValid() for p in PARTS),'step':str(CAD/'HEX_200_Assembly.step'),
      'mesh_mb':round((ROOT/'meshes'/'assembly_meshes.json').stat().st_size/1e6,2)},indent=2))

if __name__=='__main__':export_all()
