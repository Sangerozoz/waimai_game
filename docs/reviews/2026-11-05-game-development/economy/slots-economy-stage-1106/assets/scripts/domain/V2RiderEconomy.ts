import { V2_CONFIG as C } from './V2EconomyConfig';
// Explicit new helpers; the legacy exports below remain the legacy evaluator.
export { slotRiderEffects,slotRiderUpgradeQuote,slotRiderHireQuote } from './V2EconomyProfiles';

function levelCheck(level:number):void {
 if(!Number.isInteger(level)||level<1||level>30)throw new Error('人物等级无效');
}
/** Fixed identity price; the UI and wallet consume this same quote. */
export function riderHireQuote(id:string):{riderId:string;priceCents:number;baseIncomeFactor:number} {
 const row=C.riders.find(r=>r.id===id);if(!row)throw new Error('人物无效');
 return {riderId:id,priceCents:row.price*100,baseIncomeFactor:row.baseIncomeFactor};
}
export function riderEffects(id:string,level:number):{baseIncomeFactor:number;trainingIncomeFactor:number;incomeFactor:number;fixedServiceReduction:number} {
 levelCheck(level);const baseIncomeFactor=riderHireQuote(id).baseIncomeFactor,progress=Math.pow((level-1)/29,.65);
 const trainingIncomeFactor=1+C.maxRiderUpgradeEffects.income*progress;
 return {baseIncomeFactor,trainingIncomeFactor,incomeFactor:baseIncomeFactor*trainingIncomeFactor,fixedServiceReduction:C.maxRiderUpgradeEffects.fixedServiceReduction*progress};
}
export function riderUpgradeQuote(id:string,level:number) {
 const current=riderEffects(id,level);if(level===30)return null;
 return {costCents:(C.upgradeLevels[level].riderCumulativeCost-C.upgradeLevels[level-1].riderCumulativeCost)*100,current,next:riderEffects(id,level+1),nextLevel:level+1};
}
/** Recommendation only; buying one identity never changes another identity's price. */
export function cheapestUnhiredRider(riders:readonly {id:string}[]) {
 const owned=new Set(riders.map(r=>r.id));const row=C.riders.filter(r=>!owned.has(r.id)).reduce<(typeof C.riders)[number]|null>((best,r)=>!best||r.price<best.price?r:best,null);
 return row?riderHireQuote(row.id):null;
}
/** Starter vehicle costs use the same phase formula as the paid model table. */
export function vehicleCumulativeUpgradeCost(basis:number,level:number):number {
 levelCheck(level);const old=(L:number)=>Math.round(3*basis*Math.pow((L-1)/29,1.65));
 if(level<=5)return old(level);const c5=old(5);
 return Math.round(c5+(1.5*basis-c5)*Math.pow((level-5)/25,1.3));
}
