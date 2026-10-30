# M1-UI-REPAIR 开发交付

2026-10-29，按项目经理边界任务实施。六项代码修订已完成，提供真实隔离组件渲染和技术验证；F1/F2已获测试角色独立续验关闭，3/3通过、退出0；用户体验验收仍待完成。

## 原始根因

详见root-cause.md。旧box倒角与PNG同时叠画，虚拟源画布再非等比缩放仍会压扁源边角；之前占地正确的测试不足以证明视觉正确。tap原先无视觉反馈。另在真实短屏构建发现loose转译将字符串展开变成concat整串，导致字宽严重低估，已在MapSample及PresentationLayout改用Array.from。署名链接Label挂在触控根上造成空层收缩，已局部包装链接。

## 六项对应实现

| 项目 | 实施 |
| --- | --- |
| 顶部 | 移除总Header背景及多余头像/金币底板，保留独立身份、真实经验条、余额/评价胶囊。修正逐字符测量；短屏100.00现在font40、159×65、line57，完整单行。 |
| 底栏 | 删除蓝底座和入口方板；常规图标108设计像素，中央餐袋约130；文字白字深描边叠图标内部下沿，中央更大。禁用灰度与动作权限保留。 |
| 定位 | item只提供稳定触控区域，显示原生准星，不加载带底图集，不画方板。 |
| 按压 | Surface与标签/图标统一移入PressVisual；触控根尺寸/scale不变。开始立即0.96，释放120ms恢复并同步回调。拖动超过7px、取消、失活和销毁立即恢复；额外触点不接管。遮罩不做收缩。 |
| 共用弹窗 | 车辆/地图/账单标题按目标尺寸绘制，移除压扁PNG；红色圆形原生X关闭，64设计像素命中根。 |
| 手机 | 原生深蓝机壳、内屏、状态栏、听筒/电池/侧键/底部手势条；顶部蓝色原生圆角。10单单列表不变，关闭为图标，所有宽窄黄色按钮按目标大小画固定圆角。 |

共享SampleUI.skin现在是重绘同一个Surface，无第二皮肤层。CartoonArt移除不再使用的chrome拉伸函数；原始图集文件保留作历史资源，头像、金币、星、菜单及餐车插画继续等比加载。无新增生图。

## 修改范围与证据

生产修改6个文件：SampleUI、CartoonArt、MapSample、OrderPhone、CityMap、PresentationLayout。baseline.json和before保存本轮前文件；production.patch是精确差异。业务订单、经济、时钟及存档代码未在本轮修改。测试调整引擎替身以支持新视觉结构，删除已退役PNG chrome契约断言，增加真实生产tap行为用例，不添加配色/源码字符串镜像断言。

- press-red.log：修前11通过/3失败，证明缺失按压视觉及复位；press-green.log：最新17通过/0失败。
- tests.log：完整npm test退出0，27核心+154地图+18存储+4Python地图数据=203通过，0失败。
- typecheck.log：npm run typecheck退出0。
- build.log：npm run build:map包装脚本退出0，15:57:57记录Cocos Web Mobile map-sample Finished。日志还包含build-script子进程SIGTERM（code null），以及构建Finished后的Recovery window failed / editor/window.json JSON解析错误。包装脚本允许Cocos退出0或36，原始Cocos进程退出码未单独记录，不能把包装脚本退出0推成Cocos进程无异常。未修改用户全局编辑器配置，也未为附带异常重跑构建。PM已核对4181首页及引用静态资产与最新build一致。
- runtime-press.log：真实引擎下按钮与地图署名视觉0.96、命中根1、取消后1，署名文字确实位于视觉子树。
- runtime-tween.log：真实引擎恢复结束及连续按压中断旧恢复的数值证据。
- wallet-runtime.log：最终短屏文字参数和被阻止的引擎存储探测；screenshots/home-360x560-after.png是最新余额无裁切图。
- screenshots/及gallery.html：标准720×1280、短窄360×560的首页/车辆/地图/账单/手机/90、174、320、620宽按钮；附短窄长金额+安全区图。screenshot-sha.json固定本批图片。

## 隔离样板与正式页面差异

fixture.js在复制的构建上截断MapSample.start，使用真实地图数据和新内存OrderBook，再调用真实正式组件。未创建CountySaveStore、未执行原start事件绑定；update/save替为空，不跑计时。长金额通过修改fixture私有内存playerState构造，安全区通过fixture覆盖；不代表正式存档读写通过。按钮样板使用noop回调，不接单、不购买，未在用户运行页操作。

隔离端口4183与专用浏览器session；Storage所有方法被拦截并直接抛错。Cocos每次会尝试setItem('storage')探测支持度，render-results.log记录每页一次被阻止的探测；没有委托真实Storage、读取或写入任何内容，不能把次数称作零访问。原始图和最新截图均来自真实Cocos渲染，非HTML仿制。

## 独立发现的处理与未测项

独立测试初版报告中的F1余额裁切、F2署名无反馈均已针对根因修正。测试角色已在independent-test-report.md追加“F1/F2 修后续验与 closure”，确认两项关闭；independent-closure.log记录3/3通过、0失败、退出0。PM亦已查看最新短屏/长金额及五页面、宽窄按钮。初版发现保留溯源，以报告末尾closure更新为准。

F1/F2技术/静态复验已闭环；真实设备、多指系统派发、实际滚动/误触手感、完整配送/购买/账单业务流程和用户审美验收未在本轮替用户完成。静态截图、事件驱动引擎样板、技术测试与用户验收分别记录。M2–M7未启动。

## 最终收尾确认

本次仅更新交付及收尾记录，未改生产源码。已对6份生产文件逐一核验final-source-sha.json，全部与已交付版本一致，结果及退出码边界记录于closure-record.json。未重复运行测试或构建。本轮开发交付结束；用户体验验收待项目经理收集。
