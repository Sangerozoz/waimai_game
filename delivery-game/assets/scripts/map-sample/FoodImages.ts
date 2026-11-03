import { Node } from 'cc';
import { foodForOffer } from './FoodCatalog';
import { cartoonArt, cartoonFoodKey } from './CartoonArt';
import { box, C, label } from './SampleUI';

export function foodImage(parent:Node,food:string,x:number,y:number,size:number):Node {
 const node=box(parent,'FoodImage',x,y,size,size,'#FFF2CD',16,C.line);
 const item=foodForOffer(food),fallback=label(node,item.name,0,0,14,C.ink,size-12,true,'center');
 const key=cartoonFoodKey(item.imageIndex);
 if(key)cartoonArt(node,key,0,0,size-10,size-10,fallback.node);return node;
}
