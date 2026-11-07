#!/usr/bin/env python3
"""Build separate native-pixel road evidence and editable inherited city planning."""
import hashlib
import heapq
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
PLAN = ROOT / 'docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/scope-plan.json'
NATIVE = HERE.parent / 'builtin-capacity-002/native.png'
TRACE = HERE / 'trace-input.json'
SNAPSHOT = ROOT / 'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json'
COLORS = {'residential':'#e6d7b6','commercial-office':'#d4a787','civic':'#b4c8dc',
          'workshop-service':'#c7c1bc','park-community-open':'#b9cdaa'}
GENERATED = {}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    GENERATED[str(path.relative_to(HERE))] = sha(path)


def area(poly):
    return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly, poly[1:]+poly[:1]))) / 2


def props(values):
    return [{'name': k, 'type': 'bool' if isinstance(v,bool) else 'float' if isinstance(v,(float,int))
             else 'string', 'value': v} for k,v in values.items()]


class Tiled:
    def __init__(self, size, metadata):
        self.oid = 1
        self.doc = {'type':'map','version':'1.10','tiledversion':'1.12.2','orientation':'orthogonal',
                    'renderorder':'right-down','infinite':False,'width':math.ceil(size[0]),
                    'height':math.ceil(size[1]),'tilewidth':1,'tileheight':1,
                    'layers':[],'tilesets':[],'properties':props(metadata)}

    def image(self, name, path, size):
        self.doc['layers'].append({'id':len(self.doc['layers'])+1,'type':'imagelayer','name':name,
            'image':path,'imagewidth':size[0],'imageheight':size[1],'offsetx':0,'offsety':0,
            'visible':True,'opacity':1,'locked':True})

    def layer(self, name, objects, color='#d03283', visible=True):
        self.doc['layers'].append({'id':len(self.doc['layers'])+1,'type':'objectgroup','name':name,
            'draworder':'index','color':color,'objects':objects,'visible':visible,'opacity':1,'locked':False})

    def object(self, name, kind, points, properties=None, polygon=False, point=False):
        x,y = points[0]
        result = {'id':self.oid,'name':name,'type':kind,'x':x,'y':y,'width':0,'height':0,
                  'rotation':0,'visible':True,'properties':props(properties or {})}
        self.oid += 1
        if point:
            result['point'] = True
        else:
            result['polygon' if polygon else 'polyline'] = [{'x':p[0]-x,'y':p[1]-y} for p in points]
        return result

    def finish(self):
        self.doc.update(nextlayerid=len(self.doc['layers'])+1, nextobjectid=self.oid)
        return self.doc


def components(nodes, edges, skip=None):
    adjacent = {n['id']:[] for n in nodes}
    for e in edges:
        if e['id'] != skip:
            adjacent[e['from']].append(e['to']); adjacent[e['to']].append(e['from'])
    unseen = set(adjacent); count = 0
    while unseen:
        count += 1; todo = [next(iter(unseen))]
        while todo:
            u = todo.pop()
            if u not in unseen: continue
            unseen.remove(u); todo.extend(adjacent[u])
    return count


def route(nodes, edges, start, end, skip=None):
    adjacent = {n['id']:[] for n in nodes}
    for e in edges:
        if e['id'] == skip: continue
        length = e.get('lengthPixels', e.get('lengthMetres'))
        adjacent[e['from']].append((e['to'],length,e['id']))
        adjacent[e['to']].append((e['from'],length,e['id']))
    best = {start:0}; queue = [(0,start,[])]; parent = {}
    while queue:
        distance,u,chain = heapq.heappop(queue)
        if distance != best[u]: continue
        if u == end: return {'length':distance,'edgeIds':chain,'from':start,'to':end}
        for v,length,eid in adjacent[u]:
            if distance+length < best.get(v,math.inf):
                best[v] = distance+length
                heapq.heappush(queue,(distance+length,v,chain+[eid]))
    raise ValueError('No geometric route')


