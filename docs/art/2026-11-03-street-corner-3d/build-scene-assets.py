#!/usr/bin/env python3
"""Deterministic, standard-library 3-D street-corner asset authoring.

No renderer, game process, network, source-map writes, or save-state access.
All authoring dimensions are metres. Output uses Cocos X/Y/Z, Y up.
"""
import hashlib
import json
import math
from pathlib import Path
import random
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'delivery-game/assets/resources/map-sample/city.json'
REFERENCE = ROOT / 'docs/art/2026-11-03-sample-fidelity-rework/user-target-v2-concept.png'
ORIGIN = (-1580.0, 75.0)
BOUNDS = (-1608.0, 39.0, -1552.0, 108.0)
BUILDINGS = [144, 145, 143]
SEED = 20261103
rng = random.Random(SEED)
city = json.loads(SOURCE.read_text())
nodes = {n['id']: n for n in city['nodes']}
objects = []
authored = Counter()
batches = defaultdict(lambda: {'vertices': [], 'indices': [], 'normals': []})
source_roads = []

M = {
 'ivory': ('#eee9dc', .78), 'chalk': ('#fff5e5', .75),
 'sand': ('#ead3a2', .8), 'terracotta': ('#ddba84', .82),
 'roof': ('#b7b9ae', .92), 'roofSeam': ('#929a97', .9),
 'frame': ('#344e52', .58), 'reveal': ('#647978', .85),
 'glass': ('#789b9d', .3), 'glassLight': ('#a0bcb8', .24),
 'glassShade': ('#587b82', .38), 'reflection': ('#c4d8cd', .25),
 'skyMid': ('#a4c1bc', .30), 'glint': ('#e8ebd5', .22),
 'warm': ('#e9bf74', .65), 'warmShade': ('#b68d59', .8),
 'orange': ('#f58b20', .68), 'orangeDark': ('#d95c15', .75),
 'stripe': ('#fff0cb', .7), 'wood': ('#a66c3f', .85),
 'woodLight': ('#c2925d', .78), 'metal': ('#38484a', .55),
 'metalLight': ('#b5c2be', .58), 'asphalt': ('#6b7679', .97),
 'roadWear': ('#7e8788', .94), 'marking': ('#f3eedb', .91),
 'paving': ('#e4d7c2', .94), 'pavingAlt': ('#d8cebd', .94),
 'pavingLine': ('#bfb7a5', .96), 'curb': ('#f2e6d2', .9),
 'soil': ('#766442', .98), 'grass': ('#7d9440', .95),
 'leafDark': ('#557b2f', .96), 'leafMid': ('#81a83d', .94),
 'leafLight': ('#a2c847', .94), 'leafSun': ('#c5db5d', .94),
 'bark': ('#8b6849', .98), 'barkLight': ('#b28b58', .95),
 'rubber': ('#2c3333', .93), 'carBody': ('#e8ece5', .42),
 'carWindow': ('#304e5a', .3), 'red': ('#bd4940', .67),
 'skin': ('#e4b38b', .85), 'fabric': ('#344b59', .94),
 'lamp': ('#ffedc2', .6), 'umbrella': ('#fff1d5', .85),
}

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,t): return tuple(x*t for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def length(a): return math.sqrt(dot(a,a))
def norm(a):
 l=length(a)
 return mul(a,1/l) if l>1e-10 else (0,1,0)
def local(p,h=0): return (p[0]-ORIGIN[0], h, -(p[1]-ORIGIN[1]))
def area(p): return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2
def ccw(p):
 p=list(p[:-1] if p[0]==p[-1] else p)
 return p if area(p)>0 else list(reversed(p))
def inset(p,d):
 """Intersection of inward offset edge lines; retains source corners/concavity."""
 out=[]
 for i,b in enumerate(p):
  a=p[i-1];c=p[(i+1)%len(p)]
  u=norm((b[0]-a[0],b[1]-a[1]));v=norm((c[0]-b[0],c[1]-b[1]))
  n=(-u[1],u[0]);m=(-v[1],v[0]);den=u[0]*v[1]-u[1]*v[0]
  if abs(den)<1e-7: out.append((b[0]+n[0]*d,b[1]+n[1]*d));continue
  q=(b[0]+n[0]*d,b[1]+n[1]*d);r=(b[0]+m[0]*d,b[1]+m[1]*d)
  t=((r[0]-q[0])*v[1]-(r[1]-q[1])*v[0])/den
  out.append((q[0]+u[0]*t,q[1]+u[1]*t))
 return out
def triangulate(p):
 remaining=list(range(len(p)));out=[]
 def orient(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 while len(remaining)>3:
  found=False
  for j,i in enumerate(remaining):
   a,b,c=remaining[j-1],i,remaining[(j+1)%len(remaining)]
   if orient(p[a],p[b],p[c])<=1e-8: continue
   if any(all(orient(p[u],p[v],p[k])>=-1e-8 for u,v in [(a,b),(b,c),(c,a)]) for k in remaining if k not in (a,b,c)):continue
   out.append((a,b,c));remaining.pop(j);found=True;break
  if not found: raise ValueError('Cannot triangulate non-simple footprint')
 out.append(tuple(remaining));return out

def mesh(group,part,material,verts,faces,vertex_normals=None):
 """Hard architectural faces; optional smooth normals for organic forms."""
 authored[group]+=1
 dst=batches[(group,material)]
 for f in faces:
  a,b,c=(verts[k] for k in f);n=norm(cross(sub(b,a),sub(c,a)))
  if length(cross(sub(b,a),sub(c,a)))<1e-9: continue
  start=len(dst['vertices'])//3
  for index,v in zip(f,(a,b,c)):
   dst['vertices'].extend(round(q,5) for q in v)
   dst['normals'].extend(round(q,6) for q in (vertex_normals[index] if vertex_normals else n))
  dst['indices'].extend([start,start+1,start+2])

def box(group,part,mat,c,size,angle=0):
 x,y,z=(s/2 for s in size);a=math.radians(angle);co,si=math.cos(a),math.sin(a)
 v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 v=[(c[0]+q[0]*co+q[2]*si,c[1]+q[1],c[2]-q[0]*si+q[2]*co) for q in v]
 f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(3,7,6),(3,6,2),(0,4,7),(0,7,3),(1,2,6),(1,6,5)]
 mesh(group,part,mat,v,f)

def cylinder(group,part,mat,a,b,r,rt=None,segments=10):
 rt=r if rt is None else rt;axis=norm(sub(b,a));ref=(0,1,0) if abs(axis[1])<.95 else (1,0,0)
 u=norm(cross(axis,ref));v=cross(axis,u);vs=[]
 for c,rad in [(a,r),(b,rt)]:
  for i in range(segments):
   t=i*math.tau/segments;vs.append(add(c,add(mul(u,math.cos(t)*rad),mul(v,math.sin(t)*rad))))
 vs += [a,b];fs=[]
 for i in range(segments):
  j=(i+1)%segments
  fs.extend([(i,j,j+segments),(i,j+segments,i+segments),(2*segments,j,i),(2*segments+1,i+segments,j+segments)])
 mesh(group,part,mat,vs,fs)

def ellipsoid(group,part,mat,c,r,scale=(1,1,1),rings=5,segs=8,irregular=0):
 vs=[]
 for j in range(rings+1):
  ph=math.pi*j/rings
  for i in range(segs):
   th=math.tau*i/segs;rr=r*(1+(rng.uniform(-irregular,irregular) if j not in (0,rings) else 0))
   vs.append((c[0]+rr*math.sin(ph)*math.cos(th)*scale[0],c[1]+rr*math.cos(ph)*scale[1],c[2]+rr*math.sin(ph)*math.sin(th)*scale[2]))
 fs=[]
 for j in range(rings):
  for i in range(segs):
   ni=(i+1)%segs;a=j*segs+i;b=j*segs+ni;c1=(j+1)*segs+i;d=(j+1)*segs+ni
   fs.extend([(a,b,c1),(b,d,c1)])
 smooth=[norm(tuple((p[k]-c[k])/(scale[k]**2) for k in range(3))) for p in vs]
 mesh(group,part,mat,vs,fs,smooth)

def prism(group,part,mat,p,h0,h1):
 p=ccw(p);v=[local(q,h0) for q in p]+[local(q,h1) for q in p];n=len(p);f=[]
 for a,b,c in triangulate(p): f.extend([(a,c,b),(a+n,b+n,c+n)])
 for i in range(n):
  j=(i+1)%n;f.extend([(i,j,j+n),(i,j+n,i+n)])
 mesh(group,part,mat,v,f)

def edgebox(group,part,mat,a,b,y,height,depth,offset=0):
 # p is CCW in map. Right normal is exterior; maps to local X/Z.
 dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);nx,ny=dy/l,-dx/l
 p=((a[0]+b[0])/2+nx*offset,(a[1]+b[1])/2+ny*offset)
 box(group,part,mat,local(p,y),(l,height,depth),math.degrees(math.atan2(dy,dx)))

