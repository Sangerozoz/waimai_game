# SLOTS-FIX01 实施交回（stage-only，未测试）

**已实际修改同一stage的5份源；live未应用，未自判PASS。** 本轮读回`_bb/legacy-mode.value=accept_edits`且pendingValue=null后，正常patch先落Fleet必要两行，再完成其余四源。未复制stage、重生数表、改权限或绕写。Fleet首写SHA为b34bcdcf9df928b623298f8c865fca3e65f572bc7bd9d1a0c0895398dc5bec61；精确前后/原live/全10源身份见fix01-manifest.json。

## 两问题与实际改动

- **SLOTS-P2-RESERVATION-01**：已读quality-part2-fail.json:7-18。Fleet.validate:56在kg/slots分支之前，对每个尚在途batch用已有e检查：所有其他rider（包括hero）不能当前配其旧车，hero activeQuotes也不能用其旧车。忽略原owner自身未来配车，故仍可保留旧车、卸为null或换另一空闲车。仅拒绝不一致组合，不清批/改paidCount/dueMs/金额/等级/历史账本，原assignVehicle限制未改。这是继承的恢复缺口，不宣称现场曾重复用车。
- **SLOTS-P2-PERF-01**：已读失败报告:23-31及完整定义/消费者。Economy:225-242从验证后私有权威读标量；Dispatch:58-62薄委托；Game:29-35、107和Runtime:163-167改走该通路。旧Dispatch首个pending订单选择保留，只传标量ID，避免把所有合法组合误当作Economy.activeQuote同序。已签slot效果读冻结terms；kg旧批用原vehicleEffects；下一未签批与拥有对象展示读当前资产slot表。

具体新API、原有Runtime字段/null/Game错误、UI消费者与capacity脱离证明见contract-fix01.md。新类型不是隔离依据：冻结capacity显式对象字面量复制；资产helper每次新建外层和capacity，不返回参数行/车辆/骑手。保留当前slot/legacy合同验证、食品/ETA/补给、原价、随机序列与存储格式。

## 静态读取数量对照（非耗时/FPS）

计数是每次到达对应getter的完整读取入口，不是实测调用频率或底层JSON遍数：

- Game.deliveryEffects：有签约1次economyState＋1次Dispatch.snapshot，无签约2＋1；改后这两种完整读取均0。
- Runtime.deliveryEffects：有签约2次economyState＋1次Dispatch.snapshot，无签约3＋1；改后均0。
- Game.nextBatchEffects / Runtime.nextBatchEffects：原1 / 2次economyState；改后0 / 0。
- Runtime拥有车辆或NPC效果：原各1次economyState；改后各0。
- 普通候选、专送候选、自动无车检查三处纯存在性：原每个到达检查1次economyState；改后0。候选需要完整历史ID等正常业务读取仍保留。

精确delta为原stage→新stage五源；full diff为原live→新完整10源（含三份原live不存在的新模块）。只在内存按行号/原上下文逐hunk严格重建，正反方向均逐字节相同；未用TS或业务函数验证。Economy原验证/报价/命令/账本/序列化、Dispatch原事务/归日/时钟/restore、Game接受/ETA/食品/完整restore、Runtime mutate/drive/30Hz均静态文本保持；Game.tick仅更换存在性读取。Route/LoadRules/Profiles/SlotConfig/Rider及参数/UI/Spacing/Skin原SHA保留。所有具体静态断言见fix01-implementation.json。

## 残余成本及未执行用例

Runtime完整Game恢复→候选序列化→完整恢复验证→commit→publish仍在；Dispatch/Fleet嵌套事务、完整快照/恢复/校验仍在。Game直接Dispatch.snapshot调用点仅16→15，其他订单/控制/补给/HUD/账单读取仍在。pending订单、拥有实例与参数行仍有线性查找，Route.position遍历/完整legs验证及其他UI资源成本未改。**不关闭U01/U02，不宣称FPS、性能、卡顿或整体验收通过。**

未执行：kg/slots/混合容器跨owner或hero activeQuote占车拒绝；原owner未来null/空闲车合法；部分paid至完成保留/释放；slot冻结与kg旧解释、下一批新效果；无车/未就绪/hero NPC接口null及Game原错误；调用方修改capacity不影响下次读取；合法订单排序差异保留原pending选择；重复getter不写状态；NPC时钟/跨午夜/补给/ready/ETA与30Hz回归。JSON列有逐项未来case，未造档/故障注入或执行DTO。

## 自动LSP及交付门禁

普通编辑器自动回报了isolated stage缺少Ledger/TripRules/RewardSession、MapTypes/FoodCatalog/RuntimeStore及cc依赖，并衍生implicit-any、receipt字段和unknown诊断；Runtime输出末尾另外3项未展开。Fleet首写及后续标量ID选择补丁未返回新的diagnostics字段，不代表既有诊断清除。未主动运行typecheck/编译，未加any或复制依赖掩盖；详细实际反馈分类见JSON。

新增交付：fix01.diff、source-fix01-full.diff、fix01-manifest.json、本文件、fix01-implementation.json、contract-fix01.md。原manifest/source.diff/contract及所有审查报告不覆盖。既有PART1/UI PASS不移植到新SHA；父PM须组织delta/Economy新投影独立门禁并协调UI窄重绑，再整体应用，不单发writer。

源码/文档交回后停止写，本批租约交还PM恢复Default；没有运行TS/App/DTO、tests/typecheck、构建/浏览器、业务/存档、commit/push或新Agent。
