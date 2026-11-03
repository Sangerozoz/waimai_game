"""Source production scheduling only; writes queue metadata, never art or runtime."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
atlas=R/'atlas-plan.json';p=json.loads(atlas.read_text());byid={r['id']:r for r in p['regions']};done=set();ordered=[]
def append(r,phase):
 neighbors=[n for n in r['neighbors'].values() if n in done]
 ordered.append(dict(index=len(ordered),id=r['id'],grid=r['grid'],zone=r['zone'],phase=phase,status='approved-art-exists-registration-pending' if r['id']=='REGION-A' else 'art-not-generated',adjacentPriorRegionIds=neighbors,referenceRegionIds=neighbors[:2],nextAction='native-registration-and-seams' if r['id']=='REGION-A' else 'make-region-input-then-imagegen',outputDir='docs/art/2026-11-03-county-region-atlas/production/'+r['id']))
 done.add(r['id'])
for ident in ['REGION-A','REGION-B','REGION-C','REGION-D']:append(byid[ident],'first-connected-2x2')
for phase in ['denseUrban','suburb','outerLandscape']:
 while True:
  pending=[r for r in p['regions'] if r['zone']==phase and r['id'] not in done]
  if not pending:break
  frontier=[r for r in pending if any(n in done for n in r['neighbors'].values())]
  if not frontier:raise RuntimeError('Zone disconnected from completed source frontier: '+phase)
  # Expanding Manhattan shells; within shell favor several known neighbors.
  pick=min(frontier,key=lambda r:(abs(r['grid'][0])+abs(r['grid'][1]),-sum(n in done for n in r['neighbors'].values()),r['grid'][1],r['grid'][0]))
  append(pick,phase)
if len(ordered)!=len(p['regions']) or len(done)!=len(p['regions']):raise RuntimeError('Queue does not own every atlas region exactly once')
batches=[]
for n in range(0,len(ordered),4):
 batch=ordered[n:n+4];batches.append(dict(index=n//4,ids=[r['id'] for r in batch],phases=sorted(set(r['phase'] for r in batch)),dependencyPolicy='Only dispatch an item after its selected prior-neighbor native reference actually exists. Items within same batch may depend sequentially on one another; batch is not an unconditional parallel barrier.'))
out=dict(schemaVersion=1,status='source-production-order-not-execution-state',atlasFile=str(atlas.relative_to(R.parents[3])),atlasSha256=hashlib.sha256(atlas.read_bytes()).hexdigest(),policy=['First preserve A and make connected B/C/D.','Then breadth-first expand green urban core, then blue suburb, then red-blue landscape.','A is included once as existing art and not scheduled for duplicate native generation.','Full1056 retained exactly once; 1055 remain ungenerated at queue creation.','All regions have a previous geometric neighbor; image references still require actual native file before dispatch.','A geometric queue never means all previous art/seams are completed.','Every roof excludes all greenery. Landscape prompts use landscape theme rather than residential blocks.'],counts=dict(regions=len(ordered),existingNativeArt=1,ungenerated=len(ordered)-1,batches=len(batches)),firstEightBatches=batches[:8],batches=batches,items=ordered)
(R/'production-order.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(R/'production-order-first8.md').write_text('# 前8批整区生产顺序（仅队列，非已生产）\n\n'+ '\n'.join(f"- 第{b['index']+1}批："+'、'.join(b['ids']) for b in batches[:8])+'\n\n每项只可在所选相邻原生图实际存在后派出；同批含依赖不代表可无条件并行。A为既有认可图，不重复生成。\n')
print(json.dumps(dict(regions=len(ordered),batches=len(batches),firstEight=batches[:8]),ensure_ascii=False))
