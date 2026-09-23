from pathlib import Path
import gzip,base64,os
ROOT=Path(__file__).resolve().parents[1]
template=(ROOT/'source/viewer_template.html').read_text()
three=(ROOT/'source/vendor/three.module.js').read_text()
pako=(ROOT/'source/vendor/pako_inflate.min.js').read_text()
mesh=ROOT/'meshes/preview_meshes.json'
if not mesh.exists():mesh=ROOT/'meshes/assembly_meshes.json'
data=base64.b64encode(gzip.compress(mesh.read_bytes(),compresslevel=9)).decode()
out=template.replace('__PAKO__',pako).replace('__THREE__',three).replace('__DATA__',data)
(ROOT/'HEX_200_Interactive.html').write_text(out)
print('Offline HTML bytes',len(out))
