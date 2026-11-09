# 用户反馈任务清单（唯一入口）

> **最新：手动时钟性能增量已交付。** 同checkout `/Users/sanger/Documents/ChatGPT/taptap 2`，本批仅Economy/Fleet/Dispatch三源省去严格受限manual双defer时钟的重复草稿，完整校验及Runtime保存后发布保持。options getter首审阻塞经真实20pass/5fail RED→25/25 GREEN关闭，独立Spec/质量复审PASS，默认192/192零跳过、typecheck0；Creator36/Finished、774构建输入无漂移。4182/4196现为`v2-manual-clock-final-1107`，入口＋全部14JS共30项本机HTTP哈希一致，524份打包resources与前包字节相同。模型40次完整结果一致，Dispatch41种/95步一致；实际隔离包长历史单次事务约109→99–101ms，rAF中位116.6/116.7→100.1ms，仍高于33ms预算，U01不关闭。用户当前无法测试，PM继续自主隔离验证；本轮真实亲送771→772、账本对平/slot完整恢复、无Runtime领域错误，仍有1条未定位资源404。补充未登录远程HTTP返回403/1010，远程响应身份未验，未动账号/权限；原自然档跨包原字节恢复仍BLOCKED；正式用户项关闭0、98%未验收。当前接续：依据热点压缩重复历史验证/状态复制，不动地图、价格、速度或30Hz。报告 `docs/reviews/2026-11-05-game-development/performance/manual-clock-1107/report.md`；下方旧包按对应历史理解。

> **11-07恢复器性能增量已交付：** 同checkout `/Users/sanger/Documents/ChatGPT/taptap 2`，仅Economy/Fleet/Dispatch接管本次JSON.parse的私有对象，删除三行重复复制，完整验证、公开投影隔离、Runtime唯一slot保存后发布均保持。默认167/167、typecheck0、独立规格/质量PASS，Creator36/Finished、773构建输入无漂移。4182/4196现为`v2-owned-restore-1107`，入口＋全部14JS共30项HTTP哈希一致，524打包resources与前包逐字节相同。40次模型事务字节一致，长期模型耗时约再降12.4%；实际隔离包长历史取餐/ready/混合行程单次事务平均约降10%，rAF中位133.3→116.6/116.7ms，仍明显不流畅，U01不关闭。用户当前无法测试，由PM自主隔离验证；无用户真实档访问，原档跨包直接恢复仍BLOCKED，正式用户项关闭0、98%未验收。报告 `docs/reviews/2026-11-05-game-development/performance/owned-restore-1107/report.md`；下方旧包均按对应历史理解。

> **11-07配送性能增量已交付：** 同checkout `/Users/sanger/Documents/ChatGPT/taptap 2`，仅Fleet无新亲送事件的同步改为先完整校验、再省去钱包事务；独立规格/质量复审PASS，默认156/156、typecheck0，Creator36/Finished、772构建输入无漂移。4182/4196现为`v2-hero-sync-validated-1107`，两端入口＋全部14JS共30项HTTP身份一致，524份打包resources与前应急借车包逐字节相同。既有771亲送/884 NPC模型输入40次候选结果全字节相等；长期取餐/行驶完整事务中位耗时降12.33%/13.03%，这不是FPS或U01整体通过。本轮无浏览器/用户档操作；原档跨包直接恢复仍BLOCKED，40用户项正式关闭0、98%未验收。报告 `docs/reviews/2026-11-05-game-development/performance/hero-sync-noop-1107/report.md`。下方旧包及旧阶段描述保留为对应时点历史。

> **11-07应急借车已交付：** 用户所选受限应急借车已实现，保留旧合同，真实亲送补额后明确取回实车归还。独立规格/质量复审PASS；默认145/145、UI11/11、typecheck0，Creator36/Finished及721输入无漂移，4182/4196现为`v2-emergency-hero-loan-1107`，每端入口和14JS的HTTP身份一致。实际Creator隔离流程使用仅mapKey变化的packed-transport副本，借还、重载及实车续送已验证；原源码夹具跨包直接恢复仍BLOCKED、失败字节保留，不能扩大结论。全部524份打包resources与前批相同，未改地图/路由或用户档。A/B已停止本批编辑，40用户项正式关闭仍0，98%未验收。报告 `docs/balance/2026-11-06-balance-round-01/pm/emergency-hero-loan-1107/report.md`。下文旧包/未救援描述均保留为对应时点历史。

