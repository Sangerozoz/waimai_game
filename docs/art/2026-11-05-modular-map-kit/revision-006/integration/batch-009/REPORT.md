# 009 首批北侧源址 — 已在原006 Cocos真实显示

入口：http://127.0.0.1:4186/revision-006/viewer/?view=north 。复用既有4186服务，没有另启/暴露端口。

本轮批准4个non-business原源址载体、同一原路149287903-0的连续0/1/2段。实际接入4楼＋8件有限场地物，共新增12静态实例；16批准地面＋4块有限连接铺地，共新增20地面。现在69静态实例/135地面，0楼拒绝。不是6～12完整街区，不是全县覆盖、导航/业务完成或用户验收。

## 交付入口与真实截图

- 可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。在原图persistentId增量添加一个group，没有init/重置；原57实例/115地面与所有旧层字段逐值保持。已有组偏移、可见性和index/topdown导出规则保留。
- 派生计划：009-derived-plan.json；源址映射：source-site-mapping.json；增量门禁：../north-009-increment.json。
- 实际Cocos全景：[四个源址与原路](cocos-north-overall.jpg)。画面由左下B01、中央双B02、右上B08组成，四楼完整可辨。
- 实际近景：[双办公门前与路肩](cocos-north-offices-close.jpg)、[市场门阶/长椅/双桶/灯/原路](cocos-north-market-close.jpg)、[B01侧门接地](cocos-north-shop-door-close.jpg)。近景边缘可见的邻楼裁出画面不是排除对象；全景仍包含全部四楼。
- 较宽关系：[北段与旧邻区](cocos-north-old-neighborhood-relation.jpg)。这是有限已画区域的关系图；区域之间仍有未布置/未绘制地面，不凭空画新道路连接、不称完整县图。上下方向来自原投影，非平面旋转。
- [旧休憩镜头实际保留](cocos-old-rest-retained.jpg)。旧N1/N2/S1/005/rest/suburb/garden/market/ucourt等全部cameraViews字段和D内存路线保持。旧截图原件未覆盖。

URL参数：`north`、`north-market`、`north-offices`、`north-shop`、`north-link`，另有`north-door-630/633/634/635`用于门点局部复看。只为新增镜头放大/留白，不缩放或移动旧物件。缩放保持视图中心的原实现保留。

## 四个源址绑定

| persistentId / sourceIndex | 原生楼型 | 候选楼体/原载体面积比 | 原生门点 |
|---|---|---:|---|
|009-src-0630 / 630|B08市场|1.004291|[820,803]|
|009-src-0633 / 633|B02办公|0.487299|[750,970]|
|009-src-0634 / 634|B02办公|0.672120|[750,970]|
|009-src-0635 / 635|B01小楼|0.521452|[973,965]|

visualReplacementOf/sourceIndex/sourcePolygon/sourceSHA绑定保存在派生计划、Tiled属性及runtime blocks/visualReplacements。源city的4个原polygon与绑定逐值相同；它们原本没有在此sprite viewer中绘制，所以没有造占位层再删，也没有移除其他源障碍。未覆盖源目标仍deferred，0新POI/导航边/业务入口修改。面积比不足1明确是“楼＋原地块余地”，不是等形重建原source footprint；本轮也不宣称完整旧parcel重建。

B01/B02/B08原生已实际打开，真实native/provenance/tool源字节逐一匹配；sourceNativeSHA256缺值仅补在本派生计划与映射中，批准原JSON保持。详情 native-provenance-verified.json。单一正缩放scale1，真实原生PPU/裁框worldSizeUnits/anchorUV保持。B01旧锚点与T01认可尺度保持，PNG没有旋转、镜像、重绘、拉斜或非等比缩放。

## 场地与静态保护

额外4面是每栋批准footprint＋批准walk/三条garden的有限凸包铺装底面，先画底面，再画原16面，最后原道路覆盖；受控草色#9db486不冒充新原生纹理。每块形成连门/路肩的有限步行前场，保留原批准1.5m门前通道。额外8件单列为4株T01、2盏L-near、市场P03长椅与P10双桶；全部复用既有图框和地脚校准。长椅/双桶在连续市场铺装内，无孤岛瓷砖。灯脚在原路肩，灯臂朝车道；没有把铺地新增成车行路或导航边。

geometry-and-door-report.json / mutual-new-building-walk-clearances.json：本栋原载体仅从自己的障碍列表排除，其他源楼全部保留；候选楼体距其他源楼最小2.675m，新四楼彼此最小7.869m，六对门前通道/其他楼与彼此通道静态均不相交。额外地面也逐块核其他源楼/原路/旧57区域。所有新增轮廓在蓝内、绿内；没有放到蓝外经营区域。

