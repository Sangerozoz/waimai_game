# M1-UI-CONSISTENCY 独立验收

2026-10-29。只读当前生产组件及本轮before/baseline；只写本报告、独立脚本/日志。不操作用户运行页/存档/业务，不开会话或子代理。

结论：本轮尚不能全部通过。加载后顶部/站点12 CSS px、定位1.5倍率与主要立体材质有实际证据；发现站点加载前边距及车辆页禁用材质两项缺口。结算退出与按压/资源保护定向回归通过。

| 五项要求 | 独立状态与证据 |
|---|---|
| 1 顶部可见两端12 CSS px | 加载后通过。独立用实际等比avatar尺寸327/344×92驱动layout，720×1280及360×560+左右安全区时，avatar左缘及RatingPill右缘换算均12px。不是只断言Header宽度。实际看home-720/home-360/home-long-safe-360，正常与长金额完整，同号同字重、爱心保留。 |
| 2 站点全过程12 CSS px | **未通过F1**。加载后及updatePlayerHeader的开发真实引擎测量均12；加载前/失败时可见标签右缘不是12。加载后save/rebuild由同一positionStation调用，加载前仍按未显示图片占位计算。 |
| 3 定位等比1.5与命中 | 定向通过。before scale1.4→当前2.1，真实同图集同等比算法，宽高倍率均1.5；请求100.8×100.8，root至少116×116。独立检查按下root不缩、视觉0.96、8单位拖动后不触发定位。三张首页图无方板，与署名/底栏有间隔；失败fallback/异步关闭测试通过。 |
| 4 黄色通栏立体底座 | 所看静态通过。home三视口/安全区图中黄底、亮上沿、白边、金色下沿，图文在上，中央餐袋突出。仅目标命名路径使用material；经验条/页头/地图未自动加立体按钮层。原生Graphics单Surface，无PNG非等比拉伸。 |
| 5 操作按钮统一 | 主要样式通过，**禁用态未通过F2**。phone刷新/宽接单、receipt确认、红X、buttons标准及按压短屏图共享厚边高光下沿，无叠两套皮肤；车辆页禁用按钮却变成亮蓝。未把图中圆角方形红X宣称为正圆按钮；其几何没有图片压扁。 |

## 发现与最小复现

**F1 / P2：站点加载前/失败边距19 CSS px，加载后12，未满足全过程一致。**

- `MapSample.ts:217-224`，positionStation读取仍inactive的图片UITransform宽108计算half54；实际可见fallback仅36宽，最右侧为94宽“站点”标签half47。720标准视口下位置为360-12-54=294，标签右缘341，所以实际可见边距19px。加载后图集等比宽约103.8，重新定位后图片右缘为348，边距12。
- 最小复现：隔离组件/无存档样板，延迟或拒绝ui-icons加载，720×1280打开首页观察站点；放行加载，比较两阶段。失败时该状态持续，而非只有一帧。
- 可执行复现：`independent-check.cjs` 中 `station visible pre-load and post-load` 用例；生产布局下显式模拟图片inactive和最终等比宽度，实际标签bbox测量，日志断言失败为`preload visible margin is 19px; loaded margin is 12px`。不是宿主100宽测量。该用例是引擎边界替身复现，尚未补真实引擎离线截图。
- 开发render-measurements.log是在等待资源完成后测量，不能否定该未加载分支。建议按当前可见内容定位并在成功切换时重新测量，或提供等可见边界的fallback；由开发选择实现。

**F2 / P2：车辆页禁用按钮用亮蓝材质，灰色禁用态不一致。**

- `SampleUI.ts:19-28`：material将C.light无条件映射为C.blue；box的Button命名路径在enabled判断之前就绘制该材质。`MapSample.ts:469`对不足余额/到达上限传C.light及enabled=false，动作虽不绑定，外观却仍变蓝。
- 最小复现：本轮内存fixture默认余额100打开garage；已实际查看`output/playwright/m1-ui-consistency/garage-720.png`，底部“还差 ¥100.00”亮蓝底、灰字，与`maps-720.png`未解锁灰按钮不一致。文字对比也弱。无需点击购买。
- 不为纯颜色写源码字符串断言；由真实截图及实际调用链给证据。建议主题显式区分disabled，避免把禁用C.light当正常蓝次操作。

## 执行证据

- `node --test --test-name-pattern 'consistency independent|receipt user dismiss|receipt continue|receipt dismissal' docs/reviews/m1-ui-consistency/independent-check.cjs`：**6项，5通过/1失败，退出1**，完整`independent-check.log`。失败为F1，其他是加载后真实可见边界换算、定位倍率/命中/拖动，以及结算X/遮罩回idle无卡、确认大厅后关闭、保存失败可见提示。真实MapSample/OrderBook+渲染边界替身，修正addChild唯一父语义，未改原测试。
- `node --test delivery-game/tests/tap-gestures.test.cjs delivery-game/tests/cartoon-art.test.cjs`：**22/22通过，退出0**，`independent-resource-press.log`。覆盖0.96视觉与稳定根、取消/拖动/多指/失活/销毁、同步单次动作、资源缓存/失败/迟到回调关闭保护。
- 阅读开发最新tests.log：27/158/18组均fail0；typecheck.log无诊断；build.log在16:22:21记录map-sample Finished。本角色不重复全套回归/构建，不把这些称作独立重跑。
- 阅读render-measurements.log：真实引擎标准scale1、短屏scale0.4375，加载后avatar/评分/站点12px、站点连续更新12px，定位高度100.8/67.2=1.5。此为开发测量，本角色独立布局补测及实际看图互证。真彩图透明边缘仍允许spec约1px栅格误差。
- 实际view_image查看10图：home-720、home-360、home-long-safe-360、phone-720、buttons-pressed-360、garage-720、maps-720、bills-720、receipt-x-720、buttons-720。仅查看本轮，不重复前两轮全审。车辆单投影及灰度站点在本轮首页图仍保留；未重做全部切车失败/方向检查。

