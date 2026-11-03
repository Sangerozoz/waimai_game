"""Generate a product-design candidate. Does not import or execute the game."""
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
GRADES = ['D', 'D+', 'C', 'C+', 'B', 'B+', 'A', 'S', 'SS', 'SSS']
SPEEDS = ['12', '14', '17', '20', '24', '28', '34', '40', '48', '56']
CAPACITIES = ['5', '7', '10', '14', '19', '25', '33', '43', '55', '70']
INCOMES = ['1', '1.15', '1.32', '1.52', '1.75', '2.01', '2.31', '2.66', '3.06', '3.52']
MAPS = [1, 1, 1, 1, 2, 2, 3, 4, 4, 5]
DISTANCES = ['0.5', '2', '5', '10']


def fixed(value, places=4):
    return format(value.quantize(D(1).scaleb(-places), rounding=ROUND_HALF_UP), 'f')


def progress(level):
    return (D('0.05') * min(level - 1, 9)
            + D('0.03') * min(max(level - 10, 0), 10)
            + D('0.025') * max(level - 20, 0))


def stats(index, level):
    p = progress(level)
    return (D(SPEEDS[index]) * (1 + D('0.30') * p),
            D(CAPACITIES[index]) * (1 + D('0.60') * p),
            D(INCOMES[index]) * (1 + D('0.40') * p))


def throughput(index, level, distance, boost=D(1)):
    speed, _, income = stats(index, level)
    # Fixed road boost is a design bound, not simulated clicking or NPC dispatch.
    seconds = D(distance) * 90 / (speed * boost) + 2
    return income / seconds


vehicles = []
level_lines = [
    '# 十档车辆1–30级完整候选表', '',
    '状态：设计候选，未接入游戏。每款30行，共300行。', '',
    '速度为游戏道路km/h；容量为kg；收入倍率是车辆对单笔基础配送费的总乘数，已含车型和车辆等级。',
    '展示值四舍五入；实际设计公式不逐级取整，收入最终结算才取整到分。',
    '升级费用参考P=¥1,000仅用于展示比例，不是任何车型已定购买价；累计费用按目标等级先取整，再作差。', '',
]
summary = []
for i, grade in enumerate(GRADES):
    rows = []
    level_lines.extend([
        f'## {grade}（第{MAPS[i]}图开放）', '',
        '| 等级 | 速度km/h | 容量kg | 车辆总收入倍率 | 升至下一级费用（示例P=¥1,000） |',
        '| ---: | ---: | ---: | ---: | ---: |',
    ])
    for level in range(1, 31):
        speed, capacity, income = stats(i, level)
        cumulative_ratio = D(level * (level - 1)) / 435
        cumulative_cents = (D(100000) * cumulative_ratio).quantize(D(1), rounding=ROUND_HALF_UP)
        if level < 30:
            next_ratio = D((level + 1) * level) / 435
            next_cents = (D(100000) * next_ratio).quantize(D(1), rounding=ROUND_HALF_UP)
            upgrade = fixed((next_cents - cumulative_cents) / 100, 2)
        else:
            upgrade = '—'
        rows.append({
            'level': level,
            'speedKph': fixed(speed, 6), 'capacityKg': fixed(capacity, 6),
            'totalVehicleIncomeMultiplier': fixed(income, 6),
            'cumulativeUpgradeCostMultipleOfBasePrice': fixed(cumulative_ratio, 9),
        })
        level_lines.append(f'| {level} | {fixed(speed, 2)} | {fixed(capacity, 2)} | ×{fixed(income, 4)} | {upgrade} |')
    level_lines.append('')
    vehicles.append({
        'grade': grade, 'unlockMap': MAPS[i],
        'baseSpeedKph': SPEEDS[i], 'baseCapacityKg': CAPACITIES[i],
        'baseVehicleIncomeMultiplier': INCOMES[i], 'levels': rows,
    })
    summary.append({'grade': grade, 'level1': rows[0], 'level30': rows[-1]})

