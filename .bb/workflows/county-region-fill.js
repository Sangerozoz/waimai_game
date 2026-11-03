export const meta = {
  name: "county-region-fill",
  description: "先完成整县原生区域覆盖并名义拼放，明显遮挡归档到整图后集中修补",
  phases: [{title:"整县原生铺图"}],
};
const base="docs/art/2026-11-03-county-region-atlas";
const schema={type:"object",required:["id","generated","imageFile","entryFile","recordFile","note"],properties:{id:{type:"string"},generated:{type:"boolean"},imageFile:{type:"string"},entryFile:{type:"string"},recordFile:{type:"string"},note:{type:"string"}}};
const all=[];
// Keep workers bounded to two so stalled provider sessions do not multiply.
for(const wave of args.waves){
 if(wave.length>2)throw new Error("Each wave is limited to two independent regions");
 const r=await pipeline(wave, item=>{
  const previous=all.find(x=>x&&x.id===item.neighborId&&x.generated);
  const neighbor=previous?previous.imageFile:item.neighborFile;
  return agent(`用户已授权持续完成整张县图、按需多Agent。只读取AGENTS.md前30行（旧历史不通读），以及${base}/assembly-first-decision-20261103.md。只写${base}/production/${item.id}/独占目录，其他只读，不动Git/源路/业务/存档，不tests/typecheck/浏览器/HTTP。禁止astra。当前只做整区原生铺图，不做人工配准或逐片修接缝，明显遮挡记问题，等整图拼完集中修。
你的区域${item.id}，真实邻图${item.neighborId}=${neighbor}。若目录已有图与记录先核对复用，不能覆盖或重复生成。缺输入时运行python3 ${base}/planning/make-region-input.py --id '${item.id}' --output-dir '${base}/production/${item.id}/input' --neighbor-art '${item.neighborId}=${neighbor}' --match-approved-scale。读取生成prompt；结构JSON只提取bounds/origin/projection/landUse/roads概要，不打印全文件；view_image实际guide、A-v3风格母版、真实邻图。调用内置image_gen一次完整原生整区，不用API/CLI。guide是原路/62.5°45°/布局权威，A只供画风，不复制其整套地标，按landUse做完整地块，无屋顶绿植。保存原字节art/${item.id}-v1.png、完整实际prompt/参考SHA/原生来源路径/尺寸/alpha/SHA到generation-record.json，实看记录明显问题到deferred-issues.json，不为错位重复生图。生成失败同内置重试一次，仍失败记录原错generated=false，不假造图片。
随后用python3 ${base}/planning/make-preview-entry.py <实际structure路径> <实际image路径> '${base}/production/${item.id}/placement-preview.json'生成显式名义preview-only entry；这只是底稿比例摆放，不是实测，不开放骑手/路线。不得伪造控制点、残差或ready。不要为此派子代理。按schema报告实际文件；generated只表示实际原生图存在且SHA核对，不表示配准或整县完成。`,{provider:"codex",model:"gpt-6.1-sol",reasoningLevel:"medium",label:`铺图:${item.id}`,phase:"整县原生铺图",schema});
 });
 all.push(...r);
 if(r.some(x=>!x?.generated)){log("有原图未成功，保留实际成果并交PM接续，不将缺图当完成。");break;}
}
return {results:all,countyComplete:false,nextAction:"PM合并真实原图到整体预览，交唯一开发批量数据接入，继续下一批；整图后集中修明显遮挡，小错位保留。"};
