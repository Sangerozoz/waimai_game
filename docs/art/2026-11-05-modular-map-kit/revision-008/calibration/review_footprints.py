#!/usr/bin/env python3
"""Read-only native review ->008/calibration only. Manual observations, no registration claim."""
import sys
sys.dont_write_bytecode=True
import json,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;B=O.parents[1];S=B/'revision-006';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old={a['id']:a for a in read(S/'integration/asset-calibration.json')['assets']};projection=read(S/'viewer/assets/scene-layout.json')['projection'];u=[.23417355683909316,-.9721948082958105];n=[.9721948082958105,.23417355683909316]
pu=[u[0]*projection['axisX'][k]+u[1]*projection['axisY'][k]for k in (0,1)];pn=[n[0]*projection['axisX'][k]+n[1]*projection['axisY'][k]for k in (0,1)];det=pu[0]*pn[1]-pn[0]*pu[1]
def local(px,c):
 x,y=[(px[k]-c['anchorPixel'][k])/c['nativePixelsPerUnit']for k in (0,1)];return [(x*pn[1]-y*pn[0])/det,(pu[0]*y-pu[1]*x)/det]
def pixel(q,c):return [c['anchorPixel'][k]+c['nativePixelsPerUnit']*(q[0]*pu[k]+q[1]*pn[k])for k in (0,1)]
def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
C={
'B07':{
 'points':[(1,[155,748],'visible','outer left base'),(2,[409,1125],'visible','left wing front outer foot'),(3,[555,1053],'visible','left wing front inner foot'),(4,[371,781],'inferred','hidden inner-left rear junction'),(5,[759,590],'visible','inner rear/right base junction'),(6,[942,862],'visible','right wing front inner foot'),(7,[1100,784],'visible','right wing front outer foot'),(8,[846,407],'inferred','outer rear closure, hidden'),(9,[480,708],'door','left inner door threshold'),(10,[488,725],'door','left inner step front'),(11,[704,609],'door','right inner door threshold'),(12,[713,626],'door','right inner step front'),(13,[749,958],'void','open courtyard mouth'),(14,[713,680],'void','courtyard clear centre'),(15,[746,825],'rejected','OLD entry: alpha0 courtyard'),(16,[410,889],'roof','wall/parapet junction, NOT ground'),(17,[554,817],'roof','wall/parapet junction, NOT ground')],
 'polygonIDs':[1,2,3,4,5,6,7,8],
 'voidPixels':[[371,781],[759,590],[942,862],[555,1053]],
 'visibleVoidConservativePixels':[[530,739],[741,631],[910,851],[582,1017]],
 'doors':[{'id':'inner-left','threshold':[480,708],'stepFront':[488,725],'approach':'from open courtyard, ground left turn; left-rear corner partly hidden'},{'id':'inner-right-primary-comparison','threshold':[704,609],'stepFront':[713,626],'approach':'from open mouth through courtyard; no invented front-middle door'}],
 'edges':[('left front base cross/frontage',2,3,'frontage',True),('right front base cross/frontage',6,7,'frontage',True),('left exterior base/depth',1,2,'depth',True)],
 'decision':'footprint-door-sufficient-for-small-wide-site-comparison',
 'reason':'visible two wing ends and actual inner doors/steps recover U body and open court; inferred rear must keep buffer; no user/navigation/camera certification',
 'suggestedPlot':[26,24],
 'notes':['OLD entry[746,825] samples alpha0, not a door. Replace in008 review only;006 library unchanged.','Inner-left rear point4 and hidden rear point8 are geometric inferences, not directly observed control points. Reservation includes uncertainty.','Transparent visible court is not a painted ground texture or a navigation surface. Under-wing occluded ground remains inferred.']},
'B09':{
 'points':[(1,[110,640],'visible','left support wing ground'),(2,[224,700],'visible','left wing/foyer junction'),(3,[250,780],'curve','curved foyer ground'),(4,[290,830],'curve','curved foyer ground'),(5,[330,860],'door','main entry step left'),(6,[410,899],'door','main entry step front centre'),(7,[538,923],'door','main entry step right'),(8,[620,919],'curve','curved foyer base'),(9,[700,910],'curve','curved foyer base'),(10,[785,871],'visible','short straight wing base start'),(11,[900,964],'visible','short wing/front corner foot'),(12,[1420,704],'visible','long wing frontage foot end'),(13,[414,875],'door','glazed entry threshold candidate'),(14,[875,603],'roof','upper fascia, NOT ground')],
 'polygonIDs':None,'visibleGroundChainIDs':[1,2,3,4,5,6,7,8,9,10,11,12],
 'doors':[{'id':'curved-foyer-main-step','threshold':[414,875],'stepFront':[410,899],'approach':'from curved stairs; glazing function inferred, visible steps are grounded; reserve full step frontage'}],
 'edges':[('long wing plinth/frontage',11,12,'frontage',True),('SHORT STRAIGHT wing plinth',10,11,'depth',True),('OLD multi-mass outer chord',1,11,'not-an-axis',False)],
 'decision':'hold',
 'reason':'old long chord across curved foyer is not depth evidence; however independent straight short-wing base10-11 is about39deg vs target55.406, a real local axis mismatch remaining after curve separation',
 'suggestedPlot':[34,30],
 'notes':['Rear ground is not visible; do not close with an invented measured rear corner. Only padded reservation rectangle supplied, not a certified physical footprint.','Curved foyer and stair chain is not a straight n axis. Existing22.765x15.819 sprite world frame and PPU remain fixed.','Wider land alone cannot correct straight-wing camera mismatch. Native revision needed before strict fixed-camera admission; no generation requested/performed.']},
'B11':{
 'points':[(1,[99,766],'visible','rear high volume visible short-face foot'),(2,[151,793],'door','rear roller threshold left'),(3,[282,859],'door','rear roller threshold right'),(4,[335,930],'visible','high/middle volume staggered foot'),(5,[389,965],'door','middle roller threshold left'),(6,[535,1048],'door','middle roller threshold right'),(7,[592,1095],'visible','middle short-face corner foot'),(8,[615,1083],'visible','annex return junction'),(9,[740,1155],'visible','annex front foot'),(10,[782,1164],'door','personnel stair front-left'),(11,[890,1112],'door','personnel stair front-right'),(12,[1169,970],'visible','annex long wall ground end'),(13,[808,1107],'door','ACTUAL personnel threshold'),(14,[835,1147],'door','personnel step front centre'),(15,[241,920],'rejected','OLD entry: not actual door threshold'),(16,[638,939.5],'anchor','retained image anchor, NOT a door')],
 'polygonIDs':None,'visibleGroundChainIDs':[1,2,3,4,5,6,7,8,9,10,11,12],
 'doors':[{'id':'rear-short-face-roller','threshold':[216.5,826],'leftRightPoints':[2,3],'approach':'short-face service yard; wide roller opening is not long-front pedestrian door'},{'id':'middle-short-face-roller','threshold':[462,1006.5],'leftRightPoints':[5,6],'approach':'independent short-face service apron; keep opening clear'},{'id':'annex-personnel','threshold':[808,1107],'stepFront':[835,1147],'approach':'actual annex door plus two steps; separate from roller-service apron'}],
 'edges':[('rear roller actual straight threshold',2,3,'depth',True),('middle roller actual straight threshold',5,6,'depth',True),('annex long frontage plinth',9,12,'frontage',True),('OLD whole staggered chord',1,9,'not-an-axis',False)],
 'decision':'hold',
 'reason':'old staggered outer chord is not depth; real straight roller threshold pairs independently remain about27-30deg instead of55.406. Short-face camera mismatch cannot be fixed by shifting door or larger land',
 'suggestedPlot':[30,28],
 'notes':['Two roller doors are on the actual visible short-facing mass ends; the personnel door is at point13 on annex, not old[241,920].','Original invisible back is not reconstructed. Padded reservation is a planning envelope only, not an invented surveyed closed footprint.','Keep nativePPU66.41010956365606 and full sprite aspect ratio. Native short-face correction needed for strict fixed-camera admission; no warp/repaint performed.']}}
