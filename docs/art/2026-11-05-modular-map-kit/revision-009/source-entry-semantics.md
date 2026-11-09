# 只读地图入口语义：导航停靠节点与绘制门点分层

这不是业务/产品修改；只约束地图的原地块适配。原city/路由/POI/经济/存档全部不动。

实际只读证据：
- delivery-game/assets/scripts/map-sample/MapTypes.ts:3-14：MapPOI仅name/node/kind/address，没有buildingId或原生门像素；buildings是独立Point[][]。
- PlaceCatalog.ts:48-64、76-89、103-120：地址从道路连通图的节点pool创建，pois.push(name,node=n.id,kind,address)，不是按建筑门像素生成。
- OrderBook.ts:319-335：取送路由的from/to直接是pois[*].node；不是新图sprite的门像素。
- CountySampleBridge.ts:20-23：显示适配器按poi.node取得坐标发送stop，未绑定某张楼图的门。
- 当前静态city.json的源POI拓扑计数：{"rawPOIs": 128, "POIsWithKnownNode": 128, "POINodesReferencedByRoads": 128}。这不是运行时已解锁/已运营地址数量；prepareCity还会构建目录，本次未运行业务。

因此，不能无证把全部poi.node等同“必须压到sprite门槛的建筑门世界坐标”。原节点/路线/名称保留不动；图中可见真实门是另一个美术点。若有确实已声明原物理门/门廊的额外证据则仍严格遵守，不泛化豁免。

下一轮候选可分记navigationStopNodeId及其原坐标、visualDoorPixel/World、sourceCarrier、visualApproachPolygon与道路肩侧接近点。视觉步行面在原车道外连至路肩，不能为了“接node”把瓷砖画过车道或新建导航边。图层接近关系是设计关联，原数据无building绑定时不得冒称原source已经指定那幢楼；正式交互仍完全用原node，不挪业务点或改里程。

此规则不表示任何候选已精密门槛/导航或用户验收通过；它只是避免制作筛选中把路图节点和图片门点误作同一个约束而错拒全部业务载体。
