"""Product-design pricing arithmetic only; does not import or run the game."""
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
SOURCE = json.loads((ROOT.parent / '2026-11-01-vehicle-growth/candidate.json').read_text())
VEHICLES = SOURCE['vehicles']
PRICES = [150, 230, 350, 520, 800, 1200, 1800, 2700, 4100, 6200]
MAP_ENDS = [5, 15, 30, 50, 80]
MAP_TOPS = [3, 5, 6, 8, 9]


def rnd(x):
    return int(D(x).quantize(D(1), rounding=ROUND_HALF_UP))


def cumulative(index, level):
    return rnd(D(PRICES[index]) * level * (level - 1) / 435)


def recruitment(n):
    return 10 * rnd((D(100) + 3 * (n - 1) ** 2) / 10)


def hourly(index, level):
    row = VEHICLES[index]['levels'][level - 1]
    speed = D(row['speedKph'])
    fee_yuan = D(rnd(D(1000) * D(row['totalVehicleIncomeMultiplier']))) / 100
    # A proposed NPC pricing reference, not the main character's animation clock.
    seconds = D(63) * 12 / speed + 27
    return D(3600) / seconds * fee_yuan


def minutes_for(cost, rate):
    return rnd(D(cost) / rate * 60)


cost_rows = []
vehicle_profiles = []
vehicle_summary = []
for i, vehicle in enumerate(VEHICLES):
    levels = []
    for level in range(1, 31):
        before = cumulative(i, level - 1) if level > 1 else 0
        levels.append({'level': level, 'upgradeToThisLevelYuan': cumulative(i, level) - before,
                       'cumulativeUpgradeYuan': cumulative(i, level),
                       'purchasePlusUpgradesYuan': PRICES[i] + cumulative(i, level)})
    vehicle_profiles.append({'grade': vehicle['grade'], 'unlockMap': vehicle['unlockMap'],
                             'purchasePriceYuan': PRICES[i], 'levels': levels})
    vehicle_summary.append({
        'grade': vehicle['grade'], 'purchasePriceYuan': PRICES[i],
        'upgradeToLevel10Yuan': cumulative(i, 10),
        'upgradeToLevel20Yuan': cumulative(i, 20),
        'upgradeToLevel30Yuan': cumulative(i, 30),
        'purchasePlusLevel30Yuan': PRICES[i] + cumulative(i, 30),
        'referenceNpcGrossYuanPerHourLevel1': rnd(hourly(i, 1)),
        'referenceNpcGrossYuanPerHourLevel30': rnd(hourly(i, 30)),
        'vehicleOnlyPaybackMinutesLevel1': minutes_for(PRICES[i], hourly(i, 1)),
        'incrementalUpgradePaybackMinutes1To30': minutes_for(cumulative(i, 30), hourly(i, 30) - hourly(i, 1)),
    })

hire_rows = []
map_rows = []
start = 1
for map_number, end in enumerate(MAP_ENDS, 1):
    for n in range(start, end + 1):
        hire_rows.append({'map': map_number, 'recruitmentOrdinal': n,
                          'recruitmentPriceYuan': recruitment(n),
                          'cumulativeRecruitmentPriceYuan': sum(recruitment(k) for k in range(1, n + 1)),
                          'hirePlusDLevel1Yuan': recruitment(n) + PRICES[0]})
    i = MAP_TOPS[map_number - 1]
    total_hires = sum(recruitment(k) for k in range(1, end + 1))
    members = end + 1
    map_rows.append({
        'map': map_number, 'newRecruitmentOrdinals': [start, end],
        'newRecruitmentCount': end - start + 1, 'totalNpcCount': end,
        'firstRecruitmentPriceYuan': recruitment(start), 'lastRecruitmentPriceYuan': recruitment(end),
        'newRecruitmentTotalYuan': sum(recruitment(k) for k in range(start, end + 1)),
        'allRecruitmentTotalYuan': total_hires,
        'referenceTopVehicle': VEHICLES[i]['grade'],
        'referenceTeamIncludingProtagonist': members,
        'staticAssetBudgetAllTopLevel10Yuan': total_hires + members * (PRICES[i] + cumulative(i, 10)),
        'staticAssetBudgetAllTopLevel30Yuan': total_hires + members * (PRICES[i] + cumulative(i, 30)),
    })
    start = end + 1

