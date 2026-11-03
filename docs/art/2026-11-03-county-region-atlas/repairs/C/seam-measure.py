"""Cross-art manual seam observations; not a game test, not pixel perfect acceptance."""
import json,math
from pathlib import Path
O=Path(__file__).resolve().parent; B=O.parent.parent;q=math.sqrt(.5);st=math.sin(math.radians(62.5))
c=json.loads((O/'region-entry.json').read_text());a=json.loads((B/'registration/region-A-AB-v4-runtime-entry.json').read_text());d=json.loads((B/'repairs/D/region-D-runtime-entry.json').read_text())
def unproject(p,e):
 s=e['nativePixelsPerUnit'];x=(p[0]-1254*e['anchorUV'][0])/s;y=(p[1]-1254*e['anchorUV'][1])/s/st
 return [e['anchorMap'][0]+q*(x+y),e['anchorMap'][1]+q*(y-x)]
def compare(id,map,cp,other,op,unc,note):
 cm=unproject(cp,c);om=unproject(op,other);dist=math.dist(cm,om)
 return dict(id=id,sourceMap=map,CObservedNativePixel=cp,otherRegion=other['id'],otherObservedNativePixel=op,CInferredMap=cm,otherInferredMap=om,crossArtDifferenceMapUnits=dist,crossArtDifferenceCNativePixels=dist*c['nativePixelsPerUnit'],manualUncertaintyCNativePixels=unc,note=note)
rows=[
compare('A-C-service-y140',[-1630.3388970588235,140],[602.5,173.8],a,[66,697],18,'C pixel interpolated along restored service lane; A original manual edge. Same source lane is now visibly separate.'),
compare('A-C-main-y140',[-1607.7114874583406,140],[687.6,287.3],a,[169,770],18,'C pixel interpolated from upper T to main-road outline exit, approximate; A manual edge.'),
compare('A-C-lower-y140',[-1536.255407725322,140],[1086.9,650.4],a,[530,1114],18,'C pixel interpolated on lower transverse street, approximate; A manual edge.'),
compare('C-D-main-x1536',[-1536,184.00205427408412],[818.8,863.1],d,[365,310],18,'C pixel interpolated between restored lower junction and branch exit; D actual west road observation. No building-ownership claim.'),
]
(O/'seam-diagnostics.json').write_text(json.dumps({'status':'measured-approximate-not-ownership-closed','observations':rows,'C-D-north':None,'reason':'Only three A shared-edge observations and one D shared-road interpolation can be paired honestly. Other matching buildings/edges not measured. Do not claim seamless or reject the whole interior based on edge errors.'},indent=2)+'\n')
for r in rows:print(r['id'],round(r['crossArtDifferenceMapUnits'],2),round(r['crossArtDifferenceCNativePixels'],1))