water-and-business-protection-check.json另外按真实源waterAreas核32个新轮廓，最小水polygon间距82.119m，最小原POI节点间距123.599m；同时保留源水线18m保守候选缓冲筛查。不存在把本栋门槛例外扩到别人楼/原路/原业务入口的情况。非经营载体仍非经营，不自动挂业务。

threshold-contact-static.json：手估本栋脚线处B08门前中心线约0.15m、B01约0.04m接触；两B02无该中心线接触，四件距门0.6m处都已在手估脚线外。原生门像素按真实PPU及原投影换算与规划entryMap一致。放大运行图中所选门阶与前场相接，没有看到明显沿墙内部穿行；这只是静态/视觉候选，不认证隐藏地基、台阶高差或可行走导航。

## 实际资源与节点读回

runtime-north-readback.json、runtime-verification.json来自真实Cocos页面全局读回，未拿HTML加载成功替代显示。静态69件＋D骑手/影子共71 items。全部69节点位置与导出原投影对应，最大浮点差约0.000001340投影像素；editorOrder和静态sibling次序对应Tiled。新增12项具体坐标/index/sibling见runtime-verification.json。

实际`__mapTextureStats`北侧视图：uniqueAssetImages27 / nativeFramesCreated25 / canvasFramesCreated2（北段地面＋骑手影子）。`__mapFrameSharing`按file同Frame：B02现在4实例共一Frame，B08两个共一Frame，T01十件共一Frame，其他重复件相同。运行包只含实际引用27张唯一PNG、2,127,723字节，全长边<=280；本批PNG字节增量0。没有带原生母版、25图、全城source-context分析快照进包。

原路现在26条/190节点：旧25条/178节点字段不变，新149287903-0完整12节点/宽8/方向0/sourceNodeIds与原city逐值核对；原投影相等。north009绘图仅裁视图bounds，不裁存储节点、不重建路由。道路前段与原生族约4.7度差是源路方向差，画面留有该轻微残差，没有旋转PNG或改路。

北侧镜头只生成有限north009画布2048×1817＝3,721,216像素；旧三地面仍在数据中而不与北侧全部常驻。north-link关系镜头只挂legacy006＋north009两块（实际canvasFrames3含影子）；旧rest镜头仍挂原三块、canvasFrames4。现有引擎只增添按新增镜头选择有限地面区域和单边2048配置，没有复制工程或实施全县渲染架构重写。当前仍加载69个静态sprite/27图；更多批次仍需区域/tile缓存接线，不能推断可常驻上千地块。未跑FPS/内存基准。

## SHA、执行与限制

- 父批准原JSON：`9360a09116a099e6df54fd2848ee49bd3b39ab7c90d0b5273ba0bfb4089cc9e6`
- 派生计划：`b2bee0c49739e2617634a13b4cb0826cc09b6c7878659ce97ed013235fda797c`
- 保护基线scene：`8035f4da47817a2d1361021f3e6c385fb3c058711390c4ea857b84ee8d6be020`
- 当前scene：`47248fdccddb32b95cb34bace541b67bcee7147590198eecb34603016eaa826f`
- 当前Tiled：`d312b8c8906bc0cd26befde34f318a74f14fd1bfeb738776be912de74ea7b716`
- 原city：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

559个只读源文件（005/007/008、006原生/规划、实际图来源、原city、库校准、既有图片等）SHA不变，详见read-only-protection.json / final-protection-and-replay.json；原57字段、115面、旧层、旧manifest项、镜头、D路径逐值保持。数据重导出不改TMJ/scene/manifest字节；重复append明确拒绝。旧staging作为批准核心4/16的准备证据保留，实际加8小物/4面在本派生包单列，pipeline/applied-009-first.json链接两阶段。

已执行（仓库根目录）：

```sh
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/prepare_first_009.py
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/add_first_009.py
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood_export.py export
```

当前增量已存在，前两命令重复运行拒绝；后续只export，不init重置。首批staging命令记录在009/pipeline/staging/expansion-009-first/prepare-report.json，运行证据与派生SHA独立。

可见限制：两B02后的T01多数树冠被楼体遮挡，未把“已载入”说成每棵都完整可见；市场温暖玻璃、原生彩边和有限280近景放大软化保留；道路与原生机位轻微差异保留；前场是有用途的有限补充，街段之间仍有未布置区域。B09/B10/B11/T03/P09未新增。没有新增车辆；原V01/V02仍仅既有静态候选。无生成图、游戏测试/typecheck/回归、存档、业务、提交或服务变更。实际显示已完成，用户/全县/导航/性能验收未完成。
