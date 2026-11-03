# UI尺寸、整按钮取餐服务进度与50款餐品

**已实现，未测试，待用户说“阶段完成”后集中测试。** 本轮未运行测试/typecheck/回归/渲染核验或独立复验，未操作用户游戏/存档，未commit/push。一次最终构建交付，未增加素材批次或冒充新图已完成。

## UI尺寸

- 底栏四个侧入口icon scale从AU03的1.15改1.725（1.5倍）；图标中心从y31上移至45，让最大82.8设计单位图片底部仍高于caption顶部。caption字号/位置、slot及触摸尺寸不变；中央订单是文字主动作圆钮，本轮没有放大其caption或点击区。
- 招募仍禁用，保留灰色语义；已有原生图标细化为人物加号轮廓，未使用不对应的AU03图，也未声明AU05新招募成图。该原生图标与其他侧入口同受1.5倍绘图scale影响。
- 站点图片显示框108→86.4（0.8倍），其禁用grayscale与无新增点击保持，既有按真实图宽定位机制继续使用。暂停仅PauseSymbol子节点scale为0.5，按钮绘制/触摸区/头像下位置及仅待配送/配送中可见规则不改。

## 真实取餐服务进度

点击取餐仍执行OrderBook.pickup并先保存；服务按钮为不可点击“取餐中”，在整个按钮内面用暖金色背景从左向右填充，保留细边、前景深色文字，不是细线。每帧读取active.pickupWaitElapsed/PICKUP_STOP_SECONDS（同业务2秒常量），不自行计时；初次绘制及读档重建也直接读取保存的真实服务进度。既有pendingSave在advance之前冻结，失败不继续服务。

满进度只是表现；仅phase=awaitDeliveryStart且非pendingSave时“去配送”主操作可点，仍调用book.deliver，必须手动点击才出发。服务完成保存失败时原服务按钮保留满填充且禁用，待同一快照提交成功重建后才出现可用“去配送”。取餐点击提交失败亦由原pending冻结，不能误开配送。服务进度节点在renderPanel时重建、随订单销毁，未改业务计时、暂停或取消语义。

## 50款餐品目录与兼容

按docs/art/prompt-batches/AU04-food50-user/catalog.json精确追加imageIndex16–49的id/name/index；前16原记录保持，包括旧易损类别/重量。新增34实际进入FOOD_CATALOG，现有OrderBook新候选两条生成路径均调用selectFoodForOffer，因此生成时可抽到新增食品；未调用刷新、重抽旧池或迁移旧候选。初始引导首单原鸡腿饭逻辑保留。

抽样仍先按COUNTY_FOOD_MIX的易损类权重选类，再在类内做未展示优先选择；类内新增项不改变类别权重。费率、县城餐损概率、时限公式和随机数提交底座未改。每份重量采用既有0.5/1kg档，整单仍由既有数量乘每份重量并受原载重保证约束。完整新增映射见new-food-mapping.json及下表。

foodForOffer按名称找目录，旧“家常饭盒/家常饭/小炒套餐”兼容别名保留；旧存档仍按原保存的food/weight/fragility履约，不因目录扩展重算。无需新schema。

FoodImages现在以准确餐品名称绘制原生卡面占位；cartoonFoodKey对无真实图索引返回null，16–49不再默认错取鸡腿饭图片。现有0–15仍加载旧food-sheet，异步失败也保留准确名称。50款新风格图片尚未交付，不能把数据扩展称为50款美术更新；后续用户五批图片到达后再按索引接入。

## 构建与证据

npm run build:map --prefix delivery-game实际包装退出0，build.log于2026-10-30 14:33:16 Finished。产物delivery-game/build/map-sample；4181静态index与主包HTTP200且SHA匹配当前产物（static-http.json），仅静态HTTP，不运行游戏。

before/及before-sha.json为真实范围基线；production.patch列实际5个生产模块差异（MapSample、SampleUI、FoodCatalog、FoodImages、CartoonArt），OrderBook仅留before未改。final-source-sha.json、build-manifest.json、delivery.json为最终指纹/构建退出码。比例、文字留白、服务恢复/提交失败与候选分布均未测试，不套用历史结果。

## 新增食品类别/每份重量

| index | id | 名称 | 类别 | kg/份 |
|---|---|---|---|---|
| 16 | curry-chicken-rice | 咖喱鸡肉饭 | normal | 1 |
| 17 | eel-rice | 鳗鱼饭 | durable | 1 |
| 18 | tomato-egg-rice | 番茄炒蛋饭 | normal | 1 |
| 19 | braised-chicken-rice | 黄焖鸡米饭 | normal | 1 |
| 20 | roast-duck-rice | 烧鸭饭 | durable | 1 |
| 21 | pork-cutlet-rice | 猪排饭 | durable | 1 |
| 22 | shrimp-fried-rice | 虾仁炒饭 | durable | 1 |
| 23 | sausage-claypot-rice | 腊味煲仔饭 | durable | 1 |
| 24 | seafood-fried-rice | 海鲜炒饭 | durable | 1 |
| 25 | mushroom-chicken-rice | 香菇滑鸡饭 | normal | 1 |
| 26 | beef-noodle-soup | 牛肉汤面 | fragile | 1 |
| 27 | spicy-rice-noodles | 酸辣粉 | fragile | 1 |
| 28 | snail-rice-noodles | 螺蛳粉 | fragile | 1 |
| 29 | rice-noodle-soup | 过桥米线 | fragile | 1 |
| 30 | spicy-mixed-noodles | 担担面 | normal | 0.5 |
| 31 | cold-noodles | 凉面 | durable | 0.5 |
| 32 | fried-noodles | 炒面 | durable | 0.5 |
| 33 | spaghetti | 意大利面 | normal | 0.5 |
| 34 | steamed-rice-rolls | 肠粉 | normal | 0.5 |
| 35 | steamed-shrimp-dumplings | 虾饺 | normal | 0.5 |
| 36 | pan-fried-buns | 生煎包 | durable | 0.5 |
| 37 | spring-rolls | 春卷 | durable | 0.5 |
| 38 | fried-chicken | 炸鸡 | durable | 1 |
| 39 | fries | 薯条 | durable | 0.5 |
| 40 | chicken-wrap | 鸡肉卷 | durable | 0.5 |
| 41 | sandwich | 三明治 | durable | 0.5 |
| 42 | grilled-skewers | 烧烤拼盘 | durable | 1 |
| 43 | fruit-cup | 水果杯 | normal | 0.5 |
| 44 | egg-tarts | 蛋挞 | fragile | 0.5 |
| 45 | pudding | 布丁 | fragile | 0.5 |
| 46 | ice-cream | 冰淇淋 | fragile | 0.5 |
| 47 | coffee | 咖啡 | fragile | 0.5 |
| 48 | lemon-tea | 柠檬茶 | fragile | 0.5 |
| 49 | orange-juice | 鲜榨橙汁 | fragile | 0.5 |
