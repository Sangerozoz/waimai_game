import { getExperienceLevel } from '../domain/GameConfig';

// County-only tuning. The original dodge game's economy remains unchanged.
export const COUNTY_VEHICLES = Object.freeze([
  Object.freeze({tier:1,name:'D',upgradeFeeCents:0,incomeMultiplier:1,speedMultiplier:1,speedKph:12,capacityKg:5}),
  Object.freeze({tier:2,name:'D+',upgradeFeeCents:20000,incomeMultiplier:1.12,speedMultiplier:1.10,speedKph:13.2,capacityKg:8}),
]);

export function countyExperienceLevel(experience:number):number {
  // Move the first threshold from 100 to 50, preserving every subsequent increment.
  return experience<50?1:getExperienceLevel(experience+50);
}
