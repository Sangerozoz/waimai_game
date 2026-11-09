# 第五批：优先补相邻街区，不再分散挑大空地凑源数

第四40源已真实进入同一006地图。父已看关系图/U院/市场，实核当前scene SHA 9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f，143静态/462面、69唯一source绑定，原city SHA不变。截图仍很稀疏，楼边绿条＋长走道不等于丰富完整街景。继续复用你，不新建规划角色。

唯一写集：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/planning/fit-round-5/。上轮fit-round-4及其他文件全部只读。只做实际可复现的布局数据/图，不生图/运行游戏测试/typecheck/回归/FPS/服务器/存档/提交，不改source city/原路水/POI/业务/nav。共享006库/renderer、009/pipeline由接入作者独占，别修改或轮询其在写文件。

## 已完成输入，不读在途viewer
- 基线只读快照revision-009/baselines/visible143/：scene-layout.json、neighborhood.tmj、asset-library.json、asset-calibration.json、asset-manifest.json和parent-check.json；父实核143/462/69与实际27PNG/2,127,723B。只是本轮规划基线，之后接入必须再次对真实最新增量核冲突，不能用快照重置主图。
- 你的fit-round-3最终既有可行选项/未选源池，fit-round-4的已完成40源/usage-contracts/import-contract；原005～008与前四批布局只读。别从头扫完整历史/全县重复187选项盘点。
- 认可25图仍作身份/用途参考，原city/三层边界不动，原路只读。真实门/视觉接近与原导航停靠node分开，不能给设计关联伪造原经营绑定。

## 本轮重点
1. 先从已有可行未分配选项中，优先选能补第四批U院0176、市场0587、1735～1739住宅等周边空缺或连接相邻已画场地的真实源；目标最多约20个新源，实际合法多少报多少。不要为了数量再散落几十个远处孤点；可以只收口1～2个相邻区域。逐项保69已绑定源/143对象/462面与原源障碍，不把未画出的其他源楼当空地豁免。
2. 同片区组合应看得出高低、屋顶、用途差异，按真实尺度/用途评估现准入B01～B08，不能所有源都改住宅或复制四族整街模板。已有几何可行不等于美术完整；给出紧凑有用途的有限场地/入口连接，不每块只有漂浮绿条＋细长走道。现有地面全部只读，只能规划新源的增量面；建议修改既有场地可单列未实施建议，不动旧数据。
3. 所有worldSizeUnits/footprint/entryMap保存最终世界值，canonical×0.9/1/1.1等允许单次正比例，uniformScale只记来源，node scale1，不二次缩放；认可基准和旧实例不变。B07必须用修正真门11[704,609]、U实体/void/台阶，曲面/隐脚线不伪称测绘。完整原路节点、顺序、width、direction/projection逐值保持。
4. 去重适配真实旧格式：visualReplacements前批有sourceIndex/sourcePolygon单数，后批是sourceIndices/sourcePolygonsMap数组；父初次只扫数组只得65，合计显式兼容后为69，别漏掉旧4源，也别改写原记录。1源多模块/多源一景分别计数。
5. B09/B10/B11/T04仍hold不使用。B12/B13 clean/T05已经真实产出，但接入作者正独立做有限校准/比较，不把catalog当全量准入，不等它们回齐才出可用批。fit-round-4 usage-contracts中1731/1383等原生比较预留先保留不占；若后续实际比较改源，主图接入时再对最新基线处理。T05是低灌木独立候选，不能当已校准主树。
6. 对确需新原生路向/真实用途类型才可覆盖的卡点，最多给Top2并绑定具体真实source/原路向和已尝试否决证据，不开所有车型/朝向矩阵、不自行生成，不以“现库8族能塞别处”否认局部缺口。

输出fifth-expansion-batch.json（可更小稳定包）/import-contract.json、joint-fit-summary.json、少量投影图/REPORT。用脚本实际执行一次布局与静态净空核对，给稳定原输入SHA；source、场景、模块、面和拒绝分开计数。和现地图一套schema/源数组/门路分层，无白盒/新业务/新导航边。先交真实可用子集，再讲其他未解，不把计划或原生候选算已显示。
