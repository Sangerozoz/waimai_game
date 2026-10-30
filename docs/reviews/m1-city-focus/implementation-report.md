# M1 CITY-FOCUS 开发交付

2026-10-29。本轮三项实施完成，生产源码已冻结，最终精确SHA见final-source-sha.json，待固定测试/美术复核。保持M1，未操作用户4181游戏或存档。

## 爱心按金币可见范围校准

金币图集实际alpha>32范围283×292，放入40适配框后的可见36.516×37.677设计像素。原爱心节点1.2并不代表与金币同体量；现将实际心形贝塞尔轮廓/多层厚边全体校准至36.546×37.677，xyScale=[1.05,1.098]，宽差0.030、高差小于0.001。icon-visible-bounds.json记录生产实际值，独立角色independent-icon.json复算一致。保留渐进色、厚度、高光和胶囊内距，无新生图。标准及360×560图见home截图。

## 平滑定位：最终只采用固定终态偏移方案

用户显式按钮→city.locateAnimated，启动/内部locate仍瞬时。动画为0.6秒easeInOutCubic，同一e驱动scale与offset；最终scale=2/30m并跟随当前骑手。起始相机offset和scale保留；offset=lerp(startOffset,-currentRider*DEFAULT_SCALE,e)。静止目标可得project(t)=(1-e)*project(0)，世界中心始终为起始中心与目标的正权重组合，单调收敛、不越过目标。骑手每帧从真实riderPoint读取，非固定旧起点。

root调试过程保留：首版把旧scale偏移和当前scale目标混合，出现骑手越过中心；pan-red.log复现。按PM提出的世界中心同e方案试验后，边缘case发现放大可把骑手推出屏，最终按PM更新规格退回固定终态偏移方案。world-center-red.log仅为已放弃的“世界中心恰好同e”假设历史，不能当成最终契约。当前测试使用两起点世界中心在线段内、距离单调、屏幕投影单调可见的断言。

render-frames.log及10张最终帧图为同一源码/构建批次：普通起点275.724的屏幕X依次275.724/258.491/137.862/17.233/0；边缘起点340依次340/318.75/170/21.25/0；scale两组均0.6/0.6875/1.3/1.9125/2。终点project[0,0]、follow=true，两组均无此前离屏再回来问题。世界中心及offset逐帧同日志保存。

重复点击从当前镜头重定向；touchStart、zoom/滚轮、内部locate/overview/focusRoute取消动画。后台onHide、rebuildLayout及onDestroy显式cancelLocate。没有定时器、Tween回调链；MapSample.update在前台推进当前city，旧对象不残留回调。动画每帧只设镜头transform/覆盖层/比例尺；详情0.1秒刷新缓存，主干道按有效线宽boost缓存（本段0.6→2始终boost1），不逐帧重画，路线仅终态sync重画。

## 城区有效营业池与兼容

原始→v1→v2→v3旧流水线保留为preparePreviousCity，旧385项全字段前缀不变；新UrbanCatalog只重建有效城区池并追加新地址。按原play/dispatch范围与原双向连通分量、urban分类筛选；东/西框内四邻街区及格按建筑数最大余数分配，首点优先建筑质心，后续最远点补齐，35米全点排斥及70米商家排斥。

实际输出：全量POI617（旧385+新增232）；营业池320，其中城区60商家/180顾客、城郊12/36、远郊8/24。东168/西72，两框均补足，无框间转移。最小点距35.2247米，商家77.7398米，四边最小play留白453.3米。每300米格数量见catalog-results.json，不缩urbanBounds，不改原区域订单配额/跨区判定/时限。

catalog v4采用dispatch-v4+dispatchBounds+operatingPOIs指纹；原节点/道路/POI哈希仍纳入。旧raw/v1/v2/v3指纹链ef9d9c7/7192a588/95a923c8/876eebc5完整保留，当前bf421530。v3直接输入与raw输出同v4，重复prepare/restore幂等。隔离真实OrderBook证明旧活动端点/路线/进度原样恢复，继续完成与重复结算不重复入账，真实节点几何改动被拒绝；12轮实际刷新候选中新增商家21个、新增顾客21个参与。原候选仍走既有恢复过滤，不免费清档或改业务规则。OrderBook文件本轮未修改。

## 最终验证

- npm test退出0：27核心+163地图+18存储+4Python地图数据，共212通过、0失败。最终已包含普通/边缘定位、移动骑手、重定向、取消、v4营业数量及原区域/时限/保存/结算回归。
- npm run typecheck退出0。
- npm run build:map包装脚本退出0；22:27:00 map-sample Finished。build.log保留build-script子进程SIGTERM/code null诊断；原始Cocos退出码未单独捕获，包装允许0或36，不宣称零异常。
- catalog-evidence.cjs运行退出0，catalog-results.json记录前缀/幂等/实际派单/活动恢复完成/单次结算/真实几何拒绝及分布数。
- gallery与截图SHA：相同视角v3/v4分布、标准/短屏home、两个定位起点0–0.6秒五帧。不是模拟HTML，调用真实生产Cocos组件。

## 修改与权限边界

实际修改MapSample、CityMap、PlaceCatalog、MapTypes、CountySnapshot，新增UrbanCatalog。before保存全部已改已有文件，production.patch为精确差异；SampleUI、OrderBook也保存校验但未改。final-source-sha.json包括最终验收版本；后续无关改动停止。

隔离fixture端口4187/独立cityfocus会话，替换start/update/save，用真实地图和新内存OrderBook，未创建CountySaveStore。相机帧以advanceLocate(.15)推进真实生产相机，时间标注是组件时间轴，不是声称实际墙钟录制。Storage原型读写全部拦截，Cocos setItem('storage')支持探针每页一次抛错阻止，日志如实保留，不称零访问。分布旧版使用preparePreviousCity复现同一镜头，不篡改用户档。

仅技术/静态开发验证完成；待固定测试和美术核对本批最终SHA/帧图，用户真机流畅手感、连续真实业务和审美验收仍待PM收集。未新增M2规则、经济、时钟或保存制度。

## 冻结补充

最终CityMap SHA=b03591de73578551b804f9d371e0e3d9e38320fa54d60d38cdda8e6ddb1a4621，与本报告最终固定终态偏移帧图/构建相符。普通和边缘起点的中间project均单调收敛；非最终的世界中心同e试验不属于冻结版本。catalog-results新增四边分别的留白，未因此改代码或重复全套测试。固定测试的independent-density.log已记录3/3通过，实际RoadRouter逐个检查320营业点从起始商家双向可达（该项是独立测试证据，不冒称本脚本重复执行）；其完整最终结论仍以独立报告为准。
