#!/usr/bin/env python3
"""Freeze only the user-confirmed roads into a standalone navigation preview."""
import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / '2026-11-05-modular-map-kit/delivery-kit/navigation-pilot'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    if OUT.exists():
        raise SystemExit('Preview already exists; preserve possible user edits')
    protected = [HERE/'画路试验.tmj', HERE/'画路试验_助手描线.tmj', HERE/'native-city-block.png']
    before = {str(p): sha(p) for p in protected}
    source = HERE/'画路试验_助手描线.tmj'
    doc = copy.deepcopy(json.loads(source.read_text()))
    removed = []
    for layer in doc['layers']:
        keep = []
        for obj in layer.get('objects', []):
            if obj.get('name') == '左下独立车道':
                removed.append({'id': obj['id'], 'name': obj['name'], 'reason': '用户明确否决：错误、不合理的车道'})
            else:
                keep.append(obj)
        if 'objects' in layer:
            layer['objects'] = keep
    assert len(removed) == 1
    OUT.mkdir(parents=True)
    tiled = OUT/'导航路网.tmj'
    save(tiled, doc)
    spec = importlib.util.spec_from_file_location('tracing_data_reader', HERE/'trace_assistant_roads.py')
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Re-read the real exported TMJ. No separate fabricated routing fixture.
    graph = module.graph_from_tiled(json.loads(tiled.read_text()))
    assert len(graph['connectedComponents']) == 1
    assert len(graph['nodes']) == 7 and len(graph['edges']) == 7
    assert all(e['name'] != '左下独立车道' for e in graph['edges'])
    graph.update({'sourceTiledSHA256': sha(tiled), 'imageSHA256': sha(HERE/'native-city-block.png'),
                  'imageSize': [1536, 1024], 'excludedVisualRoads': removed,
                  'status': 'confirmed-main-network-navigation-prototype-not-game-integration'})
    save(OUT/'graph.json', graph)
    shutil.copyfile(HERE/'native-city-block.png', OUT/'native-city-block.png')
    for name in ['index.html', 'navigation.js']:
        shutil.copyfile(HERE/'web'/name, OUT/name)
    (OUT/'README.md').write_text(
        '# 路网与导航对齐小样\n\n'
        '打开现有4186服务下的 `/delivery-kit/navigation-pilot/`。点路上起终点，或点示例，再播放。'
        '蓝色标记只沿绿色计算路径移动。左下错误车道已从路网剔除，底图画面本体暂未修。\n\n'
        'Tiled文件为 `导航路网.tmj`。此文件是独立确认主路副本，未覆盖此前用户稿/助手稿。'
        '修改后网页不会自动导入；本次数据已冻结用于对齐验证。\n\n'
        '本小样只有7节点/7路段/1个连通分量，全部双向；距离单位为图片像素，播放速度是演示速度。'
        '不是任意图像自动识路、正式配送/导航接入或游戏测试，也未操作存档。\n', encoding='utf-8')
    assert all(sha(Path(p)) == h for p, h in before.items())
    record = {'excluded': removed, 'nodeCount': len(graph['nodes']), 'edgeCount': len(graph['edges']),
              'componentCount': len(graph['connectedComponents']), 'sourceTiledSHA256': sha(tiled),
              'imageSHA256': graph['imageSHA256'], 'protectedInputs': before,
              'protectedInputsUnchanged': True, 'originalGameOrSaveTouched': False,
              'servedDirectory': str(OUT), 'runtimeInteractionVerified': False}
    save(OUT/'build-record.json', record)
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
