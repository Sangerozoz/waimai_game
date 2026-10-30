"""Scenery imports must never invalidate the saved routing graph or invent geometry."""
import copy, importlib.util, pathlib, tempfile, unittest

SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'scripts/import-map-details.py'

def load_importer():
    spec=importlib.util.spec_from_file_location('map_details',SCRIPT)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

BASE={'title':'测试城','width':2226.4,'height':2226.4,'nodes':[{'id':'road-a','x':0,'y':0},{'id':'road-b','x':200,'y':0}],
      'roads':[{'id':'road','nodes':['road-a','road-b'],'speed':6,'direction':0}], 'pois':[{'name':'虚构餐厅','node':'road-a','kind':'restaurant'}],
      'labels':[{'text':'虚构路','x':0,'y':0,'kind':'street'}],'buildings':[],'areas':[],'waterways':[]}
XML='''<osm><node id="a" lon="0" lat="0"/><node id="b" lon="0.001" lat="0"/><node id="c" lon="0.001" lat="0.001"/><node id="d" lon="0" lat="0.001"/>
<way id="1"><nd ref="a"/><nd ref="b"/><nd ref="c"/><nd ref="d"/><nd ref="a"/><tag k="building" v="yes"/><tag k="name" v="Do not import real names"/></way>
<way id="2"><nd ref="a"/><nd ref="b"/><nd ref="c"/><nd ref="d"/><nd ref="a"/><tag k="leisure" v="park"/></way>
<way id="3"><nd ref="a"/><nd ref="b"/><tag k="waterway" v="river"/></way></osm>'''

class MapDetailTests(unittest.TestCase):
    def run_import(self,xmls,base=None):
        with tempfile.TemporaryDirectory() as temp:
            paths=[]
            for i,text in enumerate(xmls):
                p=pathlib.Path(temp)/f'{i}.osm';p.write_text(text);paths.append(p)
            return load_importer().add_details(copy.deepcopy(BASE if base is None else base),paths,(-.01,-.01,.01,.01))
    def test_adds_real_outer_scenery_without_changing_graph_pois_names_or_input(self):
        original=copy.deepcopy(BASE)
        out=self.run_import([XML])
        self.assertEqual(out['buildings'],[[[0.0,0.0],[111.32,0.0],[111.32,111.32],[0.0,111.32]]])
        self.assertEqual(out['areas'][0]['kind'],'green');self.assertEqual(out['waterways'],[[[0.0,0.0],[111.32,0.0]]])
        for key in ['nodes','roads','pois','labels','title','width','height']:self.assertEqual(out[key],BASE[key])
        self.assertEqual(BASE,original);self.assertNotIn('Do not import real names',str(out))
    def test_duplicate_source_tiles_and_reversed_closed_rings_do_not_double_buildings(self):
        first=self.run_import([XML,XML])
        reversed_xml=XML.replace('<nd ref="a"/><nd ref="b"/><nd ref="c"/><nd ref="d"/><nd ref="a"/>','<nd ref="a"/><nd ref="d"/><nd ref="c"/><nd ref="b"/><nd ref="a"/>')
        second=self.run_import([reversed_xml],first)
        self.assertEqual(first,second);self.assertEqual(len(second['buildings']),1)
    def test_a_polygon_enclosing_the_city_is_clipped_even_without_an_inside_vertex(self):
        xml='''<osm><node id="a" lon="-0.02" lat="-0.02"/><node id="b" lon="0.02" lat="-0.02"/><node id="c" lon="0.02" lat="0.02"/><node id="d" lon="-0.02" lat="0.02"/><way id="p"><nd ref="a"/><nd ref="b"/><nd ref="c"/><nd ref="d"/><nd ref="a"/><tag k="landuse" v="forest"/></way></osm>'''
        out=self.run_import([xml]);self.assertEqual(len(out['areas']),1)
        self.assertEqual(sorted(out['areas'][0]['points']),[[-1113.2,-1113.2],[-1113.2,1113.2],[1113.2,-1113.2],[1113.2,1113.2]])
    def test_incomplete_and_server_error_sources_are_rejected_instead_of_drawing_fake_connections(self):
        for xml in [XML.replace('<nd ref="b"/>','<nd ref="missing"/>'),'<osm><remark>runtime error</remark></osm>']:
            with self.subTest(xml=xml[-50:]):
                with self.assertRaises(ValueError):self.run_import([xml])

if __name__=='__main__':unittest.main()