def edgepoint(a,b,t,out=0,y=0):
 dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
 return local((a[0]+dx*t+dy/l*out,a[1]+dy*t-dx/l*out),y)

def parapet(group,p,y):
 for a,b in zip(p,p[1:]+p[:1]):
  edgebox(group,'parapet wall','chalk',a,b,y+.49,.98,.24,-.10)
  edgebox(group,'parapet coping','ivory',a,b,y+1.02,.12,.38,-.10)
  edgebox(group,'dark coping underside','reveal',a,b,y+.93,.06,.29,-.10)

def roof_equipment(group,p,y):
 cx=sum(q[0] for q in p)/len(p);cy=sum(q[1] for q in p)/len(p)
 # Distinct clustered service equipment, no vegetation on roofs.
 for k,(dx,dz,s) in enumerate([(-1.2,.8,1),(1.1,1,.65)]):
  c=local((cx+dx,cy+dz),y+.55*s)
  box(group,'HVAC plinth','reveal',(c[0],y+.15,c[2]),(2.05*s,.3,1.25*s))
  box(group,'HVAC housing','metalLight',c,(1.9*s,.9*s,1.12*s))
  for j in range(7):box(group,'HVAC grille','frame',(c[0]-.65*s+j*.21*s,c[1],c[2]+.567*s),(.075*s,.62*s,.035))
  cylinder(group,'fan rim','frame',(c[0],y+1.01*s,c[2]),(c[0],y+1.04*s,c[2]),.37*s,segments=20)
  for j in range(4):box(group,'fan grille','metalLight',(c[0]-.24*s+j*.16*s,y+1.05*s,c[2]),(.032,.03,.58*s))
 for dx in [-2.0,2.0]:
  c=local((cx+dx,cy-1),y)
  cylinder(group,'vent duct','metalLight',add(c,(0,.05,0)),add(c,(0,.85,0)),.13,segments=10)
  cylinder(group,'vent cap','chalk',add(c,(0,.83,0)),add(c,(0,.9,0)),.23,segments=10)
 # Separate stair-overrun with door, soffit and a true perimeter.
 c=local((cx,cy-1.4),y+1.12)
 box(group,'stair overrun','ivory',c,(2.1,2.24,2.2))
 box(group,'overrun cap','chalk',add(c,(0,1.18,0)),(2.32,.18,2.42))
 box(group,'roof access door','reveal',add(c,(0,-.19,1.11)),(.82,1.84,.05))
 box(group,'door glazing','glassShade',add(c,(0,.25,1.145)),(.55,.65,.035))

def glass_patch(group,part,mat,a,b,lo,hi,points,out):
 # Local points run across this pane and up it. All reflection/interior paint
 # surfaces sit beyond the opaque pane's outer face (.1195 m), below mullions.
 verts=[edgepoint(a,b,u,out,lo+v*(hi-lo)) for u,v in points]
 mesh(group,part,mat,verts,[(0,k,k+1) for k in range(1,len(verts)-1)])

