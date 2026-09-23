"""Illustrated engineering record. ReportLab; landscape A4."""
from pathlib import Path
import math,json,collections,csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.colors import HexColor as _HexColor,Color,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
ROOT=Path(__file__).resolve().parents[1]
def HexColor(value):return _HexColor('#'+value.lstrip('#'))
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=landscape(A4);M=36;INK='#193548';TEAL='#137a77';LIGHT='#edf3f6';GREY='#536b7b'
C=canvas.Canvas(str(ROOT/'HEX_200_Technical_Design.pdf'),pagesize=(W,H))
C.setTitle('HEX-200 | Detailed 3D Tile Design | Revision A')
C.setAuthor('HBIS CSP - design prepared with ChatGPT')
N=9
styles={}
for size in (8,9,10,11,12):styles[size]=ParagraphStyle(str(size),fontName='DejaVu',fontSize=size,leading=size*1.45,textColor=HexColor(INK),spaceAfter=6)
styles['small']=styles[9]
def text(x,y,s,size=10,bold=False,color=INK):
 C.setFillColor(HexColor(color));C.setFont('DejaVu-Bold' if bold else 'DejaVu',size);C.drawString(x,y,s)
def para(x,y,s,width,size=10):
 p=Paragraph(s,styles[size]);w,h=p.wrap(width,1000);p.drawOn(C,x,y-h);return y-h-9
def header(num,title,kicker):
 C.setFillColor(white);C.rect(0,0,W,H,fill=1,stroke=0)
 text(M,H-30,'HEX-200   /   HBIS COLLABORATIVE SCIENCES PROJECT',9,True,TEAL)
 text(M,H-65,title,23,True)
 text(M,H-85,kicker,9,False,GREY)
 C.setStrokeColor(HexColor('#cddbe2'));C.line(M,37,W-M,37)
 text(M,22,'REV A  •  22 SEPTEMBER 2026  •  ALL CAD DIMENSIONS IN mm',8,False,GREY)
 C.drawRightString(W-M,22,f'{num:02d} / {N:02d}  |  ENGINEERING CONCEPT')
