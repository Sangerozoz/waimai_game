/** Explicit load units. Parsing never converts or rounds legacy kilograms into slots. */
export type V2Load=Readonly<{version:'kg-v1';weightKg:number}>|Readonly<{version:'slots-v1';occupiedSlots:1|2}>;
export type V2Capacity=Readonly<{version:'kg-v1';capacityKg:number}>|Readonly<{version:'slots-v1';capacitySlots:number}>;
export type V2SlotLoad=Extract<V2Load,{version:'slots-v1'}>;
export type V2SlotCapacity=Extract<V2Capacity,{version:'slots-v1'}>;

function check(value:unknown):asserts value {if(!value)throw new Error('配送容量单位或条款无效');}
function record(raw:unknown,keys:readonly string[]):Record<string,unknown> {
 check(raw&&typeof raw==='object'&&!Array.isArray(raw));
 check(Reflect.ownKeys(raw).length===keys.length&&keys.every(key=>Object.prototype.propertyIsEnumerable.call(raw,key)));
 return raw as Record<string,unknown>;
}
function positive(raw:unknown):raw is number {return typeof raw==='number'&&Number.isFinite(raw)&&raw>0;}

export function parseV2Load(raw:unknown):V2Load {
 check(raw&&typeof raw==='object'&&!Array.isArray(raw));
 const version=(raw as {version?:unknown}).version;
 if(version==='kg-v1'){const value=record(raw,['version','weightKg']);check(positive(value.weightKg));return {version,weightKg:value.weightKg};}
 check(version==='slots-v1');const value=record(raw,['version','occupiedSlots']);
 check(value.occupiedSlots===1||value.occupiedSlots===2);return {version,occupiedSlots:value.occupiedSlots};
}

export function parseV2Capacity(raw:unknown):V2Capacity {
 check(raw&&typeof raw==='object'&&!Array.isArray(raw));
 const version=(raw as {version?:unknown}).version;
 if(version==='kg-v1'){const value=record(raw,['version','capacityKg']);check(positive(value.capacityKg));return {version,capacityKg:value.capacityKg};}
 check(version==='slots-v1');const value=record(raw,['version','capacitySlots']);
 check(typeof value.capacitySlots==='number'&&Number.isSafeInteger(value.capacitySlots)&&value.capacitySlots>0);
 return {version,capacitySlots:value.capacitySlots};
}

/** Canonical deterministic portion for a validated order identity; consumes no draw. */
export function slotLoadForOrderId(orderId:string):V2SlotLoad {
 check(typeof orderId==='string'&&orderId.length>0&&orderId.length<=200);
 let hash=2166136261;for(let i=0;i<orderId.length;i++)hash=Math.imul(hash^orderId.charCodeAt(i),16777619)>>>0;
 return {version:'slots-v1',occupiedSlots:(hash&1)===0?1:2};
}

export function sameV2Load(left:V2Load,right:V2Load):boolean {
 return left.version===right.version&&(left.version==='kg-v1'?left.weightKg===(right as Extract<V2Load,{version:'kg-v1'}>).weightKg:left.occupiedSlots===(right as V2SlotLoad).occupiedSlots);
}

export function totalV2Load(loads:readonly V2Load[],capacity:V2Capacity):number {
 const limit=parseV2Capacity(capacity);let total=0;
 for(const raw of loads){const load=parseV2Load(raw);check(load.version===limit.version);total+=load.version==='kg-v1'?load.weightKg:load.occupiedSlots;check(Number.isFinite(total)&&(load.version==='kg-v1'||Number.isSafeInteger(total)));}
 return total;
}

export function fitsV2Capacity(loads:readonly V2Load[],capacity:V2Capacity):boolean {
 const limit=parseV2Capacity(capacity),total=totalV2Load(loads,limit);
 return total<=(limit.version==='kg-v1'?limit.capacityKg:limit.capacitySlots);
}

/** Read batch size, not a holding limit or a promise of available orders. */
export function slotCandidateRequestCount(capacitySlots:number):number {
 check(Number.isSafeInteger(capacitySlots)&&capacitySlots>0);
 return Math.min(50,Math.max(8,2*capacitySlots));
}
/** A separate finite NPC pool. Skipping an oversized offer never rerolls it. */
export function slotFleetOrderIds(batchId:number,capacitySlots:number):string[] {
 check(Number.isSafeInteger(batchId)&&batchId>0);const count=slotCandidateRequestCount(capacitySlots),ids:string[]=[];let remaining=capacitySlots;
 for(let index=0;index<count&&remaining>0;index++){
  const id=`fleet-${batchId}-${index}`,load=slotLoadForOrderId(id);if(load.occupiedSlots>remaining)continue;
  ids.push(id);remaining-=load.occupiedSlots;
 }
 return ids;
}