> **11-07前批历史覆盖：** 唯一车防新增防线已集成并部署到4182/4196的`v2-hero-car-reserve-1107`；默认回归113/113、typecheck0、Creator36/Finished、721输入无漂移，每端入口及14脚本HTTP一致。[集成交付](../../balance/2026-11-06-balance-round-01/pm/softlock-prevention-1107/report.md)。旧已签零额度档救援仍开放；原B20～41证据保留，本轮无浏览器/用户档操作。长期有界结果150.076223分/12NPC/3图/5付费车型，两节点未到、二八null。40用户项/9工程项，正式关闭0，整体98%未验收。

> **11-06历史覆盖（当前以11-07记录为准）：** 4196最近交付为`v2-rider-recovery-1106`。骑手U23—U29及Runtime修正独立静态PASS、Creator成功/500输入无漂移，HTTP index/main bundle一致；已正常继续既有进度并实看首屏10完整卡+露头、末位书宁及约3屏范围，详见`integration/visual-riders-recovery-1106/receipt.json`。这7项不再仅源码/静态稿，未代填用户验收或整体98%。U39/U40的A十文件后端和B配套UI/资金刷新均已交回隔离候选；核心PART1四文件独立通过，PART2与完整UI门禁按`integration/slots-joint-admission-1106.json`接续。PM只撤掉候选误加的7行首页签约/容量/速度/收益浮字，该微修亦交独立审查，不恢复已删信息层。新格子/费用尚未进预览，旧根因和U01/U02运行验证不因局部源码PASS清空。任务内权限由PM管理，开发交回释放lease，原生Default尚pending时不虚报已生效；复审只读，仍不跑阶段测试或消费/造档。

当前不是已完成交付；此前所有“源码已改”均不等于网页更新或验证通过。

去重后用户反馈40项，另列工程发现9项；正式关闭0项。按优先级推进，不要求用户反复重述。

## 当前优先：先恢复可玩的配送过程

1. U01 连续沿路移动/卡顿跳站。
2. U02 地图跟随。
3. U03～U07 五类图片在实际分享入口可见。
4. 正式方案中的取餐/继续动作与时间契约，再收首页交互和页面视觉。

## 用户反馈逐条清单

### U01 · P0 · 配送严重卡顿、接单/取餐后跳站，恢复连续可见的沿路移动
- 负责人：PM / thr_29f6fcihz6
- 状态：B25～31有真实单状态链、画面和100ms投影；B32仅本单active窗rAF。不能再称未走配送，也不能关闭整体卡顿/跳站问题。（未关闭）
- 验收：按正式V1§4实际沿路移动、到点停下取餐、取完主动继续；不卡帧补跑成瞬移，不改速度/时间换算掩盖问题
- 历史问题依据（当前以上方状态/证据为准）：V2RuntimeController.drive每帧mutate；V2GameUI.update显示更新受0.5s节流，尚无性能实测

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/25-ui-depart-motion.json；docs/reviews/2026-11-06-product-testing/b/31-auto-delivered-finished.json；docs/reviews/2026-11-06-product-testing/b/32-active-delivery-performance.json

- 11-07追加性能证据：仅Fleet空同步省去重复钱包事务，保留完整组合校验；默认156/156、独立Spec/质量PASS。771亲送/884 NPC既有模型的长期行驶候选事务常规中位167.245→145.454ms（-13.03%），仍超过33ms；40次完整状态字节一致，不是FPS，不关闭本项。实际预览已更新，见[本轮报告](performance/hero-sync-noop-1107/report.md)。

