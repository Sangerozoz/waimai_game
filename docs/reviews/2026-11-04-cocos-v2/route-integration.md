# V2真实路线与组合存档接入（源码，未验证）

新增 `V2RouteSession.ts`、`V2GameSession.ts` 与meta；Runtime控制器已统一调用GameSession，旧OrderBook/原CityData/美术均未修改。UI代理消费统一API，实际场景挂载由该代理交接。

RouteSession复用RoadRouter有向原路，取送POI仅在operatingPOIs及dispatchBounds/playBounds内；过滤外节点时切断连续路段，不连接断点造捷径。普通候选整数1/2/3kg只展示单车能装的重量，接单时总重仍经Dispatch验证；连通性先筛选，plan逐站验证整批，逐单先取后送。专送候选只绑定真实广告候选ID，不伪造授权。fast/main/smooth实际路径相同则合并aliases，不造三条不同路线。

道路复用既有40游戏秒/现实秒比例，再乘车辆速度效果；服务仍为现实秒，快进道路不会缩短服务。快照显式timeProfile=road40-service2-1-v1。手动真实时钟行驶到取货点停住，`pickup()`后取货服务2秒，再道路行驶、送货服务1秒，送完产生与trip/order/stop绑定的arrivalToken。自动权益使用许可秒数、按当前车辆速度推进，自动取货；仅idle/finished且无活批时自动选普通候选，容量内组批后出发，完成后下一tick继续，不接专送。末帧只有剩余权益秒数，超出的时间不补手动行程。无广告成功模拟；真实SDK仍外部注入。Dispatch奖励只认RouteSession已经产生的到达凭证，tick会逐个消费；重复凭证不重复入账。

Runtime.configure现在需要 `{city,ads,nowSeconds,storage?,writer?}`，删除外部delivery/advanceAutoRoute空port。公开 `normalCandidates`、`specialCandidate`、`acceptBatch`、`routeChoices`、`beginTrip`、`pickup`；`snapshot`仍Dispatch读模型，`routeSnapshot`包含phase、position、orders、stops、legs/cursor、legSeconds、serviceSeconds、picked、arrivals。无路线选择阶段时routeChoices返回空数组。

组合格式county-v2-game/version1保存dispatch和完整route checkpoint，包含原图身份、订单、真实段进度/服务/位置锚点、余站、到达凭证、单号与trip序列。控制器先克隆组合候选，tick和命令、路线推进、逐单结算全部在保存前发生，同一CountySaveStore提交成功后才发布新状态，消除“预算先扣持久化，路线另回调”窗口。取消中途保留有向段位置，下批从该段剩余部分继续，不瞬移；恢复首帧不追赶主角离线行程。

原runtime仅Dispatch存档拒绝自动升级，因为无法还原真实位置/取货状态；需要后续显式迁移流程，不覆盖旧字节。Store继续复用独立key、备份、写租约和冲突保护。本轮未读写任何真实存档。

同时修复广告SDK失联：RewardSession.expirePending(now)在Dispatch.tick清理超时pending，过期当帧仍冻结，下一帧恢复；auto成功回调若活批为专送只保存600秒权益并保持manual，避免组合验证回滚导致pending卡死。

待执行 `tests/v2-route.test.cjs` 及Dispatch新增两项已注册run-v2入口；覆盖原路/蓝框、合法容量与多单、取送顺序、伪凭证拒绝、位置/服务恢复、取消不瞬移、未知版本/错图/伪造进度拒绝、自动循环与离线冻结、TTL和专送广告交错。**用户未宣告阶段完成，本轮未运行tests/typecheck/build/游戏，未操作实际存档。仅静态阅读，不能声称通过。**

限制：服务时间为V1取2送1；天气/风险/餐损/迟到/体力/补给尚未接路线结算，当前收入为锁价正常完成报价。主角有真实路由，NPC仍为既有经营模型，未实现30名可见骑手。自动循环采用固定POI序列和普通容量贪心，非已校准平衡/任务供给。静态原图Router/合法POI/边缓存于WeakMap，仅同一个不可变CityData对象复用；mapKey使用长度+双32位非安全摘要，不每帧写完整几何。每帧全历史克隆和序列化校验的长期性能仍未测，不宣称适于长期30人运行。实际广告平台认证、真实SDK恢复重连、旧runtime路线迁移、集中引擎测试与存档失败验证仍待后续。组合校验是数据一致性检查，不是抗恶意存档签名。