review={'status':'manual-native-footprint-review-no-runtime-or-user-acceptance','projection':projection,'localAxes':{'T':u,'N':n,'originMeaning':'retained per-asset anchor maps to local[0,0]'},'assets':[]}
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',21);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
col={'visible':'#167a3c','curve':'#a86a09','door':'#e34a05','void':'#007f99','inferred':'#b11a9c','roof':'#375bb5','rejected':'#cc1010','anchor':'#55616b'}
for aid,s in C.items():
 c=old[aid];raw=S/f'native/{aid}-001/{aid}-v1.png';der=read(S/f'native/{aid}-001/{aid}-runtime-280.runtime.json');prov=read(S/f'native/{aid}-001/provenance.json');src=Path(prov['toolSourceAbsolutePath']);assert sha(raw)==sha(src)==der['sourceSHA256'];assert c['sourceNativeSHA256']==sha(raw);image=Image.open(raw).convert('RGBA');points=[];pt={idx:xy for idx,xy,kind,name in s['points']}
 for idx,xy,kind,name in s['points']:
  tn=local(xy,c);back=pixel(tn,c);assert math.dist(back,xy)<1e-9;cropUV=[(xy[k]-der['cropBox'][k])/(der['cropBox'][k+2]-der['cropBox'][k])for k in (0,1)];rpx=[cropUV[k]*der['runtimeSize'][k]for k in (0,1)];points.append({'id':idx,'nativePixel':xy,'classification':kind,'description':name,'localTN':tn,'cropUV':cropUV,'runtimePixelApprox':rpx,'alphaAtPixel':image.getpixel(tuple(round(v)for v in xy))[3],'pixelRoundtripError':math.dist(back,xy),'uncertaintyPx':8 if kind in ['visible','door']else 25 if kind=='curve'else None,'usableAsObservedGroundControl':kind in ['visible','door','curve'],'uncertaintyNote':'not measurable hidden ground; planning reservation only' if kind=='inferred' else 'manual visual point, not surveyed'})
 edges=[]
 for name,a,b,axis,reliable in s['edges']:
  p,q=pt[a],pt[b];angle=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]));target=-28.486362688849802 if axis=='frontage'else 55.40598449120886 if axis=='depth'else None
  if target is not None:
   while angle-target>90:angle-=180
   while angle-target<-90:angle+=180
  intervals=[]
  if target is not None:
   for ax in [-8,8]:
    for ay in [-8,8]:
     for bx in [-8,8]:
      for by in [-8,8]:
       v=math.degrees(math.atan2(q[1]+by-p[1]-ay,q[0]+bx-p[0]-ax))
       while v-target>90:v-=180
       while v-target<-90:v+=180
       intervals.append(v)
  edges.append({'manualEndpoint8pxAngleRangeDeg':[min(intervals),max(intervals)] if intervals else None,'description':name,'pointIds':[a,b],'measuredScreenAngleDegManual':angle,'targetDeg':target,'differenceDeg':angle-target if target is not None else None,'validAxisEvidence':reliable,'precision':'manual endpoint +/-8px; not exact surveying'})
 # Never change prior scale; preserve source crop-to-world transform.
 x,y,x2,y2=der['cropBox'];ppu=c['nativePixelsPerUnit'];uv=[(c['anchorPixel'][0]-x)/(x2-x),(c['anchorPixel'][1]-y)/(y2-y)];world=[(x2-x)/ppu,(y2-y)/ppu];assert uv==c['anchorUV'] and world==c['worldSizeUnits']
 chain=[pt[j]for j in (s.get('visibleGroundChainIDs')or s['polygonIDs'])];tn=[local(p,c)for p in chain];margin=2 if aid=='B07'else 4;lo=[min(p[k]for p in tn)-margin for k in (0,1)];hi=[max(p[k]for p in tn)+margin for k in (0,1)];reserve=[[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]]
 item={'id':aid,'decision':s['decision'],'reason':s['reason'],'nativePath':str(raw.resolve()),'nativeSHA256':sha(raw),'actualToolSourcePath':str(src),'toolSourceSHA256':sha(src),'nativeSize':list(image.size),'cropBox':der['cropBox'],'runtimeSize':der['runtimeSize'],'runtimeSHA256':der['sha256'],'nativePixelsPerUnit':ppu,'anchorPixel':c['anchorPixel'],'anchorUV':uv,'candidateWorldSizeUnits':world,'positiveUniformOnly':True,'scaleChangedFrom006':False,'points':points,'straightEdgeReview':edges,'visibleGroundChainNativePixels':chain,'visibleGroundChainLocalTN':tn,'conservativeOccupiedPolygonLocalTN':[local(p,c)for p in chain]if aid=='B07'else None,'rearClosure':'points4/8 inferred with explicit2m reservation margin'if aid=='B07'else'not recovered; no invented measured rear closure; use padded rectangular planning reservation and remain hold','conservativeReservationPolygonLocalTN':reserve,'conservativeOccupiedReservationPolygonLocalTN':reserve,'reservationIsConfirmedPhysicalFootprint':False,'reservationMarginUnits':margin,'reservationMeaning':'candidate placement exclusion envelope, NOT surveyed building footprint or guaranteed bound on unseen rear','reservationSpanUnits':[hi[k]-lo[k]for k in (0,1)],'visibleDoors':[dict(d,thresholdLocalTN=local(d['threshold'],c),stepFrontLocalTN=local(d['stepFront'],c)if d.get('stepFront')else None)for d in s['doors']],'suggestedPlotFrontageDepthCandidate':s['suggestedPlot'],'plotPolicy':'suggestedPlot or reservationSpan+2m each side, whichever larger; add declared entry/service apron; must recheck source geometry','notes':s['notes'],'footprintReliability':'medium-visible-ground-plus-declared-U-rear-inferences' if aid=='B07' else 'visible-front-chain-only; hidden rear unclosed; hold','requiresNewNativeForStrictFixedCamera':aid in ['B09','B11']}
 if aid=='B07':
  item['courtyardVoidLocalTN']=[local(p,c)for p in s['voidPixels']];item['visiblyClearConservativeVoidLocalTN']=[local(p,c)for p in s['visibleVoidConservativePixels']];pathpx=[[740,920],[713,680],[713,660]];path=[local(p,c)for p in pathpx];test=[]
  for a,b in zip(path,path[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dy);nx,ny=-dy/le*.75,dx/le*.75;poly=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]];test.append({'polygonLocalTN':poly,'allCornersWithinInferredCourtyardVoid':all(inside(p,item['courtyardVoidLocalTN'])for p in poly)})
  item['courtyardApproach']={'widthCandidate':1.5,'centrelinePixel':pathpx,'centrelineLocalTN':path,'mouthAccessPixel':[[749,980],[740,920]],'lastStepApproachPixel':[[713,660],[713,626]],'corridorChecks':test,'status':'static-inferred-void-small-comparison-only; final doorstep and levels unknown; not navigation'};item['courtyardMouthWidthUnits']=math.dist(local(pt[3],c),local(pt[6],c));item['wallHeightRecheck']={'old320pxEstimateImpliedHeight':320/ppu/abs(projection['axisZ'][1]),'newVisibleVerticalPairs':[[16,2],[17,3]],'verticalSpansPx':[pt[2][1]-pt[16][1],pt[3][1]-pt[17][1]],'candidateEaveHeights':[(pt[2][1]-pt[16][1])/ppu/abs(projection['axisZ'][1]),(pt[3][1]-pt[17][1])/ppu/abs(projection['axisZ'][1])],'correction':'old16m came from unpinned320px estimate; actual numbered same-x wall-foot/parapet pairs about236px. Source/PPU/world frame unchanged; NOT anisotropically compressed to10m. Roof equipment excluded.'}
 review['assets'].append(item)
 # Numbered overlays on native-scale copy, no source pixel modification.
 bg=Image.new('RGBA',image.size,'#c4cccc');bg.alpha_composite(image);out=Image.new('RGB',(image.width+660,max(image.height,1100)),'#f3f5f4');out.paste(bg.convert('RGB'),(0,0));d=ImageDraw.Draw(out)
 if aid=='B07':
  kinds={idx:kind for idx,xy,kind,name in s['points']}
  for j in range(len(chain)):
   a,b=chain[j],chain[(j+1)%len(chain)];ia=s['polygonIDs'][j];ib=s['polygonIDs'][(j+1)%len(chain)]
   if 'inferred' in [kinds[ia],kinds[ib]]:
    le=math.dist(a,b)
    for k in range(0,int(le),16):
     f0=k/le;f1=min((k+9)/le,1);d.line([(a[0]+f0*(b[0]-a[0]),a[1]+f0*(b[1]-a[1])),(a[0]+f1*(b[0]-a[0]),a[1]+f1*(b[1]-a[1]))],fill='#b11a9c',width=4)
   else:d.line([a,b],fill='#167a3c',width=4)
  d.line(s['voidPixels']+[s['voidPixels'][0]],fill='#007f99',width=3)
 else:d.line(chain,fill='#a86a09',width=4)
 for ed in edges:
  if ed['validAxisEvidence']:d.line([pt[j]for j in ed['pointIds']],fill='#cc2020'if abs(ed['differenceDeg']or 0)>8 else'#24723d',width=6)
 for idx,xy,kind,name in s['points']:
  x,y=xy;co=col[kind];d.ellipse((x-7,y-7,x+7,y+7),fill=co,outline='white',width=2);d.text((x+10,y-16),f'{idx:02}',font=font,fill=co,stroke_width=2,stroke_fill='white')
 x=image.width+18;d.text((x,18),aid+' NATIVE PIXEL REVIEW',font=font,fill='black');d.text((x,53),'Native image pixels retained; overlay copy only',font=small,fill='#333333');y=90
 for idx,xy,kind,name in s['points']:
  d.text((x,y),f'{idx:02} {str(xy):18} {kind}',font=small,fill=col[kind]);d.text((x,y+21),name,font=small,fill='#242a2a');y+=48
 d.text((x,y+10),'GREEN visible base / ORANGE door / MAGENTA inferred',font=small,fill='black');d.text((x,y+35),'BLUE wall-top only / RED rejected or axis conflict',font=small,fill='black');out.save(O/f'annotated-{aid}.jpg',quality=95)
write(O/'footprint-review.json',review);before=read(O/'source-protection-before.json');assert all(sha(p)==h for p,h in before.items());layout=read(S/'viewer/assets/scene-layout.json');assert len(layout['blocks'])==43 and len(layout['groundSurfaces'])==85;write(O/'source-protection-result.json',{'protectedFiles':len(before),'allSHAUnchanged':True,'sourceSnapshotSHA256':sha(O/'source-protection-before.json'),'existing006StaticInstances':43,'existing006GroundSurfaces':85,'gameTestsRun':False,'coordinateChecks':'manual native -> localTN -> native roundtrip for all points; cropUV/runtime transforms; priorPPU/anchor/world frame unchanged','maxPixelRoundtripError':max(p['pixelRoundtripError']for a in review['assets']for p in a['points'])});print([(a['id'],a['decision'],a['reservationSpanUnits'])for a in review['assets']]);print('review SHA',sha(O/'footprint-review.json'))
