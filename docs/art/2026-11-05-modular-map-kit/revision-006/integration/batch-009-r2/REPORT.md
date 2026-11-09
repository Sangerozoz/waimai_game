# 009第二批5源址：实际Cocos接入与单次0.9验证

同一入口 http://127.0.0.1:4186/revision-006/viewer/?view=r2-courts ，旧N1/N2/S1/rest/suburb/U院/首批north镜头保留。继续使用既有4186服务，没有新建引擎、启动/暴露服务。

已实际显示5唯一源602/609/599/418/223：B06两栋、B01两栋、B05一栋，0楼拒绝；新增20规划地面＋9小范围地面（4庭院草地、5门前小铺地），无新场地物件。当前74静态实例/164地面。1处可选599矩形草坪因邻源楼净距不足0.5m未加，其楼/原通路/原三绿边保留；没有把楼缩小掩盖冲突。五个源址不是五个完整街区，未覆盖源楼/空白场地仍待后续。

## 实际截图与路径

- [602/609/599关系整体](cocos-round2-courts-overall.jpg)：3栋与两条原路的实际位置，尚有未布置地面。
- [602/599两住宅门前近景](cocos-round2-two-homes-close.jpg)：两张原生门阶、0.9楼体及1.5m步行面与路肩关系。
- [609小楼门前](cocos-round2-source609-door.jpg)、[418北铺](cocos-round2-source418-shop.jpg)、[223南宅](cocos-round2-source223-home.jpg)：补齐另外三源的放大实际画面。
- [原1.0与新0.9的真实Cocos等比例双视口](cocos-real-map-equal-scale-1_0-vs-0_9.jpg)，可运行入口 http://127.0.0.1:4186/revision-006/viewer/scale-compare.html 。两个iframe均运行同一个006 viewer，楼在各自真实原址；左右视口均639×552、22单位镜头、实际初始zoom1.818181818，不搬旧楼、不合成截图。此诊断页有两个独立WebGL上下文，资源/Frame读回各属自身viewer；正常地图仍是单viewer，不能用此页推算游戏内存性能。
- 可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。本批只增一个group，原69对象/135面和所有已有group offset、可见性、层/index字段保持。
- 派生计划：009r2-derived-plan.json；来源/真实门/尺度：native-scale-entry-check.json；原停靠点层次：stop-door-association.json；实际节点/Frame/UI：runtime-final.json、runtime-scale-once-verification.json、runtime-scale-compare.json；最终保护：final-verification.json。

镜头参数：`r2-courts`（三源关系）、`r2-homes`（双住宅）、`r2-shop609`、`r2-north-shop`、`r2-south-home`；双视口各用`r2-scale-original`和`r2-scale-new`。旧镜头参数/相机/缩放中心逻辑不改。

## 0.9只应用一次：真实UI尺寸

方案为“已缩图框＋运行节点localScale1”：先核plan.worldSizeUnits == canonical库图框 × uniformScale，再把plan图框直接写成Tiled width/height×16；现有导出器从canonical库读出0.9，manifest写实际world frame；Cocos按该frame×32设UI。没有第二处再乘0.9，没有改canonical PPU/anchorUV/原生PNG。canonical按asset-library/asset-calibration中的B06/B05读取，运行instance-*别名仅指实例。

|源址/实例|素材|单次比例|实际世界图框|实际UI单位|候选/源载体面积比|
|---|---|---:|---|---|---:|
|602 / 009r2-src-0602|B06|0.9|13.419888 × 12.999245|429.436423 × 415.975827|0.847704|
|609 / 009r2-src-0609|B01|1|7.936234 × 9.940515|253.959490 × 318.096485|0.422470|
|599 / 009r2-src-0599|B06|0.9|13.419888 × 12.999245|429.436423 × 415.975827|0.437786|
|418 / 009r2-src-0418|B01|1|7.936234 × 9.940515|253.959490 × 318.096485|0.435203|
|223 / 009r2-src-0223|B05|0.9|9.162777 × 10.486393|293.208871 × 335.564577|0.452788|

