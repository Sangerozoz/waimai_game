import {
  Damage, DAMAGE_EFFECTS, Fragility, GAME_CONFIG, getExperienceLevel,
  getPlayerIncomeMultiplier, Order, Phase, Receipt, RouteId, RoutePreview, ROUTES,
  SessionState, VEHICLES,
} from './GameConfig';

const SAVE_VERSION = 1;

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

function routePreviews(order: Order, vehicleTier: number): RoutePreview[] {
  const vehicle = VEHICLES[vehicleTier - 1];
  return ROUTES.map(route => {
    // T01 has no vehicle strengthening or arrival-temperature demand.
    const durationSeconds = Math.max(GAME_CONFIG.minimumDurationSeconds,
      route.baseSeconds * order.distanceFactor * (order.rain ? GAME_CONFIG.rainDurationMultiplier : 1)
      / vehicle.speedMultiplier);
    return {
      id: route.id, name: route.name, description: route.description, durationSeconds,
      lateSeconds: Math.max(0, durationSeconds - order.deadlineSeconds),
      damageChance: route.damageChance[order.fragility] + (order.rain ? GAME_CONFIG.rainDamageChance : 0),
      arrivalTemperature: null,
    };
  });
}

function firstOrder(): Order {
  return {
    id: 'order-1', title: '第一单 · 送到街角', foodName: '家常饭盒', type: 'normal',
    fragility: 'durable', weightKg: 1, basePriceCents: 2000, deadlineSeconds: 15,
    rain: false, distanceFactor: 1, destinationIndex: 0,
  };
}

export class DeliverySession {
  private state: SessionState;
  private fixedDamage: Damage | null = null;
  private sequence = 1;
  private readonly rng: () => number;

  constructor(rng: () => number = Math.random) {
    this.rng = rng;
    this.state = {
      phase: 'orders',
      player: {
        cashCents: GAME_CONFIG.initialCashCents, rating: GAME_CONFIG.initialRating,
        experience: 0, completedOrders: 0, vehicleTier: 1, stationLevel: 1, level: 1,
      },
      orders: [firstOrder()], activeOrder: null, activeRoute: null,
      elapsedSeconds: 0, receipt: null, tutorialComplete: false,
    };
  }

  static restore(serialized: string, rng: () => number = Math.random): DeliverySession {
    let saved: unknown;
    try {
      saved = JSON.parse(serialized);
    } catch {
      throw new Error('Invalid delivery save: JSON could not be read');
    }
    validateSave(saved);
    const restored = new DeliverySession(rng);
    restored.state = clone(saved.state);
    restored.fixedDamage = saved.fixedDamage;
    restored.sequence = saved.sequence;
    return restored;
  }

  getState(): SessionState {
    return clone(this.state);
  }

  acceptOrder(orderId: string): void {
    this.requirePhase('orders');
    const index = this.state.orders.findIndex(order => order.id === orderId);
    if (index < 0) throw new Error('Order is not available');
    const order = this.state.orders[index];
    if (order.weightKg > VEHICLES[this.state.player.vehicleTier - 1].capacityKg) {
      throw new Error('Order exceeds vehicle capacity');
    }
    this.state.activeOrder = order;
    this.state.orders.splice(index, 1);
    this.state.phase = 'routes';
  }

  previewRoutes(): RoutePreview[] {
    return this.state.activeOrder ? routePreviews(this.state.activeOrder, this.state.player.vehicleTier) : [];
  }

  depart(routeId: RouteId): void {
    this.requirePhase('routes');
    const route = this.previewRoutes().find(candidate => candidate.id === routeId);
    if (!route) throw new Error('Unknown route');
    // Exactly one probability roll; severity is sampled only if damage occurs.
    let damage: Damage = 'none';
    if (this.random() < route.damageChance) {
      const severity = this.random();
      damage = severity < 0.70 ? 'minor' : severity < 0.95 ? 'moderate' : 'severe';
    }
    this.fixedDamage = damage;
    this.state.activeRoute = route;
    this.state.elapsedSeconds = 0;
    this.state.phase = 'delivering';
  }

