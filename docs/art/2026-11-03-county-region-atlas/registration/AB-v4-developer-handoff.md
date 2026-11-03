# A-v3 + B-v4 可接入资料

实际观察结论：B-v4按诊断腾出了北侧共享原路通道，先前的原路穿楼已消除。A/B共享路口、向东横路及西南街端仍有局部路侧偏差，但已具备连续街道画面，适用用户允许少量穿帮的制作尺度。无需为局部纹理再无限重生。

## 可直接消费的两个region entry

- `region-A-AB-v4-runtime-entry.json`
- `region-B-v4-runtime-entry.json`

两者均有真实锚点、统一原生比例、SHA、3个以上分散控制点、全已观测残差、实际画面道路分界ownershipPolygonUV及独立routeCoverageMapPolygon。entry的`registration.status`留为preview-only，供PM在收取本次证据后显式翻为ready；开发不能把原始名义例值7.8套回。

A图相对素材文件名REGION-A-v3.png，原生源在`docs/art/2026-11-03-whole-region-map/REGION-A-v3.png`；B图相对文件名REGION-B-v4.png，源在`../images/REGION-B-v4.png`。素材包复制必须原字节，诊断副本不进入游戏。

`A-B-v4-production-handoff.json`提供同一条接缝的native/source/world坐标与互补分界。接缝沿实际共用街道及外轮廓，不是强行把生成图套回120m数学正方形。A保留西北侧完整楼群，B保留东南侧楼群；实际已在统一世界比例诊断合成图核看，没有观察到沿当前分界切断完整楼体。

## routeCoverage保持在内部实见走廊

A覆盖原主干两核心路口间及向共享路口的源支路；B覆盖共享北段map y>=78附近、共享路口到东侧路口的主横路。两个source-map信任多边形在共享路口重叠，防止因为图边界不准而永远隐藏骑手。北部最外端和南下出图端不自动扩大为已可信路线。

routeCoverage只定义信任范围，原路中心线与蓝框配送边界仍由开发原接口限制；它不是允许在该多边形内任意穿越楼体。中央虚构支路已被B4院落铺装替代，不新增原路。

## 误差与事实边界

- A既有全部观测max47.69px（低置信地面角）；内部3路口max11.43px。
- B4固定B2变换后，内部标定基点max19.67px，全部当前观测max34.60px（北外边界）。人工标注约±5–12px，不声称精确到像素。
- B4目标[498,373]现在在路下缘附近，距中心约15–25px，已不再是屋顶；上游[733,208]在路侧附近。
- `diagnostic/A-B-v4-ownership-composite.jpg`仅为素材生产的统一world裁切诊断，非Cocos运行截图。存在道路宽度、路缘及颜色小差，不声称像素级无缝、全县完成或游戏测试通过。

原PNG/原city未修改；没有tests/typecheck/回归/页面或正式存档操作。开发仅按PM明确派工集成独立工程与必要构建，保护旧认可入口。
