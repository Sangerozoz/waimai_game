# FOOD-RISK-IMPLEMENT-A-1106

状态：**已按approved-contract实际修改A独占三源，未运行阶段案例、未构建，待PM规格与独立质量审查。交回即释放本段写lease，不继承临时Accept Edits，不自行改权限。**

先读同目录approved-contract.md并核对三源SHA，无漂移。B独占GameUI；本报告不把B的在途源码变化算作本批保护输入漂移，也不声称已核验B的UI接线或画面。

## 稳定API与实际变更

- FoodCatalog保持原50项及两个旧helper全文不变，仅加类型依赖与`foodForV2Order`/`foodPresentationById`。前者精确复用旧UI UTF-16 FNV hash及现50项顺序，后者唯一ID严格查找；均返回新标量对象，不泄漏原目录引用，不返回unitWeightKg、不调用抽样helper。不复制50项表。
- Trip导出`V2FoodRiskContract`、`V2FoodRiskById`、`parseV2FoodRisk`及版本判别的`V2TripState`。parse要求恰好三个own enumerable字段，拒绝额外键/符号、null/undefined、数组、未知版本/分类，返回副本。结构验证不能冒充Game的目录真实性绑定。
- `begin(...,foodById?)`以`arguments.length>=4`识别真正提供第四参，因此显式undefined/null均拒绝；真正三参仅对现Trip2保留旧行为，Trip3不能省略降级。完整字段/ID集合/own-key/元数据验证均在状态修改和roll之前；上下文规范化成null-prototype表，所有订单一一对应。
- Game候选返回`V2FoodOffer`，含canonical food。accept保留原合法路线/经营/真实重量/safe链，显式投影七个RouteOrder字段，不把caller风险字段或候选food传入Route/Dispatch。输入food真正缺失时仍生成新合同；显式或继承food不能绕过parse/规范身份匹配。canonical身份由Game按合法订单id重新确定，不采纳caller的risk/draw/fragility作为结果。
- 生产Game始终传完整foodById，新批必须生成Trip3才可发布。原Dispatch容量/报价/合同事务仍在最终赋值前执行，失败不发布局部Trip/Route；没有改变ordinary-effort-v1、实际weightKg或专送/NPC价格。
- 新food随Trip3当前订单保存；新批/取消按原生命周期替换或清空。没有追写历史Dispatch/receipt，不承诺永久历史食品详情。

## 格式及metadata边界

| 输入/场景 | 处理 |
| --- | --- |
| Game1无Trip、Game2/Trip1、Game3/Trip2、Game4/Trip2 | 按原版本配对及全部原完整校验；仅沿用既有Trip1→2/Route1→2转换；旧当前批不补food、不升食品规则 |
| 旧Trip1/2中food真正缺失 | 保持normal规则，G/D/risk/draw/severityDraw/seed/action/已到账不改 |
| 旧Trip1/2显式food为null/undefined/对象，或继承food | 拒绝保留字段污染，不静默剥离；在clone前核查 |
| Game5/Trip3/Route2 | 每单必须own enumerable完整food，先结构校验，全部原组合/legs校验后再按实际订单ID核验canonical值 |
| Game4+Trip3、Game5+Trip2、未知Game/Trip/food版本 | 拒绝；不按缺字段猜测legacy、不把新格式缺失food默置normal |
| Trip3 food缺失/null/undefined/额外键/未知ID或分类不符 | 拒绝；clone前检查presence，clone后再次结构检查，Game查规范身份 |
| 第四参缺项/多项/重复订单ID/继承上下文/显式undefined/null | 在写状态或roll之前拒绝；特殊字符串ID使用null-prototype/own-key，不会落入__proto__/constructor原型回退 |
| 原三参领域begin | Trip2继续旧normal与原随机调用；已有Trip3不得回落旧规则 |
| 合法旧批结束/取消后第一次生产新accept | 仅这次新批生成Trip3/Game5；旧历史记录与到账不迁移/重结算 |

serialize只读取一次Trip快照：Trip2写Game4，Trip3写Game5，Route2/Dispatch/经济config/slot不变。fresh空状态仍可为Trip2；Game1—4恢复不会用提前改版本的方式借新门槛。旧reader不支持Game5，现Store失败保留原slot，不提供清档兜底；需由PM统一新reader/writer及B的UI候选发布。

## 已保留的旧完整验证：纯文本证据

