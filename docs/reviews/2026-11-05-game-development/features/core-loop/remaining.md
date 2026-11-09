# 核心配送闭环B：依赖、未执行case与阻塞

状态：Runtime/UI接线已落盘，**尚未功能验证**。用户未说阶段完成，本批未tests/typecheck/回归/构建/部署/游戏操作；未接单、购买、造档、清档或模拟SDK成功。

## 必须交齐的领域依赖

1. 逻辑owner交回`V2GameSession.continueTrip():void`、`V2RouteSession.continueTrip():void`、ready联合类型和`Stop.orderIds`。静态读取时仍是Game组合v3/Route v1；B不向这些文件写临时stub/强转。父PM必须等两写集齐，不能拿当前中间态做可用包。
2. Game/Route保证取餐服务完全结束才进入ready；cursor指向下一Stop，人物仍在商家，legSeconds/serviceSeconds为0。UI ready取上一Stop的真实商家/份数，下一Stop仅用于“去配送/去下一站”判断，绝不本地修位置。
3. Game.continueTrip只允许ready且无补给action，不扣费、不补跑。auto经同一Game入口；ready tick只推进真实NPC经营，不增主角行程。Runtime仅保留既有原子时钟/保存接线，不代实现。
4. Route v2/Game v4旧当前进度兼容与单成员Stop规范化由逻辑owner完成。原在途顺序/到达凭证/合同/期限/已入账结果不由UI重新生成。
5. 同权威商家新批合并2秒/1点、逐客交付与收据独立，以及choices/起步体力预算口径属于领域owner。UI只显示真实数组数，不把显示份数当合并正确证据。

## 待阶段集中case（全部未运行）

- 同店两单：两页均显示真实商家/2份，取餐只发一次pickup命令；服务0→2秒文字来自serviceSeconds，组内订单均更新；服务结束原地ready，显示去配送/去下一站。
- 不同店/同名不同店不误并；旧在途规范化后按原单成员顺序显示。零成员数组仅展示防空回退，不改权威快照。
- ready首页等待10秒：主角位置、gameSeconds、体力/风险不变；NPC按现实额度推进。再continue先tick旧ready到now，下一帧只用继续后的新时间，不追赶10秒停留。
- 重复/过期pickup与continue、planned/travelling/service/finished直接continue均拒绝，不推第二站、不发钱；保存或完整restore失败保持原committed/live，不展示成功阶段。
- 后台直接调用beginTrip/pickup/continue被Runtime门禁拒绝；hide/show首帧无补跑；无论paused与否，后台不允许这些显式阶段命令。NPC推进和SDK回调既有路径不受新路线门禁误伤。
- 详情paused时显式选路/取餐/继续仍可确认，回首页才计时；只点“回到配送地图”不能从ready偷偷继续。补给选择及其他页面的原主角暂停仍有效。
- ready补给/休息：action存在时不能继续，完成后恢复ready按钮；预算/库存/取消边界不变。**父PM集成已将补给禁用改为仅serviceCharged=true；未扣点服务可选择补给/免费休息。源码已改，仍须集中核对实际可达性，不声称行为通过。**
- service已扣点后体力恰为0仍显示真实进度，而非误标全程体力堵塞；未扣点仍显示体力不足；不能重复提交或插入另一补给服务。
- 部分顾客已送后取消：保留已到账/经验，取消全部未完成，保当前位置；本批关闭无重复收入/批次奖。
- 连续顾客服务/自动批次造成相同phase不同cursor时，详情订单状态与主动作不漏刷；action起止与blocked改变时控制状态刷新，进度秒只更新Label不每帧整页重建。
- 地图每帧权威position、首次出发跟随、ready显示/继续、拖动后follow/zoom/offset保留；八个原稳定滚动key的保位不退化。
- 骑手/车辆/地图/账单四页无顶部页名；首页完整HUD、订单大厅标题、配置车辆/补给标题、其余页金币栏和全部导航/功能仍在。已有订单/地图/账单用户修订不回退。

## 集成与其他边界

- 父PM等两owner交齐后统一必要Creator构建；构建成功也不等于行为case通过或98%视觉验收。
- patch自动逐文件检查被项目tsconfig规则跳过；未运行独立语法检查或tsc，不能报告“编译无误”。
- 原Runtime历史lastError保持最近失败及整快照事务成本、NPC事件时点、后四运行地图、真实广告SDK、未配置奖励等不属本批关闭项。
- 骑手“主角/小等级/未招募下移/取送省时/价格外置”新布局与万元近似取整仍待用户确认，本批未夹带落入源码。