- 11-07追加实际长历史诊断及恢复器增量：隔离before/after真实取餐、ready等待、继续行程及交付771→772；账本一致，实际单次Runtime事务平均约121→109ms，rAF中位约133.3→116.7ms，仍明显卡顿。默认167/167及独立复审通过，原试玩已更新；用户当前无法测试，PM继续自主处理。详见[诊断](performance/runtime-profile-1107/report.md)及[增量交付](performance/owned-restore-1107/report.md)，不关闭本项。

本批手动时钟增量：实际隔离长历史取餐事务108.669→98.829ms、ready107.714→99.633ms、混合配送109.743→100.950ms；rAF中位约100.1ms，仍明显卡顿。默认192/192、独立复审PASS、实际一单及账本/保存恢复通过，4182/4196最终包身份已核；U01继续开放，不能计真机FPS或98%验收。详见`performance/manual-clock-1107/report.md`。

### U02 · P0 · 配送移动时地图自动跟随骑手
- 负责人：PM / thr_29f6fcihz6
- 状态：115个记录投影follow均true且偏移居中；B33手拖后false、B34定位恢复true。未覆盖真机、多批/全部视角。（未关闭）
- 验收：出发后按既定体验跟随骑手，用户拖动可浏览、定位可恢复；切换路线/阶段不能无声丢跟随
- 历史问题依据（当前以上方状态/证据为准）：CityMap.setRoutes设置follow=false；V2GameUI没有可靠出发恢复跟随证据

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/31-auto-delivered-finished.json；docs/reviews/2026-11-06-product-testing/b/33-user-pan-not-forced-follow.json；docs/reviews/2026-11-06-product-testing/b/34-ui-locate-restores-follow.json

### U03 · P0 · 底部菜单图标缺失
- 负责人：PM / thr_29f6fcihz6
- 状态：底栏图标在新修复包B21～40多张实际画面可见；正式分享入口由PM核对。（未关闭）
- 验收：用户实际分享入口的对应图片真实可见，加载/失败不静默空白；本地文件和HTTP200不能代替远程显示
- 历史问题依据（当前以上方状态/证据为准）：ui-fidelity-recovery/resources/report.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/21-fixed-package-continue-same-order.jpg；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.jpg

### U04 · P0 · 骑手页人物图片缺失
- 负责人：PM / thr_29f6fcihz6
- 状态：B04/B05旧冻结包首末屏肖像实际可见；保留旧包来源，不当成本次新渲染全部骑手页。（未关闭）
- 验收：用户实际分享入口的对应图片真实可见，加载/失败不静默空白；本地文件和HTTP200不能代替远程显示
- 历史问题依据（当前以上方状态/证据为准）：ui-fidelity-recovery/resources/report.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U05 · P0 · 车辆页车辆图片缺失
- 负责人：PM / thr_29f6fcihz6
- 状态：B06/B09旧冻结包车辆主图与宫格实际可见；未做全部车型交互矩阵。（未关闭）
- 验收：用户实际分享入口的对应图片真实可见，加载/失败不静默空白；本地文件和HTTP200不能代替远程显示
- 历史问题依据（当前以上方状态/证据为准）：ui-fidelity-recovery/resources/report.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/06-vehicles-top.jpg；docs/reviews/2026-11-06-product-testing/b/09-vehicles-select-no-jump.jpg

### U06 · P0 · 地图页场景插图缺失
- 负责人：PM / thr_29f6fcihz6
- 状态：B10仅观察既有产品卡片插图；不属于地图制作/整城验收，不派地图工作。（未关闭）
- 验收：用户实际分享入口的对应图片真实可见，加载/失败不静默空白；本地文件和HTTP200不能代替远程显示
- 历史问题依据（当前以上方状态/证据为准）：ui-fidelity-recovery/resources/report.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/10-maps-top.jpg

