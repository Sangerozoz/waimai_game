"""Check short check-ins and sustained play without a daily quota reset."""
import json
from pathlib import Path
from simulate import Sim
BASE=Path(__file__).parent
c=json.loads((BASE/'calibrated-parameters.json').read_text())
results=[]
for name,minutes,sessions in [('five-minute-check-in',5,365),('four-hours-daily',240,45),('continuous-play',1440,7)]:
 r=Sim(c,'manual',minutes,seed=23).run(sessions)
 small={k:r[k] for k in ['milestones','final','gross','spend','accountingDrift']};small['case']=name;small['sessionMinutes']=minutes
 results.append(small)
 print(name,{k:(v['session'],round(v['activeMinutes']/60,2)) for k,v in r['milestones'].items() if k in ['map5','npc16','npc30']},flush=True)
(BASE/'session-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
