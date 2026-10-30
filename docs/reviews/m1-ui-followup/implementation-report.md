# M1-UI-FOLLOWUP 开发交付

2026-10-29。本轮只实施结算退出链路及六项指定美术更正，固定测试角色已独立复核，当前无遗留已证实缺陷；用户体验仍待验收。未启动M2。

## 原因及修复

结算X/遮罩原先直接closeDialog，仅销毁弹窗，OrderBook仍done，所以renderPanel保留已结算卡。red.log真实MapSample/OrderBook回归复现done!=idle。新增dismissDialog只承担用户关闭：receipt且done时走既有act→finish→save，再closeDialog和rebuildLayout；其他弹窗普通关闭。内部closeDialog没有新增业务语义，避免弹窗内部切换或重建误确认。继续接单原路径保持，并加done守卫避免重复打开大厅。保存失败按既有save/act协议显示notice，不扩大为全局存储重构。

六项视觉修正：

1. target重新进入生成图标路径，保留原生准星作异步失败回退；宿主仍无方板。
2. moneyFont与rating同用m.body、相同行高/粗体，保留Array.from字宽修复和长金额多行完整性。
3. 评分改原生圆润心形，贝塞尔轮廓和白色高光，替换星形。
4. 禁用站点图标108设计像素，与常规底栏同体量；实际截图发现右缘接触后中心由309内移296，保持安全区、灰度和无动作。
5. NavigationBackdrop为原生通栏轻浅底板，覆盖118高菜单及手势安全区；大图标、内部标签、中央餐袋、PressVisual保持。
6. CityMap在道路后建VehicleGroundShadow，再建DeliveryRider。投影为五层低alpha椭圆，单节点、固定屏幕光向、随project(riderPoint)移动；车旋转不导致光向绕车。投影放在车辆根的前一个兄弟节点，确保加载中/失败时根Graphics占位也盖在影子上。选择CityMap承载而非MapVehicle子节点是为解决根Graphics先于子节点绘制的问题；MapVehicle及车图80×128尺寸未改。

## 验证

- 完整npm test退出0：27核心+157地图+18存储+4Python地图数据，共206通过、0失败，tests.log。
- npm run typecheck退出0，typecheck.log。
- npm run build:map包装脚本退出0；16:11:13 map-sample Finished，build.log。日志附带build-script子进程SIGTERM/code null调试信息，不能称零异常。Cocos进程原始退出码未单独记录，包装脚本允许0或36；不推定引擎进程所有阶段无异常。
- 新增真实行为用例：X退出idle、无大厅/卡片、玩家资产/账单不变、serialize恢复idle；继续接单单次打开及大厅关闭回首页；保存失败仍可见提示。其余原行为回归沿用。
- render-results.log记录真实Cocos内存样板的X/继续/大厅关闭事件：均idle、assetsUnchanged=true、hasSheet=false；仅继续路径phoneOpened=true。
- screenshots和gallery提供首页标准720×1280、短窄360×560、长金额/安全区，D/D+两朝向，loading/failed占位单投影，结算弹窗及退出后的实际截图。

## 权限及未测

隔离构建端口4184，专用浏览器session；fixture截断正式start，用真实地图/新内存OrderBook，关闭update/save，不创建CountySaveStore。本轮允许的临时订单仅在fixture里经真实accept/depart/advance/settle构造已结算场景，不操作用户原页、不购买、不访问用户存档。Storage所有方法被拦截；引擎每次setItem('storage')支持度探测被直接抛错阻止，日志保留一次尝试，不称零访问。

长金额、D+和朝向由fixture内存设定，loading/failed仅在fixture拦截车辆纹理请求；不改变正式资源加载。用户设备手感、多指系统派发、真实长期存档及完整配送体验仍待验收。独立复核见independent-test-report.md及其“最新站点批次补验”：行为6/6、资源11/11、阴影1/1通过，站点P3已关闭；本报告沿用测试角色结论。

before/baseline.json保留本轮前源码；production.patch提供精确差异；final-source-sha.json固定版本。MapVehicle文件未变，业务规则/经济/时钟/存档模块未修改。

## 站点最终边界批次

本次无生产源码变更，final-source-sha.json四项均复核一致。MapSample.ts初始化controls和layoutPlayerHeader都使用296-safeInsets.right，updatePlayerHeader→layoutPlayerHeader及保存后的刷新路径不会恢复309。

新批次station-boundary.log在最终构建的真实Cocos隔离样板中连续调用updatePlayerHeader三次：默认x296、右缘347.8532、安全右界360；右安全区10时x286、右缘337.8532、安全右界350。三次各自一致，全部inside=true，距边界约12.15设计像素。UITransform.getBoundingBoxToWorld含已加载的实际图标及文字子节点；不是只量100宽触控根。新增station-boundary.png、station-boundary-safe.png记录该批次，SHA已补入screenshot-sha.json。旧home-720.png等仍是同一源指纹的最终批次，最新补图用于边界专项复验。

## 最终收尾

PM已确认独立测试最新批次与final-source-sha一致，无遗留已证实缺陷。本次只更新报告和计划，不改源码、不扩大验证；本轮开发交付结束。用户真机体验仍未代验收。
