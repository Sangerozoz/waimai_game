# 车辆展示增量：独立静态代码质量审查

## 结论

**`passed: true`，仅本次增量静态质量通过。** 未发现新增安全问题或逻辑阻塞；`security_concerns`、`logic_errors` 均为空。两项非阻塞观察见下文。

- 审查者：`thr_psjr9wsysc`；父PM：`thr_axf6i4e89t`；同环境：`env_e54zrbdgxt`。
- 主目标：`V2GameUI.ts:20,409-432`、`VehicleShowcase.ts`及其meta。实读实际源码，不以作者交付报告代替判断。
- 本结论不是运行功能、Creator导入/构建、部署、用户体验或98%一致性通过。
- **U21独立沉浸场景仍为已声明素材阻塞**，中性底面仅为产品UI，不是街景/车库，也不是本增量新编程回归；不关闭U21。
- 机器可读结果、完整源码/依赖/图片SHA见[quality-review.json](quality-review.json)。

## 1. 实际候选与边界

当前工作区为 `/Users/sanger/Documents/ChatGPT/taptap 2`、分支 `codex/food-delivery`。三个主目标均未被git跟踪，限定目标的git diff为空；因此直接读取文件审查，而非把空diff当作无改动。

没有找到与作者记录的紧邻前版本SHA `6ee10985eafe1cf86af61cad1605cd617edafd0e27a40bc274994f09ba2e3684` 相符的独立前像。发现父PM较早 `rider-map-before/V2GameUI.ts`，实际SHA为 `a7528919732d797933317d9411910454337d71a31cca5de6faa4b8c422953671`，不能用其证明本次“仅一处import＋vehicles差分”。**本次批准的是下列当前源码版本与指定增量行为，不是整份V2GameUI所有历史变更。**

| 主目标 | 开始读取与收尾均相同的SHA-256 |
| --- | --- |
| `delivery-game/assets/scripts/map-sample/V2GameUI.ts` | `a33f933e5dc1e41827ac5cfbfaee1563d494d0acceae5fdaebec9321d10a1e96` |
| `delivery-game/assets/scripts/map-sample/VehicleShowcase.ts` | `aeee30bde4e3f121f39b395bd84feff5708b5dfb63cf4941cb91df6d9e00f14c` |
| `delivery-game/assets/scripts/map-sample/VehicleShowcase.ts.meta` | `5b18e74841d1937ef6894b6cadf03557c70b9ba6ca5fc993d35a6881602633d8` |

依赖只读至必要对外契约：SampleUI节点/Label/tap、V2ApprovedSkin的panel/action/levelBadge、VehicleSideArt映射、CartoonArt对外contain/事件/节点保护、UIArtResources公开类型/签名；另读尺寸常量、投影函数及购买命令定义。未扩入UIArtResources内部加载实现，未改公共API/key/事件或Game接口。

## 2. 规格与联动静态核对

1. **同一选中车型贯穿全部信息与购买目标。**
   - `delivery-game/assets/scripts/map-sample/V2GameUI.ts:410-420`：`v=CONFIG.vehicles[this.model-1]`；主图用`v.id`，名称/速度/容量/收入加成/价格均用`v`，拥有数按真实`state.vehicles`中`modelId===v.id`计数；购买闭包捕获`v.id`，不在异步图片返回时更改目标。
   - 实读配置并静态解析，车型正好10档、10个唯一id，依次为1..10。因此当前数组索引与modelId约定吻合；不是凭作者报数。
   - 当前配置车辆完整属性为速度、容量、收入系数，界面均展示；新购Lv.1与`V2EconomySession.ts:111-112`创建level=1的定义一致。拥有数不是图中示例值，也不把starter误计入某个数字车型。

2. **唯一购买，不从缩略宫格误购。**
   - `V2GameUI.ts:420`仅一个购买入口；`:426-430`宫格只显示图片/名称/拥有数/选中标记，tap只设置`this.model=model.id`再重绘。
   - `V2RuntimeController.ts:156` → `V2DispatchSession.ts:57-60` → `V2EconomySession.ts:111-112`使用已存在的`{type:'buyVehicle',modelId:number}`链路；价格读取同一配置项。不新增业务状态或经济资格。
   - `V2GameUI.ts:70`捕获命令错误后重绘；本增量未绕过既有资金/交易约束，也未为验证购买造库存。

3. **三列十档、保位key不随车型改变。**
   - `V2GameUI.ts:424-430`按`columnWidth(3)`与原配置循环；scroll key固定为`vehicles`，不含modelId。
   - `:85-89`先采集旧ScrollView offset再停用/销毁旧页面；`:165-173`恢复原key的offset并钳制有效范围，延迟回调还检查旧ScrollView是否有效及是否仍为当前实例。快速重绘的旧回调不会覆盖新实例。
   - 所有重绘都沿上述同一机制，包括切车与购买成功/失败；这里只确认代码路径成立，未验证实际滚动手感、触控事件顺序或刷新后的数值。

4. **原生比例与完整车体。**
   - `VehicleShowcase.ts:22`仅调用`vehicleSideArt`；`VehicleSideArt.ts:4-5`十档key映射与现有原件对应。
   - 核对十个相关key最终均为原件全画布`rect:[0,0,1,1]`；十张实际PNG均为1536×1024，逐张SHA与来源记录相符。未裁切或写入原件。
   - `CartoonArt.ts:141-150`按`min(width/originalWidth,height/originalHeight)`contain；本次预览给644×252容器，原件按378×252显示，落在660×268遮罩内部，四周保留空间，不在此增量剪轮/外卖箱。
   - 已目视[静态排版PNG](../../../../art/2026-11-05-vehicle-showcase/model-03-product-layout-static.png)与[十原件联系表](../../../../art/2026-11-05-vehicle-showcase/source-vehicles-contact-sheet.png)：未见轮或后箱被本次排版切断、拉伸；第10档仍为悬浮车。它们不是游戏截图，不能证明Web轻量包/引擎实际加载后的每档显示。

