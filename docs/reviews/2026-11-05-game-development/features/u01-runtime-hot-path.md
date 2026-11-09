# U01 运行热路径：静态诊断与最小修改

2026-11-05，功能owner thr_f2cxhbkw45。已读正式V1§4与feedback-ledger U01。**源码已写，未测耗时/帧率/行为，U01不结案。** 未运行tests/typecheck/回归/游戏/存档，未构建或部署。此次只修改V2RuntimeController.ts及features报告。

## 确定证据与推断边界

旧路径update → drive → mutate，每次外层工作：

1. live.serialize → GameSession.restore，生成候选。
2. candidate.tick → Dispatch.tick → 内部transact/恢复校验/Fleet事务。
3. candidate.serialize → GameSession.restore，验证待保存候选。
4. live.serialize，比较前后字节 → Store.commit → live=candidate。

因此仅Runtime外层每次3次整局serialize、2次整局restore；每个tick都增frame.sequence/更新时间，即使暂停也会改变快照，从而同步setItem唯一slot。ready原先在drive/mutate/commit重复检查，均可能读epoch。领域内部序列化次数未精确枚举，不将外层次数当总成本。

另见V2RouteSession.restore：非idle/planned会调用makeLegs(preference)重算整批路由并JSON比较。Runtime两次恢复至少产生两轮全部legs重算；PreparedMap WeakMap只复用router/几何，未缓存makeLegs结果。这是确定的计算路径，不是已测毫秒瓶颈。已发父PM，由逻辑owner处理其写集，不能删恢复安全检查冒充优化。

用户实际跳站/卡顿可与上述主线程工作、UI显示节流及取餐后缺主动继续契约共同相关；无性能轨迹不能认定唯一根因。真实40游戏秒/现实秒换算保持，未调慢车辆。

## 已实施最小改进

- 私有committed保存最近一次成功提交的完整字符串，下一事务从它恢复，比较也用它。Runtime外层serialize由3次减为1次；两次restore完整保留。quoteCandidates也使用同一已提交快照，预览仍是独立draft，未接受真实单。
- publishedAtSeconds记录最近一次成功事务采样的绝对时钟。普通update仅在间隔至少1/30秒时drive，将高帧率渲染回调合并。命令不受此门限；setPaused、onHide、onShow均force立即走原事务。时钟倒退不会被门限无限阻塞。
- 不累积帧delta、不截断迟到帧、不丢掉现实时间、不将多个固定小步循环补跑。Session仍收到完整nowSeconds并负责沿原路、停点、服务、后台冻结和NPC有限额度。
- 每个发布状态仍先restore校验再commit，写入成功后同时更新cache与live；失败cache/live保持原状态，Store原先冻结行为保留。没有先发布运动、数秒后补存这种保存窗口。
- Store文件本次未修改。writer/epoch/expected、单slot、坏档防覆盖与reset拒绝保持；destroy清理committed引用。

在60渲染回调/秒且事务耗时低于门限的理想情况下，普通时钟事务约至30次/秒；这只是调度上限说明，**不是实测提升比例或稳定30FPS承诺**。若单次事务本身很慢，此门限不能解决长帧补走，需逻辑层路由缓存及UI逐帧位置展示共同完成。

## 跨owner边界

公开API与快照结构/版本未变。已向父PM报告最小方案后落实。父PM需协调：

- 逻辑owner缓存固定几何/origin/stops/preference的已验证路线或给出受控内存fork方案；首次外部存档验证不可弱化，缓存不可错配城市或路线。
- 正式V1§4同店合并服务、取完主动“去下一站/去配送”尚在逻辑/UI契约中，Runtime不擅自发明新动作API。
- E03长/细帧NPC补额度事件时点必须由逻辑owner继续核验；降低调用频率不能宣称修复事件时点。
- UI每帧显示位置、跟随与低频文字刷新由UI owner负责；本角色未改UI/CityMap。

## 待集中验证

1. 用隔离fixture/明确授权的性能场景，对比每秒drive事务/restore/makeLegs/commit数、耗时分位与长任务；包括起步单、多单、30NPC/长账本。不得读取真实用户档做profile。
2. 固定绝对时钟轨迹对比细帧/稀帧/命令穿插：里程、期限、耗能、风险、金币、逐单ID集合一致；暂停/hide/show跨门限不补跑。
3. beginTrip/pickup/停止恢复/广告回调立即提交，不等1/30秒；setPaused(true)与恢复都记录状态边沿。
4. commit/epoch/slot冲突失败不发布候选与缓存；随后SDK回调不能绕冻结；重载只从最后成功slot恢复。
5. 取完服务后等待主动继续、同店合并与到点停下连续画面，需逻辑/UI最终契约到位再验。此项当前不能通过静态改动勾选。
