# AU01 人物头像与D档地图车实际接入

**已实现，未测试，待阶段集中测试。** 已看用户接受的人物原图与车辆顶视原图，并按style-bible和style-migration-checklist执行接入。无测试/typecheck/回归/渲染核验，未操作用户游戏/存档，未commit/push。

| key | 真实接入 | 处理与状态 |
|---|---|---|
| avatar | 用户接受的rider-master-original.png | 在CartoonArt中用SpriteFrame.rect取原1024×1536母版的x340/y0/w360/h360头肩区，运行时显示92×92；脸、头发与肩部直接来自母版，没有重新设计脸，没有另生图或派生裁图文件。已接入，未测试。 |
| top-d | 用户交回vehicle-top-original.png | 完整1024×1536原图与alpha导入，保留暖光半透明边，不用阈值抠图。沿MapVehicle的80×128显示框、-90°车头朝向补偿、CityMap道路角度/锚点/比例及现有触控逻辑。已作为D档新风格样板接入，未测试，不能代称车辆全系列获用户接受。 |
| top-d-plus | 旧vehicle-sheet | 未替换，等待同车系D+顶视图。 |
| side-d / side-d-plus | 旧vehicle-sheet | 未替换，等待独立展示视角；没有将顶视图用于侧视。 |

两张文件原样复制到`delivery-game/assets/resources/map-sample/anime/au01/`，同时保留docs/art/user-deliveries/2026-10-30-au01/用户原件。asset-sha.json记录原件与导入件指纹；PNG未重编码，原始alpha保持。新增Cocos图像导入metadata。未编写永久派生工具。avatar/top-d通过原有共享loader加载和重试；失败时沿现有原生占位回退，旧图集文件留存。新图接入不等于旧图标/餐品/其他车辆全量替换完成。

唯一修改的生产脚本为CartoonArt.ts中两个key映射。MapVehicle和MapSample仅纳入before基线，逻辑未改；M2底座与按钮增量保留。其他旧头像图集切片留在源库存但当前avatar key已改指新母版；状态图标、餐品、D+和侧视车仍需继续替换。

交付命令`npm run build:map --prefix delivery-game`包装退出0，build.log记录实际Finished；产物为4181使用的delivery-game/build/map-sample。既有静态服务仍监听127.0.0.1:4181并指向该目录；仅HTTP请求首页确认服务，status=200，响应index与当前构建index的SHA记录在static-http.json。没有用浏览器打开游戏或读取/写入localStorage。

before/、before-sha.json记录接入前基线，production.patch记录脚本映射差异，final-source-sha.json及build-manifest.json为本轮最新源码与构建指纹，delivery.json为命令/服务结果。图片裁框的小尺寸清晰度、透明边效果、车辆实际朝向显示与完整页面体验均未渲染复验；待用户说阶段完成后集中测试，审美体验由用户确认。