def glazing(group,a,b,lo,hi,style,bay):
 l=math.dist(a,b)
 if l<2.5: return
 pad=.42 if style!='modern' else .28
 n=max(1,round((l-2*pad)/bay));w=(l-2*pad)/n
 # Broad dark recess is bounded by deep reveals, thick piers and sills.
 aa=(a[0]+(b[0]-a[0])*pad/l,a[1]+(b[1]-a[1])*pad/l)
 bb=(b[0]-(b[0]-a[0])*pad/l,b[1]-(b[1]-a[1])*pad/l)
 edgebox(group,'deep shadow recess','frame',aa,bb,(lo+hi)/2,hi-lo,.10,.025)
 for j in range(n):
  t0=(pad+j*w+.095)/l;t1=(pad+(j+1)*w-.095)/l
  q0=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0)
  q1=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
  m=['glass','glassLight','glassShade'][(j+(0 if style=='modern' else 1))%3]
  edgebox(group,'large glazing panel',m,q0,q1,(lo+hi)/2,hi-lo-.2,.055,.092)
  # Broad two-tone sky shape plus a restrained diagonal glint. These are
  # outward geometry surfaces, not reflective PBR claims or blue wall tint.
  h=hi-lo
  glass_patch(group,'soft sky reflection lower','skyMid',q0,q1,lo,hi,
   [(0,.57),(1,.68),(1,.94),(0,.94)],.146)
  glass_patch(group,'bright sky reflection upper','reflection',q0,q1,lo,hi,
   [(0,.79),(1,.85),(1,.965),(0,.965)],.154)
  if j%3!=1:
   glass_patch(group,'slant narrow reflected light','glint',q0,q1,lo,hi,
    [(.05,.33),(.14,.33),(.74,.86),(.65,.86)],.169)
   glass_patch(group,'slant faint secondary reflection','reflection',q0,q1,lo,hi,
    [(.22,.30),(.25,.30),(.84,.83),(.81,.83)],.171)
  if (j%3!=1 and lo<5) or (j%4==0 and style!='modern'):
   # Side-lit partial interior and a lighter inset produce depth rather than
   # a uniform ochre strip across every ground-floor window.
   glass_patch(group,'warm interior depth','warmShade',q0,q1,lo,hi,
    [(.12,.06),(.58,.06),(.58,.47),(.12,.55)],.151)
   glass_patch(group,'lit interior wall','warm',q0,q1,lo,hi,
    [(.17,.08),(.49,.08),(.49,.43),(.17,.49)],.160)
   mid=(t0+t1)/2;light=edgepoint(a,b,mid,.182,lo+min(.9,h*.3))
   cylinder(group,'interior pendant glow','warm',add(light,(0,.5,0)),add(light,(0,.68,0)),.13,.20,10)
   edgebox(group,'interior counter','wood',q0,q1,lo+.43,.09,.09,.21)
  # Paired real casement mullions, not tiny texture windows.
  for t in [t0,t1]:
   c=edgepoint(a,b,t,.19,(lo+hi)/2)
   box(group,'projecting window mullion','frame',c,(.10,hi-lo,.17),math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])))
  if w>2.4:
   c=edgepoint(a,b,(t0+t1)/2,.19,(lo+hi)/2)
   box(group,'slender glass subdivision','metalLight',c,(.045,hi-lo,.085),math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])))
 for y,h in [(lo-.10,.22),(hi+.08,.18)]:
  edgebox(group,'thick window surround','chalk',aa,bb,y,h,.40,.16)

def canopy(group,a,b,width_fraction=.78):
 l=math.dist(a,b)
 if l<4: return
 t0=(1-width_fraction)/2;t1=1-t0
 # Sloped fabric mesh with solid valance, edge piping, and physical brackets.
 vs=[edgepoint(a,b,t0,.15,3.60),edgepoint(a,b,t1,.15,3.60),edgepoint(a,b,t1,1.65,3.0),edgepoint(a,b,t0,1.65,3.0)]
 mesh(group,'sloped orange awning','orange',vs,[(0,2,1),(0,3,2),(0,1,2),(0,2,3)])
 front0,front1=vs[3],vs[2]
 cylinder(group,'front awning piping','stripe',front0,front1,.035,segments=8)
 cylinder(group,'wall awning rail','orangeDark',vs[0],vs[1],.055,segments=8)
 for t in [t0,t0+(t1-t0)*.5,t1]:
  p=edgepoint(a,b,t,.18,2.53);q=edgepoint(a,b,t,1.61,2.99)
  cylinder(group,'diagonal canopy support','metal',p,q,.045,segments=8)
  cylinder(group,'awning seams','stripe',edgepoint(a,b,t,.17,3.61),edgepoint(a,b,t,1.66,3.01),.022,segments=6)
 # Valance dimensions follows the front, positioned through map outward normal.
 aa=(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0)
 bb=(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)
 edgebox(group,'orange valance','orangeDark',aa,bb,2.88,.26,.08,1.65)

