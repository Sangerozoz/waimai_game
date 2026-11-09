# 源125一场景两模块独立复审

结论：**safe-for-limited-integration**。仅允许给scene级consumer作者一次局部入图比较任务；不是现有单模块导入器可直接消费、不是美术/导航/用户/全县验收。当前没有候选静态几何阻塞项。consumer合同适配和接入前复核最新发布基线仍为必要门禁，不能删防重断言直接导入。

被审唯一候选：`revision-009/planning/compound-pilot/scene-compound-pilot.json`

SHA256：`a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27`。

实际基线：161静态 / 501面 / 81唯一源，scene SHA `e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7`，TMJ SHA `5a4ee4e32ca61f88c81d97161469fa558fdfa75d1f8051ffaeef7c03badfee5c`。pipeline/current-integration-reference.json与applied-market-life.json及实际已发布字节一致。本目录published161-scene.json为该已发布文件原字节冻结副本，不是用旧156回退主图。候选protection仍写156/497，属旧规划来源；本复审补查最新161/501，不擅自改候选SHA。新版本或发布前进后，本结论不得自动继承。

## 源、场景、模块所有权

实际解析1scene / 2modules / 5面 / 1唯一源 / rendered0，声明值一致。sceneId为009compound-source0125-court；module-01-B05与module-02-B01各自persistentId唯一，双向sceneId/moduleIds一致；5面均归属该scene并有明确moduleIds，ID不复用旧对象/旧面。125不在旧81源绑定或当前fit-round-4 reservations中。原city.buildings[125]的闭合多边形及SHA逐值相同，scene与两模块metadata均保留。

重复source125只在此scene内两模块共享；不把两个模块计为两个源。originalSemanticStatus保持unknown，scenicProgramme显式是PM纯美术设计，不新增POI、经营地址或nav边。原数据没有给这幢楼原始用途/门/经营绑定；不能以scenicRole声称原楼本来就是住宅或服务店。门的真实图像点与原停靠node分层，门路只是美术步行连接。

本目录review_static.py包含6种负例：重复persistentId、缺sceneId、scene漏列模块、跨scene复用源、旧绑定源、预留源，均拒绝。它是审查期合同模型，未调用或改写共享consumer，不冒充consumer功能已通过。旧sourceIndex/sourcePolygon及数组格式应只读归一化成临时scene所有权集合，不写回旧记录、不按模块长度重算旧源计数。

## 原路、比例与脚线

原路605760963-0完整4节点ID/坐标/顺序及原字段（width5、direction1等）逐值保持；不是只导出门口一段。两门接原段2→3，道路肩端点距离centerline减width/2均为0.03m，1.5m步行条带不穿原车道。固定原投影逐值一致；没有为贴原路切线旋转PNG（候选已说明原路屏幕切线约-41.15°与素材临街轴-28.49°不同，以侧院/路径衔接）。

从canonical世界尺寸、原生PPU、anchor与像素控制点独立反投影：B05@0.9、B01@1均与候选脚线/entryMap一致，worldSize=canonical×单一正比例、nodeScale1、rotation0、anchorUV保留。B01运行/原生归档SHA与既有library一致，B01尺度不改；B05同样复核运行PNG长边≤280与原生来源SHA。

限定：B05脚线来自手工可见角+隐藏后角推断；B01旧calibration只保留PPU/anchor，生产者沿用固定手估像素四点[198,910]/[438,1229]/[1055,931]/[815,612]，本复核明确采用同一手估定义，不能将其当新增测绘真值。该控制点缺少独立calibration字段是可追溯性风险，consumer须携带该定义与不确定性，不能改成整个屋顶billboard。旧实体保护采用既有exporter actual-old-shape证据（含无更近脚点时保守包络）、r4/r5实际脚线和comparison脚点，覆盖161个真实instance ID。

独立体间距 **4.691031036m**；双方门路避另一实体最小 **4.445288033m**。同源没有豁免互查。各门首0.6m为明确手估门槛容差，其后路径距自身脚线≥0.05m；所有共享庭院、种植面和连接面距两实体≥0.15m，真实自家门槛面只对其thresholdOf允许首段容差。仍需真实渲染看门槛高差与遮挡。

## 最新市场层与外部空地

复核全局3524原source（仅本scene源125豁免）、所有原道路段/width、水域与水道3m半宽+5m安全、原POI节点、蓝界、161旧脚点和501旧面。bbox只用于可证明距离下界的剪枝；没有略去未画原楼、没有对同源模块或旧普通地面全局豁免。

市场market-layout.json SHA与applied-market-life发布记录一致；T02树、P03椅、P01灯箱、P10桶、T05低灌丛的groundContactPolygonMap逐值匹配当前scene。树/灌丛anchor导出有2.84e-14m浮点差，按1e-8m比较，不记为移动。T02根部0.4m框、T05保守2.2×1.6m根团仍属手估；P03/P01/P10按既有可见底脚，非冠/顶盖精密脚线。市场连接面和4个合法替换旧面以最新scene实际多边形参与检查，不能拿v1市场图代替。

