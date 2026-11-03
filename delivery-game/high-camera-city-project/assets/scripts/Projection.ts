export type Point = [number, number];
/** One canvas-down projection for ground, native sprite anchors, route and markers. */
export class Projection {
 constructor(readonly origin:Point, readonly pixelsPerUnit:number) {}
 projectMap(x:number,y:number,z=0):Point {
  const dx=x-this.origin[0],dy=y-this.origin[1];
  return [(dx-dy)*.7071067812*this.pixelsPerUnit,((dx+dy)*.6272113751-z*.4617486132)*this.pixelsPerUnit];
 }
}
