/** V1 section 6. Supply prices are deliberately independent of the V2 asset curve. */
export type V2SupplyId='water'|'noodles'|'drink'|'fastFood'|'milkTea'|'premiumMeal';
export interface V2SupplyItem {id:V2SupplyId;name:string;unlockMapId:number;costCents:number;restore:number;durationSeconds:number;gameSeconds:number}
export const V2_SUPPLY_CATALOG:ReadonlyArray<Readonly<V2SupplyItem>>=Object.freeze([
 {id:'water',name:'纯净水',unlockMapId:1,costCents:100,restore:20,durationSeconds:1,gameSeconds:30},
 {id:'noodles',name:'泡面',unlockMapId:1,costCents:300,restore:70,durationSeconds:3,gameSeconds:120},
 {id:'drink',name:'瓶装饮料',unlockMapId:2,costCents:400,restore:40,durationSeconds:1,gameSeconds:30},
 {id:'fastFood',name:'快餐',unlockMapId:2,costCents:900,restore:90,durationSeconds:2,gameSeconds:60},
 {id:'milkTea',name:'奶茶',unlockMapId:3,costCents:700,restore:60,durationSeconds:1,gameSeconds:30},
 {id:'premiumMeal',name:'高档餐食',unlockMapId:4,costCents:1500,restore:100,durationSeconds:1,gameSeconds:30},
].map(item=>Object.freeze(item as V2SupplyItem)));
export const supplyItem=(id:unknown)=>V2_SUPPLY_CATALOG.find(item=>item.id===id);
export const emptySupplyInventory=():Record<V2SupplyId,number>=>({water:0,noodles:0,drink:0,fastFood:0,milkTea:0,premiumMeal:0});
export interface V2SupplyReward {id:string;items:ReadonlyArray<{kind:V2SupplyId;quantity:number}>}
// No approved V2 task reward table exists. A future task implementation must add reviewed
// entries here and verify its own completion before calling the claim event interface.
export const V2_SUPPLY_REWARDS:ReadonlyArray<V2SupplyReward>=Object.freeze([]);
