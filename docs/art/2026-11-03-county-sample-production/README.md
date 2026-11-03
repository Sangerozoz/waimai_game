# 县城首块样板：场景制作与工程输入

2026-11-03。按用户“没有需其确认/决策的事项就持续推进”的授权执行[样板落地计划](../../superpowers/plans/2026-11-03-county-sample-production.md)。PM制作场景数据和美术样板，固定开发并行实现独立样板浏览入口。

## 已实际产出

| 文件 | 用途与状态 |
| --- | --- |
| [地块内容安排](01-parcel-layout.png) | 原380×440m样板内校园/运动场、住宅庭院、商住、公园与河岸绿地的安排；2160×1980 |
| [斜俯视结构底稿](02-structure-reference.png) | 按原几何投影定位建筑、道路、河道、桥梁；2048×2048，纯色结构不代表目标美术 |
| [美术样板v1](03-art-sample-v1.png) | 内置imagegen实际输出1254×1254，PM已查看；尚非用户视觉验收或游戏截图 |
| [工程输入JSON](sample-scene-layout.json) | 117个含细碎边角的场景分区，16栋新增非交互建筑、96株地面树、145项场地内容；原坐标，原地图未改 |
| [摘要](layout-summary.json)、[结构图投影](projection.json) | 地块用途/数量和结构图公式，不冒充引擎摄像机已验证 |
| [完整提示词](03-sample-art-prompt.txt)、[来源与SHA](art-manifest.json) | 几何底稿为编辑目标、认可首页为画风参考；原始输出及项目副本保留 |
| [HF01墙窗材质](HF01-wall-windows.png)、[规格与SHA](HF01-manifest.json)、[提示词](HF01-wall-windows-prompt.txt) | 原生1254×1254 RGB，正面2层×2窗，上部立面候选；物理重复单元建议8×6m，投影/裁切由原建筑几何决定，接缝/重复/引擎未验证 |
| [HT01完整地面树](HT01-ground-tree-v1.png)、[规格与SHA](HT01-manifest.json)、[提示词](HT01-ground-tree-prompt.txt) | 原生1254×1254 RGBA，含树干/根部，固定斜俯视配景候选；地面锚点与内容框已有记录，不把旧正顶视树冠当整树 |
| [本轮PM产出文件清单](production-manifest.json) | 原图/材质/输入文件尺寸、SHA与静态盘点；方向素材另见逐张manifest |
| [初始D车＋主角八方向](rider-directions/README.md)、[逐张manifest](rider-directions/manifest.json) | 八张独立RGBA原件已齐；全橙圆灯身份、原生尺寸/alpha/主体框/前后轮接地候选已记录。独立生成存在小机械差异，锚点未引擎验证；已交开发接入 |

117个分区不是117个经营地点或玩法系统。原建筑按相交范围带入，口径不同于上一轮按中心数出的113处，不改旧库存统计。原数据没有建筑的地块已安排用途，用少量模块和完整场地组合。

## 工程字段与精度

| 字段 | 内容 |
| --- | --- |
| `bounds` | X −1720..−1340，Y −240..200，地面米 |
| `parcels` | `id/landUse/name/groundColor/center/rings/areaSquareMetresApprox`；`rings`含外环及内孔，须正确处理洞 |
| `addedBuildings` | `id/parcelId/footprint/heightMetres/module`；新增非交互场景，不新增经营地址 |
| `sceneFeatures` | `pedestrian-path`用`points/widthMetres`；`sports-court/garden-bed/bench`用`bounds`（左上、右下两个地面点） |
| `trees` | `groundAnchor/crownDiameterMetres/heightMetres`；仅地面种植 |
| `sourceBuildings` | 原图相交建筑`sourceIndex/footprint`和建议层高；层高不是实测数据 |
| `sourceRoads` | 原ID/nodes/浮点points/width/direction等；数组未截边，绘制裁切，寻路保原连接 |
| `sourceWaterPolygons/sourceWaterways` | 原水域/水道几何，线状水道20m仅为本次保守装饰避让宽度 |
| `entrances` | 原节点：榕树街食堂1623821046、晴川广场9657208284 |

地块边界由道路、水系、原建筑和入口保护区外的1m栅格提取，仅适用于装饰分区。原路段和建筑保持原浮点几何。场地步道不加入寻路；地块内孔不能涂成草地覆盖道路/建筑。

美术样板指导外观，不能作为整张背景硬贴，也不能从生成图反推路网。生成图不保证每条边逐像素对齐；工程按数据固定位置，用立面、材质、地面和小物重建画面，不能改道路迁就图片。

## 正在推进

固定开发已产出独立HTML/JS坐标浏览入口，接入地面/屋顶/墙窗/完整树、触屏、八向D车和运动场/花坛/座椅细节；正式游戏同源只读桥接已实现并完成必要构建（包装退出0、Cocos日志Finished，子进程SIGTERM等诊断保留）。首次启动Abort trap失败是历史，原日志保留。当前已继续[蓝框城区/郊区扩展](../../superpowers/plans/2026-11-03-county-expansion.md)，首块样板保留不重造。实施见[开发报告](../../reviews/county-sample-20261103/implementation-report.md)。桥接不复制订单或移动真实存档，工程画风目标尚未全部达成或用户验收，所有新改动未游戏测试。

本地交付服务已启动：127.0.0.1:4181，根目录`delivery-game/build/map-sample`，仅确认进程监听，没有打开或请求页面。独立样板路径`/county-sample/`；正式游戏`/?countySample=live`显式开启可关闭的实时只读样板浮层。实际交互/显示效果仍待阶段测试与用户体验。

PM继续配套场景与素材，开发继续落地和补外观，无产品方向决策事项就执行下一项。用户仍未说“阶段完成”，不运行游戏测试/typecheck/回归/渲染矩阵，不操作用户存档或发布；既有首页与旧dirty/untracked保留。

依据：[长期实施基准](../../product/implementation-baseline.md)、[认可首页](../2026-11-02-approved-ui-reference/00-home-v2.png)、[布局确认](../2026-11-02-county-production-layout/2026-11-03-layout-review.md)。
