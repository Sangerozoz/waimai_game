# Cocos V2第一批经济核心实做（2026-11-04）

已写正式 `delivery-game/assets/scripts/` 中的可复用纯逻辑与显式迁移门面；**未接正式UI，未切换旧OrderBook运行经济，未运行任何测试/typecheck/构建，未打开游戏或真实存档。** 这是分阶段实现记录，不是上线/验收结论。

## 已实现

- `domain/V2EconomyConfig.ts`：最新frontloaded参数JSON完整静态副本，配置ID `frontloaded-2026-11-04-v1`；原参数里的candidate状态保留来源语义。钱包统一整数分，配置价格为金币、入账/扣费转换100倍。
- `domain/V2EconomySession.ts`：实际新档100金币＋独立免费旧车（2kg/收入1），普通接单锁价、按订单ID完成与去重、买10款车、按成功招募顺位报价（30名NPC）、买五图、切图、唯一配车/卸车、单车实例改装1–30与NPC培养1–30。价格足够即可购买，未设等级/地图/时间资格；未虚构额外购买奖励。
- 首车300金币、首NPC120金币；初始车与新车型1分开。推荐路径前10单每单20，买街行后第11–15单24，15单时120可招任意未招募NPC，旧车可复用。前15单经验正常累计但收入经验倍率延后，之后复用现有GameConfig经验等级与收入倍率。
- 升级按累积表差价收费，改装只改变选中实例。作用属性提供 `vehicleEffects`（速度/容量/收入）；NPC培养费用已接，NPC自动经营与服务时间收益尚未实现。
- schema `format:county-v2-economy/version:1`，独立配置版本；恢复校验金额、资产、唯一配车、地图、顺位、经验、报价金额。事务先生成并验证草稿，再提交内存状态；失败不扣钱、不推进编号/招募顺位。
- `map-sample/CountyV2Session.ts`：不依赖新地图的新档入口，以及复用既有 `OrderBook.restore` 的旧档显式迁移与旧途单恢复门面。原始serialized字节保存两处，原schema1–7能表达的钱/经验/完成单数/车辆实例保留，旧车保留原tier属性，不映射为新购街行。未知旧字段保留在原始checkpoint；这不表示未知NPC/地图字段已转为可经营V2资产。
- 旧在途单由原OrderBook继续报价/路由/餐损/结算；提供选路/出发/推进/取餐/开始送餐/取消/结算动作。迁移未完成旧单时锁住V2新单/消费；完成后仅同步原差额一次。原始checkpoint永久保留，续送checkpoint合并保留旧根字段。
- `CountySaveStore.ts`：增加对V2未知schema/config/旧checkpoint未来版本的识别。读取失败发现未来版本则保持既有写保护，提交封套/备份/写入租约机制不改。V2明确使用新key `delivery-county-v2-economy-save-v1`；不写旧key、不自动迁移真实存档。

## 调用方法与真实接入范围

```ts
const app = CountyV2Session.fresh(); // 无CityData依赖
const s = app.economy;
s.acceptOrdinary('v2-order-1');
// 由上层确认真实配送完成后调用；本模块不模拟路线/时间，也不判定到达。
s.completeDelivery('v2-order-1');
// 重复相同id返回上次回执或拒绝；旧id回调不会结算另一活动单。
const snapshot = app.serialize();
// 实际保存应使用现有CountySaveStore + COUNTY_V2_SAVE_KEY + 已有安全写入租约。
```

有金币后调用 `buyVehicle(modelId)` 取得实例ID，`assignVehicle('hero', id)`；先 `assignVehicle('hero', null)` 可卸车，旧车空闲后 `assignVehicle('npc-1', 'starter-1')`。`hireRider('npc-1')` 只招人，不免费送车；全部未招人同成功顺位价格。`buyMap(5)` 不要求先买2–4，但切换仍须已拥有。购买地图只创建资产，不声称地图画面/路网已完成。

旧档：`CountyV2Session.migrate(cityData, serializedLegacy)` 只读解析并返回内存对象；接入层选择何时写新key。`app.legacyActive` 查看旧阶段，按需 `selectLegacyRoute/departLegacy/advanceLegacy/pickupLegacy/deliverLegacy/settleLegacy`；取消用 `cancelLegacy(data, afterPickup)`。保留旧报价，不拿新20金币公式重算迁移订单。旧单完成/取消后经济门面可进行新V2操作。

正式运行调用链仍是 `MapSample -> OrderBook -> CountyRules`，没有被本次替换。新增调用链是未来接入方 `CountyV2Session -> V2EconomySession`，旧单桥接再调用原OrderBook。新单普通经济合同是可实际逐单推进的钱包逻辑，当前未连接原订单列表/餐品/重量/路线到达回调。

## 尚未接入及风险边界

- 旧正式页面仍展示旧价格/资格，`CountyRules`旧评价倍率与单AcceptedDelivery仍在；不得宣称正式UI、现有骑手动画/自动配送已应用新经济。
- 新普通单核心暂为确定基础收入合同，尚未接组单、重量、餐损/超时/评价/体力/补给、专送、广告、额度、NPC在线离线经营；广告/平台SDK和任务去重回调尚未连接。它的完成API须由已确认到达的上层调用，不能用本门面立即完成的示例宣称完成真实配送。
- 主角经验倍率复用原GameConfig；NPC培养效果待经营系统消费，车辆速度/容量效果待路线/订单选择消费。无地图/路由代码改动。
- 旧NPC/地图等不在现存OrderBook schema中的字段仅原文保留；没有假设旧档已存在这些资产，也没销毁其原字段。
- 旧途单桥接方法已按原手动取送动作补齐，但没有运行验证，不能宣称续送通过。
- 订单去重ID保留列表随完成数增长；长期压缩/迁移方案未做。
- 未调用StoragePort、未接触浏览器localStorage；所有迁移须后续在测试授权后验证，再由接入层明确启用。

## 待执行测试

`tests/v2-economy.test.cjs`：10/15单路径、招募顺位与失败原子性、车型表、重载不重奖、旧id回调撞新活动单、未来schema、唯一配车、高价车型/地图无资格限制、单实例升级。

`tests/v2-county-adapter.test.cjs`：旧资金/旧车/未知字段与原始字节保留、旧途单旧价结算一次、未来schema/config写保护。

已写独立入口 `node delivery-game/tests/run-v2.cjs`，编译上述正式纯逻辑及依赖后运行这两组。**本轮未执行它，也未运行现有任何测试或typecheck；没有通过结论。** 后续用户明确阶段完成后才能执行，并按实际失败修复。没有改动其他代理的 `tests/rewards-v2.test.cjs`。
