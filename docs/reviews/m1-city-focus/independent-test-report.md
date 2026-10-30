# M1 CITY-FOCUS 独立测试报告（最终续验）

2026-10-29。只写independent-*，未改生产/开发tests、未派代理、未访问用户4181或存档。最终：**F1两种复现均已关闭；城市、图标及动画在下述技术/隔离渲染范围内通过，无遗留已证实缺陷。** 下文阶段发现保留溯源，最终状态以文末closure为准；用户真机体验未验收。

## 实质发现 F1 / P2（旧动画批次，待最终渲染复验）

CityMap.ts:142旧实现将起始offset与`-riderPoint*当前中间scale`插值，尺度变化又改变目标，导致镜头越过静止骑手。真实引擎render-frames.log：起始project[275.724,-77.994]可见，.3秒变[-401.299,-84.494]超出720视口左界-360，再回[0,0]。实际view_image看locate-frame-2.png车被裁出左边；不是只由替身推测。

最小复现：内存fixture720×1280，overview100m，offset=[1200,0]并sync，真实FollowRider start/end后推进.3秒；不得只断言scale变化/末态正确。独立原日志independent-animation.log记录4项中3过1失败（`initially visible rider stays visible`），保留不覆盖。新增60个.01秒检查世界center位于start→rider线段、距离单调减小、不越目标。目前并行开发已将目标改为DEFAULT_SCALE端点；新检查点5/5通过，见independent-animation-checkpoint.log，**不是旧源码红灯日志**。最终截图/冻结仍待对齐。

## 独立结论与范围

| 主题 | 已证实结论 |
|---|---|
| 图标真实可见内容 | 独立PIL读取生产ui-icons alpha>32的coin crop，按40容器等比缩放得36.516×37.677；采样生产心形五层Bezier并应用实际1.05/1.098缩放，轮廓并集36.546×37.677，见independent-icon.json。已看本轮home-720/home-360图，体积/内距保持，美术art-review通过。非只比UITransform。 |
| 按钮→相机→update | 真实MapSample按钮接真实CityMap方法实例，由生产update(.15)驱动idle/running两态，0/.15/.3/.45/.6平移与缩放同时变化、末态精确scale2/30m/follow=true。含移动目标、重复点击从当前画面重定向、拖动/双指起手/滚轮/后台中断。此项不掩盖上述旧版本中途反甩问题。 |
| 动画资源/生命周期 | advanceLocate不重画全量主干路；详情约.1秒节流并走既有缓存，无定时器链；hide/destroy显式cancel。重建换新camera且内部立即locate清零，新实例无残动画；旧实例无计时器自行推进。销毁引擎生命周期/真实设备fps未独立实测，不能由替身推断“不卡顿”。 |
| 城区与分框 | 独立生产模块生成v4：320营业，城区60商/180顾，东42/126、西18/54，无跨框转移；城郊12/36、远郊8/24保持。总pois617，非617营业点。urban任意点最小35.224743m、商家77.739795m，节点不共用；营业点都在dispatchBounds，四边450m内缩。 |
| 真候选与可达 | 对全部320营业点独立RoadRouter双向查询均有路径。用生产nearbyOffers70批隔离候选采样，新索引>=385商家24种、顾客21种实际出现在offer取送端点；所有普通端点都属有效池。该内部入口检查不消耗用户刷新，不冒充所有新点都逐个派到。 |
| 历史目录与mapId | 从本轮before PlaceCatalog运行旧流水线，旧v3为385项，与新前缀JSON全字段完全一致。raw/v1/v2/v3直接升级的完整pois/operating结果一致，v4输入幂等；历史mapId ef9d9c7/7192a588/95a923c8/876eebc5均被当前v4接纳；改变真实节点坐标后恢复拒绝路网变化。 |
| 旧活动与资产 | 独立routes/running/paused/arrived/done五态，均明确断言源状态，不拿已经done冒充arrived；样本from/to至少一端退出新营业池。恢复active全JSON不变（paused按既有规则归running），端点/routes/elapsed/receipt等保留，玩家/账单/刷新额度相等，骑手位置1e-8容差不变。继续depart/advance/settle到done，finish两次不再次入账/改账单。 |
| 分布与保留 | 已实际看同overview镜头distribution-v3/v4：东部/西部建筑街区点明显增密，未移城市或隐藏候选。home标准短屏及动画0/2/4帧实际看过，新图非旧HUD代用。区域配额/时限代码沿用既有规则；策划方案与独立计数相符。完整配额/时限回归以开发最新全测及具体本轮受影响用例佐证，非单靠点数。 |

