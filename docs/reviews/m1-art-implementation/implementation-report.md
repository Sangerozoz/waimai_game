# M1 方案 A — Task 1 实施报告

2026-10-29。Task 1 生产呈现层实施与自动检查完成；Cocos 导入、构建、预览和真实视觉验收交主代理执行。未自行构建、启动预览、操作用户接单/升级、访问浏览器存档、提交或暂存任何文件。

## 文件和结果

- `delivery-game/assets/scripts/map-sample/MapSample.ts`：顶卡保留头像、白色无阴影、安全区 top12/side18；取消横向压扁。头像昵称/等级与余额/评价重排，余额保留完整数字，异常长数字采用明确的正文最小字号，不依赖 SHRINK。导航仍透明，只有“抢单”黄底；站点不可交互，禁用车辆/抢单/招募继续无事件。活动面板根据可读字号确定高度，同步地图、定位及版权边界；路线内容区滚动，标题、时间、两行风险对齐；主操作固定，配送进度和取餐倒计时沿用原数据。通用弹窗固定安全区内尺寸，不缩放整卡；账单、结算、地图目录、车辆和门口需求内容区可滚动，头部和主操作固定。结算保留全部 summary、基础价、评价、经验、等级、最终余额。门口需求仍无关闭、保留原两选项和暂停计时说明。
- `SampleUI.ts`：仅修改辅助色为 `#64695F`、分隔线 `#E3E2D8`；既有通用 label/button 字级行为保留，避免旧场景溢出。
- `OrderPhone.ts`：保留黑色圆角手机外框、侧键、状态栏、岛、电池和底部手势线；蒙层黑色 alpha153。真实可用宽高布局，订单按文字长度增加卡高；餐图、餐名、预计收入、商家、目的地、里程/预计时间和加急/怕洒标签完整，独立接单区域。十单同一滚动列表，无分页；刷新次数和用尽后的禁用行为沿用。
- `CityMap.ts`：仅快捷路线内芯颜色由 `#B78312` 改 `#795020`；保留地图/路线白描边、缩放、顶视车辆和版权。
- 新增 `PresentationLayout.ts`：按真实 SHOW_ALL 比例换算可读字级、44 CSS px 操作高度；换行文本固定字号、明确高度，Mask + ScrollView 只滚动内容。无领域依赖。
- 新增 `VehicleSideArt.ts`：D→旧电动车，D+→翻新电动车；纹理 Promise 缓存、失败移除缓存以允许重试、失败保留可读车型回退；严格校验节点及父级实际活跃状态，关闭弹窗后异步回调不会写入。原比例完整显示，不裁剪图。
- 新增资源 `assets/resources/map-sample/vehicles/side-d.png`、`side-d-plus.png`。原图逐字节复制；Cocos 生成的 importer 元数据由主代理完成并保留。
- 测试调整仅 `tests/map-hud.test.cjs`、`modal-shade.test.cjs`、`map-vehicle.test.cjs`、`map-gestures.test.cjs`，不改测试 runner。新模块使用真实实现；仅扩展 Cocos 引擎边界。旧 camera 测试不再绑定旧固定 467 高度，HUD 真实节点检查承担新面板与地图边界一致性。

## 几何与语义自检

- 320×568 CSS 设备：720×1280 SHOW_ALL 比例约 .444，正文34→15.1 CSS px，辅助30→13.3，关键金额59→26.2，主操作100→44.4。393/430 宽下按 frame/设计高度重新计算；没有整卡二次缩放。异常长余额允许降到明确的正文字号底线，金额字符串不省略。
- 主页顶卡宽 `720-left-right-36`，顶部始终安全区外留12；头像存在且无非等比缩放。导航相邻槽间距大于触区宽；定位触区加大后保持右侧安全边距。
- 活动 sheet 底部固定在导航顶部 `-522`，高度至少520，地图底部等于真实 sheet 顶部；新增跨高屏→横向短屏→普通手机的回归验证，避免用旧 frame 的字体尺寸导致地图/面板间隙。地图视口和定位随 bottom inset 一起移动，版权使用原 CityMap footer。
- 路线三卡固定列：标题、预计时间、准时/晚到与餐损分两行，不以缩字塞入；内容超出仅滚动，操作和交付需求固定。正文段落尽量按 `textHeight` 分配高度，非无限 SHRINK。
- 账单仍调用原 `billingRows`，钱包原索引3，今日原索引0/1/2/4/5/6/7/8，累计9/10/11；`billValues[index]` 使用原索引，不按新视觉顺序 push。每秒更新/保存更新保持对应关系；日期、≥历史下限、未知—原样保留。完整12项末项可滚动到达。
- 结算不增加领取步骤；普通自动结算、2秒取餐、门口选择不可跳过、D+¥200、余额不足/已达上限禁用均沿用原规则。原经济和存档逻辑未修改。

## 验证证据

最终 `npm --prefix delivery-game test` **退出0**：27 原配送测试 +138 map测试 +18 county-store测试 +4 Python地图数据测试 = **187项全部通过**（基线184，新增3项）。日志 `verification/npm-test.log`。

