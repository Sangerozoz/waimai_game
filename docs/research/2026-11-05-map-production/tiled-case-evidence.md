# Tiled成品案例与Cocos 3.8验证依据

核查：2026-11-05。仅资料研究；本轮没有安装、导入或运行示例，没有修改项目代码与素材。

## 成品案例：Brigador

**有可信成品案例，但它证明的是“编辑器＋专用资产管线＋游戏转换”，不是安装Tiled即可得到相同画面。**

Brigador官方Steam商店提供Modkit与地图编辑器DLC，含Tiled安装器、SpritePacker和社区地图包。[官方产品页](https://store.steampowered.com/app/468270/Brigador_Modkit__Map_Editor/)

官方[2021版Modkit PDF](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/468270/manuals/Brigador_Modkit___Map_Editor_DLC_Readme.pdf?t=1724871690)明确：

- 第2页：使用为Brigador定制的Tiled分支，启用Automapping。
- 第3～4页：TMX存编辑地图；TSX描述可放置对象与图集；Ctrl-E导出游戏JSON至`assets/levels`，外部修改后运行`genpack`打包。
- 第4～5页：SpritePacker从渲染图打包精灵，生成TSX、调整编辑器可视落点；TSX含偏移及游戏资产路径属性。

因此可借鉴的是：**先有规范素材，再确定性摆放，保留编辑源文件，通过转换绑定游戏对象。** 不能据此断言Brigador所有原始关卡均按同一版本Tiled制作、其定制导出器能用于Cocos，或其素材可以直接复用。本次未下载游戏/Modkit，也未检验其当前系统兼容性。

## Cocos 3.8的直接证据

1. [3.8 Tiled资源文档](https://docs.cocos.com/creator/3.8/manual/en/asset/tiledmap.html)列出TMX、PNG与部分TMX所需TSX的导入流程；版本表写明Creator 3.0及以上对应Tiled 1.4。它还说明3.8.5调整过瓦片边缘处理，图集需要外扩边缘像素。**不能把这张版本表解读为所有更新Tiled特性均支持。**
2. [3.8 TiledMap组件文档](https://docs.cocos.com/creator/3.8/manual/en/editor/components/tiledmap.html)提供TMX显示、自动创建图层，以及`TiledLayer.addUserNode`让节点与瓦片交错渲染的示例；明确遮挡按节点坐标判定，不按节点体积判定。旋转地图或放在3D相机时需关闭其内置裁剪。故它提供遮挡入口，但不会自动解决大楼、凹形对象或门廊的全部遮挡。
3. 该文档链接官方[3.x tiled-map示例目录](https://github.com/cocos/cocos-test-projects/tree/v3.8.7/assets/cases/middleware/tiled-map)。核查时有`shield-node`、`dynamic-tiled-map`、`puzzle`、`Hexa`、`object-group-image`场景。[package.json](https://raw.githubusercontent.com/cocos/cocos-test-projects/v3.8.7/package.json)的`creator.version`为3.8.7。

额外通过GitHub API读取了官方源码：[`shield-node.ts`](https://github.com/cocos/cocos-test-projects/blob/v3.8.7/assets/cases/middleware/tiled-map/shield-node.ts)实例化节点并调用`addUserNode`；[`dynamic-tiled-map.ts`](https://github.com/cocos/cocos-test-projects/blob/v3.8.7/assets/cases/middleware/tiled-map/dynamic-tiled-map.ts)分别加载`tile_iso_offset`及`tile_iso_offset_with_tsx`，创建TiledMap并设置`tmxAsset`。这比只引用一个功能名更直接，**但读源码不等于本项目运行成功**。本次API树查询分支提交为`f1070f7e79a7bc107c40c436db40c8c923a0a146`，示例分支后续可能更新。

## 不混用的旧证据

官方[`cocos/example-projects`](https://github.com/cocos/example-projects) README明确标注“Cocos Creator 2.x 开发范例”。其中示例只能作为历史/思路参考，不能冒称3.8工程验证。`cocos/cocos-test-projects`的3.8.7分支与3.8文档才是本次优先依据。

## 最小快速验证建议（尚未执行）

建议把**导入兼容**和**美术效果**分两道门槛，避免再花一周后才发现方法不成立：

1. 用实际项目的Creator补丁版本，在隔离的展示场景导入一个小TMX＋外部TSX＋PNG，包含两种地面、一个透明建筑、一棵树和一个可移动节点；记录Tiled/Creator版本与导出格式，不改正式导航。
2. 对齐原地图的几个已知世界点，验证一次坐标转换；移动节点经过建筑前后，检查锚点、大小、交错遮挡及缩放后的瓦片边缘。若直接TiledMap不能匹配既有任意角度道路，可让Tiled只编辑对象，再转换为现有JSON，由Cocos按原路显示。这是备用设计，尚无本地运行证据。
3. 前两步过关只说明工具链可用。再用一个完整街区验证旧失败的六项：美观、地面内容、种植区、入口朝向、骑手比例、阴影；必须拿出工程画面与第二个不同地块的复现结果。Tiled不会生成这些美术内容，也不会给现有1254整区图补出近景细节。

可以给出的结论是：**Tiled有成熟游戏采用的证据，Cocos 3.8也有官方TMX及节点遮挡入口，值得进行小规模兼容验证；本项目美术达标、原道路精确对应、无限地图/World流式加载及全县性能仍未验证。** 不把案例成功替代项目验证，不承诺完成时长。