### U07 · P0 · 抢单页菜品图片缺失
- 负责人：PM / thr_29f6fcihz6
- 状态：B12旧冻结包菜图可见；B22新修复包酸辣粉图片/脆弱徽标/2格可见。（未关闭）
- 验收：用户实际分享入口的对应图片真实可见，加载/失败不静默空白；本地文件和HTTP200不能代替远程显示
- 历史问题依据（当前以上方状态/证据为准）：ui-fidelity-recovery/resources/report.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.jpg；docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.jpg

### U08 · P1 · 六页/主要画面与认可效果图一致性目标98%，现版明显不达标
- 负责人：PM / thr_29f6fcihz6
- 状态：本次未执行六页对原始8张认可图的完整视觉验收；98%目标仍未通过。（未关闭）
- 验收：按8原图及后续明确变更逐页对照；主体图片/首页背景不排除，不贴整页截图假装游戏，不主观报百分比
- 历史问题依据（当前以上方状态/证据为准）：ui-fidelity-recovery/visual/spec-audit.md

- 11-07当前证据：完整验收仍开放；见结构化清单与范围说明

### U09 · P0 · 开发范围包含游戏逻辑、经济数值与功能，不限UI
- 负责人：PM / thr_gf8gehviua
- 状态：既有95/95纯V2日志及本次收口的真实单链均保留；不把95个TAP计数当95条完整玩家路径。（未关闭）
- 验收：主循环、报价扣费账本、运行入口分别逐条审查；不以有类/有按钮当完整实现
- 历史问题依据（当前以上方状态/证据为准）：dispatch.json及logic/economy/features报告

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/31-auto-delivered-finished.json

### U10 · P1 · 去掉首页配送状态/天气余单悬浮文字
- 负责人：PM / thr_29f6fcihz6
- 状态：已有B25～31行驶/取餐/ready/完成画面，可供浮字核对；删除项已实施，不重回旧静态稿；本次不宣称完整布局验收。（未关闭）
- 验收：首页不再创建该浮字；顶部HUD与订单详情保留

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/25-ui-depart-motion.jpg；docs/reviews/2026-11-06-product-testing/b/28-ready-before-continue.jpg；docs/reviews/2026-11-06-product-testing/b/31-auto-delivered-finished.jpg

### U11 · P1 · 去掉首页本批收入/补给/净赚/库存悬浮汇总
- 负责人：PM / thr_29f6fcihz6
- 状态：已有B25～31行驶/取餐/ready/完成画面，可供浮字核对；删除项已实施，不重回旧静态稿；本次不宣称完整布局验收。（未关闭）
- 验收：首页不再显示该浮字；不删真实结算和账本

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/25-ui-depart-motion.jpg；docs/reviews/2026-11-06-product-testing/b/28-ready-before-continue.jpg；docs/reviews/2026-11-06-product-testing/b/31-auto-delivered-finished.jpg

### U12 · P1 · 删除头像下骑手数量条，改已招募NPC活动卡
- 负责人：PM / thr_29f6fcihz6
- 状态：首页NPC活动卡替代数量条已有实现交接；测试只有主角，未验证已招募NPC卡及其持续入账，不重做现有源码。（未关闭）
- 验收：排除hero；真实头像姓名/空闲或配送状态；倒计时来自实际批次，不造NPC/ETA
- 历史问题依据（当前以上方状态/证据为准）：用户NPC卡附件；UI owner已报quota/batch/dueMs来源

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/21-fixed-package-continue-same-order.json

### U13 · P1 · 补给改图标按钮并移至右侧上方
- 负责人：PM / thr_29f6fcihz6
- 状态：新包右上图标实际可见，B37打开真实补给页、B38购买水；图标入口不再列待实现。（未关闭）
- 验收：旧右下文字按钮移除，新图标可辨且入口有效，不遮HUD

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/36-nonzero-progress-restored.jpg；docs/reviews/2026-11-06-product-testing/b/37-real-supply-menu.jpg；docs/reviews/2026-11-06-product-testing/b/38-ui-buy-use-water.json

