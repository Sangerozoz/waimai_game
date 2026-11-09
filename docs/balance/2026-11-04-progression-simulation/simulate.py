"""Standalone economic design simulation. No game imports, saves, runtime or network."""
import json, math, random, sys
from functools import lru_cache
from pathlib import Path
BASE=Path(__file__).parent
SOURCE=BASE.parent/'2026-11-04-product-v2-economy/candidate-parameters.json'
def half(v):return math.floor(v+.5)
@lru_cache(None)
def mean_batch(capacity,limit,weights):
 @lru_cache(None)
 def rest(left,slots):
  if slots<=0:return 0.
  return sum((1+rest(left-w,slots-1)) if w<=left else 0 for w in weights)/len(weights)
 eligible=[w for w in weights if w<=capacity]
 assert eligible
 return sum(1+rest(capacity-w,limit-1) for w in eligible)/len(eligible)
class Sim:
 def __init__(self,config,mode='manual',minutes=45,seed=1,pace=1,strategy='roi'):
  self.c=config;self.ad_duration=config.get('adSeconds',30);self.tail_waste=0.;self.mode=mode;self.minutes=minutes;self.rng=random.Random(seed);self.pace=pace;self.strategy=strategy
  self.purchase_delay=0.;self.takeovers=0;self.t=0.;self.work=0.;self.q=0.;self.cash=100.;self.hero={'car':-1,'level':1};self.npcs=[];self.idle=[];self.map=0;self.maps={0};self.energy=100.;self.completed=0;self.hero_done=0;self.xp=0;self.npc_done=0
  self.hero_due=0;self.hero_batch=None;self.auto=0.;self.ad_until=0.;self.last_auto=-1e9;self.last_special=-1e9
  self.gross={'heroOrdinary':0.,'special':0.,'npc':0.};self.spend={'vehicles':0.,'hire':0.,'vehicleUpgrade':0.,'riderUpgrade':0.,'maps':0.,'supplies':0.};self.ads=0;self.ad_seconds=0.;self.milestones={};self.transactions=[];self.min_cash=100;self.max_gap=0.;self.last_purchase=0.;self.active=0.;self.session=0;self.timeline=[]
 def quota(self):
  for x in reversed(self.c['quotaMilestones']):
   if self.completed>=x['teamCompletedOrders']:return x['capMinutes']*60,x['minutesPerHeroOrder']*60
 def attrs(self,obj):
  v=self.c['starterVehicle'] if obj['car']<0 else self.c['vehicles'][obj['car']]
  g=((obj['level']-1)/29)**.65
  return v['speedRelativeToStarter']*(1+.2*g),v['capacityKg']*(1+.25*g),v['incomeFactor']*(1+.2*g)
 def traincost(self,l):return half(self.c.get('trainingCost',4800)*((l-1)/29)**1.8)
 def carcost(self,obj,l):
  p=150 if obj['car']<0 else self.c['vehicles'][obj['car']]['price']
  return half(self.c.get('upgradeFactor',3)*p*((l-1)/29)**1.65)
 def hirecost(self):
  n=len(self.npcs)+1
  return self.c['riders'][n-1]['price']
 def hero_mult(self):
  starts=[0,50,185,367,613,945,1393,1998,2815,3917];gap=1102
  while starts[-1]<=self.xp and len(starts)<80:
   gap=half(gap*1.35);starts.append(starts[-1]+gap)
  lvl=sum(self.xp>=x for x in starts)
  return min(1.6,1+.03*(lvl-1))
 def expected(self,obj,region=None,hero=False):
  r=self.map if region is None else region;m=self.c['maps'][r];s,cap,a=self.attrs(obj);s/=self.c.get('distanceFactor',1)
  weights=tuple(self.c.get('orderWeights',[[1,2,3]]*5)[r]);k=mean_batch(math.floor(cap+1e-8),m['expectedBatchDensityCap'],weights);g=((obj.get('training',1)-1)/29)**.65
  road=60/s*(1+.25*(k-1))*[1,1.1,1.25,1.45,1.6][r]
  secs=road+30*k*(1-.15*g)
  if hero:secs=(20/s*(1+.25*(k-1))*[1,1.1,1.25,1.45,1.6][r]+(3*k if self.auto>0 else 7*k+5))*self.pace
  fee=m['ordinaryBaseFee']*a*((self.hero_mult() if hero else 1+.2*g))
  retention=[.995,.99,.98,.965,.95][r]
  return k*fee*retention*60/secs
 def income(self,region=None,hero=None,npcs=None):
  h=self.hero if hero is None else hero;ns=self.npcs if npcs is None else npcs
  return self.expected(h,region,True)+sum(self.expected(n,region) for n in ns)
 def mark(self,key):
  if key not in self.milestones:self.milestones[key]={'activeMinutes':round(self.active/60,2),'session':self.session,'heroOrders':self.hero_done,'npcCount':len(self.npcs),'cash':round(self.cash,2)}
 def purchase(self,kind,cost,detail,action):
  if self.cash+1e-8<cost:return False
  self.cash-=cost;self.spend[kind]+=cost;self.purchase_delay+=1.5;action();self.min_cash=min(self.min_cash,self.cash)
  if self.hero_done>15:self.max_gap=max(self.max_gap,self.active-self.last_purchase)
  self.last_purchase=self.active
  self.transactions.append({'activeMinutes':round(self.active/60,2),'kind':kind,'cost':cost,'detail':detail,'cash':round(self.cash,2)})
  return True
 def newnpc(self,car):
  n=dict(car,training=1,remaining=0,due=0)
  self.npcs.append(n);self.npc_batch(n)
  for count in [1,2,3,5,8,12,16,20,24,30]:
   if len(self.npcs)==count:self.mark('npc'+str(count))
 def early(self):
  if self.hero['car']<0:
   old=dict(self.hero)
   if self.purchase('vehicles',300,'firstCar',lambda:self.hero.update(car=0,level=1)):
    self.idle.append(old);self.mark('firstCar')
  if not self.npcs and self.hero['car']>=0 and self.idle:
   car=self.idle[0]
   if self.purchase('hire',120,'firstRider',lambda:None):self.idle.pop(0);self.newnpc(car)
 def buy(self):
  self.early()
  if not self.npcs or self.hero_done<15:return
  # Reuse already-owned vehicles before proposing any paid investment.
  for _ in range(100):
   best=None
   for idle in self.idle:
    for target,ishero in [(self.hero,True)]+[(n,False) for n in self.npcs]:
     new=dict(target,car=idle['car'],level=idle['level'])
     gain=self.expected(new,hero=ishero)-self.expected(target,hero=ishero)
     if gain>1e-7 and (best is None or gain>best[0]):best=(gain,idle,target)
   if best is None:break
   _,idle,target=best;old={'car':target['car'],'level':target['level']};self.idle.remove(idle);target.update(car=idle['car'],level=idle['level']);self.idle.append(old);self.purchase_delay+=1.5
  base=self.income(); candidates=[]
  def add(kind,cost,detail,gain,fn):
   if cost<=0 or gain<=1e-8:return
   score=gain/cost
   if self.strategy=='expand' and kind=='hire':score*=2
   if self.strategy=='equipment' and kind in ['vehicles','vehicleUpgrade']:score*=2
   candidates.append((score,kind,cost,detail,fn))
  # Hold savings for best marginal return; avoid spending the target budget on lower return items.
  for idx,m in enumerate(self.c['maps']):
   if idx>self.map and (self.strategy!='skipmap' or idx==4):
    add('maps',m['price'],'map'+str(idx+1),self.income(idx)-base,lambda idx=idx:(self.maps.add(idx),setattr(self,'map',idx),self.mark('map'+str(idx+1))))
  h=self.hero
  for i,v in enumerate(self.c['vehicles']):
   new={'car':i,'level':1}
   gain=self.expected(new,hero=True)-self.expected(h,hero=True)
   def equip(i=i):self.idle.append(dict(self.hero));self.hero={'car':i,'level':1}
   add('vehicles',v['price'],'heroCar'+str(i+1),gain,equip)
  if h['level']<30:
   new=dict(h,level=h['level']+1);delta=self.carcost(h,new['level'])-self.carcost(h,h['level'])
   add('vehicleUpgrade',delta,'heroLevel'+str(new['level']),self.expected(new,hero=True)-self.expected(h,hero=True),lambda:h.update(level=h['level']+1))
  for j,n in enumerate(self.npcs):
   if n['level']<30:
    new=dict(n,level=n['level']+1);delta=self.carcost(n,new['level'])-self.carcost(n,n['level'])
    add('vehicleUpgrade',delta,'npcCarLevel',self.expected(new)-self.expected(n),lambda n=n:n.update(level=n['level']+1))
   if n['training']<30:
    new=dict(n,training=n['training']+1);delta=self.traincost(new['training'])-self.traincost(n['training'])
    add('riderUpgrade',delta,'npcTraining',self.expected(new)-self.expected(n),lambda n=n:n.update(training=n['training']+1))
   # Replace a bike only if the current invoice has settled; changed rates start next batch.
   for i,v in enumerate(self.c['vehicles']):
    new=dict(n,car=i,level=1)
    def equipnpc(n=n,i=i):self.idle.append({'car':n['car'],'level':n['level']});n.update(car=i,level=1)
    add('vehicles',v['price'],'npcCar'+str(i+1),self.expected(new)-self.expected(n),equipnpc)
  if len(self.npcs)<30:
   if self.idle:
    car=max(self.idle,key=lambda x:self.expected(x));cost=self.hirecost()
    def hire(car=car):self.idle.remove(car);self.newnpc(car)
    add('hire',cost,'rider'+str(len(self.npcs)+1),self.expected(dict(car,training=1)),hire)
   else:
    # Joint investment includes a usable vehicle; no unfunded hire or free car.
    car={'car':0,'level':1};cost=self.hirecost()+300
    def hire():self.spend['vehicles']+=300;self.spend['hire']-=300;self.newnpc({'car':0,'level':1})
    add('hire',cost,'riderWithCar'+str(len(self.npcs)+1),self.expected(dict(car,training=1)),hire)
  if candidates:
   best=max(candidates,key=lambda x:x[0]);_,kind,cost,detail,fn=best
   if self.cash>=cost+10:
    if self.purchase(kind,cost,detail,fn):return True
  return False
 def batch(self,obj,hero=False,special=False):
  s,cap,a=self.attrs(obj);s/=self.c.get('distanceFactor',1);m=self.c['maps'][self.map];r=self.map
  if hero and self.hero_done<15:k=1
  elif special:k=1
  else:
   target=m['expectedBatchDensityCap'];weights=self.c.get('orderWeights',[[1,2,3]]*5)[r]
   first=self.rng.choice([w for w in weights if w<=cap]);total=first;k=1
   for _ in range(target-1):
    weight=self.rng.choice(weights)
    if total+weight>cap:break
    total+=weight;k+=1
   assert total<=cap+1e-8
  g=((obj.get('training',1)-1)/29)**.65
  road=(20 if hero else 60)/s*(1+.25*(k-1))*[1,1.1,1.25,1.45,1.6][r]
  duration=(road+((3*k if self.auto>0 else 7*k+5) if hero else 30*k*(1-.15*g)))*(self.pace if hero else 1)
  if hero and self.hero_done<15:fee=20*a
  else:fee=m['ordinaryBaseFee']*a*(self.hero_mult() if hero else 1+.2*g)*[.995,.99,.98,.965,.95][r]
  if special:fee=self.rng.uniform(100,150)*(1 if self.hero_done<15 else [0.995,.99,.98,.965,.95][r])
  energy=.6*(1+.25*(k-1))*[1,1.15,1.35,1.55,1.8][r]*[2,2,3,3,4][r]+2*k
  return k,duration,half(fee*100)/100,energy
 def npc_batch(self,n):
  k,secs,fee,_=self.batch(n)
  n.update(remaining=k,period=secs/k,fee=fee,due=self.work+secs/k)
 def start_hero(self,end):
  for _ in range(200):
   if not self.buy():break
  if self.mode in ['auto','mixed'] and self.auto<=0 and (self.mode=='auto' or self.t-self.last_auto>=1200):
   self.ads+=1;self.ad_seconds+=self.ad_duration;self.last_auto=self.t;self.auto=600;self.hero_due=self.t+self.ad_duration+self.purchase_delay;self.purchase_delay=0;self.hero_batch={'ad':True};return
  special=False
  if self.auto<=0 and self.mode in ['special','mixed']:
   if self.rng.random()<.8 and (self.mode=='special' or self.t-self.last_special>=600):special=True;self.last_special=self.t
  k,secs,fee,energy=self.batch(self.hero,True,special)
  supply=0
  if self.energy<energy:
   if self.cash>=3:self.cash-=3;self.spend['supplies']+=3;self.energy=min(100,self.energy+70);supply=3
   else:self.energy=min(100,self.energy+20);supply=10
  self.energy=max(0,self.energy-energy)
  if special:self.ads+=1;self.ad_seconds+=self.ad_duration;secs+=self.ad_duration
  secs+=supply
  secs+=self.purchase_delay;self.purchase_delay=0
  self.hero_batch={'ad':False,'remaining':k,'period':secs/k,'fee':fee,'special':special,'automatic':self.auto>0}
  self.hero_due=self.t+secs/k
 def credit(self):
  cap,add=self.quota();self.q=min(cap,self.q+add)
 def run_session(self):
  end=self.t+self.minutes*60;self.session+=1
  if self.hero_batch is None:self.start_hero(end)
  while self.t<end-1e-7:
   dn=min([n['due']-self.work for n in self.npcs],default=1e30) if self.q>1e-8 else 1e30
   dt=max(0,min(end-self.t,self.hero_due-self.t,dn,self.q if self.q>1e-8 else 1e30,self.auto if self.hero_batch and self.hero_batch.get('automatic') and self.auto>1e-8 else 1e30))
   if dt<1e-8:dt=0
   if self.q>1e-8:self.work+=dt;self.q=max(0,self.q-dt)
   if self.hero_batch and self.hero_batch.get('automatic'):self.auto=max(0,self.auto-dt)
   self.t+=dt;self.active+=dt
   if self.hero_batch and self.hero_batch.get('automatic') and self.auto<=1e-8 and self.hero_due>self.t+1e-7:
    self.hero_batch['automatic']=False;self.takeovers+=1;self.hero_due+=5+4*self.hero_batch['remaining']
   for n in self.npcs:
    if n['due']<=self.work+1e-7:
     self.cash+=n['fee'];self.gross['npc']+=n['fee'];self.completed+=1;self.npc_done+=1;n['remaining']-=1
     if n['remaining']<=0:self.npc_batch(n)
     else:n['due']+=n['period']
   if self.hero_due<=self.t+1e-7:
    b=self.hero_batch
    if b.get('ad'):self.hero_batch=None;self.start_hero(end);continue
    self.cash+=b['fee'];self.gross['special' if b['special'] else 'heroOrdinary']+=b['fee'];self.hero_done+=1;self.completed+=1;self.xp+=10;self.credit();b['remaining']-=1
    if b['remaining']<=0:
     self.hero_batch=None
     if self.t<end-1e-7:self.start_hero(end)
    else:self.hero_due+=b['period']
  if len(self.npcs)==30 and self.map==4 and self.hero['level']==30 and all(n['training']==30 and n['level']==30 for n in self.npcs):self.mark('fullyDeveloped')
  self.timeline.append({'session':self.session,'activeHours':round(self.active/3600,2),'cash':round(self.cash,2),'npcCount':len(self.npcs),'map':self.map+1,'heroCar':self.hero['car']+1,'heroLevel':self.hero['level'],'heroOrders':self.hero_done,'npcOrders':self.npc_done,'ads':self.ads,'earned':round(sum(self.gross.values()),2),'spent':round(sum(self.spend.values()),2)})
 def offline(self):
  # Hero frozen, NPC consumes only stored quota, no new quota gifts or offline multiplier.
  while self.q>1e-7 and self.npcs:
   dn=min(n['due']-self.work for n in self.npcs);dt=min(self.q,max(0,dn));self.work+=dt;self.q-=dt
   for n in self.npcs:
    if n['due']<=self.work+1e-7:
     self.cash+=n['fee'];self.gross['npc']+=n['fee'];self.completed+=1;self.npc_done+=1;n['remaining']-=1
     if n['remaining']<=0:self.npc_batch(n)
     else:n['due']+=n['period']
  self.t+=max(0,86400-self.minutes*60)
  # Hero pending action keeps remaining seconds, not wall-clock deadline.
  self.hero_due=self.t+max(0,self.hero_due-(self.t-(86400-self.minutes*60)))
 def run(self,sessions):
  for _ in range(sessions):self.run_session();self.offline()
  drift=100+sum(self.gross.values())-sum(self.spend.values())-self.cash
  assert abs(drift)<.05,drift
  return {'mode':self.mode,'minutesPerSession':self.minutes,'pace':self.pace,'strategy':self.strategy,'milestones':self.milestones,'finalOnline':self.timeline[-1],'final':dict(self.timeline[-1],cash=round(self.cash,2),npcOrders=self.npc_done,earned=round(sum(self.gross.values()),2),spent=round(sum(self.spend.values()),2)),'gross':{k:round(v,2) for k,v in self.gross.items()},'spend':{k:round(v,2) for k,v in self.spend.items()},'endEquipment':[{'car':n['car']+1,'level':n['level'],'training':n['training']} for n in self.npcs],'autoEndManualTakeovers':self.takeovers,'autoUnusedTailMinutes':round(self.tail_waste/60,2),'ads':self.ads,'adMinutes':round(self.ad_seconds/60,2),'maxPurchaseGapActiveMinutes':round(self.max_gap/60,2),'accountingDrift':round(drift,8),'timeline':self.timeline,'transactions':self.transactions}
def main():
 c=json.loads((BASE/'calibrated-parameters.json').read_text()); runs=[]
 for mode,minutes,pace,strategy in [('manual',45,1,'roi'),('special',45,1,'roi'),('auto',45,1,'roi'),('mixed',45,1,'roi'),('manual',20,1,'roi'),('manual',90,1,'roi'),('manual',45,1.5,'roi'),('manual',45,1,'expand'),('manual',45,1,'equipment'),('manual',45,1,'skipmap')]:
  s=Sim(c,mode,minutes,seed=23,pace=pace,strategy=strategy);r=s.run(int(sys.argv[1]) if len(sys.argv)>1 else 150);runs.append(r)
  print(mode,minutes,pace,strategy,{k:v['activeMinutes'] for k,v in r['milestones'].items()},r['final'],flush=True)
 (BASE/'simulation-results.json').write_text(json.dumps(runs,ensure_ascii=False,indent=2)+'\n')
 (BASE/'simulation-inputs.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
