# HEX-200 - detailed hexagonal piezoelectric tile concept

Revision A / 22 September 2026 / HBIS Collaborative Sciences Project

The regular hexagon is **200 mm across opposite flats**, 230.940 mm across
opposite corners and 50 mm high. This interpretation of “20 cm width” was an
explicit design assumption. The moving cover has a 2 mm downstroke.

## Start here

- `HEX_200_Interactive.html`: offline interactive 3D assembly. Open the downloaded
  file in a current desktop browser with WebGL 2. Rotate, zoom, inspect components,
  remove the cover, section the housing, separate components, or adjust the two
  illustrative motion controls. All scripts and meshes are embedded; no server
  or internet connection is required. File-preview apps may not execute HTML.
- `HEX_200_Technical_Design.pdf`: nine illustrated pages with dimensions, section,
  mechanism, calculations, circuit connections, materials, assembly and limits.
- `CAD/HEX_200_Assembly.step`: the editable solid assembly. **Units: millimetres.**
  This is the authoritative nominal shape representation.
- `HEX_200_Assembly.glb`: coloured visual 3D model. Its world scale is **metres**,
  as required by glTF. The root applies 0.001 to CAD coordinates in millimetres.
- `CAD/*.step`: representative individual components. Repeated parts are included
  at their first assembly location; the complete STEP contains every instance.
- `meshes/*.stl`: representative display / fit-study meshes in **mm**. Parts retain
  their assembly coordinates. These files do not qualify a printed part for loads.
- `CAD/Cover_Plate_Reference.dxf`: cover outline, 18 through holes and countersink
  reference circles in mm. Layer names distinguish through and reference geometry.
  This is a reference drawing, not a released laser/CNC job.
- `Cover_Hole_Coordinates.csv`: exact nominal XY coordinates of all 18 cover holes.
- `BOM.csv`, `parts_manifest.json`: 142 component records, materials and notes.
- `Electrical_Connections.csv`: reference circuit connectivity, not a SPICE model
  or PCB manufacturing file.
- `geometry_validation.json`: verification scope and nominal results.
- `figures/`: CAD-derived assembled, inside, exploded and cartridge renderings.

## Mechanism

The cover carries three PZT/brass bimorph beams. Their tip masses lag when the
cover accelerates, creating bending and an electrical response. Three springs
return the cover; six separate aluminium stop pillars carry the foot load after
2 mm of travel. Moving cages constrain relative tip motion. Three separate bridge
rectifiers feed a shared DC bus and a reference LTC3588-1 regulator circuit.

Cover stroke and beam deflection are independent quantities. The viewer’s beam
control is a geometric illustration, not a dynamic simulation or predicted
response. ±0.45 mm refers to total tip-centre displacement from the nominal flat
beam, including any static offset; it is not extra travel on top of gravity sag.

## Accuracy and verification

- All 142 CAD component shapes are valid in OpenCascade.
- The nominal rigid-part check found no unintended overlaps at rest or with the
  moving assembly 2 mm lower. Intended thread engagement, deforming bumper pads,
  wire routes and provisional PCB packages are excluded as stated in the report.
- The exact imported pan envelope measures 230.940107676 × 200 × 50 mm.
- Tip pitch at ±0.45 mm centre displacement leaves about 0.0765 mm nominal edge
  clearance. Manufacturing tolerances and dynamic impacts are not covered by that
  geometric result.
- The commercial bender is its published 63.5 × 31.8 × 0.51 mm mechanical envelope.
  Electrode and adhesive microgeometry is not reconstructed. Thread helices are
  omitted in the usual simplified fastener representations.
- Light visual meshes are decimated. Use STEP, not the visual meshes, for exact
  face/edge inspection. The renderings come from CAD triangles, not image generation.
- The viewer's JavaScript syntax and embedded mesh data were checked. A WebGL
  browser runtime was not available in the authoring environment, so live browser
  interactions were not independently executed there.

**This is an engineering concept for a CSP and bench development, not a fabrication
release or certified walkway product.** No measured electrical output, structural
load rating, fatigue life, slip class, acoustic performance or ingress rating is
claimed. The circuit board and electronic packages are placement references;
there are no Gerber files. Guide alignment, clamp preload, spring supply, wire
routing and seals require prototype qualification. A surrounding flush floor
mount / drainage arrangement is outside the single-tile scope.

## Rebuilding the CAD

The source was run with Python 3.12 and CadQuery 2.7.0:

```sh
python -m pip install -r source/requirements.txt
python source/build_tile.py
python source/check_geometry.py
```

This is a **fixed Rev A, dimensioned CAD construction script**. The exported
`parameters.json` records the design values; it is not an automatically consumed
configuration file. Changing just the width does not redesign the mechanisms.
Edit the coordinated dimensions in the script and repeat the clearance checks.
`build_tile.py` overwrites the generated geometry and BOM outputs.

Optional presentation rebuild, after regenerating the CAD:

```sh
python source/preview_meshes.py
python source/make_viewer.py
python source/render_raster.py
python source/make_report.py
```

The report script uses system DejaVu font paths; adjust them on other systems.
The DXF and connection CSV files in this release are independent reference
deliverables and are not regenerated by `build_tile.py`.

## References

1. [Piezo.com T220-A4BR-2513XB](https://piezo.com/products/piezoelectric-bending-transducer-t220-a4br-2513xb)
2. [Analog Devices LTC3588-1 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/35881fc.pdf)
3. [Piezo.com mounting guidelines](https://support.piezo.com/article/126-mounting-guidelines)
4. [Piezo.com wiring guidelines](https://support.piezo.com/article/127-wiring-guidelines)

The user-supplied spring/cantilever sketch inspired the mechanism. Unspecified
dimensions, arrangement and protective details were designed for this request.

The embedded Three.js engine and pako library are MIT-licensed third-party tools;
their licences are included under `source/vendor/`.
