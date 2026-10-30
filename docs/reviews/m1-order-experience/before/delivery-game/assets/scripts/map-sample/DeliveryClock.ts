export interface DeliveryTiming { displaySeconds:number; animationSeconds:number }
export interface DeliveryProgress extends DeliveryTiming {
  progress:number; routeElapsedSeconds:number; routeElapsedMetres:number; remainingSeconds:number;
}

export const PICKUP_STOP_SECONDS=2;

// Pickup waiting consumes real time separately from movement along the road.
export function advancePickupClock(elapsed:number,pickupWaitElapsed:number,delta:number,pickupAt:number,animationSeconds:number):{elapsed:number;pickupWaitElapsed:number} {
  if(!Number.isFinite(delta)||delta<=0)return {elapsed,pickupWaitElapsed};
  if(elapsed<pickupAt){
    const movement=Math.min(delta,pickupAt-elapsed);
    elapsed+=movement;
    delta-=movement;
  }
  if(elapsed>=pickupAt&&pickupWaitElapsed<PICKUP_STOP_SECONDS){
    const waiting=Math.min(delta,PICKUP_STOP_SECONDS-pickupWaitElapsed);
    pickupWaitElapsed+=waiting;
    delta-=waiting;
  }
  return {elapsed:Math.min(animationSeconds,elapsed+delta),pickupWaitElapsed};
}

export function animationSecondsFor(displaySeconds:number):number {
  if(!Number.isFinite(displaySeconds)||displaySeconds<0)throw new RangeError('Invalid delivery time');
  return Math.min(15,displaySeconds/180);
}

export function deliveryTiming(distanceMetres:number,speedKph=12):DeliveryTiming {
  if(!Number.isFinite(distanceMetres)||distanceMetres<0)throw new RangeError('Invalid road distance');
  if(!Number.isFinite(speedKph)||speedKph<=0)throw new RangeError('Invalid vehicle speed');
  const displaySeconds=distanceMetres*3.6/speedKph;
  return {displaySeconds,animationSeconds:animationSecondsFor(displaySeconds)};
}

export function deliveryProgress(distanceMetres:number,elapsedAnimation:number,speedKph=12):DeliveryProgress {
  const timing=deliveryTiming(distanceMetres,speedKph);
  const progress=timing.animationSeconds===0?1:Math.max(0,Math.min(1,elapsedAnimation/timing.animationSeconds));
  return {...timing,progress,routeElapsedSeconds:timing.displaySeconds*progress,routeElapsedMetres:distanceMetres*progress,remainingSeconds:timing.displaySeconds*(1-progress)};
}

// Frozen pre-revision clock, used only to validate and continue existing deliveries.
export function legacyDeliveryTiming(travelSeconds:number,speedMultiplier:number):DeliveryTiming {
  const displaySeconds=Math.ceil((8*60+travelSeconds*1.6/speedMultiplier)/60)*60;
  return {displaySeconds,animationSeconds:Math.min(12,displaySeconds/360)};
}

export function formatDeliveryTime(seconds:number):string {
  const minutes=Math.ceil(Math.max(0,seconds)/60);
  return minutes<60?`${minutes}分钟`:`${Math.floor(minutes/60)}小时${minutes%60?`${minutes%60}分`:''}`;
}

export function formatRemaining(seconds:number):string {
  const whole=Math.ceil(Math.max(0,seconds)),s=String(whole%60+100).slice(1),m=String(Math.floor(whole/60)%60+100).slice(1);
  return whole>=3600?`${Math.floor(whole/3600)}:${m}:${s}`:`${m}:${s}`;
}