原1.0 B06实际UI477.151581×462.195364、世界14.910987×14.443605；新B06实际429.436423×415.975827、世界13.419888×12.999245，宽/高比均0.9。B05宽高相对canonical也均0.9；B01均1。读回节点自身scaleX/scaleY全部1。不是仅核X/Y：runtime-scale-once-verification逐项核UI width/height、world frame、node local scale与Frame。原旧69 UI图框/资源别名也和当前基线逐项相同。

运行包仍27张唯一PNG、2,127,723字节，全部长边<=280，新增PNG文件/字节0。真实__mapTextureStats为27 uniqueAssetImages /25 nativeFrames/2 canvasFrames（当前单新区域地面＋D影子）。B06四个实例（旧1.0两件、新0.9两件）共享Frame17；B05/B01及全部重复file也各共享同一个Frame，0.9没有拷贝PNG/另建Texture。原生B06/B05和既有B01均核真实tool源SHA；库PPU/UV/所有原69尺寸保持。

## 原停靠点与真实门分层

这是**新设计接近关联**，不证明原源楼本来绑定某POI。city.buildings仍是独立polygon数组，原POI/node/名称/经营类型/路线数据SHA不变。五个新显示源址关联3个原stop；新增业务地址0、POI0、导航边0。

|源址|关联原stop|原node对应名称/类型（仅只读证据）|
|---|---|---|
|602 /609 /599|6438106307|桥边咖啡 /restaurant（共用同一原点，不复制为3个POI，不给三栋改名）|
|418|3387477852|文昌春和里·10栋 /office|
|223|1623821215|河畔小馆 /restaurant|

实际entryPixel固定：B06[730,1038]、B01[973,965]、B05[810,1070]，从真实PPU按0.9/1换算entryMap，与规划逐值对应；图中门不移动去压原node。visualApproach止于既有源路肩；原stop仍在原坐标、独立于门点和装饰步行面。stop-door-association保留每件源polygon、真实门、原stop坐标、原POI只读对象、视觉路肩终点。Tiled与runtime blocks也保留sourceIndex/visualReplacementOf/sourcePolygon/sourceSHA/sourceNativeSHA、原stop关联字段。

五源原polygon仅作为各自载体豁免；其他源楼仍为障碍。此sprite viewer原本未画原source polygon占位，因此0删除/抑制占位；未搭一层再删，也未修改原city楼数据。面积比见上表，均为候选楼＋有限余地，未宣称整形重建源楼或已获知其原用途。

## 实际69保护与有限场地

准备器第三索引批`expansion-009-round2`从真实69/135读取baseline，不使用plan中冻结57字段重放；pre-r2-scene/TMJ/manifest是本轮69的字节快照。geometry-protection-check、ground-protection-check、每个额外面staticCheck逐件核当前全部69保守sprite包络、135实际地面；另显式核首批8件真实树/灯/长椅/双桶接触轮廓与4块forecourt-base。新楼距该首批8物最小231.586m、距4补面最小225.475m；所有新增29面也通过相同旧物/旧地面筛查。保守sprite包络仅用于排除相交，不称旧楼实测地基。

新楼与其他源楼最小2.074m，原车道最小2.088m（步道按原批准肩侧相接），真实waterAreas最小46.576m；34个新楼/地面轮廓不盖原POI节点，最小节点间距52.470m。新29面与别的新楼最小8.244m，未以“本栋台阶误差”豁免别人楼/源路/原node。

静态人工脚线处门前中心线短触碰：B06两件约0.07m，B01两件约0.05m，B05无该中心线触碰；距门0.6m处都在候选脚线外。真实放大画面中所选门阶接到小门前铺装/1.5m通路，没有看到明显墙内穿行。隐藏地脚、台阶高差和导航仍未认证，不把人工控制点误差推广为统一净空放宽。

