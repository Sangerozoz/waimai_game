import { DeliveryTiming } from './DeliveryClock';
/** Frozen profile identifier. Changing these values requires a new profile. */
export const LEGACY_TRIP_PROFILE='m2-120-service60-v1';
export const TRIP_PROFILE='m2-40-service60-v2';
export type TripProfile=typeof LEGACY_TRIP_PROFILE|typeof TRIP_PROFILE;
export function isTripProfile(value:unknown):value is TripProfile{return value===LEGACY_TRIP_PROFILE||value===TRIP_PROFILE;}
export function tripTiming(metres:number,speedKph:number,profile:TripProfile=TRIP_PROFILE):DeliveryTiming {
 if(!Number.isFinite(metres)||metres<0||!Number.isFinite(speedKph)||speedKph<=0)throw new Error('无效行程');
 if(!isTripProfile(profile))throw new Error('未知行程时钟版本');
 const road=metres*3.6/speedKph,rate=profile===LEGACY_TRIP_PROFILE?120:40;
 return {displaySeconds:road+60,animationSeconds:road/rate};
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
 static readonly TAU=.25;
 private target=1;
 private value=1;
 private queued:number[]=[];
 private recent:number[]=[];
 get multiplier():number{return this.value;}
 reset():void{this.target=1;this.value=1;this.queued=[];this.recent=[];}
 click(time:number):boolean {
  if(!Number.isFinite(time))return false;
  if(this.target+this.queued.length*.5>=ClickBoost.MAX)return false;
  this.recent=this.recent.filter(t=>time-t<1);
  if(this.recent.length>=8)return false;
  this.recent.push(time);this.queued.push(time);return true;
 }
 /** Analytic integral of actual speed, following a piecewise linear target. */
 integrate(seconds:number,end:number):number {
  if(!Number.isFinite(seconds)||seconds<=0)return 0;
  let cursor=end-seconds,area=0;
  const follow=(duration:number,slope:number)=>{
   const tau=ClickBoost.TAU,oneMinus=-Math.expm1(-duration/tau);
   const initial=this.value,target=this.target;
   area+=target*duration+slope*(duration*duration/2-tau*duration)+(initial-target+slope*tau)*tau*oneMinus;
   this.value=Math.max(1,Math.min(ClickBoost.MAX,initial+(target-initial)*oneMinus+slope*(duration-tau*oneMinus)));
   this.target=Math.max(1,target+slope*duration);
  };
  const decay=(duration:number)=>{
   const falling=Math.min(duration,Math.max(0,(this.target-1)/1.5));
   if(falling>0)follow(falling,-1.5);
   if(duration>falling){this.target=1;follow(duration-falling,0);}
  };
  while(this.queued.length&&this.queued[0]<=end){
   const at=Math.max(cursor,this.queued.shift()!);decay(at-cursor);cursor=at;
   this.target=Math.min(ClickBoost.MAX,this.target+.5);
  }
  decay(end-cursor);return area;
 }
}
