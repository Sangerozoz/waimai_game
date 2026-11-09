# UI原图还原第二轮实施计划

用户最新授权：按已有认可效果图先做，细节后续再调整，不重新提设计或等批准。

固定参考docs/art/2026-11-02-approved-ui-reference/八PNG；最新经济固定ID报价、地图虚拟名称与单slot不变。首页导航地图有独立生产线程正在处理拼接，不在本轮改源几何或假贴首页截图。

- [x] 新鲜开发上下文实看8原图+当前截图，按原图构图调整六页展示，保留间距系统。
- [x] 重点车辆：大图左/参数右、标题层级、三列宫格；订单：连续卡片层级、图文与勾选、固定汇总；账单：三指标/七日图/累计区；首页HUD/底栏统一。
- [x] 只补缺的复杂UI图标，不重做已有19公共PNG/31肖像/5地图插图；原生素材由独立图像会话写指定目录。
- [x] 独立静态审阅展示交互/异步生命周期，不运行tests/typecheck/回归。
- [x] 必要Cocos构建到4182，实际六页截图核对并归档；不宣称98%，首页地图差距保留事实。

工程delivery-game/assets/scripts/map-sample/V2GameUI.ts、V2ApprovedSkin.ts、V2ImageSkin.ts、V2Spacing.ts与resources/ui-v2；开发只写此展示层。报告写docs/reviews/2026-11-04-cocos-v2/fidelity-pass2/。

执行完成证据：fidelity-pass2/README.md及六页after实图；小细节和首页地图差距不计本轮完成等于98%通过。
