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
 reset():void{this.previous=null;}
 frame():number {
  const now=typeof performance!=='undefined'?performance.now():NaN;
  const delta=this.previous===null?0:Math.max(0,(now-this.previous)/1000);
  this.previous=Number.isFinite(now)?now:null;
  return Number.isFinite(delta)?delta:0;
 }
}
