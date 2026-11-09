"""Offline verification only; never executes or alters the first-round model."""
from pathlib import Path
import collections
import hashlib
import json
import math
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RUN = HERE / (sys.argv[1] if len(sys.argv) > 1 else "run-01")
assert RUN.parent == HERE

def read(p):
    return json.loads(p.read_text())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

checks = []
def check(name, condition, evidence=None):
    checks.append({"name": name, "ok": bool(condition), "evidence": evidence})

r = read(RUN / "result.json")
x = read(RUN / "execution.json")
identity = read(RUN / "run-identity.json")
scenario = read(RUN / "scenario.json")
p = read(ROOT / "docs/balance/2026-11-06-capacity-slots-economy/parameters.json")
ledger = read(RUN / "ledger.json")["entries"]
receipts = read(RUN / "receipts.json")
events = [json.loads(line) for line in (RUN / "events.jsonl").read_text().splitlines()]
commands = [json.loads(line) for line in (RUN / "commands.jsonl").read_text().splitlines()]
f = r["final"]
expected_inputs = read(HERE.parent / "run-identity.json")["sourceHashes"]

check("same 36 inputs before/after", len(identity["sourceHashes"]) == 36 and
      identity["sourceHashes"] == expected_inputs == x["sourceHashesAfter"] and
      all(digest(ROOT / name) == h for name, h in expected_inputs.items()))
check("all first-round files unchanged", not x["firstRoundChanges"] and
      all(digest(ROOT / name) == h for name, h in identity["firstRoundHashes"].items()),
      {"fileCount": x["firstRoundFileCount"]})
check("executed model and strategy fingerprints", digest(HERE / "run-long-term.cjs") == identity["modelSHA256"] and
      digest(HERE / "strategy.md") == identity["strategySHA256"])
check("strict domain compile and worker exit", x["compilerExit"] == 0 and x["childResult"]["code"] == 0 and
      not x["childResult"]["timedOut"] and not x["unexpected"] and not r["unexpected"])
check("precise scratch cleanup", x["cleanup"]["removed"] and not Path(x["cleanup"]["scratch"]).exists())
check("public combination restore", r["restoreValidation"] == {"ok": True})
check("raw event sequence", [v["event"] for v in events] == list(range(1, len(events) + 1)))
check("raw ledger exactly preserved", [v["entry"] for v in events if v["type"] == "ledger-entry"] == ledger)
check("all public investment commands preserved", [{k: v for k, v in ev.items() if k not in ("event", "type")} for ev in events
      if ev["type"] == "public-command"] == commands)

by_category = collections.defaultdict(int)
for row in ledger:
    by_category[row["category"]] += row["amountCents"]
check("cash independently sums from actual ledger", 10000 + sum(row["amountCents"] for row in ledger) == f["cashCents"] and
      r["cashConservation"]["residualCents"] == 0)
check("all investment and supply totals", all(-by_category[k] == value for k, value in f["spentCents"].items()))
check("actual hero/NPC income totals", by_category["hero_ordinary"] + by_category["hero_special"] == f["heroIncomeCents"] and
      by_category["npc_delivery"] == f["npcIncomeCents"])
check("unique income and order IDs", len({v["id"] for v in ledger}) == len(ledger) and
      len({v["orderId"] for v in receipts}) == len(receipts))
hero = [v for v in receipts if v["actor"] == "hero"]
npc = [v for v in receipts if v["actor"] != "hero"]
check("actual settled order counts", len(hero) == f["heroOrders"] and len(npc) == f["npcOrders"])
check("no purchased training or vehicle upgrade", f["spentCents"]["rider_upgrade"] == f["spentCents"]["vehicle_upgrade"] == 0 and
      all(v["level"] == 1 for v in f["vehicles"]) and all(v["level"] == 1 for v in f["riders"]))
check("supply allocation conserves actual charges", r["supplyAllocation"]["allocatedCents"] +
      r["supplyAllocation"]["unallocatedCents"] == f["spentCents"]["supply_purchase"] and
      sum(v["receivedCents"] - v["operatingNetCents"] for v in hero) == r["supplyAllocation"]["allocatedCents"])

