import { Fragility } from '../domain/GameConfig';

export interface FoodItem { id:string; name:string; imageIndex:number; fragility:Fragility; unitWeightKg:number }
// Atlas coordinates: 4 columns × 4 rows, left to right, starting at the top.
export const FOOD_CATALOG:ReadonlyArray<FoodItem>=[
  {id:'chicken-rice',name:'鸡腿饭',imageIndex:0,fragility:'durable',unitWeightKg:1},
  {id:'beef-rice',name:'牛肉饭',imageIndex:1,fragility:'durable',unitWeightKg:1},
  {id:'pork-rice',name:'红烧肉饭',imageIndex:2,fragility:'durable',unitWeightKg:1},
  {id:'tofu-rice',name:'麻婆豆腐饭',imageIndex:3,fragility:'normal',unitWeightKg:1},
  {id:'soup-noodles',name:'鲜汤面',imageIndex:4,fragility:'fragile',unitWeightKg:1},
  {id:'mixed-noodles',name:'拌面',imageIndex:5,fragility:'durable',unitWeightKg:.5},
  {id:'wonton',name:'馄饨',imageIndex:6,fragility:'fragile',unitWeightKg:1},
  {id:'hotpot',name:'小火锅',imageIndex:7,fragility:'fragile',unitWeightKg:1.5},
  {id:'dumplings',name:'饺子',imageIndex:8,fragility:'normal',unitWeightKg:.5},
  {id:'buns',name:'包子',imageIndex:9,fragility:'durable',unitWeightKg:.5},
  {id:'pizza',name:'披萨',imageIndex:10,fragility:'normal',unitWeightKg:1},
  {id:'burger',name:'汉堡',imageIndex:11,fragility:'durable',unitWeightKg:.5},
  {id:'salad',name:'轻食沙拉',imageIndex:12,fragility:'normal',unitWeightKg:.5},
  {id:'sushi',name:'寿司',imageIndex:13,fragility:'normal',unitWeightKg:.5},
  {id:'cake',name:'蛋糕',imageIndex:14,fragility:'fragile',unitWeightKg:1},
  {id:'milk-tea',name:'奶茶',imageIndex:15,fragility:'fragile',unitWeightKg:.5},
];
export function foodForOffer(text:string):FoodItem {
  const name=text.split('·')[0].trim();
  const legacy:Record<string,number>={'家常饭盒':0,'家常饭':0,'小炒套餐':2};
  return FOOD_CATALOG.find(food=>food.name===name)||FOOD_CATALOG[legacy[name]??0];
}