def box(x,y,w,h,fill=LIGHT):C.setFillColor(HexColor(fill));C.rect(x,y,w,h,fill=1,stroke=0)
def table(x,y,rows,widths,size=9):
 cell=ParagraphStyle('cell',fontName='DejaVu',fontSize=size,leading=size*1.35,textColor=HexColor(INK))
 rr=[[Paragraph(str(a),cell) for a in row] for row in rows]
 t=Table(rr,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e2edf1')),('VALIGN',(0,0),(-1,-1),'TOP'),
 ('LINEBELOW',(0,0),(-1,0),.7,HexColor('#a4beca')),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#d7e2e7')),
 ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 tw,th=t.wrap(sum(widths),1000);t.drawOn(C,x,y-th);return y-th
def img(name,x,y,w,h):C.drawImage(str(ROOT/'figures'/f'{name}.png'),x,y,width=w,height=h,mask='auto',preserveAspectRatio=True,anchor='c')
def arrow(x1,y1,x2,y2,color=INK):
 C.setStrokeColor(HexColor(color));C.setFillColor(HexColor(color));C.setLineWidth(.7);C.line(x1,y1,x2,y2)
 a=math.atan2(y2-y1,x2-x1);p=C.beginPath();p.moveTo(x2,y2)
 p.lineTo(x2-5*math.cos(a-.45),y2-5*math.sin(a-.45));p.lineTo(x2-5*math.cos(a+.45),y2-5*math.sin(a+.45));p.close();C.drawPath(p,fill=1,stroke=0)
def dim(x1,y1,x2,y2,label,dx=0,dy=0):
 C.setLineWidth(.5);C.setStrokeColor(HexColor(GREY));C.line(x1,y1,x1+dx,y1+dy);C.line(x2,y2,x2+dx,y2+dy)
 arrow(x1+dx,y1+dy,x2+dx,y2+dy,GREY);arrow(x2+dx,y2+dy,x1+dx,y1+dy,GREY)
 text((x1+x2)/2+dx+4,(y1+y2)/2+dy+5,label,8,False,GREY)
def polygon(points,fill,stroke=INK):
 p=C.beginPath();p.moveTo(*points[0])
 for v in points[1:]:p.lineTo(*v)
 p.close();C.setFillColor(HexColor(fill));C.setStrokeColor(HexColor(stroke));C.setLineWidth(.65);C.drawPath(p,fill=1,stroke=1)
def hexpoints(af,cx,cy,s):return [(cx+af/math.sqrt(3)*math.cos(a*math.pi/3)*s,cy+af/math.sqrt(3)*math.sin(a*math.pi/3)*s) for a in range(6)]

# 1 - overview
header(1,'A complete tile, from tread to transducer','Regular hexagon • 200 mm across flats • 50 mm high • 2 mm cover stroke')
img('Tile_Inside',18,110,525,380)
y=H-120
for title,body in [
 ('Based on your reference','The cover carries three piezoelectric cantilevers with tip masses. During a footstep, acceleration of the cover makes each mass lag and bends its beam.'),
 ('Two separate mechanical roles','Springs return the cover. Six structural stops transfer the main foot load to the pan after the cover moves 2 mm. The ceramic beams are not foot-load supports.'),
 ('What is defined','142 CAD components: housing, cover, tread, guide assemblies, springs, beam cartridges, limiters, fasteners, seals and a reference electronics bay.'),
 ('What accuracy means here','The STEP geometry and clearances are dimensioned. Spring specification, clamp details, PCB layout and load/energy performance still require prototype qualification.')]:
 text(565,y,title,11,True);y=para(565,y-10,body,235,9)-9
box(36,60,770,45)
para(48,96,'<b>Use for the CSP and bench development.</b> This is a detailed engineering concept, not a certified floor tile or a fabrication release. The user reference is a schematic, so unspecified dimensions were designed here rather than inferred as measurements.',744,9)
C.showPage()

# 2 - actual plan dimensions
header(2,'Envelope and installation geometry','Plan and elevation at 1:2 when printed at 100% on A4 landscape; dimensions override display scaling.')
s=72/25.4/2;cx=225;cy=318
polygon(hexpoints(200,cx,cy,s),'e7eef2');polygon(hexpoints(194,cx,cy,s),'ffffff');polygon(hexpoints(192,cx,cy,s),'f7fafb')
for a in (0,120,240):
 r=math.radians(a)
 def tr(x,y):return (cx+s*(x*math.cos(r)-y*math.sin(r)),cy+s*(x*math.sin(r)+y*math.cos(r)))
 polygon([tr(22,-15.9),tr(85.5,-15.9),tr(85.5,15.9),tr(22,15.9)],'b8b0dc')
 polygon([tr(22,-22),tr(34.7,-22),tr(34.7,22),tr(22,22)],'849aa9')
 polygon([tr(75.5,-20),tr(85.5,-20),tr(85.5,20),tr(75.5,20)],'d6af88')
for a in (60,180,300):
 x,y=78*math.cos(math.radians(a)),78*math.sin(math.radians(a));C.setStrokeColor(HexColor('#ad823d'));C.circle(cx+x*s,cy+y*s,10.25*s,fill=0,stroke=1);C.circle(cx+x*s,cy+y*s,3*s,fill=0,stroke=1)
for a in range(30,360,60):
 x,y=83*math.cos(math.radians(a)),83*math.sin(math.radians(a));C.setFillColor(HexColor('#6b808d'));C.circle(cx+x*s,cy+y*s,6*s,fill=1,stroke=0)
dim(cx,cy-100*s,cx,cy+100*s,'200 AF',dx=-182)
dim(cx-200/math.sqrt(3)*s,cy,cx+200/math.sqrt(3)*s,cy,'230.940 across corners',dy=166)
C.setDash(3,3);C.setStrokeColor(HexColor('#bdcbd2'));C.line(cx-175,cy,cx+175,cy);C.line(cx,cy-150,cx,cy+150);C.setDash()
text(90,150,'PLAN - cover removed to show layout',9,True)
# Elevation; not a sectional component drawing.
x0=cx-200/math.sqrt(3)*s;y0=65
C.setFillColor(HexColor('#dbe5eb'));C.rect(x0,y0,400/math.sqrt(3)*s,50*s,fill=1,stroke=1)
dim(x0+400/math.sqrt(3)*s,y0,x0+400/math.sqrt(3)*s,y0+50*s,'50',dx=15)
text(105,52,'ELEVATION - fixed rim defines overall height',8)
table(455,480,[['Design dimension','Value'],['Width across flats','200.000 mm'],['Width across corners','230.940 mm'],['Hexagon side length','115.470 mm'],['Housing wall / base','3.0 / 5.0 mm'],['Cover AF / thickness','192.0 / 6.0 mm'],['Tread thickness','2.0 mm'],['Cover-to-wall clearance','1.0 mm at each flat'],['Guide stations','R78; 60°, 180°, 300°'],['Beam axes','0°, 120°, 240°'],['Structural stop stations','R83; 30° + n × 60°']], [180,171],9)
para(455,126,'<b>Width assumption:</b> “20 cm width” is interpreted as across opposite flats. A 200 mm corner-to-corner hexagon would be only 173.205 mm across flats and needs a redesigned internal layout.',350,9)
C.showPage()

# 3 - section through beam / opposite guide
header(3,'Section: the cover moves, the base stays fixed','Nominal undeformed geometry. Diagram shows the beam axis and opposite guide; strokes are not exaggerated.')
s=2.9;cx=420;y0=280
def R(x,z,w,h,col):box(cx+x*s,y0+z*s,w*s,h*s,col)
R(-115.47,0,230.94,5,'485a6a');R(-115.47,5,3.464,45,'485a6a');R(112.006,5,3.464,45,'485a6a')
R(-110.851,42,221.702,6,'a5b7c7');R(-110.851,48,221.702,2,'177b79')
# opposite guide cross section
R(-81,5,6,31,'c8d3df');R(-83,36,10,3,'c8d3df')
R(-85,25,3,11,'a5b7c7');R(-74,25,3,11,'a5b7c7');R(-85,36,1.7,2,'a5b7c7');R(-72.7,36,1.7,2,'a5b7c7')
R(-90,38,24,4,'a5b7c7');R(-83.3,38,10.6,4,'ffffff')
R(-82,25,.95,11,'41576a');R(-74.95,25,.95,11,'41576a')
R(-81,5,6,31,'c8d3df');R(-83,36,10,3,'c8d3df')
# Spring cross-section wire centres, symbolic projection.
C.setFillColor(HexColor('#dfb45d'))
for zz in (6.25,8.75,13.95,19.15,24.35,29.55,34.75,36.75):
 for xx in (-87,-69):C.circle(cx+xx*s,y0+zz*s,1.25*s,fill=1,stroke=0)
# beam and clamp
R(22,28.355,12.7,13.645,'41576a');R(22,24.645,12.7,3,'41576a');R(22,27.745,63.5,.51,'8272cb')
R(75.5,24.645,10,3,'ce9560');R(75.5,28.355,10,1.5,'41576a')
R(73.5,39,14,3,'41576a');R(73.5,30.755,14,.8,'41576a');R(73.5,22.545,14,1.2,'c8d3df')
R(75.5,30.455,10,.3,'263743');R(75.5,23.745,10,.3,'263743')
# electronics hood in section
R(-26,5,1.5,14,'bddedb');R(24.5,5,1.5,14,'bddedb');R(-26,17.5,52,1.5,'bddedb');R(-22,8.5,44,1.6,'258979')
dim(cx+34.7*s,y0+27.745*s,cx+85.5*s,y0+27.745*s,'50.8 free span',dy=-48)
dim(cx+22*s,y0+28.355*s,cx+34.7*s,y0+28.355*s,'12.7 clamp',dy=73)
text(58,465,'Guided return assembly',11,True);arrow(190,455,cx-78*s,y0+36*s)
text(530,465,'Root moves with cover',11,True);arrow(570,455,cx+28*s,y0+37*s)
text(647,228,'Protected tip mass',10,True);arrow(695,240,cx+80.5*s,y0+26*s)
text(62,235,'Guide head retains the cover at rest.',9);text(62,222,'1.0 mm head clearance at full stroke.',9)
table(36,190,[['Vertical datum','z at rest / mm'],['Underside of tile','0.000'],['Pan floor surface','5.000'],['Piezo mid-plane','28.000'],['Spring upper seat','38.000'],['Metal stop top','40.000']], [207,150],9)
table(450,190,[['Vertical datum','z at rest / mm'],['Bumper top','40.500'],['Moving plate underside','42.000'],['Plate upper surface','48.000'],['Tread / fixed rim upper surface','50.000'],['Plate underside after 2 mm stroke','40.000']], [221,135],9)
C.showPage()

# 4 - cartridge detail
header(4,'Cantilever cartridge: three identical modules','Each cartridge is attached beneath the moving cover. All tip fasteners straddle the ceramic.')
img('Cantilever_Cartridge',10,182,540,315)
table(560,483,[['Feature','Nominal'],['Beam envelope [1]','63.5 × 31.8 × 0.51'],['Clamped length','12.7'],['Free beam length','50.8'],['Mass-centre lever arm','45.8'],['Proof-mass blank','10 × 40 × 3'],['Tip cap','10 × 40 × 1.5'],['Electrical shims','0.10 each side'],['Upper / lower flat gaps','0.60 / 0.60'],['Visual tip-centre range','±0.45']], [137,111],9)
text(36,174,'A protective cage follows the cover',12,True)
y=para(36,157,'The upper and lower pads travel with the beam root. They limit <b>relative</b> mass motion; they do not define the 2 mm cover stroke. Screws are outside the beam edges, so no holes are drilled through PZT.',465,10)
para(36,y,'Tip rotation matters. With a 45.8 mm lever arm, a 0.45 mm centre displacement gives about 0.845° pitch. The minimum nominal edge clearance is about <b>0.0765 mm</b>. This is a geometric check, not an impact or fatigue guarantee.',465,10)
para(560,152,'<b>Source and modelling boundary</b><br/>The selected reference bender is Piezo.com T220-A4BR-2513XB, a PZT 5A/brass bimorph [1]. It is modelled as its published external envelope. Internal adhesive/electrode thicknesses are not reverse-engineered. Clamp preload and permissible tip mass need supplier confirmation.',246,9)
C.showPage()

# 5 calculations
header(5,'Spring and beam calculations','Screening estimates for understanding and prototype selection; these are not measured output or strength results.')
text(36,484,'Cover return springs',14,True)
para(36,465,'Three custom target springs: wire diameter <b>d = 2.5 mm</b>; mean coil diameter <b>D = 18 mm</b>; five active turns, seven total turns; assumed shear modulus <b>G = 79,000 N/mm²</b>. Free length 34 mm, installed length 33 mm.',360,10)
box(36,332,360,69)
text(48,377,'k = Gd⁴ / (8D³n) = 13.23 N/mm per spring',11,True)
text(48,353,'K = 3k = 39.69 N/mm total',11,True)
table(36,317,[['Idealised quantity','Value'],['Initial spring force (1 mm preload)','39.69 N total'],['Spring force after 2 mm downstroke','119.06 N total'],['Additional force over the stroke','79.37 N'],['Minimum spring length at full stroke','31 mm'],['Approximate solid length, 7 × 2.5','17.5 mm'],['Increase in stored spring energy','0.159 J']], [254,106],9)
para(36,117,'Spring force is not the net foot force: the moving assembly weight and seal friction also act. Most walking loads will bring this low-travel design onto its stops. Springs store and return mechanical energy; that stored energy is not an electrical-output prediction.',360,9)
text(444,484,'Mass-loaded piezoelectric beam',14,True)
y=para(444,465,'Use a first-mode model about the gravity-deflected equilibrium:<br/><b>m q̈ + c q̇ + kq + electrical coupling = −m ÿ</b><br/>Here y is cover motion and q is mass motion relative to the cover. Cover acceleration drives the beam.',362,10)
y=para(444,y,'For an illustrative estimate, assume the supplier’s quoted stiffness of 0.388 N/mm applies to a 50.8 mm free span [1]. Moving the force application to 45.8 mm gives k ≈ 0.388(50.8/45.8)³ ≈ <b>0.530 N/mm</b>. This mounting assumption must be checked.',362,10)
y=para(444,y,'A 9.60 g steel mass blank plus cap/fasteners and effective beam mass gives roughly 12 g effective modal mass. Then f ≈ (1/2π)√(k/m) ≈ <b>33 Hz</b>. Estimated static sag is around <b>0.2 mm</b>; CAD is shown flat before sag.',362,10)
y=para(444,y,'A walking cadence of a few steps per second does not continuously excite a 33 Hz resonance. The idea relies on the acceleration transient and subsequent vibration. Actual damping and the circuit strongly affect how much energy is collected.',362,10)
box(444,70,362,53)
para(456,112,'<b>Required measurement:</b> use the measured capacitance and ΔE = ½C(Vf² − Vi²), then divide by counted activations. Subtract leakage and account for any load current.',337,9)
C.showPage()

# 6 electrical design
header(6,'Electrical architecture and connectivity','A complete reference topology with provisional board placement; not a routed or fabrication-ready PCB.')
for i,y in enumerate((455,402,349),1):
 box(36,y-30,115,35,'ece8f6');text(48,y-16,f'PZT beam {i}',10,True)
 box(185,y-30,146,35,'e7f1ef');text(196,y-16,f'Bridge {i}: 4 diodes',10,True);arrow(151,y-12,184,y-12)
 C.setStrokeColor(HexColor(TEAL));C.line(331,y-12,359,y-12)
C.line(359,337,359,443);arrow(359,402,394,402,TEAL)
box(394,368,145,68);text(406,410,'Rectified DC bus',10,True);text(406,391,'CIN: 47 µF effective',9);text(406,376,'≥35 V; low leakage',9)
arrow(539,402,579,402)
box(579,367,105,69,'e7f1ef');text(588,406,'LTC3588-1',10,True);text(588,386,'3.3 V target',9)
arrow(684,402,723,402)
box(723,368,83,68);text(731,407,'COUT',9,True);text(731,390,'47 µF',9);text(731,375,'≥6.3 V',8)
para(36,294,'<b>Why one rectifier per beam?</b> The three beams need not vibrate in phase. Rectifying separately before joining the DC outputs avoids directly opposing their AC voltages. The LTC3588-1 internal bridge is bypassed here; the external DC bus feeds VIN. Verify this implementation and leakage on a bench [2].',770,10)
table(36,236,[['Connection','Reference design'],['Each bridge, AC terminals A/B','D1: A → DC+; D2: B → DC+; D3: GND → A; D4: GND → B. Arrows denote anode → cathode.'],['Regulator input / unused AC inputs','VIN to rectified DC+; ground/exposed pad to GND. PZ1 and PZ2 left unconnected.'],['Buck and output','SW → 10 µH inductor → VOUT; COUT between VOUT and GND; PGOOD available at test pad.'],['Rail capacitors / voltage selection','1 µF CAP-to-VIN; 4.7 µF VIN2-to-GND. D1 tied to VIN2, D0 to GND for 3.3 V.'],['Qualification points','Measure diode leakage, capacitor effective C and cold start. Allow for nominal ~5.05 V start-up at 3.3 V setting [2].']], [201,569],9)
para(36,78,'No battery is fitted. A low-duty-cycle sensor or switched LED is a candidate load only after energy measurement. The 44 × 44 mm board, parts and hood are mechanical placement envelopes; footprints, routing and exact capacitor packages remain provisional.',770,8)
C.showPage()

# 7 materials and parts
header(7,'Materials and bill of materials','All 142 individual components are listed in BOM.csv and selectable in the 3D viewer.')
table(36,485,[['Assembly / quantity','Material and function'],['1 housing with 6 integral stops','6061-T6 aluminium. 5 mm base, 3 mm sidewalls. Stops end at z40.'],['1 cover + 1 tread','6 mm aluminium load spreader; 2 mm replaceable EPDM tread.'],['3 guide sets','Steel headed guide, aluminium spring-seat cup, POM sleeve.'],['3 return springs','Custom spring-steel targets; 2.5 mm wire / 18 mm mean diameter.'],['3 piezoelectric beams','Reference PZT 5A/brass bimorphs; supplier external dimensions [1].'],['3 root clamp sets','POM tower + clamp shoe; polyimide electrical isolation.'],['3 proof-mass sets','Stainless steel mass + POM cap + isolating shims.'],['3 limiter cages','POM cage, removable steel bottom, two EPDM stop pads.']], [191,185],9)
table(444,485,[['Assembly / quantity','Material and function'],['6 stop bumper rings','EPDM; nominal compression 0.5 mm at full stroke.'],['1 wiper + 1 cable grommet','EPDM lip in the sidewall groove; underside cable port.'],['1 PCB + splash hood','FR4 reference board; polycarbonate hood bonded to pan.'],['18 cover screws','M3 countersunk reference geometry.'],['3 guide anchor screws','M4 countersunk nominal custom-length envelopes.'],['6 root / 6 tip screws','M3 root clamp / M2 tip clamp screws.'],['6 cage + 4 PCB screws','M2 nominal hardware envelopes.'],['Wires and electrical components','Fine flexible leads, three bridge rectifiers, regulator, capacitors, inductor and connectors.']], [179,183],9)
text(36,154,'Material choices for the library corridor',12,True)
para(36,136,'The proposed rubber tread, polymer guide liners and buffered stops address contact noise, but their acoustic benefit has not been measured. A wipeable lip and drained pan address incidental water; the hood protects electronics only if its bond and feedthroughs are qualified.',373,9)
para(444,151,'Bio-based polymer samples can be investigated for removable cosmetic parts. This revision uses aluminium for the structural cover and stops because no creep, impact or moisture data have been supplied for a bioplastic formulation. Printed PLA copies are display models, not step-on products.',362,9)
C.showPage()

# 8 build and tolerances
header(8,'Assembly sequence and fit control','Prototype workflow. Dimensions are nominal; fit tolerances below are proposed targets requiring manufacturing review.')
steps=[('1','Prepare the pan','Machine the pocket, six stop pillars, wiper groove, drain holes and anchor bores. Deburr all edges; verify the six stop tops are coplanar.'),
 ('2','Build the three cartridges','Fit insulating shims, root clamps and tip clamps. Keep fasteners outside the ceramic. Fit the limiter cages; confirm the top/bottom gaps optically.'),
 ('3','Install captive guides','Insert each headed guide through its cup and sleeve. Seat springs and guides on the pan. Hold each guide in a fixture while securing its underside anchor screw.'),
 ('4','Fit electronics and wiring','Assemble and bench-test the circuit separately. Install the board/hood and route flexible service loops clear of springs, beam spans and cage stops.'),
 ('5','Close the tile','Lower the cartridge-loaded cover onto the three guide-cup flanges and secure its top screws. Verify return and retention. Fit the wiper and replaceable tread.'),
 ('6','Qualify on a fixture','Use controlled mechanical loading on the bench. Check return motion, edge loading, electrical output and repeated cycling before considering foot use.')]
y=484
for n,title,body in steps:
 box(36,y-22,25,25,'d9efeb');text(43,y-14,n,11,True,TEAL);text(73,y-4,title,11,True);y=para(73,y-15,body,329,9)-10
table(444,485,[['Fit / feature','Proposed target'],['Aluminium noncritical dimensions','±0.10 mm'],['Polymer noncritical dimensions','±0.15 mm; account for temperature/moisture'],['Stop top height / coplanarity','40.00 ±0.05 mm / within 0.05 mm'],['Guide shaft / sleeve bore','Ø6.00 −0.01/0; bore Ø6.10 +0.02/0'],['Radial guide clearance','0.050 to 0.065 mm, before alignment effects'],['Tip stop gaps','0.60 ±0.05 mm; measure assembled'],['Cover clearance at flats','1.0 mm nominal each side'],['Thread geometry','Tap sizes / thread classes set at manufacture; STEP threads are simplified']], [180,182],9)
para(444,162,'<b>Assembly access matters.</b> Lower guide-anchor screws are accessed from the underside. Cage bottoms are removable for beam service. Cover screws are accessed after peeling or removing the tread. The floor installation must allow the tile to be removed.',362,9)
para(444,89,'Supplier clamp instructions [3] are useful background, but their torque values do not automatically apply to these custom POM clamps. Establish preload experimentally with the actual beam and shims.',362,8)
C.showPage()

# 9 evidence / references / package use
header(9,'What has been checked, and what comes next','The CAD is inspectable and editable. Precision of geometry must not be mistaken for proven floor performance.')
V=json.loads((ROOT/'geometry_validation.json').read_text())
table(36,485,[['Check','Result / boundary'],['Solid validity','142 components valid in OpenCascade.'],['Nominal rigid interference','No unintended overlaps found at rest or at 2 mm cover stroke.'],['Envelope','200.000 mm flats; 230.940 mm corners; 50.000 mm height.'],['Tip pitch at ±0.45 mm','Nominal minimum edge gap ≈0.0765 mm.'],['Excluded from rigid verdict','Thread engagement envelopes, PCB packages and indicative wire routing.'],['Not yet performed','FEA, local heel/edge loads, fatigue, wear, ingress/slip/acoustic tests or electrical-output tests.']], [160,215],9)
y=225
text(36,y,'Before any real corridor installation',12,True)
y=para(36,y-15,'Verify local cover bending, off-centre loading and guide binding; qualify the beam clamps, tip-mass retention and overtravel impacts. Check wet grip, raised-edge hazards, liquid paths and a removable flush mounting frame. No pedestrian load rating or IP rating is claimed.',375,9)
text(36,y-5,'Open the package',12,True)
para(36,y-21,'<b>HTML:</b> open HEX_200_Interactive.html in a current desktop browser; all viewer resources are embedded.<br/><b>CAD:</b> import CAD/HEX_200_Assembly.step in millimetres. Individual representative parts are included.<br/><b>STL:</b> units are mm; meshes are for visualisation/display prototypes.<br/><b>Source:</b> build_tile.py rebuilds the fixed Rev A design. Editing the width alone does not automatically redesign the mechanism.',375,9)
text(444,485,'Sources and provenance',13,True)
refs=[
 ('[1] Piezo.com, T220-A4BR-2513XB','Published external dimensions, PZT 5A/brass construction and stiffness reference. Accessed 22 September 2026.','https://piezo.com/products/piezoelectric-bending-transducer-t220-a4br-2513xb'),
 ('[2] Analog Devices, LTC3588-1 datasheet','Reference regulator connections and start-up behaviour. The proposed three-bridge circuit and board arrangement are this design’s engineering choices.','https://www.analog.com/media/en/technical-documentation/data-sheets/35881fc.pdf'),
 ('[3] Piezo.com, Mounting Guidelines','Background on clamp practice and fixing security. Commercial-kit torque recommendations are not adopted for the custom clamps.','https://support.piezo.com/article/126-mounting-guidelines'),
 ('[4] Piezo.com, Wiring Guidelines','Background on electrode connection and lead strain relief. Exact terminations need qualification with the purchased device.','https://support.piezo.com/article/127-wiring-guidelines')]
y=462
for title,body,url in refs:
 text(444,y,title,9,True);y=para(444,y-9,body,362,8)
 y=para(444,y,f'<link href="{url}" color="#137a77">{url}</link>',362,8)-8
para(444,105,'<b>Original work:</b> hexagonal geometry, spatial arrangement, spring target, captive guides, protective cages, clearances, diagrams and CAD were developed for this request. The supplied sketch inspired the mechanism; it did not provide a complete specification. Renders are derived from CAD, not AI-generated pictures.',362,9)
C.showPage();C.save()
print(ROOT/'HEX_200_Technical_Design.pdf')