## 3. Mask、绘制、异步与生命周期

- **遮罩尺寸与Graphics分工正确。** `VehicleShowcase.ts:11-18`先由`item`设置UITransform尺寸，再加`GRAPHICS_RECT` Mask；渐变画在独立子节点`NeutralProductSurface`，不复用/清空Mask自身的Graphics。40行是单次创建时绘制，不是每帧重画。
- **核对真实CC定义，而非猜测API。** 项目声明引用实际安装的Cocos Creator 3.8.8。其`engine/bin/.declarations/cc.d.ts:2685-2701,3122-3123,3294,3363,17365,23415,46022,75873`包含Mask/Graphics导出别名、`Mask.Type.GRAPHICS_RECT`、`Color`构造、`rect/fill`与严格`isValid`定义；`UITransform.setContentSize`也有数值重载。
- 实读引擎`cocos/2d/components/mask.ts:300-330,395-426`：启用时按UITransform更新矩形并监听尺寸，Mask自行管理其Graphics及销毁。新增helper不需要另造Stencil组件或持有全局清理器。meta可解析，UUID在`delivery-game/assets`的meta搜索中只匹配本文件；没有Creator实际导入证据。
- **异步返回不串车型。** 每次重绘创建独立picture，绑定自己的modelId与fallback节点；返回结果只写该picture。原对外`CartoonArt.ts:146-151`成功回调检查parent与picture严格有效性，失败回调检查picture；页面重绘先停用旧树再销毁，新helper未建立共享“当前图片”变量。
- **新主预览失败可见。** `VehicleShowcase.ts:20-26`先创建可见pending Label，再调用车图。Promise回调在创建返回后执行，失败事件监听可及时注册；初始同步loading事件即使先发出，也无需监听来显示pending。成功由既有fallback参数隐藏Label；失败时明确显示“车型图片未载入，请重新打开本页”，并用`isValid(pending,true)`避免给已销毁组件写string。
- 监听器挂在本次picture本身，捕获的pending也属于同一viewport；没有全局订阅、定时器、重试循环或新的永久节点引用。未故障注入，不能把此静态保护链写成真实竞态/销毁测试通过。
- 新增import/helper及所审vehicles内容未见凭据、动态代码执行、外部传输、文件写入、存档更改或地图资源引用。

## 4. 布局矩形核算

按实际`V2Spacing.ts`与`V2ImageSkin.ts:68-72`转换，用Python做纯数值核算，未执行游戏代码：

- 详情卡：684×444，世界y约 **122.551～566.551**。
- 主预览：660×268，x为−330～330，世界y约 **290.551～558.551**，在卡内。
- 唯一购买：212×62，x为106～318，世界y约 **155.551～217.551**，在卡内，不被预览Mask覆盖。速度/容量位于其上，收入加成在左侧，声明矩形不相交。
- 宫格标题中心y约92.959；宫格视口y约 **−499.988～67.711**，详情卡下边至视口上边相隔约54.840。宫格不会盖住购买入口。
- 宫格每列220宽、12间距；4行×205=820内容高，视口高约567.699，最大offset约252.301。最后一格下边位于内容−809，位于820内容范围内，第10档可滚到。
- 宫格下边比底部导航上边高约14.537设计单位，不因本次详情卡增高而与导航重叠。

这些是声明节点矩形与静态图片证据，不包含真实字体绘制边缘、异步皮肤素材边缘或运行中的点击命中验证。

## 5. 非阻塞建议

- **Q01，`V2GameUI.ts:428`：** 宫格保留现有“车型载入中”fallback。失败时仍可见，不是空白，但没有新主预览那样区分最终失败。后续若统一，只追加同一事件的失败文案即可；不以此把保留路径归为本增量新增逻辑回归，不扩查loader。
- **Q02，`V2GameUI.ts:413-416`：** 主预览下边与名称Label节点上边仅约1.4设计单位。当前矩形与离线PNG均未显示重叠，不据此改设计；后续集中验证时检查真实字体与最长购买文案。

## 6. 未执行、既有缺口与交回

**未执行任何tests、typecheck、回归、游戏/存档、合成快照、Creator构建或部署。** 图片只查看已有文件及尺寸/SHA，没有运行作者合成脚本或造库存。JSON解析、源码文本静态解析、哈希与上述矩形算术不是项目功能测试。

待父PM在获准阶段集中验证：十档快速切换后的预览/价格/购买目标一致；成功/不足资金后的真实数量；深滚动处切车/买车/离页再回的offset；缓存命中/图片失败/离页销毁的fallback与旧回调；真实字体和底部点击范围。

ready/组数、关闭×、去重开、订单KG/¥/去pin、地图未解锁、账单去币图等其他已批准代码未由本审查修改，也不在此重新授予功能通过。待确认骑手新卡、万元近似规则未夹带实施。每帧routeSnapshot克隆仍为已知既有性能缺口，未扩写Game接口，不将其列为本增量回归。

独立场景素材不合格/未到位的状态单独保留；本线不写、加工、组织或派发地图素材、地图数据、地图制作方案。没有向其他线程派工。

**只写本目录`quality-review.json`与`quality-review.md`。源码只读范围已释放，交回父PM处理后续修复、集成、获准构建与验收。**
