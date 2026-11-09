import gzip,http.client,os,pathlib,socket,subprocess,tempfile,time,unittest
ROOT=pathlib.Path(__file__).resolve().parents[3]
class Transport(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.base=pathlib.Path(cls.tmp.name);cls.data=b'const game='+b'1234567890'*1000+b';';cls.gz=gzip.compress(cls.data,mtime=0)
  (cls.base/'bundle.abc123.js').write_bytes(cls.data);(cls.base/'bundle.abc123.js.gz').write_bytes(cls.gz);(cls.base/'index.html').write_bytes(b'<title>game</title>');(cls.base/'plain.json').write_bytes(b'{"game":true}');(cls.base/'nested').mkdir();(cls.base/'nested/index.html').write_text('<script src="main.js"></script>');(cls.base/'nested/main.js').write_text('game')
  outside=cls.base.parent/(cls.base.name+'-outside.txt');outside.write_text('outside');cls.outside=outside;(cls.base/'escape.txt').symlink_to(outside)
  with socket.socket() as s:s.bind(('127.0.0.1',0));cls.port=s.getsockname()[1]
  cls.fallback=cls.base.parent/(cls.base.name+'-fallback');cls.fallback.mkdir();cls.legacy=b'old-runtime-resource'*100;(cls.fallback/'old.cafe01.js').write_bytes(cls.legacy);(cls.fallback/'old.cafe01.js.gz').write_bytes(gzip.compress(cls.legacy,mtime=0));(cls.fallback/'bundle.abc123.js').write_text('obsolete');(cls.fallback/'outside.txt').symlink_to(outside)
  env=dict(os.environ,PORT=str(cls.port),PREVIEW_FALLBACK_BUILD=str(cls.fallback));cls.proc=subprocess.Popen(['bash',str(ROOT/'delivery-game/scripts/serve-web.sh'),str(cls.base)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(100):
   try:cls.request('/index.html');break
   except OSError:time.sleep(.02)
  else:raise RuntimeError('test server did not listen')
 @classmethod
 def tearDownClass(cls):
  cls.proc.terminate();cls.proc.wait(5);cls.tmp.cleanup();__import__('shutil').rmtree(cls.fallback);cls.outside.unlink(missing_ok=True)
 @classmethod
 def request(cls,path,encoding=None,method='GET',extra=None):
  c=http.client.HTTPConnection('127.0.0.1',cls.port,timeout=3);headers=extra or {}
  if encoding is not None:headers['Accept-Encoding']=encoding
  c.request(method,path,headers=headers);r=c.getresponse();out=(r.status,dict(r.getheaders()),r.read());c.close();return out
 def test_gzip_is_negotiated_and_losslessly_decoded(self):
  status,h,body=self.request('/bundle.abc123.js','gzip');self.assertEqual(status,200);self.assertEqual(h.get('Content-Encoding'),'gzip');self.assertEqual(gzip.decompress(body),self.data);self.assertLess(len(body),len(self.data))
 def test_identity_and_rejected_gzip_still_return_original_bytes(self):
  for value in ['gzip;q=0, *;q=1','br','xgzip']:
   status,h,body=self.request('/bundle.abc123.js',value);self.assertEqual(status,200);self.assertNotIn('Content-Encoding',h);self.assertEqual(body,self.data)
 def test_missing_sidecar_falls_back_to_identity(self):
  status,h,body=self.request('/plain.json','gzip');self.assertEqual(status,200);self.assertNotIn('Content-Encoding',h);self.assertEqual(body,b'{"game":true}')
 def test_head_uses_encoded_length_and_no_body(self):
  status,h,body=self.request('/bundle.abc123.js','gzip','HEAD');self.assertEqual(h.get('Content-Encoding'),'gzip');self.assertEqual(int(h['Content-Length']),len(self.gz));self.assertEqual(body,b'')
 def test_content_addressed_assets_have_vary_and_long_cache(self):
  status,h,body=self.request('/bundle.abc123.js','gzip');self.assertIn('Accept-Encoding',h.get('Vary',''));self.assertIn('immutable',h.get('Cache-Control',''));self.assertEqual(h.get('Content-Type'),'text/javascript; charset=utf-8')
 def test_html_is_revalidated_on_every_navigation(self):
  status,h,body=self.request('/?v2=1');self.assertEqual(status,200);self.assertIn('no-cache',h.get('Cache-Control',''))
 def test_etag_304_and_encoding_variants(self):
  _,gz,_=self.request('/bundle.abc123.js','gzip');_,raw,_=self.request('/bundle.abc123.js','identity');self.assertTrue(gz.get('ETag'));self.assertNotEqual(gz.get('ETag'),raw.get('ETag'))
  status,h,body=self.request('/bundle.abc123.js','gzip',extra={'If-None-Match':gz['ETag']});self.assertEqual(status,304);self.assertEqual(body,b'');self.assertIn('Accept-Encoding',h.get('Vary',''))
 def test_symlink_cannot_escape_the_served_build(self):
  status,h,body=self.request('/escape.txt');self.assertEqual(status,403);self.assertNotEqual(body,b'outside')
 def test_no_acceptable_representation_returns_406(self):
  for path,value in [('/bundle.abc123.js','gzip;q=0, identity;q=0'),('/bundle.abc123.js','*;q=0'),('/plain.json','gzip, identity;q=0'),('/plain.json','gzip;q=1, *;q=0')]:
   status,h,body=self.request(path,value);self.assertEqual(status,406,(path,value,status));self.assertNotEqual(body,self.data)
 def test_explicit_encoding_quality_overrides_wildcard(self):
  status,h,body=self.request('/bundle.abc123.js','*;q=0, identity;q=1');self.assertEqual(status,200);self.assertNotIn('Content-Encoding',h);self.assertEqual(body,self.data)
  status,h,body=self.request('/bundle.abc123.js','gzip;q=1, identity;q=0');self.assertEqual(status,200);self.assertEqual(h.get('Content-Encoding'),'gzip');self.assertEqual(gzip.decompress(body),self.data)
 def test_directory_redirect_keeps_query_and_relative_asset_base(self):
  status,h,body=self.request('/nested?v2=1');self.assertEqual(status,301);self.assertEqual(h.get('Location'),'/nested/?v2=1')
  status,h,body=self.request(h['Location']);self.assertEqual(status,200);self.assertIn(b'main.js',body)
 def test_cached_old_resource_is_served_from_explicit_previous_build(self):
  status,h,body=self.request('/old.cafe01.js','gzip');self.assertEqual(status,200);self.assertEqual(h.get('Content-Encoding'),'gzip');self.assertEqual(gzip.decompress(body),self.legacy)
  status,h,body=self.request('/bundle.abc123.js','identity');self.assertEqual(status,200);self.assertEqual(body,self.data,'current asset must win over previous build')
 def test_previous_build_cannot_expose_symlinks_outside_its_root(self):
  status,h,body=self.request('/outside.txt');self.assertEqual(status,403);self.assertNotEqual(body,b'outside')
if __name__=='__main__':unittest.main(verbosity=2)
