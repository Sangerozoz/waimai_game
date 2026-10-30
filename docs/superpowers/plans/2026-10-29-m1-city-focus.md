# M1城市聚集与定位动画实施计划

**目标：** 在M1完成本轮三项用户反馈，保留历史进度和现有订单规则。
**架构：** 头像栏继续复用SampleUI；CityMap管理一次可中断的定位状态，MapSample每帧驱动；PlaceCatalog保留旧生成链，在其输出上生成v4营业池。
**技术：** Cocos Creator 3.8.8、TypeScript、既有Node/Python测试与隔离Cocos样板。
**执行：** 固定开发会话负责生产，固定测试独立复核；PM负责本计划与收口。按用户已授权方式执行，不重复创建实现或审查代理。

全局约束见本轮spec，重点为0.6秒同步easeInOutCubic、240城区/80郊区、35米/70米间距、450米边界及完整旧POI前缀。使用本轮快照作为差异基准，不以git HEAD代表现有未跟踪项目。

## 1. 可见图标和相机动画

文件：SampleUI.ts、MapSample.ts、CityMap.ts；测试map-hud、map-gestures及相应图形测试。
接口：保留locate(resetZoom=false)供内部立即定位，显式按钮调用locateAnimated():void；advanceLocate(dt:number):void推进，cancelLocate():void中断。

- [x] 保存before与SHA；记录现有图标可见范围、定位瞬切的失败回归。
- [x] 校准心形到金币透明区裁剪后的大小；保留原图标语义和材质。
- [x] 使用单一状态保存开始scale/offset与elapsed，统一插值；每帧以当前riderPoint计算目标，完成置follow=true并精确同步。
- [x] 在真实生产MapSample.update驱动；验证idle也能推进，后台/rebuild/destroy取消；触摸/滚轮/重复点击不争夺控制。
- [x] 红绿回归覆盖中间帧位置和scale同时改变、终态及连续跟随、中断/重复；检查动画帧渲染量。

## 2. v4城市目录和兼容

文件：PlaceCatalog.ts（必要时提取专责选点模块）、MapTypes.ts、CountySnapshot.ts；仅必要时改OrderBook.ts候选迁移。测试city-content、dispatch、county-save相关。
接口：prepareCity(data:CityData):CityData继续返回确定、缓存且幂等目录；countyMapId(data:CityData):string明确包含新版有效目录规则；OrderBook继续消费operatingPOIs。

- [x] 冻结v3全量385个POI和历史指纹；新增修改文件先补快照。
- [x] 建立240城区/60商180顾、密格聚集、点距、可达性及旧前缀的失败回归。
- [x] 在保留v3前缀上重选合格旧点并尾部追加新点；按策划报告分东/西及街区权重，受容量限制的份额转移显式报告。
- [x] v4有效池320，郊/远营业点保持；版本/hash与legacyMapIds链同步；v3输入直升和v4幂等。
- [x] 用真实OrderBook证明新商家/顾客参与派单、原区域/时限保证保留；旧活动全状态恢复及完成单次结算。

## 3. 渲染与交付

- [x] 真实隔离Cocos样板出标准/窄屏心与金币图；定位0/.15/.3/.45/.6秒帧和连续镜头录制或等效证据。
- [x] 同镜头同scale城市点位前后图及全营业区点位分布图，附目标/实际数、分框、格、间距、可达和留白。
- [x] 完整npm test、typecheck、build:map，保存退出码、日志、最终源及图像SHA和实施报告。
- [x] 固定测试独立核对技术与存档边界，美术仅复核图标视觉大小；如有实质问题定向修后回归。
- [x] PM核对当前源指纹、独立报告与4181构建字节，更新团队快照后交用户体验。
