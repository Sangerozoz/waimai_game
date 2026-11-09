"""PM offline admission of saved records; does not execute the model or edit A files."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MODEL = HERE.parent / "a/long-term-1107"
RUN = MODEL / "run-01"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


r = read(RUN / "result.json")
x = read(RUN / "execution.json")
i = read(RUN / "run-identity.json")
f = r["final"]
ledger = read(RUN / "ledger.json")["entries"]
receipts = read(RUN / "receipts.json")
commands = [json.loads(s) for s in (RUN / "commands.jsonl").read_text().splitlines()]
events = [json.loads(s) for s in (RUN / "events.jsonl").read_text().splitlines()]
params = read(ROOT / "docs/balance/2026-11-06-capacity-slots-economy/parameters.json")
checks = []


def verify(name, condition):
    checks.append({"name": name, "passed": bool(condition)})


verify("36 historical input fingerprints match before integration",
       len(i["sourceHashes"]) == 36 and i["sourceHashes"] == x["sourceHashesAfter"]
       and all(sha(ROOT / p) == h for p, h in i["sourceHashes"].items()))
verify("35 first-round files unchanged", len(i["firstRoundHashes"]) == 35
       and not x["firstRoundChanges"]
       and all(sha(ROOT / p) == h for p, h in i["firstRoundHashes"].items()))
verify("strict compile and bounded worker actually exited zero", x["compilerExit"] == 0
       and x["childResult"] == {"code": 0, "signal": None, "timedOut": False}
       and not x["unexpected"] and not r["unexpected"])
verify("scratch removed and combination restored", x["cleanup"]["removed"]
       and not Path(x["cleanup"]["scratch"]).exists()
       and r["restoreValidation"] == {"ok": True})
verify("model and declared strategy fingerprints", sha(MODEL / "run-long-term.cjs") == i["modelSHA256"]
       and sha(MODEL / "strategy.md") == i["strategySHA256"])
verify("raw ledger and commands match event log", ledger == [e["entry"] for e in events if e["type"] == "ledger-entry"]
       and commands == [{k: v for k, v in e.items() if k not in ("event", "type")}
                        for e in events if e["type"] == "public-command"])
categories = Counter()
for row in ledger:
    categories[row["category"]] += row["amountCents"]
verify("cash sums from opening 100 coins", 10000 + sum(categories.values()) == f["cashCents"])
verify("no grants or simulated advertising income", set(categories) <= {
       "hero_ordinary", "npc_delivery", "vehicle_purchase", "rider_hire", "map_purchase", "supply_purchase"})
verify("all spending and income totals reconcile", all(-categories[k] == v for k, v in f["spentCents"].items())
       and categories["hero_ordinary"] == f["heroIncomeCents"]
       and categories["npc_delivery"] == f["npcIncomeCents"])
hero = [v for v in receipts if v["actor"] == "hero"]
npc = [v for v in receipts if v["actor"] != "hero"]
verify("actual unique payouts and counts", len({v["id"] for v in ledger}) == len(ledger)
       and len({v["orderId"] for v in receipts}) == len(receipts)
       and len(hero) == f["heroOrders"] == 771 and len(npc) == f["npcOrders"] == 884
       and sum(v["receivedCents"] for v in hero) == f["heroIncomeCents"]
       and sum(v["receivedCents"] for v in npc) == f["npcIncomeCents"])

prices = {"buyVehicle": {v["id"]: v["price"] * 100 for v in params["vehicles"]},
          "hireRider": {v["id"]: v["price"] * 100 for v in params["riders"]},
          "buyMap": {v["id"]: v["price"] * 100 for v in params["maps"]}}
key = {"buyVehicle": "modelId", "hireRider": "riderId", "buyMap": "mapId"}
entries = {v["id"]: v for v in ledger}
cost_errors = []
for row in commands:
    c = row["command"]
    cost = prices[c["type"]][c[key[c["type"]]]] if c["type"] in prices else 0
    if row["cashBeforeCents"] - row["cashAfterCents"] != cost or sum(
            entries[k]["amountCents"] for k in row["ledgerEntryIds"]) != -cost:
        cost_errors.append(row)
verify("each recorded purchase matches independent parameter-table price", not cost_errors)

actors = {"hero": "starter-1"}
cars = {"starter-1": "starter"}
maps = {1}
cash = 10000
bad_timeline = []
quota = Counter()
for e in events:
    if e["type"] == "ledger-entry":
        cash += e["entry"]["amountCents"]
        if cash < 0:
            bad_timeline.append(e["event"])
    elif e["type"] == "public-command":
        c = e["command"]
        if c["type"] == "buyVehicle":
            cars[e["result"]] = c["modelId"]
        elif c["type"] == "hireRider":
            actors[c["riderId"]] = None
        elif c["type"] == "assignVehicle":
            actors[c["riderId"]] = c["vehicleId"]
        elif c["type"] == "buyMap":
            maps.add(c["mapId"])
        ids = [v for v in actors.values() if v is not None]
        if cash != e["cashAfterCents"] or len(ids) != len(set(ids)) or any(v not in cars for v in ids):
            bad_timeline.append(e["event"])
    elif e["type"] == "tick":
        if not actors["hero"] or e["quotaBeforeMs"] + e["quotaAddedMs"] - e["quotaConsumedMs"] - e["quotaClippedMs"] != e["quotaAfterMs"]:
            bad_timeline.append(e["event"])
        for name in ("quotaAddedMs", "quotaConsumedMs", "quotaClippedMs"):
            quota[name] += e[name]
verify("public actions replay ownership and nonnegative cash with hero equipped at each tick", not bad_timeline
       and actors == {v["id"]: v["vehicleId"] for v in f["riders"]}
       and cars == {v["id"]: v["modelId"] for v in f["vehicles"]} and maps == set(f["ownedMapIds"]))
verify("finite quota conserves independently", all(quota[k] == f[k] for k in quota)
       and quota["quotaAddedMs"] - quota["quotaConsumedMs"] - quota["quotaClippedMs"] == f["quotaMs"])
verify("10 and 15 delivery purchase budgets preserved", r["milestones"]["firstCar"]["heroOrders"] == 10
       and r["milestones"]["firstNPC"]["heroOrders"] == 15
       and r["milestones"]["firstCar"]["cashCents"] == r["milestones"]["firstNPC"]["cashCents"] == 0)
verify("endpoint ratio withheld until both actual endpoints", r["assetTimeRatio"] is None
       and r["milestones"]["asset80"] is None and r["milestones"]["assetFull"] is None)
verify("bounded stop is within declared CPU/order/event/time limits", r["stop"]["kind"] == "cpu-cooperative-limit"
       and r["workerCPUSeconds"] <= r["limits"]["cpuHardSeconds"]
       and f["heroOrders"] <= r["limits"]["heroOrders"]
       and len(events) <= r["limits"]["events"]
       and f["atSeconds"] <= r["limits"]["simulatedSeconds"])

report = {"capturedAt": datetime.now(timezone.utc).isoformat(), "pm": "thr_4xmqy6fzdm",
          "scope": "Independent offline saved-record admission; no model rerun, browser, or user save access",
          "checks": checks, "passed": sum(v["passed"] for v in checks),
          "failed": sum(not v["passed"] for v in checks),
          "evidence": {str(p.relative_to(ROOT)): sha(p) for p in (
              MODEL / "report.md", MODEL / "strategy.md", MODEL / "verification.json", RUN / "result.json",
              RUN / "execution.json", RUN / "run-identity.json", RUN / "events.jsonl", RUN / "commands.jsonl",
              RUN / "ledger.json", RUN / "receipts.json")},
          "observed": {"minutes": f["atMinutes"], "heroOrders": f["heroOrders"], "npcOrders": f["npcOrders"],
                       "equippedNPCs": f["equippedNPCs"], "maps": f["ownedMapIds"],
                       "paidModels": sorted({v for v in cars.values() if isinstance(v, int)}),
                       "cashCents": f["cashCents"], "workerCPUSeconds": r["workerCPUSeconds"],
                       "assetTimeRatio": None},
          "limits": ["same city reused for every mapId", "paid training and vehicle upgrades excluded",
                     "partial asset path only; long-term 80/20 target still unverified",
                     "historical source fingerprints apply before the separately approved prevention patch"]}
(HERE / "long-term-admission-1107.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"passed": report["passed"], "failed": report["failed"], "observed": report["observed"]}, ensure_ascii=False))
if report["failed"]:
    raise SystemExit(1)
