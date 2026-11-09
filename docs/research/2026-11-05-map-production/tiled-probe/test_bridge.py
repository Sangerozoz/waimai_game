import copy
import unittest
import tempfile
from pathlib import Path
import bridge

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.projection = {'axisX':[.7071067811865476,.62721137512625], 'axisY':[-.7071067811865476,.62721137512625], 'originMap':[-1591.5766733668343,75]}
        self.asset = {'id':'tree', 'anchorUV':[.48766447,.82302937], 'nativeSize':[1216,1294], 'nativePixelsPerUnit':1216/6.6}
        self.meta = {'projection':self.projection, 'editorOrigin':[768,768], 'pixelsPerUnit':16}

    def test_native_anchor_roundtrip_with_nonunit_scale(self):
        point = [-1601.25,80.125]
        obj = bridge.make_object(3,'persistent-tree',self.asset,point,1.25,self.meta,1)
        actual,scale = bridge.object_pose(obj,self.asset,self.meta)
        self.assertLess(max(abs(a-b)*16 for a,b in zip(actual,point)),.5)
        self.assertAlmostEqual(scale,1.25)
        # Tiled bottom-left is NOT the native trunk-ground anchor.
        self.assertNotEqual(bridge.project(point,self.meta),[obj['x'],obj['y']])

    def test_gui_move_delete_then_append_preserves_authoritative_objects(self):
        obj = bridge.make_object(1,'tree',self.asset,[-1600,80],1,self.meta,1)
        deleted = bridge.make_object(2,'deleted-lamp',self.asset,[-1590,70],1,self.meta,1)
        doc = {'nextobjectid':3,'layers':[{'type':'objectgroup','name':'Editable objects','objects':[obj,deleted]}]}
        doc['layers'][0]['objects'].pop()
        obj['x'] += 27
        obj['properties'].append({'name':'manualLocked','type':'bool','value':True})
        before = copy.deepcopy(obj)
        bridge.append_object(doc,self.asset,[-1595,72],self.meta,'ai-new',1)
        self.assertEqual(doc['layers'][0]['objects'][0],before)
        self.assertEqual([bridge.props(o)['persistentId'] for o in doc['layers'][0]['objects']],['tree','ai-new'])

    def test_nonzero_layer_offset_import_and_append_world_position(self):
        point=[-1601.25,80.125]
        obj=bridge.make_object(1,'original',self.asset,point,1,self.meta,1)
        layer={'type':'objectgroup','name':'Editable objects','offsetx':-13,'offsety':-26,'draworder':'index','objects':[obj]}
        doc={'nextobjectid':2,'layers':[layer]}
        expected=bridge.unproject([bridge.project(point,self.meta)[0]-13,bridge.project(point,self.meta)[1]-26],self.meta)
        actual,_=bridge.object_pose(obj,self.asset,self.meta,layer)
        self.assertEqual(actual,expected)
        before=copy.deepcopy(obj)
        target=[-1595,72]
        appended=bridge.append_object(doc,self.asset,target,self.meta,'new-at-world-point',1)
        actual,_=bridge.object_pose(appended,self.asset,self.meta,layer)
        self.assertAlmostEqual(actual[0],target[0]);self.assertAlmostEqual(actual[1],target[1])
        self.assertEqual(obj,before)

    def test_import_move_scale_duplicate_delete_then_incremental_append(self):
        # Fixture represents a GUI save: JSON numbers are positions and sizes,
        # copied tiles inherit properties, a deleted object is absent entirely.
        with tempfile.TemporaryDirectory(dir=bridge.HERE) as temp:
            temp=Path(temp); path=temp/'edited.tmj'; out=temp/'runtime'
            doc=bridge.read(bridge.HERE/'initial-map-snapshot.json')
            layer=bridge.object_layer(doc)
            layer.update({'offsetx':-13,'offsety':-26,'draworder':'index'})
            layer['objects']=[o for o in layer['objects'] if bridge.props(o)['assetId']!='HC-P-EAST']
            tree=next(o for o in layer['objects'] if bridge.props(o)['assetId']=='T02')
            tree['x']+=29;tree['y']-=11;tree['width']*=1.2;tree['height']*=1.2
            tree['properties']=bridge.property_list({**bridge.props(tree),'manualLocked':True})
            lamp=next(o for o in layer['objects'] if bridge.props(o)['assetId']=='P01')
            duplicate=copy.deepcopy(lamp);duplicate['id']=doc['nextobjectid'];doc['nextobjectid']+=1;duplicate['x']+=40;layer['objects'].append(duplicate)
            bridge.write(path,doc);original_bytes=path.read_bytes();bridge.import_map(path,out)
            scene=bridge.read(out/'assets/scene-layout.json');report=bridge.read(out/'import-report.json')
            self.assertEqual(len(scene['blocks']),4)
            self.assertEqual(report['deletedInitialPersistentIds'],['initial-HC-P-EAST'])
            self.assertTrue(report['roadsUnchanged'])
            meta=bridge.read(bridge.HERE/'bridge-meta.json')
            width=doc['width']*doc['tilewidth'];height=doc['height']*doc['tileheight']
            corners=[bridge.unproject(point,meta) for point in ([0,0],[width,0],[width,height],[0,height])]
            expected={'minX':min(p[0] for p in corners),'maxX':max(p[0] for p in corners),'minY':min(p[1] for p in corners),'maxY':max(p[1] for p in corners)}
            self.assertEqual(scene['bounds'],expected)
            self.assertEqual(report['runtimeBounds'],expected)
            self.assertEqual(report['editorCanvasSizePx'],[1792,1792])
            self.assertEqual(report['editorCanvasWorldCorners'],corners)
            base=bridge.read(bridge.HERE/'base-scene-layout.json')
            self.assertEqual(report['previousBounds'],base['bounds'])
            self.assertEqual(scene['roads'],base['roads'])
            self.assertLess(expected['minX'],base['bounds']['minX'])
            self.assertGreater(expected['maxY'],base['bounds']['maxY'])
            self.assertEqual((out/report['sourceMapSnapshot']).read_bytes(),original_bytes)
            self.assertEqual(report['tiledLayerOffsetPx'],[-13,-26])
            self.assertFalse(report['manualDrawOrderPreserved'])
            self.assertEqual(len({b['persistentId'] for b in scene['blocks']}),4)
            actual=next(b for b in scene['blocks'] if b['persistentId']=='initial-T02')
            self.assertTrue(actual['manualLocked']);self.assertAlmostEqual(actual['scale'],1.2)
            doc=bridge.read(path);before=copy.deepcopy(bridge.object_layer(doc)['objects'])
            asset=next(a for a in bridge.read(bridge.HERE/'assets/asset-manifest.json')['assets'] if a['id']=='P01')
            bridge.append_object(doc,asset,[-1595,72],bridge.read(bridge.HERE/'bridge-meta.json'),'ai-lamp',4)
            self.assertEqual(bridge.object_layer(doc)['objects'][:-1],before)
            bridge.write(path,doc);bridge.import_map(path,out)
            later=bridge.read(out/'assets/scene-layout.json')
            self.assertEqual(later['blocks'][:-1],scene['blocks'])
            self.assertNotIn('HC-P-EAST',[b['sourceAssetId'] for b in later['blocks']])

if __name__ == '__main__': unittest.main()
