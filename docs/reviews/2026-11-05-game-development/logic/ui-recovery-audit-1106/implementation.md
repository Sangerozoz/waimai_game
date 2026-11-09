# UI纠偏A：P0 Runtime交回（1106）

**已实际修正Runtime的陈旧lastError保留，并加入受限阶段/stack诊断；原始Dispatch异常触发仍unknown，未宣称整条错误已解决。**

## 现场与源码证据

- 已实际查看既有 `integration/user-preview-after-rejection-1106.jpg`：顶部为 `Error: V2 dispatch input/state invalid`，骑手页仍有“我”、作业耗时100%、招募价格写在按钮。截图不能提供抛错调用栈。
- PM既有只读摘要 `integration/user-preview-readonly-diagnostic-1106.json:3-21` 绑定4196的 `v2-product-deadline-1106`，phase=finished、pendingBatchCount=0、frameCounter=publishedFrame=24094，成功发布后32毫秒lastError仍在。它确认“成功发布仍残留旧错误”，不证明最初哪条Dispatch校验失败。文件记录uiMessage为null，不据此补造其他用户状态。
- 4196是Game4历史包，不是尚未发布的food Game5；没有把食品版本当根因。Runtime原mutate在成功publish后没有清lastError，仅open成功清，drive和UI会继续展示该旧值。

## 实际变更（仅Runtime）

1. 完整候选restore→同步旧时钟→动作→serialize→完整validate→必要commit→publish之后，才清 `lastError`。失败仍记录并抛回原异常；持续失败没有成功publish就不会走清除路径。
2. 增加私有阶段标记及 `[V2 runtime failure]` console诊断：只含固定stage、Error类别及最多8条/每条240字符的代码stack frame，去掉URL query/hash，不记录命令参数、完整状态、订单/用户信息、slot或凭据。
3. WeakSet抑制同一异常在mutate/drive嵌套重复记录，指纹抑制相同位置反复刷屏；诊断自身失败不覆盖原异常。没有新增公开API、保存字段或版本。
4. 精确逆去新增诊断/清旧错语句后，Runtime其余源码与原始捕获全文逐字一致：时间源、30Hz门禁、帧序号、真正elapsed、事务/失败保留/唯写者/存档槽均未改变，无clamp、丢交易、隐藏UI或清档。

## 不把可达guard误报为实屏根因

Dispatch.command:65确有batchIds非空禁令，当前/历史骑手操作存在可达调用，可形成相同通用错误的静态反例；但PM现场pending=0、phase=finished，不能据此反推原始用户触发。

正式V1:106规定主角换车/升级须无活动批次，但NPC工作中可申请调整、完成当前单后变更；锁定合同应结清旧费率。现Dispatch的全局batch禁令与Economy.idle/transact全局activeQuote检查可能过严，不能只让B禁掉所有UI来掩盖。本批**未删/改任何guard**，未称UI单方错误。需要独立冻结后续调整/锁定生效协议才可变更。

## SHA与精确diff

- Runtime修改前：`725a4a6354712a960f854b80295d406049155e800cccc628eb97e19c2daff721`
- Runtime修改后：`86eb7eac42b0cdc63effa5fb03e4d59b2ae8a992e4499b3a31dd8e10fb8de333`
- [完整真实diff](runtime.diff)，SHA256：`b8065330f24f9e111be93101e14929387e384db8bde1b619087e81080ed8c383`
- Dispatch保持原 `40c79d5443c35f2e6b3bba69fac129f07106d8d25ee76a6e27b7fde514d3fe0f`；未写Game/food/UI/资源/参数/公共ledger。

## 缺失的最小诊断与未测项

原始错误stack/最近动作仍unknown，旧lastError字符串无法恢复已丢的stack。本次诊断需PM独立复审/构建后，从后续自然发生的错误读取stage+代码frames及served bundle身份；不要求主动重放用户业务。A未接管tab、未读localStorage、未主动跑游戏。

未运行tests/typecheck/TS/回归/Creator/新浏览器/购买招募升级接单/真实或合成档。仅静态diff/SHA核对，未自判PASS。该Runtime修正尚不在历史4196包内。

按最新steering取消扩写旧38项长对账；下步仅给整数slots及前10级升级的参数/接口候选，不写Economy/Config，不改旧合同，也不夹带红灯/变天/食品预测。
