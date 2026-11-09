# Isolated two-native-image build fixtures; not a claim about all-game coverage.
import importlib.util,json,pathlib,shutil,struct,tempfile,unittest,zlib,hashlib
BASE=pathlib.Path(__file__).resolve().parent;ROOT=BASE.parents[2];script=ROOT/'delivery-game/scripts/optimize-web-package.py';spec=importlib.util.spec_from_file_location('packager',script);pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
class Images(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.source=self.root/'input';self.out=self.root/'output';self.source.mkdir();(self.source/'src').mkdir();resources=self.source/'assets/resources';resources.mkdir(parents=True)
  all_images=json.loads((BASE/'image-inventory-before.json').read_text())['files'];available=json.loads((BASE/'tinypng/web-receipt.json').read_text())['results'][:2];lookup={r['sha256']:r for r in all_images};self.rows=[lookup[j['sourceSHA256']] for j in available];self.jobs=[];uuids=[];versions=[]
  for i,(row,original_job) in enumerate(zip(self.rows,available)):
   source=ROOT/row['path'];uuid=json.loads(source.with_suffix(source.suffix+'.meta').read_text())['uuid'];uuids.append(pack.compact_uuid(uuid));versions.extend([i,'old00'+str(i)]);native=resources/'native'/uuid[:2]/(uuid+'.old00'+str(i)+source.suffix);native.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,native)
   job=dict(original_job);job['optimizedPath']=str((ROOT/job['optimizedPath']).resolve());self.jobs.append(job)
  (resources/'config.abcde.json').write_text(json.dumps({'uuids':uuids,'versions':{'native':versions}}));(resources/'index.abcde.js').write_text('resources')
  (self.source/'src/settings.abcde.json').write_text(json.dumps({'assets':{'bundleVers':{'resources':'abcde'}},'splashScreen':{'totalTime':2000}}));(self.source/'application.abcde.js').write_text("const settings='src/settings.abcde.json';");(self.source/'index.abcde.js').write_text("import './application.abcde.js';");(self.source/'index.html').write_text('<script src="index.abcde.js"></script>')
  self.before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.rglob('*') if p.is_file()}
 def tearDown(self):self.tmp.cleanup()
 def inputs(self,rows,jobs):
  inventory=self.root/'inventory.json';receipt=self.root/'receipt.json';inventory.write_text(json.dumps({'files':rows}));receipt.write_text(json.dumps({'status':'COMPLETE','provider':'TinyPNG official public website','results':jobs}));return inventory,receipt
 def unchanged(self):self.assertTrue(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==v for p,v in self.before.items()))
 def test_missing_inventory_image_is_rejected_without_publishing(self):
  i,r=self.inputs(self.rows[:1],self.jobs[:1]);self.assertRaises(ValueError,pack.optimize,self.source,self.out,i,r);self.assertFalse(self.out.exists());self.unchanged()
 def test_valid_header_but_corrupt_pixel_stream_is_rejected_atomically(self):
  job=dict(self.jobs[0]);raw=pathlib.Path(job['optimizedPath']).read_bytes();at=8;corrupt=bytearray(raw[:8])
  while at<len(raw):
   length=struct.unpack('>I',raw[at:at+4])[0];kind=raw[at+4:at+8];body=raw[at+8:at+8+length]
   if kind==b'IDAT':body=b'\0'*length
   corrupt+=struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff);at+=12+length
  bad=self.root/'bad-pixels.png';bad.write_bytes(corrupt);job['optimizedPath']=str(bad);job['outputSHA256']=hashlib.sha256(corrupt).hexdigest()
  i,r=self.inputs(self.rows,[job,self.jobs[1]]);self.assertRaises(Exception,pack.optimize,self.source,self.out,i,r);self.assertFalse(self.out.exists());self.assertFalse(self.out.with_name('output.part').exists());self.unchanged()
 def test_complete_valid_image_set_updates_versions_and_preserves_input(self):
  i,r=self.inputs(self.rows,self.jobs);result=pack.optimize(self.source,self.out,i,r);self.assertTrue(result['allImageInputsCovered']);self.assertEqual(result['imagesCompressed'],2);settings=json.loads(next((self.out/'src').glob('settings.*.json')).read_text());v=settings['assets']['bundleVers']['resources'];self.assertTrue((self.out/f'assets/resources/config.{v}.json').is_file());self.unchanged()
if __name__=='__main__':unittest.main(verbosity=2)
