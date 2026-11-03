import { Point, Projection } from './Projection';
export type Bounds={minX:number;maxX:number;minY:number;maxY:number};
export type ImageSpec={file:string;sha256:string;nativeSize:Point};
export type Region=ImageSpec&{id:string;anchorMap:Point;anchorUV:Point;nativePixelsPerUnit:number;sortOrder:number;ownershipPolygonUV?:Point[];registration:{status:'preview-only'|'ready';evidence?:string;controlPoints?:Array<{map:Point;pixel:Point}>;maxResidualPixels?:number;routeCoverageMapPolygon?:Point[]|null}};
export type RiderFrame=ImageSpec&{direction:string;wheelContactAnchorUV:Point;widthUnits:number};
export type Atlas={schemaVersion:number;projection:{originMap:Point;elevationDeg:number;azimuthDeg:number};displayBounds:Bounds;deliveryPolygon:Point[];camera:{focusMap:Point;viewWidthUnits:number;minViewWidthUnits:number;maxViewWidthUnits:number};regions:Region[];streaming?:{paddingScreenPixels?:number;releaseDelaySeconds?:number;maxConcurrentLoads?:number};roads?:Array<{id:string;width:number;nodes:Point[]}>;rider?:{frames:RiderFrame[];initialMap?:Point;initialDirection?:string}};
export const inside=(p:Point,poly:Point[]):boolean=>{let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[j],b=poly[i],cross=(p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0]);if(Math.abs(cross)<1e-7&&p[0]>=Math.min(a[0],b[0])-1e-7&&p[0]<=Math.max(a[0],b[0])+1e-7&&p[1]>=Math.min(a[1],b[1])-1e-7&&p[1]<=Math.max(a[1],b[1])+1e-7)return true;if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;};
export class AtlasModel {
 readonly projection:Projection;
 constructor(readonly atlas:Atlas){
  if(atlas.schemaVersion!==1||atlas.projection.elevationDeg!==62.5||atlas.projection.azimuthDeg!==45)throw Error('Unsupported atlas projection');
  this.projection=new Projection(atlas.projection.originMap,1);
  const ids=new Set<string>();for(const r of atlas.regions){if(ids.has(r.id)||!(r.nativePixelsPerUnit>0)||!Number.isFinite(r.sortOrder))throw Error('Invalid region '+r.id);ids.add(r.id);if(r.ownershipPolygonUV&&r.ownershipPolygonUV.length<3)throw Error('Invalid ownership '+r.id);if(r.registration.status==='ready'){const c=r.registration.controlPoints??[];let spread=false;for(let i=1;i<c.length;i++)for(let j=i+1;j<c.length;j++)if(Math.abs((c[i].map[0]-c[0].map[0])*(c[j].map[1]-c[0].map[1])-(c[j].map[0]-c[0].map[0])*(c[i].map[1]-c[0].map[1]))>1e-5)spread=true;if(!r.registration.evidence||!Number.isFinite(r.registration.maxResidualPixels)||!spread)throw Error('Missing measured registration '+r.id);}}
  if(atlas.deliveryPolygon.length<3)throw Error('Missing blue delivery polygon');
  for(const r of atlas.regions){const coverage=r.registration.routeCoverageMapPolygon;if(coverage&&(coverage.length<3||coverage.some(p=>p.length!==2||!p.every(Number.isFinite))))throw Error('Invalid route coverage polygon '+r.id);}
 }
 imageBounds(r:Region):Bounds{const p=this.projection.projectMap(...r.anchorMap),w=r.nativeSize[0]/r.nativePixelsPerUnit,h=r.nativeSize[1]/r.nativePixelsPerUnit;return {minX:p[0]-r.anchorUV[0]*w,maxX:p[0]+(1-r.anchorUV[0])*w,minY:p[1]-r.anchorUV[1]*h,maxY:p[1]+(1-r.anchorUV[1])*h};}
 ownership(r:Region):Point[]{const b=this.imageBounds(r);return (r.ownershipPolygonUV??[[0,0],[1,0],[1,1],[0,1]]).map(p=>[b.minX+p[0]*(b.maxX-b.minX),b.minY+p[1]*(b.maxY-b.minY)] as Point);}
 /** Route trust is independent of native art ownership/clipping. Legacy entries retain their ownership coverage. */
 routeCoverage(r:Region):Point[]{const coverage=r.registration.routeCoverageMapPolygon;return coverage?coverage.map(p=>this.projection.projectMap(...p)):this.ownership(r);}
 allowed(map:Point):boolean{const p=this.projection.projectMap(...map);return inside(map,this.atlas.deliveryPolygon)&&this.atlas.regions.some(r=>r.registration.status==='ready'&&inside(p,this.routeCoverage(r)));}
 onSourceRoad(map:Point):boolean{return (this.atlas.roads??[]).some(r=>r.nodes.some((q,i)=>i>0&&this.onSegment(map,r.nodes[i-1],q)));}
 private onSegment(p:Point,a:Point,b:Point):boolean{const dx=b[0]-a[0],dy=b[1]-a[1],len=dx*dx+dy*dy;if(len<1e-10)return Math.hypot(p[0]-a[0],p[1]-a[1])<.02;const t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/len;return t>=-1e-6&&t<=1.000001&&Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)<.02;}
 routeAllowed(route:Point[]):boolean{
  if(!route.length||route.some(p=>!p.every(Number.isFinite)||!this.allowed(p)))return false;
  for(let i=1;i<route.length;i++)if(!(this.atlas.roads??[]).some(r=>r.nodes.some((q,j)=>j>0&&this.onSegment(route[i-1],r.nodes[j-1],q)&&this.onSegment(route[i],r.nodes[j-1],q))))return false;
  // Split at every delivery/trusted-corridor boundary, then inspect each open interval.
  const polys=[this.atlas.deliveryPolygon.map(p=>this.projection.projectMap(...p)),...this.atlas.regions.filter(r=>r.registration.status==='ready').map(r=>this.routeCoverage(r))];
  for(let i=1;i<route.length;i++){const a=this.projection.projectMap(...route[i-1]),b=this.projection.projectMap(...route[i]),dx=b[0]-a[0],dy=b[1]-a[1],ts=[0,1];for(const poly of polys)for(let j=0;j<poly.length;j++){const p=poly[j],q=poly[(j+1)%poly.length],ex=q[0]-p[0],ey=q[1]-p[1],den=dx*ey-dy*ex;if(Math.abs(den)<1e-10)continue;const t=((p[0]-a[0])*ey-(p[1]-a[1])*ex)/den,u=((p[0]-a[0])*dy-(p[1]-a[1])*dx)/den;if(t>0&&t<1&&u>=0&&u<=1)ts.push(t);}ts.sort((x,y)=>x-y);for(let j=1;j<ts.length;j++){const t=(ts[j-1]+ts[j])/2,p:Point=[route[i-1][0]+(route[i][0]-route[i-1][0])*t,route[i-1][1]+(route[i][1]-route[i-1][1])*t];if(!this.allowed(p))return false;}}
  return true;
 }
}
