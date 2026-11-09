#!/usr/bin/env python3
"""006 library build/validate. No image edits, no source/005 writes."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,shutil,math,argparse
from pathlib import Path
from PIL import Image
I=Path(__file__).resolve().parent;R=I.parent;B=R.parent;OLD=B/'revision-005';V=R/'viewer';A=I/'assets'
def read(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def protected():
 files=[p for p in OLD.rglob('*') if p.is_file()]+[p for p in (R/'native').glob('B*-001/*') if p.is_file()]+[p for p in (R/'native').glob('V*-002/*') if p.is_file()]+[R/'planning/source-context.json',Path(read(R/'planning/source-context.json')['source'])]

 return {str(p.resolve()):sha(p) for p in files}
# Visible exterior ground controls left/front/right, hidden rear inferred by parallelogram.
# Irregular occupied contours below remain separate from this scale-only envelope.
SPECS={
 'B06':{'corners':[[158,971],[390,1198],[1090,878]],'dims':[11,7,7.5],'wallRisePx':245,'entry':[730,1038],'shape':'asymmetric pitched residential + flat wing','risk':'left pitched mass and low flat wing; inset connector/entry not a full cuboid'},
 'B07':{'corners':[[155,748],[409,1125],[1100,784]],'dims':[18,12,10],'wallRisePx':320,'entry':[746,825],'shape':'U courtyard, open notch','outline':[[155,748],[409,1125],[555,1053],[343,735],[759,590],[942,862],[1100,784],[846,407]],'void':[[555,1053],[942,862],[759,590],[343,735]],'risk':'open courtyard and wing ends must remain unblocked; hidden rear outline inferred'},
 'B08':{'corners':[[90,785],[491,970],[1400,536]],'dims':[15,9,6.5],'wallRisePx':205,'entry':[820,803],'shape':'connected multi-barrel hall + curved annex','outline':[[90,785],[280,883],[330,930],[410,962],[491,970],[1400,536],[999,351]],'risk':'more roof spans/annexes than source candidate; curved annex expands side envelope; warm glazing, alpha maximum254, low alpha perimeter'},
 'B09':{'corners':[[110,640],[868,962],[1426,704]],'dims':[14,10,8],'wallRisePx':235,'entry':[480,895],'shape':'fan shell + curved foyer + rectangular side wings','outline':[[110,640],[260,721],[280,830],[340,888],[470,918],[600,889],[868,962],[1426,704],[1100,545],[868,640],[668,532]],'risk':'fan shell roof overhang is not ground footprint; curved foyer and support wings need separate clearances; alpha maximum254'},
 'B10':{'corners':[[100,930],[443,1170],[1173,835]],'dims':[13,9,6],'wallRisePx':340,'entry':[760,1014],'shape':'multi-bay sawtooth factory','risk':'sawtooth tips are not wall height; broad loading entry requires apron'},
 'B11':{'corners':[[104,929],[770,1170],[1172,950]],'dims':[10,7,5],'wallRisePx':245,'entry':[241,920],'shape':'staggered pitched workshop; short-side roller door','outline':[[104,929],[356,1036],[421,1013],[770,1170],[1172,950],[506,709]],'risk':'roller door on visible left short side, entry must use reachable side yard; not long-front centre','entrySide':'short-side'} }
def build():
 A.mkdir(exist_ok=True);baseline=I/'inputs-before.json'
 if not baseline.exists():write(baseline,protected())
 old=read(OLD/'integration/asset-manifest.json');cal=read(OLD/'integration/asset-calibration.json');assets=[];checks=[]
 for c in read(OLD/'integration/provenance-check.json'):
  assert sha(c['source'])==sha(c['native'])==c['sha256'];checks.append(dict(c,verificationScope='rechecked-retained005-tool-source'))
 for a in old['assets']:
  a=dict(a);src=OLD/'integration/assets'/a['file'];assert sha(src)==a['sha256'];shutil.copyfile(src,A/a['file']);a['availability']='hold-comparison-only' if a['id']=='T03' else 'retained-005';assets.append(a)
 oldplan=read(OLD/'planning/mixed-street-layout.json')
 for ca in cal['assets']:
  if ca['id'].startswith('B'):
   ob=next(b for b in oldplan['buildings'] if b['id']==ca['id']);ca['candidateDimensionsFrontageDepthHeight']=[ob['dimensionsCandidate'][k] for k in ['frontage','depth','height']];ca['candidateDimensionStatus']='retained005 PM candidates, not measured dimensions';ca['candidateFootprintPolygonMapAt005Placement']=ob['footprintPolygonMap']
  ca['status']='retained-005-accepted-scale' if ca['id'] in ['B01','T01'] else 'retained-005-candidate'
  if ca['id']=='T03':ca['availability']='comparison-only-hold-for-bulk-placement'
 ref=read(OLD/'planning/mixed-street-layout.json')['referenceFrame'];p=old['projection'];u=ref['frontageTangent'];n=ref['positiveRoadNormal']
 def pr(q):return [q[0]*p['axisX'][k]+q[1]*p['axisY'][k] for k in (0,1)]
 pu,pn=pr(u),pr(n);lu,ln=math.hypot(*pu),math.hypot(*pn)
 def local(pixel,anchor,ppu):
  x=(pixel[0]-anchor[0])/ppu;y=(pixel[1]-anchor[1])/ppu;det=pu[0]*pn[1]-pn[0]*pu[1];return [(x*pn[1]-y*pn[0])/det,(pu[0]*y-pu[1]*x)/det]
 for aid,s in SPECS.items():
  root=R/f'native/{aid}-001';raw=root/f'{aid}-v1.png';rt=root/f'{aid}-runtime-280.png';prov=read(root/'provenance.json');source=Path(prov['toolSourceAbsolutePath']);der=read(rt.with_suffix('.runtime.json'));rawsha=sha(raw);assert sha(source)==rawsha==der['sourceSHA256'];assert rawsha in json.dumps(prov);assert sha(rt)==der['sha256'];assert list(Image.open(raw).size)==der['sourceSize'];assert list(Image.open(rt).size)==der['runtimeSize'] and max(der['runtimeSize'])<=280
  checks.append({'id':aid,'nativePath':str(raw.resolve()),'toolPath':str(source),'nativeSHA256':rawsha,'toolSHA256':sha(source),'runtimeSHA256':sha(rt),'nativeSize':der['sourceSize'],'runtimeSize':der['runtimeSize'],'sourceCopyEqual':True})
  left,front,right=s['corners'];rear=[left[k]+right[k]-front[k] for k in (0,1)];anchor=[(left[k]+right[k])/2 for k in (0,1)];lengths=[math.dist(front,right),math.dist(left,front)];target=[s['dims'][0]*lu,s['dims'][1]*ln];ppu=sum(a*b for a,b in zip(lengths,target))/sum(x*x for x in target)
  actualdims=[lengths[0]/ppu/lu,lengths[1]/ppu/ln];diff=[(actualdims[k]/s['dims'][k]-1)*100 for k in (0,1)];box=der['cropBox'];w,h=box[2]-box[0],box[3]-box[1];uv=[(anchor[0]-box[0])/w,(anchor[1]-box[1])/h];world=[w/ppu,h/ppu]
  outline=s.get('outline',[left,front,right,rear]);localoutline=[local(q,anchor,ppu) for q in outline];entry=local(s['entry'],anchor,ppu)
  ca={'id':aid,'status':'manual-candidate-not-registration-ready','sourceNativeSHA256':rawsha,'sourceNativeSize':der['sourceSize'],'runtimeSize':der['runtimeSize'],'nativePixelsPerUnit':ppu,'anchorPixel':anchor,'groundCornersPixelLeftFrontRightRear':[left,front,right,rear],'controlUncertaintyPx':25,'hiddenRearInferred':True,'cropBox':box,'anchorUV':uv,'worldSizeUnits':world,'scaleMethod':'single positive scalar least squares of two hand-estimated envelope edge lengths against PM candidate frontage/depth, no anisotropic scaling','candidateDimensionsFrontageDepthHeight':s['dims'],'inferredEnvelopeFrontageDepth':actualdims,'envelopeDeltaVsCandidatePercent':diff,'inferredEaveHeightUnits':s['wallRisePx']/ppu/abs(p['axisZ'][1]),'eaveHeightMethod':'hand-estimated wall rise; excludes pitched/shell/sawtooth roof rise, not total height measurement','shape':s['shape'],'occupiedGroundOutlineLocalTN':localoutline,'occupiedGroundOutlinePixel':outline,'courtyardVoidLocalTN':[local(q,anchor,ppu) for q in s.get('void',[])],'entryLocalTN':entry,'entryPixel':s['entry'],'entrySide':s.get('entrySide','visible-front-candidate'),'risk':s['risk'],'availability':'candidate-needs-in-scene-grounding','requiresFootprintReview':any(abs(v)>15 for v in diff),'positiveUniformOnly':True}
  ca['frontageChordAngleDeg']=math.degrees(math.atan2(right[1]-front[1],right[0]-front[0]));ca['depthChordAngleDeg']=math.degrees(math.atan2(front[1]-left[1],front[0]-left[0]));ca['chordCaveat']='curved/stepped outlines are envelope chords, not precise straight-edge camera measurements'
  if aid in ['B09','B11']:ca['availability']='hold-pending-footprint-and-entry-fit'
  if aid=='B10':ca['availability']='hold-depth-edge-pose-review';ca['risk']+='; visible straight short-edge chord about35deg versus target55.4deg, no stretching permitted'
  cal['assets'].append(ca);a={'id':aid,'kind':'building','file':rt.name,'sha256':sha(rt),'nativeSize':der['runtimeSize'],'nativePixelsPerUnit':1,'worldSizeUnits':world,'anchorUV':uv,'projectionId':p['id'],'runtimeDerivation':der,'availability':ca['availability']};assets.append(a);shutil.copyfile(rt,A/rt.name)
 for base,contacts,wheelbase,dims in [('V01',[[632,894],[1110,646]],2.55,[4.1,1.75,1.5]),('V02',[[621,941],[1093,665]],3.4,[5.8,2.05,2.7])]:
  aid=base+'-v2';root=R/f'native/{base}-002';raw=root/f'{base}-v2.png';rt=root/f'{base}-v2-runtime-280.png';prov=read(root/'provenance.json');source=Path(prov['toolSourceAbsolutePath']);der=read(rt.with_suffix('.runtime.json'));rawsha=sha(raw);assert sha(source)==rawsha==der['sourceSHA256'];assert rawsha in json.dumps(prov);assert sha(rt)==der['sha256']
  checks.append({'id':aid,'nativePath':str(raw.resolve()),'toolPath':str(source),'nativeSHA256':rawsha,'runtimeSHA256':sha(rt),'sourceCopyEqual':True,'nativeSize':list(Image.open(raw).size),'runtimeSize':list(Image.open(rt).size)})
  anchor=[sum(q[k] for q in contacts)/2 for k in (0,1)];ppu=math.dist(*contacts)/(wheelbase*lu);box=der['cropBox'];w,h=box[2]-box[0],box[3]-box[1];uv=[(anchor[0]-box[0])/w,(anchor[1]-box[1])/h];world=[w/ppu,h/ppu]
  ca={'id':aid,'status':'static-parking-comparison-only-not-user-accepted','sourceNativeSHA256':rawsha,'sourceNativeSize':der['sourceSize'],'runtimeSize':der['runtimeSize'],'nativePixelsPerUnit':ppu,'wheelContactPixelsManual':contacts,'anchorPixel':anchor,'anchorMeaning':'near-side visible wheel-contact midpoint, not surveyed vehicle centre; far wheels occluded','cropBox':box,'anchorUV':uv,'worldSizeUnits':world,'candidateDimensionsLengthWidthHeight':dims,'candidateWheelbaseUnits':wheelbase,'scaleMethod':'positive scalar from manually estimated visible wheelbase and candidate wheelbase, no measured metres claim','availability':'static-parking-comparison-only','risk':'coarse outline/highlights and residual native haze need actual street comparison; no traffic AI, no mirror or rotation'}
  cal['assets'].append(ca);assets.append({'id':aid,'kind':'parked-vehicle','file':rt.name,'sha256':sha(rt),'nativeSize':der['runtimeSize'],'nativePixelsPerUnit':1,'worldSizeUnits':world,'anchorUV':uv,'projectionId':p['id'],'runtimeDerivation':der,'availability':ca['availability']});shutil.copyfile(rt,A/rt.name)
 cal['status']='11-building-library-calibration-candidates-not-new-streets';write(I/'asset-calibration.json',cal);write(I/'asset-library.json',{'schemaVersion':1,'projection':p,'assets':assets,'newVehicleAssetsIncluded':['V01-v2','V02-v2'],'status':'library-ready-for-plan-fit-check-not-runtime-scene','runtimePNGDirectory':str(A.resolve())});write(I/'provenance-check.json',checks);validate()
def validate():
 lib=read(I/'asset-library.json');images=[]
 for a in lib['assets']:
  f=A/a['file'];assert sha(f)==a['sha256'];size=list(Image.open(f).size);assert max(size)<=280 and size==a['nativeSize'];images.append({'file':a['file'],'bytes':f.stat().st_size,'size':size,'sha256':sha(f)})
 assert len({a['id'] for a in lib['assets']})==len(lib['assets']);assert len(set(x['file'] for x in images))==len(images);assert set(f.name for f in A.glob('*.png'))==set(x['file'] for x in images)
 assert read(I/'inputs-before.json')==protected(),'source SHA changed'
 old={a['id']:a for a in read(OLD/'integration/asset-manifest.json')['assets']}
 for aid in ['B01','T01']:
  a=next(a for a in lib['assets'] if a['id']==aid);assert a['worldSizeUnits']==old[aid]['worldSizeUnits'] and a['anchorUV']==old[aid]['anchorUV']
 buildingtypes=sum(a['id'].startswith('B')for a in lib['assets'])
 write(I/'resource-report.json',{'status':'static-library-validation-only','buildingTypes':buildingtypes,'uniquePNG':len(images),'PNGBytes':sum(a['bytes'] for a in images),'images':images,'protectedFiles':len(protected()),'allProtectedSHAUnchanged':True,'B01T01ScalePreserved':True,'newSceneShown':False,'gameTestsRun':False});print('VALIDATED:',len(images),'unique PNG,',sum(a['bytes'] for a in images),'bytes;',buildingtypes,'building types; source SHA preserved')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['build','validate']);a=p.parse_args();build() if a.command=='build' else validate()