allocation = []
for n, top in [(1, 3), (5, 3), (15, 5), (30, 6), (50, 8), (80, 9)]:
    options = [{'grade': VEHICLES[i]['grade'], 'hirePlusVehicleYuan': recruitment(n) + PRICES[i],
                'grossPaybackMinutes': minutes_for(recruitment(n) + PRICES[i], hourly(i, 1)),
                '_exact': D(recruitment(n) + PRICES[i]) / hourly(i, 1)} for i in range(top + 1)]
    best = min(options, key=lambda x: x['_exact'])['grade']
    for item in options:
        del item['_exact']
    allocation.append({'recruitmentOrdinal': n, 'referenceBestPaybackGrade': best, 'options': options})

upgrade_comparisons = []
for i in [0, 3, 5, 8, 9]:
    for a, b in [(1, 10), (10, 20), (20, 30), (1, 30)]:
        fee = cumulative(i, b) - cumulative(i, a)
        delta = hourly(i, b) - hourly(i, a)
        upgrade_comparisons.append({'grade': VEHICLES[i]['grade'], 'fromLevel': a, 'toLevel': b,
                                    'costYuan': fee, 'referenceExtraGrossYuanPerHour': rnd(delta),
                                    'incrementalGrossPaybackMinutes': minutes_for(fee, delta)})

all_positive = all(row['upgradeToThisLevelYuan'] >= 1 for v in vehicle_profiles for row in v['levels'][1:])
totals_match = all(sum(row['upgradeToThisLevelYuan'] for row in v['levels']) == 2 * v['purchasePriceYuan'] for v in vehicle_profiles)
nondecreasing_fees = all(all(a['upgradeToThisLevelYuan'] <= b['upgradeToThisLevelYuan'] for a, b in zip(v['levels'][1:], v['levels'][2:])) for v in vehicle_profiles)
profile = {
    'id': 'vehicle-and-rider-pricing-candidate-20261101-v1',
    'status': 'proposal-not-approved-not-implemented',
    'confirmedBaseFeeYuan': 10,
    'assumedStartCashYuan': 100, 'assumedFreeProtagonistVehicle': 'D Level1',
    'actualPricesUseWholeYuan': True,
    'upgradeCostFormula': 'C(L)=roundHalfUp(P*L*(L-1)/435); feeToL=C(L)-C(L-1)',
    'recruitmentFormula': 'H(n)=10*roundHalfUp((100+3*(n-1)^2)/10), n=1..80 excluding protagonist',
    'referenceNpc': {
        'status': 'pricing-assumption-not-approved-game-rule',
        'dLevel1StandardCycleSeconds': 90,
        'roadPartSecondsAtSpeed12': 63, 'fixedWorkPartSeconds': 27,
        'cycleSeconds': '63*12/preciseVehicleSpeedKph+27',
        'feePerOrder': '10*preciseVehicleIncomeMultiplier rounded once to cents',
        'allOtherMultipliers': 1, 'extraOperatingExpenses': 0,
        'excludesRiderLevelsOfflineCapsWeatherDamageAndHeavyOrderBonus': True,
    },
    'vehicles': vehicle_profiles, 'recruitment': hire_rows,
}
arithmetic = {
    'status': 'design-arithmetic-only-not-game-verification',
    'vehicleSummary': vehicle_summary, 'mapBudgets': map_rows,
    'referenceRecruitAndVehicleChoices': allocation,
    'referenceUpgradeComparisons': upgrade_comparisons,
    'wholeYuanPositiveFees': all_positive,
    'level30FeesEqualExactlyTwicePurchasePrice': totals_match,
    'perLevelFeesNondecreasing': nondecreasing_fees,
    'firstHirePlusDLevel1Yuan': recruitment(1) + PRICES[0],
    'initialCashAssumptionYuan': 100,
    'firstHireExtraStandardDOrdersAtFee10': 15,
    'all80RecruitmentYuan': sum(recruitment(n) for n in range(1, 81)),
    'all80WithDLevel1ExcludingFreeProtagonistYuan': sum(recruitment(n) for n in range(1, 81)) + 80 * PRICES[0],
    'all81SssLevel30And80RecruitmentStaticBudgetYuan': sum(recruitment(n) for n in range(1, 81)) + 81 * PRICES[-1] * 3,
    'sensitivity': {'halfNpcProductivityPaybackTimeMultiplier': 2,
                    'oneAndHalfNpcProductivityPaybackTimePercentOfBase': 67,
                    'twentyPercentLessNetIncomePaybackTimePercentOfBase': 125},
    'staticBudgetExcludesPriorDiscardedPurchasesRiderUpgradesAndOtherExpenses': True,
}