entries = {v["id"]: v for v in ledger}
price_vehicle = {v["id"]: v["price"] * 100 for v in p["vehicles"]}
price_rider = {v["id"]: v["price"] * 100 for v in p["riders"]}
price_map = {v["id"]: v["price"] * 100 for v in p["maps"]}
command_errors = []
for row in commands:
    c = row["command"]
    costs = {"buyVehicle": lambda: price_vehicle[c["modelId"]], "hireRider": lambda: price_rider[c["riderId"]],
             "buyMap": lambda: price_map[c["mapId"]]}
    expected = costs[c["type"]]() if c["type"] in costs else 0
    charged = [entries[k] for k in row["ledgerEntryIds"]]
    if row["cashBeforeCents"] - row["cashAfterCents"] != expected or sum(v["amountCents"] for v in charged) != -expected:
        command_errors.append(row)
    if c["type"] not in ("buyVehicle", "hireRider", "buyMap", "selectMap", "assignVehicle"):
        command_errors.append(row)
check("every investment uses same-source price and real deduction", not command_errors,
      {"commands": len(commands), "errors": command_errors})

# Reconstruct actor/vehicle ownership only from the recorded public commands.
vehicles = {"starter-1": "starter"}
actors = {"hero": "starter-1"}
maps = {1}
cash = 10000
timeline_errors = []
tick_count = 0
quota_added = quota_used = quota_clipped = quota_stalled = 0
time_buckets = collections.defaultdict(float)
for ev in events:
    kind = ev["type"]
    if kind == "ledger-entry":
        cash += ev["entry"]["amountCents"]
        if cash < 0:
            timeline_errors.append({"event": ev["event"], "negativeCash": cash})
    elif kind == "public-command":
        c = ev["command"]
        if c["type"] == "buyVehicle":
            vehicles[ev["result"]] = c["modelId"]
        elif c["type"] == "hireRider":
            actors[c["riderId"]] = None
        elif c["type"] == "assignVehicle":
            actors[c["riderId"]] = c["vehicleId"]
        elif c["type"] == "buyMap":
            maps.add(c["mapId"])
        ids = [v for v in actors.values() if v]
        if cash != ev["cashAfterCents"] or len(ids) != len(set(ids)) or any(v not in vehicles for v in ids):
            timeline_errors.append({"event": ev["event"], "invalidCommandOwnershipOrCash": c})
    elif kind == "tick":
        tick_count += 1
        if not actors["hero"]:
            timeline_errors.append({"event": ev["event"], "heroHadNoVehicleDuringTime": True})
        if ev["quotaBeforeMs"] + ev["quotaAddedMs"] - ev["quotaConsumedMs"] - ev["quotaClippedMs"] != ev["quotaAfterMs"]:
            timeline_errors.append({"event": ev["event"], "quotaMismatch": True})
        quota_added += ev["quotaAddedMs"]
        quota_used += ev["quotaConsumedMs"]
        quota_clipped += ev["quotaClippedMs"]
        quota_stalled += ev["quotaStalledMs"]
        time_buckets[ev["bucket"]] += ev["toSeconds"] - ev["fromSeconds"]
    elif kind == "stage":
        stage = ev["stage"]
        if cash != stage["cashCents"]:
            timeline_errors.append({"event": ev["event"], "stageCashMismatch": True})
check("public-command ownership replay, cash, and hero car at every tick", not timeline_errors, timeline_errors)
check("final replay equals actual assets", vehicles == {v["id"]: v["modelId"] for v in f["vehicles"]} and
      actors == {v["id"]: v["vehicleId"] for v in f["riders"]} and maps == set(f["ownedMapIds"]) and bool(actors["hero"]))
check("quota independently sums from raw ticks", quota_added == f["quotaAddedMs"] and quota_used == f["quotaConsumedMs"] and
      quota_clipped == f["quotaClippedMs"] and quota_added - quota_used - quota_clipped == f["quotaMs"] and
      quota_stalled == round(f["quotaStalledSeconds"] * 1000) and r["quotaConservation"]["residualMs"] == 0)
