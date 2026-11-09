# 008郊区核心：实际接入同一006地图

2026-11-06。已运行现有导出器并真正打开Cocos，全部13个核心实例已显示；原43实例/85地面不动，当前**56静态实例、102地面**。未新建008引擎、未init重置、未改原city/005/007/008 planning-calibration；未生图/游戏tests/typecheck/回归/存档/业务/提交。

## 入口与实际画面

主入口仍 http://127.0.0.1:4186/revision-006/viewer/ ，旧默认近景及N1/N2/S1/rest镜头保持。新增：

- 郊区整体：http://127.0.0.1:4186/revision-006/viewer/?view=suburb — [真实截图](cocos-008-overall.jpg)
- 住宅菜园：http://127.0.0.1:4186/revision-006/viewer/?view=garden — [真实近景](cocos-008-garden.jpg)
- 市场后勤：http://127.0.0.1:4186/revision-006/viewer/?view=market — [真实近景](cocos-008-market.jpg)
- B06门槛 `?view=door-b06` — [放大实拍](cocos-008-door-b06.jpg)
- B08门槛 `?view=door-market` — [放大实拍](cocos-008-door-market.jpg)
- [接入后旧休憩角回看实拍](cocos-008-protected-rest.jpg)，确认未被第二块地面盖住。原截图未覆盖。

全部为本Cocos真实运行截图，不是规划图/原生图。门槛放大图可见280运行图的软化，不冒称高清母版。

## 可见增量与门槛

新增B05住宅、B06住宅、B08市场各1；P08菜畦3、P06/P07独立短段各1、T02树4、V02-v2静态后勤车1。核心全13项保留，没有因有限门槛误差误剔整栋。

蓝内绿外58×40候选地块的草地基底、有限菜园土面、门前/侧院1.5m步行面、市场后勤铺地全部17面已导出，未只放房子留孤岛。草地/土面使用受控颜色，铺装和路面使用已有纹理，没有新贴图/POI/可行车捷径/导航边。T02是同族变体，三P08是重复同图，不宣称新增三种菜畦或树种。

B05/B06/B08分别使用真实entryPixel `[810,1070]`、`[730,1038]`、`[820,803]`，各自按原PPU和anchor换算，和固定规划门位差均小于1e-8，未把B05注记当另外两栋门点。父仅允许B06/B08与**本栋人工地脚**约0.124/0.192m接触；放大实看铺地接到可见台阶，没有明显大面积穿墙/墙内路线。本轮未挪新增楼、未改门像素/新步行面，也未把例外扩到源楼/其他楼/水/车道。证据：008-door-threshold-evidence.json。

住宅/菜园/市场后勤实拍未见明显压菜畦、通路或车位；这不是精密地基/导航/用户验收。市场暖色玻璃、T02视角和P07短段姿态保留为候选差异，不自动生图。P06/P07条数和原短跨度仍不同，未镜像/旋转/非等比或拉长凑闭环。

V02保留原候选5.8×2.05车身及世界图框，候选body polygon逐点在原8×4车位内；anchorMap按**近侧轮中点**直接接入，没有误作车身中心二次偏移或缩车。仅静态后勤比较，无交通AI/配送/商城。D骑手内存演示仍原蓝内路径。P02/P09/B07/B09/B10/B11均未加入，不等待在写B07扩展。

## 分离地面画布

两区相隔约879m，世界坐标、尺度、旧镜头保持；没有将旧场景缩小或跨空白烘成县图。真实__mapGroundStats：

|区域|独立有限画布|地面|绘制原路引用|
|---|---|---|---|
|legacy006|3072×2725|原85面|原3条|
|suburb008|3072×2725|新17面|规划23条，绘制按bounds裁切|

旧画布保持原bounds、原3路、旧地面和材质，新增路径引用不在旧区重画。两块地面先于所有sprite；SiblingIndex起始偏移按地面数处理，避免第二块地面盖楼。实际旧休憩角回看已确认正常。

场景JSON去重为**25条完整原道路、178原节点**。节点顺序/坐标/宽度/方向/sourceNodeIds全部逐值核对原city；仅绘制做视图裁切，不裁改JSON节点，不添加连通捷径。默认与旧overall镜头未变成跨879m远景。

## 可编辑地图与来源

地图：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`，在原TMJ追加008 group及地面/静态index子层。组offset/可见性/正等比/顺序可编辑，拒绝平面旋转/镜像/非等比。地图头改为无限对象地图以容纳远处负编辑坐标，原对象字段逐字保持。add_suburb_core.py拒绝重复增量；后续只用neighborhood_export.py export，不init。

固定父输入：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-008/planning/next-district-plan.json`

父原SHA：`a5412d65a4a9149051f98f43026b8d9e00d4b2e111d3c9366b998a2e4f230758`。

派生008-runtime-subset-plan.json SHA：`0e4f9bb89fa92f6e61b1d2e2c444a1abb71699a8cf155fdee53b2edf31744ef6`。

父快照、派生规则分别记录在008-parent-plan-snapshot.json、008-runtime-subset-plan.json、suburb-increment.json，未把派生SHA冒充父原SHA。pre-008-neighborhood.tmj/scene/asset-manifest/export-report保留接入前基线。

原43对象位置、原图SHA、worldSizeUnits、anchorUV、相对顺序及85面、旧cameraViews、D路径逐项相同。本次必需只读源**394项SHA保持**。宽范围保护采样中旁路b07-extension有4个非核心文件被规划会话并发更新；已单列，未读入/接入其方案，不伪称整个planning目录冻结。证据在suburb-source-protection-before/result.json。

## 运行读回与资源

56静态＋D骑手＋程序阴影＝58节点；editorOrder与导出一致。最大坐标差1.29e-06引擎单位，核对容差1e-4（投影常数舍入）。runtime-008-readback.json包含真实节点/地面/纹理与Frame共享读回。

__mapTextureStats：uniqueAssetImages=26、nativeFramesCreated=24、canvasFramesCreated=3（两地面＋骑手阴影）。__mapFrameSharing中008-bed-0/1/2均为frameIndex18，共用P08-runtime-280.png同一个SpriteFrame。按file+SHA共享解码image，未每实例新建Texture。

最终**26张唯一PNG全部长边≤280，共2,036,271 bytes**；viewer55文件、5,735,710 bytes（含Cocos）。只包引用派生图，无原生/25图/source-context全城快照，候选库不等同运行包。

已完成本核心真实显示与静态/像素换算/节点Frame核对，未用户验收、未阶段游戏测试、未全县完成；没有启动/杀服务、暴露端口或远程探测。
