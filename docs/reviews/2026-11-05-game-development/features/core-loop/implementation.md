# 核心配送闭环B：Runtime/UI实施

状态：**两份源码已编辑，未测试、未typecheck、未构建/部署；依赖逻辑owner交齐后由父PM统一集成。** 本文只记录接线及静态调用审阅，不代表配送闭环功能通过或用户验收。

## 写集与实际落盘

- `delivery-game/assets/scripts/map-sample/V2RuntimeController.ts`
- `delivery-game/assets/scripts/map-sample/V2GameUI.ts`
- 本目录 `implementation.md`、`remaining.md`。

只用patch编辑，保留同checkout已有dirty/untracked。未写Route/Game/TripRules/Store/Bootstrap/CityMap/ApprovedSkin/经济/地图/资源/公共清单；未commit/push/stash/worktree。

## 精确接口与事务

Runtime公开入口：

```ts
continueTrip(): void {
    this.mutate(session => {
        this.requireForegroundTripCommand();
        session.continueTrip();
    });
}
```

- 源码锚点：`V2RuntimeController.ts:100–117`（原mutate），`:139–152`（前台门禁及三种路线命令）。保留从committed字节restore候选→同步绝对now tick→调用Game→serialize→再次restore完整校验→store.commit→publish；没有直接操作Route字段，也没有在命令后补tick过去停留秒数。
- `continueTrip`与`beginTrip/pickup`都经过mutate，命令不受普通drive约30Hz合并限制。失败不发布候选；写者检查、同步保存及错误通道保持原实现。
- **静态发现并最小修复：** 原mutate把foreground/paused传给tick，只阻止时间推进，不能阻止随后显式`beginTrip/pickup`改变阶段。现三种路线命令在候选内统一拒绝后台调用，错误为“后台不能操作配送，请回到游戏后继续”。未改广告异步回调或其他命令的既有权限，不能据此声称所有Runtime命令均禁止后台调用。
- 暂停仍是主角时钟门禁，不盲目禁止显式命令：订单详情本来就暂停，路线选择、取餐及继续必须可以在详情确认，然后回首页计时。`setPaused`前后强制drive和hide/show强制drive保留；Game/Dispatch以当前和前一帧前台/暂停标志判定时间，恢复首帧不补跑。对应Runtime锚点`:181–200`。
- ready自身不设置Runtime暂停；首页原`setPaused(supplyOpen || page !== '首页')`保持。因此ready等待不冻结全局经营，主角不推进的领域保证由另一owner实现。

依赖的冻结契约（未在B写集中伪实现）：

```ts
Game.continueTrip(): void;
Route.continueTrip(): void;
Stop = { orderId: string; orderIds: string[]; kind: 'pickup' | 'dropoff'; node: string };
// Route snapshot v2 / Game组合v4 / TripRules v2
// ready: cursor指向下一站、人物仍在刚取完的商家、legSeconds/serviceSeconds均0。
```

UI的`RouteState`直接从`V2RuntimeController['routeSnapshot']`推导，不以any或本地新状态机遮掩领域类型尚未交齐。`orderIds`缺失/空时仅展示回退`[orderId]`；不按同名、距离或菜图自行合并。

## 各phase可达展示与动作

首页原有配送双按钮与订单详情共用`tripControl/tripButton`（`V2GameUI.ts:271–286`）；不是在UI推进人物或cursor。

| phase | 展示/有效主动作 | 其他既有边界 |
|---|---|---|
| idle | 暂无配送；无取餐/继续提交 | 原大厅组单、补给入口保持 |
| planned | 请先选择路线；详情路线卡经`beginTrip(preference)`出发 | 回地图不自动选路；原补给/取消未完成单入口保持 |
| travelling | 配送中，取餐/继续按钮禁用；沿权威position显示 | 查看详情/补给选择冻结主角，不重选路线 |
| pickup | 到店取餐；多人组显示真实份数；调用Runtime.pickup后回首页 | 有补给action则禁取餐；不在本地标picked |
| service | 取餐或交付的真实`serviceSeconds / 2或1秒`；按钮禁用 | 不重复提交；原补给页service禁用规则及取消入口保持；已扣点服务即使体力到0也显示真实服务进度 |
| ready | 去下一站；下一Stop为dropoff显示去配送；调用Runtime.continueTrip后回首页 | 返回地图本身不继续；无补给action才可继续；原补给/取消/查看暂停规则保持 |
| finished | 本批已完成，不提供取餐/继续动作 | 本批关闭后回原大厅；不二次结算/发奖 |

