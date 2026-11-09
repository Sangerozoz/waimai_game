import hashlib,json,math,pathlib
from PIL import Image,ImageChops,ImageStat
base=pathlib.Path(__file__).resolve().parent;root=base.parents[3];receipt=json.loads((base/'web-receipt.json').read_text());rows=[]
for result in receipt['results']:
 source=root/result['source'];output=root/result['optimizedPath'];assert hashlib.sha256(source.read_bytes()).hexdigest()==result['sourceSHA256'];assert hashlib.sha256(output.read_bytes()).hexdigest()==result['outputSHA256']
 with Image.open(source) as a,Image.open(output) as z:
  assert a.size==z.size and a.format==z.format;before=a.convert('RGBA');after=z.convert('RGBA');alpha=ImageStat.Stat(ImageChops.difference(before.getchannel('A'),after.getchannel('A'))).mean[0]
  psnr=[]
  for background in ['white','#202020']:
   first=Image.new('RGBA',a.size,background);first.alpha_composite(before);second=Image.new('RGBA',a.size,background);second.alpha_composite(after)
   stats=ImageStat.Stat(ImageChops.difference(first.convert('RGB'),second.convert('RGB')));mse=sum(x*x for x in stats.rms)/3;psnr.append(None if mse==0 else 10*math.log10(255**2/mse))
  rows.append({'source':result['source'],'beforeBytes':result['inputBytes'],'afterBytes':result['outputBytes'],'width':a.width,'height':a.height,'alphaMeanAbsoluteDifference':alpha,'whiteCompositePSNRdB':psnr[0],'darkCompositePSNRdB':psnr[1]})
summary={'provider':receipt['provider'],'images':len(rows),'allDimensionsAndFormatsPreserved':True,'originalAuthoringSHAUnchanged':True,'inputBytes':sum(x['beforeBytes'] for x in rows),'outputBytes':sum(x['afterBytes'] for x in rows),'maximumAlphaMeanAbsoluteDifference':max(x['alphaMeanAbsoluteDifference'] for x in rows),'minimumWhiteCompositePSNRdB':min(x['whiteCompositePSNRdB'] for x in rows if x['whiteCompositePSNRdB'] is not None),'minimumDarkCompositePSNRdB':min(x['darkCompositePSNRdB'] for x in rows if x['darkCompositePSNRdB'] is not None),'rows':rows,'limit':'numerical image checks and later visual inspection, not98% visual acceptance'}
(base/'quality-result.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='rows'}))
