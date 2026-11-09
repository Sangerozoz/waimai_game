# 六页UI还原源码实施记录

2026-11-05，UI唯一owner thr_uevwv32vnh → 父PM thr_axf6i4e89t。

**状态：已写待构建、未运行。不是还原验收通过，未报告98%。** 本线程没有Creator构建、部署、重启服务、tests/typecheck/回归，也未打开游戏、购买、招募、升级、接单、造档或清档。当前JPEG都是改动前证据，不能用于证明本次实现效果。

## 写集与依据

仅编辑以下源码，未改资源loader、manifest、Bootstrap、业务domain、路网、存档、全局baseline/handoff：

- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2GameUI.ts`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2ApprovedSkin.ts`
- `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2Spacing.ts`

三文件原本均为untracked，本轮原地编辑，没有清理其他dirty/untracked、提交、推送、建worktree或派子代理。当前源码SHA和方法行号见 `source-evidence.json`，行号会随后续编辑变化。

实际逐张打开认可目录8张PNG：00-home-v2、01-riders-v4、02-vehicles-v1、03-orders-v4、04-maps-v1、05-bills-v1、02-vehicles-locked-v1、02-vehicles-gallery-scroll-v1。已读revision-requirements-at-approval.md和implementation-baseline.md顶部最新UI/经济覆盖段。

实际打开当前riders-after/maps-after、pass3车辆/订单/账单、配车/升级、补给top/bottom；另查看原始皮肤panel-glass-v1与用户关闭×近照。完成自身对照后读回独立visual/spec-audit.md和resources/report.md。保留新版固定身份/报价、自由购买、五图命名与唯一slot规则，未恢复旧资格。

## 最新用户要求覆盖旧参考的实施

1. 首页两个配送/结算浮字节点、关联tripText/feedbackText字段与纯展示刷新函数已删。订单详情状态、账本及结算实现不改。
2. 首页骑手数量条已删。改为真实已招募NPC活动摘要，明确排除hero。无NPC不生成卡。每张摘要有头像、真实姓名、绿色空闲/蓝色配送中；最多显示3行，其余可滚动，避免遮满地图。
3. NPC状态读取V2FleetSnapshot.fleet.quotaMs、batches；计时只用匹配批次orders[paidCount].dueMs-elapsedMs。不读取墙钟推算、不虚构路网ETA；无quota显示经营时长已用完，无车显示待配车。
4. 右下“补给”文字按钮删除，使用既有补给箱expense图标，按钮置于右侧上方(x290,y425)，调用原supplyOpen流程；定位保留右下。水/饮料缺独立美术的问题仍登记。
5. 任务提示固定first-car → first-npc → first-paid-map，仅取首个未完成目标，全完成隐藏；去掉targetIndex/换按钮。读领域owner新增first-paid-map，不复制付费图判定。即使余额不足也可去查看，不形成资格门槛。背景alpha仅作用皮肤，文字保持清晰，不加奖励。
6. 删除账单“重新开始”、confirmRestart和UI内runtime.restart调用，不移到其他位置。公开onRestartFailure属性暂保留，以兼容未修改的Bootstrap绑定；本UI已无调用。启动页入口由父PM其他owner处理。
7. mainAction关闭态字形上移12设计单位，普通抢单文字上移4；盘心/146×146热区/底栏位置不变。依据已打开近照：约210px盘径，×可见中心下偏约20px，换算至约122设计单位可见盘径约12单位。此为光学修正候选，未运行截图证实居中，正常文字也需复核。

## 逐页结构与源码证据