最终 `npm --prefix delivery-game run typecheck` **退出0**。日志 `verification/typecheck.log`。

有意义的先红后绿：

1. 短屏账单/结算滚动可达性、12项、完整 summary、固定安全按钮和只读打开状态：修改前 `test:map` 失败“bill has a scroll viewport”；最终通过。
2. 车辆侧图缓存/关闭父级后异步返回/失败回退与可重试：修改前失败“VehicleSideArt implementation is required”；最终通过。关闭场景覆盖父级实际 inactive（仍未完成销毁的同帧），避免只检查节点 isValid。
3. 重排账单实时更新：独立期待钱包¥100.00、今日收入¥0.00、在线1:00:00仍归属原字段。首次测试误用1970时间区间被发现；改用固定2026-10-29本地中午与注入日期，使测试确定且不访问浏览器存档，最终通过。
4. 原 HUD 边界用例补充连续 resize：先失败“resizing keeps the actual sheet and map boundary together”；改为用新 frame 的 SHOW_ALL 比例决定面板高度，最终通过。红日志 `verification/resize-red.log`；最初两项红日志 `verification/initial-red.log`。

源文件与 before 快照逐字节比较：既有 map-sample TS 只变化 `MapSample.ts`、`OrderPhone.ts`、`CityMap.ts`、`SampleUI.ts`。`OrderBook`、`CountyRules`、`CountySnapshot`、`CountyConfig`、`DeliveryLedger`、`BillingPresentation`、`MapVehicle`、`SafeAreaLayout` 均 unchanged；before 保存的13个原资源文件无变化。

| 新资源 | SHA-256 | 与用户原图 |
| --- | --- | --- |
| side-d.png | bd27bcbbe7ea0838706a5735ef0ccb6cd95b100b7e1f6598a78c64ac5f6bf743 | byte-exact |
| side-d-plus.png | 989366029cbfef33558997dbac050207b6ec61be00756330aa9dead2d05f510f | byte-exact |

## 尚需主代理 / 用户复验

上述自动节点与数值检查不等同于实际字体栅格/滚动手感和真机视觉验收。文字换行高度采用字符宽度的保守估算，需要 Cocos 实际截图复核长地址、短屏、异常长余额和透明底栏。正式图标仍待用户素材；当前占位图标保留。源PNG无重画或裁剪，实际透空留白随原图显示。主代理应刷新 TypeScript 资源、确认无 Cocos 导入/编译错误后构建并恢复 MapSample 预览，再做获授权的静态截图与只读检查。

## 独立审查 Round 1 — 两项 P2 修复

审查发现两个真实 CLAMP 高度不足，已在同一批限定修复；本批只改 `MapSample.ts`、`tests/map-hud.test.cjs`，没有领域/存档/资源变化，也未构建或启动预览。

1. **活动面板餐品元数据。** 原58高容不下320×568窄屏的合法“麻婆豆腐饭 · 3份 · 3kg · 普通餐品”。改为根据真实列宽与辅助字号调用 `textHeight`，保留58下限；该样例现在为94高，增加36。保留元数据顶部位置，将增量传递给三张路线卡与滚动内容总高，以及配送阶段、计时器、进度组、到达提示和完成说明/统计的位置。完成说明再留出12间距，避免与元数据下沿贴靠。固定按钮、sheet高度、地图边界均未移动。
2. **账单大金额。** 原固定行高约105，值区约95，合法长余额二行约120–128会被截断。账单行按带“≥”的 `Number.MAX_SAFE_INTEGER` 分币金额，以最大强调字号与真实值列宽预留高度；320×568下行144、值区134，可容纳两行。不在每秒更新中重建弹窗或改变行高，`updateBills`仍只按原稳定索引替换字符串；原content/滚动位置保持。

本批两个新增真实HUD回归先运行 `npm --prefix delivery-game run test:map`，**退出1：138通过 /2失败**，分别失败于“the valid description needs two readable lines”和“the grown value has space for both lines”（`verification/round1-red.log`）。修复后 focused命令 **退出0，140/140通过**（`round1-focused.log`）。前者检查路线、运行、完成三状态元数据可读、后续字段无重叠、全部路线可滚动及固定按钮/地图边界；后者从短值更新到合法 `¥1234567890123.45`，检查同一wallet Label、同一modal和手动设置的content偏移123均保持，并检查重开长值也有足够高度。

最终覆盖两修复与完成态间距检查的 `npm --prefix delivery-game test` **退出0：27+140+18+4 =189项全通过**（`verification/round1-npm-test.log`）。`npm --prefix delivery-game run typecheck` **退出0**（`verification/round1-typecheck.log`）。这是当前最新完整检查证据，先前187项记录是首轮交付时状态。

真实 Cocos 字体栅格与换行仍由主代理预览验证；保留 `getFrameSize` CSS尺度语义，本批未处理其非阻塞弃用警告。
