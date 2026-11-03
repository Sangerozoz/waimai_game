# D/D+新车辆资源映射修复

**已实现，未测试，待阶段集中测试。** 仅源码入口诊断、资源映射修改、必要交付构建与静态HTTP；未打开用户游戏或读取用户存档，不能由本次定位推断用户实际车辆档位。未运行测试、typecheck、渲染复验或回归，未commit/push。

根因已由实际入口确认：MapVehicle.setTier在tier=2请求top-d-plus；MapSample.openGarage传当前p.vehicleTier给vehicleSideArt，后者tier=2请求side-d-plus。此前CartoonArt只覆盖top-d/side-d，新图未覆盖两个D+ key，D+仍命中旧vehicle-sheet切片。

最小修复仅CartoonArt：top-d-plus显式别名到top-d（au01新动漫顶视）；side-d-plus别名到side-d（au02新动漫45度展示）。两个入口继续按原档位选key，但当前开放D和D+均不再用旧图集车辆切片。D+暂与D共用原图，不做未经批准变色，不称独立D+素材完成；后续独立D+素材实际交付时替换其key。顶视与展示用途没有混用，车辆价格/速度/载重/经济/存档及取消配送/暂停均未修改。

共享frame缓存仍按key缓存本版本资源，新版本页面正常重启后重新初始化；没有操作用户页面来主动清缓存或改档位。

命令npm run build:map --prefix delivery-game包装退出0，实际日志build.log记录Finished。产物delivery-game/build/map-sample。4181服务继续存活；只HTTP请求index.html及当前assets/main主包，均200且逐字节SHA与本次构建一致，详static-http.json。没有浏览器或游戏层操作；此静态诊断不等于实际显示已测试。

before/、before-sha.json保留真实改前CartoonArt与两个显示入口源码；production.patch为本轮映射差异；final-source-sha.json、build-manifest.json及delivery.json记录最终源码/构建指纹与命令结果。新映射、D/D+实际显示、用户视觉体验仍待阶段测试及用户确认。
