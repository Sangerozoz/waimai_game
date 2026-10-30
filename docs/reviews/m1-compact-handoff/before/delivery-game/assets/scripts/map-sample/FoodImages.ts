import { Node } from 'cc';
import { foodForOffer } from './FoodCatalog';
import { cartoonArt, cartoonFoodKey } from './CartoonArt';
import { box, C, label } from './SampleUI';

export function foodImage(parent:Node,food:string,x:number,y:number,size:number):Node {
 const node=box(parent,'FoodImage',x,y,size,size,'#FFF2CD',16,C.line);
 const fallback=label(node,'餐品',0,0,14,C.muted,size-12,false,'center');
 cartoonArt(node,cartoonFoodKey(foodForOffer(food).imageIndex),0,0,size-10,size-10,fallback.node);return node;
}