def building(index,style,height,levels):
 group=f'building-{index}-{style}';p=ccw(city['buildings'][index]);bodymat={'restaurant':'sand','modern':'ivory','residential':'terracotta'}[style]
 prism(group,'exact original footprint shell',bodymat,p,.18,height)
 # Roof is an actual concave horizontal surface, inset parapet walkway.
 prism(group,'concrete roof deck','roof',inset(p,.22),height,height+.06)
 parapet(group,p,height)
 # Restaurant gets equipment on its upper terrace below; don't bury a second
 # complete HVAC/access-room assembly inside the setback penthouse.
 if style!='restaurant':roof_equipment(group,p,height+.08)
 edges=list(zip(p,p[1:]+p[:1]))
 for ei,(a,b) in enumerate(edges):
  l=math.dist(a,b);dx,dy=b[0]-a[0],b[1]-a[1];out=(dy/l,-dx/l)
  street=out[0]<-.25 or out[1]>.45
  edgebox(group,'stone foundation','reveal',a,b,.31,.27,.28,.04)
  edgebox(group,'ground floor cornice','chalk',a,b,4.18,.32,.48,.12)
  if l<2.7:
   edgebox(group,'irregular corner pier','chalk',a,b,height/2,height,.20,.05);continue
  # Main edges glass, secondary edges controlled by larger individual bays.
  glazing(group,a,b,.48,3.85,style,3.0 if street else 3.5)
  if style=='restaurant':
   glazing(group,a,b,4.55,7.25,style,3.4)
   glazing(group,a,b,7.75,10.30,style,3.4)
   edgebox(group,'second floor fine cornice','ivory',a,b,7.48,.24,.36,.09)
   if street: canopy(group,a,b)
  elif style=='modern':
   # Tall continuous two-storey glazing field, very slim horizontal transoms.
   glazing(group,a,b,4.6,height-.56,style,2.5)
   for y in [7.65,10.9,14.15]:edgebox(group,'curtain wall transom','frame',a,b,y,.11,.20,.20)
   for t in [.04,.96]:
    box(group,'full height white fin','chalk',edgepoint(a,b,t,.32,(height+4.5)/2),(.30,height-4.5,.64),math.degrees(math.atan2(dy,dx)))
  else:
   for f in range(1,levels):
    lo=4.5+(f-1)*3.15
    glazing(group,a,b,lo,lo+2.32,style,4.6)
    edgebox(group,'projecting floor slab','ivory',a,b,lo+2.66,.24,.57,.12)
   if street and ei%2==0:
    # Real shallow upper balconies with solid base and thin guard rail.
    for y in [7.3,10.45]:
     aa=(a[0]+dx*.15,a[1]+dy*.15);bb=(a[0]+dx*.80,a[1]+dy*.80)
     edgebox(group,'balcony slab','chalk',aa,bb,y,.20,1.0,.45)
     edgebox(group,'balcony handrail','metal',aa,bb,y+1.0,.055,.07,.92)
     for t in [.16,.32,.48,.64,.79]:
      q=edgepoint(a,b,t,.92,y+.52);cylinder(group,'balcony baluster','metal',add(q,(0,-.43,0)),add(q,(0,.43,0)),.025,segments=6)
  # Thick external corner piers create a visible facade depth hierarchy.
  for t in [0,1]:
   box(group,'corner pier','chalk',edgepoint(a,b,t,.09,height/2),(.36,height,.40),math.degrees(math.atan2(dy,dx)))
  if street:
   # Ground door leaf, transom and warm entry threshold, integral to glazing.
   t=.50 if style!='restaurant' else .72;c=edgepoint(a,b,t,.26,1.52)
   box(group,'entrance door frame','frame',c,(1.16,2.75,.17),math.degrees(math.atan2(dy,dx)))
   box(group,'entrance door glass','glassShade',add(c,(0,0,.0)),(.96,2.54,.20),math.degrees(math.atan2(dy,dx)))
   h=edgepoint(a,b,t-.026,.40,1.46);cylinder(group,'door pull','metalLight',add(h,(0,-.27,0)),add(h,(0,.27,0)),.025,segments=8)
   aa=(a[0]+dx*(t-.07),a[1]+dy*(t-.07));bb=(a[0]+dx*(t+.07),a[1]+dy*(t+.07))
   edgebox(group,'entry step','chalk',aa,bb,.16,.15,.78,.40)
 # Set-back upper terrace volumes are smaller than original ground footprint.
 if style=='restaurant':
  top=inset(p,1.20)
  prism(group,'setback rooftop penthouse','ivory',top,height+.07,height+1.28)
  prism(group,'penthouse roof','chalk',inset(top,-.12),height+1.28,height+1.40)
  # Keep roof equipment on upper terrace, not buried inside setback volume.
  roof_equipment(group+'-upper-roof',top,height+1.43)

def clip_segment(a,b,bounds):
 xmin,ymin,xmax,ymax=bounds;t0,t1=0.,1.;dx=b[0]-a[0];dy=b[1]-a[1]
 for p,q in [(-dx,a[0]-xmin),(dx,xmax-a[0]),(-dy,a[1]-ymin),(dy,ymax-a[1])]:
  if abs(p)<1e-9:
   if q<0:return None
  elif p<0:t0=max(t0,q/p)
  else:t1=min(t1,q/p)
 if t0>t1:return None
 return ((a[0]+t0*dx,a[1]+t0*dy),(a[0]+t1*dx,a[1]+t1*dy))

road_segments=[]
for road in city['roads']:
 retained=[]
 for ia,ib in zip(road['nodes'],road['nodes'][1:]):
  aa,bb=nodes[ia],nodes[ib];a=(aa['x'],aa['y']);b=(bb['x'],bb['y']);seg=clip_segment(a,b,BOUNDS)
  if seg and math.dist(*seg)>.02:
   retained.append({'fromNode':ia,'toNode':ib,'sourceEndpoints':[list(a),list(b)],'visibleEndpoints':[list(seg[0]),list(seg[1])]})
   road_segments.append((road,seg[0],seg[1]))
 if retained:source_roads.append({'id':road['id'],'width':road['width'],'kind':road['kind'],'direction':road['direction'],'segments':retained})

def road_distance(p):
 best=1e6
 for r,a,b in road_segments:
  d=sub(b,a);t=max(0,min(1,dot(sub(p,a),d)/dot(d,d)));q=add(a,mul(d,t));best=min(best,math.dist(p,q)-r['width']/2)
 return best
def inside(p,poly):
 c=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c
primary_polys=[ccw(city['buildings'][i]) for i in BUILDINGS]
def on_building(p): return any(inside(p,poly) for poly in primary_polys)

# Cut sidewalk/curb geometry out of the actual branch mouths, rather than
# hiding intersecting raised strips under an equally raised asphalt disc.
JUNCTIONS=[('1623821577',5.15),('9634601487',4.6)]
def split_halfplane(poly,a,b):
 def distance(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 positive=[];negative=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=distance(p),distance(q)
  (positive if dp>=0 else negative).append(p)
  if (dp>0 and dq<0) or (dp<0 and dq>0):
   t=dp/(dp-dq);r=(p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1]))
   positive.append(r);negative.append(r)
 return positive,negative
def subtract_junctions(poly):
 pieces=[poly]
 for node_id,radius in JUNCTIONS:
  n=nodes[node_id]
  ring=[(n['x']+math.cos(k*math.tau/24)*radius,n['y']+math.sin(k*math.tau/24)*radius) for k in range(24)]
  result=[]
  for piece in pieces:
   pending=piece
   for a,b in zip(ring,ring[1:]+ring[:1]):
    if len(pending)<3:break
    pending,outside=split_halfplane(pending,a,b)
    if len(outside)>=3 and abs(area(outside))>1e-7:result.append(outside)
  pieces=result
 return pieces
