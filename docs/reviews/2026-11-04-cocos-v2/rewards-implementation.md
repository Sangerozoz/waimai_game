# Cocos V2 广告权益实现交接

新增 `delivery-game/assets/scripts/rewards-v2/RewardSession.ts`（目录/脚本meta齐备），无 `cc`、DOM、旧OrderBook、地图与存档依赖。按二八曲线及 balanced-economy-plan 广告章节实现纯状态模块。未改旧单单 OrderBook 或地图工程；正式页面与 SDK 调用链尚未接入，未来由新 V2 门面消费权益。

## API 与接入责任

- `enterLobby(entryId, appearanceRoll, priceRoll)`：调用方仅在真实进入大厅分配新 entryId，滚动/详情返回复用原ID。两个随机值须为[0,1)有限数。出现值<0.8，价格为100+floor(priceRoll×51)，整数100—150。不提供默认Math.random或隐藏抽奖。重复进入事件返回同一结果，已消费不复活；每次新进入都独立判定；未授权且无待播票据旧候选撤销，新进入失败返回null。待播/已授权权益单独保留不丢失，但失败入口不展示它；成功入口可展示此唯一保留权益。
- `requestAd('special', candidate.id, nowSeconds, ttlSeconds)` / `requestAd('auto', null, nowSeconds, ttlSeconds)`：颁发绑定票据，一个待播广告；TTL由SDK集成方明确指定，无叠加/重置未耗尽自动权益；活动批次期间禁止请求新的自动广告。
- `RewardedAdSDK.show(ticket, callback)`：仅接口，无伪造广告成功实现。SDK适配方仅在平台验证奖励事件后回调`completed`，取消/失败分别回调对应结果。
- `resolveAd(ticket, outcome, nowSeconds)`：完整ID/权益/订单/到期时间匹配；成功一次，未知/不匹配/重复/过期返回false，取消失败终结票据不奖励。非法结构/倒退到请求前的回调时间抛错。时间须为跨恢复仍可比较的秒时钟，TTL不冻结。
- `beginBatch(orders)`：普通单可多单，专送必须单独一单并有广告授权；已知专送ID禁止伪装普通单，已有活批次禁止再次开始。返回专送固定标价`specialCoins`，不叠乘车辆/经验，不在此处入账。正式订单门面还需验证容量、路线、体力，完成后通过正常结算链发钱；不能在广告成功时发钱。
- `endBatch()`：关闭活批次，不复活已消费专送；在途完成/取消由正式配送状态负责。
- `advanceAuto(deltaSeconds, foreground, paused)`：仅前台非暂停消耗600秒预算，返回`runSeconds=min(delta,剩余)`。调用方必须只推进此段自动配送时间，归零后的帧尾交还手动，保留在途单，禁止自动接受下一单或免费跑完批次。后台/暂停返回0；专送活动批次调用本接口抛错，禁止自动配送专送；返回`manualRequired`供切换。广告期间调用方应暂停主角；NPC经营额度不由此模块管理。
- `serialize()/restore()`：纯字符串快照接口，不读取/写入游戏存档，无离线自动收益/时长补算。恢复校验版本、有限数值、唯一ID、候选/票据/活批次引用、单次授权、时长边界。调用方必须事务性保存本模块与正式订单状态，避免两者分别保存造成半提交。

## 待执行验证及限制

已先写 `delivery-game/tests/rewards-v2.test.cjs`，遵循现有 cartoon-art 测试的隔离 TypeScript transpile 约定。覆盖80%临界、价格上下限、重复入口、唯一候选、票据绑定、取消失败/未知/过期/重复回调、独占批次、重新标类攻击、600秒末帧截断、后台暂停冻结、恢复与坏输入。

按用户阶段测试要求，本轮未运行 tests/typecheck/build/游戏/存档。只进行了源码静态阅读；不能宣称测试通过或正式调用链可玩。无真实SDK、平台凭据或广告供给保障；SDK接口并非平台防作弊认证。保存状态是本地数据完整性检查，不能防止攻击者重写整个存档。历史entry和ticket保留用于幂等，后续可由独立迁移策略控制长期体积，不能随意清除后复用ID。真实大厅事件来源、前后台/暂停事件、帧差分、正常订单结算/主角经验/NPC额度补充、自动补给授权和UI倒计时均待V2门面接入。
