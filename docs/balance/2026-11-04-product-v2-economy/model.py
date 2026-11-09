"""Design arithmetic only. Does not read/write game state or run the game."""
import json, math
from pathlib import Path
ROOT=Path(__file__).parent
MAPS=[('晴川县',0,20,2),('云浦市',6000,27,3),('星澜城',35000,37,5),('曜川都会',150000,51,7),('海境港',600000,70,10)]
CARS=[('街行',300,1.1,3,1.2),('轻燕',900,1.3,4,1.3),('满载',2000,1.15,7,1.4),('城风',4000,1.5,6,1.55),('远途',7500,1.4,10,1.7),('疾影',13000,1.8,8,1.85),('重航',22000,1.6,15,2),('星驰',36000,2,12,2.15),('金穗',56000,1.85,20,2.35),('晨光',85000,2.2,18,2.5)]
def half(x): return math.floor(x+0.5)
def hire(n):return 120 if n==1 else 10*half(40*(n-1)**2.7)
def upgrades(p,l):return half(3*p*((l-1)/29)**1.65)
def training(l):return half(4800*((l-1)/29)**1.8)
def rate(car,region,level=1,rider=1):
    _,p,s,c,a=car
    x=((level-1)/29)**.65; y=((rider-1)/29)**.65
    s*=1+.2*x;c*=1+.25*x;a*=1+.2*x
    _,_,fee,density=MAPS[region]
    k=min(c/2,density)
    seconds=60/s*(1+.25*(k-1))+30*k*(1-.15*y)
    gross=k*fee*a*(1+.2*y)
    return {'expectedBatchOrders':round(k,3),'expectedBatchSeconds':round(seconds,3),'coinsPerMinute':round(60*gross/seconds,3)}
config={'status':'proposal-not-approved-not-runtime','startCoins':100,'intro':{'ordinaryOrders1To10NetCoins':20,'firstCarPrice':300,'ordinaryOrders11To15NetCoinsWithFirstCar':24,'firstRiderPrice':120,'safeOrders':15,'noPaidSuppliesRequired':True},'maps':[{'id':i+1,'name':m[0],'price':m[1],'ordinaryBaseFee':m[2],'expectedBatchDensityCap':m[3]} for i,m in enumerate(MAPS)],'vehicles':[{'id':i+1,'name':c[0],'price':c[1],'speedRelativeToStarter':c[2],'capacityKg':c[3],'incomeFactor':c[4]} for i,c in enumerate(CARS)],'riders':[{'hireOrdinal':n,'price':hire(n)} for n in range(1,31)],'upgradeLevels':[{'level':l,'riderCumulativeCost':training(l),'vehicleCumulativeCosts':[upgrades(c[1],l) for c in CARS]} for l in range(1,31)],'maxVehicleUpgradeEffects':{'speed':.2,'capacity':.25,'income':.2},'maxRiderUpgradeEffects':{'income':.2,'fixedServiceReduction':.15}}
start=100;intro=[]
for i in range(1,16):
    start+=20 if i<=10 else 24
    before=start
    bought=None
    if i==10:start-=300;bought='firstCar'
    if i==15:start-=120;bought='firstRider'
    intro.append({'delivered':i,'cashBeforePurchase':before,'purchase':bought,'cashAfterPurchase':start})