补给/休息action优先展示其真实elapsed/duration并禁用取餐/继续。顾客交付仍由领域自动处理，无新增交付确认。

## 共享取餐与刷新

- `pickupGroup`（UI`:264–270`）在pickup/service等阶段读当前Stop；ready读`cursor-1`的已完成pickup Stop，不误认下一顾客为商家。商家名来自Route订单的`pickupName`，份数来自该Stop的`orderIds.length`。
- 首页`:156–160`在原余单/路线按钮内显示真实商家、份数与详情入口，右侧复用同一阶段动作。不恢复已删除的地图悬浮行程/结算文字卡。
- 订单详情`:499–554`显示商家/共享份数；组内所有订单同显到店待取、取餐服务中、已取餐待发，送达回执仍逐单。已有餐图映射、报价、真实期限及收入展示保留，没有新编菜品/ETA/收入字段或合并收据。
- UI`:613`的重建key加入tripId/cursor/serviceCharged、补给action起止、blocked、逐单picked/delivered；同一phase不同Stop或共享组成员变更不再仅靠phase/batchIds漏刷。进度秒不入key，只更新真实文字，避免服务中每帧重建。
- UI`:590–605`每帧读取真实route.position仍在0.5秒HUD节流之前；captureView→setRoutes→restoreView保follow/zoom/offset，首次出发locate(false)不变。滚动稳定key及记录/还原偏移实现未改。

## 四个顶部标题删除的源码锚点

统一锚点`V2GameUI.render():98–101`：顶部文本仅在补给、订单大厅或骑手配置车辆时创建，不再以`this.page`无条件生成标题。没有整体上移/重构布局。

| 页面 | 顶部标题删除条件/锚点 | 保留 |
|---|---|---|
| 骑手 | `page === '骑手' && !configureRider`不进入`:98`标题分支 | 配置车辆子页标题、金币、卡片、底栏入口 |
| 车辆 | `page === '车辆'`不进入`:98`标题分支 | 金币、预览/车型选择/购买功能及底栏入口 |
| 地图 | `page === '地图'`不进入`:98`标题分支 | 金币、五地图卡名/状态/购买选择及底栏入口 |
| 账单 | `page === '账单'`不进入`:98`标题分支 | 金币金额、账单模块/图表及底栏入口 |

首页完整HUD`:93–97`、金币栏`:102–107`、订单大厅标题`:100`及导航入口保持。父PM已落实的订单地址末端pin移除、KG随餐名、订单¥、时间偏移、地图“未解锁”、账单金币图片移除均未回退。骑手新卡稿、万元近似取整未实施，未改经济数值或资源。

## 证据与限制

实际证据为read_file/search_files的源码调用链和patch落盘结果。patch工具因检测到项目tsconfig自动跳过逐文件tsc，**没有语法/typecheck通过结论**，也没有手动补跑任何检查命令。初次及交付前目标git status仍显示两源码为既有untracked；未以git add或覆盖方式处理。具体未执行case和跨owner依赖见`remaining.md`。
## PM集成追加（尚未运行）

- 回收上一轮独立审查的真实P1：跨自动批次同phase/cursor会复用旧路线。父PM在update的routeViewKey加tripId，lastRouteTripId显式识别新批出发；同批保留原captureView/restoreView与用户拖动。
- 父PM静态追到补给死路：Game.supply仅禁止已扣点服务，但UI原来禁止全部service。现UI只在serviceCharged=true时锁补给，未扣点低体力服务可选补给/免费休息；tripControl低体力禁取餐/继续并显示补给提示，已扣点服务可继续完成。
- B规格已由父PM实际源码读回；全新独立质量审查sa-0-18581804已派发，无source运行/构建/用户存档通过结论。
