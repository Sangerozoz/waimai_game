# 开发：2026-10-30新会话交接

只读取本交接及本次任务所需文件，不fork、不读旧开发长历史。用户要求停止使用旧开发会话，新会话唯一负责生产代码集成；汇报当前PM，ID见docs/team/README.md。你接任后先简短确认，迁移登记完成后由新PM派具体工作，不因接任自主改生产。

工程delivery-game，Cocos Creator3.8.8/TypeScript/Web Mobile；当前checkout有大量既有untracked，不清理/reset/批量提交。改前保存本轮范围before+SHA，HEAD不等于改前基线。业务代码开发单写，其他角色仅自己的审查文件。

最新产品入口docs/team/product-baseline.md；当前M1体验收尾，M2手动取送首切片已交付，完整M2未完。最近交付docs/reviews/m1-compact-handoff/pm-acceptance.md，按需读implementation-report/verification/final-source-sha，不重做已完成内容。241测试（27+190+20+4）、typecheck/构建包装0，08:42:24 Finished，SIGTERM/code null诊断保留。真机/用户体验不代填。

关键生产模块：MapSample（HUD/弹窗/主动事件/保存失败）、CompactOrderInfo（大厅与当前单共享布局）、OrderPhone（手机大厅）、PresentationLayout（按CSS可读字号/测量/滚动）、OrderBook（单单/phase/schema4/道路anchor）、ManualHandoff、RiderAnchor、CountyRules/CountySnapshot/CountySaveStore。地图catalog4与snapshot schema4不同概念。

当前新单：去取餐→到店待点击取餐→2秒服务→待点击去送餐→自动按需求交付结算；旧活动原自动过程。规划/去店/到店未取可免费取消且保真实停靠点，不换池/钱/评分/刷新；取餐后拒绝。X只收卡，中央订单找回；到店/待送/结算从子弹窗主动触达一次，新accept清事件键防同ID重接吞提示。receipt X/遮罩finish+save干净首页，继续才开大厅。保持经济公式和纯收益分解，不二次扣钱。pendingSave冻结动作/行驶，失败持续提示；未知未来主备档写保护。跨页原子CAS仍非已实现。

本轮待新PM派工任务：docs/team/tasks/2026-10-30-order-text-layout.md。用户金额¥19.84在某些尺寸拆行，两个入口均有；另要求结算标题和所有内容居中。先复现真实字体/测量，范围仅布局。证据新建docs/reviews/order-amount-singleline/；不得覆盖上一轮最终图/清单。用户两图在该目录reference。

权限：不得操作用户4181游戏/存档、接单购买清档。可静态HTTP核构建；真Cocos测试用新内存Book、创建CountySaveStore前截start/update/save、拦Storage。引擎setItem(storage)探针如实记录。复用4191隔离原理但新轮独立fixture/图。现有npm test --prefix delivery-game、npm run typecheck --prefix delivery-game、npm run build:map --prefix delivery-game；按改动必要性跑，不为接任重跑。

后续不自动做加速/多单/体力/NPC或独立页面；不重生成已有资源。不要求PM或用户逐文件重复许可。工作报告明确实际命令/退出码、根因、修复、未测项和最终指纹。角色接任输出控制在几句话，先不改代码。

## 测试节奏（2026-10-30用户最新指令）

用户原话：“测试，当我说阶段完成时进行测试，过程开发不再进行测试了。太耗时耗 token”。此规则优先于旧任务、交接和默认技能中的逐改动测试要求。

- 开发过程中不自动运行测试、回归、独立复验或为验证而启动渲染矩阵；PM不逐次派测试角色，也不自行补跑同类测试。
- 仅在用户明确说“阶段完成”后，由PM组织该阶段集中测试；开发自行认为完成、单次修复落盘或构建完成均不触发测试。
- 开发交付如实标注“已实现，未测试，待阶段集中测试”，不将历史通过结果套用于新改动。阶段集中测试的证据与用户体验验收继续分开。
- 按交付需要生成可试玩构建不等于测试，不借构建附带全套测试。保留用户存档与实际页面操作边界。
