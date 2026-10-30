# M1 ORDER-EXPERIENCE 独立验收报告

**最终结论：本轮在所列生产模块与隔离渲染范围内通过，未发现待修实质缺陷。用户真机操作与体验未验收。** 按PM最终spec：配送费使用feeCents，卡底间距12 CSS px；真实少于三路线按实际显示，旧30m错误fixture图不作生产缺陷。

## 覆盖与结论

| 要求 | 证据与结论 |
|---|---|
| 红圆×1.3、safe正圆、稳定根 | 真实Cocos3组记录claim=145.6×145.6，比例112×1.3；卡底到圆最高边标准12设计单位、短屏27.42857，按SHOW_ALL实际scale1/.4375换算均12 CSS px。标准/短屏safe图显示正圆、清楚字与间距。根/视觉按压机制沿用；本轮未另做真机触控根测试，开发相关回归及支持的真实按钮状态检查补证。 |
| 手机3D与整蓝顶、黄/绿按钮 | 亲自view_image看最新lobby-first-720、transfer-button-360-safe：机身多层深蓝边/亮边/侧键，状态栏至标题贯通蓝色；黄抢单、绿接受转单均立体且文字清楚。美术终检通过，部分图重拍SHA与美术当时清单不同，不冒称同批逐图美术验收；PM已复看当前代表图，本角色亦查看。 |
| 信息顺序与真实数据 | 独立解析3组开发真实Cocos大厅记录：10候选均按实际deadline分钟标签→信息→配送费fee→对应抢单/接受转单；首/中/尾截图无叠字，备注只在确有数据时出现。已亲看lobby-middle-720、lobby-bottom-360-safe，转单备注与费用分行。期限与accept同口径、来源正交/不扰RNG由审核支持独立模块验证，见下。没有把ETA当承诺或把预计收入当配送费。 |
| source/quantity/buyerNote兼容与strict | 审核支持fresh-audit实际11组通过：三种种子旧字段逐项及RNG调用365/365/366一致；before生成schema3旧idle/routes/running/arrived/done整个恢复序列化不变且0RNG；实际新CC-6转单接/恢复/完成及防重、direct/transfer×normal/urgent正交、18种非法字段拒绝。旧无新字段不回填、不重标；首单direct。该组非本角色亲跑。 |
| 导航/收起/找回/交付/回执 | 支持模块检查卡X不cancel、显隐两态三弹窗往返+resize、车辆可看不能升级、唯一去取餐只depart一次、运行收起继续、不重启；账单中到达不强踢，返回可处理门口交付，回执X后finish干净idle。开发真实Cocos26状态记录另经本角色断言核数：arrival仍modal=bills，finish为idle/modal=null，手动pan在重开/resize后capture值完全相同。亲看arrival-bill-360-safe和receipt-closed-360-safe图。 |
| 详情/路线滚动与固定按钮 | routes-top与route-1标准/safe图实际看过：详情可换行，单固定去取餐未盖路线；末条路线完整出现于按钮上方。记录detailsHeight1091/1387大于卡高440/441，大厅maxScroll为正、10单首中尾可达。开发真引擎脚本实际scroll到各路线再发按钮事件，选线高亮几何有变化；本角色不是自行点击全部10单或真机滚动。 |
| 自动全程总览及marker/vehicle | **亲跑通过**：独立执行生产CityMap相机方法，6组长折返/不同高/side-safe组合，所有points在预留矩形中、允许scale<.6。再独立断言3组真实Cocos记录中582个路线点、9个车辆/取送pin bbox均在viewport内，避上HUD、卡、红圆、站点、定位。已看route-1-720及360-safe，骑手不再如早期padding不足图被裁边，车图未缩小；取送pin可见。真实两条路线未造第三条。 |
| 手动pan保留与低scale定位 | **亲跑通过**：自动fit后真实touchStart/move/end→capture，autoFit=false；另一高度camera.restoreView保持实际scale/offset。随后locateAnimated在.3秒投影减半，.6秒scale2/follow=true；手动zoom仍.6–6。开发真引擎两组locate-pan帧同样收敛30m，重开与resize记录不再误fit；不是仅传true检查。 |

## 本角色亲跑

