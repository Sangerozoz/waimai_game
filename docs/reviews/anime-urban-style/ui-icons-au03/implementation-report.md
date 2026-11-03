# AU03六图标真实入口接入 + 默认15m

**已实现，未测试，待阶段集中测试。** 已实际查看用户原图、读取intake；本轮未运行测试/typecheck/回归/渲染矩阵或独立复验，未操作用户游戏/存档，未commit/push。截图及实际小尺寸显示未验。

## 原图与裁框

用户原图保留docs/art/user-deliveries/2026-10-30-au03/ui-icons-six-original.png，原样复制至resources/map-sample/anime/au03/，新增Cocos导入meta；未重编码、重绘或另生图。asset-sha.json记录两处字节指纹。

按实际可见轮廓而非机械512格切割，SpriteFrame.rect采用原1536×1024左上像素坐标：coin[56,72,420,424]、heart[540,92,456,400]、station[1008,50,516,456]、vehicle[8,500,528,500]、bills[538,516,448,480]、map[990,548,534,432]。车辆前轮越过512线，裁框延伸至x536、y1000以保完整；各框给轮廓留边且避开邻图实体，没有以alpha阈值硬切暖光。crop-rectangles.json为权威映射数据；原图始终完整留存。

## 六处实际入口

| key | 实际接入与回退 |
|---|---|
| coin | MapSample钱包badge沿cartoonArt改用AU03切片，40×40框内等比，失败保留¥占位。 |
| heart | 评价badge此前直接原生heart；本次实际增加cartoonArt('heart')，40×40等比；失败保留原生爱心（原生占位缩至badge内）。 |
| station | 原站点cartoonArt key覆盖AU03；原grayscale和禁用/未开放逻辑保留，布局仍按真实图片宽度定位。 |
| vehicle | SampleUI.icon实际生成图入口恢复vehicle；底栏现调用icon因此实际加载新切片，失败保留原生车辆线图标。仅导航，不改地图车辆或车辆展示。 |
| bills | 同上接底栏真实账单入口，失败原生账单占位。 |
| map | 同上接底栏真实地图入口，失败原生折叠地图占位。 |

底栏三入口绘图中心从y10上移至y31，scale从2.25收至1.15，图片最大55.2设计单位，以给原文字上沿留间距；导航slot/触控尺寸及文字字号/位置不改。原生失败占位同样使用新中心及尺度。缓存、生命周期检查、异步失败保留占位均复用原CartoonArt机制，没有重复loader。

avatar仍为AU01人物母版，top-d/top-d-plus仍AU01新顶视共图，side-d/side-d-plus仍AU02新45度共图。暂停Ⅱ、取消/关闭、招募等未交新图入口保持原样，没有拿六图标替换不对应功能；餐品、其他状态图标等旧资源仍待后续批次。D+共图仍为临时资源状态，不称独立D+美术完成。

## 比例尺增量

用户本轮追加默认15m。CityMap新增DEFAULT_METRES=15，DEFAULT_SCALE=60/DEFAULT_METRES；初始scale、locate(resetZoom=true)、locateAnimated目标全部复用该常量，初始比例尺文字同步为15m。MIN_SCALE/MAX_SCALE、手动拖动/缩放和路线总览fit保持原代码，未把总览强制到15m。

## 构建与证据

最终交付命令npm run build:map --prefix delivery-game包装退出0，build.log记录2026-10-30 14:17:09 Finished，产物delivery-game/build/map-sample。比例尺指令在首轮AU03构建期间到达，首轮日志另存build-before-scale-increment.log，最终日志/指纹为包含15m的交付。4181静态index与当前主包HTTP200且SHA匹配，static-http.json保留结果；仅HTTP不启动游戏。

before/及before-sha.json记录本轮范围（含CityMap增量），production.patch记录实际差异，final-source-sha.json、build-manifest.json及delivery.json为最终源/构建指纹和结果。未将静态服务或构建成功写作六入口/比例尺实际渲染通过，后续阶段测试与用户体验验收单列。
