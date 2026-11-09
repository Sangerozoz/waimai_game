# V2第四批：真实路线体力、补给与交付结算

状态：源码接入、静态阅读完成；未运行tests、typecheck、构建、游戏、SDK或用户存档。不是阶段完成或运行验证通过。

依据：implementation-baseline.md、正式V1第5/6/7/12节和最新二八曲线。仅修改V2纯逻辑/组合路线与其待执行验证；旧MapSample、地图和runtime/UI由其他代理负责。

## 已写入

- V2TripRules保存100上限体力、初始80评价、行程钟、初始天气、seed/每单固定抽值/严重度、已取/交付及累积风险、补给动作进度、实际支出和自动补给累计预算。
- 道路逐真实edge推进，体力按当前地图2/2/3/3/4每公里扣一次，不乘订单数；耗尽返回精确已走比例、真实道路坐标，不负体力。取餐1、交付1，由路线serviceCharged门闩保存，跨帧/重进不重复扣。未扣费而体力不足的服务点仍可补给；已经确认的服务动作不能插入补给。
- 原地水1币/20/1实秒/30游戏秒、泡面3币/70/3实秒/120游戏秒；活动批次休息10实秒/20/600，无批次20实秒恢复满。启动扣款一次、保存进度、完成后恢复封顶；满体力拒绝且不收费，取消不退费。暂停/后台不推进主角行程或动作，NPC独立经营时钟保留。
- 自动默认不花金币。configureAutoSupply({enabled,budgetCents,kind})显式授权并限制累计开销，重新配置不清spentCents，低于已花额度拒绝。blocked且无预算/余额时保留auto权益，NPC时钟继续；自动权益仅扣实际移动/服务/补给秒数，耗尽体力后的帧尾不扣。
- 首15完成前使用真实短途候选：每单独立最快完整取送<=1000m，组合实际选路<=1000m×单数且实际总路程/服务耗能不超过现有体力；拒绝远程伪教学。自动组合按可行路线选择，必要减少组合单数。15单在最耗能地图的保守上界60道路+30取送=90体力，不免费加满、不篡改原路。取消重复绕行或自行提前花钱不属于推荐收支保证。实际CityData是否存在足够短途尚未运行验证，可能无可用候选，不能宣称已达到20分钟小队目标。
- 初始天气晴/雨/恶劣按地图概率、道路时间1/1.1/1.25，并在路线选项显示。期限从出发地独立最快真实取送+服务90游戏秒+余量300建立并保存；同批共享行程钟。当前普通餐品风险按已取未送实际里程/独立持餐里程累积，固定一次抽值比较，封顶25%。保护单无迟到/餐损惩罚。
- 逐单交付：迟到95/85/75%，餐损90/75/50%，各一次相乘后最终按分取整；评价变化+1或迟到/餐损各-1/-3/-5、合计损失封顶10、范围20–100，评价不乘收入。专送锁定100–150基础报价也只扣相应损失，不叠车辆/经验倍率。
- 签约quote.incomeCents保持base；receipt另存baseIncomeCents/lateGameSeconds/damage/lateRetain/damageRetain/ratingDelta及最终incomeCents。Dispatch验证从锁定base与受限outcome重新核算，避免旧相等校验拒绝合法扣减；旧无结果receipt只允许与base相同，旧默认调用仍准时完好。已完成交付重试不重复结算。
- 组合档version=2显式包含tripState；未知未来版本拒绝。旧version=1仅无活动批次且idle/finished安全初始化，不为在途单虚构体力/风险；旧在途拒绝等待显式迁移。路线paid-service进度与trip已取/已送、dispatch结算对应校验。

## 接口

V2GameSession.tripState；supply('water'|'noodles'|'rest')；configureAutoSupply({enabled,budgetCents,kind:'water'|'noodles'})。action提供elapsedSeconds/durationSeconds/costCents等；自动策略spentCents永久累计，不因页面或开关清零。V2DispatchSession.tick默认行为兼容；组合owner使用deferAuto选项，再consumeAutomaticProgress扣实际进度。

## 明确未完成

库存与任务赠品消费、其它饮食种类、食品fragility分类、红灯、单趟一次变天、同商家连续取餐合并及更优跨单共享取送顺序未实现。当前路线仍为逐单pickup/dropoff顺序，因此不能声称完整V1三策略调度/合并服务系统已完成。风险仅普通餐品首版模型；路线UI显示期限而未完成逐单ETA/完整风险预测。升级车辆对游戏钟/期限的进一步统一校准也仍需集中验证。未部署，不把代码存在当成可运行验收。

## 待执行验证

真实用例已写delivery-game/tests/v2-trip-rules.test.cjs，纳入tests/run-v2.cjs；旧route用例适配由组合owner推进和未来版本号。覆盖精确耗尽截断、补给跨恢复进度、base/final损失与幂等入账、零体力服务可补给、自动blocked保留权益、预算不重置、旧在途与未来版本拒绝。补充人工场景清单trip-rules-pending-tests.md保留，不能替代运行。任何用例均未执行。

静态复查见trip-static-review.md；已修复服务点零体力无法补给及自动停住仍消费权益两个P1，并经独立代理定向阅读复核。静态阅读不保证无编译/集成错误。
