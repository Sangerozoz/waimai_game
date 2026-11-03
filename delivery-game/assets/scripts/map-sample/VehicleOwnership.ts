export interface VehicleInstance {id:string;tier:number}
export interface VehicleInventory {version:1;nextId:number;playerVehicleId:string;instances:VehicleInstance[];vehicleQualifications:{s:boolean;ss:boolean;sss:boolean}}
export const VEHICLE_GRADES=['D','D+','C','C+','B','B+','A','S','SS','SSS'];
export const VEHICLE_NAMES=['旧电动车','翻新电动车','品牌电动车','长续航电动车','大箱摩托车','运动摩托车','豪华摩托车','限量豪华摩托车','黄金限量摩托车','至尊飞行摩托车'];
export const VEHICLE_LIMITS=[11,11,11,11,11,11,11,4,3,2];
export const VEHICLE_SPEED=[12,13.2,14.4,15.6,16.8,18,19.8,24,25.2,26.4];
export const VEHICLE_CAPACITY=[5,8,12,16,22,28,35,60,70,80];
export const VEHICLE_INCOME=[1,1.12,1.25,1.4,1.57,1.76,1.97,2.48,2.65,2.78];
export const VEHICLE_PRICE=[50000,70000,120000,360000,690000,1520000,2590000,5770000,10770000,18510000];
export function initialInventory(tier:number):VehicleInventory{return {version:1,nextId:2,playerVehicleId:'vehicle-1',instances:[{id:'vehicle-1',tier}],vehicleQualifications:{s:false,ss:false,sss:false}};}
export function validateVehicleInventory(raw:unknown,tier:number):asserts raw is VehicleInventory {
 const fail=()=>{throw new Error('存档校验失败：车辆库存');};
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return fail();const v=raw as VehicleInventory;
 if(v.version!==1||!Number.isSafeInteger(v.nextId)||v.nextId<2||!Array.isArray(v.instances)||!v.instances.length||!v.vehicleQualifications||typeof v.vehicleQualifications!=='object')return fail();
 if(!['s','ss','sss'].every(k=>typeof (v.vehicleQualifications as unknown as Record<string,unknown>)[k]==='boolean'))return fail();
 const ids=new Set<string>(),counts=Array(10).fill(0);let max=0;
 for(const a of v.instances){if(!a||typeof a.id!=='string'||!/^vehicle-[1-9]\d*$/.test(a.id)||!Number.isSafeInteger(a.tier)||a.tier<1||a.tier>10||ids.has(a.id))return fail();const n=Number(a.id.slice(8));if(!Number.isSafeInteger(n))return fail();ids.add(a.id);max=Math.max(max,n);if(++counts[a.tier-1]>VEHICLE_LIMITS[a.tier-1])return fail();}
 const selected=v.instances.find(a=>a.id===v.playerVehicleId);if(!selected||selected.tier!==tier||v.nextId<=max)return fail();
}
