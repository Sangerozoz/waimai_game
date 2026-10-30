# M1-UI-REPAIR 独立验收报告

日期：2026-10-29（上海时间）。测试角色按 PM 有边界派工执行；未操作用户页面、接单、购买或用户存档，未修改生产代码或开发测试文件，未创建角色/子会话。

## 结论

不能宣称六项全部通过。提供批次的短屏首页存在余额裁切（P2），以及共享 tap 对根节点自带 Label 的地图署名链接漏掉视觉反馈（P3）。主按钮定向行为、真实父子重排后的布局/进度/回调、异步图标保护均通过本次隔离检查；静态样板中的底栏、定位、弹窗标题/关闭、手机几何主要缺陷已修正。用户手感验收仍待用户。

## 可复现问题

### F1 / P2：360×560 默认余额已经换行并裁切

- 证据：`output/playwright/m1-ui-repair/home-360x560-after.png`，实际 view_image 查看；同批 `maps-360x560-after.png` 与 `buttons-360x560-after.png` 背后页头重复出现。
- 所看首页 PNG SHA256：`ff7179b0e3598e26aaf7fda38dedbd2b6c1dae62d1377ccba9ca4eb8f8b13e90`。
- 症状：默认 `100.00` 显示为上下两行 `100.` / `00`，两行的上/下部被金额标签边界截断。720×1280 首页没有该症状。不是需要极长金额才出现。
- 最小复现：沿用开发无用户存档隔离样板，视口360×560，打开 `?page=home`，等待图标加载；无需执行任何业务动作。检查顶部金额是否完整。
- 关联实现：`delivery-game/assets/scripts/map-sample/MapSample.ts:185-188,210-213`，字体宽度估算、换行所需高度与真实 Label 渲染需一致。自动节点矩形检查通过，不能证明真实字体没有多换一行。
- 当前状态：报告核对时源码已见 `.66` 字符宽度系数及相应高度计算；该调整不能直接证明提供批次截图已修好，需开发给出重新构建的短屏和长金额图后复核。此项按“已发现、待最新渲染复验”记录。

### F2 / P3：署名链接按压时只有空层缩放

- 位置：`delivery-game/assets/scripts/map-sample/SampleUI.ts:39-41,51`；真实调用 `CityMap.ts:60-61`。
- 根因：tap 只搬移 children。CityMap 用 `label(...).node` 直接注册 tap，Label 是触控根本身的组件，生成的 PressVisual 为空；按下该层变0.96，根Label和根scale仍为1，文字没有反馈。
- 最小复现：创建生产 label，向 label.node 注册生产 tap，发送 TOUCH_START；检查根仍持有 Label、PressVisual.children.length===0，根scale未变化；TOUCH_END 回调仍只执行一次。独立检查脚本有完整可执行用例，名称含 `root-attached label tap`。
- 影响：这是可用地图署名入口的按压反馈遗漏，无动作/存档错误，严重度低；第4项“所有可用按钮”的完整覆盖仍有缺口。主导航和当前所有 box/item 按钮不受该模式影响。

## 六项对应状态

| 用户要求 | 独立状态 | 实际证据 |
|---|---|---|
| 1 顶部去重复层、层级及短屏/长金额 | 部分通过；F1待复验 | 标准home图单层清楚；短屏home图余额裁切。独立重排测试包含极值金额、XP边界与安全区布局，但不能替代字体像素验收。 |
| 2 无底座、大图标、文字在内部下方 | 所看标准/短屏静态通过 | home两尺寸及buttons两尺寸，底栏浮在地图；中央餐袋较大；禁用招募灰色，文字覆盖图标内部下沿。真实导航重排后原开手机回调仍执行一次。 |
| 3 定位无方框 | 静态及资源路径通过 | home两尺寸仅准星；真实icon(target)测试不发图集请求，保留UITransform触控面积。 |
| 4 按压稳定、取消/拖动/多指/禁用/销毁 | 主按钮定向通过；F2遗漏；实机手感待用户 | 最新tap/cartoon定向22/22；独立检查42/42含缺陷复现断言。根尺寸/scale不变、视觉0.96、取消/失活/销毁复位、回调同步单次；署名根Label例外。 |
| 5 所有共用Dialog标题/关闭/比例 | 共用生产路径及代表截图通过；手感待用户 | 看garage标准、maps短屏、bills短屏，标题无压扁PNG，红色图标关闭可见。独立调用dialog多个kind，真实closeButton关闭后modal清空并失活；标题单Surface。 |
| 6 手机结构/图标关闭/10单滚动/按钮比例 | 静态和隔离结构检查通过；实际拖滚手感待用户 | phone标准与短屏显示机壳、屏幕、听筒/状态栏、图标关闭；独立继承实际OrderPhone结构/10单/可滚动高度检查；buttons两尺寸90/174/320/620宽圆角不随宽度压扁。未通过用户页面滚动或接单。 |