check("operation and travel wall-clock partition", math.isclose(sum(time_buckets.values()), f["atSeconds"], abs_tol=1e-7) and
      all(math.isclose(time_buckets[k], v, abs_tol=1e-7) for k, v in f["operationWallSeconds"].items()))

baseline = next(v for v in read(HERE.parent / "baseline-results.json")["runs"]
                if v["id"] == "production/current-game-supply/squad-first/regular/main")
m = r["milestones"]
check("10/15 order budgets retained", m["firstCar"]["heroOrders"] == 10 and m["firstCar"]["cashCents"] == 0 and
      m["firstNPC"]["heroOrders"] == 15 and m["firstNPC"]["cashCents"] == 0 and sum(v["receivedCents"] for v in hero[:15]) == 32000)
check("first-round audited core reproduced without rerunning baseline suite",
      m["firstCar"]["atSeconds"] == baseline["first15Budget"]["car"]["seconds"] and
      m["firstNPC"]["atSeconds"] == baseline["first15Budget"]["npc"]["seconds"] and
      m["threeEquipped"]["atSeconds"] == baseline["final"]["threeEquipped"]["seconds"])
check("exact endpoint catalog denominator fixed", scenario["endpoints"]["asset80"]["catalogNumerator"] == 36 and
      scenario["endpoints"]["asset80"]["catalogDenominator"] == scenario["endpoints"]["assetFull"]["catalogDenominator"] == 45 and
      scenario["endpoints"]["assetFull"]["catalogNumerator"] == 45)
check("ratio only if both endpoint times reached", r["assetTimeRatio"] ==
      (m["asset80"]["atSeconds"] / m["assetFull"]["atSeconds"] if m["asset80"] and m["assetFull"] else None))
check("CPU/order/event/simulation bounds", r["workerCPUSeconds"] <= r["limits"]["cpuHardSeconds"] and
      f["heroOrders"] <= r["limits"]["heroOrders"] and len(events) <= r["limits"]["events"] and
      f["atSeconds"] <= r["limits"]["simulatedSeconds"] and r["iterations"] <= r["limits"]["iterations"],
      {"workerCPUSeconds": r["workerCPUSeconds"], "events": len(events), "ticks": tick_count})
check("bounded stop is explicit", r["stop"]["kind"] in ("cpu-cooperative-limit", "hero-order-limit", "event-headroom-limit",
      "simulated-time-limit", "iteration-limit", "full-asset-set-reached", "no-canonical-offers", "all-selected-rejected"))

out = {"checks": checks, "passed": sum(v["ok"] for v in checks), "failed": sum(not v["ok"] for v in checks),
       "observedEventCount": len(events), "serializedEventCountBeforeFinalMarker": r["eventCount"],
       "eventCountNote": "result.eventCount is written before the last worker-finished marker; the raw log includes that final marker.",
       "inputCount": 36, "firstRoundFileCount": x["firstRoundFileCount"], "runDirectory": str(RUN)}
(HERE / "verification.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")

