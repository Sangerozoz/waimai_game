# 主角可恢复车辆：隔离候选交付

2026-11-07，作者B `thr_29f6fcihz6` → PM `thr_4xmqy6fzdm`。本轮是冻结窄规格的实现，独立于此前对A的只读复核。

**PASS范围：隔离候选的防新增行为、历史兼容和相关领域回归。** 新增18项与既有53项合计 **71/71通过，exit 0**；TypeScript 5.8.2严格领域编译通过。尚未集成生产，交PM独立审查和串行集成。已签零额度软锁旧档仍需独立救援设计。

## 候选与最小差分

| 文件 | 基线SHA256 | 候选SHA256 |
|---|---|---|
| `stage/domain/V2EconomySession.ts` | `90b331aea0ecfb05cef239b09b08affc97402336273611eedafd96497fa694a8` | `c16544237e819b6ca03830e07c9723cf78f71d20b7292273f8c016bec8cc539d` |
| `stage/domain/V2FleetSession.ts` | `b34bcdcf9df928b623298f8c865fca3e65f572bc7bd9d1a0c0895398dc5bec61` | `bd22eb20d158dc60880a89cd4911aba0aba2aab16f7c3c44bbc13ab4bf0cda34` |

Economy新增只读标量 `hasRecoverableHeroVehicle`。已拥有车辆中，排除任一NPC当前配车及任一未付NPC合同占车；主角当前车和真正闲置车均可计入，未来购买能力不计入。NPC非空配车在事务草稿变更后检查，失败原子拒绝，文案为“请为主角保留一辆可用车辆”。重复提交危险旧状态也检查。两个直接合同注册入口使用相同查询。

Fleet只在 `startBatches` 签新批前跳过危险状态；原 `advanceTo` 旧批推进和额度扣除未改。restore、快照校验、版本、价表、购买招募和合同结算未修改。两源差分合计+9/-1行，其中配车事务为1行替换。

## TDD与回归证据

| 实际入口命令（同checkout） | 编译exit | 测试/操作exit | 实际结果 | 原始证据 |
|---|---:|---:|---|---|
| `node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/run-stage.cjs red` | 0 | 1 | 最小RED：1项，0通过/1失败，`Missing expected exception` | `red.log`、`red-receipt.json` |
| `node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/run-stage.cjs capture-history` | 0 | 0 | 原生产代码通过公开动作生成kg/slots合法历史夹具 | `historical-fixtures.json`、`capture-history-receipt.json` |
| `node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/run-stage.cjs red red-boundaries` | 0 | 1 | 边界RED：18项，1通过/17失败 | `red-boundaries.log`、`red-boundaries-receipt.json` |
| `node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/run-stage.cjs green` | 0 | 0 | GREEN：71项，71通过/0失败/0跳过 | `green.log`、`green-receipt.json` |
| `node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/run-stage.cjs green green-root-fix` | 0 | 0 | ROOT修正后的最终GREEN：71项，71通过/0失败/0跳过 | `green-root-fix.log`、`green-root-fix-receipt.json` |

边界RED同时包含未拒绝非法配车/直接签约、Fleet继续签约/耗额度，以及尚不存在查询的断言失败；唯一通过项是已签零额度旧档保持可读且不隐式救援。不能把全部17项写成同一种失败。18项边界测试在RED和GREEN间SHA均为 `e5aca2fd7ea702bb8ca92e30cde313339910ecf4f5fd6a7c3e6cf229b06c667e`，未为GREEN放宽。最初单用例后来扩展为18项，原首轮测试SHA仍留在原收据，首轮runner保存在 `runner-red-baseline.cjs`；没有伪造旧测试文件版本。

PM审查后仅修正测试ROOT默认值为 `path.resolve(__dirname,'../../..')`，适配集成目标 `delivery-game/tests/product-regression-1106/hero-car-reserve.test.cjs`。最终测试SHA为 **`23819a18703548df6970b7e4db6e84227f1f208220bacd7896cdf830711dbf13`**。最终GREEN使用相同18项断言；审计可将这唯一一行还原于内存并核对原GREEN测试SHA。两份TS候选SHA未变。stage runner继续显式传ROOT；标准默认入口的整体执行仍待PM集成，不能把此次隔离GREEN写成已运行完整默认回归。

既有测试逐字保留：`v2-economy.test.cjs` 7项、`v2-fleet.test.cjs` 10项、`v2-dispatch.test.cjs` 10项、`product-regression-1106/current-contract.test.cjs` 26项，共53项。包括10/15单精确预算、自由购买/招募、旧kg合同占车与旧价、slots锁定条款、在线/离线一致性、时钟与存档原子性。旧测试部分使用原有富资金夹具；本轮新增缺陷与历史路径未借此证明合法可达性。

