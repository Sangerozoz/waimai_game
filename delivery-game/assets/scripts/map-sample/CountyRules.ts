import { Damage, DAMAGE_EFFECTS, Fragility, GAME_CONFIG, getExperienceLevel, getPlayerIncomeMultiplier, Player, RouteId, ROUTES } from '../domain/GameConfig';
import { COUNTY_VEHICLES, countyExperienceLevel } from './CountyConfig';
import { formatDeliveryTime } from './DeliveryClock';

export interface CountyTerms {
  id:string; feeCents:number; type:'normal'|'urgent'; fragility:Fragility; demand:'none'|'door';
}
export interface CountyOutcome { displaySeconds:number; deadlineSeconds:number; damage:Damage; doorAnswer:boolean|null }
export interface CountyReceipt {
  orderId:string; incomeCents:number; basePriceCents:number; ratingBefore:number; ratingDelta:number; ratingAfter:number;
  experienceGained:number; levelBefore:number; levelAfter:number; lateSeconds:number; damage:Damage;
  completedOrders:number; newCashCents:number; summary:string[]; playerBefore:Player; outcome:CountyOutcome;
}
export function newCountyPlayer():Player {
  return {cashCents:GAME_CONFIG.initialCashCents,rating:GAME_CONFIG.initialRating,experience:0,completedOrders:0,vehicleTier:1,stationLevel:1,level:1};
}
export function countyDamageChance(route:RouteId,fragility:Fragility):number {
  return ROUTES.find(r=>r.id===route)!.damageChance[fragility];
}
export function estimateCountyIncome(player:Readonly<Player>,feeCents:number):number {
  return Math.round(feeCents*COUNTY_VEHICLES[player.vehicleTier-1].incomeMultiplier*getPlayerIncomeMultiplier(player.level)*(.85+player.rating*.003));
}
export function countySettlement(before:Readonly<Player>,offer:CountyTerms,outcome:CountyOutcome):{player:Player;receipt:CountyReceipt} {
  return settle(before,offer,outcome,countyExperienceLevel);
}
export function legacyCountySettlement(before:Readonly<Player>,offer:CountyTerms,outcome:CountyOutcome):{player:Player;receipt:CountyReceipt} {
  return settle(before,offer,outcome,getExperienceLevel);
}
/** Computes a settlement quote without creating or changing a wallet. */
export function quoteCountyIncome(before:Readonly<Player>,offer:CountyTerms,outcome:CountyOutcome):{incomeCents:number;ratingDelta:number;ratingAfter:number;lateSeconds:number;summary:string[]} {
  if(offer.demand==='door'&&outcome.doorAnswer===null)throw new Error('请先处理顾客的放门口需求');
  const effect=DAMAGE_EFFECTS[outcome.damage],lateSeconds=Math.max(0,outcome.displaySeconds-outcome.deadlineSeconds),summary:string[]=[];
  let change=effect.ratingDelta;
  if(lateSeconds>0){change-=3;summary.push(`晚到${formatDeliveryTime(lateSeconds)}，评价−3`);}
  else if(offer.type==='urgent'){change+=2;summary.push('加急准时，评价+2');}
  else summary.push('准时送达');
  if(offer.fragility==='fragile'&&outcome.damage==='none'){change+=2;summary.push('怕洒餐品完好，评价+2');}
  if(offer.demand==='door'){change+=outcome.doorAnswer?2:-3;summary.push(outcome.doorAnswer?'按要求放门口，评价+2':'敲门打扰顾客，评价−3');}
  summary.push(effect.label);
  const ratingDelta=Math.max(-10,Math.min(6,change)),ratingAfter=Math.max(20,Math.min(100,before.rating+ratingDelta));
  const incomeCents=Math.round(offer.feeCents*COUNTY_VEHICLES[before.vehicleTier-1].incomeMultiplier*getPlayerIncomeMultiplier(before.level)*(.85+ratingAfter*.003)*effect.retainedIncome);
  return {incomeCents,ratingDelta,ratingAfter,lateSeconds,summary};
}

function settle(before:Readonly<Player>,offer:CountyTerms,outcome:CountyOutcome,levelForExperience:(xp:number)=>number):{player:Player;receipt:CountyReceipt} {
  const {incomeCents,ratingDelta,ratingAfter,lateSeconds,summary}=quoteCountyIncome(before,offer,outcome);
  const effect=DAMAGE_EFFECTS[outcome.damage];
  const cashCents=before.cashCents+incomeCents,experience=before.experience+GAME_CONFIG.experiencePerOrder,completedOrders=before.completedOrders+1;
  if(![cashCents,experience,completedOrders,incomeCents].every(Number.isSafeInteger))throw new Error('经营数值超出安全范围');
  const player={...before,cashCents,experience,completedOrders,rating:ratingAfter,level:levelForExperience(experience)};
  summary.push(`经验+${GAME_CONFIG.experiencePerOrder}`,`车辆收入×${COUNTY_VEHICLES[before.vehicleTier-1].incomeMultiplier.toFixed(2)} · 等级收入×${getPlayerIncomeMultiplier(before.level).toFixed(2)}`,`评价倍率×${(.85+ratingAfter*.003).toFixed(3)} · 餐损保留${Math.round(effect.retainedIncome*100)}%`);
  const receipt:CountyReceipt={orderId:offer.id,incomeCents,basePriceCents:offer.feeCents,ratingBefore:before.rating,ratingDelta,ratingAfter,experienceGained:GAME_CONFIG.experiencePerOrder,levelBefore:before.level,levelAfter:player.level,lateSeconds,damage:outcome.damage,completedOrders,newCashCents:cashCents,summary,playerBefore:{...before},outcome:{...outcome}};
  return {player,receipt};
}

/** Ordered counterfactuals are presentation only and never touch player funds. */
export function receiptIncomeBreakdown(offer:CountyTerms,receipt:CountyReceipt):{onTimeUndamaged:number;lateImpact:number;damageImpact:number}|null {
 const actual=receipt.outcome,before=receipt.playerBefore;
 const onTimeUndamaged=quoteCountyIncome(before,offer,{...actual,displaySeconds:Math.min(actual.displaySeconds,actual.deadlineSeconds),damage:'none'}).incomeCents;
 const actualTimeUndamaged=quoteCountyIncome(before,offer,{...actual,damage:'none'}).incomeCents;
 const quotedActual=quoteCountyIncome(before,offer,actual).incomeCents;
 if(quotedActual!==receipt.incomeCents)return null;
 return {onTimeUndamaged,lateImpact:onTimeUndamaged-actualTimeUndamaged,damageImpact:actualTimeUndamaged-quotedActual};
}
