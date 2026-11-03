import { DeliveryTiming } from './DeliveryClock';
/** Frozen profile identifier. Changing these values requires a new profile. */
export const TRIP_PROFILE='m2-120-service60-v1';
export function tripTiming(metres:number,speedKph:number):DeliveryTiming {
 if(!Number.isFinite(metres)||metres<0||!Number.isFinite(speedKph)||speedKph<=0)throw new Error('无效行程');
 const road=metres*3.6/speedKph;
 return {displaySeconds:road+60,animationSeconds:road/120};
}
export function travelDelta(realSeconds:number,multiplier=1):number {
 if(!Number.isFinite(realSeconds)||realSeconds<=0)return 0;
 if(!Number.isFinite(multiplier)||multiplier<1||multiplier>4)throw new Error('无效行驶倍率');
 return realSeconds*multiplier;
}

/** Monotonic foreground intervals. Background/resume and pending commits reset the origin. */
export class ForegroundClock {
 private previous:number|null=null;
 get time():number{return this.previous===null?0:this.previous/1000;}
 reset():void{this.previous=null;}
 frame():number {
  const now=typeof performance!=='undefined'?performance.now():NaN;
  const delta=this.previous===null?0:Math.max(0,(now-this.previous)/1000);
  this.previous=Number.isFinite(now)?now:null;
  return Number.isFinite(delta)?delta:0;
 }
}

/** Ephemeral input only: timestamps share the foreground performance clock. */
export class ClickBoost {
 static readonly MAX=10/3;
 private value=1;
 private queued:number[]=[];
 private recent:number[]=[];
 get multiplier():number{return this.value;}
 reset():void{this.value=1;this.queued=[];this.recent=[];}
 click(time:number):boolean {
  if(!Number.isFinite(time))return false;
  this.recent=this.recent.filter(t=>time-t<1);
  if(this.recent.length>=8)return false;
  this.recent.push(time);this.queued.push(time);return true;
 }
 /** Integral of B(t), splitting at each click and where decay reaches one. */
 integrate(seconds:number,end:number):number {
  if(!Number.isFinite(seconds)||seconds<=0)return 0;
  let cursor=end-seconds,area=0;
  const decay=(duration:number)=>{
   const boosted=Math.min(duration,(this.value-1)/1.5);
   area+=duration+(this.value-1)*boosted-.75*boosted*boosted;
   this.value=Math.max(1,this.value-1.5*duration);
  };
  while(this.queued.length&&this.queued[0]<=end){
   const at=Math.max(cursor,this.queued.shift()!);decay(at-cursor);cursor=at;
   this.value=Math.min(ClickBoost.MAX,this.value+.5);
  }
  decay(end-cursor);return area;
 }
}