1. `node docs/reviews/m1-order-experience/independent-camera.cjs`，退出0，independent-camera.log：生产CityMap转译执行，6组相机模型、3真实渲染视口记录、582points、9marker bounds、12CSS间距均PASS。渲染边界为替身；Cocos bbox记录为开发在4190隔离样板产生，本角色独立数值断言，不称独立重跑引擎。
2. 独立解析browser-check-evidence及browser-states-evidence，independent-records.log：3组10单顺序/费用/操作、26状态的pan保留、低scale定位终态、账单中到达、回执退出断言通过。该日志是对真实引擎记录独立核算，非重新派发浏览器事件。
3. 亲自view_image查看11张最终图：lobby-first-720、lobby-middle-720、lobby-bottom-360-safe、transfer-button-360-safe、routes-top-720、route-1-720、routes-top-360-safe、route-1-360-safe、arrival-bill-360-safe、receipt-closed-360-safe、manual-pan-restored-720。

## 审核支持与开发证据（不冒充亲跑）

- PM派发审核支持的fresh-audit.cjs/.log/.md：**11组独立断言、最终退出0**，只复用fake引擎骨架，未执行开发test。before缺失domain/GameConfig依当前未改文件补读；本角色核其报告、最终PASS日志及读取的28份输入SHA全部与实际一致，详independent-manifest.json。初次脚本路径/API错误已经修正，不当产品失败。合成单路线只证index0，复杂相机/多路几何由本角色与真实图承担。
- 开发tests.log：27核心+173地图+18存储+4Python=222、fail0；typecheck无诊断；build.log23:18:58 Finished。verification记录各命令退出0。未机械重复全套。保留Cocos子进程code:null/SIGTERM，wrapper退出0不等于原始引擎零异常。
- PM的18组相机补检为额外支持，未计入本角色6组。开发browser-check与browser-states为真实Cocos组件数据；来源、角色与mock边界均不混称。

## 发现与修后闭环

本角色最终未复现新增实质缺陷。开发/PM已锁定并修正两项：早期规划padding只保points导致车辆/marker裁切，以及manual低scale收卡/重开/resize误fit。最终本角色全部points+实际bbox/避控件断言通过、实际route-1图完整、手动pan低scale恢复一致，确认闭环。fixture直接book.accept造成错误30m规划图已由生产sample.accept路径重拍，不归咎生产。没有为凑发现扩展返工。

## 冻结指纹

独立实际核对final-source-sha.json **11/11**、screenshot-sha.json **41/41**、fixture-sha.json **4/4**一致；fresh-audit输入**28/28**一致。build-manifest实际构建**66/66**一致；隔离site同66文件逐字节一致（index仅去掉授权fixture脚本后比较）。见independent-manifest.json、independent-build-check.json、independent-fixture-build.json。

- MapSample：`fb58ca1b172f85d4ca49c3f4367106494bccab448bd0b21e32a350e80abfcf2e`
- CityMap：`1f4e47681fa54d0e7bee302367110149639cc9bfdf6c7e76941e2d35313c9392`
- OrderBook：`f57bc0c7472ca0d0e00e536073447f497d51d367182999ffd249634a8d6d9570`
- OrderPhone：`31105248c105f34b6812541edbacdcbfc0eaac160aa0ef4e18b580a88619c302`
- OrderPresentation：`541d11ec650364dfab41132a0dea9242ba6f5dca48113062b43274764ca38d86`
- fixture.js：`9863274d3ea0b17dc6fc4d629937601a98c6c5e4609b27e26afda9878422081c`

其余源及全部截图完整指纹见冻结清单与独立核对记录，未将历史图SHA冒充当前图。

## 限制/未测项

本角色仅写independent-*，未改生产/开发测试、未派代理、未访问用户4181页/存档或真实接单购买。fresh-audit支持来自PM另行派发，不是本角色自行开代理。4190样板禁生产start/update/save、不构造CountySaveStore、使用新内存OrderBook；Storage.setItem('storage')支持度探测每页被拦，不能称零访问或用户数据写入。

旧schema1/2与旧营业区外大厅list边界本轮未另造全组合独立复验，沿用开发相关全回归，不把schema3五态扩写成schema1/2已亲测。未实机逐一点击10张长备注卡、未全餐品/地名/路线组合遍历，长备注及首中尾主要依开发真实样板及所看图。未重测所有经济/时钟/长期业务；未将组件时间轴或mock当真实fps/多指手感。真机系统手势、连续操作体验、审美与用户最终验收仍待PM收集。