comparisons = []
gain_ranges = []
for boost in [D(1), D(10) / 3]:
    gains = [throughput(i, 30, d, boost) / throughput(i, 1, d, boost)
             for i in range(10) for d in DISTANCES]
    gain_ranges.append({'fixedRoadBoost': fixed(boost, 6),
                        'minimumGainRatio': fixed(min(gains), 6),
                        'maximumGainRatio': fixed(max(gains), 6)})
for i in range(9):
    cases = []
    for boost in [D(1), D(10) / 3]:
        for distance in DISTANCES:
            catch_level = next(level for level in range(1, 31)
                               if throughput(i + 1, level, distance, boost)
                               >= throughput(i, 30, distance, boost))
            cases.append({'km': distance, 'fixedRoadBoost': fixed(boost, 6), 'nextGradeLevel': catch_level})
    speed_level = next(level for level in range(1, 31) if stats(i + 1, level)[0] >= stats(i, 30)[0])
    capacity_level = next(level for level in range(1, 31) if stats(i + 1, level)[1] >= stats(i, 30)[1])
    comparisons.append({'fromGradeLevel30': GRADES[i], 'nextGrade': GRADES[i + 1],
                        'speedCatchLevel': speed_level, 'capacityCatchLevel': capacity_level,
                        'allSelectedCasesCatchLevel': max(speed_level, capacity_level, max(c['nextGradeLevel'] for c in cases)),
                        'cases': cases})

monotonic = all(all(all(a < b for a, b in zip(stats(i, level), stats(i, level + 1)))
                    for level in range(1, 30)) for i in range(10))
calculation = {
    'status': 'design-arithmetic-only-not-game-verification',
    'assumptions': {
        'sameMapSameBaseFeeSameRiderOtherMultipliers': True,
        'distanceKmIncludingPickupAndDelivery': DISTANCES,
        'roadGameSecondsPerRealSecond': 40,
        'pickupRealSeconds': 2,
        'readingPlanningAndHumanReactionSeconds': 0,
        'capacityChangesOrderEligibilityOnly': True,
        'fixedMaxBoostIsBoundNotMeasuredClicking': True,
        'doesNotImplementNpcDispatchOfflineOrActualPurchasePrices': True,
    },
    'generatedRows': sum(len(v['levels']) for v in vehicles),
    'everyLevelIncreasesAllThreeAttributes': monotonic,
    'selectedScenarioEfficiencyGainRanges': gain_ranges,
    'adjacentGradeComparisons': comparisons,
}
candidate = {
    'id': 'vehicle-growth-candidate-20261101-v1',
    'status': 'proposal-not-approved-not-implemented',
    'levelMin': 1, 'levelMax': 30,
    'growthProgress': {'levels2To10PerLevel': '0.05', 'levels11To20PerLevel': '0.03', 'levels21To30PerLevel': '0.025'},
    'maximumBonus': {'speed': '0.30', 'capacity': '0.60', 'vehicleIncome': '0.40'},
    'upgradeCost': {'reference': 'fixed undiscounted model purchase price P; free starter uses model reference price',
                    'cumulativeAtLevelL': 'roundCents(P * L * (L - 1) / 435)',
                    'singleUpgrade': 'cumulative(L+1) - cumulative(L)',
                    'currency': 'coins only; deterministic success proposed'},
    'vehicles': vehicles,
}
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / 'candidate.json').write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'calculation.json').write_text(json.dumps(calculation, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'all-levels.md').write_text('\n'.join(level_lines))
print('候选数值已生成：300行；三项逐级递增=' + str(monotonic))
for item in summary:
    a, b = item['level1'], item['level30']
    print(f"{item['grade']}: 速度{a['speedKph']}→{b['speedKph']}；容量{a['capacityKg']}→{b['capacityKg']}；收入{a['totalVehicleIncomeMultiplier']}→{b['totalVehicleIncomeMultiplier']}")
print('相邻车型在所选场景下追平旧款满级所需等级：' + ', '.join(f"{c['nextGrade']} Lv.{c['allSelectedCasesCatchLevel']}" for c in comparisons))
print('仅设计算术；未启动游戏、测试、构建、渲染或存档访问。')