|页/区域|本次已写改动|对照与尚未核验|
|---|---|---|
|公共框架|沿用940×1673→720×1280投影；地图金币壳300原图宽、账单274原图宽，订单237原图宽；金币整数去无意义.00，真实分值保留小数；余额数字/coin/plus独立分区|六位整数在100设计宽金额区按24字号排布，尚无新运行长金额截图；更长小数仍需核验|
|公共皮肤|skinSurface用圆角stencil裁切既有图片皮肤的外溢杂点，保留连续GlassEdge；不改loader/原生图；支持fill alpha只影响皮肤层；状态胶囊裁切半径h/2|原panel-glass透明边外可见脏点已实际查看；裁切是否完整清除小/中/大卡杂边需构建后看图|
|底栏|保留四菜单/内侧切角/当前唯一×/橙圆；仅圆盘文字光学偏移|图标实际轮廓与圆盘环线仍依赖资源及实图，未称通过|
|首页|身份HUD拆为地址/定位针、等级徽标和经验条，头像不再与两行文字挤压；可点身份区看骑手经验。删除数量条/浮字；新增NPC真实摘要、右上补给图标和固定半透明目标|旧地图主体仍为P0；主体没有换/遮掉/排除。保留底部已送统计、定位及原配送动作|
|骑手|双列166高+10行距，约5完整行+下一行露出；31身份16行总2816设计高，约2.81内容视口。姓名/等级/状态重新分区；未招募显示真实收入加成和服务耗时，无配车信息；已拥有今日收入仍来自当日ledger/riderId，升级价仍riderUpgradeQuote|无真实短介绍字段，不编造人物简介；已招募/配送/满级仍缺新运行证据|
|车辆|默认预览第3车型，对应原图主态但使用最新名称；主图节点500×350，依据原图alpha实物边界校准；右侧完整详情与唯一购买保留；下方三列宫格图更大、选中改橙角白勾而非蓝等级牌|C源1536×1024、alpha>32范围(215,18)..(1425,1014)，500宽contain时估实物约394×324，接近原图投影目标391×325。只是源像素估算，镜/胎/后箱是否完整待实图；没有恢复地图锁|
|地图|五图独立卡/现代名称/真实状态费用；去深蓝硬标题矩形，改白字深蓝描边；图边距由8降4，状态胶囊；缺图显示加载/失败状态|未购/当前/已购非当前仍依状态调用原API；不把5张商店图卡说成5张运行地图|
|订单|调用原FoodImages，展示层146×128矩形窗口取代128方缩略；保留连续列表/蓝取绿送/真实重量时限；金额和固定汇总收入更突出，汇总高105、路线按钮216×77，列表安全边界保留|无权威fragility/菜品字段或刷新API，未造易损标识/刷新次数。菜图仍是原有按order id稳定映射的展示素材，不是业务权威菜品。选单/报价/路线未行为核验|
|账单|保留四模块，今日副区恢复完成/主角里程/在线三位置；缺字段明确未记录。累计区恢复配送/任务奖励/支出三位置，奖励无字段标未记录；真实初始资金/余额；七日轴以400金币最低上限，柱仍由真实分值算；去无意义.00|不画样例24km/38分钟/57奖励，不造非零柱。任务奖励与里程/在线是业务数据缺口，页面不算完整通过|
|辅助页|配车、升级、补给、配送中结构和调用保留；统一皮肤及滚动位置管理|未改assignVehicle/supply/pickup/upgrade/acceptBatch等业务定义，无扣款/占用/配送行为验证|

## 滚动位置修复

已追到共因：render销毁body后，PresentationLayout.scrollContent新ScrollView默认从顶部开始。本次保留真实ScrollView偏移，不禁止数据刷新。

- render销毁前采集每个仍有效ScrollView.getScrollOffset().y。
- stable key为riders、vehicles、configuration:riderId、maps、bills、orders:lobby、orders:trip、supplies；首页活动摘要另有home:npcs。车型key不含modelId。
- 新content立即按保存偏移放置；布局后scheduleOnce调用stopAutoScroll/scrollToOffset(Vec2)，依据getMaxScrollOffset clamp，防内容缩短/列表变长时越界。
- 延迟恢复检查节点有效及key所对应的ScrollView实例，防已销毁旧页回调覆盖新页。位置仅在内存，不写存档。
- 已只读核对Creator3.8.8 scroll-view.ts中getScrollOffset/getMaxScrollOffset/scrollToOffset定义；未执行运行滚动验证。

## 静态核验范围

已逐段读回三份展示源码，rg核对无targetIndex、confirmRestart、UI runtime.restart、首页RiderCount/tripText/feedbackText创建；所有8条原页面scrollContent路径已改稳定key包装，辅助活动摘要独立保存key。读取domain定义后才使用V2FleetSnapshot字段与first-paid-map，不发明API。

资源工程新增ui-art-state事件已从实现读回，地图/NPC肖像状态订阅接入；imageSkin、cartoonArt公共签名不变。没有以SHA/文件存在声称屏幕显示正确。下一步由父PM统一构建、远程路径图片确认和独立实图审查；本线程不越权补运行证据。

## 追加P0：U01连续移动与U02跟随

父PM最新排序将连续移动/跟随提至皮肤之前。本UI已写：map.setRider(route.position,0)移到0.5秒节流之前，每帧读取真实routeSnapshot；不插值、不虚构进度、不通过动画掩盖业务时间补跑。HUD/账本/状态仍节流。route cursor变化只更新路线层，不再因cursor切换全页销毁重建；phase/batch变化仍更新真实控件。

CityMap既有captureView/restoreView/isFollowing/locate API已追定义：setRoutes会清follow，本UI在调用前captureView、调用后restoreView保留用户跟随/缩放/偏移。planned/idle/finished→travelling时locate(false)进入跟随；用户拖动造成follow=false在后续leg/阶段保留，定位按钮可恢复。没有改CityMap/Runtime。routeSnapshot仍有clone成本，Runtime热路径与时间契约属于父PM功能/逻辑owner；不能凭本UI节流修正宣称卡顿已解决。以上全部未构建/未运行。

U21车辆顶部“场景+选中车”是最新授权需求，覆盖旧透明图展示，但排在P0之后；本次尚未实施场景。车型切换/身份/动态参数保留，不能将放大透明车图报为已完成U21。