def street_strip(group,part,mat,a,b,y,height,depth,offset=0):
 dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);nx,ny=dy/l,-dx/l
 p=[(a[0]+nx*(offset-depth/2),a[1]+ny*(offset-depth/2)),
    (b[0]+nx*(offset-depth/2),b[1]+ny*(offset-depth/2)),
    (b[0]+nx*(offset+depth/2),b[1]+ny*(offset+depth/2)),
    (a[0]+nx*(offset+depth/2),a[1]+ny*(offset+depth/2))]
 for piece in subtract_junctions(ccw(p)):prism(group,part,mat,piece,y-height/2,y+height/2)

# A thin bounded city plinth. No substitute lawns or parking desert.
prism('street-base','bounded streetscape foundation','paving',[(-1608,39),(-1552,39),(-1552,108),(-1608,108)],-.22,0)
for r,a,b in road_segments:
 g='road-'+r['id'];w=r['width'];l=math.dist(a,b)
 edgebox(g,'exact source-width asphalt', 'asphalt',a,b,.015,.06,w)
 # Shoulders are constructed outside carriageways. Source width is unchanged.
 for side in [-1,1]:
  street_strip(g,'stone gutter','roofSeam',a,b,.05,.045,.28,side*(w/2-.13))
  street_strip(g,'raised sidewalk','paving',a,b,.13,.22,2.4,side*(w/2+1.2))
  street_strip(g,'continuous curb','curb',a,b,.18,.28,.22,side*(w/2+.11))
 # Major through-street only: don't invent lane markings on narrow service roads.
 if w>=8:
  for d in range(2,int(l)-2,6):
   t0=d/l;t1=min(1,(d+2.5)/l)
   q0=add(a,mul(sub(b,a),t0));q1=add(a,mul(sub(b,a),t1))
   edgebox(g,'centre dash','marking',q0,q1,.061,.012,.13)
 # Paver cross joints and individually segmented curb faces.
 for d in range(1,int(l),2):
  t=d/l;dx=(b[0]-a[0])/l;dy=(b[1]-a[1])/l
  for side in [-1,1]:
   q=(a[0]+dx*d+dy*side*(w/2+1.3),a[1]+dy*d-dx*side*(w/2+1.3))
   qa=(q[0]-dy*1.075,q[1]+dx*1.075);qb=(q[0]+dy*1.075,q[1]-dx*1.075)
   street_strip(g,'sidewalk cross-joint','pavingLine',qa,qb,.247,.008,.022)

# Clear intersection surfaces remove curb/sidewalk strips crossing real branches.
for node_id,radius in JUNCTIONS:
 p=nodes[node_id];c=local((p['x'],p['y']))
 cylinder('intersection','junction carriageway','asphalt',add(c,(0,.045,0)),add(c,(0,.055,0)),radius,segments=24)

# Fine joints in remaining sidewalk/court, clipped against source carriageways/buildings.
for x in range(-1607,-1552,2):
 for y in range(40,108,2):
  p=(x+.95,y+.95)
  if road_distance(p)<1.1 or on_building(p):continue
  box('court-paving','warm stone unit', 'paving' if (x+y)%4 else 'pavingAlt',local(p,.022),(1.97,.035,1.97))

building(144,'restaurant',10.85,3)
building(145,'modern',16.95,5)
building(143,'residential',13.75,4)

def planter(group,p,size=1.45):
 c=local(p,.19);box(group,'tree pit stone base','curb',c,(size,.22,size))
 box(group,'tree pit soil', 'soil',add(c,(0,.13,0)),(size-.22,.05,size-.22))
 # Narrow metal tree grate slats, leaves keep a clearly visible trunk.
 for k in range(6):
  box(group,'tree grate','metal',add(c,(-size*.34+k*size*.135,.17,0)),(.035,.03,size-.31))

def tree(p,scale,number):
 g='tree-'+str(number);base=local(p,.34);planter(g,p,1.65*scale)
 cylinder(g,'root flare','bark',base,add(base,(.08,1.0*scale,.03)),.21*scale,.13*scale,9)
 trunk_top=add(base,(.11*scale,4.45*scale,.08*scale))
 cylinder(g,'tapered trunk','barkLight',add(base,(.08,.8*scale,.03)),trunk_top,.13*scale,.065*scale,9)
 for k in range(7):
  t=k*math.tau/7+.23;end=add(base,(math.cos(t)*1.32*scale,(4.15+(k%3)*.32)*scale,math.sin(t)*1.17*scale))
  start=add(base,(.1,(2.65+k*.11)*scale,.05));cylinder(g,'branch fork','bark',start,end,.08*scale,.025*scale,7)
  cylinder(g,'twig silhouette','barkLight',end,add(end,(math.cos(t)*.42*scale,.45*scale,math.sin(t)*.42*scale)),.026*scale,.009*scale,6)
 # Nine irregular, staggered branch lobes with smaller outer growth. Smooth
 # normals soften each lobe without increasing its tessellation. Lower dark
 # pockets and higher yellow-green tips preserve a readable layered crown.
 for k in range(9):
  th=k*2.39996;rad=1.12 if k<6 else .38;h=4.65+(k%3)*.48
  center=add(base,(math.cos(th)*rad*scale,h*scale,math.sin(th)*rad*scale))
  mat=['leafDark','leafMid','leafLight'][k%3]
  ellipsoid(g,'branch foliage lobe',mat,center,(.60+.08*(k%3))*scale,(1.05,.85,.94),5,8,.035)
  for j in range(4):
   ang=j*2.39996+k;rr=(.43+.12*(j%2))*scale
   c=add(center,(math.cos(ang)*rr,(.10+.10*j)*scale,math.sin(ang)*rr))
   mat=['leafMid','leafLight','leafSun','leafLight'][(j+k)%4]
   ellipsoid(g,'fine outer foliage tuft',mat,c,(.24+.045*((j+k)%3))*scale,(1,.82,.88),4,7,.025)
   # Bent tiny leaf sprays break the outline; 4 triangles per spray rather
   # than hundreds of extra sphere vertices. Mixed facing keeps some visible.
   if j%2==0:
    for leaf in range(2):
     direction=ang+leaf*1.1
     q=add(c,(math.cos(direction)*.24*scale,.13*scale,math.sin(direction)*.24*scale))
     u=(math.cos(direction)*.20*scale,.035*scale,math.sin(direction)*.20*scale)
     v=(-math.sin(direction)*.085*scale,.04*scale,math.cos(direction)*.085*scale)
     vs=[sub(q,u),add(q,v),add(q,(0,.055*scale,0)),add(q,u),sub(q,v)]
     mesh(g,'outer leaf spray','leafSun' if k%3 else 'leafLight',vs,[(0,1,2),(1,3,2),(3,4,2),(4,0,2),
       (2,1,0),(2,3,1),(2,4,3),(2,0,4)])

