# 地图载具顶视图接入

**后续尺寸调整（2026-10-28）：** 用户要求再放大1倍，当前地图载具已从40×64改为80×128设计像素，宽高各2倍。更新全部营业点在各缩放/高度下的旋转包围范围检查为76像素半径；79项地图检查、类型检查、Cocos构建通过，构建脚本已核对80×128实际尺寸。[检查](map-vehicle-art/size-2x-tests.log)、[构建](map-vehicle-art/size-2x-build.log)。下文保留初次接入记录。

2026-10-28。用户要求先把各等级载具的顶视图用于地图，页面侧视图后续处理。

已完成地图接入：D使用旧电动车，D+使用翻新电动车。C/C+/B/B+/A/S/SS/SSS按既有素材顺序配置映射，当前县城仍只开放D、D+。10张透明原图逐字节复制到工程resources，原文件保留；[来源与SHA](map-vehicle-art/assets.json)。

CityMap将原骑手图标替换为40×64设计像素的等比例图片，显示尺寸不随地图缩放变化。顶视原图朝上，子节点旋转−90度，将车头与道路0度向东的角度对齐，再由骑手父节点跟随道路转向。图片加载期间或失败时保留原图标。

MapSample首次进入、存档恢复、布局重建和升级时传入当前车辆档位。MapVehicle按需加载、缓存贴图，防止旧异步回调覆盖新车型，并跳过销毁节点；失败可重试。未更改经济数值、存档结构或配送路线。

验证结果：

- 新增5项聚焦检查：10级素材映射/原图SHA、四方向车头、升级异步竞态、布局重建复用及失效节点、加载失败回退与重试；并扩展实际MapSample布局回归，核对重建时使用玩家已拥有的D+。
- 修前失败记录：[资源/加载器](map-vehicle-art/red.log)、[玩家车辆接线](map-vehicle-art/integration-red.log)。
- `npm test`共113项通过（27旧域＋64地图/经营/展示＋18存储＋4数据）；[完整日志](map-vehicle-art/tests.log)。
- `npm run typecheck`与Cocos Web Mobile构建退出0：[类型日志](map-vehicle-art/typecheck.log)、[构建日志](map-vehicle-art/build.log)。
- 构建资源表确认10条顶视图`/texture`路径均为cc.Texture2D，主脚本包含MapVehicle加载器；[构建清单](map-vehicle-art/build-manifest.json)。

未进行页面自动操作。用户刷新[当前游戏](http://localhost:4181/)查看现有车图，送一单观察转向；资金达到200元时升级D+，确认即时换成翻新电动车，刷新后仍保留对应车型。侧视图本次未接入页面。
