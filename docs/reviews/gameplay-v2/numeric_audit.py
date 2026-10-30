"""Design arithmetic only. Does not import, operate or validate the game runtime."""
import itertools
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'trial-profile.json').read_text())
checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def cents(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def energy(metres, pickups, drops):
    e = P['energy']
    return Decimal(str(metres)) / 1000 * e['perKm'] + pickups * e['perPickupVisit'] + drops * e['perDrop']


def growth_case(severe):
    g, c = P['growth'], P['county']
    cash, rating, tier, station, recruited = c['initialCashCents'], c['ratingStart'], 1, 1, False
    events = {}
    for completed in range(1, 10001):
        xp_before = (completed - 1) * g['experiencePerOrder']
        level = sum(xp_before >= threshold for threshold in g['thresholds'])
        if level > len(g['thresholds']) or xp_before >= g['thresholds'][-1]:
            raise AssertionError('growth case exceeded explicitly modeled experience table')
        exp = min(Decimal(str(g['maximumExperienceMultiplier'])), Decimal(1) + (level - 1) * Decimal(str(g['incomePerLevel'])))
        vehicle = [Decimal(1), Decimal(str(g['firstVehicleIncomeMultiplier'])), Decimal(str(g['cityVehicleIncomeMultiplier']))][tier - 1]
        station_factor = Decimal(1) if station == 1 else Decimal(str(g['station2IncomeMultiplier']))
        rating = max(c['ratingFloor'], rating - 10) if severe else rating
        rating_factor = Decimal(str(c['ratingCoefficientBase'])) + rating * Decimal(str(c['ratingCoefficientPerPoint']))
        damage = Decimal(str(c['minimumDamageRetention'])) if severe else Decimal(1)
        cash += cents(Decimal(c['minimumFeeCents']) * vehicle * exp * rating_factor * damage * station_factor)
        if tier == 1 and cash >= g['firstVehicleFeeCents']:
            cash -= g['firstVehicleFeeCents']; tier = 2; events['D+'] = completed
        if completed == g['cityOrderThreshold']:
            events['cashAt100BeforeStation'] = cash
        if completed >= g['cityOrderThreshold'] and station == 1 and cash >= g['station2FeeCents']:
            cash -= g['station2FeeCents']; station = 2; events['station2'] = completed
        if station == 2 and tier == 2 and cash >= g['cityVehicleFeeCents']:
            cash -= g['cityVehicleFeeCents']; tier = 3; events['C'] = completed
        if tier == 3 and not recruited and cash >= g['riderDFeeCents']:
            cash -= g['riderDFeeCents']; recruited = True; events['riderD'] = completed
        check('wallet nonnegative: ' + str(severe) + '/' + str(completed), cash >= 0)
        if recruited:
            events['cityUnlock'] = completed
            return events
    raise AssertionError('city gate not reached under positive-income scenario')


def route_trace(customers, order):
    # Explicit synthetic bidirectional line; all pickups at coordinate zero.
    point, game_seconds, metres, picked = 0, 0, 0, False
    arrivals = {}
    for i in order:
        if not picked:
            game_seconds += P['clock']['pickupGameSeconds']; picked = True
        distance = abs(customers[i] - point)
        metres += distance
        game_seconds += distance / (12000 / 3600)
        arrivals[str(i)] = game_seconds
        point = customers[i]
    return {'metres': metres, 'arrivalsGameSeconds': arrivals}


c = P['county']; e = P['energy']; s = P['supply']
minimum = cents(Decimal(c['minimumFeeCents']) * (Decimal(str(c['ratingCoefficientBase'])) + c['ratingFloor'] * Decimal(str(c['ratingCoefficientPerPoint']))) * Decimal(str(c['minimumDamageRetention'])))
maximum_single_energy = energy(c['singleOrderMaxMetres'], 1, 1)
water_count = math.ceil((maximum_single_energy + e['finishReserve']) / s['water']['recovery'])
water_cost = water_count * s['water']['priceCents']
check('minimum county fee after worst damage is 683 cents', minimum == 683)
check('longest single order costs 22 energy', maximum_single_energy == 22)
check('two waters leave reserve and positive net income', water_count == 2 and minimum - water_cost == 283)
check('one meal leaves reserve and positive net income', s['meal']['recovery'] > maximum_single_energy + e['finishReserve'] and minimum - s['meal']['priceCents'] == 183)
check('zero cash and zero energy can recover for free', s['idleRest']['priceCents'] == 0 and s['idleRest']['recoveryTo'] >= maximum_single_energy + e['finishReserve'])
check('active recovery does not require cash', s['activeRest']['priceCents'] == 0 and s['activeRest']['recovery'] > 0)
check('4km single costs 10 energy', energy(4000, 1, 1) == 10)
check('8km same-merchant triple costs 20 energy', energy(8000, 1, 3) == 20)

tasks = tuple((kind, i) for i in range(3) for kind in ('P', 'D'))
legal = [p for p in itertools.permutations(tasks) if all(p.index(('P', i)) < p.index(('D', i)) for i in range(3))]
check('three distinct orders have 90 precedence-valid sequences', len(legal) == 90)


def capacity_ok(sequence, weights):
    load = 0
    for kind, i in sequence:
        load += weights[i] if kind == 'P' else -weights[i]
        if load > 5 or load < 0:
            return False
    return load == 0


valid_capacity = sum(capacity_ok(p, [3, 3, 1.5]) for p in legal)
check('weight test has feasible routes and rejects overloaded permutations', 0 < valid_capacity < len(legal))
check('pick-all route overloads D while staggered pickup works', not capacity_ok((('P', 0), ('P', 1), ('D', 0), ('D', 1), ('P', 2), ('D', 2)), [3, 3, 1.5]) and capacity_ok((('P', 0), ('D', 0), ('P', 1), ('D', 1), ('P', 2), ('D', 2)), [3, 3, 1.5]))

same = route_trace([2000, 3000, 4000], [0, 1, 2])
opposite = route_trace([2000, 3000, -4000], [0, 1, 2])
due = {str(i): abs(position) / (12000 / 3600) + P['clock']['pickupGameSeconds'] + P['clock']['normalSlackSeconds'] for i, position in enumerate([2000, 3000, 4000])}
check('same-direction arrivals fit independently promised deadlines', all(same['arrivalsGameSeconds'][i] <= due[i] for i in due))
check('opposite-direction addition makes final order 25 minutes late', opposite['arrivalsGameSeconds']['2'] - due['2'] == 1500)
check('same-direction route is 4km while chosen opposite route is 10km', same['metres'] == 4000 and opposite['metres'] == 10000)

base = 1200 / P['clock']['gameSecondsPerRealSecond']
boost = P['clock']['maxBoostNumerator'] / P['clock']['maxBoostDenominator']
check('20 minute road leg is 10 seconds at base and 3 at instant maximum', base == 10 and math.isclose(base / boost, 3))
check('service time is not multiplied by driving conversion', P['clock']['pickupGameSeconds'] != P['clock']['pickupRealSeconds'] * P['clock']['gameSecondsPerRealSecond'])
normal_growth, worst_growth = growth_case(False), growth_case(True)
check('even fixed severe damage reaches the city gate', worst_growth['cityUnlock'] > 100 and worst_growth['cityUnlock'] < 1000)

dependencies = {
    'county': [], 'orders100': ['county'], 'station2': ['orders100'], 'Ccar': ['station2'], 'riderD': ['station2'],
    'city': ['orders100', 'station2', 'Ccar', 'riderD'], 'orders300': ['city'], 'station3': ['orders300'],
    'Bcar': ['station3'], 'workingCrider': ['station3'], 'province': ['orders300', 'station3', 'Bcar', 'workingCrider'],
    'orders800': ['province'], 'station4': ['orders800'], 'Acar': ['station4'], 'workingArider': ['station4'],
    'firstTier': ['orders800', 'station4', 'Acar', 'workingArider'], 'orders2000': ['firstTier'], 'station5': ['orders2000'],
    'international': ['station5', 'Acar', 'workingArider'], 'cluesS': ['firstTier', 'Acar', 'workingArider'],
    'purchaseS': ['international', 'cluesS'],
}
reached = set()
while len(reached) < len(dependencies):
    available = {name for name, requirements in dependencies.items() if name not in reached and set(requirements) <= reached}
    if not available:
        raise AssertionError('unlock dependency cycle')
    reached |= available
check('region and hidden dependencies contain no cycle', len(reached) == len(dependencies))

result = {'profile': P['id'], 'scope': 'design arithmetic only; not runtime, RNG distribution, balance or device verification', 'checksPassed': len(checks), 'minimumIncomeCents': minimum, 'maximumSingleOrderEnergy': str(maximum_single_energy), 'waterCostCents': water_cost, 'precedenceSequences': len(legal), 'capacityValidSequences': valid_capacity, 'sameDirection': same, 'oppositeDirection': opposite, 'normalFixedLowFeeGrowth': normal_growth, 'allSevereFixedLowFeeGrowth': worst_growth, 'unlockNodesReached': len(reached)}
(ROOT / 'numeric-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
summary = f'''# V2候选参数数值审计

参数：`{P['id']}`，状态为试算、未实施。用 `python3 docs/reviews/gameplay-v2/numeric_audit.py` 可重放。

## 边界结果

- 最低县城单收入¥{minimum / 100:.2f}，最长独立普通单{maximum_single_energy}点体力。
- 从0补足并留1点需{water_count}瓶水，¥{water_cost / 100:.2f}，最低净收益¥{(minimum - water_cost) / 100:.2f}；一份饭后最低净收益¥{(minimum - s['meal']['priceCents']) / 100:.2f}。
- 零钱零体力可免费恢复；这只证明费用/恢复规则，补给地点可达性必须由实际计划逐段校验，不能假设无体力也能先走到商店。
- 三单有{len(legal)}种先取后送合法顺序；重量3/3/1.5kg、D载重5kg时只有{valid_capacity}种通过逐段载重，说明必须验证顺序，不能分别检查每张单。
- 合成双向直线算例：同店三客在2/3/4km处，选顺序后4km总路程、到达11/16/21游戏分钟，均准时；将第三客换到反方向4km，选同样顺序则10km、第三单51分钟到达、比26分钟承诺晚25分钟。
- 20游戏分钟行驶基准10现实秒、理论瞬间满加速3秒；升速/衰减后的实际点击手感尚未模拟或体验。
- 指定的城市/站点/车辆/骑手/隐藏前置图{len(reached)}个节点拓扑可达；现金积累依赖持续正收益，不能把有向无环图当作实际游戏已无锁死的证明。

## 两个固定低价成长场景

共同假设：每单基础¥15、单单独立出发、全用免费恢复；按经验增长，现金够即买D+，100单之后按站点2→C车→D骑手顺序购买；不计NPC收入、不含付费补给，也不代表随机概率。

| 场景 | D+单数 | 站点2单数 | C车单数 | 城市条件全部满足单数 |
| --- | --- | --- | --- | --- |
| 无餐损、评价保持80 | {normal_growth['D+']} | {normal_growth['station2']} | {normal_growth['C']} | {normal_growth['cityUnlock']} |
| 每单严重餐损、评价降至20 | {worst_growth['D+']} | {worst_growth['station2']} | {worst_growth['C']} | {worst_growth['cityUnlock']} |

极端场景第100单、购买站点之前余额¥{worst_growth['cashAt100BeforeStation'] / 100:.2f}。因此100单只能承诺最低资格，不能承诺人人第100单已买齐资产。数值需要在M4/M5按实际候选分布、必要补给、玩家选择和被动收益重新模拟并体验。

## 限制

本次{len(checks)}个算术/枚举断言含成长过程中逐单余额非负检查，并非{len(checks)}种独立游戏测试。未运行V2实现（尚未开发），未验证真实地图、随机分布、持久化原子性、音画、手机或“好不好玩”。后续阶段仍须按实施方案完成实际代码/存档/设备与用户验收。
'''
(ROOT / 'numeric-audit.md').write_text(summary)
print(json.dumps(result, ensure_ascii=False, indent=2))
