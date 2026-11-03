import { Fragility } from '../domain/GameConfig';
import { COUNTY_FOOD_MIX } from './CountyConfig';

export interface FoodItem { id:string; name:string; imageIndex:number; fragility:Fragility; unitWeightKg:number }
// Stable indices: first 16 retain their atlas; 16–49 await the approved AU04 artwork.
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
  {id:'curry-chicken-rice',name:'咖喱鸡肉饭',imageIndex:16,fragility:'normal',unitWeightKg:1},
  {id:'eel-rice',name:'鳗鱼饭',imageIndex:17,fragility:'durable',unitWeightKg:1},
  {id:'tomato-egg-rice',name:'番茄炒蛋饭',imageIndex:18,fragility:'normal',unitWeightKg:1},
  {id:'braised-chicken-rice',name:'黄焖鸡米饭',imageIndex:19,fragility:'normal',unitWeightKg:1},
  {id:'roast-duck-rice',name:'烧鸭饭',imageIndex:20,fragility:'durable',unitWeightKg:1},
  {id:'pork-cutlet-rice',name:'猪排饭',imageIndex:21,fragility:'durable',unitWeightKg:1},
  {id:'shrimp-fried-rice',name:'虾仁炒饭',imageIndex:22,fragility:'durable',unitWeightKg:1},
  {id:'sausage-claypot-rice',name:'腊味煲仔饭',imageIndex:23,fragility:'durable',unitWeightKg:1},
  {id:'seafood-fried-rice',name:'海鲜炒饭',imageIndex:24,fragility:'durable',unitWeightKg:1},
  {id:'mushroom-chicken-rice',name:'香菇滑鸡饭',imageIndex:25,fragility:'normal',unitWeightKg:1},
  {id:'beef-noodle-soup',name:'牛肉汤面',imageIndex:26,fragility:'fragile',unitWeightKg:1},
  {id:'spicy-rice-noodles',name:'酸辣粉',imageIndex:27,fragility:'fragile',unitWeightKg:1},
  {id:'snail-rice-noodles',name:'螺蛳粉',imageIndex:28,fragility:'fragile',unitWeightKg:1},
  {id:'rice-noodle-soup',name:'过桥米线',imageIndex:29,fragility:'fragile',unitWeightKg:1},
  {id:'spicy-mixed-noodles',name:'担担面',imageIndex:30,fragility:'normal',unitWeightKg:0.5},
  {id:'cold-noodles',name:'凉面',imageIndex:31,fragility:'durable',unitWeightKg:0.5},
  {id:'fried-noodles',name:'炒面',imageIndex:32,fragility:'durable',unitWeightKg:0.5},
  {id:'spaghetti',name:'意大利面',imageIndex:33,fragility:'normal',unitWeightKg:0.5},
  {id:'steamed-rice-rolls',name:'肠粉',imageIndex:34,fragility:'normal',unitWeightKg:0.5},
  {id:'steamed-shrimp-dumplings',name:'虾饺',imageIndex:35,fragility:'normal',unitWeightKg:0.5},
  {id:'pan-fried-buns',name:'生煎包',imageIndex:36,fragility:'durable',unitWeightKg:0.5},
  {id:'spring-rolls',name:'春卷',imageIndex:37,fragility:'durable',unitWeightKg:0.5},
  {id:'fried-chicken',name:'炸鸡',imageIndex:38,fragility:'durable',unitWeightKg:1},
  {id:'fries',name:'薯条',imageIndex:39,fragility:'durable',unitWeightKg:0.5},
  {id:'chicken-wrap',name:'鸡肉卷',imageIndex:40,fragility:'durable',unitWeightKg:0.5},
  {id:'sandwich',name:'三明治',imageIndex:41,fragility:'durable',unitWeightKg:0.5},
  {id:'grilled-skewers',name:'烧烤拼盘',imageIndex:42,fragility:'durable',unitWeightKg:1},
  {id:'fruit-cup',name:'水果杯',imageIndex:43,fragility:'normal',unitWeightKg:0.5},
  {id:'egg-tarts',name:'蛋挞',imageIndex:44,fragility:'fragile',unitWeightKg:0.5},
  {id:'pudding',name:'布丁',imageIndex:45,fragility:'fragile',unitWeightKg:0.5},
  {id:'ice-cream',name:'冰淇淋',imageIndex:46,fragility:'fragile',unitWeightKg:0.5},
  {id:'coffee',name:'咖啡',imageIndex:47,fragility:'fragile',unitWeightKg:0.5},
  {id:'lemon-tea',name:'柠檬茶',imageIndex:48,fragility:'fragile',unitWeightKg:0.5},
  {id:'orange-juice',name:'鲜榨橙汁',imageIndex:49,fragility:'fragile',unitWeightKg:0.5},
];

export function selectFoodForOffer(classRoll:number,itemRoll:number,shownFoodIds:readonly string[]):FoodItem {
  if(![classRoll,itemRoll].every(n=>Number.isFinite(n)&&n>=0&&n<1))throw new Error('Food sample must be within [0,1)');
  const classes:Fragility[]=['fragile','normal','durable'];
  const weights=classes.map(kind=>COUNTY_FOOD_MIX.weights[kind]);
  const total=weights.reduce((sum,n)=>sum+n,0);
  if(weights.some(n=>!Number.isFinite(n)||n<0)||!Number.isFinite(total)||total<=0)throw new Error('Invalid food class weights');
  const pools=classes.map(kind=>FOOD_CATALOG.filter(food=>food.fragility===kind));
  if(pools.some((pool,i)=>weights[i]>0&&!pool.length))throw new Error('Positive food class has an empty catalog');
  let cumulative=0;
  for(let i=0;i<classes.length;i++){
    cumulative+=weights[i];
    if(classRoll>=cumulative/total)continue;
    const unseen=pools[i].filter(food=>shownFoodIds.indexOf(food.id)<0);
    const choices=unseen.length?unseen:pools[i];
    return choices[Math.floor(itemRoll*choices.length)];
  }
  throw new Error('Invalid food class weights');
}

export function foodForOffer(text:string):FoodItem {
  const name=text.split('·')[0].trim();
  const legacy:Record<string,number>={'家常饭盒':0,'家常饭':0,'小炒套餐':2};
  return FOOD_CATALOG.find(food=>food.name===name)||FOOD_CATALOG[legacy[name]??0];
}
