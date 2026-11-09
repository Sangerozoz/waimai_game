#!/usr/bin/env python3
"""Put the received native city-block image in Tiled without drawing user routes."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent


def main():
    target = HERE / '画路试验.tmj'
    if target.exists():
        raise SystemExit('Keep existing user route work; map already exists')
    image = HERE / 'native-city-block.png'
    provenance = json.loads((HERE / 'provenance.json').read_text())
    assert hashlib.sha256(image.read_bytes()).hexdigest() == provenance['nativeSHA256']
    with Image.open(image) as im:
        im.load()
        width, height = im.size
    doc = {
        'type': 'map', 'version': '1.10', 'tiledversion': '1.12.2',
        'orientation': 'orthogonal', 'renderorder': 'right-down',
        'width': math.ceil(width / 32), 'height': math.ceil(height / 32),
        'tilewidth': 32, 'tileheight': 32, 'infinite': False,
        'backgroundcolor': '#deded7', 'nextobjectid': 1, 'nextlayerid': 3,
        'tilesets': [],
        'properties': [
            {'name': 'purpose', 'type': 'string', 'value': '用户手工标注道路中心线的独立小样，不改原游戏路网'},
            {'name': 'imagePixelWidth', 'type': 'int', 'value': width},
            {'name': 'imagePixelHeight', 'type': 'int', 'value': height},
            {'name': 'imageSHA256', 'type': 'string', 'value': provenance['nativeSHA256']},
        ],
        'layers': [
            {'id': 1, 'type': 'imagelayer', 'name': '街区底图（锁定）',
             'image': image.name, 'x': 0, 'y': 0, 'opacity': 1,
             'visible': True, 'locked': True},
            {'id': 2, 'type': 'objectgroup', 'name': '路线（在这里画道路中心线）',
             'draworder': 'index', 'x': 0, 'y': 0, 'opacity': 1,
             'visible': True, 'locked': False, 'color': '#ff28b8', 'objects': []},
        ],
    }
    target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    (HERE / 'README.md').write_text(
        '# 小街区画路试验\n\n'
        '打开 `画路试验.tmj`。底图已经锁定，选择上面的“路线”对象层，'
        '按 P（插入多边形工具），沿道路中心线逐点点击，按 Enter 或右键结束，'
        '这样生成的是开放的多边线。不要点回第一个点闭合成填充多边形。每段结束后再画下一段。\n\n'
        '先画几条相互连接、含转弯和交叉口的路即可，不必马上描完全部。'
        '希望连通的交叉点尽量点在同一位置，必要时放大检查。'
        '第一轮可先描中央十字路与上方环路；左下小支路可能独立，不要为追求连通而强接穿楼。'
        '完成后按 Command+S 保存这份TMJ并告诉助手；不要改底图的大小、偏移或覆盖原图。\n\n'
        '这是新生成的一张试验底图，不是旧图裁片。实际尺寸及来源在 provenance.json。'
        '地图坐标就是图片像素坐标，没有再次施加等角投影。'
        '路线层初始为空，由用户亲自绘制；自动转路网及寻路尚未完成，不作为本次已验证结果。'
        '原游戏、旧路网、旧Tiled和用户布局均未改。\n', encoding='utf-8')
    (HERE / 'tiled-initialization.json').write_text(json.dumps({
        'imageSize': [width, height], 'imageSHA256': provenance['nativeSHA256'],
        'initialUserRouteObjects': 0, 'imageLayerLocked': True,
        'routeLayerEditable': True, 'pixelCoordinatesUnchanged': True,
        'automaticGraphExtractionVerified': False,
    }, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'map': str(target), 'imageSize': [width, height],
                      'userRouteLayerEmpty': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