|候选部分|最近旧面及距离m|最近旧实体距离m|距其他原source m|距车道边m|
|---|---|---:|---:|---:|
|module-01-B05|009r4-src-0587-walk-0 1.312391|11.043372|13.948741|2.433242|
|module-02-B01|market-life-rest-terrace 6.198555|7.987965|14.154495|2.241389|
|module-01-B05-entry-walk-0|009r4-src-0587-walk-0 3.816987|14.586855|13.612869|0.030000|
|module-02-B01-entry-walk-0|market-life-rest-terrace 9.493425|11.178942|16.827231|0.030000|
|shared-court|market-life-rest-terrace 7.176454|8.555701|13.445226|1.123352|
|garden-bed|market-life-rest-terrace 3.134056|4.428229|8.228129|7.665873|
|court-link|009r4-src-0587-walk-0 4.559438|15.656985|14.302797|0.182444|

新市场脚点对任意候选面/体的最小间距4.428229m（garden-bed到P03椅）；不是把树冠透明范围当可步行空地。B05最近旧面仍为原0587-walk-0，1.312391m，满足本体1m门禁但余量只有0.312391m，入图需重点检查可见脚线/排序，不扩大为误差无限许可。

共享4块铺装构成连通并集；garden-bed与shared-court接边，花土不替代通行。共享连接面宽1.5m，接两门路和庭院。材质/路径层次应在consumer按purpose/surfaceClass维持明确先后，不用土草盖住门路，也不改任何旧地面。当前纯几何连通不等于实际Cocos遮挡/观感验证。

两个模块在source125外部的脚线面积分别8.021113㎡（B05，insideFraction0.5916336025）和13.400038㎡（B01，insideFraction0.4516761317），独立凸多边形裁切与候选一致。只有约19.47%原source面积由新脚线覆盖，其余是有意美术重组；不是等形原楼还原。本候选的场景所有权只绑定源125和这5个有限新面，**不新增一圈可经营土地所有权**。外伸区域按上述全局障碍逐项验证无占用；不能将“原source只保存metadata”推广为随意抹掉其他未画源。不存在旧面编辑权限请求，不能借此接入批准重划邻院。

## 生产者检查覆盖与缺口

来信提87项，实际冻结static-verification.json为95项（verify_static.py逐require追加计数，包含按模块/面重复的检查）。它覆盖scene双向所有权、源副本、比例、脚线/门、源路和肩点、PNG、互避、铺装连通及全局遗漏障碍下界；不是95项独立验收。其几何只针对156/497，未包含市场五件新物和最新面。当前复核补齐这一缺口，但没有运行producer脚本，也未把检查数当通过理由。

仍未覆盖：原生隐藏脚线实测、实际门阶高差/树冠可见遮挡、Cocos图层排序、最终近景清晰度/设备性能、实际consumer兼容与防重复。这些均不由静态通过自动解决。没有发现当前候选实体/路径净空的可证错误；B01手估控制点来源散落和旧156protection需接入时显式携带当前基线证明，为非阻塞追溯项。

## consumer最小适配与准入负例

1. 在任何写入前解析scene级source集合、source原多边形/SHA和moduleIds；验证模块/面双向归属、每源唯一scene所有权、persistentId/面ID唯一以及旧绑定/预留源排重。允许同scene共享源，拒绝跨scene、旧绑定冲突；不能仅删assigned断言。旧单模块输入以临时legacy scene方式处理，保留原字段及数值，不回写旧记录。
2. 每模块按自身canonical尺寸×一次比例和真实anchor创建独立instance；每面按scene归属且保留moduleIds/thresholdOf，实体/路径彼此互查。sourceCount按scene源集合并集，moduleCount独立，scene1/source1/modules2；displayed/rendered状态只能在实际入图证据后更新。若schema未知、scene模块漏列/孤儿、源多边形不符、同源互相穿体、旧面ID被占用或重复导入，必须在事务写入前拒绝。
3. 接入作者在精确候选SHA下另产增量，不重放snapshot；当前基线若不是本审161/501发布SHA，先按新发布重核。保护旧161对象、501面、81源映射、原POI/路线，consumer只增本scene2模块/5面，源并集理应增加1而非2。不擅改B01/PNG/library/Tiled既有层。

本审查仅给合同适配作者明确的受限入口，不提交共享实现补丁。源125不需新增业务停靠/经营地址；门路终点在原路肩，不把门强绑POI。

## 保护与复核材料

review.json记录62项本次独立断言、7个实体/面的全局距离与市场五脚点距离、裁切面积、负例及SHA；全部断言通过。冻结前后30个输入SHA一致，changedInputs为空。只写本目录，原审查目录/producer/共享代码/原city/PNG均只读。未生图、未游戏tests/typecheck/回归/FPS、未浏览器/服务/提交。review_static.py仅AST提取已读无副作用纯几何函数；未导入/执行producer或共享导入器模块。
