import { Point } from './MapTypes';

export interface Bounds { minX:number; maxX:number; minY:number; maxY:number }
export function contains(bounds:Bounds,point:Point):boolean {
  return point[0]>=bounds.minX&&point[0]<=bounds.maxX&&point[1]>=bounds.minY&&point[1]<=bounds.maxY;
}
export function expandBounds(bounds:Bounds,fraction:number):Bounds {
  const x=(bounds.maxX-bounds.minX)*fraction,y=(bounds.maxY-bounds.minY)*fraction;
  return {minX:bounds.minX-x,maxX:bounds.maxX+x,minY:bounds.minY-y,maxY:bounds.maxY+y};
}
/** Offsets are screen pixels; bounds and the camera centre are road metres. */
export function clampCamera(bounds:Bounds,offset:Point,scale:number,width:number,height:number):Point {
  const axis=(min:number,max:number,half:number,value:number):number=>{
    const low=min+half/scale,high=max-half/scale;
    const centre=low>high?(min+max)/2:Math.max(low,Math.min(high,-value/scale));
    return -centre*scale;
  };
  return [axis(bounds.minX,bounds.maxX,width/2,offset[0]),axis(bounds.minY,bounds.maxY,height/2,offset[1])];
}
/** Only historic outside geometry widens the camera, never ordinary dispatch. */
export function compatibilityBounds(bounds:Bounds,points:Point[],halfWidth:number,halfHeight:number):Bounds {
  const result={...bounds};
  for(const p of points)if(!contains(bounds,p)){
    result.minX=Math.min(result.minX,p[0]-halfWidth);result.maxX=Math.max(result.maxX,p[0]+halfWidth);
    result.minY=Math.min(result.minY,p[1]-halfHeight);result.maxY=Math.max(result.maxY,p[1]+halfHeight);
  }
  return result;
}