def lamp(p,index):
 g='street-furniture';c=local(p,.24)
 cylinder(g,'lamp stone footing','curb',c,add(c,(0,.12,0)),.25,segments=12)
 cylinder(g,'lamp base','metal',add(c,(0,.1,0)),add(c,(0,.43,0)),.16,.11,12)
 cylinder(g,'tapered lamp post','metal',add(c,(0,.43,0)),add(c,(0,4.65,0)),.075,.046,10)
 cylinder(g,'collar','metalLight',add(c,(0,4.5,0)),add(c,(0,4.58,0)),.11,segments=10)
 cylinder(g,'lantern lower flare','metal',add(c,(0,4.61,0)),add(c,(0,4.78,0)),.08,.21,8)
 cylinder(g,'lantern warm lens','lamp',add(c,(0,4.78,0)),add(c,(0,5.13,0)),.18,.25,4)
 cylinder(g,'lantern roof','metal',add(c,(0,5.14,0)),add(c,(0,5.30,0)),.31,.03,4)
 for dx,dz in [(-.15,-.15),(-.15,.15),(.15,-.15),(.15,.15)]:
  cylinder(g,'lantern corners','metal',add(c,(dx,4.78,dz)),add(c,(dx*1.45,5.14,dz*1.45)),.018,segments=5)

def cafe_set(p,number,umbrella=False):
 g='cafe-terrace';c=local(p,.23)
 cylinder(g,'table pedestal','metal',add(c,(0,.05,0)),add(c,(0,.78,0)),.065,segments=10)
 cylinder(g,'table foot','metal',add(c,(0,.02,0)),add(c,(0,.08,0)),.32,segments=12)
 box(g,'wood table','woodLight',add(c,(0,.83,0)),(1.0,.09,.85),-13)
 for sx,sz in [(-.85,0),(.85,0),(0,.80)]:
  q=add(c,(sx,0,sz));box(g,'chair seat','wood',add(q,(0,.46,0)),(.46,.065,.46))
  for dx in [-.18,.18]:
   for dz in [-.18,.18]:cylinder(g,'chair thin leg','metal',add(q,(dx,.03,dz)),add(q,(dx*.86,.47,dz*.86)),.022,segments=6)
  back=(0,0,.21 if sz>=0 else -.21)
  box(g,'chair backrest','woodLight',add(q,add(back,(0,.78,0))),(.44,.35,.055))
  for dx in [-.18,.18]:cylinder(g,'chair back frame','metal',add(q,(dx,.44,back[2])),add(q,(dx,.98,back[2])),.02,segments=6)
 # Cup and saucer give a deliberate human scale at the restaurant entrance.
 cylinder(g,'ceramic cup','chalk',add(c,(.18,.88,.1)),add(c,(.18,1.01,.1)),.057,.067,10)
 if umbrella:
  cylinder(g,'parasol pole','woodLight',add(c,(0,.85,0)),add(c,(0,3.14,0)),.032,segments=8)
  vs=[add(c,(0,3.22,0))]+[add(c,(math.cos(k*math.tau/8)*1.48,2.64,math.sin(k*math.tau/8)*1.48)) for k in range(8)]
  faces=[]
  for k in range(8):faces.extend([(0,1+(k+1)%8,1+k),(0,1+k,1+(k+1)%8)])
  mesh(g,'cream canvas parasol','umbrella',vs,faces)
  for k in range(8):cylinder(g,'parasol radial rib','woodLight',add(c,(0,3.19,0)),vs[1+k],.012,segments=5)

# Forecourt west of the concave restaurant; all furniture is off carriageway.
for i,p in enumerate([(-1583.8,69.7),(-1582.8,64.7)]):cafe_set(p,i,i==0)
for i,(p,s) in enumerate([((-1585.3,78.7),.95),((-1580.2,48.2),.83),((-1591.9,89.3),.9),((-1575.6,103.6),.83),((-1600.8,74.7),.95),((-1596.2,54.8),.86)]):
 if road_distance(p)>1:tree(p,s,i)
for i,p in enumerate([(-1588.0,83.6),(-1582.5,59.4),(-1578.5,43.8),(-1560.4,101.0),(-1600.1,81.1),(-1594.3,57.8)]):
 if road_distance(p)>.4:lamp(p,i)

# Two source-mapped small utility pavilions are retained at low height for context;
# they prevent the restaurant court from pretending these original footprints vanish.
for index in [146,147]:
 p=ccw(city['buildings'][index]);g='context-pavilion-'+str(index)
 prism(g,'original context footprint','ivory',p,.1,2.6)
 prism(g,'pavilion flat roof','roof',inset(p,-.08),2.6,2.79)
 for a,b in zip(p,p[1:]+p[:1]):
  if math.dist(a,b)>3.5:glazing(g,a,b,.55,2.15,'residential',2.5)

# Short designed planted strips occupy the rear edge without a lawn filler.
for y in [55,62,69,76,83,90]:
 p=(-1556.0,y);c=local(p,.2)
 box('rear-courtyard','raised planting border','sand',c,(1.3,.4,2.6))
 box('rear-courtyard','planter soil','soil',add(c,(0,.22,0)),(1.08,.05,2.38))
 for j in range(9):
  q=add(c,(rng.uniform(-.38,.38),.52+rng.random()*.3,rng.uniform(-.9,.9)))
  ellipsoid('rear-courtyard','small shrub tuft',['leafDark','leafMid','leafLight'][j%3],q,.34,(1,.9,1),3,6,.1)

