# M1-UI-FOLLOWUP 独立复核

2026-10-29（上海）。按本轮spec及before/baseline核对，不用Git HEAD代表修前。只写本报告及本角色隔离脚本/日志，未操作用户页面/存档/接单/购买，未改生产或开发测试，未创建会话/子代理。

结论：结算退出与保存协议定向通过；六项美术主要呈现符合本轮要求。首批截图曾发现P3站点右缘轻微越界，开发内移后最新批次已复验关闭（见文末）。真机手感仍待用户。

| 项目 | 结果与证据 |
|---|---|
| 1 结算退出 | 通过。真实MapSample+OrderBook的X、Shade均finish→save→关闭→重建idle；无DeliverySheet、不打开大厅。内部closeDialog仍保留done。确认继续打开大厅，关闭大厅后无结算卡。玩家资产/账单不变，地点以1e-8米容差不变；重复输入、重建、序列化恢复不重复发奖。保存失败提示可见并在重建后保留，后续save重试写入idle。receipt-x-home、receipt-continue-home图均实际查看。 |
| 2 圆形3D定位 | 通过所看标准/短屏图。原宿主item无方底；icon(target)复用图集，原生准星仍为fallback。加载失败用例通过，未把圆蓝底误当成应删除的背景。 |
| 3 金额/评分同字号字重 | 通过。真实生产标签fontSize、lineHeight、isBold一致；home-720、home-360及home-long-safe-360实际看图，长金额两行完整。 |
| 4 爱心替星 | 静态通过。原生双曲线心形及白高光可辨，截图未见五角星替代；未新增位图。 |
| 5 站点放大、灰度禁用 | 通过；首批P3右缘细节已在最新批次关闭。图集请求尺寸108×108，与普通入口108相近；仍grayscale，无tap事件。文字未压住页头。但右侧安全余量不足，见下。 |
| 6 通栏及手势区 | 通过隔离布局/静态范围。NavigationBackdrop原生Graphics，宽720；bottom inset=64时实际变换后底边等于屏幕底边。标准/短屏/带安全区图保留大图标与内部下沿文字，中央餐袋更大。 |
| 7 车辆投影 | 所看方向/车型静态及位置层级检查通过。home/vehicle、north、plus、plus-north图中单一浅影在车下。真实CityMap构造及syncOverlay独立检查：shadow在overlay中早于rider、随投影坐标移动，0/90度和scale .6/2/6下固定+3/-8接地偏移且唯一；D/D+资源加载与失败用例通过。阴影是固定地面椭圆，无须随车旋转；本轮没有将它误记为旋转车体的一部分。 |

## 发现

**P3：站点放大后右缘轻微超出安全边界。**

- `delivery-game/assets/scripts/map-sample/MapSample.ts:215,218-220`：中心仍为309-rightInset，生成图标放大到108，半宽54，所以设计占位右缘为363-rightInset，超过安全右边360-rightInset约3单位。实际图集等比适配后略小，标准home-720/vehicle图仍见圆形右缘贴边且轻微切边。标签宽94未越界。
- 最小复现：本轮隔离样板720×1280 home，等待station图集加载，观察右缘；带rightInset时仍沿用相同余量。
- 建议由开发为放大图标半宽留足右边距；无需改变禁用状态或增加交互。低严重性，不影响结算退出正确性。

## 本轮执行

- `node --test --test-name-pattern 'receipt user dismiss|receipt continue|receipt dismissal|followup independent' docs/reviews/m1-ui-followup/independent-check.cjs`：**6/6、退出0**，见independent-check.log。复用真实HUD/OrderBook并在内存替身修正addChild的唯一父关系，新增X/遮罩重复输入、内部销毁、账单/骑手、恢复、保存失败可见及重试、底部安全区和字号检查；不是源代码字段匹配。
- `node --test delivery-game/tests/cartoon-art.test.cjs delivery-game/tests/map-vehicle.test.cjs`：**11/11、退出0**，见independent-art.log。实际执行生产资源加载器的缓存、失败、过期回调与切换保护；不操作用户游戏。
- `node docs/reviews/m1-ui-followup/independent-shadow.cjs`：**1/1、退出0**，见independent-shadow.log。实际生产CityMap构造和syncOverlay；无关道路绘制/车辆加载边界替换，加载器另由上组验证。没有声称该替身就是Cocos渲染或触控派发。
- 初次严格序列化地点比较失败于599.9999999999999→600，差异约1e-13米；确认来源为浮点归整后改为1e-8米容差，最终通过，非实际位移问题。
- 实际view_image查看10张本轮图：home-720、home-360、home-long-safe-360、vehicle-720、vehicle-north-720、vehicle-plus-720、vehicle-plus-north-720、receipt-x-home、receipt-continue-home、receipt-continue-720。
- 读取最新开发tests/typecheck/build.log：Node测试各组fail=0，typecheck无诊断，构建16:11:13记录map-sample Finished。本轮未重复全套回归或重跑构建。构建日志含插件更新403/计时调试信息，不称为完全无告警。
- 读取render-results.log：开发真实Cocos隔离路径记录X后idle且phoneOpened=false；继续后idle且phoneOpened=true，关大厅后phoneClosed=true，两路hasSheet=false/assetsUnchanged=true。此为开发执行证据，本角色另做上述独立行为检查。

限制：截图fixture替换start/update/save，内存订单，不是用户运行页；Storage的setItem探测被fixture拦截并记录，不等于零访问或业务存档写入。未验收用户真机手势、完整按压手感和连续实际配送；不把构建、替身行为、静态图及用户体验混称为同一结论。

当前源码SHA256：MapSample `4ba647d3c244f67e739cc4d91bd5667b8323272271e226828c06ecd1c851330d`；SampleUI `4f25c5cd60228618bd79d67fa329c00cc42c9f541dfe2e2481a89a93accf99de`；CityMap `9ea027e926bde5958684f15fe5ad95e8db79952049e2e5f9263f1a648d66063c`；MapVehicle `3931c4901d8c0b56c8bd7013908aa6b080657ca06861516e7ff9bfde2d82793d`。


## 最新站点批次补验

收到PM更新后，再次实际查看home-720与home-long-safe-360：圆形站点图完整，右边留出余量，文字无重叠。当前MapSample.ts:215,218已由309改为296-rightInset；108宽设计图标右边为350-rightInset，位于安全右边360-rightInset内。独立检查追加实际放大图标bounds不越安全右边断言，重跑同一最小组合 **6/6通过、退出0**。原P3只针对此前所看批次，现关闭；当前本轮未遗留已证实缺陷。上述源码指纹对应最终版本。用户真机体验及隔离fixture/Storage限制保持不变。
