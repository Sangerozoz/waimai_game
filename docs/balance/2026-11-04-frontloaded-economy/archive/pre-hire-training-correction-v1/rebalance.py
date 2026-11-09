"""Design experiment: frontloaded content; imports only independent planning model."""
import json,sys,math
from pathlib import Path
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT.parent/'2026-11-04-progression-simulation'))
from simulate import Sim,half
class FrontSim(Sim):
 def purchase(self,kind,cost,detail,action):
  ok=super().purchase(kind,cost,detail,action)
  if ok:
   owned={x['car'] for x in [self.hero]+self.npcs+self.idle if x['car']>=0}
   self.check_content()
  return ok
 def check_content(self):
  owned={x['car'] for x in [self.hero]+self.npcs+self.idle if x['car']>=0}
  if len(self.npcs)>=24 and len(self.maps)>=4 and all(i in owned for i in range(8)):self.mark('content80')
 def newnpc(self,car):
  super().newnpc(car);self.check_content()
 def buy(self):
  self.early()
  if len(self.npcs)>=20:
   owned={x['car'] for x in [self.hero]+self.npcs+self.idle if x['car']>=0}
   missing=[i for i in range(8) if i not in owned]
   if missing:
    i=missing[0];cost=self.c['vehicles'][i]['price']
    if self.cash>=cost:
     self.purchase('vehicles',cost,'optionalCollectionCar'+str(i+1),lambda:self.idle.append({'car':i,'level':1}));self.check_content();return True
  # Guided target for first squad. A purchase preference, never a purchase eligibility gate.
  if 1<=len(self.npcs)<3:
   if self.idle:
    car=self.idle[0];cost=self.hirecost()
    if self.cash>=cost:
     self.purchase('hire',cost,'guidedSquadRider',lambda:None);self.idle.pop(0);self.newnpc(car);return True
   else:
    cost=self.hirecost()+300
    if self.cash>=cost:
     hire=self.hirecost();self.purchase('hire',hire,'guidedSquadRider',lambda:None)
     self.purchase('vehicles',300,'guidedSquadCar',lambda:None);self.newnpc({'car':0,'level':1});return True
   return False
  return super().buy()
def config():
 c=json.loads((ROOT.parent/'2026-11-04-progression-simulation/calibrated-parameters.json').read_text())
 for n,r in enumerate(c['riders'],1):r['price']=([120,120,180][n-1] if n<=3 else 10*half(30*(n-2)**1.6)) if n<=24 else [400000,800000,1400000,2200000,3200000,4400000][n-25]
 for m,price in zip(c['maps'],[0,1500,10000,45000,600000]):m['price']=price
 for i,v in enumerate(c['vehicles']):
  if i>=1:v['price']=[300,600,1000,1800,3000,5000,8000,12000,80000,160000][i]
 # Recalculate inherited level table after price changes.
 for row in c['upgradeLevels']:row['vehicleCumulativeCosts']=[half(3*v['price']*((row['level']-1)/29)**1.65) for v in c['vehicles']]
 c['formulas']['hire']='n<=3: [120,120,180]; 4<=n<=24: 10*roundHalfUp(30*(n-2)^1.6); n>=25: [400000,800000,1400000,2200000,3200000,4400000]'
 c['status']='frontloaded-design-candidate-not-runtime'
 return c
def main():
 c=config();(ROOT/'parameters.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');rs=[]
 for mode,pace in [('manual',1),('auto',1),('mixed',1),('manual',1.5)]:
  s=FrontSim(c,mode,45,seed=23,pace=pace);r=s.run(80);rs.append(r)
  print(mode,pace,{k:round(v['activeMinutes'],2) for k,v in r['milestones'].items()},flush=True)
 (ROOT/'results.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