def bench(p):
 g='street-furniture';c=local(p,.22)
 for z in [-.23,-.07,.09,.25]:box(g,'bench seat timber','woodLight',add(c,(0,.49,z)),(1.65,.09,.12))
 for y in [.76,.94]:box(g,'bench back timber','wood',add(c,(0,y,-.27)),(1.65,.12,.08))
 for x in [-.62,.62]:
  box(g,'bench iron leg','metal',add(c,(x,.26,0)),(.09,.5,.47))
  box(g,'bench back support','metal',add(c,(x,.72,-.30)),(.065,.5,.065))
bench((-1559.5,82))
for p in [(-1581.9,76.9),(-1559.5,79.8)]:
 c=local(p,.6);box('street-furniture','public bin','metal',c,(.48,.8,.48))
 box('street-furniture','bin lid','metalLight',add(c,(0,.42,0)),(.54,.08,.54))
 box('street-furniture','bin front slot','rubber',add(c,(0,.24,.246)),(.31,.12,.025))

def car(p):
 g='parked-compact';c=local(p,.08);angle=-13
 def part(name,mat,offset,size):
  a=math.radians(angle);x,y,z=offset;q=(c[0]+x*math.cos(a)+z*math.sin(a),c[1]+y,c[2]-x*math.sin(a)+z*math.cos(a))
  box(g,name,mat,q,size,angle)
 part('lower sculpted sill','carBody',(0,.43,0),(1.67,.48,3.4))
 part('bonnet','carBody',(0,.77,-1.07),(1.62,.25,1.08))
 part('cabin glazing','carWindow',(0,1.06,.12),(1.47,.67,1.73))
 part('floating roof','carBody',(0,1.43,.18),(1.40,.12,1.46))
 part('rear deck','carBody',(0,.8,1.25),(1.64,.25,.8))
 part('front grille','frame',(0,.55,-1.72),(.78,.19,.035))
 for x in [-.55,.55]:
  part('headlamp','lamp',(x,.73,-1.72),(.35,.14,.055));part('tail light','red',(x,.79,1.72),(.32,.16,.06))
 for x in [-.84,.84]:
  for z in [-1.05,1.06]:
   a=math.radians(angle);q=(c[0]+x*math.cos(a)+z*math.sin(a),c[1]+.40,c[2]-x*math.sin(a)+z*math.cos(a));ax=(math.cos(a),0,-math.sin(a))
   cylinder(g,'rubber tire', 'rubber',add(q,mul(ax,-.105)),add(q,mul(ax,.105)),.32,segments=16)
   cylinder(g,'alloy wheel','metalLight',add(q,mul(ax,.12 if x>0 else -.12)),add(q,mul(ax,.13 if x>0 else -.13)),.20,segments=12)
car((-1593.0,73.0))

def rider(p):
 g='D-scooter-and-rider';c=local(p,.08)
 for z in [-.69,.69]:
  cylinder(g,'scooter wheel','rubber',add(c,(-.11,.30,z)),add(c,(.11,.30,z)),.29,segments=18)
  cylinder(g,'wheel hub','metalLight',add(c,(-.125,.30,z)),add(c,(.125,.30,z)),.13,segments=12)
 box(g,'orange footboard','orange',add(c,(0,.45,0)),(.51,.13,1.36))
 ellipsoid(g,'rounded orange front fairing','orange',add(c,(0,.81,-.56)),.35,(.83,1.4,.65),6,10)
 box(g,'dark saddle','rubber',add(c,(0,.83,.22)),(.44,.15,.67))
 box(g,'rear cargo box','orange',add(c,(0,1.08,.77)),(.59,.55,.53))
 box(g,'cargo lid','orangeDark',add(c,(0,1.37,.77)),(.63,.05,.57))
 box(g,'cargo reflective stripe','stripe',add(c,(0,1.10,1.045)),(.49,.08,.015))
 cylinder(g,'steering stem','metal',add(c,(0,.73,-.58)),add(c,(0,1.15,-.61)),.035,segments=8)
 cylinder(g,'handlebar','metal',add(c,(-.33,1.15,-.61)),add(c,(.33,1.15,-.61)),.027,segments=8)
 cylinder(g,'round D headlamp','metalLight',add(c,(0,1.08,-.72)),add(c,(0,1.08,-.79)),.13,segments=16)
 cylinder(g,'round D lamp lens','lamp',add(c,(0,1.08,-.79)),add(c,(0,1.08,-.8)),.105,segments=16)
 ellipsoid(g,'orange rider jacket','orange',add(c,(0,1.22,.03)),.30,(.78,1.28,.66),6,10)
 ellipsoid(g,'rider head','skin',add(c,(0,1.65,-.015)),.17,(.85,1,1),6,10)
 ellipsoid(g,'orange helmet','orange',add(c,(0,1.77,.0)),.205,(1,.72,1),6,10)
 box(g,'helmet dark visor','frame',add(c,(0,1.72,-.16)),(.31,.09,.06))
 for side in [-1,1]:
  shoulder=add(c,(side*.22,1.38,-.02));hand=add(c,(side*.27,1.13,-.59))
  cylinder(g,'rider sleeve','orangeDark',shoulder,hand,.065,.045,9)
  ellipsoid(g,'rider glove','rubber',hand,.06,(1,1,1),4,7)
  hip=add(c,(side*.15,.95,.15));knee=add(c,(side*.23,.77,-.19));foot=add(c,(side*.23,.49,-.12))
  cylinder(g,'rider thigh','fabric',hip,knee,.09,.075,9);cylinder(g,'rider lower leg','fabric',knee,foot,.075,.06,9)
  box(g,'rider shoe','rubber',add(foot,(0,-.03,-.06)),(.14,.10,.28))
rider((-1587.0,55.0))

# Zebra crossing on the actual main road, aligned to its source segment.
a=(-1592.85,80.3);b=(-1591.44,74.45)
dx,dy=sub(b,a);l=math.hypot(dx,dy)
for k in range(7):
 p=(a[0]+dx/l*k*.75,a[1]+dy/l*k*.75)
 box('road-markings','crosswalk stripe','marking',local(p,.065),(7.0,.014,.40),math.degrees(math.atan2(dy,dx))+90)