### U14 · P1 · 首页任务提示半透明
- 负责人：PM / thr_29f6fcihz6
- 状态：半透明首辆新车提示已显示；未购买首车/首NPC/首张付费地图，不能补报整条引导通过。（未关闭）
- 验收：提示不遮挡主要地图和车辆，文字仍清晰

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/21-fixed-package-continue-same-order.jpg；docs/reviews/2026-11-06-product-testing/b/39-water-complete.jpg

### U15 · P1 · 不可换任务，固定引导首车→首NPC→首张付费地图，可忽略
- 负责人：PM / thr_29f6fcihz6
- 状态：半透明首辆新车提示已显示；未购买首车/首NPC/首张付费地图，不能补报整条引导通过。（未关闭）
- 验收：无换按钮；只显示首个未完成项，完成自动前进；免费初始图不计完成；不新增资格/奖励
- 历史问题依据（当前以上方状态/证据为准）：V2ProgressTargets first-paid-map已交；economy/implementation.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/21-fixed-package-continue-same-order.jpg；docs/reviews/2026-11-06-product-testing/b/39-water-complete.jpg

### U16 · P1 · 骑手页按钮点击后保持列表位置
- 负责人：PM / thr_29f6fcihz6
- 状态：B05→B07骑手返回偏移2004.7110692767483相同；未做招募/升级后的保位验证。（未关闭）
- 验收：重绘/进入配车后返回仍保留真实offset并clamp，不以旧数据显示掩盖跳顶

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.json；docs/reviews/2026-11-06-product-testing/b/07-riders-return-offset.json

### U17 · P1 · 车辆页按钮/车型选择后保持宫格滚动位置
- 负责人：PM / thr_29f6fcihz6
- 状态：B08→B09选择晨光后偏移252.30122761506283相同；未购买/升级，不外推所有按钮。（未关闭）
- 验收：选择末排车型后仍停原位置且预览正确更新，key不含车型id

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/08-vehicles-scrolled.json；docs/reviews/2026-11-06-product-testing/b/09-vehicles-select-no-jump.json

### U18 · P1 · 去掉账单底部重新开始按钮
- 负责人：PM / thr_29f6fcihz6
- 状态：B11/B40所查账单无重开入口，B20继续唯一进度及B35/36非零续档成立；不宣称所有入口/坏档/未来版本浏览器矩阵。（未关闭）
- 验收：按钮及确认入口消失，不搬到别页，不删当前进度

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/20-fixed-package-normal-reload.jpg；docs/reviews/2026-11-06-product-testing/b/36-nonzero-progress-restored.json；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.jpg

### U19 · P1 · 不允许玩家重新开始/清档重开
- 负责人：PM / thr_29f6fcihz6
- 状态：B11/B40所查账单无重开入口，B20继续唯一进度及B35/36非零续档成立；不宣称所有入口/坏档/未来版本浏览器矩阵。（未关闭）
- 验收：启动页无reset入口，startOver/restart拒绝且不触store；空slot首次正常开局和坏档防覆盖保留
- 历史问题依据（当前以上方状态/证据为准）：features/implementation.md

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/20-fixed-package-normal-reload.jpg；docs/reviews/2026-11-06-product-testing/b/36-nonzero-progress-restored.json；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.jpg

### U20 · P1 · 抢单圆盘关闭×视觉居中
- 负责人：PM / thr_29f6fcihz6
- 状态：实际B12/B22圆盘关闭×画面已留；不以本次证据整理代替用户视觉验收。（未关闭）
- 验收：真实截图里×可见中心与圆盘对齐；圆盘和热区不动；+12仅源码候选不是运行通过
- 历史问题依据（当前以上方状态/证据为准）：V2ApprovedSkin.mainAction；用户关闭态近照

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.jpg；docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.jpg

