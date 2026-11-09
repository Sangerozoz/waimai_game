#!/usr/bin/env python3
"""True distinct-module + connected finite courtyard joint fitting, scene ownership only."""
import context as x
import math,itertools
from collections import Counter

def point_along_back(pts,back=2.2):
 a,b=pts[-2:];le=math.dist(a,b);frac=min(.65,back/le);return [b[k]+(a[k]-b[k])*frac for k in (0,1)]
def valid_ground(poly,mods,N):
 q=x.audit(poly,N);bad=x.failures(q,False)
 if any(x.pp(poly,m['footprintPolygonMap'])<.15 for m in mods):bad+=['new-court-or-garden-vs-module']
 return bad,q

def select(idx,options,already=[]):
 N=x.nearset([idx]);counts=Counter();witness={};paircount=0;courtcount=0
 # Favor public/shared-space use plus distinct dwelling/service mass. No same two-roof template mandate.
 pref={'B04':0,'B06':1,'B05':2,'B02':3,'B03':4,'B08':5,'B07':6,'B01':7};options=sorted(options,key=lambda o:(pref[o['assetId']],abs(o['uniformScale']-1)))
 for a,b in itertools.combinations(options,2):
  if a['assetId']==b['assetId']:continue
  paircount+=1
  if paircount>20000:counts['bounded-pair-cap']+=1;break
  mods=[a,b];gap=x.pp(a['footprintPolygonMap'],b['footprintPolygonMap']);bad=[]
  if gap<2:bad+=['peer-body-gap<2']
  if min([x.pp(q,b['footprintPolygonMap']) for q in a['approachPolygonsMap']]+[x.pp(q,a['footprintPolygonMap']) for q in b['approachPolygonsMap']])<.15:bad+=['peer-entry-walk-vs-body']
  if bad:counts.update(bad);continue
  # Shared near-shoulder link may overlap same-scene walks, but must miss every peer/old/source body.
  qa,qb=[point_along_back(m['centrelineMap']) for m in mods];link=x.strip(qa,qb)
  if link is None:counts['degenerate-link']+=1;continue
  bg,lq=valid_ground(link,mods,N)
  if bg:counts.update(['link:'+v for v in bg]);continue
  mid=x.center([qa,qb]);lenu=abs(sum((qa[k]-qb[k])*x.u[k] for k in (0,1)))
  courtlength=min(6,max(3,lenu));best=None
  for ds,dt,w,d in itertools.product([0,-2,2],[0,-1.5,1.5],[courtlength,3],[3,4]):
   courtcount+=1;ctr=x.at(mid,ds,dt);court=x.rect(ctr,w,d);bad,cq=valid_ground(court,mods,N)
   if x.pp(court,link)>1e-7:bad+=['court-does-not-join-link']
   if bad:counts.update(['court:'+v for v in bad]);continue
   for sign in [-1,1]:
    gc=x.at(ctr,0,sign*(d/2+.75));garden=x.rect(gc,min(3,w),1.5);bad,gq=valid_ground(garden,mods,N)
    if any(x.pp(garden,q)<.05 for m in mods for q in m['approachPolygonsMap']) or x.pp(garden,link)<.05:bad+=['garden-covers-door-or-shared-walk']
    if bad:counts.update(['garden:'+v for v in bad]);continue
    grounds=[q for m in mods for q in m['approachPolygonsMap']]+[link,court,garden]
    # Whole candidate must protect previously frozen round2 scene bodies and surfaces.
    peer=[]
    for scene in already:
     obs=[m['footprintPolygonMap'] for m in scene['buildings']]+[s['polygonMap'] for s in scene['groundSurfaces']]
     for m in mods:
      if min(x.pp(m['footprintPolygonMap'],o) for o in obs)<1 or min(x.pp(m['footprintPolygonMap'],b['footprintPolygonMap']) for b in scene['buildings'])<2:peer+=['cross-scene-body-vs-ground-or-body']
     for po in grounds:
      if min(x.pp(po,o) for o in obs)<.15:peer+=['cross-scene-ground-vs-ground-or-body']
    if peer:counts.update(peer);continue
    best={'sourceIndices':[idx],'modules':mods,'extraGrounds':[{'tag':'shared-walk','materialId':'S01-paving','polygonMap':link,'purpose':'finite1.5m side-yard link joins both real door approaches','clearance':lq},{'tag':'shared-court','materialId':'S01-paving','polygonMap':court,'purpose':'bounded shared forecourt, community meeting/turning and pause area','clearance':cq},{'tag':'garden','materialId':'G02-planting','polygonMap':garden,'purpose':'finite planting/soil edge adjoins shared court without covering through walk','clearance':gq}],'bodyGapMetres':gap,'pairAttemptIndex':paircount,'courtTrialIndex':courtcount};break
   if best:break
  if best:
   x.write(f'source-{idx:04d}-joint-audit.json',{'status':'joint-option-found','pairAttempts':paircount,'courtTrials':courtcount,'multiLabelRejectedAttempts':dict(counts),'sameSourceDoesNotExemptPeers':True});return best
 x.write(f'source-{idx:04d}-joint-audit.json',{'status':'no-joint-option-within-budget','pairAttempts':paircount,'courtTrials':courtcount,'multiLabelRejectedAttempts':dict(counts),'sameSourceDoesNotExemptPeers':True});return None
if __name__=='__main__':
 import sys
 i=int(sys.argv[1]);r=select(i,x.read(x.O/f'source-{i:04d}-options.json'));x.write(f'source-{i:04d}-joint.json',r);print(i,'JOINT',None if not r else [m['assetId'] for m in r['modules']])
