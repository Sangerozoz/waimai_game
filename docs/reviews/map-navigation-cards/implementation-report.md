# 地图导航路线与取送点信息卡（2026-10-30）

状态：已实现，未测试，待阶段集中测试；用户视觉/体验未验收。

## 实际实现

已查看 reference 中 poi-info-card.png、route-blue-thick.png、route-contrast.png 三图。只修改 CityMap.ts、MapSample.ts 两个呈现层文件，不修改路网、候选、经济、存档、时钟或素材。

CityMap 的 NAVIGATION_STYLE 集中路线与卡片配置。选中路线 #168BFF，7.5 CSS px，浅色外沿总宽10 CSS px，沿已有 Graphics 圆端/圆角绘制；备选蓝灰4 CSS px，选中路线最后画。每次缩放及定位动画重画时以 cssUnits / worldScale 换算，保真实 routes、selected 和路段顺序。

新增 setNavigationStops(stops|null) 仅接收展示数据：真实取餐/配送 POI 名称及节点坐标、当前 offer.food。MapSample 从当前订单与 CityData 注入；取餐卡为餐厅名，配送卡为既有 FoodImages 缩略图或准确餐名占位加目的地名。没有价格/ETA/新点击入口，未使用未净化的50张新图。

卡片置于不随世界缩放的 overlay，146×52 CSS px，正文13 CSS px、17 CSS px行高，暖白面板、克制边框与阴影。文字固定可读字号、有限区域换行并裁止，超长名称不无限撑大卡片。图片占位单独采用10 CSS px文字。

所有相机同步路径（拖动、缩放、rider跟随、locate动画、restore/resize重建）更新屏幕锚点；取送Pin按同一实际POI锚点保留，不恢复全地图POI圆点。点位出视口时隐藏信息卡，不把离屏点强行钉在边上。

卡片避让采用头部/暂停实际底缘、底卡限定的地图视口、站点/定位/加速上边界及安全区内16 CSS px边距。先上下错位，近点优先左右并排，再尝试左右/视口内候选，保留引线；候选避开另一卡与两枚Pin。空间不足时隐藏无法安全摆放的卡片，保留Pin，不以遮HUD或裁卡强行展示。主卡框按16 CSS px边界约束，小阴影可外伸1–2 CSS px。

总览沿原真实路线范围和相机公式，加入实际POI坐标，用卡片实际半宽、卡高、Pin高度和间隔收紧可放置锚点范围；允许原有总览小于手动最小比例。15m默认与手动缩放限制保留。

重建/切单/取消由旧DeliveryUI整树失活销毁清理；done不注入卡片数据。setNavigationStops重设时先销毁旧卡/引线。沿用FoodImages→CartoonArt原有isValid严格销毁检查，旧图片回调不写入新卡；临时隐藏使用UIOpacity，避免异步图片因为当时卡片离屏而永久放弃展示。

## 保留与边界

保留16 CSS px公共入口、暂停半尺寸白Ⅱ/热区/阶段、40新单时钟与指数加速、取消保存边界、结算清卡与回执业务；生产素材未改。极端短视口、长名称、近点和多种屏幕比例的实际观感，留待阶段集中测试与用户体验验收；本次不声称这些已经验证通过。

## 交付证据

一次必要构建：npm run build:map --prefix delivery-game。16:20:27 Cocos日志显示Finished，包装退出码0。build.log保留原始 `Exit process with code:null, signal:SIGTERM in task build-script` 诊断，不把包装成功说成每个原子进程无异常。

4181只做静态HTTP交付：200，本地index与响应SHA一致；build-manifest.json包含index与最终构建JS清单。未打开/操作用户游戏页面或存档。

before/为真实改前文件，source-sha.json为前后SHA，changes.patch仅本轮增量。无commit/push，无reset/clean，既有未提交/untracked保留。

未运行测试、typecheck、回归、渲染或独立复验；构建与静态HTTP不代替阶段测试及用户验收。
