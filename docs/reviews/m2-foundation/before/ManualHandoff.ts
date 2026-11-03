/** The player's decisions are explicit boundaries; no frame may cross one. */
export type HandoffPhase='planning'|'toPickup'|'awaitPickup'|'picking'|'awaitDeliveryStart'|'toDropoff'|'arrived';
export interface HandoffState {version:1;phase:HandoffPhase;elapsed:number;serviceElapsed:number}
function requirePhase(state:HandoffState,phase:HandoffPhase):void {
 if(state.phase!==phase)throw new Error('当前阶段不能执行此操作');
}
export function beginTrip(state:HandoffState,pickupAt:number):HandoffState {
 requirePhase(state,'planning');if(!Number.isFinite(pickupAt)||pickupAt<0)throw new Error('无效取餐位置');
 return {...state,phase:pickupAt===0?'awaitPickup':'toPickup'};
}
export function startPickup(state:HandoffState):HandoffState {
 requirePhase(state,'awaitPickup');return {...state,phase:'picking'};
}
export function startDelivery(state:HandoffState):HandoffState {
 requirePhase(state,'awaitDeliveryStart');return {...state,phase:'toDropoff'};
}
export function advanceHandoff(state:HandoffState,delta:number,pickupAt:number,total:number):HandoffState {
 if(!Number.isFinite(delta)||delta<=0)return state;
 if(!Number.isFinite(pickupAt)||!Number.isFinite(total)||pickupAt<0||pickupAt>total)throw new Error('无效路线时间');
 if(state.phase==='toPickup'){
  const elapsed=Math.min(pickupAt,state.elapsed+delta);return {...state,elapsed,phase:elapsed>=pickupAt?'awaitPickup':'toPickup'};
 }
 if(state.phase==='picking'){
  const serviceElapsed=Math.min(2,state.serviceElapsed+delta);return {...state,serviceElapsed,phase:serviceElapsed>=2?'awaitDeliveryStart':'picking'};
 }
 if(state.phase==='toDropoff'){
  const elapsed=Math.min(total,state.elapsed+delta);return {...state,elapsed,phase:elapsed>=total?'arrived':'toDropoff'};
 }
 return state;
}

/** Reject malformed persisted phases before any state can be resumed. */
export function validateHandoff(value:unknown,pickupAt:number,total:number):asserts value is HandoffState {
 if(!value||typeof value!=='object'||Array.isArray(value)||!Number.isFinite(pickupAt)||!Number.isFinite(total)||pickupAt<0||pickupAt>=total)throw new Error('无效的取送状态');
 const s=value as Partial<HandoffState>;
 if(s.version!==1||!Number.isFinite(s.elapsed)||!Number.isFinite(s.serviceElapsed)||s.elapsed!<0||s.elapsed!>total||s.serviceElapsed!<0||s.serviceElapsed!>2)throw new Error('无效的取送进度');
 const at=Math.abs(s.elapsed!-pickupAt)<1e-8,done=s.serviceElapsed===2;
 const valid=s.phase==='planning'?s.elapsed===0&&s.serviceElapsed===0:
  s.phase==='toPickup'?s.elapsed!<pickupAt&&s.serviceElapsed===0:
  s.phase==='awaitPickup'?at&&s.serviceElapsed===0:
  s.phase==='picking'?at&&s.serviceElapsed!<2:
  s.phase==='awaitDeliveryStart'?at&&done:
  s.phase==='toDropoff'?s.elapsed!>=pickupAt&&s.elapsed!<total&&done:
  s.phase==='arrived'?s.elapsed===total&&done:false;
 if(!valid)throw new Error('取送阶段与进度不一致');
}