## 执行记录

- independent-density.cjs：**3/3通过，退出0**，independent-density.log。独立编译生产模块，加载before旧目录并比较全字段、直接升级/幂等、路网拒绝、全池双向路由、间距/边界、真实候选采样和状态迁移；不是复用catalog-evidence脚本结论。
- 为防“arrived实际上已done”覆盖不足，补选需门口交付订单并实际断言五态，执行`node --test --test-name-pattern 'active snapshots' .../independent-density.cjs`：**1/1通过，退出0**，independent-active.log；记录五态outsideNewPool均true。
- independent-animation.cjs：旧批次4项3过1败；新增单调线段检查后的当前源码检查点**5/5通过、退出0**。日志保留旧失败，不把已改动源码采样叫修前red。包含既有两条相机动画测试及三条独立用例，执行筛选`city-focus independent|animated locate`。
- 初步读取开发tests/typecheck/build，build22:22:56 Finished；开发仍在为动画修正重出产物，本报告不提前宣称最终版本全套检查/构建通过。未机械重复全量测试。

## 指纹与待闭环

本次模块检查点源SHA保存在independent-source-checkpoint.json；该清单只代表生成时源码，不冒充最终冻结。旧动画缺陷时CityMap SHA为`6f0d3d64184881936726e0738baad4c366a62a4be31106d735dfad7f11fac11e`；最终待开发freeze后重新计算并对比，只重验变化路径。最终图、fixture及源码清单尚待补齐。

限制：Cocos fixture禁start/update/save、内存OrderBook、Storage探针拦截，不是零访问或用户存档写入；本角色未操作浏览器或用户页，真引擎帧为开发产物并独立看图/核数值，模块级测试使用引擎边界替身。真实连续帧率、触控平台派发、后台/销毁真机、用户审美与完整长期业务未验收。最终构建后需追加F1 closure及真实新帧/冻结SHA，不以本报告阶段结论代填用户验收。

### F1 新增近边界复现（世界中心修正后，仍未关闭）

当前开发已改为世界startCenter→rider插值，60个.01秒线段/距离单调检查通过。但近边缘起始可见骑手仍会被同步放大短暂推出画面：真实CityMap方法，rider[-1540,-130]、100m、offset[1264,0]并sync时project.x=340；locateAnimated→advanceLocate(.3)后project.x=368.333333，超过右界360。当前`independent-animation-edge.log`为6项5通过/1失败，测试`visible near-edge stationary rider...`。相机中心本身未越过目标，但投影仍离屏，故不能只凭中心单调就关闭“可见目标被反甩离屏”要求。代码`CityMap.ts:141-143`需同时处理放大与可视范围关系；未修改生产。开发最新已有旧复现场景的新帧，近边缘新复现尚无真实引擎帧，只作模块级确定问题记录。

另核对before/OrderBook.ts与当前文件无差异，区域配额/时限、经济/额度/结算实现未被本轮改写；数据变动影响候选池的验证见上文。最终渲染与冻结待本新增边界处理后再核，不取中间版本SHA作最终结论。


## F1 最终 closure 与冻结核对

**F1关闭。** 最终采用PM已允许的等效方法：offset向固定30m终态偏移插值，scale使用同一个easeInOutCubic进度e。对静止骑手，project(t)=(1-e)project(0)；世界中心在线段内单调收敛，但不要求世界中心进度恰等于e。未把已放弃的“世界中心正好中点”当产品硬需求。

