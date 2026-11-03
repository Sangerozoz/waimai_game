# 县城蓝框：样板以外的完整场景数据

2026-11-03。依据[长期实施基准](../../product/implementation-baseline.md)、[三层分区](../2026-11-02-county-zoning/selection.json)、[布局及空白地块要求](../2026-11-02-county-production-layout/2026-11-03-layout-review.md)，把[380×440m样板](../2026-11-03-county-sample-production/README.md)的做法扩到整个蓝框。此包是实际产出的坐标数据与新规划图，尚未全县接入、游戏测试或用户视觉验收。

| 产物 | 内容 |
| --- | --- |
| [county-scene-layout.json](county-scene-layout.json) | 蓝框全域地块、原始几何、补景、样板及空间索引；兼容样板主要字段 |
| [全县地块图](01-county-scene-plan.png) | 3328×3290，新数据平面图；不是目标美术效果图 |
| [城区接续详图](02-urban-scene-detail.png) | 2133×3456，显示城区、样板及新增街坊关系 |
| [数量/面积摘要](layout-summary.json) | 全量与新增数量、地块用途、楼层、场地物件分类 |
| [来源与文件清单](production-manifest.json) | 原city与样板SHA、脚本/JSON/PNG的SHA与尺寸 |
| [可复现脚本](build-county-layout.py) | Python 3＋Pillow；离线执行，只写本目录 |
| [边界生产排除清单](production-exclusions.json) | 10栋跨蓝框源建筑不生产；146条含蓝框外点的原路仅供裁切/收口参考 |
| [数据完整性记录](integrity-report.json) | 原件SHA、样板子集逐值一致、原始几何、覆盖/空间ID/内容核对 |

## 范围与真实数量

蓝框X **−2652.59..−361.42**，Y **−1282.79..867.46**米，严格采用已有近似边界。绿框X−1947.26..−940.64、Y−926.24..661.93为繁华城区。新增建筑按自身中心区分3–6层城区与1–3层郊区；地块跨绿框时属密度过渡，不添加玩法门槛。原样板楼高建议原样保留。

| 类别 | 原样板原样复用 | 本次新增 | 本包合计 |
| --- | ---: | ---: | ---: |
| 场景分区 | 117 | 2298 | 2415 |
| 非交互补景建筑 | 16 | 1186 | 1202 |
| 场地实物/步道 | 145 | 6159 | 6304 |
| 地面树 | 96 | 530 | 626 |

新增地块约**2,775,691.30m²**，来自695,510个2m装饰栅格单元，蓝框边缘单元按原0.01m边界裁切。另有道路/水系/原建筑/合法入口及保守退让区，样板范围不重造。所有2298个新增地块均有实物内容；没有仅名称/换底色的无内容分区。1103块小型庭院/边角花园合计约9.73万m²，许多为道路、建筑之间的细小余地，不能解读成1103个大公园。

新增用途：住宅731块、沿街商住256块、公园104块、完整校园17块、水岸绿带84块、庭院/边角花园1103块、活动前场3块。完整校园均有校舍及运动场；另有一块狭长公园保留活动场而不虚称校园。新增场地为1420段装饰步道、2371处花床/地被、2350处座椅、18个运动场；与建筑、少量树组合形成完整场景。植物克制、均为地面，不在屋顶种树。图中受控的暖灰、米色和绿色只表示结构，不替代已认可厚涂画风或增加蓝色。

原几何在本包中为1018处建筑、1071条原道路、17个水面多边形、35条水道；只收录与蓝框或24m显示保护圈相关的原件，不复制12km整张原始地图。其中**1008栋源建筑整栋在蓝框内可生产，10栋跨界源建筑保留原足迹但标`excludedFromProduction`，生产时必须整栋跳过**，不能裁成半栋、挪位或扩框。新规划图已跳过这10栋。道路可按蓝框显示裁切，路由收口另行处理。146条原路含蓝框外点，清单包含24m显示缓冲内/跨界相关原件，不等于历史按穿界线段统计的98条或79组，不将此数量冒充已修复边界。14个入口仅为**原始POI参考**，不等于运行时动态经营目录，不限正式产品地址数量，也未据此产生新订单。

## 样板的复用与精度