  advance(seconds: number): void {
    if (this.state.phase !== 'delivering' || !Number.isFinite(seconds) || seconds < 0) return;
    const duration = this.state.activeRoute!.durationSeconds;
    this.state.elapsedSeconds = Math.min(duration, this.state.elapsedSeconds + seconds);
    if (this.state.elapsedSeconds >= duration) this.state.phase = 'arrived';
  }

  settle(): Receipt {
    if (this.state.phase === 'result') return clone(this.state.receipt!);
    this.requirePhase('arrived');
    const order = this.state.activeOrder!;
    const route = this.state.activeRoute!;
    const player = this.state.player;
    const damage = this.fixedDamage!;
    const effect = DAMAGE_EFFECTS[damage];
    const late = route.durationSeconds > order.deadlineSeconds;
    const ratingDelta = clamp(effect.ratingDelta + (late ? -3 : order.type === 'urgent' ? 2 : 0), -10, 6);
    const ratingAfter = clamp(player.rating + ratingDelta, 20, 100);
    // Award XP only after income uses the departure/current player level.
    const incomeCents = Math.round(order.basePriceCents * VEHICLES[player.vehicleTier - 1].incomeMultiplier
      * getPlayerIncomeMultiplier(player.level) * (0.85 + ratingAfter * 0.003) * effect.retainedIncome);
    const newCashCents = player.cashCents + incomeCents;
    const experience = player.experience + GAME_CONFIG.experiencePerOrder;
    const completedOrders = player.completedOrders + 1;
    if (![incomeCents, newCashCents, experience, completedOrders].every(Number.isSafeInteger)) {
      throw new Error('Delivery totals exceed safe numeric limits');
    }
    const receipt: Receipt = {
      orderId: order.id, incomeCents, ratingDelta, ratingAfter,
      experienceGained: GAME_CONFIG.experiencePerOrder, lateSeconds: route.lateSeconds,
      damage, completedOrders, newCashCents,
      summary: [
        late ? `晚到 ${route.lateSeconds.toFixed(1)} 秒，评价 -3` : order.type === 'urgent' ? '加急准时，评价 +2' : '准时送达',
        effect.label, `获得 ${GAME_CONFIG.experiencePerOrder} 点经验`,
      ],
    };
    player.rating = ratingAfter;
    player.cashCents = newCashCents;
    player.experience = experience;
    player.level = getExperienceLevel(experience);
    player.completedOrders = completedOrders;
    this.state.receipt = receipt;
    this.state.phase = 'result';
    return clone(receipt);
  }

  returnToOrders(): void {
    this.requirePhase('result');
    this.state.tutorialComplete = true;
    this.state.activeOrder = null;
    this.state.activeRoute = null;
    this.state.receipt = null;
    this.state.elapsedSeconds = 0;
    this.fixedDamage = null;
    while (this.state.orders.length < GAME_CONFIG.orderCount) this.state.orders.push(this.generateOrder());
    this.state.phase = 'orders';
  }

  serialize(): string {
    return JSON.stringify({ version: SAVE_VERSION, state: this.state, fixedDamage: this.fixedDamage, sequence: this.sequence });
  }

  private requirePhase(phase: Phase): void {
    if (this.state.phase !== phase) throw new Error(`Expected ${phase} phase; current phase is ${this.state.phase}`);
  }

  private random(): number {
    const value = this.rng();
    return Number.isFinite(value) ? clamp(value, 0, 1 - Number.EPSILON) : 0.99;
  }

  private generateOrder(): Order {
    const urgent = this.random() < GAME_CONFIG.urgentFrequency;
    const fragilityRoll = this.random();
    const fragility: Fragility = fragilityRoll < GAME_CONFIG.fragileFrequency ? 'fragile'
      : fragilityRoll < 0.55 ? 'normal' : 'durable';
    const foodName = fragility === 'fragile' ? '鲜汤面' : fragility === 'durable' ? '家常饭盒' : '小炒套餐';
    // County weights are capped by capacity without rejection sampling, including a degenerate RNG.
    const weightKg = 1 + Math.floor(this.random() * Math.min(5, VEHICLES[this.state.player.vehicleTier - 1].capacityKg));
    const order: Order = {
      id: `order-${++this.sequence}`, title: urgent ? '加急配送' : '街坊订单', foodName,
      type: urgent ? 'urgent' : 'normal', fragility, weightKg,
      basePriceCents: 1500 + Math.floor(this.random() * 1001),
      deadlineSeconds: urgent ? GAME_CONFIG.urgentDeadlineSeconds : GAME_CONFIG.normalDeadlineSeconds,
      rain: false, distanceFactor: 1, destinationIndex: Math.floor(this.random() * 5),
    };
    const fastest = routePreviews(order, this.state.player.vehicleTier)[0].durationSeconds;
    order.deadlineSeconds = Math.max(order.deadlineSeconds, fastest);
    return order;
  }
}

