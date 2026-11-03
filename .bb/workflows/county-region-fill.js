export const meta = {
  name: "county-region-fill",
  description: "修正样板真实验收证据通过后才允许继续整区生产；色调与建筑同质化不能延期",
  phases: [{title:"整县原生铺图"}],
};
const base="docs/art/2026-11-03-county-region-atlas";
const schema={type:"object",required:["id","generated","imageFile","entryFile","recordFile","qualityBlocked","note"],properties:{id:{type:"string"},generated:{type:"boolean"},imageFile:{type:"string"},entryFile:{type:"string"},recordFile:{type:"string"},qualityBlocked:{type:"boolean"},note:{type:"string"}}};
// Missing acceptance args reject before any worker or generation. The script has no FS access;
// a read-only worker verifies the actual evidence and hashes before the production pipeline.
const accepted=args.acceptedCorrection;
if(!accepted || accepted.acceptedBy!=="thr_7w55f3h66f" || accepted.status!=="accepted-correction" ||
 ![accepted.imageFile,accepted.imageSha256,accepted.evidenceFile,accepted.evidenceSha256].every(x=>typeof x==="string"&&x.trim()) ||
 !/^[a-f0-9]{64}$/.test(accepted.imageSha256) || !/^[a-f0-9]{64}$/.test(accepted.evidenceSha256))
 throw new Error("批量生图已暂停：必须提供本次PM已接受修正样板的真实imageFile/imageSha256/evidenceFile/evidenceSha256、acceptedBy=thr_7w55f3h66f与status=accepted-correction。");
if(!/^[A-Za-z0-9_-]+$/.test(args.productionVersion||""))throw new Error("必须提供新的productionVersion；不允许覆盖旧输入。");
if(!Array.isArray(args.waves)||!args.waves.length)throw new Error("Missing waves");
for(const wave of args.waves){
 if(!Array.isArray(wave)||wave.length>2)throw new Error("Each wave is limited to two regions");
 for(const item of wave)if(!/^[A-Za-z0-9_+-]+$/.test(item.id||"")||!/^[A-Za-z0-9_+-]+$/.test(item.neighborId||""))throw new Error("Invalid region id");
}
const gate=await agent(`只读质量闸，不生图、不改文件、不运行游戏/HTTP/browser/tests/typecheck/Git。不派子代理。核对这次修正样板与PM验收原始证据：${JSON.stringify(accepted)}。实际读取两个路径并计算SHA256，必须逐项匹配。证据必须明确记录本次2026-11-04偏黄/建筑雷同纠正已被PM thr_7w55f3h66f接受，绑定上述修正imageFile及imageSha256，覆盖中性日光无整体黄染与真实建筑形态差异。旧A-v3认可或空泛“已认可”不能替代本次证据。缺文件、哈希不符、验收不明确一律ok=false；不能自行补证或代填验收。`,{provider:"codex",model:"gpt-6.1-sol",reasoningLevel:"low",label:"修正样板证据闸",phase:"整县原生铺图",schema:{type:"object",required:["ok","note"],properties:{ok:{type:"boolean"},note:{type:"string"}}}});
if(!gate?.ok)throw new Error("修正样板质量闸未通过："+(gate?.note||"missing result"));
const shellQuote=value=>"'"+String(value).replace(/'/g,"'\\''")+"'";
const all=[];
// Keep workers bounded to two so stalled provider sessions do not multiply.
for(const wave of args.waves){
 if(wave.length>2)throw new Error("Each wave is limited to two independent regions");
 const r=await pipeline(wave, item=>{
  const previous=all.find(x=>x&&x.id===item.neighborId&&x.generated);
  const neighbor=previous?previous.imageFile:item.neighborFile;
  return agent(`用户已授权持续完成整张县图、按需多Agent。只读取AGENTS.md前30行（旧历史不通读），以及${base}/assembly-first-decision-20261103.md。只写${base}/production/${item.id}/${args.productionVersion}/独占新版本目录，其他只读，不动Git/源路/业务/存档，不tests/typecheck/浏览器/HTTP。禁止astra。当前只做已通过修正样板质量闸后的整区生产。偏黄/建筑同质化不是地砖小差，不能延期到整图后修。发现即停止并报告PM，不继续下一批。
你的区域${item.id}，真实邻图${item.neighborId}=${neighbor}。若目录已有图与记录先核对复用，不能覆盖或重复生成。缺输入时运行python3 ${base}/planning/make-region-input.py --id '${item.id}' --output-dir '${base}/production/${item.id}/${args.productionVersion}/input' --accepted-style-reference ${shellQuote(accepted.imageFile)} --neighbor-art ${shellQuote(item.neighborId+'='+neighbor)} --match-approved-scale。已通过本次修正样板证据闸：${JSON.stringify(accepted)}。读取生成prompt及architecture-intent.json的逐地块/逐楼组合；结构JSON只提取bounds/origin/projection/landUse/roads概要，不打印全文件；view_image实际guide、A-v3、PM已接受修正样板及真实邻图。修正样板为palette/style主参考、A-v3原锚；邻图仅边缘几何/轮廓，不继承其黄调或内部楼型。不能复制任一样板的整套建筑组合。调用内置image_gen一次完整原生整区，不用API/CLI。guide是原路/62.5°45°/布局权威，白灰墙、真实灰路、中性日光、局部材料本色，无全局黄/橙/奶黄或蓝罩染。按实际landUse及architecture metadata改变体量/屋顶/立面节奏/入口/用途，不能只换色或重复白框橙篷公寓，不强塞学校地标。设计分配不是已达标计数，按landUse做完整地块，无屋顶绿植。保存原字节art/${item.id}-v1.png、完整实际prompt/参考SHA/原生来源路径/尺寸/alpha/SHA到generation-record.json，实看记录明显问题到deferred-issues.json，不为错位重复生图。生成失败同内置重试一次，仍失败记录原错generated=false，不假造图片。
随后用python3 ${base}/planning/make-preview-entry.py <实际structure路径> <实际image路径> '${base}/production/${item.id}/${args.productionVersion}/placement-preview.json'生成显式名义preview-only entry；这只是底稿比例摆放，不是实测，不开放骑手/路线。不得伪造控制点、残差或ready。不要为此派子代理。按schema报告实际文件；qualityBlocked必须真实报告是否出现整体偏黄/建筑明显雷同，出现即true并停批，不因文件存在而标为风格通过；generated只表示实际原生图存在且SHA核对，不表示配准或整县完成。`,{provider:"codex",model:"gpt-6.1-sol",reasoningLevel:"medium",label:`铺图:${item.id}`,phase:"整县原生铺图",schema});
 });
 all.push(...r);
 if(r.some(x=>!x?.generated||x?.qualityBlocked!==false)){log("原图失败或风格被阻断，保留实际成果并交PM；停止后续批次。");break;}
}
return {results:all,countyComplete:false,nextAction:"PM合并真实原图到整体预览，交唯一开发批量数据接入，继续下一批；后续生产继续受修正样板质量闸约束；偏黄/建筑同质化立即停批，小地砖错位按原容忍规则。"};
