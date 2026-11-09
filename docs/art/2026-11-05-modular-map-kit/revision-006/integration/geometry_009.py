"""Static map-plane geometry only; no game graph or image manipulation."""
import math

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def edges(p):return list(zip(p,p[1:]+p[:1]))
def inside(q,p):
 hit=False
 for a,b in edges(p):
  if abs(cross(a,b,q))<1e-9 and min(a[0],b[0])-1e-9<=q[0]<=max(a[0],b[0])+1e-9 and min(a[1],b[1])-1e-9<=q[1]<=max(a[1],b[1])+1e-9:return True
  if (a[1]>q[1])!=(b[1]>q[1]) and q[0]<(b[0]-a[0])*(q[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit

def segments(a,b,c,d):
 ab1,ab2,cd1,cd2=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
 if ab1*ab2 < -1e-12 and cd1*cd2 < -1e-12:return True
 def on(a,b,q):return abs(cross(a,b,q))<1e-9 and min(a[0],b[0])-1e-9<=q[0]<=max(a[0],b[0])+1e-9 and min(a[1],b[1])-1e-9<=q[1]<=max(a[1],b[1])+1e-9
 return any([on(a,b,c),on(a,b,d),on(c,d,a),on(c,d,b)])

def point_segment(q,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];sq=dx*dx+dy*dy
 t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/sq)) if sq else 0
 return math.dist(q,[a[0]+dx*t,a[1]+dy*t])

def segment_gap(a,b,c,d):return 0 if segments(a,b,c,d) else min(point_segment(q,x,y)for q,x,y in [(a,c,d),(b,c,d),(c,a,b),(d,a,b)])
def gap(a,b):
 if any(inside(q,b)for q in a) or any(inside(q,a)for q in b):return 0
 return min(segment_gap(x,y,z,w)for x,y in edges(a)for z,w in edges(b))
def line_gap(poly,line):
 if any(inside(q,poly)for q in line):return 0
 return min(segment_gap(a,b,c,d)for a,b in edges(poly)for c,d in zip(line,line[1:]))
def hull(points):
 points=sorted(set(tuple(p)for p in points));lo=[];hi=[]
 for stack,seq in [(lo,points),(hi,reversed(points))]:
  for q in seq:
   while len(stack)>1 and cross(stack[-2],stack[-1],q)<=0:stack.pop()
   stack.append(q)
 return [list(q)for q in lo[:-1]+hi[:-1]]
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in edges(poly)))/2

def clip_half(poly,n,c):
 result=[]
 for a,b in edges(poly):
  da=sum(a[k]*n[k]for k in (0,1))-c;db=sum(b[k]*n[k]for k in (0,1))-c
  if da<=1e-9:result.append(a)
  if (da<0)!=(db<0):
   t=da/(da-db);result.append([a[k]+t*(b[k]-a[k])for k in (0,1)])
 return result