## 本轮执行证据与边界

1. `node --test delivery-game/tests/tap-gestures.test.cjs delivery-game/tests/cartoon-art.test.cjs`：最新22测试、22通过、0失败，退出0，见 `independent-targeted.log`。最初读取日志是14条tap green；开发后来增至17条tap，所以本报告使用本轮新跑的22总数。
2. `node docs/reviews/m1-ui-repair/independent-behavior.cjs`：最新42测试、42通过、0失败，退出0，见 `independent-behavior.log`。包含既有HUD行为、既有资源行为与7条独立用例。独立runner只在内存修正引擎替身的addChild重排语义、补层级active/destroy事件，转译并调用真实生产组件；不改原测试。缺陷复现用例“通过”表示成功证明遗漏，不能理解成该缺陷已修复。
3. 独立新增用例：背景与文字确实全部移入唯一PressVisual；根尺寸不变；禁用不绑定/执行；销毁/失活/取消/拖回不误操作；第二手指取消不影响主触点；原导航回调；共用Dialog图标关闭；异步图标在重排后成功等比加载、隐藏fallback，以及父关闭后的迟到回调不复活。
4. 复用原HUD行为在真实重排语义下检查XP更新、长金额/安全区布局、配送进度、页面重建、手机10单、账单动态值与滚动位置。测试内是独立内存模型和替身save，不触及用户存档。UI皮肤/root子关系测试不是仅匹配源码字符串。
5. 阅读 `art-diagnosis.md`、`press-motion-spec.md`、`press-red.log`、`press-green.log`、`tests.log`、`typecheck.log`、`build.log`。历史red为缺少视觉层的3项失败、green14/14。开发提供的回归日志无失败、typecheck无诊断、Cocos日志显示map-sample Finished；本轮未无因重复全套回归/类型/构建，不能把开发日志称为本角色重新执行。
6. 已实际查看9张新图：home与phone各两尺寸、garage标准、maps短屏、bills短屏、buttons两尺寸。修前以 `before/` 四份生产源码及现有修前图/诊断为基准，未使用Git HEAD代表未跟踪修前状态。
7. 引擎真实运行的按压补充记录为开发 `runtime-press.log`：视觉0.96、根1、取消1；其中storageAccess=1表示有一次被fixture拦截的Storage访问尝试，不能称作零访问。fixture覆盖原start、不构造用户SaveStore，update/save被替换；该运行记录不是本角色操作所得，也不证明指针事件派发、120ms缓动、实机多指或完整正式生命周期。
8. 替身Tween不推进真实时间，因此120ms恢复结束、新按压打断旧Tween与平台触控派发的最终手感仍需真实无存档样板/用户验收。没有仅凭单张静态图宣称这些通过。

## 阅读时的源码指纹

- SampleUI.ts：`eec97d4e2a11d4c1c4a6724a0cd470ff6ad6a81b3db9a3fbdf6147af4c06462f`
- CartoonArt.ts：`e0e2c51a8bc52861018ff85f88ef43ab5d71d8fb0395213377ac17fcc4a41513`
- MapSample.ts：`108a6c6b10d9123bef1f6540fd385389555adef2d837b38fcea7698e5224c089`
- OrderPhone.ts：`dff88ddee47c708ead0b2b05dbef158387c25d81d1678f2174bd6869ad5a3014`