interface SavedSession {
  version: number;
  state: SessionState;
  fixedDamage: Damage | null;
  sequence: number;
}

function valid(condition: unknown, detail: string): asserts condition {
  if (!condition) throw new Error(`Invalid delivery save: ${detail}`);
}

function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function finite(value: unknown, minimum: number, maximum = Number.MAX_SAFE_INTEGER): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value >= minimum && value <= maximum;
}

function integer(value: unknown, minimum: number, maximum = Number.MAX_SAFE_INTEGER): value is number {
  return finite(value, minimum, maximum) && Number.isSafeInteger(value);
}

function damageValue(value: unknown): value is Damage {
  return value === 'none' || value === 'minor' || value === 'moderate' || value === 'severe';
}

function validateOrder(value: unknown): asserts value is Order {
  valid(object(value), 'order must be an object');
  for (const key of ['id', 'title', 'foodName']) valid(typeof value[key] === 'string' && value[key].length > 0, `order ${key}`);
  valid(value.type === 'normal' || value.type === 'urgent', 'order type');
  valid(value.fragility === 'normal' || value.fragility === 'durable' || value.fragility === 'fragile', 'order fragility');
  valid(finite(value.weightKg, 0.5, 80), 'order weight');
  valid(integer(value.basePriceCents, 1), 'order price');
  valid(finite(value.deadlineSeconds, 2), 'order deadline');
  valid(typeof value.rain === 'boolean', 'order rain');
  valid(finite(value.distanceFactor, Number.MIN_VALUE, 100), 'order distance');
  valid(integer(value.destinationIndex, 0, 4), 'order destination');
}

