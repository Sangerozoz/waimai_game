# M1 HUD-final 独立测试报告

2026-10-29（上海）。依据本轮hud-final-design、before/baseline和当前冻结源码。**本轮七项在所列技术/隔离渲染范围内通过，未发现需转开发的实质缺陷。用户真机体验未验收。** 不将开发日志、美术意见和本角色独立执行混为一项证据。

## 七项结论

| 项目 | 结论及实际证据 |
|---|---|
| 1 定位100m恢复30m并跟随当前骑手 | 通过。独立将生产MapSample生成的FollowRider按钮接真实CityMap方法实例，overview→移动骑手至[-2500,100]并扰动offset→按钮start/end，scale变2、标签30m、follow=true、当前骑手project≈[0,0]；再移动至[-2490,110]仍居中，原边界约束通过。不是只断言转发true。实际看locate-before/after，路网比例和骑手视图变化吻合；开发真实引擎记录也为0.6→2。 |
| 2 底栏只上圆角、底部及手势区填满 | 所看标准/短屏/安全区静态通过。topOnlyBar补齐各层下角矩形；home-720-10000-safe及home-360-100000000000-safe底部无地图角洞。未给经验条或地图套入按钮材质。 |
| 3 红圆抢单、大横排字、稳定命中 | 通过。已无餐袋，红色多层体积、白字描边清楚。独立在左右不对称安全区下核对生产Nav-orders最终bounds宽=高，祖先横向缩放由slot逆缩放抵消；start仅PressVisual变0.96，hit root宽不变。开发真实引擎有效尺寸112×112；美术art-review亦通过。 |
| 4 站点左下避让与禁用 | 通过所测状态。实际看首页左下站点在比例尺/底栏上，署名在另一侧。独立在idle/routes/running+side/bottom safe下量图像与文字最低边均高于footer和DeliverySheet顶部；站点无事件绑定。源码SIZE/ACTIVE及页头更新统一positionStation，当前active图片/标签半宽决定12CSS左距。保持灰度和原加载保护。 |
| 5 图标内距与3D心 | 静态通过。金币、心形与胶囊左侧/数字有留白；心有深红下缘、红粉明暗与亮面体积，语义清楚。实际看标准及短屏图，美术终检通过；没有将纯红白点当3D验收。 |
| 6 小同号数字、胶囊hug及大金额完整 | 通过所测范围。独立实际标签string检查100.00/10000000.00/100000000.00/1000000000.00/90071992547409.91，标准与短屏+side/bottom safe均保持原值和两位，不缩写；金额评分fontSize/isBold相同。所看各级截图无裁切省略；开发真实测量短值胶囊宽178，千万257，十亿288，最大352，随内容增长而非固定百分比。字体标准24、短屏28设计单位，较旧body更小；受限时评分下排路径保留，未无限缩字。 |
| 7 无昵称、头像下XP等宽、异步及真实进度 | 通过。真实CartoonArt加载器在资源等待、成功/失败、updatePlayerHeader、save、rebuild中触发生产SIZE/ACTIVE监听，独立量XP宽=当前显示图片或fallback宽，无手动调用布局来冒充事件。成功约87.359，失败84；这里“等宽”是每状态XP与当前头像相等，成功与fallback本身并非同尺寸。经验条下置且不被文字撑宽，无昵称/旧身份板；阈值用例含XP40/50=0.8及升级边界，实际引擎layout-measurements.log也为0.8。文字只保留Lv.等级，进度仍由真实规则计算。 |

## 本角色执行与证据

- `node --test --test-name-pattern 'independent HUD-final|compact avatar|XP presentation|receipt user dismiss|receipt continue|receipt dismissal|explicit locator|explicit default locate' docs/reviews/m1-hud-final/independent-check.cjs`：**11/11通过、退出0**，independent-check.log。运行生产MapSample/CityMap/OrderBook，边界为Cocos替身；修正addChild唯一父语义。含结算X/遮罩回idle无残卡、继续大厅再关闭、保存失败提示受影响路径回归；不重复无关阶段。
- `node docs/reviews/m1-hud-final/independent-avatar.cjs`：**1/1通过、退出0**，independent-avatar.log，内部遍历加载成功与失败两支。加载/缓存/裁切为生产CartoonArt，注入资源响应和尺寸/active事件的引擎边界。首次runner截取旧测试入口名称已变化，误载全测试并缺少MAP_ROUTER_MODULE；已纠正仅取harness，最终日志为上述1项，非产品缺陷。
- `node --test delivery-game/tests/tap-gestures.test.cjs delivery-game/tests/cartoon-art.test.cjs`：**22/22通过、退出0**，independent-resource-press.log。保留0.96、稳定命中、取消/拖动/多指/禁用销毁/同步单次回调、图集缓存/失败/异步关闭保护。
- 已实际view_image看10图：home-720-10000-.png、home-360-10000-.png、home-720-1000000000-.png、home-360-10000000000-.png、home-360-100000000000-safe.png、home-360-9007199254740991-safe.png、home-360-10000-avatarfail.png、home-720-10000-safe.png、locate-before/after.png。头像失败图仍有占位和等宽经验条；不把未激活图片width92误当可见fallback84。
- 阅读开发implementation-report、render-measurements、layout-measurements、art-review及tests/typecheck/build日志。开发全回归27+158+18+4项无失败，typecheck无诊断；build21:45:43 Finished。保留build-script SIGTERM/code null附带诊断及包装脚本退出码边界，不称原始Cocos进程零异常。本角色未机械重复全套/构建。

## 冻结与追溯

当前生产文件与final-source-sha.json逐项MATCH：

- MapSample.ts：`2ef624b6eaa8127b7be3293b8ec76b936fe5e69acb1b46b7b7a079fcb62d7c68`
- SampleUI.ts：`82f002343fd46ac964954483ff16fd7b60c75aa2b5e8c8d80bf4e271d1340721`

fixture.js SHA256：`d4df41c2768e96ca20fccfc8ffa06b8a966901bc6ef8bbbc35cf3736346daf2d`。

已独立生成independent-sha.json（上述源码、实际依赖源码、fixture与本轮所有顶层截图指纹）；开发screenshot-sha.json的10项与实际output图**10/10匹配**，记录independent-manifest-check.log。代表定位后图SHA `2548e014fd8e7109c1c73a064fb35f05431ac16ec1924e0126b82b5ce470aaac`，头像失败图SHA `3bd881930e9bf9c56f63308451e6f6d7a7df912a6082800ab3d7792d1c164cd2`。与最终implementation-report再次核对冻结一致；原before仅用于本轮差异追溯。

## 未测边界与权限

未访问用户4181页面/存档或真实接单购买；仅生产组件内存模型及开发提供的4186隔离图。fixture禁start/update/save、不构造CountySaveStore，Storage.setItem('storage')每页引擎支持度探针被拦并抛错，不能称零访问，也不是用户数据写入。

本角色未自行驱动浏览器真实指针或系统手势；Tween替身不证明120ms实机动画完成。未重测所有配送/经济/时钟、长期业务、所有金额×视口笛卡尔组合、真机多指/触觉；已覆盖指定金额代表图及两视口布局断言，车辆单投影只核首页保留，不重复此前全部切车失败验证。技术、静态、美术结论均不能代填用户实际体验验收。
