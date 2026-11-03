import { Node } from 'cc';
import { cartoonArt } from './CartoonArt';
// Each immutable picture belongs to one dialog; the shared loader protects closed pages.
export function vehicleSideArt(parent:Node,tier:number,x:number,y:number,width:number,height:number,fallback:Node):Node {
 return cartoonArt(parent,['side-d','side-d-plus','side-c','side-c-plus','side-b','side-b-plus','side-a','side-s','side-ss','side-sss'][tier-1]||'side-d',x,y,width,height,fallback);
}