coins = lambda cents: f"{cents / 100:,.2f}"
mins = lambda seconds: f"{seconds / 60:.6f}"
rows = ["# 11-07 长期经营有界实跑", "", f"验证：{out['passed']}/{len(checks)} 项通过，失败 {out['failed']}。",
        "", f"实际停止原因：`{r['stop']['kind']}`。运行到 {mins(f['atSeconds'])} 分钟（{f['atHours']:.6f} 小时），"
        f"实际亲送 {f['heroOrders']} 单、NPC 成交 {f['npcOrders']} 单。",
        f"子进程 CPU {r['workerCPUSeconds']:.3f} 秒，墙钟 {r['workerWallSeconds']:.3f} 秒；"
        f"监督/编译 CPU {x['supervisorCPUSeconds']:.3f} 秒，整体墙钟 {x['supervisorWallSeconds']:.3f} 秒。",
        "", "## 时间问题的结论", "",
        "80 节点定义为 NPC1..24 + 地图1..4 + 车型1..8，36/45 目录项，并要求主角和全部 24 名 NPC 各配不同车辆实例；"
        "完整节点为 NPC1..30 + 地图1..5 + 车型1..10，45/45，并要求 31 名演员各配车。"
        "初始地图1计入目录，初始车/主角不计目录项；配车是附加条件，25/31 不冒称精确80%。",
        "", "本轮明确排除全部付费人物训练/车辆升级（包括30级），因此只回答此资产目录定义，不能代表全内容或升级完成。",
        "", f"80 节点：{'已到达，'+mins(m['asset80']['atSeconds'])+' 分钟' if m['asset80'] else '未到达'}。"
        f"完整节点：{'已到达，'+mins(m['assetFull']['atSeconds'])+' 分钟' if m['assetFull'] else '未到达'}。",
        (f"同一路径时间比：{r['assetTimeRatio']:.8f}。" if r['assetTimeRatio'] is not None else
         "**不报告二八时间比**：两个精确节点尚未在同一路径都实际到达；没有用价格/收入比例外推。"),
        "", "## 真实购买与配车阶段", "", "| 阶段 | 分钟 | 主角/NPC单 | 配车NPC | 地图 | 已拥有车型 | 现金金币 | 累计收入金币 | 投资金币 | 补给金币 |",
        "|---|---:|---:|---:|---|---|---:|---:|---:|---:|"]
for s in r["stages"]:
    if s["label"] not in ("start", "final") and not s["label"].startswith("purchase-step-"):
        continue
    model_ids = sorted({v["modelId"] for v in s["vehicles"] if isinstance(v["modelId"], int)})
    investment = sum(v for k, v in s["spentCents"].items() if k != "supply_purchase")
    rows.append(f"| {s['label']} | {mins(s['atSeconds'])} | {s['heroOrders']}/{s['npcOrders']} | {s['equippedNPCs']} | "
                f"{','.join(map(str,s['ownedMapIds']))} | {','.join(map(str,model_ids)) or '初始车'} | {coins(s['cashCents'])} | "
                f"{coins(s['totalIncomeCents'])} | {coins(investment)} | {coins(s['spentCents']['supply_purchase'])} |")
rows += ["", f"终态配齐 {f['equippedNPCs']} 名 NPC，拥有地图 {f['ownedMapIds']}，"
         f"付费车型 {sorted({v['modelId'] for v in f['vehicles'] if isinstance(v['modelId'],int)})}。"
         f"下一固定步骤是 `{json.dumps(f['nextTask'],ensure_ascii=False)}`；已完成 {r['reachedTaskCount']}/{r['totalTaskCount']} 个购买步骤。",
         f"终态拥有 {f['assetFull']['catalogItems']}/45 个目录项；80节点还缺 NPC13..24、地图4、车型6..8及新增演员的逐实例配车。"
         "这项资产计数不用于外推剩余时间。",
         "", "首车在第10单后、首NPC在第15单后，分别为 " + mins(m["firstCar"]["atSeconds"]) + " / " +
         mins(m["firstNPC"]["atSeconds"]) + " 分钟，两个时点现金均0。前15单实际收入320金币。"
         + "三名配车NPC在 " + mins(m["threeEquipped"]["atSeconds"]) + " 分钟到达，与第一轮推荐常规路径精确相同。",
         "", "## 收入、投入、额度与操作", "",
         f"主角报价毛额 {coins(f['heroIncomeCents'] + sum(v['quotedCents']-v['receivedCents'] for v in hero))} 金币，"
         f"实际到账 {coins(f['heroIncomeCents'])}；NPC实际到账 {coins(f['npcIncomeCents'])}。"
         f"合计实际收入 {coins(f['totalIncomeCents'])}，扣实际补给后的经营净额 {coins(f['operatingNetCents'])}。"
         "经营净额没有扣资产投资；现金另外按完整账目守恒。",
         "", "| 真实扣费类别 | 金币 |", "|---|---:|"]
for k, v in f["spentCents"].items():
    rows.append(f"| {k} | {coins(v)} |")
