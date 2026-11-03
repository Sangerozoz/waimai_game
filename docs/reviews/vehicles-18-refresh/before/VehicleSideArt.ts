import { Node } from 'cc';
import { cartoonArt } from './CartoonArt';
// Each immutable picture belongs to one dialog; the shared loader protects closed pages.
export function vehicleSideArt(parent:Node,tier:number,x:number,y:number,width:number,height:number,fallback:Node):Node {
 return cartoonArt(parent,tier===2?'side-d-plus':'side-d',x,y,width,height,fallback);
}
