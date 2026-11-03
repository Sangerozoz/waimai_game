export const meta = {
  name: "county-region-next-batch",
  description: "按已认可地图标准连续制作下一批真实整区图与配准资料，完成后唤醒PM接入并推进下一批",
  phases: [{ title: "整区原生生产" }, { title: "原路标定与接缝资料" }],
};
const selection = { provider: "codex", model: "gpt-6.1-sol", reasoningLevel: "medium" };
const base = "docs/art/2026-11-03-county-region-atlas";
const common = `工作区为原checkout，用户已认可REGION-A-v3并授权持续完成整张地图及多Agent。先读AGENTS.md、本轮计划docs/superpowers/plans/2026-11-03-county-region-completion.md。只写分配给你的production子目录，不动他人资料/业务代码/原city/存档/git index。严禁tests/typecheck/回归/浏览器自动化/发布。不是游戏测试，这是实际地图制作。保留全部原生/全prompt/参考SHA；不脚本改生成美术像素、镜像、旋转、压扁。图已存在须核对记录复用，不重复生成。每个状态如实，不能把目标写成完成。`;
const artSchema = {type:"object",required:["id","generated","imageFile","recordFile","structureFile","note"],properties:{id:{type:"string"},generated:{type:"boolean"},imageFile:{type:"string"},recordFile:{type:"string"},structureFile:{type:"string"},note:{type:"string"}}};
const regSchema = {type:"object",required:["id","generated","imageFile","entryFile","seamReady","note"],properties:{id:{type:"string"},generated:{type:"boolean"},imageFile:{type:"string"},entryFile:{type:"string"},seamReady:{type:"boolean"},note:{type:"string"}}};
async function produce(items) {
  return await pipeline(items,
    item => agent(`${common}\n你只负责完整区域 ${item.id} 的原生美术，独占 ${base}/production/${item.id}/。先运行 python3 ${base}/planning/make-region-input.py --id '${item.id}' --output-dir '${base}/production/${item.id}/input' --neighbor-art '${item.neighborId}=${item.neighborFile}' --match-approved-scale（若input已存在，不覆盖，先读实际源记录）。读取输出的structures/与prompts/，先view_image其guide、用户认可A-v3以及item实际相邻图。按完整prompt调用内置image_gen，一次生成完整区域，guide是唯一源路/镜头/框架权威，A只是材质画风，不复制整套玻璃塔+学校球场+弧顶厅+排屋。当地landUse决定场景，屋顶全面无绿植。透明RGBA、全地块内容完整、同A细节尺度，骑手独立。内置生成保存后原字节复制到独占目录art/${item.id}-v1.png，记录完整实际prompt、原生sourcePath/尺寸/alpha/输出与参考SHA至generation-record.json。实看新图，有明显源路/屋顶违约最多一次定向整景编辑保留v1为v2，不重复刷图。不能API/CLI生图；认证错误最多同内置一次重试，仍失败将generated=false及原错写入record后返回，别假造图片。结果按schema报告真实路径。`, {provider:"codex",model:"gpt-6.1-sol",reasoningLevel:"medium",label:`整区:${item.id}`,phase:"整区原生生产",schema:artSchema}),
    async (art,item) => {
      if (!art?.generated) { log(`${item.id} 未生成，跳过标定；原因 ${art?.note || "worker failed"}`); return {id:item.id,generated:false,seamReady:false,note:art?.note||"worker failed"}; }
      return await agent(`${common}\n你只负责区域 ${item.id} 标定/接缝生产资料，独占 ${base}/production/${item.id}/registration/。实际原图 ${art.imageFile}，结构 ${art.structureFile}，参考邻区 ${item.neighborId}=${item.neighborFile}。先实看原图和结构guide，参考既有${base}/registration/measure-region-A.py、开发docs/reviews/county-region-20261103/atlas-interface.json。人工观察至少3处分散非共线原路口/沿路边缘的sourceMap/native imagePx/confidence；绝不造点。固定62.5/45仅统一缩放平移拟合anchorMap/anchorUV/nativePixelsPerUnit；逐点误差、隐藏估计、不可对应点null及实际可用道路走廊routeCoverageMapPolygon完整记录，原city不改，不旋转扭曲原图。输出measurement.json、region-entry.json、recommendation.md、可复算脚本与诊断资料。entry默认preview-only，PM决定ready；用户明确一两块地砖级的小错位接受，只修明显压路遮挡且影响使用，不因全图最大残差拒绝可用内部。源路严重穿楼/街口断开则给具体whole-region修图坐标、全楼移位建议，不能硬拟合藏错。共享16m与相邻图实际接头/自然切楼归属要记录；没有互补归属及实际对应不能说seamReady。主路/建筑受遮挡需局部整景编辑，只记录具体方案不改别人原图。schema中的generated仅表示原生文件实际存在且SHA已核对，与配准ready无关；原图存在则generated=true，即使preview-only或seamReady=false。按schema给真实entry路径、误差与遗留问题；产物不代表已部署或全县完成。`,{provider:"codex",model:"gpt-6.1-sol",reasoningLevel:"medium",label:`标定:${item.id}`,phase:"原路标定与接缝资料",schema:regSchema});
    }
  );
}
log("本次只推进下一相邻批，覆盖范围由args.waves明确给出；全县剩余队列并未省略或标完成。完成会自动唤醒PM继续包接入和下一批。");
const results=[];
for (const wave of args.waves) {
  const inputs=wave.map(item => { const n=results.find(x => x && x.id===item.neighborId && x.generated); return n ? Object.assign({},item,{neighborFile:n.imageFile}) : item; });
  const r=await produce(inputs);
  results.push(...r);
  if (r.some(x=>!x?.generated)) {log("当前波有未生成区域，依赖波不盲目继续；PM按真实阻塞接续。");break;}
}
return {results,countyComplete:false,nextAction:"PM接收真实图/标定包，收口接缝并交唯一开发，再按production-order继续，不转做新任务。"};