for (group,mat),data in sorted(batches.items()):
 objects.append({'name':group+'/'+mat,'type':'mesh','material':mat,'position':[0,0,0],'rotation':[0,0,0],
  'castShadow':mat not in ('marking','pavingLine','reflection'),'receiveShadow':True,**data})

source_buildings=[]
for index,role in [(144,'three-storey concave restaurant'),(145,'five-storey modern glazed building'),(143,'four-storey mixed residential retail'),(146,'low context pavilion'),(147,'low context pavilion')]:
 footprint=city['buildings'][index]
 p=ccw(footprint)
 assert abs(sum(abs(area([p[a],p[b],p[c]])) for a,b,c in triangulate(p))-abs(area(p)))<1e-7
 source_buildings.append({'index':index,'role':role,'originalFootprint':footprint,
  'footprintSHA256':hashlib.sha256(json.dumps(footprint,separators=(',',':')).encode()).hexdigest(),
  'groundFootprintUnchanged':True,'heightIsArtDirectionNotSurvey':True})

materials={key:{'color':color,'roughness':rough,**({'metallic':.25} if key in ('metal','metalLight') else {}),**({'emissive':'#3c2d12'} if key=='lamp' else {})} for key,(color,rough) in M.items()}
scene={'version':1,'origin':{'x':ORIGIN[0],'y':ORIGIN[1]},
 'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
  'referencePath':str(REFERENCE.relative_to(ROOT)),'referenceSHA256':hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
  'coordinateMapping':'X=map.x-origin.x; Y=height metres; Z=-(map.y-origin.y)',
  'focusNode':nodes['1623821577'],'secondaryJunctionNode':nodes['9634601487'],
  'mapBounds':{'minX':BOUNDS[0],'minY':BOUNDS[1],'maxX':BOUNDS[2],'maxY':BOUNDS[3]},
  'buildings':source_buildings,'roads':source_roads,
  'roadPolicy':'Only display clipping at the stage perimeter; original centerlines, widths, directions and topology unchanged.',
  'artDirection':'Exact three primary source footprints; architectural heights/materials are new isolated visual study, not gameplay data.'},
 # V1 actual image showed too much empty stage edge. A slightly more frontal
 # view narrows the projected 3-building group so a closer portrait frame can
 # retain its primary silhouettes. This revised fit is static, not rendered.
 'camera':{'target':[8,7,3],'position':[-30,70,105],'orthoHeight':31},
 'materials':materials,'objects':objects}

# Input-asset integrity only: not a game/render/unit-test run.
for obj in objects:
 assert len(obj['vertices'])%3==0 and len(obj['indices'])%3==0
 assert len(obj['normals'])==len(obj['vertices'])
 assert all(math.isfinite(v) for v in obj['vertices']+obj['normals'])
 assert min(obj['indices'])>=0 and max(obj['indices'])<len(obj['vertices'])//3
 assert obj['material'] in materials
 assert all(abs(length(obj['normals'][i:i+3])-1)<2e-6 for i in range(0,len(obj['normals']),3))
 for i in range(0,len(obj['indices']),3):
  ids=obj['indices'][i:i+3]
  a,b,c=[obj['vertices'][j*3:j*3+3] for j in ids]
  face=cross(sub(b,a),sub(c,a))
  assert length(face)>1e-10, (obj['name'],'degenerate rounded triangle')
  ns=[obj['normals'][j*3:j*3+3] for j in ids]
  # Hard faces retain exact winding normals; organic surfaces legitimately
  # interpolate radial normals, which must stay in the outward hemisphere.
  threshold=.999 if ns[0]==ns[1]==ns[2] else .05
  assert all(dot(norm(face),n)>threshold for n in ns), (obj['name'],'normal mismatch')

output=HERE/'scene-design.json'
output.write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':'))+'\n')
manifest={'version':1,'generator':'build-scene-assets.py','seed':SEED,'dependencies':'Python 3 standard library only',
 'sourceSHA256':scene['source']['sha256'],'sceneSHA256':hashlib.sha256(output.read_bytes()).hexdigest(),
 'generatorSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'objects':len(objects),'authoringParts':sum(authored.values()),'triangles':sum(len(o['indices'])//3 for o in objects),
 'vertices':sum(len(o['vertices'])//3 for o in objects),'materials':len(materials),'sceneBytes':output.stat().st_size,
 'groups':dict(sorted(authored.items())),
 'cameraCandidates':[scene['camera'],{'target':[6,6,3],'position':[-52,68,83],'orthoHeight':35}],
 'integrity':'Source-footprint triangulated area, finite vertices/normals, index range, material references, unit normals, nondegenerate triangles and outward hard/smooth normal agreement checked during asset generation.',
 'staticCorrections':['Cocos camera half-height changed from 63 to 35 m; aim shifted toward the three primary buildings.',
  'Removed lower HVAC/access assembly buried inside the restaurant setback penthouse; retained equipment on the upper terrace.',
  'Subtracted branch-mouth polygons from raised sidewalks/curbs/joints and lowered junction asphalt to carriageway level.',
  'V1 actual-engine-image response: layered outward sky/diagonal/warm glass patches, warmer facade accents, smooth organic normals and rebuilt layered tree crowns.',
  'V1 actual-engine-image response: narrowed projected group with a slightly more frontal camera and reduced half-height to 31 m.'],
 'feedbackImageSHA256':hashlib.sha256((HERE/'engine-v1.jpg').read_bytes()).hexdigest(),
 'notPerformed':['game launch','browser operation','render screenshot','typecheck','unit or regression tests','save-state access','user visual approval'],
 'limitations':['Opaque layered glass approximation; no transmission or screen-space reflections.',
  'No external character/car/sculpture models: static authored scale references.',
  'Building heights and facade programs are art direction, not original cadastral attributes.',
  'Stage-border road clipping is presentation only; no routing edits.',
  'Final on-screen lighting, camera fit, anti-aliasing and material response require the scheduled stage review.']}
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['objects','authoringParts','triangles','vertices','sceneBytes','sceneSHA256']},indent=2))
