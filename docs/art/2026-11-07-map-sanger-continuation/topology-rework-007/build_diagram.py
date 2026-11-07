"""Editable design diagrams only. No raster generation or game-map writes."""
import hashlib
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()


def svg(data, straight=False):
    w,h = data['canvas']
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           '<title>路网连接设计草案；不是实际地图、米制或导航验收</title>',
           '<defs><marker id="outward" markerUnits="userSpaceOnUse" markerWidth="42" markerHeight="38" refX="37" refY="19" orient="auto-start-reverse"><path d="M0 0L42 19L0 38Z" fill="#71858b"/></marker></defs>']
    colors = {'arterial':'#34464e','secondary':'#677b84','local':'#9eafb2','lane':'#bcc8c4'}
    for kind in ['arterial','secondary','local','lane']:
        for edge in data['roads']:
            if edge['kind'] != kind:
                continue
            points = [data['nodes'][edge['from']],data['nodes'][edge['to']]] if straight else edge['points']
            coordinates = ' '.join(str(x)+','+str(y) for x,y in points)
            markers = (' marker-start="url(#outward)"' if edge['from'] in data['boundaryContinuationNodes'] else '') + (' marker-end="url(#outward)"' if edge['to'] in data['boundaryContinuationNodes'] else '')
            out.append(f'<polyline points="{coordinates}" fill="none" stroke="{colors[kind]}" stroke-width="{data["roadWidthsForDiagram"][kind]}" stroke-linecap="round" stroke-linejoin="round"{markers}/>')
    for item in data['callouts']:
        x,y = data['nodes'][item['node']]
        tx,ty = item['anchor']
        out.append(f'<circle cx="{x}" cy="{y}" r="26" fill="#fff" stroke="#bd7425" stroke-width="5"/>')
        out.append(f'<text x="{x}" y="{y+11}" text-anchor="middle" font-family="sans-serif" font-size="31" font-weight="bold" fill="#5d3a10">{data["junctions"][item["node"]]["degree"] if item["node"] in data["junctions"] else 2}</text>')
        out.append(f'<text x="{tx}" y="{ty}" font-family="sans-serif" font-size="30" fill="#30473b">{html.escape(item["label"])}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def main():
    proposed = json.loads((HERE/'proposal.json').read_text())
    old = json.loads((HERE.parent/'organic-north-006/structure-guide.json').read_text())
    data = {'proposal':proposed,'old006':old}
    template = (HERE/'viewer-template.html').read_text()
    assert template.count('__TOPOLOGY_DATA__') == 1
    outputs = {'proposal.svg':svg(proposed).encode(), 'proposal-straight.svg':svg(proposed,True).encode(),
               'straight.svg':svg(proposed,True).encode(),
               'viewer-data.json':encoded(data),
               'index.html':template.replace('__TOPOLOGY_DATA__',json.dumps(data,ensure_ascii=False)).encode()}
    path = HERE/'generated-files.json'
    prior = json.loads(path.read_text()) if path.exists() else {}
    for name in outputs:
        target = HERE/name
        if target.exists():
            assert name in prior and sha(target) == prior[name]['sha256'],name
    for name,raw in outputs.items():
        (HERE/name).write_bytes(raw)
    path.write_bytes(encoded({name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in sorted(outputs.items())}))
    print(json.dumps({'status':'design-diagrams-written','nodes':len(proposed['nodes']),'edges':len(proposed['roads']),
                      'userApproved':False,'imageRequests':0,'actualMapWritten':False}))


if __name__ == '__main__':
    main()
