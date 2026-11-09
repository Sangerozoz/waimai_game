# UI fidelity pass 2 — 展示实现交接

2026-11-04。源码与真实资源接入完成，已停写，可由主会话构建。没有运行 tests / typecheck / 回归 / 构建 / 浏览器截图，也没有宣称视觉验收或98%。

## 对照依据

实际以view_image逐张查看已认可目录全部8 PNG：00-home-v2、01-riders-v4、02-vehicles-v1、02-vehicles-locked-v1、02-vehicles-gallery-scroll-v1、03-orders-v4、04-maps-v1、05-bills-v1；另查看image-skin-pass/riders-fixed-prices-spacing.jpg、maps-named-spacing.jpg与visual-restoration/after-vehicles、after-orders、after-bills。两张supplement原生图集均已实际查看。

## 已改展示

- 深蓝文字与细边统一；底栏恢复连续四格，两内格用Cocos Mask GRAPHICS_STENCIL裁下角衔接中央圆钮，图标/文字向外光学偏移。保留图片纹理与唯一当前页×行为。
- 骑手保持174高、双列与188行步长（约5整行，31人约3屏）。主角/未拥有肖像98×144，卡内有边距，右侧独立操作按钮；已拥有NPC肖像98×116，下排双操作。真实身份名/固定ID报价照旧。
- 已拥有NPC今日收入只汇总当日npc_delivery且detail.riderId匹配；作业耗时为真实riderEffects服务耗时比例；收入加成来自incomeFactor。候选展示真实基础收益与服务耗时，无配车信息。
- 车辆大图左（366×316）、参数右（独立228宽），名称/拥有数/等级/三参数/唯一购买分层；三列宫格单独图片区与底部标题拥有数，选中标记不挤出卡边。
- 订单食物128图、27字标题、32字报价；时限、蓝取/绿送两条地址带、真实checkbox；固定汇总恢复载重/预计收入/选择路线三分区。真实专送及广告暂不可用、路由交互保留。
- 账单四模块：今日经营、近七日配送收入、累计账目、累计支出明细。增加真实指标图标与清晰图表轴线、刻度、每日数值。图表和合计均只汇总hero_ordinary/hero_special/npc_delivery/legacy_delivery四类，其他收入不混入。V2账本无任务奖金分类，不编造任务奖金栏目。
- 模型无持久里程/在线时长，不填样例；对应空间展示真实今日主角/骑手完成数、累计完成数、在册人数。日期未知账目保留单独说明。
- 五地图原画保留，仅标题字号层级调整，晴川县/云浦市/星澜城/曜川都会/海境港仍来自CONFIG，价格与真实购买选择保留。
- 首页加真实CityMap.locate(true)定位按钮，未改CityMap/源地图。

## 资源

复制supplement/attributes-atlas-v2.png和navigation-atlas-v1.png到resources/ui-v2并建立唯一meta；公共manifest增加12枚icon及income/expense别名。PNG未处理/抠图/放大，rect依据inspection.json已记录alpha128BBoxWithinRect外加40原生像素必要边缘，不扩大光晕为背景罩。原图status仍candidate，未改称验收。

V2ApprovedSkin.glyph保留明确fallback。资源加载后隐藏fallback，页面销毁后的异步回调仍由isValid保护；现有自有SpriteFrame销毁逻辑未改。

## 本轮写入边界与待目视事项

只写V2GameUI.ts、V2ApprovedSkin.ts与ui-v2资源/manifest/meta及本报告。没有改domain经济/报价、路由、存档、Bootstrap、CityMap、原地图几何；没有生成地图或新人物。构建后主会话需实看六页：尤其内格Mask、骑手长价格适配、车辆图文间隔、订单汇总、账单零数据和非零数据轴线、补图低alpha边缘。当前只完成展示实现与静态源检查，运行画面未复核。
