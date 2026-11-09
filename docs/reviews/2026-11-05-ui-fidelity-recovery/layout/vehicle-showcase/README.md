# U21车辆展示交付：纯产品UI已写，独立场景素材阻塞

父PM：`thr_axf6i4e89t`；工作线：`thr_rddariqvsa`。共享checkout保留，未fork/worktree、清理、commit/push。

## 实际改动与绝对路径

1. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2GameUI.ts:20,409–425`
   - 只新增展示helper import并改`vehicles()`呈现：全宽当前车型图；名称、真实拥有数、新购Lv.1、完整属性与唯一购买下置。
   - 价格／属性／购买modelId／拥有数仍绑定同一个选中`v`，原`buyVehicle`命令不改。
   - 顶部框保留原顶缘，尺寸684×444；图框660×268。标题/宫格顶部下移，仍三列十档，滚动key `vehicles`、tileHeight194、rowStep205与恢复机制不变。
2. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/VehicleShowcase.ts:10`及同名`.meta`
   - 新纯产品UI helper，原车图等比contain；中性浅色UI面不是城市／车库场景。
   - 只调用已见`vehicleSideArt`，没有新Game API、存档或公共manifest接口。
3. `/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-vehicle-showcase/`
   - 实际PNG、原件联系表、逐车SHA、来源manifest与Pillow复现脚本，见下。

`V2ApprovedSkin.ts`未改（前后SHA均`e3be2228f8ac59746fa412146b289b2c0a267fa18184fcf5859460f59f972e8e`）。CartoonArt／V2ImageSkin／UIArtResources／VehicleSideArt／FoodImages／公共manifest均未写。

## 可查看证据

- [单张排版PNG](../../../../art/2026-11-05-vehicle-showcase/model-03-product-layout-static.png)：**684×444 RGB**，SHA `e973388900142e031f526514432ff6e7f4a6a1c5c35c7cdedb9463edbb068e0a`。
- [单张车图框PNG](../../../../art/2026-11-05-vehicle-showcase/model-03-product-preview-static.png)：**660×268 RGB**，SHA `e4b8857d54c853025fe60f7d04bdc58fd7da0fd3775e2d462138a8a16e5bff27`。
- [来源manifest](../../../../art/2026-11-05-vehicle-showcase/source-manifest.json)：批准原图、10档原件、独立车库弃用原因、真实尺寸/SHA、源码前后SHA和未验证项。
- [10档原件联系表](../../../../art/2026-11-05-vehicle-showcase/source-vehicles-contact-sheet.png)：1250×520；采集计数由Python实算为10条／10唯一modelId。

以上都是静态产品图片，不是游戏截图，不展示用户已拥有。默认model 3原生1536×1024完整画布仅缩小为378×252；无重绘、无裁掉车轮／后箱、无插值冒充高清。

## 范围纠正与U21素材阻塞

- 中断前只完成原件联系表／SHA清单，没有地图衍生PNG，也没有接入新的地图背景引用；本轮地图衍生隔离文件清单为**空**。原有地图页保留，不向地图线派工。
- 修正后只读查看**独立产品**旧车库`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/vehicle-shop-production/garage-clean-background.png`，1374×1145，SHA `5859bc695354277505d15c1af22b647d6aabd09d2152aa94a6a2a42504d00021`。目视是强暖黄夕照、偏暗工位，不能覆盖当前明亮中性宽幅方向，未裁切／染色／复制／集成。
- 因此**U21仍为独立产品场景素材阻塞**。中性UI面不是街景，未达成“真实场景＋车”的交付，不把纯排版当完成。
- 未来只允许独立产品场景，需实看车角度／尺度／轮地／阴影；model10为原生悬浮车，不能画成轮式摩托。

## 静态追踪与未验证

- 新helper→原VehicleSideArt→CartoonArt→UIArtResources沿既有图片链，原节点存活保护保留。预览加载失败用可见文字，未做故障注入。
- 原`CONFIG.vehicles`循环、选中赋值与scroll key不改；动态所有权／购买目标与属性来自同一选中对象。此为静态追踪，**不是运行联动通过**。
- 本轮源码改动局限`vehicles()`与import；原ready/continueTrip/组数、订单KG/¥/时间偏移、地图未解锁、账单无币图、四页无标题、tripId缓存／新批跟随、低体力补给和滚动恢复未动。万元／骑手卡未动。
- 未执行tests、主动typecheck、回归、游戏／真实或合成存档、Creator构建或部署。编辑工具曾自动提示新helper的`padStart`目标库问题，已直接改成现有`Color`构造，不据此声称类型或运行通过。
- 4182／旧v2-candidate不能代表本次源码；获准后的必要构建／非消费预览仍由PM统一。
- 每帧routeSnapshot深拷贝性能缺口保持，未跨写或发明Game API。

**不关闭U21，不报98%／功能通过／用户验收。**
