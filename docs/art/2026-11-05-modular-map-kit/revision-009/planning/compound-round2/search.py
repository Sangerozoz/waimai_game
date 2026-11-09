#!/usr/bin/env python3
"""Finite local joint trials, no historical failure replay or runtime writes."""
import context as x
import math,itertools,json,time
from collections import Counter
O=x.O
from compact_attempts import compact
sourceQueue=[352,343,339,268,267,589,193]
def attempt(idx,seconds=120):
 startTime=time.monotonic();budgetHit=False
 src=x.c['buildings'][idx];C=x.center(src);N=x.nearset([idx]);A=x.area(src);assert idx not in x.bound|x.reserved
 local=[[sum((v[k]-C[k])*d[k] for k in (0,1)) for d in (x.u,x.n)] for v in src];lo=[min(q[k] for q in local) for k in (0,1)];hi=[max(q[k] for q in local) for k in (0,1)]
 anchors=[x.at(C,s,t) for s in range(math.ceil(lo[0]),math.floor(hi[0])+1,3) for t in range(math.ceil(lo[1]),math.floor(hi[1])+1,3) if x.inside(x.at(C,s,t),src)];anchors=sorted(anchors,key=lambda a:math.dist(a,C))[:48]
 options=[];attempts=Counter();rejections=Counter();witness={};routecounts=Counter();rows=[]
 for aid in ['B04','B06','B05','B02','B03','B08','B07','B01']:
  for sc in ([1] if aid=='B01' else [.9,1,1.1]):
   for anchor in anchors:
    if time.monotonic()-startTime>seconds:budgetHit=True;break
    key=f'{aid}@{sc}';attempts[key]+=1;poly=x.footprint(aid,anchor,sc);q=x.audit(poly,N);bad=x.failures(q,True)
    if sum(x.inside(v,src) for v in poly)<len(poly)/2:bad+=['conservative-carrier-half-corners-support']
    r={'assetId':aid,'uniformScale':sc,'anchorMap':anchor,'bodyClearance':q,'bodyRejectedBy':bad,'routeAttempts':[]};rows.append(r)
    if bad:
     rejections.update(bad)
     for rule in bad:witness.setdefault(rule,r.copy())
     continue
    entry=x.pixelmap(x.doors[aid],anchor,x.cal[aid],sc);start=x.pixelmap([713,626],anchor,x.cal[aid],sc) if aid=='B07' else entry;prefix=[start]+([x.at(anchor,0,7*sc)] if aid=='B07' else []);found=None;acceptedRoutes=[]
    for road,j,a,b in sorted(N['segments'],key=lambda t:math.dist(prefix[-1],x.foot(prefix[-1],t[2],t[3])[0]))[:6]:
     qp,tt=x.foot(prefix[-1],a,b);D=math.dist(prefix[-1],qp)
     if D<road['width']/2+2 or D>65:continue
     if not all(x.inbounds(x.nodes[v],'city') for v in road['nodes'][j:j+2]):continue
     norm=[(qp[k]-prefix[-1][k])/D for k in (0,1)];end=x.add(qp,x.mul(norm,-(road['width']/2+.03)));strategies=[('direct',prefix+[end])]
     for forward in [1.5,3,5]:
      out=x.add(prefix[-1],x.mul(x.n,forward));mid=x.add(out,x.mul(x.u,sum((end[k]-out[k])*x.u[k] for k in (0,1))));strategies+=[(f'side-L-front{forward}',prefix+[out,mid,end]),(f'front-then-diagonal{forward}',prefix+[out,end])]
     for name,pts in strategies:
      routecounts[aid+':'+name]+=1;pts=[v for k,v in enumerate(pts) if k==0 or math.dist(v,pts[k-1])>.001];polys=[x.strip(a,b) for a,b in zip(pts,pts[1:])]+[x.rect(v,1.5,1.5) for v in pts[1:-1]];aq=[];fails=[]
      for po in polys:
       qq=x.audit(po,N);aq.append(qq);fails+=['walk:'+f for f in x.failures(qq,False)]
      if aid=='B07':
       if any(x.pp(po,poly)<.05 for po in polys):fails+=['walk:own-U-entity']
      else:
       le=math.dist(start,pts[1]);cut=x.add(start,x.mul([(pts[1][k]-start[k])/le for k in (0,1)],.6));tail=x.strip(cut,pts[1]);
       if tail is None or x.pp(tail,poly)<.05 or any(x.pp(po,poly)<.05 for po in polys[1:]):fails+=['walk:own-entity-after0.6m']
      r['routeAttempts'].append({'strategy':name,'roadId':road['id'],'nodeRangeInclusive':[j,j+1],'centrelineMap':pts,'clearances':aq,'rejectedBy':sorted(set(fails))})
      if fails:
       rejections.update(set(fails))
       for rule in set(fails):witness.setdefault(rule,{'assetId':aid,'uniformScale':sc,'anchorMap':anchor,'entryPixel':x.doors[aid],'route':r['routeAttempts'][-1]})
       continue
      found={'sourceIndices':[idx],'assetId':aid,'uniformScale':sc,'anchorMap':anchor,'footprintPolygonMap':poly,'entryMap':entry,'entryPixel':x.doors[aid],'walkStartMap':start,'centrelineMap':pts,'approachPolygonsMap':polys,'roadId':road['id'],'roadNodeRangeInclusive':[j,j+1],'routeStrategy':name,'bodyClearance':q,'approachClearances':aq};break
     if found:
      acceptedRoutes.append(found);options.append(found);found=None
      if len(acceptedRoutes)>=3:break
    r['outcome']='accepted-module-option' if acceptedRoutes else 'bounded-door-search-rejected'
    # All accepted alternative source segments retained for joint topology; up to3 per actual body.
 x.write(f'source-{idx:04d}-attempts.json',compact({'sourceIndex':idx,'sourcePolygonMap':src,'areaSquareMetres':A,'centerMap':C,'zone':x.zone(C),'originalSemanticStatus':'unknown','scenicProgramme':'PM-designed mixed shared-court/service/residential scene, subject to actual two-module fit','wallTimeBudgetSeconds':seconds,'wallTimeBudgetReached':budgetHit,'actualElapsedSeconds':time.monotonic()-startTime,'maxAnchorCount':48,'gridStepMetres':3,'testedAnchorCount':len(anchors),'assetScaleAttempts':dict(attempts),'routeStrategyAttempts':dict(routecounts),'multiLabelRejectedAttempts':dict(rejections),'firstWitnessPerRule':witness,'records':rows}))
 x.write(f'source-{idx:04d}-options.json',options);x.assert_protected();print('SOURCE',idx,'options',len(options),'attempts',sum(attempts.values()),flush=True)
 return options
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('source',type=int);p.add_argument('--seconds',type=float,default=120);args=p.parse_args();attempt(args.source,args.seconds)