本次没有大三角铺地凸包：草地只在批准三边种植带/候选脚线形成的有限住宅或街铺小庭院内，小铺地每块约2.4×1.2m，与原1.5m步行面相接。599可选草坪原矩形最近邻源楼0.067m，缩进0.25m仍不足独立的0.5m额外面筛选值，因此不加入；既定20面不因此改动，详见派生rejected。没有为了填满额外挤入小物。

新增地面分三处有限区域（r2-courts/r2-north-shop/r2-south-home），按相应镜头只挂当前区域，最长边上限2048；当前住宅组真实读回2048×1817、17面/2源路。没有把三处分散地块烘成跨县巨图，也没有把它们连成新路。原首批north和旧各区数据/镜头保留。正常页面目前仍加载74静态sprite/27引用PNG，不能据此声称全县大量地块常驻可行；009/pipeline tile/cache准备仍是后续扩量接口，没有跑FPS或内存基准。

原路当前30条、212完整节点；旧26条/190节点字段保持，新4条全部节点顺序/宽度/方向/sourceNodeIds及原投影核源city。733760357-0的bridge=true是原数据，未新增桥。绘制裁区域bounds，存储不裁节点，不增加导航边。

## SHA、真实执行与剩余项

- 父原SHA：`1ba66318371ce8e9ff1ec905335a302d5070f28522a2130f295dc3c9decd92f1`
- 本派生SHA：`fcb42d40f55af19be0506cdfd89783cf6040324c2f9d31ca391874dab20c14fe`
- 实际69基线scene：`47248fdccddb32b95cb34bace541b67bcee7147590198eecb34603016eaa826f`
- 实际69基线Tiled：`d312b8c8906bc0cd26befde34f318a74f14fd1bfeb738776be912de74ea7b716`
- 当前scene：`4f6fbbaeb2b5a2969282a992d88e41324a89e786c7115d3fe644376a4aaa3354`
- 当前Tiled：`da725fa794c7745ba2cf7f852a65a0b9fc07539dab8ee3123e78b7e3e13d075c`
- 原city：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

572个只读输入/已有资产/首批报告截图SHA未变；旧69全部字段、135面、旧层/tileset、旧镜头、D内存路、bounds、origin和旧manifest实例字段保持。实际readback 74静态＋D/影子共76项，位置最大浮点差约0.000001340投影像素；UI尺寸和静态index/sibling次序匹配导出。数据重导出TMJ/scene/manifest字节稳定，重复append拒绝。旧证据不覆盖，六张本批实际截图另存本目录。

实际执行：

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-009/pipeline/batch_prepare.py prepare --batch-id expansion-009-round2 --index 3 --plan docs/art/2026-11-05-modular-map-kit/revision-009/planning/fit-round-2/second-expansion-batch.json --parent-sha 1ba66318371ce8e9ff1ec905335a302d5070f28522a2130f295dc3c9decd92f1
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/prepare_second_009.py
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/add_second_009.py
python3 -B docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood_export.py export
```

当前已有增量，前三命令重复会拒绝，不init；后续保留手调使用export。pipeline/staging/expansion-009-round2的原始准备差分保留69基线与5/20数据证据，pipeline/applied-009-round2.json链接真正接入的5/29、实际尺寸/截图读回。

限制：三组间/楼间空白仍未完成生活细节和所有源目标，未称五完整街区或全县完成；路向与原生边存在可见角差（原路实向保持，图未旋转）；B05底边彩边/280放大软化等原生残差保留；门与stop分层只是设计关联与视觉候选，未认证可导航/业务。B09/B10/B11/T03/P09未新增，无新增车辆/AI。没有生图、游戏tests/typecheck/回归/渲染矩阵/FPS、存档业务或提交，没有服务变更。实际画面已显示，用户/导航/全县/性能验收仍待后续。
