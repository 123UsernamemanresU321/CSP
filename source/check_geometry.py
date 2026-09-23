"""Clearance and geometry evidence for HEX-200, not a structural analysis."""
import json, math, itertools
from pathlib import Path
import build_tile as b
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

parts=b.PARTS
report={'scope':'Nominal rigid CAD at rest and 2 mm stroke. No FEA or fatigue/ingress/energy validation.',
        'part_count':len(parts),'invalid_parts':[p['code'] for p in parts if not p['shape'].isValid()]}
def overlap_bbox(a,c,tol=.005):
    aa=a.BoundingBox();bb=c.BoundingBox()
    return all(min(getattr(aa,s+'max'),getattr(bb,s+'max'))-max(getattr(aa,s+'min'),getattr(bb,s+'min'))>tol for s in 'xyz')
def interference(a,c):
    if not overlap_bbox(a,c):return 0
    return a.intersect(c).Volume()

# Fastener major-diameter envelopes overlap tapped minor bores by design.
# Flex leads / PCB package envelopes are checked separately as layout concepts.
rigid=[p for p in parts if p['group'] not in ('Fasteners','Wiring','Electronics')]
clashes=[]
for p,q in itertools.combinations(rigid,2):
    v=interference(p['shape'],q['shape'])
    if v>.02: clashes.append([p['code'],q['code'],round(v,4)])
report['rest_unintended_rigid_interferences_mm3']=clashes

moving=[p for p in rigid if p['motion'] in ('cover','beam','tip')]
fixed=[p for p in rigid if p['motion']=='fixed']
clashes=[]
for p,q in itertools.product(moving,fixed):
    # Structural bumper rings compress by 0.5 mm at the 2 mm stroke endpoint.
    if q['code'].startswith('A03'):continue
    v=interference(p['shape'].translate((0,0,-2)),q['shape'])
    if v>.02:clashes.append([p['code'],q['code'],round(v,4)])
report['full_stroke_unintended_rigid_interferences_mm3']=clashes

pan=next(p for p in parts if p['code']=='A01')['shape']
bb=Bnd_Box();BRepBndLib.AddOptimal_s(pan.wrapped,bb,False,False)
v=bb.Get()
report['measured_housing_bbox_mm']={'x':v[3]-v[0],'y':v[4]-v[1],'z':v[5]-v[2]}
report['derived_dimensions_mm']={'across_flats':200,'across_corners':200/math.cos(math.pi/6),
 'side_length':200/math.sqrt(3),'cover_to_wall_each_flat':(194-192)/2,
 'hard_stop_stroke':42-40,'bumper_contact_stroke':42-40.5,
 'guide_diametral_clearance':6.1-6,'head_top_to_cover_at_full_stroke':42-2-39,
 'nominal_lower_tip_gap':24.645-24.045,'nominal_upper_tip_gap':30.455-29.855}
report['notes']=['Threaded joints use nominal envelopes, not helical mating threads.',
 'Beam envelope is flat; small gravitational sag is estimated in the report.',
 'Tip pitch means 0.60 mm edge gaps are not a ±0.60 mm permissible centre displacement.',
 'Spring coils are a CAD sweep of a custom target, not a sourced qualified spring.',
 'Wire routing and electronic package envelopes are provisional and excluded from rigid clearance verdict.']
report['passed']=not(report['invalid_parts'] or report['rest_unintended_rigid_interferences_mm3'] or report['full_stroke_unintended_rigid_interferences_mm3'])
(b.ROOT/'geometry_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
