# 市场0587：候场、树荫长椅与独立垃圾点已实际显示

本轮把同一市场前场组织为可理解的日间用途：原门前有限候场铺装＋入口灯箱、支路连通的树荫长椅、另一侧独立双桶收集点，沿入口配一簇低灌木。没有复制610圆桌双凳套餐，没有新增楼或靠挪楼/造路填90～108m空白。所有新物已在实际Cocos近景见到，数量仅作审计。

## 实际画面与入口

- [市场完整用途场景](cocos-market-life.jpg) / [同一viewer](http://127.0.0.1:4186/revision-006/viewer/?view=market-life)：整栋既有B08市场、真实入口台阶、原1.5m门路及原道路同框，五件新物可辨。
- [入口与设施细节](cocos-market-life-detail.jpg) / [细节镜头](http://127.0.0.1:4186/revision-006/viewer/?view=market-life-detail)：长椅腿、灯箱底座、双桶盖/脚、低灌木及短连接更清楚；屋顶自然裁切，完整楼体保留在上图。不是靠藏问题对象宣称通过。

两图均实际Cocos页面取图后直接复制，未生图/拼贴/改图；embed=1只隐藏预览工具条。第一次细节发现新source-court轮廓的小凹口，随后仅去掉该获准面一个凹顶点，补齐步道旁小缺口，物件/原门路不动；before图、布局与pre-court-refinement.tmj保留iterations/和market-layout-v1.json，最后两张均已重新实际打开核对。没有逐物矩阵。

可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。旧life-street、第五批市场/住宅、rest/N1/N2/S1、郊区/U院、第四批与native-low/shop/shrub镜头全部字段保持，只新增market-life/market-life-detail。新镜头仍同一006引擎与同一scene，无新工程/服务。

## 精确地面权限与前态

以已发布156静态／497面为基线。只修改父授权的下列4面，原ID保持、完整原始world/Tiled字段都在actual-four-surface-diff.json。旧source-court原来主要覆盖载体内部的大面积白砖，现收成沿真实连拱市场前缘的有限入口铺地；三条原绿矩形改成树/低灌木/垃圾点旁的有边界小口袋。

|surfaceId|材质适配|候选面积前→后|用途/理由|
|---|---|---|---|
|009r4-src-0587-source-court-587|S01-paving → S01-paving|143.819 → 34.480|finite entrance apron follows actual curved-market front; replace large mostly hidden carrier paving|
|009r4-src-0587-planted-pocket-0|G12-r4-planted → G02-planting|41.788 → 5.020|bounded shade-tree pocket adjoining waiting terrace, no floating rear rectangle|
|009r4-src-0587-planted-pocket-1|G12-r4-planted → G02-planting|8.566 → 5.260|low shrub planting joins entrance apron, native root is inferred|
|009r4-src-0587-planted-pocket-2|G12-r4-planted → G01-lawn|8.566 → 6.120|finite green edge bounds garbage pad; no extra facility/vehicle road|

原`009r4-src-0587-walk-0`的world polygon、材质、所有Tiled属性、宽度/位置/顺序严格相同。其他493面world/Tiled全字段与相对序列相同。四个授权面的原层ID/index/offset/visibility保持，属性只改surfaceAssetId或有限polygon/x/y；没有修改源parcel、道路或业务图。

新增有限4面，原ID没有复用/改名：

- `market-life-rest-terrace`：finite waiting terrace with one bench and adjoining shade-tree pocket；面积约16.780候选平方米。
- `market-life-waste-pad`：small separate double-bin collection landing, away from main door；面积约8.840候选平方米。
- `market-life-rest-connector`：short visual pedestrian branch connecting existing immutable1.5m walk to rest landing; no nav edge；面积约5.856候选平方米。
- `market-life-waste-connector`：short visual pedestrian branch connecting existing immutable1.5m walk to waste landing; no nav edge；面积约3.026候选平方米。

两条支路是视觉步行面，分别宽1.5/1.2候选米，从原门路边界接到长椅平台/垃圾落脚区。每条用原walk侧边半平面裁止，新polygon只共享边界、面积全在门路外侧；不从旧path中心叠大铺装盖住原路。四个授权基底保持原先在walk之前的draw index，旧门路仍在其上，原道路最后覆盖所有地面。无车行连接/导航边。

## 五件原生设施与静态顺序

P01/P03/P10/T02母版与运行图均先实际打开，原calibration脚点也已读取：P01四角底板、P03四腿接点、P10底部保守4角均沿原PPU正等比换算；T02用原可见树根校准的0.4m候选保护盒。native-contact-provenance.json给母版/tool绝对路径与相同SHA，原PNG未改。T01也读取了原认可尺度后选择本次更适合有限种植边的T02，未重设计T01。

|persistentId|资产|实际anchorMap|不变canonical world frame|新static rank|用途|
|---|---|---|---|---|---|
|market-life-shade-tree|T02|[-1459.0155590273594, 215.1491722245363]|2.9657×5.9943|128.666667|one natural shade tree next to waiting seat|
|market-life-waiting-bench|P03|[-1456.6028222970895, 213.67312972162287]|2.4838×2.3614|128.833333|one waiting bench facing the market forecourt|
|market-life-entry-sign|P01|[-1460.2439768358852, 204.87585777944622]|0.7890×1.2226|128.166667|daytime blank information lightbox near entrance, no invented text|
|market-life-waste-bins|P10|[-1456.8860127110972, 203.31891303519924]|1.6690×1.8649|128.333333|separate public collection double bin, no business logic|
|market-life-low-shrub|T05|[-1461.8885168208997, 211.06277851901356]|2.5160×1.8017|128.500000|one additional low clump comparison along entrance planting edge|

五件都用已有单一PPU/anchorUV/世界图框，node scale1，无旋转/镜像/拉伸。新物按实际脚点深度插入旧排序值之间，而非全置顶；市场旧editorRenderOrder128及原156所有固定值/相对顺序保持。实际Frame/node详情在new-five-runtime-node-frame-check.json。

实际画面中P03座面/四腿可辨，树干在旁、长椅不遮门；P10两种颜色盖与独立箱体/落脚可辨，结构/姿态在此大小未见明显异常，所以保留候选，不改PNG；P01是原生空白灯箱/公告面，本次不伪造文字或广告业务。它们均在前场而非楼后。T02为原同族自然树变体，非新增树种/已精密机位通过。

T05只增加本次1簇，与旧612庭院1簇合计2，使用原316.376402894 PPU及裁框/UV/2.515990424×1.801651434图框。根原点[660,930]仍为叶簇遮住的推断，原像素±70候选不确定性；保守2.2×1.6接地包络完整在有限种植面内。细节中低叶团在树冠一侧可辨，有自然局部叠挡，没有藏楼后；不称实测根或导航接地验收。B12/B13仍原各1有限比较实例，T04继续hold，其余hold不解除。

没有桌/凳/围栏闭环/油罐/菜畦。V01/V02不放：本轮没有给出独立合法parkingSpace与可理解的车辆接近安排，原1.5m门路保持步行用途；未画假车道、未新增交通AI/业务。

## 原障碍、门路和真实尺度核验

prepare_market_life.py逐面/逐物核原source他楼、原156地脚/保守接地点、未获准493面、原道路车道、水polygon/全部492原waterway（3m半宽+5m安全）、蓝边和原POI。只自己的587载体豁免，旧市场本栋实际占地仍作为障碍，门/台阶前未被新物覆盖。授权四面是支撑地面，原walk不是新物可豁免面。新增连接与walk共享边仅是显式几何接边，不是放宽全体障碍。

各类最小候选静态距离见clearance-summary.json：

- otherSourceGap：2.477578
- old156GroundContactGap：0.519840
- unapprovedGroundGap：1.225693
- waterPolygonGap：116.915972
- waterwayMinus3mGap：192.370469
- carriagewayGap：13.788570
- originalPOIGap：164.812683
- fixtureMinimumImmutableWalkGap：1.225693

实际放大检查未见门口被桶/树/灯箱堵住，原步道连续可见；主入口台阶、影子/软边仍是原生估点，不拿静态净距宣称可通行导航或用户验收。

## 真实节点、Frame与资源

当前161静态／501面／81源绑定：新增5物、4面、改4面，源绑定和楼数均未增加。old156所有block字段、坐标、图框/PPU/UV、固定顺序及实际UI尺寸逐项等于第五批基线；旧497地面中除获准4面外493全部保持。Tiled旧156 sprite对象和其他ground对象全字段保持，旧层/tiles/offset/index也保持，只有新增group向后追加。

__mapPreviewOrder＋__mapUIDimensions实读161静态＋D/影子共163项，全量核坐标/UI/world frame/scale/index；最大位置差约0.000001340投影像素。market-life-runtime.json／market-life-detail-runtime.json保留实际读回。新物使用小数rank，D仍原内存蓝内路线，不变业务。

运行仍30张唯一PNG，总2,425,880字节，新增PNG0字节，全长边<=280。P01/P03/P10/T02/T05原本已在包中，新实例只增加引用；相同file+SHA实际共享同一image/Frame。__mapTextureStats实读30 images／28 nativeFrames／2 canvasFrames（当前有限地面＋D影子），无每实例Texture。原生、25图、全城分析快照未入viewer。

当前新镜头只激活market-life-ground一块2048×1817画布，9面/1原路引用，约72.34×72.34m有限bounds；单份RGBA候选14,884,864字节，不是实际总内存。没有FPS或实际内存测量，不等容量审查或假称性能通过。原95道路引用619完整节点/宽度/方向/投影逐值保留，只在画面中clip。

## SHA保护与复现

- baselineSceneSHA256：`69ee3cb14645be306500d5db09a46a3eac4b5c75c8154eaacb586a90a23e6cc8`
- baselineTiledSHA256：`861adb2bb3f5ca0b227e96496cc18b561ece6ec7f06a264b8e73938ad208dc21`
- marketLayoutSHA256：`d70ca481d21fb6cb33c37a075c4d146c9013d58f3d6284de443f538b4c2fde14`
- finalSceneSHA256：`e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7`
- finalTiledSHA256：`5a4ee4e32ca61f88c81d97161469fa558fdfa75d1f8051ffaeef7c03badfee5c`
- sourceCitySHA256：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

691个只读源/旧证据文件SHA不变，资产库/校准条目/PNG也未改；原156、493非授权面、原walk、旧镜头、D/source/POI/nav与原city均保护。actual-four-surface-diff.json给每面完整world前后/Tiled前后/变更字段/层与组偏移；tiled-four-surface-diff.json保留原始前态，court-refinement.json另记小凹口收顺过程，未覆盖before证据。

实际执行prepare_market_life.py→add_market_life.py→neighborhood_export.py export→capture_market_life.py→verify_market_life.py。add重复运行会拒绝；export重复后scene/manifest/TMJ字节稳定。较早冻结ground断言只增加与本次父授权4 ID/明确after值对应的严格比对，不放开其他面或初始化覆盖手调图；不重放任何历史scene快照。

## 可见未解与边界

市场与第五批新簇之间90～108m空白仍保持，没有借本次做全面密度规划；前场之外大部仍未布置。设施能表达候场/树荫休息/收集用途，但受控绿地仍较平，灯箱仍空白，B08暖玻璃/曲面基脚和原生软alpha、T02亮叶缘、小物画法差异仍可见；T05根推断与叶团重复仍只比较。没有把新增5件数量或静态能放当美术达标、全县完成或用户验收。

本轮只写006/integration、viewer与009/pipeline。无生图、新Agent/工程/服务/端口操作、游戏tests/typecheck/回归/渲染矩阵/FPS、存档、产品/UI/经济/业务代码或提交。