未测边界：未执行用户真机手感与真实业务；未自行通过浏览器发送用户触控。fixture内存订单及Storage拦截：记录有一次引擎setItem(storage)探测被阻止，不能写成零访问或用户存档写入。Tween替身不证明120ms实机完成；静态截图不证明触控派发。F1/F2待开发修复及补图后复验。

源码SHA256：SampleUI `fc7ae5821c5163574ce175e7a898d23ebfe1092bb77da13eb549db8723226381`；MapSample `3c544a066eb69b8796837cecc419c8b30af7721045a9273fd9bdb51a8daf18b2`；PresentationLayout `86ba9045b18ae7bd7b6ee21d75055a7a6bd9473cd1107fdbfeca013bc6167d11`；OrderPhone `dff88ddee47c708ead0b2b05dbef158387c25d81d1678f2174bd6869ad5a3014`。

## F1/F2 修后 closure（2026-10-29，最终批次）

更新当前结论：**F1关闭、F2关闭；本轮未遗留已证实缺陷。** 原发现、原失败日志及原指纹保留，不将其误称为最终版本状态。本节仅补两个发现的复验，其他范围沿用上文。

- **F1关闭**：执行新的`independent-closure.cjs`，加载生产CartoonArt与MapSample，资源入口使用可控回调，Node active setter及UITransform尺寸变化发出各自事件；生产订阅由此执行，**不手调positionStation**。真实加载器顺序是setContentSize→设置sprite→active=true；成功和失败两分支下，360×560+左右/底部安全区的可见标签/图片右缘在加载前、响应后、updatePlayerHeader、save及rebuild后均为12 CSS px。成功后实际等比图片宽度由真实crop计算，失败继续按可见94宽标签计算。已核对本机Cocos 3.8.8的node-event.ts/node.ts确实提供并发出SIZE_CHANGED/ACTIVE_CHANGED；测试没有伪造一个生产引擎不存在的事件。此为真实生产加载及监听链+引擎边界替身，不冒充浏览器像素或引擎事件派发实测。
- 开发更新的`render-measurements.log`补充真实引擎initial站点12、firstLoaded站点12、连续页头更新12，标准及0.4375短屏缩放均一致；avatar透明边缘修正后约11.91/11.96 CSS px，在spec约1px误差内。该记录为开发执行证据，独立替身复验与之互证。
- **F2关闭**：分别调用真实SampleUI.button、MapSample.action和OrderPhone.action，disabled时记录Graphics实际fill命令包含`#C5CCD5`表面，且不存在之前的蓝色表面绘图；三个节点均没有TOUCH_START/END绑定，回调次数为0。另实际构造refreshesLeft=0的OrderPhone，`广告未开放`按钮灰表面、模拟点击后刷新次数回调仍0。不是仅搜索源码含灰色色值。
- 实际重新view_image查看最终`garage-720.png`及`home-360.png`：前者不足余额按钮已灰，文字保留可读，后者站点/定位/黄底栏正常。红X高光未作为新缺陷扩大返工。禁用零次刷新暂无额外截图，本轮由实际生产绘图/触控断言覆盖。
- 执行`node docs/reviews/m1-ui-consistency/independent-closure.cjs`：**3项全部通过、退出0**，完整输出`independent-closure.log`。未无因再跑全套。原independent-check.log的5通过/1失败是修前发现证据，保留不覆盖；不能用其旧替身手动状态切换方式判断修后事件链。
- 读取最新开发tests.log：27/158/18组三组fail0；typecheck无诊断；构建16:25:57记录map-sample Finished，均未称为本角色重跑。

最终源码SHA256：

- MapSample.ts：`22ae9e247bcba5e199d9694b5275f8963ce16409917707fd33154cacdb7480ec`
- SampleUI.ts：`c9ee57354b8880a369f66c8d9291393355adacab6a27ea6264fbf2ae24e8119d`
- OrderPhone.ts：`f288261ca7a53b4a011728ec43206eae81236e625443e07b8335b9c5c9da788e`
- PresentationLayout.ts：`86ba9045b18ae7bd7b6ee21d75055a7a6bd9473cd1107fdbfeca013bc6167d11`

保留限制：无用户页面/存档/真实业务操作；Storage引擎探测被fixture拦截不等于零访问。用户真机手感、多指平台派发及完整体验未验收，不能用本轮closure代填。
