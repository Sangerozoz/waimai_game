# M1-UI-CONSISTENCY 开发交付

2026-10-29。本轮五项展示修订完成，固定测试角色已复核最终批次，F1/F2关闭、最小复验3/3通过，当前无遗留已证实缺陷；用户真机体验仍待验收。未启动M2，保留结算退出、同号金额评分/爱心、车辆单投影和按压/滚动。

## 根因与实施

旧Header外侧18设计单位、inner再内缩12、104容器内92头像，名义边界不能代表图像可见边。站点以固定中心296放置，也不随CSS缩放变化。新增PresentationLayout.cssUnits，按SHOW_ALL的min(frameWidth/720,frameHeight/designHeight)转换12 CSS px，短屏以游戏可见边缘算，不把letterbox计作内边距。

Header按安全区+12CSS定位，无inner额外内缩；昵称/余额/评分列向两边展开。头像保留104容器、92高等比图像，按实际图宽向左锚定；源alpha>32的左留白7/337×92≈1.91设计单位，向左补偿2，使可见边约12CSS（允许1px透明锯齿）。头像SIZE_CHANGED和ACTIVE_CHANGED均触发布局，首次异步显示不依赖后续save/update。

站点加载前或失败按可见标签94宽的半宽47锚定；图片active后按其实际UITransform宽103.706/2与标签半宽取大。SIZE_CHANGED发生在active前，故同时监听ACTIVE_CHANGED，在正式显示切换后再校正。初始化、更新页头、保存刷新和重建都调用同一positionStation。

定位scale1.4→2.1，显示高度67.2→100.8，等比1.5；触控根至少116，包含全部图像。idle定位上移到-400设计Y，避免放大后贴署名或底栏，保留圆形原图和失败准星，不加方底。

共享material只用于按钮/关闭/地区或路线操作卡/NavigationBackdrop，在同一个Surface清空重绘目标尺寸几何：低alpha底影、金/深色下沿、白厚边、主体色和左上高光，圆角按高度及宽度限制。panel、经验条、地图普通box保持原几何，不全局套皮。黄色通栏底座覆盖手势区；普通主按钮黄、次操作蓝、关闭红。SampleUI.button、MapSample.action、OrderPhone.action均按enabled显式把禁用材质转灰，保留原无事件状态，不再由C.light误猜成亮蓝。

## 验证与版本

- red.log：新增真实HUD/CSS边距回归在修前失败；修后相关回归通过。
- tests.log：npm test退出0，27核心+158地图+18存储+4地图数据=207通过、0失败。
- typecheck.log：退出0。
- build.log：包装脚本退出0，16:25:57 map-sample Finished；含build-script子进程SIGTERM/code null诊断，不称零异常。Cocos进程原始退出码未单独记录，包装脚本允许0或36。
- render-measurements.log：真实Cocos隔离组件的标准/短窄/长金额+安全区首次加载及后续更新尺寸、12CSS和定位倍率证据。图像透明边缘按源alpha元数据补充，不能仅凭触控根矩形声称图像可见边正确。
- screenshots/gallery：首页、车库/地图/账单/手机/结算、90/174/320/620宽按钮及按下态。最新批次均来自本次final-source-sha对应构建。

before/baseline.json保留修前源码，production.patch为精确差异，final-source-sha.json固定本次生产文件。OrderPhone仅增加显式禁用材质，原手机结构/10单滚动与按钮动作未改。业务订单、经济、时钟和存档源文件未在本轮修改。

## 隔离与未测

端口4185专用内存fixture，替换start/update/save，使用真实生产组件和地图、新内存OrderBook。为结算图只在fixture内构造临时已结算订单；未操作用户4181页、接单购买或存档。Storage原型方法全部拦截并抛错，日志中每次引擎setItem('storage')支持度探测均被阻止，不称零访问。fixture保存于本报告目录，可复核与正式页面差异。

固定测试角色独立结论见 `independent-test-report.md` 末尾F1/F2 closure，当前两项已关闭；项目经理已查看最终首页、手机、车库、多宽按钮及短屏/长金额图。真机手势、手感、用户审美、正式长期存档和连续业务流程仍待用户验收。

## 最终批次测量

初始可见站点12CSS；图片加载完成后12CSS，连续三次updatePlayerHeader仍12CSS。标准首次头像可见左边11.911CSS，短窄11.961CSS；最右评分胶囊12CSS。站点源alpha右侧约3/327×108=0.991设计单位透明边，对应可见右距12.991CSS（标准）/12.434CSS（短窄），在允许1px范围。定位高度100.8/旧67.2=1.5。render-measurements.log记录首次加载的值在手动update之前，后续更新另列。最新车库图中余额不足按钮已为立体灰色、无事件，区别于之前的亮蓝批次。
