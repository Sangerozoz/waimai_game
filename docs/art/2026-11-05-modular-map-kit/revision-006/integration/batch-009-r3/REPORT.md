# 009第三批20源：同一006实际显示

入口：http://127.0.0.1:4186/revision-006/viewer/?view=r3-central 。先前第二批5源的实显、UI与截图回报已完成，本轮从其真实最终74实例/164地面继续增量，没有重放57或69快照。

20唯一源/20模块/96面全部准入，拒绝0，额外物件/地面0；当前94静态实例/260地面。加上首4、第二5，当前29个明确源载体有视觉模块绑定，不等于29个源footprint等形重建、完整街区或全县已覆盖。654+2387组合未加入。现阶段仍未用户/导航/性能验收。

## 实际画面与可编辑入口

- [较宽原路/新旧片区关系图](cocos-round3-wide-relationship.jpg)：1536上限的有限关系视图；20新图框实际均在canvas及工具条以下，overview-new-frame-viewport-check.json有运行节点/UI/镜头到CSS包围框校核，范围图不是近景清晰度证据。
- [中央混合街巷近景](cocos-round3-central-close.jpg)：新B05/B01与既有第二批B01同场，真实门、载体庭院、窄通路及原路相接。
- [东北住宅近景](cocos-round3-northeast-close.jpg)：B01/B05/B06的沿街相邻源址，庭院与边缘种植组织；未把间隔源楼伪装成已画楼。
- [办公门前近景](cocos-round3-office-close.jpg)：B02真实门前与较长1.5m通路/原路肩；外围仍有未布置空地。
- Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`；派生计划009r3-derived-plan.json；父原/派生/基线SHA分别记录在../round3-009-increment.json与final-verification.json。

新镜头按钮：`r3-overview`、`r3-central`、`r3-northeast`、`r3-office`；另有`r3-south`、`r3-large-home`参数用于后续局部复看，本轮没有跑逐对象渲染矩阵。旧rest/郊区/U院/首批north/第二批及1.0/0.9等镜头字段保持；D内存演示路线不延伸到新路。

## 数组源绑定与20项尺寸读回

visualReplacementOf的sourceIndices与sourcePolygonsMap按数组原样保持，每对象当前一元素；root sourceMappings、sourceIndices与多对多语义保存在派生包、Tiled JSON属性、scene的round3SourceMappings与新blocks/visualReplacements。没有旧单键读取失败后生成空源或假ID。sourceDataChanged=false，源polygon逐索引与原city相等；旧9个映射字段原样保持，不强改其历史schema。

候选sceneRole/landUseIntent及原stop接近关联是新设计，不冒称原source已存在楼—POI绑定。source-mapping-and-stop-semantics.json保留每模块源数组、原停靠节点/坐标、真实门、视觉路肩通路和原POI只读对象。本批关联4个原stop，新增POI/业务地址/导航边0；node/名称/经营类型/路线与city源SHA保持。

|sourceIndices|persistentId|canonical素材|单次比例|真实Cocos UI宽高|
|---|---|---|---:|---|
|191|009r3-src-0191|B01|1|253.959 × 318.096|
|640|009r3-src-0640|B06|0.9|429.436 × 415.976|
|115|009r3-src-0115|B05|0.9|293.209 × 335.565|
|646|009r3-src-0646|B06|0.9|429.436 × 415.976|
|390|009r3-src-0390|B01|1|253.959 × 318.096|
|194|009r3-src-0194|B05|0.9|293.209 × 335.565|
|593|009r3-src-0593|B05|0.9|293.209 × 335.565|
|610|009r3-src-0610|B01|1|253.959 × 318.096|
|263|009r3-src-0263|B06|0.9|429.436 × 415.976|
|612|009r3-src-0612|B01|1|253.959 × 318.096|
|600|009r3-src-0600|B05|0.9|293.209 × 335.565|
|562|009r3-src-0562|B02|0.9|381.931 × 457.313|
|438|009r3-src-0438|B06|0.9|429.436 × 415.976|
|557|009r3-src-0557|B05|1.1|358.366 × 410.134|
|487|009r3-src-0487|B01|1|253.959 × 318.096|
|486|009r3-src-0486|B05|0.9|293.209 × 335.565|
|463|009r3-src-0463|B06|0.9|429.436 × 415.976|
|485|009r3-src-0485|B05|0.9|293.209 × 335.565|
|515|009r3-src-0515|B01|1|253.959 × 318.096|
|484|009r3-src-0484|B06|0.9|429.436 × 415.976|

实际13件0.9、6件1.0、1件1.1；B01全为1。图框已含比例，Tiled使用该图框×16，导出器按canonical库计算一次比例，Cocos UI用实际图框×32，节点localScaleX/Y全部1。canonicalPPU、UV、原生PNG和原74实例尺寸不改。runtime-scale-and-frame-verification逐项读UI宽/高并核canonical比率；1.1 B05真实世界图框11.1989499163×12.8167026000，UI358.366397322×410.134483202，不是1.21。

94静态节点＋D/影子共96 items，实际位置和静态index/sibling顺序匹配导出，最大浮点差约0.000001340投影像素；旧74 UI尺寸也和旧manifest逐项相同。runtime-final.json使用columns明确的紧凑列表，来自__mapPreviewOrder、__mapUIDimensions、__mapFrameSharing和__mapTextureStats；一次大对象读回触工具JSON长度限制，已改紧凑读回并保留readback-oversize-error.json，错误未当作成功证据。

运行27张唯一PNG、2,127,723字节，全长边<=280，新增PNG字节0；nativeFrames25、当前局部canvasFrames2（地面＋D影子）。同file/源SHA共用image/Frame，0.9/1/1.1只改实例UI，不拷图或每实例新建Texture。源码/运行manifest没有整张原生母版、25图或全城分析快照。

## 真实74/164保护与逐项准入

actual74-body-protection-check.json与actual164-ground-protection-check.json核20楼和96面，使用当前实际74/164，而不是planning冻结69加第二批5/20。明确包含首批8件树灯/长椅/双桶真实接触轮廓、第二批实际补的9面。相邻第二批楼使用已准入的真实候选脚线，按当前运行anchor/尺寸核对，未把高楼sprite逆投影包围框误作相邻楼的实测地基；远处无更近地脚证据的旧物使用保守包络作排除，方法逐件记在actual-old-shape-evidence.json。

新楼最小间距：其他源楼2.084候选单位、当前旧物4.175、当前164地面/第二批9补面2.970、原水polygon7.462、原车道边2.115、新同批楼4.807。96面同样逐项不与其他源楼/原水/原车道/旧地面/原POI点相交；仅自己的sourceIndices载体豁免，没有删源障碍/全体净空豁免。源楼、通路、蓝边、原水、原节点持续作为硬障碍。

固定门像素按真实PPU及一次比例换算，entryMap一致；手估自身脚线处第一米中心线触碰最大约0.07单位，20件在门前0.6m处均已出候选脚线。已放大检查的近景门阶与通路相接，没有明显墙内穿行；隐藏地基、步高和可导航性未精密验收，不用该门槛容差放宽其他楼/路/水的保护。

96面具体为20条1.5m通路、17块可安全放置的原载体庭院、59种植边。住宅庭院使用受控#A5BB8C、种植边#9FB584，混合街铺/办公地面用既有S01-paving；不是新原生纹理。保留原用地/连接组织，不加统一大三角凸包、不造白盒补未画源楼；无额外树灯以凑数量。部分载体只放小楼与有限余地，面积比不代表等形重建，sourceMappings继续明确该限制。

## 范围、道路与有限地面预算

180m是source邻接连通阈值。20锚点包围跨度约282.85×753.71单位，最大锚点对距约760.47，不能说整片直径180m；中间未安排/未画源目标仍为空白。

旧30条/212节点保持，新45条完整源路与旧引用去重后共72条/485完整节点。节点顺序、宽度、方向、sourceNodeIds与源city逐值核对；投影保持。只增加视觉引用，原桥标记/原路数据不改，不造道路/捷径/POI。

局部区域按镜头只生成一块最长2048的canvas（真实东北2048×1817＝3,721,216像素）；有限关系概览只在选中时生成1536×1363＝2,093,568像素，含可见旧城区上下文，不常驻全县巨画布。RGBA8单色面理论分别约14.20/7.99MiB，若CPU canvas保留另有同量级，均非实测内存，不含GPU/浏览器开销。旧区region字段保持，旧r2-courts镜头只在自身既有bounds内补画新引用几何，以免相邻新楼没有地面；未移动或重缩旧对象。新窗口按与bounds相交的完整源几何引用绘制，原路最后覆盖、原节点不裁。

这是有限窗口呈现，不是全县无限拖动缓存完成；拖出bounds未自动补全地面。pipeline仍给64m tile引用索引（本批25个候选active tile）供后续接线；本轮未把25块同时常驻，也未宣称LRU/FPS/实际内存通过。94静态sprite/27图仍加载在本独立viewer，更多批扩量需继续按区域可见性接线。

## 保护SHA与执行记录

- 父原：`654ccb00f1f75af0f487c9d2d3f7e8f88b06258ca1f73542dcc950978c1a6a12`
- 派生：`15ddb741b3ddc98397a09c084f49b9ba63b07b0423775e80a6bd5ec407251f0b`
- 实际74基线scene：`4f6fbbaeb2b5a2969282a992d88e41324a89e786c7115d3fe644376a4aaa3354`
- 实际74基线Tiled：`da725fa794c7745ba2cf7f852a65a0b9fc07539dab8ee3123e78b7e3e13d075c`
- 当前scene：`51d53b3eebe803355770ddbd7f26fee5184f613d48f6a3e5efed9923fbcd8ebc`
- 当前Tiled：`d4a604151166c3c5c787ca79690e58f54067a09be485ca2ddb1988f8c0438d0e`
- 原city：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

605个只读文件SHA保持，含原生/工具实际来源、库校准、原city、005/007/008及先前两批证据；首批9360与第二批1ba原SHA不变。旧74/164全部字段、旧图层/tileset、旧镜头/D路/bounds/origin、旧manifest别名逐值保持。数据重导出TMJ/scene/manifest字节稳定，重复append拒绝。

实际执行：

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py prepare --batch-id expansion-009-round3 --index 4 --plan docs/art/2026-11-05-modular-map-kit/revision-009/planning/fit-round-3/third-expansion-batch.json --parent-sha 654ccb00f1f75af0f487c9d2d3f7e8f88b06258ca1f73542dcc950978c1a6a12
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/prepare_third_009.py
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/add_third_009.py
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood_export.py export
```

当前已有增量，prepare/append重复拒绝；后续保留手调使用export，不init。pipeline/applied-009-round3.json链接原准备包74基线与本实际显示证据。规划/原生未写，没有游戏tests/typecheck/回归/渲染矩阵/FPS、业务存档、提交、生图或服务启动/暴露。

剩余：大片未布置地面和未覆盖源楼仍存在，庭院生活细节仍少，部分门前通路较长；原生彩边/近景280软化和原路与原生族角差保留。本轮无新增树/车/道具，不把4楼型复用称新楼型生产。B09/B10/B11/T03/P09未新增，654+2387未加。实际运行画面已交，未用户、全县、导航或性能验收。
