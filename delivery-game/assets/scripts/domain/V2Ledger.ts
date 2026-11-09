/** Integer-cent cash ledger. Dates are supplied by the host, never inferred from order IDs. */
export const V2_LEDGER_CATEGORIES = ['hero_ordinary','hero_special','npc_delivery','vehicle_purchase','rider_hire','vehicle_upgrade','rider_upgrade','map_purchase','supply_purchase','legacy_delivery'] as const;
export type V2LedgerCategory = typeof V2_LEDGER_CATEGORIES[number];
export interface V2LedgerContext { nowMs:number; dayKey:string|null }
export interface V2LedgerDetail { orderId?:string; vehicleId?:string; modelId?:number; riderId?:string; mapId?:number; level?:number; supplyId?:string; quantity?:number; transactionId?:string }
export interface V2SupplyChargeDetail { supplyId?:string; quantity?:number; transactionId?:string }
export interface V2LedgerEntry { id:string; category:V2LedgerCategory; amountCents:number; atMs:number|null; dayKey:string|null; detail:V2LedgerDetail }
export interface V2Ledger { opening:{id:'opening';balanceCents:number;atMs:null;dayKey:null;source:'initial'|'migration'}; entries:V2LedgerEntry[]; nextId:number }
export interface V2LedgerQuery { todayDayKey:string; recentDayKeys:string[] }
export interface V2LedgerTotals { incomeCents:number; expenseCents:number; netCents:number; byCategory:Record<V2LedgerCategory,number> }
function check(ok:unknown):asserts ok {if(!ok)throw new Error('账本校验失败');}
const integer=(n:unknown):n is number=>typeof n==='number'&&Number.isSafeInteger(n);
export function validLedgerDay(key:unknown):key is string {
 if(typeof key!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(key))return false;
 const d=new Date(`${key}T00:00:00.000Z`);return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===key;
}
export function validateLedgerContext(context:unknown):asserts context is V2LedgerContext|null {
 if(context===null)return;const c=context as V2LedgerContext;check(!!c&&integer(c.nowMs)&&c.nowMs>=0&&(c.dayKey===null||validLedgerDay(c.dayKey)));
}
export function createLedger(balanceCents:number,source:'initial'|'migration'):V2Ledger {
 check(integer(balanceCents)&&balanceCents>=0);return {opening:{id:'opening',balanceCents,atMs:null,dayKey:null,source},entries:[],nextId:1};
}
export function ledgerBalance(ledger:V2Ledger):number {let balance=ledger.opening.balanceCents;for(const e of ledger.entries){balance+=e.amountCents;check(integer(balance)&&balance>=0);}return balance;}
export function validateLedger(value:unknown,cashCents:number):asserts value is V2Ledger {
 const l=value as V2Ledger;check(!!l&&!!l.opening&&l.opening.id==='opening'&&integer(l.opening.balanceCents)&&l.opening.balanceCents>=0&&l.opening.atMs===null&&l.opening.dayKey===null&&['initial','migration'].includes(l.opening.source)&&Array.isArray(l.entries)&&integer(l.nextId)&&l.nextId>=1);
 const ids=new Set<string>();let maxId=0;
 for(const e of l.entries){check(!!e&&typeof e.id==='string'&&e.id.length>0&&e.id.length<=240&&!ids.has(e.id));ids.add(e.id);
  check(V2_LEDGER_CATEGORIES.includes(e.category)&&integer(e.amountCents)&&!!e.detail&&typeof e.detail==='object'&&!Array.isArray(e.detail));
  const income=['hero_ordinary','hero_special','npc_delivery','legacy_delivery'].includes(e.category);check(income?e.amountCents>=0:e.amountCents<0);
  check(e.atMs===null?e.dayKey===null:integer(e.atMs)&&e.atMs>=0&&(e.dayKey===null||validLedgerDay(e.dayKey)));
  if(/^transaction:[1-9]\d*$/.test(e.id))maxId=Math.max(maxId,Number(e.id.slice(12)));
 }check(l.nextId>maxId&&ledgerBalance(l)===cashCents);
}
export function appendLedger(ledger:V2Ledger,entry:{id?:string;category:V2LedgerCategory;amountCents:number;detail?:V2LedgerDetail},context:V2LedgerContext|null):void {
 validateLedgerContext(context);const id=entry.id||`transaction:${ledger.nextId++}`;check(!ledger.entries.some(e=>e.id===id));
 ledger.entries.push({id,category:entry.category,amountCents:entry.amountCents,atMs:context?.nowMs??null,dayKey:context?.dayKey??null,detail:{...entry.detail}});
}
function totals(entries:V2LedgerEntry[]):V2LedgerTotals {
 const byCategory={} as Record<V2LedgerCategory,number>;for(const c of V2_LEDGER_CATEGORIES)byCategory[c]=0;
 let incomeCents=0,expenseCents=0;for(const e of entries){byCategory[e.category]+=e.amountCents;if(e.amountCents>=0)incomeCents+=e.amountCents;else expenseCents-=e.amountCents;check(integer(incomeCents)&&integer(expenseCents)&&integer(byCategory[e.category]));}
 return {incomeCents,expenseCents,netCents:incomeCents-expenseCents,byCategory};
}
export function summarizeLedger(ledger:V2Ledger,query:V2LedgerQuery) {
 check(validLedgerDay(query.todayDayKey)&&Array.isArray(query.recentDayKeys)&&query.recentDayKeys.length<=7&&query.recentDayKeys.every(validLedgerDay)&&new Set(query.recentDayKeys).size===query.recentDayKeys.length);
 return {today:totals(ledger.entries.filter(e=>e.dayKey===query.todayDayKey)),recentSevenDays:totals(ledger.entries.filter(e=>e.dayKey!==null&&query.recentDayKeys.includes(e.dayKey))),cumulative:totals(ledger.entries),unknownDate:totals(ledger.entries.filter(e=>e.dayKey===null)),opening:{...ledger.opening},reconciliation:{expectedCashCents:ledgerBalance(ledger)}};
}
