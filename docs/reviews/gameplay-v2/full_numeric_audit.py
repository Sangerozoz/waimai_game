"""Independent design calculations and assumed cohorts, not production-game tests."""
import json
import math
import random
import statistics
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'trial-profile.json').read_text())
D = lambda v: Decimal(str(v))


def rounded_cents(value):
    return int(D(value).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def earned_fee(base, rating, exp, vehicle=1, station=1, retained=1):
    return rounded_cents(D(base) * (D('.85') + rating * D('.003')) * D(exp) * D(vehicle) * D(station) * D(retained))


def experience_factor(completed):
    xp = completed * 10
    thresholds = P['growth']['thresholds']
    level = sum(xp >= boundary for boundary in thresholds)
    threshold, increment = thresholds[-1], 1102
    while xp >= threshold:
        increment = math.floor(increment * 1.35 + .5)
        threshold += increment
        if xp >= threshold:
            level += 1
        else:
            break
    return min(1.6, 1 + (level - 1) * .03)


def multiplier_work(bonus, dt):
    active = min(dt, bonus / P['clock']['boostDecayPerSecond'])
    return dt + bonus * active - .5 * P['clock']['boostDecayPerSecond'] * active * active


@lru_cache(None)
def road_wall_time(base_seconds, clicks):
    if base_seconds <= 0 or clicks == 0:
        return base_seconds
    clicks = min(clicks, P['clock']['effectiveClicksPerSecond'])
    dt = 1 / clicks
    cap = P['clock']['maxBoostNumerator'] / P['clock']['maxBoostDenominator'] - 1
    bonus, elapsed, work_left = 0., 0., base_seconds
    while work_left > 0:
        bonus = min(cap, bonus + P['clock']['clickImpulse'])
        work = multiplier_work(bonus, dt)
        if work_left <= work:
            low, high = 0., dt
            for _ in range(48):
                mid = (low + high) / 2
                if multiplier_work(bonus, mid) < work_left:
                    low = mid
                else:
                    high = mid
            return elapsed + (low + high) / 2
        elapsed += dt
        work_left -= work
        bonus = max(0, bonus - P['clock']['boostDecayPerSecond'] * dt)


def cohort(seed, mix, supply_policy):
    # Assumptions, not measured generation: 80% solo 10-20min, 20% 21-30min;
    # fast routes, 20% urgent, 50% fulfilled door demand, uniform 15-25 yuan.
    rng = random.Random(seed)
    cash, rating, tier, station, energy = 10000, 80, 1, 1, 100.
    income_total = supply_total = free_rests = 0
    first_upgrade = None
    base_wall = fast_wall = 0.
    worst_net = float('inf')
    for completed in range(1, 2001):
        fee = rng.randint(1500, 2500)
        solo_minutes = rng.randint(10, 20) if rng.random() < .8 else rng.randint(21, 30)
        urgent, door = rng.random() < .2, rng.random() < .5
        selector = rng.random()
        fragile, durable = selector < mix[0], selector >= 1 - mix[1]
        damage_roll, severity_roll = rng.random(), rng.random()
        if completed == 1:
            fee, urgent, door, fragile, durable = 2000, False, False, False, True
        speed = [12, 13.2, 14.4][tier - 1]
        road_game_seconds = solo_minutes * 60 - P['clock']['pickupGameSeconds']
        metres = road_game_seconds * speed / 3.6
        energy_cost = metres / 1000 * 2 + 2
        pickup_prefix_cost = 0 if completed == 1 else metres / 1000 * .25 * 2 + 1
        spend, supply_game, supply_real = 0, 0, 0
        if energy < energy_cost + 1:
            if supply_policy == 'free' or energy < pickup_prefix_cost + 1:
                energy = 100; free_rests += 1
                base_wall += 20; fast_wall += 20
            else:
                kind = 'meal' if supply_policy == 'meal-aware' and not urgent else 'water'
                item = P['supply'][kind]
                count = math.ceil((energy_cost + 1 - energy) / item['recovery'])
                if cash < count * item['priceCents']:
                    energy = 100; free_rests += 1
                    base_wall += 20; fast_wall += 20
                else:
                    spend = count * item['priceCents']; cash -= spend
                    supply_game = count * item['gameSeconds']; supply_real = count * item['realSeconds']
                    energy = min(100., energy + count * item['recovery'])
        energy -= energy_cost
        assert energy >= 1 - 1e-7 and cash >= 0
        probability = .45 if fragile else .08 if durable else .20
        damaged = damage_roll < probability
        retained, damage_rating = (1., 0)
        if damaged:
            retained, damage_rating = (.9, -2) if severity_roll < .7 else (.75, -5) if severity_roll < .95 else (.5, -10)
        late = supply_game > (120 if urgent else 300)
        delta = damage_rating + (-3 if late else 2 if urgent else 0) + (2 if fragile and not damaged else 0) + (2 if door else 0)
        rating = max(20, min(100, rating + max(-10, min(6, delta))))
        fee_earned = earned_fee(fee, rating, experience_factor(completed - 1), [1, 1.12, 1.25][tier - 1], 1 if station == 1 else 1.1, retained)
        income_total += fee_earned; supply_total += spend; cash += fee_earned
        worst_net = min(worst_net, fee_earned - spend)
        # UI decision overhead is an explicit 2s assumption per single order.
        pickup_fraction = 0 if completed == 1 else .25
        pickup_base = road_game_seconds / 120 * pickup_fraction
        drop_base = road_game_seconds / 120 * (1 - pickup_fraction)
        base_wall += pickup_base + drop_base + 2 + supply_real + 2
        fast_wall += road_wall_time(pickup_base, 8) + road_wall_time(drop_base, 8) + 2 + supply_real + 2
        if tier == 1 and cash >= 20000:
            cash -= 20000; tier = 2; first_upgrade = completed
        if completed >= 100 and station == 1 and cash >= 100000:
            cash -= 100000; station = 2
        if station == 2 and tier == 2 and cash >= 50000:
            cash -= 50000; tier = 3
        if tier == 3 and cash >= 80000:
            cash -= 80000
            return {'firstUpgrade': first_upgrade, 'cityOrders': completed, 'supplyCents': supply_total, 'minimumSingleNetCents': int(worst_net), 'baseMinutes': base_wall / 60, 'denseClickMinutes': fast_wall / 60, 'freeRestCount': free_rests}
    raise AssertionError('candidate cohort did not reach city')


def percentile(values, p):
    return sorted(values)[math.ceil(len(values) * p) - 1]


def summarize(values):
    fields = ['firstUpgrade', 'cityOrders', 'baseMinutes', 'denseClickMinutes', 'supplyCents', 'freeRestCount']
    output = {field: {'median': round(statistics.median([r[field] for r in values]), 3), 'p95': round(percentile([r[field] for r in values], .95), 3)} for field in fields}
    output['lowestSingleNetCents'] = min(r['minimumSingleNetCents'] for r in values)
    return output


click_times = {str(hz): road_wall_time(10., hz) for hz in [0, 3, 4, 6, 8, 80]}
assert math.isclose(click_times['8'], 3.32955, abs_tol=5e-6)
assert click_times['80'] == click_times['8']
assert all(click_times[str(a)] >= click_times[str(b)] for a, b in [(0, 3), (3, 4), (4, 6), (6, 8)])
bonus = work = 0.
step_size = .0001
for step in range(100001):
    if step % 1250 == 0:
        bonus = min(10/3-1, bonus + .5)
    work += (1 + bonus) * step_size
    bonus = max(0., bonus - 1.5 * step_size)
    if work >= 10:
        assert abs((step+1)*step_size-click_times['8']) < .001
        break
else:
    raise AssertionError('independent fine-step click integration did not finish')

amounts = P['npc']['tierIncomeMultipliers']
city_d_hour = D(3000) * D(amounts[0]) * D(amounts[0]) * D(1.1) * D(1.09) * P['npc']['ordersPerRealHour']
county_d_hour = D(2000) * D(1.1) * D(1.09) * 6
assert rounded_cents(city_d_hour) == 21582
assert rounded_cents(county_d_hour) == 14388
assert amounts[2] == 1.25 and amounts[9] == 2.78

# Independent hand-computable anti-backfill cases.
split_rate_cents = 10000 * 1 + 20000 * 1
assert split_rate_cents == 30000 and split_rate_cents != 20000 * 2
old_cap = 3000 * 7 // 3
paid_before_new_active = min(10000, old_cap)
discarded = (10000 - paid_before_new_active) + 2 * 10000
paid_immediately_after_new_active = 0
new_cap = 6000 * 7 // 3
paid_next_hour = min(10000, new_cap - paid_before_new_active)
assert discarded == 23000 and paid_immediately_after_new_active == 0 and paid_next_hour == 7000
offline_correct_cents = 10000 * .5 * min(16, 8)
offline_wrong_daywise_cents = 10000 * .5 * (min(7, 8) + min(9, 8))
assert offline_correct_cents == 40000 and offline_wrong_daywise_cents == 75000
whole_claim_cap = 2000 * 500
assert min(1000000 * .5 * 8, whole_claim_cap) == 1000000

q = P['strengthening']
fixed_quote_reference = rounded_cents(D(11250) * D(q['fixedVehicleTierMultiplier']) * D(1.6) * (D('.85') + q['referenceRating'] * D('.003')) * D(1.4))
level29_quote = fixed_quote_reference * 29
sum_fixed = sum(fixed_quote_reference * level for level in range(1, 30))
assert sum_fixed == fixed_quote_reference * 435
assert sum(level * (D(1) + (level - 1) * D('.01')) for level in range(1, 30)) == D('516.2')

sample_count = 512
scenarios = [
    ('target10-fragile-free', (.1, 0.), 'free'),
    ('catalog-equal-free', (5/16, 6/16), 'free'),
    ('catalog-equal-water', (5/16, 6/16), 'water'),
    ('catalog-equal-meal-aware', (5/16, 6/16), 'meal-aware'),
]
cohorts = {}
for name, mix, policy in scenarios:
    rows = [cohort(seed, mix, policy) for seed in range(sample_count)]
    cohorts[name] = summarize(rows)
    assert all(r['minimumSingleNetCents'] > 0 for r in rows)

remaining_clue_probability = sum(math.comb(1200, k) * .05**k * .95**(1200-k) for k in range(9))
result = {
    'scope': 'candidate design mathematics and assumed cohorts only; not game implementation, actual offer distribution or device verification',
    'profile': P['id'], 'clickRoadSeconds': click_times,
    'npcCityDHourlyCents': rounded_cents(city_d_hour), 'npcCountyDHourlyCents': rounded_cents(county_d_hour),
    'cityFirstRiderGrossPaybackHours': 130000 / float(city_d_hour),
    'fixedStrengthReferenceCents': fixed_quote_reference, 'fixedLevel29QuoteCents': level29_quote, 'fixedFullStrengthCostCents': sum_fixed,
    'npcAntiBackfillExample': {'discardedCents': discarded, 'immediatePayoutAfterNewActiveCents': paid_immediately_after_new_active, 'nextHourPayoutCents': paid_next_hour},
    'offline16HourCorrectCents': offline_correct_cents, 'wrongPerDayCapCents': offline_wrong_daywise_cents,
    'clueMeanOrdersPerCategory': 9/.05, 'notNineCluesAfter1200ProbabilityPerCategory': remaining_clue_probability,
    'assumptions': {'seedsPerScenario': sample_count, 'route': 'fast', 'soloMinutesDistribution': '80% integers10-20,20%integers21-30 including 1min pickup', 'feeCents': 'uniform1500..2500, first2000', 'urgentProbability': .2, 'fulfilledDoorProbability': .5, 'foodMix': 'target10fragile/restnormal OR current catalog equally weighted5fragile/6durable/5normal, not actual lobby frequency', 'pickupRoadFraction': '.25 except first0', 'npcIncomeBeforeCity': 'excluded; D rider bought last', 'menuRealSecondsPerOrder': 2, 'supplyLocations': 'merchant reached if starting energy covers pickup; otherwise idle free rest before accepting; no shop detour modeled', 'tripSize': 1},
    'cohorts': cohorts,
}
(ROOT / 'full-numeric-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