1. Trip从`const legacy=`至旧`t.s=s`之前的原完整验证块，剔除新增的Trip3末尾food检查后，与基线逐字相同。包括旧Trip1转换、所有数值/订单/draw/risk/库存守恒/奖励/预算/账目/动作参数检查，未删减或放宽。
2. Game restore只扩展允许Game5、Trip3及其对应Route2/grouped条件，并追加仅Game5的canonical核验。把这些已批准新格式扩展反向还原后，完整旧restore与基线逐字相同。原版本1在途拒绝、原版本配对、服务动作互斥、订单/取送/arrival/凭证、补给解锁、ordinaryPricing路程核对及权威legs门槛全部保留；旧route规范化顺序不变。
3. Game从routeChoices注释起到restore之前整段与基线字节相同：ETA全部字段/公式、P0 motion、ready、planned补给布尔门禁、NPC真实事件时点/双门禁调用、真实used/自动额度/后台/暂停/rebase均未改。
4. Trip的roll实现、原天气生成整行、原逐单deadline/risk/draw/severity/heldMetres/safe构造式保持；begin中的roll调用点仍是原一处天气与逐单两处。食品选择不消耗该随机序列。原choose到travel前的服务/补给段、serviceTime到restore前的outcome/评价/取消段字节相同；没有重建D或回滚旧planned正G。
5. FoodCatalog除新增type import/helper外，原目录和旧helper全文逐字相同。Route、Runtime、RuntimeStore、Dispatch、Economy、EconomyConfig、SupplyCatalog、GameConfig、V1参数JSON及approved-contract在本次前后SHA一致。B的UI是另一个授权写集，不做错误的旧SHA锁定。

## 实际风险边界

Trip2仍取原normal三值；Trip3逐单按已冻结fragility取fast/main/smooth：fragile .12/.06/.02，normal .06/.03/.01，durable .02/.01/0。新增字面基表已用纯文本解析对照冻结参数JSON的百分数除100，逐项一致。

原累积运算顺序保留：`min(.25,oldRisk+(base*mapFactor+weatherExtra)*metres*fraction/heldMetres)`。地图系数、雨/恶劣加值、体力截断、仅已取未送非safe、一次保存draw/severity及outcome/收入保留率不变。不使用旧GameConfig.ROUTES，不追加每帧天气概率，不启用红灯/途中变天或方案餐损概率预测。

## 前后SHA与精确diff

| 文件（相对仓库） | 修改前SHA256 | 修改后SHA256 |
| --- | --- | --- |
| `delivery-game/assets/scripts/map-sample/FoodCatalog.ts` | `7923a40ad6b3dd5a9038d221f65d94693a6fb06e59cae6eac9df8739a85410b4` | `75b38659452e802535ca0fed526ea34f925472ce999396c0598a0f75e3755c20` |
| `delivery-game/assets/scripts/domain/V2TripRules.ts` | `213cefc4da3a6166c5ba9b5bd36d3a795b94f676d92fcf5448324df79a768e01` | `da737af1e82a110ae5c923a0d3b8fe270fde7b0ba66bdb784df7489511683b97` |
| `delivery-game/assets/scripts/map-sample/V2GameSession.ts` | `0fe0d7fe23a1457e4c5286539ea32a7f5a796c94fe45312f5f143ddda65abce3` | `8a96a5b5e2d4b5d5e72980757c58ae3c1aa07a7020e53c6834ad9250bb472ca6` |

[完整真实unified diff](source.diff)，SHA256：`43dc808caf9b0ab57843a72c54f8bb0baac27c13df4efede1e4a6a8b4f345217`。diff直接由捕获的真实修改前全文及修改后全文生成，不是未跟踪文件的空Git diff；没有另做源副本或覆盖旧审查产物。

## 未执行案例与限制

- 新批候选/预览/接受food一致；省略输入food仍生成canonical，显式undefined/null/未知版本/错ID/错分类/额外风险键拒绝；caller risk/draw被白名单隔离。
- 特殊字符串订单ID、上下文缺/多/重复/继承键，第四参显式undefined与真正省略的差别，验证失败前seed/状态不变。
- Game1—4旧合法planned/在途/service/ready全部原校验后G/D/risk/draw/seed/到账保持；旧批完成/取消后唯一的新批升级。
- Game5/Trip3各种metadata presence、跨版本错配、目录不匹配严格拒绝，不能借clone丢undefined或降级回normal。
- 三品类/三偏好/五系数/已知天气、cap、safe保护、取餐前后、部分体力、不同分帧及跨读档不重抽。
- planned补给不加G、ready仍加G、同帧补给后自动出发、NPC/自动额度/账目时点、恢复失败不发布等上游边界。
- DTO修改不改变内部food；UI三处新冻结身份与旧normal标识、重量/金额/地址/ETA/滚动/素材由B和后续授权集成验证。

仅静态检索旧fixture：`tests/v2-supply-inventory.test.cjs:40,43,46`原三参begin仍走Trip2；`tests/v2-trip-rules.test.cjs:34-39`的未知99/旧Game1在途拒绝门槛保留。这些不是运行结果，未修改fixture，也未把旧fixture配车/时钟前置条件视为已验证。

未运行tests/typecheck/TS编译/回归/Creator/浏览器/游戏/广告/购买接单/真实或合成档。patch工具跳过per-file tsc；自动LSP附带旧Game.includes目标lib提示，涉及未改的方法或旧检查调用，本批未改lib、不追修无关源，不声称编译通过。

仅用正常patch/write_file，未改权限、未commit/push、未派Codex/Agent，不读写地图数据/素材，不把旧deadline构建当食品新候选。未自判独立PASS/性能通过/用户验收/98%或全产品完成；由父PM收齐B后独立复审与必要构建。
