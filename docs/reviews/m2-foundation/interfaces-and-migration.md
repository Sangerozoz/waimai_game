# B1 保存与时钟接口

本轮状态：已实现，未测试，待用户说“阶段完成”后集中测试。

## 写入权与提交

`WebWriterLease.acquire()` 用 origin 内 `delivery-county-save-v1:writer` 的 Web Locks 排他锁，`ifAvailable`立即返回；锁持续到组件销毁。未持锁/宿主不支持/拒绝能力时，当前页只读，操作提示关闭其他页后重新打开。后台保留锁以保证恢复不继续旧状态；没有超时抢锁，没有localStorage租约降级。页面退出由浏览器释放，组件销毁主动释放。

`CountySaveStore(storage,key,canWrite)` 默认禁止写。生产由MapSample注入真实锁状态；`save(snapshot, commandId?, expectedRevision=currentRevision)`在持锁范围内检查原主档字节及revision，写主档单个完整JSON提交记录。旧“比较后写”仅做额外冲突探测，原子互斥来自Web Locks。主档单键替换是提交点，backup失败不覆盖主档。写失败保留同一提交ID、expectedRevision和快照，冻结后续动作，重试原内容；成功才递增revision并清pending。lastCommand支持最近成功提交原内容重放；更早ID须由expectedRevision拒绝，不提供无限期命令历史查询。MapSample动作均先检查写权/pending，再执行业务与保存；行驶到人工/结算边界立即提交，成功后才继续。

Web Locks协调所有采用本协议的当前页面；不能向不遵守协议的旧代码或外部写入器授予原子保证。旧标签主档字节失配将被现有冲突保护拒绝；旧版本不能识别新提交记录，保留存档并只读。首次升级应关闭旧版游戏标签。外部绕过锁在比较与写入之间写入的情况不由localStorage提供CAS；本实现不声称能阻止任意旧代码并发写入。

## 保存迁移

继续使用原主键，不清除原进度。外层 `{format:'county-commit',version:1,revision,commandId,snapshot}`，snapshot为JSON字符串。主档/备档均识别裸schema1–4和新包络。第一次成功迁移前将原裸主档保留在`:pre-foundation`；已有值不覆盖。损坏主档留`:corrupt`，有效备份可恢复。新包络未知版本、内部未来schema、未知tripProfile均写保护，不能误当损坏回退覆盖。

业务快照升级schema5：保留schema4单单、handoff与riderAnchor，新增uint32 `randomState`；旧1/2/3/4先按旧校验读入，序列化才升级。旧活动不加tripProfile，继续旧timing、服务与回执校验；旧done不重复结算。新接活动冻结 `tripProfile:'m2-120-service60-v1'`。随机种子由初始存档提交后才开放操作；后续每次随机消费更新持久化状态，读档不重新抽已固定餐损。迁移候选仍走原确定性迁移roll。

## 三时间与后续接口

- 前台现实时间：在线账单仍用真实本地日期时间轴，未乘游戏倍率；后台和待提交期间不记账，恢复不补算冻结区间。
- 游戏行程：道路秒=米×3.6/kmh。新profile道路现实秒=道路秒/120，无15秒封顶；总游戏用时=道路秒+60，期限新普通余量300、新加急120。旧活动保留原期限与旧时钟。
- 表现/服务：2现实秒取餐独立推进，服务消耗60游戏秒；进度中的剩余时间按已完成服务比例计算。`ForegroundClock`提供单调前台间隔，隐藏/恢复重置。`advance(realSeconds,multiplier=1)`只对新profile移动段应用倍率，服务段独立；人工边界截断大dt，不把剩余dt带入下一次确认。倍率允许1–4，B3负责点击积分/衰减、输入与音画；本轮没有点击入口。

B4增量里程/跨午夜分配/补给支出尚未实现，当前DeliveryLedger保留旧结算记里程行为；不能称完整M2账单。仍单单，无体力/NPC/多单。保存迁移、锁争用、失败恢复、时钟与零距离边界均待阶段集中测试，不以本说明代替测试结论。
