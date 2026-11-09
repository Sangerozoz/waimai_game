"""Run parameter uncertainty checks against the same economic candidate."""
import json
from pathlib import Path
from simulate import Sim
BASE=Path(__file__).parent
base=json.loads((BASE/'calibrated-parameters.json').read_text())
cases=[('manual-seed7','manual',7,30,1),('manual-seed71','manual',71,30,1),('auto-seed7','auto',7,30,1),('auto-seed71','auto',71,30,1),('special-ad15','special',23,15,1),('special-ad60','special',23,60,1),('auto-ad15','auto',23,15,1),('auto-ad60','auto',23,60,1),('manual-short-routes','manual',23,30,.75),('manual-long-routes','manual',23,30,1.5)]
results=[]
for name,mode,seed,ad,dist in cases:
 c=json.loads(json.dumps(base));c['adSeconds']=ad;c['distanceFactor']=dist
 r=Sim(c,mode,45,seed=seed).run(150)
 small={k:r[k] for k in ['milestones','final','gross','spend','ads','adMinutes','maxPurchaseGapActiveMinutes','accountingDrift']}
 small.update(case=name,mode=mode,seed=seed,adSeconds=ad,distanceFactor=dist)
 results.append(small)
 print(name,{k:round(v['activeMinutes']/60,2) for k,v in r['milestones'].items() if k in ['map2','map5','npc8','npc16','npc30']},flush=True)
(BASE/'sensitivity-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