### U21 · P1 · 车辆顶部预览改为场景+选中车辆的沉浸式画面
- 负责人：PM / thr_29f6fcihz6
- 状态：B06满载和B09晨光的独立产品场景/车型联动已有画面；不重生图，不裁地图；未覆盖10车型/hover/购买矩阵。（未关闭）
- 验收：预览包含协调场景/地面/接地光影和选中车型，切换同步；车型身份/原图保留，参数和购买仍动态
- 历史问题依据（当前以上方状态/证据为准）：`layout/vehicle-showcase/scene-quality-1106.json`、`integration/visual-product-scene-1106/check.json`；单张原生来源保留，不重复生图，不将离线合成冒充运行截图

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/06-vehicles-top.jpg；docs/reviews/2026-11-06-product-testing/b/09-vehicles-select-no-jump.jpg

### U22 · P1 · 普通订单全为20金币，核查并补齐订单报价差异
- 负责人：PM / thr_gf8gehviua
- 状态：当前第一单20金币是保护期合同，B40真实结算2000分；不把保护单同价报成新故障。第15单及报价/成长平衡由A/PM现有数值工作继续。 A已完成同源策略模型，保护退出短途倒挂与2/4km同价风险保留；候选C仅隔离对照，生产报价不变。（未关闭）
- 验收：明确新手保护与长期报价边界；差异化报价必须显示/接单合同/结算同源，不能仅UI随机改价，不破坏已确认成长目标
- 历史问题依据（当前以上方状态/证据为准）：历史根因`economy/u22-order-pricing.md`；新版`economy/ordinary-effort-stage/{spec-review,quality-review,application}.json`；保留U22-PERF-01未测校验成本，不承诺不同订单必然不同价

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.json；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.json

## 新增排版/金额与订单反馈（明确结构已进源码，近似金额单独held）

### U23 · P1 · 骑手页我改主角
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U24 · P1 · 等级缩小并紧邻角色姓名
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U25 · P1 · 未招募标记移到肖像下
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U26 · P1 · 收益文案去基础二字
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U27 · P1 · 作业耗时100%改为易懂的取送省时表达
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U28 · P1 · 未招募NPC也展示统一收益和省时信息
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U29 · P1 · 招募按钮只写招募，价格独立置于信息卡
- 状态：主角、小等级靠姓名、肖像下未招募、收入加成/取送省时、外置价格与纯招募按钮已在B04/B05真实旧冻结包画面；不再整套held等静态稿，U30单独保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U30 · P1 · 一万以上万单位/易读金额，内部精确数值不改
- 状态：39,140→4万、42,170→4.5万、3,080,000→308万未形成统一普通四舍五入规则；仅金额展示held，不改精确扣款，不阻塞已实施骑手排版。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/05-riders-bottom.jpg

### U31 · P1 · 删除骑手/车辆/地图/账单顶部页面标题
- 状态：B04/B06/B10/B11四管理页顶部大标题已删；订单大厅标题不是本条四页删除目标。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/04-riders-top.jpg；docs/reviews/2026-11-06-product-testing/b/06-vehicles-top.jpg；docs/reviews/2026-11-06-product-testing/b/10-maps-top.jpg；docs/reviews/2026-11-06-product-testing/b/11-bills-no-restart.jpg

### U32 · P1 · 删除订单取送地址末端定位针图标
- 状态：B12/B22地址末端未见旧定位针；取/送前缀徽标保留。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.jpg；docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.jpg

### U33 · P1 · 订单重量紧跟餐品名称
- 状态：B22酸辣粉2格紧跟餐名，B40新签合同/订单均slots-v1占2格。旧ledger仍写当前KG为历史陈旧状态；不修改旧kg已签合同。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.json；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.json

### U34 · P1 · 订单金额移除金币图片，改数字前货币符号
- 状态：B12报价和B22订单报价使用¥文本；本条不删除页面全局HUD的其他图标，不改变金币单位计算。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.jpg；docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.jpg

### U35 · P1 · 订单时间图标与描述垂直居中
- 状态：B12/B22有实际图标和时间行；没有测量/用户验收，不主观关闭对齐问题。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.jpg；docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.jpg

### U36 · P1 · 明确顶部高价专送候选是否占位/实际可接状态
- 状态：B12真实高价专送133及广告未接入提示可见；未执行广告/自动权益，不伪造成功。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.json；docs/reviews/2026-11-06-product-testing/b/12-orders-lobby.jpg

