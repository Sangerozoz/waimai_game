# 车辆商城与骑手配车实施记录

状态：已实现并生成试玩构建；未测试，待阶段集中测试和用户体验验收。未操作用户页面或存档。

## 实际产出

- 车辆商城采用独立车库背景、放大车辆预览、属性及购买按钮、车型收藏滚动区。全部车型和已拥有均按车型聚合；选择车型只影响预览。现有订单、余额、档位开放、数量上限与确认逻辑沿用原 `OrderBook` 和 `act` 保存处理，购买不会自动配车。
- 底栏“骑手”和头像指向同一个骑手入口；主角为当前已有玩家，骑手页按车辆实例编号配置并显示当前配置。原车 D 升 D+ ¥200 位于骑手现用车辆详情；商城 D/D+ 副本价格沿用 ¥500/¥700。原有活动单冻结、载重约束及保存失败处理沿用既有逻辑。没有添加 NPC、招募、收益或存档 schema。
- D 的侧45资源是 `delivery-game/assets/resources/map-sample/anime/au02/vehicle-d-three-quarter-original.png`，D+ 是 `delivery-game/assets/resources/map-sample/anime/vehicles-20261031/V01-d-plus-45.png`；不使用概念稿抠车。其余八档沿用各自原件。
- 展示元素使用现有按压反馈；车型切换重建预览，旧异步回调通过节点存活检查避免覆盖新页面。窄屏仍按安全区和原布局函数分配，效果未渲染验证。

## 资源来源与 SHA256

四张源图来自 `docs/art/vehicle-shop-production/`，原图未改，复制到 `delivery-game/assets/resources/map-sample/anime/vehicle-shop-20261101/`，背景按比例 cover；三个透明皮肤按主体边界裁帧、九宫格缩放。

| 源文件 | SHA256 |
| --- | --- |
| garage-clean-background.png | `5859bc695354277505d15c1af22b647d6aabd09d2152aa94a6a2a42504d00021` |
| metal-panel.png | `e4d2b5230997dbd83a41c4ec271cfeeae1b599cf4a0bdf88e1b9a8b7f82608cd` |
| card-frame.png | `0c88ee85ac681938cd382645371970b499aeb8527db76bd7055ac2980af9dc7d` |
| primary-amber-button.png | `9396f820fda6807dd14805f17f87a7e3c42d1dfea140309585d5100140a2986d` |

## 构建和未验证项

- `npm run build:map --prefix delivery-game` 包装命令退出0，Cocos日志显示 Finished；原始 `build.log` 包含 `build-script` 子进程 SIGTERM 和 asset-db `trackTimeEnd failed` 诊断，包装成功不能证明所有子进程均无异常。
- 现有 4181 服务 PID 59869 指向 `delivery-game/build/map-sample`，HTTP 根路径返回200。此为静态交付信息，不是玩法或显示验证。
- 未运行测试、类型检查、回归或渲染复验；购买、配车、保存失败、活动单冻结、不同屏幕及九宫格效果均待用户明确“阶段完成”后的集中测试。用户审美及体验未代验收。

## 01:14 场景及编号调整

- 车库背景改为位于独立顶部场景节点，范围从屏幕顶端到车型信息条下缘，仍等比 cover；收藏区使用独立面板。实际构图和落地感未渲染验证。
- 骑手页当前配置显示与列表一致的可读两位起始编号，内部 ID 不再用于该文字；删除 D+ 早期共用 D 图的别名，保留原有独立 D+ 母版映射。
- 重建命令 `npm run build:map --prefix delivery-game` 退出0，日志显示 Finished；原始 `build-scene-adjustment.log` 保留 build-script 子进程 SIGTERM 和 asset-db trackTimeEnd 诊断。未运行测试、类型检查或渲染复验，未操作游戏和存档。