function validateSave(value: unknown): asserts value is SavedSession {
  valid(object(value), 'root must be an object');
  valid(value.version === SAVE_VERSION, 'unsupported version');
  valid(integer(value.sequence, 1), 'order sequence');
  valid(object(value.state), 'missing session state');
  const state = value.state;
  valid(['orders', 'routes', 'delivering', 'arrived', 'result'].indexOf(state.phase as string) !== -1, 'phase');
  valid(typeof state.tutorialComplete === 'boolean', 'tutorial flag');
  valid(finite(state.elapsedSeconds, 0), 'elapsed time');
  valid(object(state.player), 'player must be an object');
  const player = state.player;
  valid(integer(player.cashCents, 0), 'cash');
  valid(integer(player.rating, 20, 100), 'rating');
  valid(integer(player.experience, 0), 'experience');
  valid(integer(player.completedOrders, 0), 'completed orders');
  valid(integer(player.vehicleTier, 1, 10), 'vehicle tier');
  valid(player.stationLevel === 1, 'T01 station level');
  valid(integer(player.level, 1) && player.level === getExperienceLevel(player.experience), 'experience level');
  valid(Array.isArray(state.orders), 'orders must be an array');
  state.orders.forEach(validateOrder);
  const orders = state.orders as Order[];
  const expectedCount = state.tutorialComplete ? GAME_CONFIG.orderCount : 1;
  valid(orders.length === expectedCount - (state.phase === 'orders' ? 0 : 1), 'order list size');
  const ids = orders.map(order => order.id);
  valid(new Set(ids).size === ids.length, 'duplicate order identifiers');
  const capacity = VEHICLES[player.vehicleTier - 1].capacityKg;
  if (state.phase === 'orders' && state.tutorialComplete) {
    valid(orders.filter(order => order.weightKg <= capacity).length >= 3, 'capacity guarantee');
  }
  for (const order of orders) valid(routePreviews(order, player.vehicleTier).some(route => route.lateSeconds === 0), 'unreachable order deadline');
  if (state.phase === 'orders') {
    valid(state.activeOrder === null && state.activeRoute === null && state.receipt === null
      && value.fixedDamage === null && state.elapsedSeconds === 0, 'idle state contains active delivery');
  } else {
    validateOrder(state.activeOrder);
    const active = state.activeOrder;
    valid(ids.indexOf(active.id) === -1, 'active order duplicated in list');
    ids.push(active.id);
    valid(active.weightKg <= capacity, 'active order exceeds capacity');
    valid(routePreviews(active, player.vehicleTier).some(route => route.lateSeconds === 0), 'unreachable active deadline');
    if (state.phase === 'routes') {
      valid(state.activeRoute === null && value.fixedDamage === null && state.receipt === null
        && state.elapsedSeconds === 0, 'route selection contains delivery result');
    } else {
      valid(damageValue(value.fixedDamage), 'missing fixed damage');
      valid(object(state.activeRoute), 'missing selected route');
      const route = state.activeRoute;
      const expected = routePreviews(active, player.vehicleTier).find(candidate => candidate.id === route.id);
      valid(expected, 'unknown selected route');
      valid(route.name === expected.name && route.description === expected.description
        && route.durationSeconds === expected.durationSeconds && route.lateSeconds === expected.lateSeconds
        && route.damageChance === expected.damageChance && route.arrivalTemperature === null, 'selected route changed');
      valid(state.elapsedSeconds <= expected.durationSeconds, 'elapsed exceeds route');
      if (state.phase === 'delivering') {
        valid(state.elapsedSeconds < expected.durationSeconds && state.receipt === null, 'in-transit state already arrived');
      } else {
        valid(state.elapsedSeconds === expected.durationSeconds, 'arrival time does not match route');
        if (state.phase === 'arrived') valid(state.receipt === null, 'arrived state already has receipt');
        else validateReceipt(state.receipt, active, expected, value.fixedDamage, player);
      }
    }
  }
  for (const id of ids) {
    valid(/^order-[1-9]\d*$/.test(id), 'order identifier');
    const orderSequence = Number(id.slice(6));
    valid(Number.isSafeInteger(orderSequence) && orderSequence <= value.sequence, 'order sequence behind identifiers');
  }
}

function validateReceipt(value: unknown, order: Order, route: RoutePreview, damage: Damage, player: Record<string, unknown>): void {
  valid(object(value), 'missing receipt');
  valid(value.orderId === order.id, 'receipt order');
  valid(integer(value.incomeCents, 1), 'receipt income');
  valid(integer(value.ratingDelta, -10, 6), 'receipt rating delta');
  valid(value.ratingAfter === player.rating, 'receipt rating');
  valid(value.experienceGained === GAME_CONFIG.experiencePerOrder, 'receipt experience');
  valid(value.lateSeconds === route.lateSeconds, 'receipt lateness');
  valid(value.damage === damage, 'receipt damage');
  valid(value.completedOrders === player.completedOrders && integer(value.completedOrders, 1), 'receipt completed orders');
  valid(value.newCashCents === player.cashCents && (player.cashCents as number) >= value.incomeCents, 'receipt cash');
  valid(Array.isArray(value.summary) && value.summary.length > 0 && value.summary.every(item => typeof item === 'string'), 'receipt summary');
  valid(integer(player.experience, GAME_CONFIG.experiencePerOrder), 'settled experience');
  const expectedDelta = clamp(DAMAGE_EFFECTS[damage].ratingDelta
    + (route.lateSeconds > 0 ? -3 : order.type === 'urgent' ? 2 : 0), -10, 6);
  valid(value.ratingDelta === expectedDelta, 'receipt rating effect');
  const previousLevel = getExperienceLevel(player.experience - GAME_CONFIG.experiencePerOrder);
  const expectedIncome = Math.round(order.basePriceCents * VEHICLES[(player.vehicleTier as number) - 1].incomeMultiplier
    * getPlayerIncomeMultiplier(previousLevel) * (0.85 + (player.rating as number) * 0.003)
    * DAMAGE_EFFECTS[damage].retainedIncome);
  valid(value.incomeCents === expectedIncome, 'receipt income calculation');
}