### U37 · P1 · 地图未购买文案改未解锁
- 状态：B10卡片显示未解锁；仅文案，不新增购买资格锁，不涉及地图制作。（未关闭）
- 负责人：PM / thr_29f6fcihz6

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/10-maps-top.json；docs/reviews/2026-11-06-product-testing/b/10-maps-top.jpg

### U38 · P1 · 账单每笔金额前金币图标全部去掉
- 状态：B40已在新包非零收入20和累计收入20实际画面验证去币图；不再保留纯源码未画面核对的旧状态。（未关闭）
- 负责人：PM / thr_29f6fcihz6

历史确认稿（明确骑手排版已实施，万元近似单独held）：[骑手首屏/大金额切换](../2026-11-05-ui-fidelity-recovery/rider-proposal-01/index.html)。仅静态稿，实际价格和存档未改。

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.json；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.jpg

### U39 · P0 · 重新优化数值系统与前段升级价值
- 状态：首轮41条模型的可达性与账表一致性获B独立只读PASS；11.04/21.58分仍仅为操作假设，10/15单预算保持。长期有界实跑150.08分钟配齐12NPC/3图/5车型，触CPU限，两个资产终点未到，二八比不报告；30级训练排除、同一city供给。唯一车防新增与受限应急借车已集成、独立审查及定向验证并部署；源码夹具跨打包直接恢复另留边界，C未批准，未平衡验收。（未关闭）
- 验收：费用、逐级属性、回本单数及购车/招募/升级取舍一致；不能只涨价或死守旧尾价，既有资产等级/已签收入保留。
- 依据：`economy/user-economy-defect-arithmetic-1106.json`、`../../product/2026-11-06-capacity-slots-upgrade-revision.md`。

- 11-07当前证据：docs/balance/2026-11-06-balance-round-01/a/report.md；docs/balance/2026-11-06-balance-round-01/a/verification.json；docs/team/handoffs/2026-11-07-codex-migration/pm-continuation-admission-1107.json

### U40 · P0 · 初始2容量，餐品占1或2，背包式整数格
- 状态：真实2/2格接单、合同、配送/清批、非零续档已覆盖；实际产物4/4含历史kg/混单位拒绝是既有回归，不冒称本次全浏览器NPC/多单兼容矩阵。（未关闭）
- 验收：承载、订单、报价输入、路线、NPC、存档和UI一起接线；整数成长有可用空间，候选供给不成为隐藏固定单数上限。旧批不重价、不随意改weightKg，不只改单位文案。
- 依据：现有旧UI缓存只读观察为8条、1kg与2kg各4条，总12kg；这是一次旧池观察，不当新槽位分布或长期实测。

- 11-07当前证据：docs/reviews/2026-11-06-product-testing/b/22-fixed-package-planned-route.json；docs/reviews/2026-11-06-product-testing/b/31-auto-delivered-finished.json；docs/reviews/2026-11-06-product-testing/b/36-nonzero-progress-restored.json；docs/reviews/2026-11-06-product-testing/b/40-bills-earned-and-supply.json

## 工程发现与依赖