vehicle_md = ['# 十档车辆购买价与1–30级升级费', '',
              '设计候选，未接入游戏。以下购买费、升级费、累计费均为实际整数元。',
              '1级为购车后初始等级，无升级费；2–30级行表示升到该级的一次费用。',
              '每级费用由整数累计费用作差，逐级与批量升级的总价完全相同。', '',
              '| 车型 | 购车价 | 1→10累计 | 1→20累计 | 1→30累计 | 购买并满级总价 |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
for row in vehicle_summary:
    vehicle_md.append(f"| {row['grade']} | {row['purchasePriceYuan']} | {row['upgradeToLevel10Yuan']} | {row['upgradeToLevel20Yuan']} | {row['upgradeToLevel30Yuan']} | {row['purchasePlusLevel30Yuan']} |")
vehicle_md.extend(['', '## 每一级费用（元）', '',
                   '| 升到等级 | ' + ' | '.join(v['grade'] for v in VEHICLES) + ' |',
                   '| ---: | ' + ' | '.join(['---:'] * 10) + ' |'])
for level in range(1, 31):
    vehicle_md.append('| ' + str(level) + ' | ' + ' | '.join(str(v['levels'][level-1]['upgradeToThisLevelYuan']) for v in vehicle_profiles) + ' |')
vehicle_md.extend(['', '30级封顶。此表中的金币费用为整数定价；车辆属性内部仍按精确成长曲线计算。', ''])

hire_md = ['# 80名骑手招募费与配车成本', '',
           '设计候选，未接入游戏。招募序号不含主角；各图新增名额，招募费不含车辆或骑手升级。',
           '招募成功永久占用一个名额，同一骑手不重复购买；累计成功招募序号决定价格，不按当前配车或临时收入改变。', '',
           '| 地图 | 招募序号 | 招募费 | 从第1名累计招募费 | 本次招募并新购D车 |',
           '| ---: | ---: | ---: | ---: | ---: |']
for row in hire_rows:
    hire_md.append(f"| {row['map']} | {row['recruitmentOrdinal']} | {row['recruitmentPriceYuan']} | {row['cumulativeRecruitmentPriceYuan']} | {row['hirePlusDLevel1Yuan']} |")
hire_md.extend(['', '若已有空闲车，则无需再次支付购车费；D车套餐仅作统一入门成本参考。', ''])

ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / 'pricing-candidate.json').write_text(json.dumps(profile, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'pricing-arithmetic.json').write_text(json.dumps(arithmetic, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'vehicle-prices-and-upgrades.md').write_text('\n'.join(vehicle_md))
(ROOT / 'rider-recruitment-prices.md').write_text('\n'.join(hire_md))
print('车型10款，费用数据300行；实际升级290次；骑手招募80条。')
print('每级费用为正整数：', all_positive, '；累计恰好2倍购车价：', totals_match, '；费用非递减：', nondecreasing_fees)
for row in vehicle_summary:
    print(row['grade'], '购买', row['purchasePriceYuan'], '升级至30', row['upgradeToLevel30Yuan'], '购入并满级', row['purchasePlusLevel30Yuan'])
for row in map_rows:
    print('地图', row['map'], '新增招募费合计', row['newRecruitmentTotalYuan'], '累计招募费', row['allRecruitmentTotalYuan'])
print('80名全部招募：', arithmetic['all80RecruitmentYuan'])
print('80名招募加81台SSS全部满级静态资产价：', arithmetic['all81SssLevel30And80RecruitmentStaticBudgetYuan'])
print('仅设计试算；未运行游戏、游戏测试、构建、渲染或存档操作。')