后续由PM转开发处理F1/F2，并补最新短屏/长余额截图；测试按具体补充派工复验，不代填用户体验验收。

## F1/F2 修后续验与 closure（2026-10-29）

本节更新前述结论，原发现和原截图指纹保留溯源。当前 **F1关闭、F2关闭**；这是本轮缺陷的技术/静态复验结论，不代填用户实机手感验收。

### F1：关闭

实际通过 view_image 查看最新 `output/playwright/m1-ui-repair/home-360x560-after.png`：默认100.00完整单行，无此前上下裁切。另查看 `home-long-safe-after.png`：长余额123456789.00按1234567 / 89.00两行完整显示，身份和评价保持分列，安全区内未见裁切。

当前 MapSample.ts:178,186 使用 Array.from 按字符计量；金额系数、高度与行高计算同步。前次ES2015/ES2020替身未覆盖字符串spread在旧转译目标下被当成单个数组元素的边界。此次独立脚本把生产MapSample及依赖转译至ES5（不启用downlevelIteration），在360×560下验证六字符金额确实按六字符计量、字体宽度不超过可用宽、长金额的高度容纳两行。图像实证承担真实字形验收，替身尺寸断言只作补充。

### F2：关闭

当前 CityMap.ts:60-62 以MapAttribution作为独立点击根，Label为其子节点，再向根注册tap。此次不是复用旧“label.node直接tap”的泛化复现来判断当前路径，而是转译并执行当前 **真实CityMap构造函数**，只替换无关地图绘制、车辆绘制和sync边界。确认署名根下只有PressVisual、真实Label在该层内；按下视觉scale=0.96，根scale和UITransform宽度不变；释放同步回调一次，重复释放不重复；取消恢复scale=1且不执行动作。旧泛化用例仍能证明共享tap不搬移根Label组件，但当前链接已避免该用法，不能据旧用例宣称F2仍存在。

### 新执行与最新日志

- 执行 `node docs/reviews/m1-ui-repair/independent-closure.cjs`，**3/3通过、0失败、退出0**，完整输出见 `independent-closure.log`。仅增加本角色的隔离脚本/日志与报告，无生产/开发测试改动。第一次试跑因ES5继承无法调用ES class形式的Component替身而失败，改为可调用的Component函数替身后运行通过；这是测试边界修正，不是产品缺陷。
- 读取更新后的tests.log：三组Node测试27、154、18条，均fail=0；Python地图检查4条OK。读取typecheck.log：无诊断。均为开发运行证据，本轮未重复全套回归/类型检查。
- 读取更新后的build.log：15:57:57记录map-sample Finished；日志同时存在build-script子进程SIGTERM调试信息，以及随后`Recovery window failed` / window.json JSON解析错误。因此本角色只确认有构建Finished记录及可查看的更新渲染产物，不把此日志表述为“完全无异常”或自行推断Cocos进程退出码；没有为此操作用户全局Cocos配置或重复构建。

最新指纹：

- MapSample.ts SHA256：`aa31ba31bf8d2b8caa2d9b482f11888bd9a60edbe3cdda62091872ef6159cb67`
- CityMap.ts SHA256：`61c97f5fa30c1704f51b8a5002be70fe9453d533a3cd89e8ce476cab16539169`
- home-360x560-after.png SHA256：`d1f7c7c90ee31b448ceebead09d22359efc57d206a99b97dbce1d5ddc7be6bda`
- home-long-safe-after.png SHA256：`7ca4d2e4c5375bb7355a3b0e662557da46f7032b8f46bac70e2bad7ec8b668a9`

六项状态随本节更新：第1项原F1短屏/长金额静态问题关闭；第4项原F2当前署名路径遗漏关闭；其余沿用前次代表截图与行为范围结论。本轮没有扩大到新的页面/玩法全验收。

限制继续有效：未操作用户页面/存档/接单/购买；截图为隔离生产组件样板，Storage访问被fixture拦截不等于零访问；真实指针派发、多指真机、120ms恢复手感、用户体验验收仍未执行。旧缺陷与修复均不替代用户实际体验决定。
