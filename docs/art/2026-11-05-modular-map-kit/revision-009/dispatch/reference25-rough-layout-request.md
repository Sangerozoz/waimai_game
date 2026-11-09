# 用户明确：25图总图要实际用于摆位和尺度，不只作为楼型图库

继续原接入作者，不新会话。v1 ZIP父已实际打开、CRC/路径与PNG尺寸核过：10213363字节、34唯一PNG、全部<=280，保留这个已交版本，**不覆盖v1/user-layout.tmj或其他可能已被用户手调的文件**。用户刚补充：“摆放的位置和大小，你还可以参考我们之前拼的那25张拼成一张地图的图。那个东西要发挥它应有的价值，毕竟我们也折腾了很长时间。”已写AGENTS/BRIEF。

## 找回的确切依据，全部只读
- 原25图完整拼图：docs/art/2026-11-04-county-twentyfive-region-plan/assembly/preview.html，placement-manifest.json。同一已认可25版本，不是25缩略卡contact sheet；仍名义摆放、非实测配准。
- 父已逐张核实际25母图SHA等于006/references/approved-25-index.json，图07保持TR25-v2。按原拼图已有transform和core裁切派生的1600宽布局参考：revision-009/references/layout25/approved-25-assembly-reference.jpg；source-record.json有25源与SHA/变换说明。没有新生图/改母图/改路，是原拼图的轻量参照，不当runtime底图。

## 现在做的有用小增量
在新`delivery-kit/reference25/`另存参考粗摆及预览（可以复用v1导出器/资源，不另造引擎/编辑器）。**实际看原总图和对应原单图区**，用它组织一个代表性相邻片区/小街区：大体量公建与中低住宅混合、前后排/成组关系、建筑相对路宽/地块的尺度、院落留白/树的高低和疏密。不是所有素材等大排一行、不是把大公建缩成小屋、不是把每楼放孤立长通道。初稿仍粗摆，少量一次成稿；不要转回逐点像素/全源净距复审。优先利用当前已有物件，参考版视觉层允许合理调整实例位置/等比大小，不改素材canonical或原道路/水/边界/POI/业务/存档。

给用户看原总图与该片区的实际Cocos结果对照，短记2～3个可观察的摆位/比例变化及参考图号。不能只把JPEG塞包就称已经按其布局。图有旧拼接错误，借相对关系和区域格局，不将像素自动认精确米数/原源绑定；不重开25图、修接缝、配准或整县精摆。既有163主图只读，新参考稿是可手调视觉副本，不复用旧的硬锁位/0.9/1.1限制。

如单独参考附件依赖v1，就明说目录/运行命令，正确相对引用，别假称完全独立；不必重打/覆盖主ZIP，用户现有布局更不能自动迁移。源参考图可附旁看，不把未配准大图放进实际路面/世界。一次导出/运行预览足够，不做矩阵或游戏tests/typecheck/回归/FPS。

## 已完成新素材，不必再生成
P11花箱与P12候车棚父已实际开280图、核原生对工具源逐字节/运行SHA，基础完整，可作为“可手调、未精校”新资产，粗默认锚点/尺寸从各.runtime.json/REPORT读：
revision-009/art-expansion/asset-pack-supplement/native/P11-001/P11-runtime-280.png
revision-009/art-expansion/asset-pack-supplement/native/P12-001/P12-runtime-280.png
准确元数据文件名请先列目录，不猜；parent-admission.json在asset-pack-supplement根。SHA分别0bb4b6c84c01f6371bffa7daf2c7843e75e1bb85cd8f6ce11b62b9f1129101be、e802d8769f540d1117da8ca0208eb9269e2f052642e38157d039dbae585207eb。前者低alpha杂点、后者玻璃偏乳白/细碎边和后脚推断，标注即可，不重生/精测。可加到新参考附件素材索引和模板，必要时在合适位置各粗摆一件。它们是参考画风下原创补充，不捏造25图上已存在公交业务。

原native/规划/共享city/现图保持，只允许你原写集＋delivery-kit/reference25。交实际文件和真实片区预览、来源图号/差异，不把派工当已按图搭完，不增加长审核报告。
