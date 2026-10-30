# 开发：当前精简交接

> 2026-10-30最新增量优先：`docs/reviews/m1-compact-handoff/pm-acceptance.md`、implementation-report及本轮冻结清单为最新入口。共享紧凑卡、取餐前免费取消/真实道路锚点、新manual handoff与严格schema4、主动事件、精简自适应结算已交付；241项完整回归。MapSample/OrderBook为新机制入口，旧活动继续原自动语义。下文10-29的schema1/2/3及M2未开工描述仅属当时历史；本轮是获准M2手动取送首个切片，不代表完整M2完成或自动开工余项。保留用户4181/存档权限边界。

2026-10-29，项目经理会话 `01a18670-bb97-7ed0-bc40-8e8bdd54115b`。

## 职责与停止点

- 用户只与项目经理沟通；你负责生产代码、资源接入、构建与开发自检，按PM具体任务执行。
- 接任已完成；按PM后续具体任务工作，不因阅读本交接自动实施M2、重跑测试或读取旧开发长会话，不fork。
- 当前为M1技术收尾及用户定向体验验收；M2–M7未开工。用户本轮要求汇报及规划，不是立即开工后续机制。
- 固定角色与最新ID见 `docs/team/README.md`；不用旧归档开发会话派工，不要求给PM反向发消息，结果留当前会话及项目文件。

## 产品来源与覆盖关系

按需读 `docs/team/product-baseline.md`，产品三件套是V2设计、V2七阶段实施、10-29全盘审查。它们描述完整目标，不等于当前游戏全部实现。

- `docs/superpowers/specs/2026-10-28-delivery-game-v2-design.md`
- `docs/superpowers/plans/2026-10-28-delivery-game-v2.md`
- `docs/reviews/2026-10-29-delivery-game-v2-full-audit.md`

V2原文UI旧位置已被后续用户明确要求覆盖。当前无昵称、头像下等宽XP、12CSS边距、金币/立体心同可见大小、数字胶囊hug、左下灰站点、放大圆形3D定位、黄色通栏只上圆角、红圆大字抢单。地图车有单投影，弹窗/关闭/刷新用统一3D材质；PNG等比、不能拉伸当任意按钮底图。

最近规格按需读m1-city-focus、m1-hud-final、m1-ui-consistency、m1-ui-followup、m1-ui-repair对应docs/superpowers/specs/文件，不整批复制历史。

## 当前代码与可玩范围

根目录 `/Users/sanger/Documents/ChatGPT/taptap 2`；工程 `delivery-game`；Cocos Creator 3.8.8、TypeScript、Web Mobile，当前构建 `delivery-game/build/map-sample`，试玩 `http://localhost:4181/`。

现有单单：10候选、普通/加急及放门口、真实寻路/路线预览、自动行驶/2秒取餐提示、一次结算、县城D/D+、经验/评分/钱包、12项账单、每日免费刷新2次、本地恢复/备份/保存失败可见。招募与站点仍灰禁用，没有NPC真实收益。

`OrderBook`统一持有单单状态，`CountyRules`结算，`CountySnapshot`保存schema仍1/2/3，`CountySaveStore`现键delivery-county-save-v1。不要把地图`placeCatalogVersion:4`误认为M2的存档schema4；新行程时钟、手动取送、点击加速、三单、体力、NPC及后期城市尚未落地。

当前时钟30游戏分钟约10现实秒、行驶封顶15秒；取餐2现实秒不计配送分钟。账单里程按完成时登记整条取送路线；M2才改实际增量口径。M2需单写者/可靠提交，现localStorage比较写不等于原子CAS。

## 最新已冻结交付

主入口 `docs/reviews/m1-city-focus/pm-acceptance.md`；必要时读取implementation-report、independent-test-report、verification.json和final-source-sha.json。