1. 在最终冻结源码重跑独立animation筛选：**7/7通过，退出0**，见independent-animation-final.log。含原275px起点越目标复现、340px近边缘复现、60×.01秒世界中心线段/单调检查、按钮→MapSample.update在idle/running逐帧推进、移动骑手、重复点击、拖动/双指起手/滚轮/后台中断，以及新增真实rebuildLayout与onDestroy取消旧camera状态（销毁后的旧引用再advance不推进）。生命周期测试仅引擎监听解绑边界替身，不自动等同真机生命周期实测。
2. 最终render-frames.log两组共10条真实引擎组件帧数值独立解析断言通过，independent-final-frames.log保存摘要。普通投影X：275.724→258.491→137.862→17.233→0；边缘：340→318.75→170→21.25→0；两组scale均.6→.6875→1.3→1.9125→2，0.6秒终态30m/follow=true。逐帧检查投影距离不增加、中心点不出视口。这里起点340本身使车图右侧部分处于屏外，不宣称整个车图起点即完整可见；修复保证投影从该可见中心收敛，不额外反甩到屏外。
3. 实际再次view_image查看最终普通1/2/3帧和边缘0/2/4帧，图像连续趋向骑手，无此前0.3秒反向出屏。其余帧数值全部核验。旧locate-frame-2路径已被开发最终图覆盖，原缺陷依旧由本报告数值及independent-animation.log/independent-animation-edge.log保留，不把同路径当前图误当旧失败图。
4. 读取最终implementation-report，22:27:00 build Finished、包装脚本退出0的开发记录；tests.log最终27+163+18+4=212无失败，typecheck无诊断。没有重跑无关全套/44秒密度组。保留Cocos子进程SIGTERM/code-null及原始进程退出码未单独捕获的限制，不写零异常。

### 最终指纹

独立读取实际文件与final-source-sha.json **8/8 MATCH**；PlaceCatalog/UrbanCatalog/CountySnapshot/OrderBook/MapTypes与先前独立检查点完全相同，故复用independent-density.log及independent-active.log已通过证据，无需重测未变的密度/迁移。

- MapSample.ts：`97d3704e3e3c5b1baf6eef01d84e5429df86762b6f93c02235d38de621ef22ce`
- CityMap.ts：`b03591de73578551b804f9d371e0e3d9e38320fa54d60d38cdda8e6ddb1a4621`
- SampleUI.ts：`82f002343fd46ac964954483ff16fd7b60c75aa2b5e8c8d80bf4e271d1340721`
- PlaceCatalog.ts：`35e937c1092bbef796260e93abd909f136ea09bcee78fa231f805c4061f01399`
- UrbanCatalog.ts：`5040a6f800273f76345fdc99bba37b307e9df7ef0b058c4666bcdb12e58cc6c1`
- CountySnapshot.ts：`7d5307024e316ee7027e66cdf5bf1e25a0bc4f9b9124832257e8c0ae6833465d`
- OrderBook.ts：`117458db4cb9c36377e6eb275f14c689c59dd3fdfd2e9f88ab73d68efdbb75d7`
- MapTypes.ts：`07d37270b930693c1c3db52bbf5281f42147cb995e62a4c8f94527222e6d5858`

本轮fixture SHA256：`960571e6a9a1930307fe86c9378cbc57ec8a5ef4572825280eb05825b454d39d`。独立实际14张顶层截图对screenshot-sha.json **14/14 MATCH**；完整源码、fixture、每张图、build.log及render-frames.log SHA见independent-final-sha.json，非只引用开发清单未经核算。最终美术爱心数据已更新，与独立算得xyScale1.05/1.098后的36.546×37.677一致，保留3D与内距。

### 最终未验收边界

帧图由开发隔离真实Cocos组件调用advanceLocate(.15)生成，组件时间轴不等于墙钟录制或真实fps。独立按钮→update在idle/running的证据为生产模块+引擎替身，不能用mock宣称不卡顿。未操作用户4181/真实存档或业务，未派子代理；fixture替换start/update/save并拦Storage，日志setItem('storage')支持探针每页被阻止，不叫零访问。真机连续帧率、多指完整缩放手感、后台系统切换、长期业务及用户体验仍由PM安排用户验收。本轮F1关闭只代表上述可重复技术与隔离画面问题已修复。