- `sampleOverlay`保存样板路径、SHA、范围。`parcels/addedBuildings/sceneFeatures/trees`四数组的前117/16/145/96项与样板**逐值一致**，包含原ID、几何、无ID的原场地物件；不往原样板对象补字段。重叠的原建筑也优先保留样板建议高度等元数据。
- 新分区只从样板矩形外提取；道路、水系、原建筑、原入口之外的自由空间按稳定100m世界分片切分，再按4邻接分区。边界近似2m，仅用于装饰；原道路节点、方向、速度、浮点points、原建筑足迹、水系数组原值保留。
- 装饰避让：原道路宽度＋5m，再加一圈2m栅格保护；线状水道按20m保护宽度，再加2m；原建筑和原入口同样保护。新建筑额外预留一圈2m放置间距。不是施工测绘或运行时碰撞模型。
- `rings`保留多环/内孔，按**evenodd**填充；不能逐环实心填色而把洞涂掉。新地块用`groundMaterial`提示地面材质与边界组合，原样板无此字段时按已有`landUse`回退。
- 小碎片可能只容得下不足2m的地被/卵石花床；这是实体配景，不冒充可步行公园或可经营地址。较大地块含分散摆放的建筑、路径和小物。场地步道不接入原寻路图。
- 新普通建筑按最近原道路方向以15度装饰模块对齐；该角度不量化原路网。建筑模块外观/高度是制作配置，未伪称原始测绘。

## 接入字段与空间裁切

保留样板字段：`version/date/status/source/sourceSHA256/bounds/coordinateUnit/parcels/addedBuildings/sceneFeatures/trees/sourceBuildings/sourceRoads/sourceWaterPolygons/sourceWaterways/entrances/constraints`。新增`zones/sampleOverlay/featureSchema/tileIndex/productionExclusions`。

| 字段 | 新增内容与读取要求 |
| --- | --- |
| `parcels` | 新ID`CP-*`；含`groundMaterial/zone/tileId/ringFillRule/contentCounts`。不将它们当POI目录 |
| `addedBuildings` | 新ID`CADD-*`；含原坐标`footprint/heightMetres/floorCount/module/orientationRadians/zone`；全部非交互 |
| `sceneFeatures` | 新ID`CF-*`；沿样板使用`pedestrian-path`的`points/widthMetres`，其余`bounds`。`microPatch/material`可选 |
| `trees` | 新ID`CTREE-*`；继续使用`groundAnchor/crownDiameterMetres/heightMetres` |
| `tileIndex.objects` | 12702个唯一对象索引，`key/collection/index/ownerTile/overlapTiles/bounds/excludedFromProduction`；生产必须跳过排除对象。对象正文仅在对应主数组存在一次 |
| `tileIndex.tiles` | 623个分片（含原件越界显示缓冲）；键为`floor(x/100):floor(y/100)`，值是按collection分组的对象key列表 |

视口先查询覆盖的100m分片，合并并去重对象key，跳过`excludedFromProduction`，再通过`collection/index`取正文。斜俯视建筑高度、树冠和阴影需要扩查询边距；精确边距由开发沿现有镜头决定。原几何的保守AABB可能命中多块，仍需裁切，不应每帧重新遍历全部约1.27万对象。`ownerTile`仅唯一归属，不是只在归属块显示。无ID的145个样板场地物件在索引中用`SF-00000`等原数组位置键，原对象不改。

稳定性范围是**当前冻结来源＋脚本版本**；未来改源或分区规则可能改变派生分区序号，不宣称跨任意源版本ID恒定。索引是接口数据，性能尚未在引擎验证。

## 复现、核对与限制

在项目根目录执行：

```sh
python3 docs/art/2026-11-03-county-expansion/build-county-layout.py
```

脚本在生成前拒绝SHA不是`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`的city原件。新数据环面积与裁切后的自由单元面积对照；样板四数组逐值、原建筑足迹、原道路字段和浮点points、唯一对象key、每新增地块实体内容、完整校园、补景越界与原保护区避让都有离线数据记录。此处只核对来源与数据完整性，**没有运行游戏测试、typecheck、回归、浏览器、Cocos或存档操作**。

本轮没有修改原地图、已认可图、样板包、业务代码、经济/取送规则或任何存档；没有新增道路节点/经营POI，也没有处理蓝框边界收口或动态地址重筛。红蓝之间背景本包没有重做，也不经营。两张图是新数据图，不能代替全县引擎画面、材质拼接、遮挡、小屏显示、路线上屏与性能的后续验证。用户未说“阶段完成”，阶段集中游戏测试继续保留。
