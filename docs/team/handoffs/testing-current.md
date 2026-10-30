# 测试：2026-10-30新会话交接

用户要求新开测试会话，停止旧长历史。只读取本交接及本任务所需文件；不fork、不读旧会话。当前PM及各角色ID见docs/team/README.md，向PM汇总，不要反向给旧PM发消息。接任先简短确认，不为接任跑全套。

项目Cocos3.8.8/TypeScript，delivery-game；大量untracked保留。只写自己的独立审查文件，不改生产/开发tests、经济或存档。产品入口docs/team/product-baseline.md；M1体验收尾，M2手动取送首切片已落地，完整M2及后期未完成。

最近交付docs/reviews/m1-compact-handoff/pm-acceptance.md和independent-test-report.md。完整开发回归241、typecheck/构建包装0；独立UI修后20/20、最后受影响17/17；核心独立16组及未来主备保护2组。各执行主体不能合并算亲跑。旧失败保留历史，不把旧SHA结果认当前结论。

已知当前功能：紧凑共享卡、免费取消至点击取餐前且保真实道路点、手动取餐与2秒服务/去送餐、关键事件从收卡/车/地图/账单主动呈现一次、同ID重接提示、简洁自适应结算、旧档1/2/3兼容/schema4、pendingSave阻断。旧单原自动过程；需求询问已隐藏，自动遵从原需求，旧done结果不改。X只收订单卡；结算X/遮罩finish+save回干净首页。

本轮待新PM安排docs/team/tasks/2026-10-30-order-text-layout.md：金额¥19.84在某尺寸换行，大厅和当前卡都需真实字体单行/边界验证；结算标题与全部内容居中，关闭右上。用户原图docs/reviews/order-amount-singleline/reference/。关注字体随CSS放大、金额列宽、两位小数不丢、不裁切、不盖邻列；不能只断言enableWrap=false。结算正常/晚到餐损多行都核中心，不能误改其他弹窗。

用户实际4181页面/存档不自动操作。只允许具体技术派工的新内存OrderBook隔离样板；创建CountySaveStore前拦生产start/update/save、Storage四API拦截，引擎setItem(storage)探针需如实记录，不写零访问。静态截图、模块替身、真实Cocos渲染、用户体验和真机FPS分开报告。

上一轮隔离逻辑fixture/prepare与browser脚本可按需复用，产物另存docs/reviews/order-amount-singleline/independent-*，不覆盖m1-compact-handoff冻结图/清单。新任务执行后，报告根因/最小复现、实际命令退出码、所看图/尺寸、源图fixture构建SHA、限制及未测项。不因上一轮绿测就放过本轮用户截图的真实缺陷。

## 测试节奏（2026-10-30用户最新指令）

用户原话：“测试，当我说阶段完成时进行测试，过程开发不再进行测试了。太耗时耗 token”。此规则优先于旧任务、交接和默认技能中的逐改动测试要求。

- 开发过程中不自动运行测试、回归、独立复验或为验证而启动渲染矩阵；PM不逐次派测试角色，也不自行补跑同类测试。
- 仅在用户明确说“阶段完成”后，由PM组织该阶段集中测试；开发自行认为完成、单次修复落盘或构建完成均不触发测试。
- 开发交付如实标注“已实现，未测试，待阶段集中测试”，不将历史通过结果套用于新改动。阶段集中测试的证据与用户体验验收继续分开。
- 按交付需要生成可试玩构建不等于测试，不借构建附带全套测试。保留用户存档与实际页面操作边界。