rows += ["", f"实际单量：亲送 {f['heroOrdersPerMinute']:.6f} 单/分钟，含NPC {f['allOrdersPerMinute']:.6f} 单/分钟。"
         f"签约容量利用 {f['capacityFillRatio']:.6%}，每批 {f['meanOrdersPerBatch']:.6f} 单，"
         f"实际签约 {f['acceptedOrders']} 单、{f['batchCount']} 批，终态未交付亲送 {f['acceptedOrders']-f['heroOrders']} 单。"
         "候选池大小/请求数/1格2格数量逐批保存在 events.jsonl，不按容量假造可接数量。",
         "", f"共享额度累计增加 {f['quotaAddedMs']}ms，实际消耗 {f['quotaConsumedMs']}ms，"
         f"容量截断 {f['quotaClippedMs']}ms，终态 {f['quotaMs']}ms，消耗/增加 {f['quotaUtilization']:.6%}。"
         f"有已配车NPC但额度不足停工 {f['quotaStalledSeconds']:.6f} 秒；"
         f"无可工作的NPC批次/配车 {f['quotaNoWorkSeconds']:.6f} 秒；终态 {f['pendingNPCBatches']} 个未完NPC批次。"
         "停工按有限额度真实推进统计，没有把未到账合同当收益。",
         "", "模拟墙钟分解：" + "，".join(f"{k} {v:.6f} 秒" for k,v in f["operationWallSeconds"].items()) + "。"
         "这些是已声明的常规操作假设，不是真实玩家手速或实际等待本模拟的CPU时间。",
         "", "## 可复现证据与局限", "",
         "- `strategy.md` 在运行前固定了所有购买顺序、同一城市供给假设、操作停顿、节点和硬上限。所有车型优先换主角，"
         "空闲旧车给后续NPC，不足时买街行；前三人配齐后保留3金币补给现金。没有做其他策略/慢操作或训练对照。",
         "- 全部地图只读复用同一 prepareCity(city.json) 路网/POI；地图购买是实际领域参数变化，"
         "**不是五图玩家体验**。NPC时间是生产Fleet有限额度设计时钟，不是地图可见NPC路由。",
         "- 原始命令及exit在 `" + str(RUN / "run-identity.json") + "`、`execution.json`、`run.log`；"
         "每条领域命令/扣费、tick、批次签约、账目见 `commands.jsonl`、`events.jsonl`、`batches.json`、`ledger.json`、`receipts.json`。",
         "- `receipts.json` 保存每个主角订单原报价、到账、损坏/迟到、容量以及明确的实际补给分摊净额；"
         "不将资本开支藏入或移出经营净额。尾批未成交部分的补给分摊保留 unallocatedCents。",
         f"- 36项同源输入前后相同，首轮 {x['firstRoundFileCount']} 个文件未改。系统scratch精确清理，真实组合restore校验通过。"
         "没有生产写入、构建/部署/浏览器、用户档操作、广告成功模拟、资格恢复、赠品或余额注入。",
         f"- 原始日志 {len(events)} 条事件；result.eventCount 记录末尾 worker-finished 标记之前的数量。"
         "asset80.catalogDenominator=36 是80节点目标子集自身的大小；最终目录总分母始终45，定义以scenario.endpoints为准。",
         "- 本轮触顶是实际证据，不是已证明长期经济不可达或产品二八目标失败。继续扩大CPU/历史量、"
         "研究更高效的可审计运行方法或改变资产定义属于后续决定；本轮没有擅改生产来凑目标。",
         "", "写集交回：`" + str(HERE) + "`。第一轮及生产文件保持只读。", ""]
(HERE / "report.md").write_text("\n".join(rows))
print(json.dumps({"passed": out["passed"], "failed": out["failed"], "stop": r["stop"],
                  "simulatedMinutes": f["atMinutes"], "heroOrders": f["heroOrders"], "npcOrders": f["npcOrders"],
                  "equippedNPCs": f["equippedNPCs"], "assetTimeRatio": r["assetTimeRatio"],
                  "verification": str(HERE / "verification.json"), "report": str(HERE / "report.md")}, ensure_ascii=False))
if out["failed"]:
    print(json.dumps([v for v in checks if not v["ok"]], ensure_ascii=False, indent=2))
    sys.exit(1)
