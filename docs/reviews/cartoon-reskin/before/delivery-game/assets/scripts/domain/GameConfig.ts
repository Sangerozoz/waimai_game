export type RouteId = 'fast' | 'main' | 'smooth';
export type Phase = 'orders' | 'routes' | 'delivering' | 'arrived' | 'result';
export type Fragility = 'durable' | 'normal' | 'fragile';
export type Damage = 'none' | 'minor' | 'moderate' | 'severe';

export interface Order {
  id: string;
  title: string;
  foodName: string;
  type: 'normal' | 'urgent';
  fragility: Fragility;
  weightKg: number;
  basePriceCents: number;
  deadlineSeconds: number;
  rain: boolean;
  distanceFactor: number;
  destinationIndex: number;
}

export interface Player {
  cashCents: number;
  rating: number;
  experience: number;
  completedOrders: number;
  vehicleTier: number;
  stationLevel: number;
  level: number;
}

export interface RoutePreview {
  id: RouteId;
  name: string;
  description: string;
  durationSeconds: number;
  lateSeconds: number;
  damageChance: number;
  arrivalTemperature: number | null;
}

export interface Receipt {
  orderId: string;
  incomeCents: number;
  ratingDelta: number;
  ratingAfter: number;
  experienceGained: number;
  lateSeconds: number;
  damage: Damage;
  completedOrders: number;
  newCashCents: number;
  summary: string[];
}

export interface SessionState {
  phase: Phase;
  player: Player;
  orders: Order[];
  activeOrder: Order | null;
  activeRoute: RoutePreview | null;
  elapsedSeconds: number;
  receipt: Receipt | null;
  tutorialComplete: boolean;
}

export const GAME_CONFIG = Object.freeze({
  initialCashCents: 10000,
  initialRating: 80,
  orderCount: 5,
  normalDeadlineSeconds: 15,
  urgentDeadlineSeconds: 8,
  urgentFrequency: 0.20,
  fragileFrequency: 0.10,
  experiencePerOrder: 10,
  rainDurationMultiplier: 1.3,
  rainDamageChance: 0.05,
  minimumDurationSeconds: 2,
});

export const VEHICLES = Object.freeze([
  { tier: 1, name: 'D', upgradeFeeCents: 0, incomeMultiplier: 1, speedMultiplier: 1, capacityKg: 5 },
  { tier: 2, name: 'D+', upgradeFeeCents: 32000, incomeMultiplier: 1.12, speedMultiplier: 1.10, capacityKg: 8 },
  { tier: 3, name: 'C', upgradeFeeCents: 50000, incomeMultiplier: 1.25, speedMultiplier: 1.20, capacityKg: 12 },
  { tier: 4, name: 'C+', upgradeFeeCents: 240000, incomeMultiplier: 1.40, speedMultiplier: 1.30, capacityKg: 16 },
  { tier: 5, name: 'B', upgradeFeeCents: 330000, incomeMultiplier: 1.57, speedMultiplier: 1.40, capacityKg: 22 },
  { tier: 6, name: 'B+', upgradeFeeCents: 830000, incomeMultiplier: 1.76, speedMultiplier: 1.50, capacityKg: 28 },
  { tier: 7, name: 'A', upgradeFeeCents: 1070000, incomeMultiplier: 1.97, speedMultiplier: 1.65, capacityKg: 35 },
  { tier: 8, name: 'S', upgradeFeeCents: 3180000, incomeMultiplier: 2.48, speedMultiplier: 2, capacityKg: 60 },
  { tier: 9, name: 'SS', upgradeFeeCents: 5000000, incomeMultiplier: 2.65, speedMultiplier: 2.10, capacityKg: 70 },
  { tier: 10, name: 'SSS', upgradeFeeCents: 7740000, incomeMultiplier: 2.78, speedMultiplier: 2.20, capacityKg: 80 },
].map(vehicle => Object.freeze(vehicle)));

interface RouteDefinition {
  id: RouteId;
  name: string;
  description: string;
  baseSeconds: number;
  damageChance: Readonly<Record<Fragility, number>>;
}

export const ROUTES: readonly RouteDefinition[] = Object.freeze([
  Object.freeze({
    id: 'fast' as RouteId, name: '快捷路', description: '路程短，颠簸较多', baseSeconds: 5,
    damageChance: Object.freeze({ fragile: 0.45, normal: 0.20, durable: 0.08 }),
  }),
  Object.freeze({
    id: 'main' as RouteId, name: '主干道', description: '速度与平稳兼顾', baseSeconds: 10,
    damageChance: Object.freeze({ fragile: 0.25, normal: 0.10, durable: 0.04 }),
  }),
  Object.freeze({
    id: 'smooth' as RouteId, name: '平稳路', description: '路面平稳，耗时较长', baseSeconds: 13,
    damageChance: Object.freeze({ fragile: 0.10, normal: 0.03, durable: 0.01 }),
  }),
]);

export const DAMAGE_EFFECTS = Object.freeze({
  none: Object.freeze({ retainedIncome: 1, ratingDelta: 0, label: '餐品完好' }),
  minor: Object.freeze({ retainedIncome: 0.90, ratingDelta: -2, label: '轻微餐损' }),
  moderate: Object.freeze({ retainedIncome: 0.75, ratingDelta: -5, label: '中度餐损' }),
  severe: Object.freeze({ retainedIncome: 0.50, ratingDelta: -10, label: '严重餐损' }),
});

const EXPERIENCE_THRESHOLDS = Object.freeze([0, 100, 235, 417, 663, 995, 1443, 2048, 2865, 3967]);

export function getExperienceLevel(experience: number): number {
  for (let index = 1; index < EXPERIENCE_THRESHOLDS.length; index++) {
    if (experience < EXPERIENCE_THRESHOLDS[index]) return index;
  }
  let level = EXPERIENCE_THRESHOLDS.length;
  let threshold = EXPERIENCE_THRESHOLDS[EXPERIENCE_THRESHOLDS.length - 1];
  let increment = 1102;
  while (true) {
    increment = Math.round(increment * 1.35);
    threshold += increment;
    if (experience < threshold) return level;
    level++;
  }
}

export function getPlayerIncomeMultiplier(level: number): number {
  return Math.min(1.6, 1 + (level - 1) * 0.03);
}
