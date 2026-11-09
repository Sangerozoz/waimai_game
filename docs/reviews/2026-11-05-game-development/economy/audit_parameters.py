"""Read-only source/parameter comparison and independent arithmetic; no game imports/tests/saves."""
import json, math, hashlib, re
from pathlib import Path
root=Path(__file__).resolve().parents[4]
params_path=root/'docs/balance/2026-11-04-frontloaded-economy/parameters.json'
ts_path=root/'delivery-game/assets/scripts/domain/V2EconomyConfig.ts'
p=json.loads(params_path.read_text()); ts=ts_path.read_text()
c=json.loads(ts.split('export const V2_CONFIG = ',1)[1].rsplit(' as const;',1)[0])
def leaves(value):
 if isinstance(value,dict): return sum(leaves(v) for v in value.values())
 if isinstance(value,list): return sum(leaves(v) for v in value)
 return 1
half=lambda v:math.floor(v+.5)
mismatches=[]
for row in p['upgradeLevels']:
 l=row['level']
 expected=[0,11,39,81,136][l-1] if l<=5 else half(136+55*(l-5)+89*(l-5)*(l-6)/600)
 if row['riderCumulativeCost']!=expected:mismatches.append(['rider',l,expected,row['riderCumulativeCost']])
 for i,v in enumerate(p['vehicles']):
  basis=v['price']; c5=half(3*basis*(4/29)**1.65)
  expected=half(3*basis*((l-1)/29)**1.65) if l<=5 else half(c5+(1.5*basis-c5)*((l-5)/25)**1.3)
  if expected!=row['vehicleCumulativeCosts'][i]:mismatches.append(['vehicle',v['id'],l,expected,row['vehicleCumulativeCosts'][i]])
steps=[(p['upgradeLevels'][i]['riderCumulativeCost']-p['upgradeLevels'][i-1]['riderCumulativeCost'])*100 for i in range(1,30)]
vehicle_totals=[sum((p['upgradeLevels'][i]['vehicleCumulativeCosts'][j]-p['upgradeLevels'][i-1]['vehicleCumulativeCosts'][j])*100 for i in range(1,30)) for j in range(10)]
starter=[]
for l in range(1,31):
 basis=p['starterVehicle']['upgradeCostBasis']; c5=half(3*basis*(4/29)**1.65)
 starter.append(half(3*basis*((l-1)/29)**1.65) if l<=5 else half(c5+(1.5*basis-c5)*((l-5)/25)**1.3))
cases=[]
for owned,cash in [([1],10000),([1],150000),([1,2],0),([1,5],0),([1,2,3,4,5],0)]:
 paid=[m for m in p['maps'] if m['id']!=p['maps'][0]['id'] and m['price']>0]
 completed=any(m['id'] in owned for m in paid)
 prices=[m['price']*100 for m in paid if m['id'] not in owned]
 price=min(prices) if prices else None
 cases.append(dict(ownedMapIds=owned,cashCents=cash,completed=completed,priceCents=price,shortfallCents=0 if completed or price is None else max(0,price-cash),canGo=not completed and (price is None or cash>=price)))
report={'scope':'static JSON extraction + independent arithmetic only; no TS/game/test/typecheck execution', 'configId':p['configId'],'tsConfigId':re.search("V2_CONFIG_ID = '([^']+)'",ts).group(1),'exactDeepEquality':c==p,'scalarLeafCount':leaves(p),'sha256':{str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [params_path,ts_path,root/'delivery-game/assets/scripts/domain/V2ProgressTargets.ts']},'formulaMismatches':mismatches,'riderFirstFiveCumulative': [x['riderCumulativeCost'] for x in p['upgradeLevels'][:5]],'riderUpgradeStepsCents':steps,'riderUpgradeSumCents':sum(steps),'vehicleUpgradeSumCents':vehicle_totals,'vehicleMaxExpectedCents':[round(v['price']*150) for v in p['vehicles']],'starterCumulativeCoins':starter,'starterUpgradeSumCents':(starter[-1]-starter[0])*100,'riderMaxEffects':p['maxRiderUpgradeEffects'],'firstPaidMapIndependentScenarios':cases,'introArithmetic':{'startCoins':p['startCoins'],'tenOrdersCashCoins':p['startCoins']+10*20,'afterFirstCarCoins':p['startCoins']+10*20-300,'nextFiveOrdinaryCoins':5*24,'afterFirstNpcCoins':p['startCoins']+10*20-300+5*24-120},'notVerified':['TS execution','typecheck','gameplay','user saves','balance acceptance','runtime/UI integration']}
output=Path(__file__).with_name('parameter-consistency.json');output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['exactDeepEquality','scalarLeafCount','formulaMismatches','riderUpgradeSumCents','vehicleUpgradeSumCents','starterUpgradeSumCents','introArithmetic']},ensure_ascii=False))