def actual_evidence(plan):
    trace = json.loads(TRACE.read_text())
    assert sha(NATIVE) == trace['nativeSHA256']
    with Image.open(NATIVE) as image: assert list(image.size) == trace['nativeSize']
    nodes=[]; edges=[]; byid={}
    def node(name,p):
        assert name not in byid
        byid[name]=p;nodes.append({'id':name,'pixel':p});return name
    def edge(name,a,b,interior=(),role='internal'):
        points=[byid[a],*interior,byid[b]]
        edges.append({'id':name,'from':a,'to':b,'points':points,
                      'lengthPixels':sum(math.dist(p,q) for p,q in zip(points,points[1:])),
                      'role':role,'geometricBidirectionalAssumption':True,'trafficDirectionValidated':False})
    rows = trace['junctionRows']
    for r,row in enumerate(rows):
        for c,p in enumerate(row):node(f'j-{r}-{c}',p)
    for r in range(3):
        for c in range(4):edge(f'h-{r}-{c}',f'j-{r}-{c}',f'j-{r}-{c+1}')
    for c in range(5):
        for r in range(2):edge(f'v-{c}-{r}',f'j-{r}-{c}',f'j-{r+1}-{c}',trace['verticalInteriors'][c][r])
    for c in range(5):
        node(f'north-{c}',trace['northPorts'][c]);node(f'south-{c}',trace['southPorts'][c])
        edge(f'out-n-{c}',f'north-{c}',f'j-0-{c}',role='edge-continuation')
        edge(f'out-s-{c}',f'j-2-{c}',f'south-{c}',role='edge-continuation')
    for r in range(3):
        node(f'west-{r}',[0,rows[r][0][1]]);node(f'east-{r}',[1672,rows[r][4][1]])
        edge(f'out-w-{r}',f'west-{r}',f'j-{r}-0',role='edge-continuation')
        edge(f'out-e-{r}',f'j-{r}-4',f'east-{r}',role='edge-continuation')
    plan_blocks = {b['id']:b for b in plan['blocks']}; blocks=[]
    for r in range(2):
        for c in range(4):
            bid=trace['blockIdsByImageRow'][r][c]
            blocks.append({'id':bid,'imageRow':r,'imageColumn':c,
                'programmeFromGuide':plan_blocks[bid]['programme'],
                'pixelEnclosure':[rows[r][c],rows[r][c+1],rows[r+1][c+1],rows[r+1][c]],
                'guideIdentityOnlyNotMetreRegistration':True})
    main=route(nodes,edges,'south-1','north-3')
    internal=[eid for eid in main['edgeIds'] if not eid.startswith('out-')]
    excluded=internal[len(internal)//2]
    alternative=route(nodes,edges,'south-1','north-3',excluded)
    assert components(nodes,edges)==1 and len(edges)-len(nodes)+1==8
    graph={'coordinateSpace':'actual-native-image-pixels-not-metres','nativeSHA256':sha(NATIVE),
        'nativeSize':[1672,941],'nodes':nodes,'edges':edges,'blocks':blocks,
        'connectedComponents':1,'boundedFaces':8,'internalEdges':22,'boundaryContinuations':16,
        'mainRoute':main,'excludedEdgeForAlternative':excluded,'alternativeRoute':alternative,
        'trafficValidated':False,'metreCalibration':None,'wholeCityCoverageFraction':None,
        'admittedAsOrdinaryCityRegion':False,'newBusinessBindings':0,'formalGameTestsPerformed':False}
    save(HERE/'actual-graph.json',graph)
    tiled=Tiled([1672,941],{'coordinate_space':'native-image-pixels-not-metres',
        'native_sha256':sha(NATIVE),'scope':'eight-block proof only; not D or whole city',
        'pixel_canvas_width':1672,'pixel_canvas_height':941,'metre_calibrated':False,
        'traffic_validated':False,'new_business_bindings':0,'ordinary_city_region':False})
    tiled.image('native-art','../../builtin-capacity-002/native.png',[1672,941])
    tiled.layer('actual-road-centrelines',[tiled.object(e['id'],'road',e['points'],
        {'from':e['from'],'to':e['to'],'length_pixels':e['lengthPixels'],'edge_role':e['role'],
         'trace_method':'visual on actual native; neutral-asphalt scans support','traffic_validated':False,
         'geometric_bidirectional_assumption':True}) for e in edges])
    tiled.layer('actual-junctions-and-edge-ports',[tiled.object(n['id'],'junction',[n['pixel']],
        {'coordinate_space':'pixels-not-metres'},point=True) for n in nodes],visible=False)
    tiled.layer('eight-complete-block-enclosures',[tiled.object(b['id'],'block-enclosure',b['pixelEnclosure'],
        {'programme_from_guide':b['programmeFromGuide'],'not_measured_metres':True},polygon=True) for b in blocks],visible=False)
    selected={e['id']:e for e in edges}
    for name,choice,color in [('geometric-main-route',main,'#138f71'),('geometric-alternative-route',alternative,'#e8a128')]:
        tiled.layer(name,[tiled.object(eid,'route-fragment',selected[eid]['points'],{'not_traffic_validated':True})
                          for eid in choice['edgeIds']],color=color,visible=False)
    save(HERE/'tiled/actual-eight.tmj',tiled.finish())
    return graph


def inset(poly, widths, extra):
    result=[list(p) for p in poly]
    for (a,b),width in zip(zip(poly,poly[1:]+poly[:1]),widths):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        normal=(-dy/length,dx/length);cut=normal[0]*a[0]+normal[1]*a[1]+width/2+extra
        output=[]
        for p,q in zip(result,result[1:]+result[:1]):
            pv=normal[0]*p[0]+normal[1]*p[1]-cut;qv=normal[0]*q[0]+normal[1]*q[1]-cut
            if (pv>=0)!=(qv>=0):
                t=pv/(pv-qv);hit=[p[k]+t*(q[k]-p[k]) for k in (0,1)]
                output.append(hit)
            if qv>=0:output.append(q)
        result=output
    assert len(result)>=3
    return result


def planning_evidence(plan):
    width,height=plan['targetDesignSizeMetres'];size=[math.ceil(width),math.ceil(height)]
    def screen(p):return [p[0],height-p[1]]
    node_by={n['id']:n['designMetres'] for n in plan['nodes']}
    node_at={tuple(n['designMetres']):n['id'] for n in plan['nodes']}
    edge_by={tuple(sorted((e['from'],e['to']))):e for e in plan['edges']}
    ledger=[];summary=defaultdict(lambda:{'blocks':0,'centrelineEnclosedAreaMetres2':0,'netAsphaltOnlyMetres2':0,'netWith2mSidewalkHypothesisMetres2':0})
    for b in plan['blocks']:
        poly=b['polygonDesignMetres'];border=[]
        assert sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(poly,poly[1:]+poly[:1]))>0
        for p,q in zip(poly,poly[1:]+poly[:1]):
            edge=edge_by[tuple(sorted((node_at[tuple(p)],node_at[tuple(q)])))];border.append(edge)
        widths=[e['proposedAsphaltWidthMetres'] for e in border]
        net=inset(poly,widths,0);sidewalk=inset(poly,widths,2)
        row={'id':b['id'],'programme':b['programme'],'densityIntent':b['densityIntent'],
             'boundaryRoadIds':[e['id'] for e in border],'boundaryAsphaltWidthsMetres':widths,
             'centrelinePolygon':poly,'netAsphaltOnlyPolygon':net,'netWith2mSidewalkHypothesisPolygon':sidewalk,
             'centrelineEnclosedAreaMetres2':area(poly),'netAsphaltOnlyMetres2':area(net),
             'netWith2mSidewalkHypothesisMetres2':area(sidewalk)}
        assert 0<row['netWith2mSidewalkHypothesisMetres2']<row['netAsphaltOnlyMetres2']<area(poly)
        ledger.append(row);group=summary[b['programme']];group['blocks']+=1
        for key in ('centrelineEnclosedAreaMetres2','netAsphaltOnlyMetres2','netWith2mSidewalkHypothesisMetres2'):group[key]+=row[key]
    total=sum(b['netAsphaltOnlyMetres2'] for b in ledger)
    total_with_sidewalk=sum(b['netWith2mSidewalkHypothesisMetres2'] for b in ledger)
    blue=plan['blueDesignBounds'];blue_area=(blue[2]-blue[0])*(blue[3]-blue[1])
    gross=sum(b['centrelineEnclosedAreaMetres2'] for b in ledger)
    net={'status':'inherited-design-conditional-land-ledger-not-image-calibration-or-final-residential-acceptance',
        'sourcePlanSHA256':sha(PLAN),'blocks':ledger,'programmeTotals':dict(summary),
        'assignedBlockNetAsphaltOnlyMetres2':total,'assignedBlockNetWith2mSidewalkHypothesisMetres2':total_with_sidewalk,
        'residentialShareOfAssignedBlockNetAsphaltOnly':summary['residential']['netAsphaltOnlyMetres2']/total,
        'residentialShareWith2mSidewalkHypothesis':summary['residential']['netWith2mSidewalkHypothesisMetres2']/total_with_sidewalk,
        'blueDesignAreaMetres2':blue_area,'assignedCentrelineBlockAreaMetres2':gross,
        'blueOutsideStreetBlockEnclosuresMetres2':blue_area-gross,
        'blueOutsideStreetBlockEnclosuresContains':'unallocated perimeter land, outer half of ring road, future paths and landscape; NOT all net developable land',
        'completeBlueNetDevelopableDenominatorKnown':False,'waterAndOtherNonDevelopableAreasEstablished':False,
        'roadWidthsAreDesignProposal':True,'sidewalk2mIsSensitivityNotAdopted':True,
        'finalResidentialAboutHalfAccepted':False,'originalPlanChanged':False}
    save(HERE/'planning-land-ledger.json',net)
    image=Image.new('RGB',tuple(size),'#e8eedf');draw=ImageDraw.Draw(image)
    for b in ledger:draw.polygon([tuple(screen(p)) for p in b['centrelinePolygon']],fill=COLORS[b['programme']])
    for edge in plan['edges']:
        draw.line([tuple(screen(node_by[edge['from']])),tuple(screen(node_by[edge['to']]))],fill='#69776f',width=round(edge['proposedAsphaltWidthMetres']))
    for bounds,color in [([0,0,width,height],'#c4564b'),(blue,'#237d9a'),(plan['denseCoreDesignBounds'],'#568c59')]:
        x0,y0,x1,y1=bounds;draw.rectangle((x0,height-y1,x1,height-y0),outline=color,width=3)
    font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',12)
    for b in plan['blocks']:
        draw.text(tuple(screen(b['centre'])),b['id'],font=font,fill='#283e34',anchor='mm')
    diagram=HERE/'tiled/plan-schematic.png';diagram.parent.mkdir(exist_ok=True);image.save(diagram);GENERATED[str(diagram.relative_to(HERE))]=sha(diagram)
    tiled=Tiled(size,{'coordinate_space':'design-metres-as-1-map-pixel; not native-art calibration',
        'source_plan_sha256':sha(PLAN),'planning_only':True,'target_width_design_metres':width,
        'target_height_design_metres':height,'ordinary_city_region':False,'production_ready':False,
        'canvas_rounding_padding_not_added_city_area':True})
    tiled.image('planning-schematic-not-art','plan-schematic.png',size)
    tiled.layer('planned-full-road-network',[tiled.object(e['id'],'planned-road',
        [screen(node_by[e['from']]),screen(node_by[e['to']])],
        {'from':e['from'],'to':e['to'],'corridor_id':e['corridorId'],'tier':e['tier'],
         'asphalt_width_design_metres':e['proposedAsphaltWidthMetres'],'length_design_metres':e['lengthMetres'],
         'traced_from_actual_art':False}) for e in plan['edges']],color='#a84569')
    tiled.layer('planned-junctions',[tiled.object(n['id'],'planned-junction',[screen(n['designMetres'])],
        {'not_native_art_registration':True},point=True) for n in plan['nodes']],visible=False)
    tiled.layer('planned-street-block-enclosures',[tiled.object(b['id'],'planned-block',[screen(p) for p in b['centrelinePolygon']],
        {'programme':b['programme'],'density_intent':b['densityIntent'],'net_asphalt_only_design_m2':b['netAsphaltOnlyMetres2']},polygon=True)
        for b in ledger],visible=False)
    tiled.layer('planned-net-plots-asphalt-only',[tiled.object(b['id'],'conditional-net-plot',[screen(p) for p in b['netAsphaltOnlyPolygon']],
        {'area_design_m2':b['netAsphaltOnlyMetres2'],'final_blue_net_denominator_known':False},polygon=True) for b in ledger],visible=False)
    tiled.layer('sensitivity-net-plots-plus2m-not-adopted',[tiled.object(b['id'],'hypothetical-net-plot',[screen(p) for p in b['netWith2mSidewalkHypothesisPolygon']],
        {'area_design_m2':b['netWith2mSidewalkHypothesisMetres2'],'sidewalk_metres_hypothesis':2,'adopted':False},polygon=True) for b in ledger],visible=False)
    save(HERE/'tiled/whole-city-planning.tmj',tiled.finish())
    plan_graph={'coordinateSpace':'design-metres-not-registered-art','nodes':plan['nodes'],'edges':plan['edges'],
        'stats':plan['stats'],'targetDesignSizeMetres':[width,height],'sourcePlanSHA256':sha(PLAN),
        'all144SingleEdgeRemovalComponents':[components(plan['nodes'],plan['edges'],e['id']) for e in plan['edges']],
        'productionReady':False,'artworkCoverageFraction':None}
    assert all(c==1 for c in plan_graph['all144SingleEdgeRemovalComponents'])
    save(HERE/'planning-graph.json',plan_graph)
    return net


