# ORDER-EXPERIENCE diagnosis

基线 47 份 before/SHA 已保存。直接运行 node --test map-hud 不能加载 realBook 所需 MAP_ROUTER_MODULE；已改用项目 scripts/test-map.cjs，red.log 为正确编译环境运行结果（163/165 pass，新增两个展示断言失败）。route-red.log 记录真实相机 focusRoute 长路径断言失败；随后旧安全区严格等式因尺寸浮点变化失败，保持原底边15单位并使用1e-7误差。

- 重建时 setRoutes(...,true) 被之后 locate(true) 覆盖；选路 setRoutes 默认 fit=false。
- focusRoute 取所有路径点但以骑手为中心且最小 .6，无法完整容纳长路径。自动规划应独立 fit，以路径 bbox 中心投影到避HUD/底控件后的区域；不改变定位默认2和手动 .6–6。
- 大厅原白状态区+蓝AppHeader+白内容；手机只有正面框。按美术短规格增加独立阴影/侧层/反光，整块蓝覆盖状态栏及标题，保持正面内容。
- 路线去重目前基于 nodes，非造三条；已有风险/分钟计算保留。
- 主菜单只在 idle 开放抢单和车；底卡没有关闭viewState；仍等待PM最终导航/转单来源规格。

PM补充手动镜头复现：manual-camera-red.log，实际 CityMap.touchStart→touchMove→captureView→restoreView 断言失败（171/172）。原因是 overview 同时承担“低缩放不clamp”和“重建时自动fit”。拆出autoFit后，手势只取消autoFit，保留低scale边界模式；显式选路重新fit，定位退出规划模式。低于100m规划比例的定位动画在动画期间沿用宽边界，终态才恢复原30m跟随，另有投影收敛回归。