编译由runner调用Creator自带TypeScript API，ES2020/CommonJS、`strict:true`、`noEmitOnError:true`，依赖与候选只编译进唯一系统scratch；不是Cocos产品构建或全项目typecheck。精确入口、编译选项、37项实际编译源SHA、子测试命令和exit均在各原始收据。实际本地Node可执行文件为 `/Users/sanger/.hermes/node/bin/node`；这是本机Node路径，没有调用Hermes Agent或切换Provider。

## 真实行为与历史来源

- 当前slots首单100→120金币、招募120后余额0：主角卸车仍允许；给NPC最后可恢复车被原子拒绝，装回后真实city的Game/Dispatch公开路径可再送一单获得20金币。
- kg/slots拟议配车均检查所有NPC当前占用，现金足够购买不能充当备用。确有另一辆闲置车时允许，主角无需一直装备。
- kg/slots两个直接注册入口均拒绝危险旧状态且序列化状态不变；自动签批skip不抛异常、不耗无工作额度、不发钱，高水位正常推进。
- 旧合同保留车辆即使已卸下，也不能算备用或交给主角；恢复动作可以卸NPC车并装回真正空闲车。
- 合法带剩余额度旧批照常推进：kg旧首批结算20金币后余90000ms；slots旧首批两单结算40金币后余45000ms；均不续签危险新批，不改旧条款。
- PM真实Game未签危险夹具字节往返后tick不签批，原60000ms额度和余额0保持，卸NPC后可归还主角。PM已签零额度夹具仍字节往返；推进一小时不补钱/额度、不取消旧批，旧车继续保留，**仍未获救援**。

PM输入：`docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json` 的 `fixtures.beforeNPCSigning` / `fixtures.signedZeroQuota`。本轮只读使用，没有重跑会写PM目录的复现脚本。

本轮 `historical-fixtures.json` SHA256：`d9f151e35936a8cf1d99f17c6a1adad9eab782af1a7d64b1f6614b3af354e675`。原生产编译输出分别创建kg/slots会话，公开完成3单、招募、卸主角车、给NPC唯一车，再推进1000ms保存；资金从10000→12000→14000→16000→4000分，额度从0→60000→120000→180000→179000ms。另用30次公开完成所得买车/招募，生成“已卸旧合同车＋另NPC当前配车”组合。原runner中的公开动作、生成收据及保存后的restore往返均保留，没有改快照注资或注额度。

## 输入保护、授权与交回

五次编译/运行均验证292项保护文件及A的36项输入无漂移；首个RED前、最终GREEN前/后与最终只读读回一致。保护包括全部生产脚本、A36、A原manifest列出的34产物及manifest、旧B证据、相关旧测试、PM夹具和本轮spec/plan。A新增长期模型输出不冒充原产物保护范围。五个自建scratch逐个确认已精确删除；没有清理其他dirty/untracked文件。

`authorization.json`保存实际线程/环境/checkout和Provider `codex`读回。`bb thread options`实际返回 `options:null`，未暴露模型、effort或编辑权限字段；`ccs-sanger/gpt-6.1-sol` / max依据PM冻结派工，不伪称原生字段已独立确认。编辑只发生在授权写集，未改路由、全局设置或权限。

总收据为 `receipt.json`，原始RED/GREEN不覆盖。只读复核入口为 `node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/verify-receipt.cjs`。PM若需复现候选，用新的日志tag：`node docs/reviews/2026-11-06-product-testing/b/softlock-prevention-1107/run-stage.cjs green pm-review`，避免覆盖作者原始日志。

PM集成还需一项明确的测试基础设施改动：现有 `delivery-game/tests/run-v2.cjs` 编译roots未含 `PlaceCatalog.ts`；新测试的真实city路径需要 `prepareCity`，PM将加入 `map-sample/PlaceCatalog.ts`。本轮stage runner已有该entry。作者没有修改生产runner；PM须按原224保护清单另记其前后SHA及批准原因，不能将后续该差分称为零漂移。

本轮交回后作者停止编辑。**PENDING_PM**：独立审查、等待A输入使用结束、两源与测试串行集成、上述runner依赖补全、完整 `run-v2` / 项目typecheck及发布门禁。未运行浏览器或真实用户档，未重做旧B整单，未构建/部署产品，未commit/push。局部通过不代表已签软锁旧档救援、长期二八、五地图体验、广告SDK、真机FPS或98%验收。
