"""Render/verify the completed, isolated domain experiment; never touches game saves."""
import csv
import hashlib
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
data = json.loads((HERE / 'baseline-results.json').read_text())
assert data.get('finishedAt'), 'Model has not completed; do not publish a partial report.'
assert data['scratchRemoved'] and not data['sourceDrift']
assert data['compilerExit'] == 0
assert hashlib.sha256((HERE / 'run-model.cjs').read_bytes()).hexdigest() == data['modelSHA256']
for name, expected in data['sourceHashes'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name

events = []
with (HERE / 'events.csv').open(newline='') as f:
    for row in csv.DictReader(f):
        events.append(json.loads(row['detail']))

names = {'squad-first': '小队优先', 'starter-upgrades-first': '旧车升至10级优先',
         'capacity-car-first': '先攒6格满载', 'npc-first-only-car': '先NPC借唯一车'}
profiles = {'regular': '常规', 'slow': '慢操作'}
def num(n, digits=2):
    return f'{n:.{digits}f}' if n is not None else '未到达'
def mins(x):
    return num(x['seconds'] / 60) if x else '未到达'
def delta(a, b):
    return num(b - a)

def npc_payback(run):
    rows = [e for e in events if e['runId'] == run['id']]
    costs = [e for e in rows if e['type'] == 'spending']
    assignments = [e for e in rows if e['type'] == 'command' and e.get('command', {}).get('type') == 'assignVehicle']
    result = []
    for rider in run['final']['riders']:
        if rider['id'] == 'hero':
            continue
        vehicle_ids = set(e['command']['vehicleId'] for e in assignments if e['command']['riderId'] == rider['id'] and e['command']['vehicleId'])
        direct_costs = [e for e in costs if e.get('riderId') == rider['id'] or e.get('vehicleId') in vehicle_ids]
        cost = sum(e['costCents'] for e in direct_costs)
        investment_at = min((e['atSeconds'] for e in direct_costs), default=0)
        total, recovered_at = 0, None
        for receipt in sorted(run['receipts'], key=lambda r: r['atSeconds']):
            if receipt['actor'] != rider['id']:
                continue
            total += receipt['incomeCents']
            if recovered_at is None and total >= cost:
                recovered_at = receipt['atSeconds']
        result.append({'riderId': rider['id'], 'vehicleIds': sorted(vehicle_ids),
                       'directCostCoins': cost / 100, 'receivedCoins': total / 100,
                       'recoveredAtMinutes': recovered_at / 60 if recovered_at is not None else None,
                       'minutesSinceInvestment': (recovered_at - investment_at) / 60 if recovered_at is not None else None,
                       'scope': 'direct cash recovery only; excludes displaced hero work, unpriced starter opportunity cost and alternative investments'})
    return result

checks = []
all_runs = data['runs'] + data['candidateRuns'] + data.get('loanSensitivity', []) + data.get('distanceSensitivity', [])
for run in all_runs:
    assert run['restoreValidated']
    final = run['final']
    hero = [r for r in run['receipts'] if r['actor'] == 'hero']
    npc = [r for r in run['receipts'] if r['actor'] != 'hero']
    assert len(hero) == final['heroOrders'] and len(npc) == final['npcOrders']
    assert sum(r['incomeCents'] for r in hero) == round(final['heroReceivedCoins'] * 100)
    assert sum(r['quotedCents'] for r in hero) == round(final['heroQuotedGrossCoins'] * 100)
    assert sum(r['incomeCents'] for r in npc) == round(final['npcReceivedCoins'] * 100)
    assert all(r['quotedCents'] == r['incomeCents'] for r in npc)
    assert sum(r.get('allocatedSupplyCents', 0) for r in hero) == run['supplyAllocation']['allocatedCents']
    assert run['supplyAllocation']['allocatedCents'] + run['supplyAllocation']['unallocatedCents'] == round(final['spentCoins']['supply_purchase'] * 100)
    assert all(r['operatingNetCents'] == r['incomeCents'] - r['allocatedSupplyCents'] for r in hero)
    for checkpoint in run['checkpoints']:
        assert checkpoint['cashCoins'] >= 0
        assert abs(checkpoint['cashCoins'] - (100 + checkpoint['totalReceivedCoins'] - sum(checkpoint['spentCoins'].values()))) < .000001
        assert checkpoint['quotaAddedMs'] - checkpoint['quotaClippedMs'] - checkpoint['quotaConsumedMs'] == checkpoint['quotaMs']
    if run['horizonMinutes'] == 60:
        assert [r['atMinutes'] for r in run['checkpoints']] == [20, 60]
    if run['policy'] == 'squad-first' and run['horizonMinutes'] == 60:
        assert final['firstCar']['heroOrders'] == 10
        assert final['firstNPC']['heroOrders'] == 15
        assert run['first15Budget']['first15IncomeCoins'] == 320
        assert final['firstNPC']['cashCents'] == 0
    checks.append({'id': run['id'], 'passed': True, 'checks': ['source-based restore', 'earned cash reconciliation', 'per-order gross/net', 'exact finite quota reconciliation', 'checkpoints']})

production = [r for r in data['runs'] if r['scenario'] == 'current-game-supply']
assert len(data['runs']) == 16 and len(production) == 8
assert len(data['candidateRuns']) == 16 and len(data['candidates']) == 1

summary = {'status': 'first-round-model-complete; production-not-edited; not player/balance acceptance',
           'command': data['command'], 'modelSHA256': data['modelSHA256'],
           'runs': [], 'candidateComparisons': [], 'verification': checks,
           'longTerm80Percent': {'timeRatio': None, 'reason': '24 NPC + 4 maps + first 8 models and full-30 denominator not simulated. The 20/60 minute policies stop buying at 3 NPC and never purchase maps. Old 19.91/27.41/385.68/1935.03 timings cannot be inherited.'}}

for run in data['runs']:
    pools = [e for e in events if e['runId'] == run['id'] and e['type'] == 'candidate-pool']
    summary['runs'].append({'id': run['id'], 'checkpoints': run['checkpoints'], 'npcDirectCashPayback': npc_payback(run),
                            'supply': {'poolMin': min((e['offers'] for e in pools), default=0),
                                       'poolMax': max((e['offers'] for e in pools), default=0),
                                       'poolMean': statistics.mean(e['offers'] for e in pools) if pools else 0,
                                       'actualSignedOrdersMin': min((len(b['orders']) for b in run['batches']), default=0),
                                       'actualSignedOrdersMax': max((len(b['orders']) for b in run['batches']), default=0)}})

for candidate in data['candidateRuns']:
    baseline = next(r for r in data['runs'] if all(r[k] == candidate[k] for k in ['scenario', 'policy', 'operationProfile']))
    a, b = baseline['final'], candidate['final']
    summary['candidateComparisons'].append({'scenario': baseline['scenario'], 'policy': baseline['policy'], 'profile': baseline['operationProfile'],
        'baselineReceivedCoins': a['totalReceivedCoins'], 'candidateReceivedCoins': b['totalReceivedCoins'],
        'receivedDeltaCoins': b['totalReceivedCoins'] - a['totalReceivedCoins'],
        'baselineOperatingNetPerMinute': a['operatingNetCoinsPerMinute'], 'candidateOperatingNetPerMinute': b['operatingNetCoinsPerMinute'],
        'baselineSquadMinutes': a['threeEquipped']['seconds'] / 60 if a['threeEquipped'] else None,
        'candidateSquadMinutes': b['threeEquipped']['seconds'] / 60 if b['threeEquipped'] else None,
        'baselineSoftlock': a['softLock'], 'candidateSoftlock': b['softLock'],
        'sameBatchOfferSequence': [x['orders'] for x in baseline['batches']] == [x['orders'] for x in candidate['batches']],
        'comparisonScope': 'same source/supply/start/profile/policy; affordability can change purchase times and later accepted batch packing'})

distance = []
for run in data['distanceSensitivity']:
    # Measure the post-protection target-distance section, excluding the earned prefix.
    batches = [b for b in run['batches'] if all(o['deliveryMetres'] == int(run['scenario'].split('-')[-1]) for o in b['orders'])]
    after_safe = [b for b in batches if len([r for r in run['receipts'] if r['actor'] == 'hero' and r['atSeconds'] < b['acceptedAt']]) >= 15]
    ids = set(o['id'] for b in after_safe for o in b['orders'])
    receipts = [r for r in run['receipts'] if r['orderId'] in ids]
    begin = min((b['acceptedAt'] for b in after_safe), default=1200)
    minutes = (1200 - begin) / 60
    gross = sum(r['quotedCents'] for r in receipts) / 100
    received = sum(r['incomeCents'] for r in receipts) / 100
    net = sum(r['operatingNetCents'] for r in receipts) / 100
    distance.append({'heldMetres': int(run['scenario'].split('-')[-1]), 'minutesAfterEarnedPrefix': minutes,
                     'completedOrders': len(receipts), 'grossCoins': gross, 'receivedCoins': received,
                     'allocatedOperatingNetCoins': net, 'netCoinsPerMinute': net / minutes if minutes else None,
                     'firstQuoteCoins': receipts[0]['quotedCents'] / 100 if receipts else None,
                     'meanAcceptanceToCompletionSeconds': statistics.mean(r['acceptanceToCompletionSeconds'] for r in receipts) if receipts else None,
                     'stop': run['final']['stop']})
summary['distanceSensitivity'] = distance

p = json.loads((ROOT / 'docs/balance/2026-11-06-capacity-slots-economy/parameters.json').read_text())
# Correct non-overlapping reference inventory: 8 distinct paid models plus 16 duplicate
# streets + starter = 25 vehicles. No map operating uplift or future earnings assumption.
summary['longTerm80Percent']['referenceAssetBudgetCoins'] = sum(r['price'] for r in p['riders'][:24]) + 16 * p['vehicles'][0]['price'] + sum(m['price'] for m in p['maps'][:4]) + sum(v['price'] for v in p['vehicles'][:8])
summary['longTerm80Percent']['costNote'] = 'Reference legal inventory: 24 NPC + hero, 1 starter + 8 different paid models + 16 duplicate streets; first 4 maps; all level 1. Budget only, no time estimate or proof of optimality.'

candidate_document = {'status': 'not-approved; isolated sensitivity only; no production changes',
    'id': 'C-base10000-slope0.5', 'basedOn': '../pm/candidate-curves.json#candidate-C',
    'changes': {'protectedFirst15': 'unchanged', 'baseBasisPoints': {'before': 9000, 'candidate': 10000},
                'basisPointsPerDeliveryMetre': {'before': 1, 'candidate': .5}, 'deliveryMetresCap': 2000},
    'unchanged': ['purchase/hire/upgrade fees', 'NPC contracts and shared quota', 'special orders', 'assets and levels', 'production source'],
    'compatibilityNotImplemented': 'The experiment replaces a scratch-module export under the current policy ID. Shipping the same replacement would make current formula validators disagree with some historical signed quotes. PM must design/version future signing separately and preserve old contracts before any integration.',
    'sourceHashes': data['sourceHashes'], 'comparisons': summary['candidateComparisons']}

lines = ['# 数值平衡第一轮：开发A真实领域模型', '',
    '已完成16条基线路径、1个未批准报价候选的16条同策略路径，另有唯一车借用与距离敏感性。生产源码/参数、UI、地图和用户存档未写；这是隔离领域模型，不是实际玩家或全产品验收。', '',
    f'实际命令：`{data["command"]}`；严格编译exit 0，模型exit 0，scratch已精确清理。模型SHA256 `{data["modelSHA256"]}`；36项源码/参数/供给SHA见run-identity.json。', '',
    '命令中的.hermes/node/bin/node是当前PATH解析的本地Node可执行文件；执行的是本模型脚本，未启动Hermes Agent或调用其模型通道。BB本会话Provider已读回codex，同环境接续。', '',
    '## 运行口径', '',
    '每条从new V2GameSession的100金币/2格开始，只用实际Game/Route/Dispatch/Economy/Fleet公开方法赚取、扣费、取送、分配和结算；结束快照经真实restore校验。首轮无广告、无赠品、无注资、无强开地图。', '',
    '真实供给按V2GameBootstrap同一prepareCity(city.json)链路只读载入；100m走廊另列为敏感性小场景，不是游戏地理。道路40游戏秒/现实秒，取2秒/送1秒，风险/天气/体力/逐单迟到均由生产函数计算。NPC实际使用有限共享经营钟，其路程仍是Fleet的设计时钟。', '',
    '常规操作等待：大厅4秒、每选一单0.6秒、选路2秒、取餐/继续各1秒、结算阅读2秒、每笔投资3秒、补给菜单2秒；慢操作对应12/2/6/4/4/6/9/6秒。等待只放在停止/菜单状态；两者道路速度与服务时长完全相同。当前Game在pickup/ready停止时不增加行程钟，NPC经营仍按真实墙钟推进。', '',
    '供给采用稳定有限池的原顺序first-fit，容量允许便继续选；真实安全路程/体力拒绝才从尾部减少组合，不刷新或重抽。推荐路径在10/15单处留投资检查点。旧车路径先升旧车至10级才买街行；容量路径先攒1000金币买满载；两者随后同样扩到3名NPC。没有买图或额外训练来污染这轮前期对照。', '',
    '旧车路径沿同一分工把街行给主角、升级旧车交NPC；此时主角从6格旧车换到3格街行，速度/收益也较低。这是明确可复跑的投资/分工样本，不是升级策略最优解；不能据该样本推断所有先升级路径都比买车差。另行保留升级旧车给主角的优化分支尚未运行。', '',
    '三条扩队路径配齐3名NPC后统一存钱，本轮不继续扩第4人或买图。因此60分是固定小队/既定分工下的经营积累对照，不代表持续最优投资路径或完整成长曲线。配车命令的点击时间合并在对应投资菜单等待内，不另加逐条命令时长。', '',
    '毛收入=签约报价；实收=真实迟到/餐损结算后；每单经营净=实收－该批补给的整数分分摊。批前补给归下一批、未完成订单的分摊单列未分配；购车/招募/升级资本支出分开记，现金变化包含所有扣款。', '',
    '## 当前游戏供给：20/60分钟', '',
    '|操作/策略|20分亲送/NPC|20分实收/经营净|20分现金|60分亲送/NPC|60分实收/经营净|60分现金|60分净/分钟|',
    '|---|---:|---:|---:|---:|---:|---:|---:|']
for run in production:
    a, b = run['checkpoints']
    lines.append(f'|{profiles[run["operationProfile"]]}·{names[run["policy"]]}|{a["heroOrders"]}/{a["npcOrders"]}|{num(a["totalReceivedCoins"])}/{num(a["operatingNetCoins"])}|{num(a["cashCoins"])}|{b["heroOrders"]}/{b["npcOrders"]}|{num(b["totalReceivedCoins"])}/{num(b["operatingNetCoins"])}|{num(b["cashCoins"])}|{num(b["operatingNetCoinsPerMinute"])}|')
lines += ['', '|操作/策略|首车：分/亲送单|首NPC：分/亲送单|3名均配车：分|60分升级/购车/招募/补给支出|', '|---|---:|---:|---:|---:|']
for run in production:
    x=run['final'];s=x['spentCoins']
    lines.append(f'|{profiles[run["operationProfile"]]}·{names[run["policy"]]}|{mins(x["firstCar"])} / {x["firstCar"]["heroOrders"] if x["firstCar"] else "—"}|{mins(x["firstNPC"])} / {x["firstNPC"]["heroOrders"] if x["firstNPC"] else "—"}|{mins(x["threeEquipped"])}|{num(s["vehicle_upgrade"]+s["rider_upgrade"])}/{num(s["vehicle_purchase"])}/{num(s["rider_hire"])}/{num(s["supply_purchase"])}|')
lines += ['', '推荐路径首15单实收320金币：100＋10×20－300＝0；再5×24－120＝0。模型实际保住第10/15单与零余额，不把这两笔预算结论扩成时间保证。', '',
    '|操作/策略|容量实装占比|平均每批单数|真实候选池范围|每批实际可接单范围|额度已消耗/累计补充|额度截顶丢失|有车无额度停工秒|', '|---|---:|---:|---:|---:|---:|---:|---:|']
for run in production:
    x=run['final'];s=next(s for s in summary['runs'] if s['id']==run['id'])['supply']
    lines.append(f'|{profiles[run["operationProfile"]]}·{names[run["policy"]]}|{num(100*x["heroCapacityFillRatio"])}%|{num(x["meanOrdersPerBatch"])}|{s["poolMin"]}～{s["poolMax"]}|{s["actualSignedOrdersMin"]}～{s["actualSignedOrdersMax"]}|{num(x["quotaConsumedMs"]/60000)}/{num(x["quotaAddedMs"]/60000)}分|{num(x["quotaClippedMs"]/60000)}分|{num(x["quotaStalledSeconds"])}|')
lines += ['', '额度是全队共用墙钟，不按骑手人数翻倍；多名NPC并行会提高同一份额度的产出。额度利用低可能来自截顶，不等于NPC一直停工；上表分别列出。', '',
    '## 扩队实际现金回收', '',
    '下表是分配给该NPC的招募＋车辆购置/升级支出，用其真实累计入账回收的时点；旧车记实际支付0。它排除了主角让车的机会成本、替代投资和时间节省，不能当完整因果ROI。', '',
    '|真实供给操作/策略|人物|直接投入|60分累计实收|现金回收于开局分钟|投入后分钟|', '|---|---|---:|---:|---:|---:|']
for run in production:
    for row in npc_payback(run):
        lines.append(f'|{profiles[run["operationProfile"]]}·{names[run["policy"]]}|{row["riderId"]}|{num(row["directCostCoins"])}|{num(row["receivedCoins"])}|{num(row["recoveredAtMinutes"])}|{num(row["minutesSinceInvestment"])}|')
lines += ['', '旧车升10级实际支出805金币，容量/速度/收益同时变化；与买满载1000金币、扩队的差异应看上面的每分钟经营净、可接组合和配车时点，不能把231次不加格升级都判为无价值。前期路径对照同时改变资产与后续可接批次，未做同一60分合法状态上逐项投入的因果分支回本。', '',
    '## 唯一旧车先给NPC：实际阻塞', '']
for run in production:
    if run['policy']=='npc-first-only-car':
        s=run['final']['stop']
        lines.append(f'- {profiles[run["operationProfile"]]}：亲送{run["final"]["heroOrders"]}单后招NPC并借唯一车；{num(s["seconds"]/60)}分额度耗尽，余额{s["cashCents"]/100:g}金币、{s["unpaidOrders"]}份未付合同。归还主角：`{s["errors"].get("returnToHero")}`；买替代车：`{s["errors"].get("buyReplacement")}`。')
lines += ['', '这里实际执行了NPC卸车及主角重新配车命令；卸下未来配车不会撤销旧合同车辆保留。无广告、无赠品、无外部余额来源的范围内已经没有亲送和自动经营收入入口。免费休息不补经营额度。修复需要PM设计旧合同与配车的解脱行为；本报价候选不能解决。', '',
    '|借车前完成亲送数（代表性场景）|结束时亲送/NPC|现金|结果|', '|---:|---:|---:|---|']
for run in data['loanSensitivity']:
    x=run['final'];lines.append(f'|{run["id"].split("loan-after-")[-1]}|{x["heroOrders"]}/{x["npcOrders"]}|{num(x["cashCoins"])}|{x["stop"]["kind"] if x["stop"] else "已合法恢复或赚得替代车；见recoveries"}|')
lines += ['', '## 距离与每分钟收益', '',
    '同一混合走廊先真实赚满安全前缀，再仅选指定持餐距离；所有到店空驶仍走真实道路。下表仅统计前缀之后至20分钟的目标段，包含读单/取送/补给及末尾未完成时间，不是供给分布。', '',
    '|持餐距离m|目标段分钟|完成单数|首报价|实收|分摊经营净/分钟|平均接单到交付秒|', '|---:|---:|---:|---:|---:|---:|---:|']
for r in distance:
    lines.append(f'|{r["heldMetres"]}|{num(r["minutesAfterEarnedPrefix"])}|{r["completedOrders"]}|{num(r["firstQuoteCoins"])}|{num(r["receivedCoins"])}|{num(r["netCoinsPerMinute"])}|{num(r["meanAcceptanceToCompletionSeconds"])}|')
lines += ['', '当前2000m/4000m报价相同而墙钟不同的风险不能用平均单价掩盖；该敏感性还包含空驶差异，无法归因全部差额给持餐段。', '',
    '## 仅1项未批准候选', '',
    'C：前15保护不动；保护后基数9000→10000、每米基点1→0.5，仍封顶2000m。只替换临时编译模块内的规则导出，生产文件与所有资产费用未动。PM已有报价敏感性：354m为19.27→20.96；2000/4000m仍22.66。候选数据不是获批新合同，也未验证历史报价兼容。', '',
    '|当前游戏供给操作/策略|60分基线实收|候选实收|差额|基线→候选3NPC分钟|', '|---|---:|---:|---:|---:|']
for r in summary['candidateComparisons']:
    if r['scenario']=='current-game-supply':
        lines.append(f'|{profiles[r["profile"]]}·{names[r["policy"]]}|{num(r["baselineReceivedCoins"])}|{num(r["candidateReceivedCoins"])}|{num(r["receivedDeltaCoins"])}|{num(r["baselineSquadMinutes"])} → {num(r["candidateSquadMinutes"])}|')
lines += ['', '对照保证相同起点、源码、供给、操作假设与策略；可负担时点变化可能改变后续组单，summary.json保留sameBatchOfferSequence，不伪称逐单序列全相同。保护内1单即借车的软锁仍在。候选只是报价边界修复的平衡输入，不以抬收藏尾价/加补贴或恢复购买资格凑目标。', '',
    '兼容门禁：试验仅在scratch内沿当前policy ID替换规则；若直接这样上线，当前校验器会按新公式重算部分旧已签报价并拒绝。这个试验不是迁移实现。旧报价/合同、资产/等级/金币保留与未来接单版本边界，仍须PM单独串行设计。', '',
    '## 二八与尚未覆盖', '',
    f'本轮60分策略最多只扩到3名NPC，没有购买地图；不能产生24/30 NPC、4/5地图、前8/10车型的80%资产节点，更没有30人均配车的同路径时间分母。当前参数下，一套明确参考资产预算为{summary["longTerm80Percent"]["referenceAssetBudgetCoins"]:,.0f}金币（24NPC＋1旧车＋8款付费车＋16台街行＋前4地图，均1级），这是金额账，不是时间预测。', '',
    '因此二八时间比例仍未验证；旧19.91/27.41分钟小队及385.68/1935.03分钟长期结论不能继承。长期多图、24/30NPC、离线会话与尾段训练需独立同源路径重跑；不能用本轮NPC收入占比冒充二八内容比例。', '',
    '真实广告SDK、UI操作、手机/GPU性能、长期留存、所有地图可玩内容和旧已签合同迁移均不在本模型证据范围。已签合同/资产/金币/等级的兼容设计由PM串行负责。', '',
    '## 可复跑证据', '',
    '- `run-model.cjs`：真实领域严格临时编译、合法路径、候选和scratch清理。',
    '- `baseline-results.json`：完整20/60分、每批、每单毛/实收/净、资金与额度。',
    '- `events.csv`：接单、出发、投资/配车命令、真实扣费、交付、拒绝和单笔账目时点；逐次等待和取餐/继续点击未单列事件，其执行顺序在模型脚本。',
    '- `order-economics.csv`：逐单报价、实收、补给分摊与经营净；生产Fleet不对NPC另扣补给，因此NPC经营净等于实收，资本支出另列。',
    '- `summary.json`：紧凑比较、NPC直接现金回收、距离与候选差异。',
    '- `run-identity.json` / `run.log`：命令、编译版本、36项输入SHA、exit与临时目录清理。',
    '- `candidate-01.json`：唯一候选与对照，明确未批准及未实施的旧合同兼容门禁。',
    '- `initial-representative-run/`：首轮原始结果原样保留；初始额度统计/借车阈值口径已由最终模型纠正，不能混用。',
    '- `failed-full-run/` / `quota-statistic-fix/`：先前16条基线、失败断言、600ms原始证据与窄RED/GREEN。最终为补齐同一版本完整事件CSV和候选才跑完整记录，未重新运行旧95项产品测试。', '',
    f'`python3 {HERE.relative_to(ROOT)}/summarize.py`已核对{len(checks)}条结果的现金、每单收入/补给分摊、有限额度守恒、检查点和自然快照恢复证据。']

(HERE / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
(HERE / 'candidate-01.json').write_text(json.dumps(candidate_document, ensure_ascii=False, indent=2) + '\n')
with (HERE / 'order-economics.csv').open('w', newline='') as f:
    columns = ['runId', 'actor', 'orderId', 'completedAtSeconds', 'quotedGrossCents', 'receivedCents', 'allocatedSupplyCents', 'operatingNetCents', 'deliveryMetres', 'occupiedSlots', 'capacitySlots', 'acceptanceToCompletionSeconds', 'damage', 'lateGameSeconds']
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    for run in all_runs:
        for r in run['receipts']:
            writer.writerow({'runId': run['id'], 'actor': r['actor'], 'orderId': r['orderId'],
                'completedAtSeconds': r['atSeconds'], 'quotedGrossCents': r['quotedCents'],
                'receivedCents': r['incomeCents'], 'allocatedSupplyCents': r.get('allocatedSupplyCents', 0),
                'operatingNetCents': r.get('operatingNetCents', r['incomeCents']),
                **{k: r.get(k, '') for k in ['deliveryMetres', 'occupiedSlots', 'capacitySlots', 'acceptanceToCompletionSeconds', 'damage', 'lateGameSeconds']}})
(HERE / 'report.md').write_text('\n'.join(lines) + '\n')
(HERE / 'verification.json').write_text(json.dumps({'exit': 0, 'runsChecked': len(checks), 'baselineRuns': len(data['runs']), 'candidateRuns': len(data['candidateRuns']), 'modelSHA256': data['modelSHA256'], 'summaryGeneratorSHA256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(), 'sourceSHAUnchanged': True, 'scratchRemoved': True, 'checks': checks}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'exit': 0, 'runsChecked': len(checks), 'report': str(HERE / 'report.md'), 'summary': str(HERE / 'summary.json')}, ensure_ascii=False))
