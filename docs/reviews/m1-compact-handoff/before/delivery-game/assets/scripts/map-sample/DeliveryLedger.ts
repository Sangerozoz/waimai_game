import { CountyReceipt } from './CountyRules';

export interface DayBilling {
  incomeCents:number;orders:number;good:number;bad:number;late:number;metres:number;onlineMs:number;
}
export interface BillingSnapshot {
  version:1;baselineOrders:number;lastCompletedOrders:number;startedDay:string;legacyStart:boolean;days:Record<string,DayBilling>;
}
export interface BillingView {
  day:string;today:DayBilling;walletCents:number;completedOrders:number;totalIncomeCents:number;highestDailyOrders:number;
  partialToday:boolean;partialHistory:boolean;partialOnline:boolean;
}
const empty=():DayBilling=>({incomeCents:0,orders:0,good:0,bad:0,late:0,metres:0,onlineMs:0});
const two=(n:number):string=>String(100+n).slice(1);
export function localBillingDay(date:Date):string{return `${date.getFullYear()}-${two(date.getMonth()+1)}-${two(date.getDate())}`;}
function canonicalDay(day:string):string {
  const parts=day.split('-').map(Number);return `${parts[0]}-${two(parts[1])}-${two(parts[2])}`;
}
function valid(condition:unknown):asserts condition {if(!condition)throw new Error('存档校验失败：账单');}
function object(value:unknown):value is Record<string,unknown>{return !!value&&typeof value==='object'&&!Array.isArray(value);}
function natural(value:unknown):value is number{return typeof value==='number'&&Number.isSafeInteger(value)&&value>=0;}
function positive(value:unknown):value is number{return typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<=Number.MAX_SAFE_INTEGER;}
function dayKey(day:unknown):day is string {
  if(typeof day!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(day))return false;
  const [y,m,d]=day.split('-').map(Number),date=new Date(y,m-1,d);
  return date.getFullYear()===y&&date.getMonth()===m-1&&date.getDate()===d;
}
export function validateBillingSnapshot(raw:unknown,completedOrders:number):asserts raw is BillingSnapshot {
  valid(object(raw)&&raw.version===1&&natural(raw.baselineOrders)&&raw.baselineOrders<=completedOrders);
  valid(raw.lastCompletedOrders===completedOrders&&dayKey(raw.startedDay)&&typeof raw.legacyStart==='boolean'&&object(raw.days));
  let count=0,income=0;
  for(const key of Object.keys(raw.days)){
    const day=raw.days[key];valid(dayKey(key)&&object(day));
    for(const field of ['incomeCents','orders','good','bad','late','onlineMs'])valid(natural(day[field]));
    valid(positive(day.metres)&&Number(day.good)+Number(day.bad)<=Number(day.orders)&&Number(day.late)<=Number(day.orders));
    if(day.orders===0)valid(day.incomeCents===0&&day.metres===0);
    count+=Number(day.orders);income+=Number(day.incomeCents);valid(natural(count)&&natural(income));
  }
  valid(count===completedOrders-raw.baselineOrders);
}

/** Daily summaries only; the wallet and rewards remain owned by OrderBook. */
export class DeliveryLedger {
  private readonly state:BillingSnapshot;
  constructor(saved:BillingSnapshot|undefined,baselineOrders:number,day:string,legacyStart=false){
    this.state=saved?JSON.parse(JSON.stringify(saved)):{version:1,baselineOrders,lastCompletedOrders:baselineOrders,startedDay:canonicalDay(day),legacyStart,days:{}};
  }
  snapshot():BillingSnapshot{return JSON.parse(JSON.stringify(this.state));}
  recordDelivery(receipt:CountyReceipt,metres:number,day:string):void {
    if(receipt.completedOrders<=this.state.lastCompletedOrders)return;
    if(receipt.completedOrders!==this.state.lastCompletedOrders+1||!positive(metres))throw new Error('账单顺序不一致');
    const key=canonicalDay(day),before=this.state.days[key]||empty();
    const next:DayBilling={...before,incomeCents:before.incomeCents+receipt.incomeCents,orders:before.orders+1,good:before.good+(receipt.ratingDelta>0?1:0),bad:before.bad+(receipt.ratingDelta<0?1:0),late:before.late+(receipt.lateSeconds>0?1:0),metres:before.metres+metres};
    if(!natural(next.incomeCents)||!positive(next.metres))throw new Error('账单数值超出范围');
    this.state.days[key]=next;this.state.lastCompletedOrders=receipt.completedOrders;
  }
  recordOnlineTime(start:number,end:number):void {
    if(!Number.isFinite(start)||!Number.isFinite(end)||end<=start)return;
    let cursor=Math.floor(start);const finish=Math.floor(end);
    while(cursor<finish){
      const date=new Date(cursor),key=localBillingDay(date),midnight=new Date(date.getFullYear(),date.getMonth(),date.getDate()+1).getTime();
      if(!dayKey(key)||!Number.isFinite(midnight)||midnight<=cursor)return;
      const until=Math.min(finish,midnight),day=this.state.days[key]||empty(),onlineMs=day.onlineMs+until-cursor;
      if(!natural(onlineMs))throw new Error('在线时长超出范围');
      this.state.days[key]={...day,onlineMs};cursor=until;
    }
  }
  view(day:string,walletCents:number,completedOrders:number):BillingView {
    const key=canonicalDay(day),today={...(this.state.days[key]||empty())};let totalIncomeCents=0,highestDailyOrders=0;
    for(const d of Object.keys(this.state.days)){const record=this.state.days[d];totalIncomeCents+=record.incomeCents;highestDailyOrders=Math.max(highestDailyOrders,record.orders);}
    const partialHistory=this.state.baselineOrders>0;
    return {day:key,today,walletCents,completedOrders,totalIncomeCents,highestDailyOrders,partialHistory,partialToday:partialHistory&&key<=this.state.startedDay,partialOnline:this.state.legacyStart&&key<=this.state.startedDay};
  }
}