- **E01 P0 自动跨批余时间、planned切自动、空闲卸车tick、取消剩余距离**：当前源码已进入已测修复包；原95项用例含自动尾段/取消/保存边界，保留旧失败；未把单一浏览器路径扩为全部状态验收。；负责人：PM / thr_gf8gehviua。
- **E02 P0 同店合并取餐、取完主动去下一站**：原95项含同商家多单合并一次服务；B25～31已实际走取餐→ready→主动继续→送达。同店多单浏览器路径尚未覆盖，整体未关闭。；负责人：PM / thr_gf8gehviua。
- **E03 P0 长帧/细帧NPC补额度事件时点一致性**：原95项已含NPC 0额度长帧/细帧一致、同毫秒先结旧单再补额及回退去重；不再记源码未实现，实际完整NPC矩阵仍未验收。；负责人：PM / thr_gf8gehviua。
- **E04 P0 运行配送范围与用户蓝框对应**：PlaceCatalog密度推算dispatchBounds线索待读回，不改源city/三框；负责人：PM/逻辑。
- **E05 P1 NPC实际workAt账本日键归属**：原95项已含逐笔workAt本地日键与旧unknown-date保留，当前包已包含；原始历史日期不迁移。完整浏览器跨日流程未覆盖。；负责人：PM / thr_gf8gehviua。
- **E06 P1 广告/自动剩余权益、停止恢复的UI接线**：领域API已有但UI缺接线；真实广告SDK仍是外部阻塞，不模拟成功；负责人：功能/UI，PM协调。
- **E07 P1 真实SDK、完整运行地图、未确认任务奖励**：按最新产品/地图严格独立要求从本线派工与验收范围移出；不修改、不推进、不声明地图完成；负责人：不由本产品线负责或派工。
- **E08 P1 经济参数同源、整数分报价扣费及累计公式**：原95项与PM同源参数/报价探针、A36项输入指纹保留；金额守恒和公式检查有证据，长期数值平衡仍未验收。；负责人：PM / thr_gf8gehviua。
- **E09 P0 唯一旧车先借NPC后额度耗尽占车**：防新增保留；受限应急借车已实现、独立规格/质量复审PASS。默认145/145、UI11/11、typecheck0；Creator36/Finished、721输入无漂移，4182/4196新包入口与14JS逐端HTTP一致。原自然终态在领域恢复成功；隔离packed-transport副本已真实借车、两次亲送补额、原NPC两合同结清、归还/重载及实车继续配送，最终100金币、永久1车。源码夹具因JSON字段顺序产生的跨打包mapKey直读仍BLOCKED，失败及原字节保留，未改生产路由或用户档。；负责人：PM / 借车作者A / 独立审查B；工程项仍待用户验收，不关闭来源夹具跨包边界。

## 11-06历史执行记录（状态以11-07覆盖为准）

- A-SPEC-01源码修复已交定向复审：只收紧游戏同店身份条件，同时要求经营资格与权威配对唯一，不改任何原始数据或地图制作内容。
- NPC逐笔日期归类三文件已读回，PM规格静态核对通过，独立质量审查thr_ef9asz76ur待结果；帧内补额度独立缺口不关闭。
- 四页标题删除已进入源码，不再依赖骑手静态稿确认；试玩旧包尚未覆盖。
- 地图制作及相关工作与本线无关，历史E07不再作为产品派工或完成门禁。

## 持续收单规则

用户继续反馈，无需自行整理。PM负责去重、编号、核对设计覆盖关系、指派唯一owner、集成与验收证据；不能因中断丢项，也不以子会话源码完成勾结案。

## 不变的处理纪律

- 产品依据：正式V1第4节的沿路自动移动、到店停下主动取餐、同店合并服务、取完主动继续；新经济与后续明确变更优先，不回退旧资格。
- 状态依次记录：待处理→处理中→源码已写→已构建/部署→核对通过→用户体验验收。证据未齐不勾完成。
- 已有多角色只写各自文件；优先级由PM协调，跨API修改串行，不继续盲目堆小修。
- 地图角色只负责既有地图，不派UI/业务协调。
- 用户未说阶段完成，不自动运行游戏tests/typecheck/回归，不清档/造档。
- 不再把明显不合格预览当验收包；未达98%不宣称达标。
## 当前执行批次：真实可见纠偏与整数容量/数值重算

- A仅在economy/slots-economy-stage-1106继续新格子/数值/双profile实际代码；临时编辑模式及首个真实写入已核实，live不改。
- B当前骑手包已交回并完成独立审查/构建/实屏，另在layout/ui-funds-stage-1106修资金状态刷新，临时编辑已实际生效；复审仍只读。
- 4196已实际更新并留首末图，不再让旧权限拒绝或万元held拖住明确UI。新经济stage不混入该包；没有购买、升级、接单或注入，不跑阶段测试、不代填用户验收。
