# 待执行定向场景（实现前登记，均未运行）

- A1 自动普通批次在一帧结束仍有许可秒数：继续下一批，合计仅扣实际动作秒数；分帧/整帧对比。
- A2 普通批已组未出发→真实自动权益成功→tick：自动选合法方案启动；不接专送。
- A3 主角空闲卸车→tick：NPC仍经营，主角无路线动作；自动余额保留。
- A4 有向边途中取消→同位置重组：路线展示距离只含剩余路段，首15单体力预算同口径。
- A5 自动途中0体力→有授权补给/无授权补给：仅实际推进扣权益；暂停/恢复/重入不补跑。
- A6 部分完成→取消全部剩余→重复交付/重入：已送收入经验、额度只保留一次。

实现后补充缺口与跨owner阻塞，不能把上述case当通过。

## 已确认但本轮未完成（源码缺口）

1. **帧内NPC/主角时点一致性**：`V2DispatchSession.tick:114`先把Fleet推进到nowSeconds；`V2GameSession:43`的路线到达回调默认用该帧nowSeconds结算，补额度在帧尾。静态反例：已有配车NPC、额度0，0→60秒帧内主角第10秒真实完成，当前到60秒才补额度；若分成0→10→60两帧，后50秒可经营。因此帧划分会改变NPC经营进度，并可能改变后续主角完成事件的teamCompletedAfter。需要在真实到达时刻推进NPC旧额度、结算主角、补新额度、再推进帧尾；不应把所有补充额度用于帧起。已报PM，请协调Dispatch/Game的帧内时间推进契约，当前不擅加公开接口。
2. **V1未被覆盖的服务流程**：Route.plan目前固定每单pickup→dropoff，同店多单不合并服务；pickup服务结束即travelling，没有“取餐完成后去下一站”阶段。实现涉及Stop/phase、恢复校验及Runtime/UI继续动作；维持现有快照格式不能假装已完整实现。已报PM；待统一接口方案后继续。
3. **红灯/单趟最多一次变天/食品分类风险**：当前TripState只保存初始天气和普通餐风险，无事件状态或食物品类契约，尚未实现。属于V1明确规则；不是未确认新玩法。需要PM串行协调快照/输入契约后落实，不凭旧报告添加自创规则。
4. **路线预测**：已有路程/总现实时间/总耗能/天气/期限；未生成完整逐单ETA、逐单迟到及餐损预测。现有main策略以主路权重实现，是否充分满足“综合”仍未核验，不能用三项标签代表完整体验。
5. **首15单与长期性能**：真实CityData的短途候选数量、分帧自动循环、每帧全历史JSON克隆及验证成本均未执行验证。无可行短途时允许返回空，不伪造路径或补体力。

## 外部阻塞及已报父PM事实

- **经营范围不等于用户蓝框**：静态读取`assets/resources/map-sample/city.json`顶层只有title/width/height/nodes/roads/buildings/areas/waterways/labels/pois，无dispatchBounds/playBounds/placeCatalogVersion。`V2GameBootstrap.ts:33`调用prepareCity；`PlaceCatalog.ts:9`按建筑密度取核心，`:47`扩大为playBounds，`:98–100`再内缩最多450m得到dispatchBounds；`:129–132`仅追加denseUrbanCatalog，未替换该边界。`V2RouteSession.ts:27`使用传入dispatchBounds||playBounds筛选原节点/路段。这证明当前运行链没有把用户框直接作为范围约束；尚未定量运行测绘，不能捏造越界订单清单。用户蓝框权威是selection.json city.worldBoundsMetresApprox：x[-2652.59,-361.42]，y[-1282.79,867.46]。不改框、不删原节点、不扩经营，交父PM与地图owner协调。
- **五图运行内容**：GameSession只有constructor传入的一份city；购买/选图改变经济mapId，不提供后四图独立CityData。不得把5张卡/5个购买记录视作5图实际可玩。
- **真实SDK**：Bootstrap广告port当前直接抛“广告暂不可用”；本轮不改SDK/RewardSession、不模拟成功。纯逻辑自动路径存在不代表正式广告权益可获得。
- **界面冻结接线**：规划/详情/补给选择面板是否均正确调用Runtime暂停，交功能/UI owner核实；本轮只读。Runtime提供setPaused，单有方法不等于所有入口已接。
- **验证权限**：用户未说阶段完成。待父PM组织集中tests/typecheck/回归、业务交互和存档失败验证；本轮没有运行这些项目。

## 未确认建议（均未实施）

候选池更优的跨单取送排程、变更自动选单策略、自动时长可叠加方式、额外任务赠品数量、经济再平衡都不在本轮自行新增范围。已有V1合并/ETA等明确需求不混入“建议”免责。

## 本轮交付边界

四项确定问题对应源码已写：自动跨批余秒、planned自动启动、无车空闲、原位续送距离。A1–A6仍为待执行案例，源码静读不能代替结果。未运行tests/typecheck/build/部署/游戏/用户存档；不是主循环全面验收或全产品完成。

## U01优先续修追加

Route恢复expected legs有界缓存已写入，不改公开接口/版本；静态入口与边界见implementation末段。新增待执行case：同权威map/计划重复restore命中但每次篡改legs仍拒绝；不同origin/stop/preference不得复用；两个city对象即使mapKey摘要相同也不同缓存；16项LRU淘汰和超长条目不缓存；首次/外来存档进度/凭证校验全部保留。未执行case、路由调用计数或耗时测量，不把该源码修改当U01关闭。

跨模块最小方案已提交cross-module-contract.md。ready、合并服务、新结构兼容、NPC事件时点接口均是提案，未实施，不覆盖前述未完成状态。当前唯一进度保留、禁止玩家重开按baseline最新覆盖执行。
