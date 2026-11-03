# M2 B1 时间与保存底座开发交付

**已实现，未测试，待用户说“阶段完成”后由PM组织集中测试。** 本轮沿当前checkout开发，未运行测试、回归、typecheck、独立复验或渲染矩阵，未操作4181用户页面/存档，未commit/push。历史测试结果不适用于本轮改动。

## 实际覆盖

- 新增WebWriterLease：使用真实Web Locks持有当前页排他写权，无不可靠的localStorage租约降级。未取得能力/锁时只读，提示关闭其他页后重新打开；销毁/页面退出释放，后台不抢锁。
- CountySaveStore增加version1提交包络、单调revision、commandId/expectedRevision、同一pending快照重试及最近提交去重；保存前校验写权和主档字节。backup先于主档，主档原子单键替换为提交点。pending时UI动作/行驶/在线账单冻结，成功后才继续。
- 新业务快照schema5保留schema4手动取送与道路anchor，并持久化uint32随机状态。原裸档迁移前留`:pre-foundation`，主备恢复及corrupt留存延续；未来包络/内部schema/未知时钟profile写保护。
- 新接订单冻结m2-120-service60-v1：120游戏道路秒/现实秒、取消15秒动画封顶；2现实秒取餐对应60游戏秒，与道路独立；新普通余量300、新加急120。乘数接口仅移动段生效，人工边界继续截断，不跨确认自动消耗余量。
- 单调ForegroundClock只推进前台表现间隔，后台/恢复重置，在线统计继续真实本地日期时间轴。旧schema1–4已有活动无新profile，按原时钟、服务、期限、餐损与done回执继续；新规则仅新接活动生效。已有业务层车辆升级活动守卫保留。

接口和严格迁移细节见interfaces-and-migration.md。Web Locks只互斥遵守该协议的页面；无法承诺任意旧构建/外部写入器都受锁约束。旧标签字节冲突保护继续生效，首次升级应关闭旧游戏标签。没有把localStorage比较后写称作原子CAS。

## 构建与证据

实际执行交付命令 `npm run build:map --prefix delivery-game`，包装退出0；build.log记录2026-10-30 12:23:09 Finished。构建脚本没有附带测试，内部`test -f`仅确认产物文件存在。构建输出仍为delivery-game/build/map-sample（4181所用目录），本轮未打开该页面或请求用户存档。构建不等同于逻辑/迁移/并发验证。

before/与before-sha.json为本轮真实修改前基线；production.patch为本轮差异；final-source-sha.json、build-manifest.json、delivery.json为最终源码/构建指纹和命令结果。本轮新增TripClock.ts、WebWriterLease.ts及Cocos meta，修改OrderBook/CountySnapshot/CountySaveStore/MapSample。

## 剩余与阶段边界

B1本轮已写入上述单写/提交、随机状态、版本化时钟及兼容实现，可靠性仍待阶段集中测试，尤其锁争用、未来档/备份迁移、保存失败重试、旧活动各状态和服务/人工边界。没有宣称并发测试通过、用户体验通过或完整M2完成。

B3后续：点击输入、倍率积分/衰减、地图拖动排除与音画反馈，接入现有移动倍率接口。B4后续：道路增量记账、真实时间轴跨午夜分段、0单有里程及补给支出；本轮DeliveryLedger仍按原结算记录整单里程。多单、体力、NPC和M3未展开。