- 城区有效营业点80→240（商60/顾180，东168/西72）；总营业池320、全量POI617；旧385项全字段前缀保持、只追加。35米全点/70米商家间距、450米留白、可达及真实派单已验证。
- 旧raw/v1/v2/v3目录可升级v4且幂等，legacyMapIds链保留；旧活动即使端点退出新池也继续原单、原路线、原进度、单次结算。
- `CityMap.locateAnimated`为0.6秒easeInOutCubic；固定终态offset与scale同步插值，当前rider参与目标计算。`advanceLocate`由MapSample.update驱动，`cancelLocate`支持手势/滚轮/后台/重建/销毁。内部locate可瞬时。
- 动画曾有越目标/边缘甩出屏F1，已关闭。必须保留`project(t)=(1-e)*project(0)`的静止目标收敛性质；不要回到混合旧尺度offset和当前scale目标，亦不要求worldCenter恰好同e。
- 爱心实际xyScale=[1.05,1.098]，与金币可见范围约36.5×37.7设计单位一致。
- 最新212测试通过（27+163+18+4）、typecheck退出0；构建包装退出0、22:27:00 Finished，保留子进程SIGTERM/code null诊断。不得写成原始Cocos进程零异常。
- 8份生产/依赖源及14截图已核SHA；PM核4181字节与最终构建一致。真机FPS/触感及用户整轮验收仍未完成。

## 关键模块及既有保护

- MapSample：HUD、面板/弹窗、控件与相机接线；SampleUI：原生3D材质、PressVisual按压；CartoonArt：等比/异步/缓存/失败回退。
- CityMap：相机、点位、图层/详情缓存；PlaceCatalog保留旧目录生成链，UrbanCatalog专责新城区密集选点；DispatchAreas和CityExtent负责区域/边界。
- 结算X/遮罩必须finish已完成单并保存后回干净首页，不留底部回执卡；“继续接单”才打开大厅，大厅关闭回首页。内部closeDialog不能被改成每次都有业务副作用。
- 触控根稳定，只缩PressVisual 0.96，释放120ms；拖动7px取消、多指/失活/销毁保护。Cocos旧转译器遇Map迭代/字符串spread用Array.from。

## 工作区与验证边界

- 使用当前checkout；大量未跟踪文件是已有项目，git HEAD不代表修改前版本。改前保存本轮范围快照/哈希，精确diff；不清理、不reset、不批量提交用户文件。
- 验证`npm test --prefix delivery-game`、`npm run typecheck --prefix delivery-game`、`npm run build:map --prefix delivery-game`；只在实际改动/失败需要时跑，不为接单重跑。
- 用户实际游戏页与存档不自动操作。自动验证使用真实生产组件+新内存OrderBook隔离fixture，禁start/update/save、不构造CountySaveStore、拦Storage。引擎setItem('storage')探针被拦须如实记录，不能称零访问。
- 最新隔离样板端口4187、目录output/playwright/m1-city-focus/；帧图是组件时间轴，不证明真实FPS。以报告区分真实渲染、模块替身及真机未测。
- 当前最新用户任务为M1订单体验修订，开发已交付，技术/体验收口由PM安排。后续仍等具体任务，勿自行扩M2、生成资源或对外发布。

## 订单体验最新增量（优先于上文历史基线）

`docs/reviews/m1-order-experience/implementation-report.md`、`final-source-sha.json`及当前spec为最新开发交付；city-focus保留为依赖证据。当前222项回归（27+173+18+4）、类型与构建包装退出0，23:18:58 Finished，SIGTERM子诊断保留。

- 无单中央“抢单”，有单中央“订单”；红圆145.6为原112的1.3倍。菜单保留，关订单卡只收起，弹窗往返保持卡显隐/选路/镜头；有单可看车但业务不能换车。
- 手机3D壳/侧边/连续蓝顶，大厅信息顺序按本轮spec；普通黄“抢单”、转单绿“接受转单”。source与normal/urgent正交，新单ID稳定约20%来源，旧字段缺失不回填；quantity/buyerNote为严格可选字段，未知份数不猜1，重量为整单。
- `OrderPresentation.ts`共享展示语义，候选/接取用相同合法路线期限。主费用统一feeCents基础配送费，预计收入不得假作固定到账。
- 已接详情/路线统一滚动，底部唯一“去取餐”接现depart，仍是M1自动配送；卡底离放大红圆最高边12CSS。自动路线总览允许scale<.6，全points和车/取送pin入镜；手动缩放仍.6–6，定位仍0.6秒回30m。
- `CityMap.autoFit`与低scale总览边界模式分开，用户拖图后收卡/重开/resize保实际offset/scale；不能恢复为每次重建focus或locate。取送pin在骑手上层。done回执X/遮罩仍finish+save干净首页。
- 最新4190隔离样板位于output/playwright/m1-order-experience/site，41张图、26条状态；来源/视图等自动验证不代表用户实际存档或真机体验。具体最终独立结论查该轮PM/测试报告。