config['starterVehicle']={'price':0,'upgradeCostBasis':150,'speedRelativeToStarter':1,'capacityKg':2,'incomeFactor':1,'sellable':False}
config['intro']['counter']='all hero delivered orders, including ordinary and special'
config['formulas']={'hire':'first=120; n>=2: 10*roundHalfUp(40*(n-1)^2.7); n is successful hire ordinal, not identity','vehicleCumulativeUpgrade':'roundHalfUp(3*price*((L-1)/29)^1.65)','riderCumulativeTraining':'roundHalfUp(4800*((L-1)/29)^1.8)','effectProgress':'((L-1)/29)^0.65','npcExpectedBatch':'min(actualCapacity/2,mapExpectedDensity)','npcBatchSeconds':'60/actualRelativeSpeed*(1+0.25*(k-1))+30*k*(1-serviceReduction)'}
config['ads']={'specialAppearancePerActualLobbyEntry':0.8,'specialBaseFeeMin':100,'specialBaseFeeMax':150,'specialExclusiveBatch':True,'autoActiveSeconds':600,'autoReceivesSeparateQuotaGift':False}
config['quotaMilestones']=[{'teamCompletedOrders':o,'capMinutes':cap,'minutesPerHeroOrder':credit} for o,cap,credit in [(0,15,1),(60,20,2),(240,25,2),(700,30,3)]]
config['intro']['xpEarnedNormallyIncomeMultiplierStartsAfterDeliveredOrder']=15
# Verify the exact introduction milestones.
assert intro[8]['cashBeforePurchase']==280
assert intro[9]['cashBeforePurchase']==300
assert intro[13]['cashBeforePurchase']==96
assert intro[14]['cashBeforePurchase']==120
rows=[]
for title,n,r,ci,vl,rl in [('初始团队',1,0,-1,1,1),('小团队',3,1,1,5,5),('成长团队',8,2,3,10,10),('成熟团队',16,3,5,15,15),('长期扩编',29,4,9,30,30),('满编满配',30,4,9,30,30)]:
    car=('初始旧车',0,1,2,1) if ci<0 else CARS[ci]
    rr=rate(car,r,vl,rl)
    fleet=rr['coinsPerMinute']*n
    rows.append({'scenario':title,'npcCount':n,'map':r+1,'vehicle':car[0],'vehicleLevel':vl,'riderLevel':rl,'npcRate':rr,'fleetCoinsPerActiveMinute':round(fleet,2),'fleetGrossPer30QuotaMinutes':round(30*fleet,2),'nextRiderPrice':hire(n+1) if n<30 else None,'nextRiderAndSameBaseCarSavingActiveMinutes':round((hire(n+1)+(300 if ci<0 else car[1]))/fleet,2) if n<30 else None})
# Compare same equal fleet across maps. No road/weather premium asserted.
map_roi=[]
for n in [1,8,30]:
    for r in range(1,5):
        diff=n*(rate(CARS[3],r)['coinsPerMinute']-rate(CARS[3],r-1)['coinsPerMinute'])
        map_roi.append({'npcCount':n,'mapToBuy':r+1,'incrementalFleetCoinsPerMinute':round(diff,2),'simplePaybackActiveMinutes':round(MAPS[r][1]/diff,2)})
for i in range(1,30):
    assert hire(i+1)>hire(i)
for car in CARS:
    costs=[upgrades(car[1],l) for l in range(1,31)]
    assert costs[0]==0 and costs[-1]==3*car[1]
    assert all(b>a for a,b in zip(costs,costs[1:]))
assert upgrades(150,30)==450 and upgrades(150,2)>0
assert training(30)==4800 and training(30)>3600
assert all(b['nextRiderAndSameBaseCarSavingActiveMinutes']>a['nextRiderAndSameBaseCarSavingActiveMinutes'] for a,b in zip(rows[:4],rows[1:5]))
result={'assumptions':['Static representative states, not a simulated purchase progression or game test.','NPC quota available throughout each stated active minute; no hidden refill assumed.','NPC expected mean weight 2kg; fractional batch counts are planning averages, not actual fractional orders.','No travel geometry, weather loss, ad latency or hero supplies modeled in NPC rates.','All NPCs in a row have identical equipment; neither affordability nor arrival time at that state is assumed.'],'introLedger':intro,'scenarios':rows,'mapMarginalPayback':map_roi,'completionSpend':{'all30Riders':sum(hire(n) for n in range(1,31)),'allMaps':sum(m[1] for m in MAPS),'thirtyTopCars':30*CARS[-1][1],'thirtyTopCarsMaxUpgrades':30*upgrades(CARS[-1][1],30),'all30RidersTraining':30*training(30)}}
(ROOT/'candidate-parameters.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
(ROOT/'arithmetic-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'intro':[intro[9],intro[14]],'scenarios':rows,'spend':result['completionSpend']},ensure_ascii=False,indent=2))
