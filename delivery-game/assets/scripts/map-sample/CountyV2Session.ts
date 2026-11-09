import { createLedger, appendLedger } from '../domain/V2Ledger';
import { V2EconomySession } from '../domain/V2EconomySession';
import { CityData } from './MapTypes';
import { OrderBook } from './OrderBook';
import { VEHICLE_SPEED, VEHICLE_CAPACITY, VEHICLE_INCOME } from './VehicleOwnership';

export const COUNTY_V2_SAVE_KEY='delivery-county-v2-economy-save-v1';
function unpack(serialized:string):string {const v=JSON.parse(serialized);if(v.format!=='county-commit')return serialized;if(v.version!==1)throw new Error('存档版本不受支持');return v.snapshot;}

/** Explicit opt-in facade, separate from the legacy UI and storage key.
 * Fresh economics do not require a map. Legacy routes use the existing OrderBook unchanged.
 */
export class CountyV2Session {
 private constructor(readonly economy:V2EconomySession){}
 static fresh():CountyV2Session {return new CountyV2Session(new V2EconomySession());}
 static restore(serialized:string):CountyV2Session {return new CountyV2Session(V2EconomySession.restore(unpack(serialized)));}
 static migrate(data:CityData,serialized:string):CountyV2Session {
  // Read/validate only. Never writes to a StoragePort, normalizes old funds or awards a migration gift.
  const original=unpack(serialized),book=OrderBook.restore(data,original),raw=JSON.parse(original);
  const snapshot=JSON.parse(new V2EconomySession().serialize()),s=snapshot.state,inventory=book.vehicleInventory;
  s.cashCents=book.player.cashCents;s.ledger=createLedger(s.cashCents,'migration');s.heroCompletedOrders=book.player.completedOrders;s.heroExperience=book.player.experience;
  s.vehicles=inventory.instances.map(v=>({id:v.id,modelId:'legacy',level:1,legacyTier:v.tier,legacySpeedKph:VEHICLE_SPEED[v.tier-1],legacyCapacityKg:VEHICLE_CAPACITY[v.tier-1],legacyIncomeFactor:VEHICLE_INCOME[v.tier-1]}));
  s.riders[0].vehicleId=inventory.playerVehicleId;
  // Original bytes and unknown fields survive; no old tier is re-labelled as the 300-coin new car.
  snapshot.legacyCheckpoint=serialized;snapshot.legacyOriginalCheckpoint=serialized;
  if(raw.active?.mode==='done')s.settledOrderIds.push(raw.active.offer.id);
  return CountyV2Session.restore(JSON.stringify(snapshot));
 }
 serialize():string {return this.economy.serialize();}
 /** Resume only the pre-migration accepted trip. No new legacy offer can enter the V2 wallet. */
 advanceLegacy(data:CityData,seconds:number):void {if(!Number.isFinite(seconds)||seconds<0)throw new Error('时间无效');this.updateLegacy(data,book=>book.advance(seconds));}
 departLegacy(data:CityData):void {this.updateLegacy(data,book=>book.depart());}
 selectLegacyRoute(data:CityData,index:number):void {this.updateLegacy(data,book=>book.select(index));}
 pickupLegacy(data:CityData):void {this.updateLegacy(data,book=>book.pickup());}
 deliverLegacy(data:CityData):void {this.updateLegacy(data,book=>book.deliver());}
 cancelLegacy(data:CityData,afterPickup=false):void {this.updateLegacy(data,book=>afterPickup?book.cancelDelivery():book.cancel());}
 get legacyActive():unknown {const raw=this.legacyCheckpoint;return raw?JSON.parse(unpack(raw)).active:null;}
 settleLegacy(data:CityData,doorAnswer:boolean|null=null):void {this.updateLegacy(data,book=>{book.settle(doorAnswer);});}
 get legacyCheckpoint():string|null {return JSON.parse(this.serialize()).legacyCheckpoint||null;}
 private updateLegacy(data:CityData,action:(book:OrderBook)=>void):void {
  if(!this.economy.hasPendingLegacyTrip)throw new Error('没有迁移前的在途订单');
  const snapshot=JSON.parse(this.serialize()),checkpoint=unpack(snapshot.legacyCheckpoint),old=JSON.parse(checkpoint),book=OrderBook.restore(data,checkpoint);
  action(book);const serialized=book.serialize(),next=JSON.parse(serialized),receipt=book.active?.receipt;
  if(receipt){
   if(next.player.completedOrders!==old.player.completedOrders+1||snapshot.state.settledOrderIds.includes(receipt.orderId))throw new Error('迁移订单结算冲突');
   const cashDelta=next.player.cashCents-old.player.cashCents;
   snapshot.state.cashCents+=cashDelta;
   appendLedger(snapshot.state.ledger,{id:`order:${receipt.orderId}`,category:'legacy_delivery',amountCents:cashDelta,detail:{orderId:receipt.orderId}},null);
   snapshot.state.heroCompletedOrders++;snapshot.state.heroExperience+=next.player.experience-old.player.experience;
   snapshot.state.settledOrderIds.push(receipt.orderId);
   snapshot.state.lastReceipt={id:receipt.orderId,incomeCents:receipt.incomeCents,heroOrderOrdinal:snapshot.state.heroCompletedOrders};
  }
  // Preserve every unknown legacy root field when the known route checkpoint advances.
  const merged={...old,...next};snapshot.legacyCheckpoint=JSON.stringify(merged);
  const validated=V2EconomySession.restore(JSON.stringify(snapshot));
  // Update this facade's session only after full validation. Existing references keep the same object.
  this.economy.replaceFrom(validated.serialize());
 }
}