def main():
    old_path=HERE/'generated-files.json';old=json.loads(old_path.read_text()) if old_path.exists() else {}
    for rel,digest in old.items():
        if not (HERE/rel).is_file() or sha(HERE/rel)!=digest:raise RuntimeError('Possible user edits; refuse overwrite: '+rel)
    for rel in ['actual-graph.json','planning-land-ledger.json','planning-graph.json','tiled/actual-eight.tmj','tiled/whole-city-planning.tmj','tiled/plan-schematic.png','index.html']:
        if (HERE/rel).exists() and rel not in old:raise RuntimeError('Existing unowned file: '+rel)
    protected=json.loads(SNAPSHOT.read_text())
    assert all((ROOT/p).is_file() and sha(ROOT/p)==s['sha256'] for p,s in protected['files'].items())
    plan=json.loads(PLAN.read_text());actual=actual_evidence(plan);net=planning_evidence(plan)
    page=(HERE/'viewer-template.html').read_text().replace('__ACTUAL__',json.dumps(actual,ensure_ascii=False)).replace('__NET__',json.dumps(net,ensure_ascii=False))
    (HERE/'index.html').write_text(page);GENERATED['index.html']=sha(HERE/'index.html')
    save(HERE/'input-fingerprints.json',{str(p.relative_to(ROOT)):sha(p) for p in [PLAN,TRACE,NATIVE,SNAPSHOT,HERE/'build_evidence.py',HERE/'viewer-template.html']})
    old_path.write_text(json.dumps(GENERATED,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'actualNativeSize':actual['nativeSize'],'actualNodes':len(actual['nodes']),
        'actualEdges':len(actual['edges']),'actualCompleteBlocks':len(actual['blocks']),
        'planningBlocks':len(net['blocks']),'residentialShareOfAssignedNet':net['residentialShareOfAssignedBlockNetAsphaltOnly'],
        'unallocatedBlueOutsideBlockEnclosuresMetres2':net['blueOutsideStreetBlockEnclosuresMetres2'],
        'productionReady':False,'protectedMatched':len(protected['files'])},ensure_ascii=False))


if __name__=='__main__':main()
