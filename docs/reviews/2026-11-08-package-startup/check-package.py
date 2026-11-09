import argparse,gzip,hashlib,json,pathlib,unittest
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=pathlib.Path,required=True);ap.add_argument('--before',type=pathlib.Path,required=True);opt,remaining=ap.parse_known_args()
class Package(unittest.TestCase):
 def test_total_png_is_below_50_mib_runtime_budget(self):
  self.assertLess(sum(p.stat().st_size for p in opt.candidate.rglob('*.png')),50*1024*1024)
 def test_heavy_text_is_served_with_exact_gzip_sidecars(self):
  for p in opt.candidate.rglob('*'):
   if p.is_file() and p.suffix in ['.js','.json','.wasm','.css','.html'] and p.stat().st_size>1024:
    side=p.with_name(p.name+'.gz');self.assertTrue(side.is_file(),str(p));self.assertEqual(gzip.decompress(side.read_bytes()),p.read_bytes())
 def test_city_and_business_bundle_are_byte_identical(self):
  for p in (opt.before/'assets/main').rglob('*.js'):self.assertEqual((opt.candidate/p.relative_to(opt.before)).read_bytes(),p.read_bytes())
  for p in (opt.before/'assets/resources/import/5e').glob('5ec2b878-98ac-489c-aca1-a0346bcf1a17.*.json'):self.assertEqual((opt.candidate/p.relative_to(opt.before)).read_bytes(),p.read_bytes())
 def test_boot_settings_resource_and_application_references_resolve(self):
  settings=list((opt.candidate/'src').glob('settings.*.json'));self.assertEqual(len(settings),1);data=json.loads(settings[0].read_text());v=data['assets']['bundleVers']['resources'];self.assertTrue((opt.candidate/f'assets/resources/config.{v}.json').is_file());self.assertTrue((opt.candidate/f'assets/resources/index.{v}.js').is_file())
  app=list(opt.candidate.glob('application.*.js'));self.assertEqual(len(app),1);self.assertIn(str(settings[0].relative_to(opt.candidate)),app[0].read_text())
  index=list(opt.candidate.glob('index.*.js'));self.assertEqual(len(index),1);self.assertIn(app[0].name,index[0].read_text());self.assertIn(index[0].name,(opt.candidate/'index.html').read_text())
 def test_native_texture_versions_resolve_and_dimensions_preserved(self):
  source={p.name.split('.')[0]:p for p in opt.before.glob('assets/resources/native/*/*') if p.suffix in ['.png','.jpg']}
  config=json.loads(next((opt.candidate/'assets/resources').glob('config.*.json')).read_text());alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  def expand(value):
   if len(value)!=22:return value
   result=value[:2]
   for i in range(2,22,2):result+=format((alphabet.index(value[i])<<6)|alphabet.index(value[i+1]),'03x')
   return '-'.join([result[:8],result[8:12],result[12:16],result[16:20],result[20:]])
  versions=config['versions']['native']
  for i in range(0,len(versions),2):
   uuid=expand(config['uuids'][versions[i]]);version=versions[i+1]
   matches=list(opt.candidate.glob('assets/resources/native/*/'+uuid+'.'+version+'.*'));self.assertEqual(len(matches),1,(uuid,version))
  for p in opt.candidate.glob('assets/resources/native/*/*'):
   if p.suffix not in ['.png','.jpg']:continue
   with Image.open(source[p.name.split('.')[0]]) as a,Image.open(p) as b:a.load();b.load();self.assertEqual(a.size,b.size);self.assertEqual(a.format,b.format)
 def test_tinypng_provenance_is_actual_completed_output(self):
  receipt=opt.candidate/'package-receipt.json';self.assertTrue(receipt.is_file(),'actual provider receipt required');d=json.loads(receipt.read_text());self.assertEqual(d['imageProvider'],'TinyPNG official public website');self.assertGreater(d['imagesCompressed'],0);self.assertTrue(d['allImageInputsCovered'])
if __name__=='__main__':unittest.main(argv=[__file__]+remaining,verbosity=2)
