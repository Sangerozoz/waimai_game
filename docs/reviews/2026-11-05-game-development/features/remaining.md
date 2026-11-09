# 剩余事项与待集中执行用例

本轮未执行以下用例。仅用户明确阶段完成后，由父PM组织隔离环境集中验证。

## 跨owner精确接线请求（已发父PM）

- UI：保持删除账单/启动页重开及确认框，不在任何页恢复玩家reset。Runtime.startOver/restart现仅拒绝兼容调用。
- 广告SDK未配置，继续明确禁用广告并标外部阻塞。接入SDK与凭据须由PM安排真实适配，completed仅来自平台verified reward。
- UI后续专送链：enterLobby返回candidate→requestAd('special', candidate.id, SDK明确TTL)→从snapshot.rewards.candidates查authorized→specialCandidate(id)取得真实路线单→acceptBatch([order])→routeChoices/beginTrip；必须一个专送独占，不能在广告回调直接加金币。
- UI自动链：requestAd('auto',null,SDK明确TTL)，显示snapshot.rewards.autoRemainingSeconds与snapshot.control；已有权益可stopAutomation()/resumeAutomation()。回调异步状态需刷新；tickets pending时显示忙碌，失败/取消/过期不显示获得权益。API和快照不新增字段，rewards当前类型unknown可由UI局部只读类型收窄。
- 当前所有经济command都被Dispatch活动批次锁拦截。是否允许途中买车/招募等由逻辑owner/PM解释V1，运行owner不越权放宽。
- 五张运行地图缺四张真实数据/画面，父PM统筹独立地图范围；不向地图owner追加UI或业务协调。
- 目标奖励表未配置，属设计未定；目标提示不是已实现领取奖励。

## 待集中验证

1. 入口仅显式?v2=1启用；无query走旧工程。UI六页/账单和启动页均无重开动作；兼容startOver/restart调用拒绝且slot/epoch/live均不变。
2. 空slot自然开局；已有slot继续保持人物/现金/路线；startNew遇已有档拒绝。坏JSON、未来组合/嵌套版本保留原字节，不fresh覆盖，不提供清空解法。
3. 仅旧游戏allowlist被废弃，其他产品sentinel不变；唯一快照不备份/自动恢复/迁移。此项只在隔离存储执行，不能碰真实用户档。
4. 双标签第二写者拒绝；epoch变化/slot外部变化/读失败/配额失败冻结且可见报错。旧标签、迟到广告不能写回。坏档/写失败不能显示已完成购买或奖励。
5. acquire等待期间销毁Bootstrap/Runtime，迟到取得锁后释放且不清理/建档；资源load迟到不创建UI/runtime；销毁去掉Game事件监听。
6. 六页真实操作与忙碌/余额不足边界；补给购买/库存/免费休息/自动政策；组批超重、路线选择、到店、服务、逐单结算、取消全部未完成；各项保存失败不发布候选。逻辑数值分别由对应owner提供期望值。
7. 大厅每真实进入一次80%口径，滚动/渲染不重复抽。专送100～150，广告授权后一单独占；正常单不能伪装special ID；广告不直接发金币。
8. SDK同步throw向UI报告失败，failed票据不授权；cancelled/failed/过期/伪造/重复/销毁后回调均不获权益。真实SDK供给仍未配置，不能拿测试adapter声称线上广告完成。
9. 600秒自动权益：停止/恢复不重置、不叠加，剩余保存，暂停/前后台/重载首帧冻结，末帧只用剩余时间，归零保留在途手动接管；自动补给授权/预算不足可见。
10. 五图购买/选择只反映经济状态，核验唯一CityData局限；任务仅提示无赠品。账单今日/七日/累计及批次净额来自真实账本，不二次发奖。

## 尚未消除的风险

U01已缓存提交字节并将普通定时事务合并至约30Hz；每次事务仍全快照克隆/双restore校验/同步保存，长期订单/广告历史增长的性能未测，整批路线重算由逻辑owner继续收口。详见u01-runtime-hot-path.md。Web Locks不支持则阻止打开；当前无跨设备存档。lastError保留最近失败用于显示，后续UI若要求成功后消除旧错误需统一反馈语义。并行owner仍可能更新UI/domain，父PM需在统一构建前复查签名与调用者。无测试/typecheck/构建证据，本报告只交源码与待验证边界。
