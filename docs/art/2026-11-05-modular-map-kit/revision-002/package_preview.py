#!/usr/bin/env python3
"""Isolated derived viewer: replace inherited fixed-screen rider sizing.
No PNG editing, source-road changes or overwrites of an editable map.
"""
import hashlib
import json
import shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'revision-001'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    viewer = HERE / 'viewer'
    if viewer.exists(): raise SystemExit('Refusing to overwrite candidate viewer')
    protected = [OLD/'integration/revision.tmj', OLD/'viewer/assets/scene-layout.json', OLD/'viewer/assets/main/index.probe41.js']
    before = {str(p): sha(p) for p in protected}
    shutil.copytree(OLD/'viewer', viewer)
    js = viewer/'assets/main/index.probe41.js'
    code = js.read_text()
    old = 'Math.max(125.53459833468403,124.00368859889521/(s-a),109.55572796738814/((h-o)*i.nativeSize[1]/i.nativeSize[0]))'
    new = 'this.layout.rider.displayOpaqueWidthUnits*this.ppm*this.initialZoom/(s-a)'
    assert code.count(old) == 1
    code = code.replace(old, new)
    oldshadow = '95/this.initialZoom,47.5/this.initialZoom'
    assert code.count(oldshadow) == 1
    code = code.replace(oldshadow, 'this.layout.rider.displayShadowWidthUnits*this.ppm,this.layout.rider.displayShadowWidthUnits*this.ppm*.5')
    oldzoom = 'Math.max(t.initialZoom,Math.min(1.6*t.initialZoom,t.zoom*e))'
    assert code.count(oldzoom) == 1
    code = code.replace(oldzoom, 'Math.max(.35*t.initialZoom,Math.min(8*t.initialZoom,t.zoom*e))')
    js.write_text(code)
    lp = viewer/'assets/scene-layout.json'
    layout = json.loads(lp.read_text())
    layout['rider'].update(displayOpaqueWidthUnits=2.2, displayShadowWidthUnits=1.6)
    layout['status'] = 'isolated-world-scale-rider-candidate-not-accepted'
    lp.write_text(json.dumps(layout, ensure_ascii=False, indent=2)+'\n')
    assert layout['roads'] == json.loads((OLD/'viewer/assets/scene-layout.json').read_text())['roads']
    assert layout['blocks'] == json.loads((OLD/'viewer/assets/scene-layout.json').read_text())['blocks']
    assert before == {str(p): sha(p) for p in protected}
    pngs = list((viewer/'assets').glob('*.png'))
    assert all(sha(p)==sha(OLD/'viewer/assets'/p.name) for p in pngs)
    evidence = {'status':'static-package-verification-only', 'oldFixedOpaqueWidthAt720':124.00368859889521,
      'newOpaqueWidthUnitsCandidate':2.2, 'newOpaqueWidthAt720With80UnitView':19.8,
      'sourceRoadsAndBlocksUnchanged':True, 'oldRevisionUnchanged':True,
      'nativePNGBytesPreserved':len(pngs), 'editableTiledSource':'../revision-001/integration/revision.tmj',
      'patchedDerivedBundle':str(js.relative_to(HERE)),
      'engineRebuilt':False, 'gameTestsRun':False, 'cameraAccepted':False,
      'caveats':['2.2 units is a display candidate, not measured vehicle length.', 'Camera/road perspective mismatch and edge fringes remain.'],
      'protectedSHA256':before}
    (HERE/'verification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(evidence,ensure_ascii=False))
if __name__ == '__main__': main()
