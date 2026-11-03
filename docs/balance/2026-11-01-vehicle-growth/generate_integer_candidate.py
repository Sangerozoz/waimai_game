"""Round the existing design candidate; never imports or runs the game."""
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
SOURCE = json.loads((ROOT / 'candidate.json').read_text())
PRICING_PATH = ROOT.parent / '2026-11-01-vehicle-economy/pricing-candidate.json'
PRICING = {v['grade']: v for v in json.loads(PRICING_PATH.read_text())['vehicles']}


def whole(value):
    return int(D(value).quantize(D(1), rounding=ROUND_HALF_UP))


vehicles = []
counts = []
lines = [
    '# 十档车辆1–30级整数审阅表', '',
    '2026-11-01。基础配送费为10元；四舍五入，表中不展示小数。',
    '状态：设计候选，未接入游戏。用户已确认仅显示整数，实际计算保留精度；具体成长曲线仍为候选。',
    '原始车型/等级成长系数仍用v1计算，速度/容量按最终展示值四舍五入，不从显示整数反推实际属性。',
    '每单参考收入仅含车辆因素，未计骑手、评价、餐损等；实际金额按完整公式最后取整到分，界面以元四舍五入显示。',
    '费用使用车辆与骑手联动定价候选的实际整数元价格，已替代原P=1000元比例示例。', '',
]
for vehicle in SOURCE['vehicles']:
    rows = []
    grade = vehicle['grade']
    price = PRICING[grade]
    lines.extend([
        f'## {grade}', '',
        '| 等级 | 速度km/h | 容量kg | 基础费10元的参考收入/单 | 升至下一级费用（元） |',
        '| ---: | ---: | ---: | ---: | ---: |',
    ])
    for old in vehicle['levels']:
        level = old['level']
        next_cost = price['levels'][level]['upgradeToThisLevelYuan'] if level < 30 else None
        reference_cents = whole(D(1000) * D(old['totalVehicleIncomeMultiplier']))
        row = {
            'level': level,
            'roundedSpeedKph': whole(old['speedKph']),
            'roundedCapacityKg': whole(old['capacityKg']),
            'displayReferenceIncomeYuanAtBase10': whole(D(reference_cents) / 100),
            'actualReferenceIncomeCentsAtBase10': reference_cents,
            'actualNextUpgradePriceYuan': next_cost,
            'actualCumulativeUpgradeYuan': price['levels'][level - 1]['cumulativeUpgradeYuan'],
        }
        rows.append(row)
        fee = next_cost if next_cost is not None else '—'
        lines.append(f"| {level} | {row['roundedSpeedKph']} | {row['roundedCapacityKg']} | {row['displayReferenceIncomeYuanAtBase10']} | {fee} |")
    keys = ['roundedSpeedKph', 'roundedCapacityKg', 'displayReferenceIncomeYuanAtBase10']
    unchanged = {k: sum(a[k] == b[k] for a, b in zip(rows, rows[1:])) for k in keys}
    unchanged['allThree'] = sum(all(a[k] == b[k] for k in keys) for a, b in zip(rows, rows[1:]))
    counts.append({'grade': grade, 'unchangedUpgradeCountsAfterRounding': unchanged})
    vehicles.append({'grade': grade, 'unlockMap': vehicle['unlockMap'], 'purchasePriceYuan': price['purchasePriceYuan'], 'levels': rows})
    lines.append('')

result = {
    'id': 'vehicle-integer-display-candidate-20261101-v2',
    'status': 'display-policy-confirmed-growth-formula-candidate-not-implemented',
    'source': 'candidate.json', 'baseDeliveryFeeYuan': 10,
    'pricingSource': '../2026-11-01-vehicle-economy/pricing-candidate.json',
    'rounding': 'round half up for final displayed attributes; actual full payout rounded to cents then displayed whole yuan',
    'actualSpeedCapacityPrecision': 'preserve original precise candidate values; never use rounded display values as actual attributes',
    'highTierOwnership': {
        'grades': ['S', 'SS', 'SSS'], 'scope': 'each grade independently',
        'limit': 'actual recruited riders plus protagonist',
    },
    'vehicles': vehicles,
}
report = {
    'status': 'design-arithmetic-only-not-game-verification',
    'rows': sum(len(v['levels']) for v in vehicles),
    'allDisplayedDataIntegers': all(isinstance(value, int) for v in vehicles for row in v['levels']
                                   for key, value in row.items() if value is not None),
    'roundedValuesNeverDecrease': all(all(all(a[k] <= b[k] for k in keys) for a, b in zip(v['levels'], v['levels'][1:])) for v in vehicles),
    'roundingPlateaus': counts,
    'eachLevelIncreasesActualAttributes': all(all(all(D(a[k]) < D(b[k]) for k in ['speedKph', 'capacityKg', 'totalVehicleIncomeMultiplier']) for a, b in zip(v['levels'], v['levels'][1:])) for v in SOURCE['vehicles']),
    'displayPlateausDoNotMeanActualAttributePlateaus': True,
}
(ROOT / 'integer-candidate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'integer-calculation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'integer-all-levels.md').write_text('\n'.join(lines))
for vehicle, count in zip(vehicles, counts):
    a, b = vehicle['levels'][0], vehicle['levels'][-1]
    print(f"{vehicle['grade']}: 速度{a['roundedSpeedKph']}→{b['roundedSpeedKph']}，容量{a['roundedCapacityKg']}→{b['roundedCapacityKg']}，参考展示收入{a['displayReferenceIncomeYuanAtBase10']}→{b['displayReferenceIncomeYuanAtBase10']}")
print('设计数据行数：', report['rows'], '；显示数据均为整数：', report['allDisplayedDataIntegers'])
print('仅设计文件生成与算术核对；未运行游戏、游戏测试、构建或存档操作。')
