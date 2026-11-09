# 五种楼型＋混合树灯街段：独立接入交付

2026-11-05。已在现有4186服务真正打开 Cocos 页面，实看总体与近景；不是素材清单交付。未做用户验收、游戏测试、typecheck、回归、存档操作、commit/push，未启动/终止任何服务器。

- 总体：http://127.0.0.1:4186/revision-005/viewer/?view=overall
- 近景：http://127.0.0.1:4186/revision-005/viewer/?view=close
- 可编辑地图绝对路径：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/integration/mixed-street.tmj`
- 运行包：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/viewer/`
- 运行派生图：上述 viewer 的 `assets/`；integration/assets 保留导出用副本与灯派生元数据。均为派生图，不是新的原生输出。
- 真实截图：[总体](cocos-overall.jpg)、[多楼近景](cocos-close.jpg)。近景有意放大，会截到最外侧高楼顶部；完整范围以总体截图为准。

## 实际显示与字节

五栋不同楼全部载入并可见；22静态实例＝5楼＋6灯＋3树池树＋6自然阔叶树＋2针叶比较树。38地面多边形全部导出；草坪、种植、草甸使用受控颜色，不是新生纹理。铺装与原路使用已有材质，原路在全部地面多边形之后绘制。

14张唯一PNG全部长边≤280，合计1,152,460 bytes；viewer全包43文件、4,715,107 bytes（含引擎）。实例按file+SHA共用解码image，按image共用SpriteFrame。实际 `__mapTextureStats`：uniqueAssetImages=14、nativeFramesCreated=12、canvasFramesCreated=2；后两项含程序地面/骑手阴影，材料不各建原生Frame。D骑手仅原有内存演示，车辆多样性尚未完成。

实际读回 `__mapPreviewOrder` 共24节点＝22静态＋D骑手＋阴影。静态editorOrder连续0～21，与Tiled导出顺序一致；动态节点插入不改变静态相对次序。逐节点位置核对最大差4.38e-8引擎单位（壳内投影常数舍入，核对容差1e-6）。详见 runtime-readback.json、browser-overall.json、browser-close.json、export-report.json。

## 校准与编辑

asset-calibration.json 保留B01原nativePPU111.2618392940353、anchorPixel[626.5,920.5]及原锚点；T01保持175PPU与原anchorPixel[620,1020]。其余楼从已实看原图手估可见地基三角点、推断隐藏后角，以PM候选长深对地基边作一个正标量最小二乘估算。树根、灯脚为手估，灯的175PPU是在真实画面显示初始比例过小后作正等比修订；没有精密配准或真实米制尺寸结论。PNG裁边后anchorUV按原像素转换，worldSizeUnits按原裁框像素/原PPU计算，缩小运行图不缩小世界物体。未镜像/平面旋转/非等比变形。

`python3 integration/mixed_street.py export`（从revision-005运行）仅导出到本viewer。`init`面对现有地图/viewer会拒绝，已验证未重置地图。支持对象位置、正等比尺寸、对象/层可见性、group offsetx/offsety、层顺序与index/topdown顺序；拒绝旋转、镜像及非等比尺寸。B01原锚点/比例受保护，其他对象可编辑。Tiled地面组可编辑全部多边形，原路图层只作锁定可视参考，真实道路仍读取不变JSON。

## SHA与边界

provenance-check.json 对十件实际原生PNG均重新读取tool源文件并比较SHA，而非采信自报。全部相等。inputs-before.json 的177项只读输入（native、revision-004全目录、runtime-280全目录、B01校准/原图、T01、源规划）终核均保持SHA不变。3条roads的全部29节点顺序、宽度、方向及projection与规划逐值相等；没有新路/桥/POI/蓝内业务修改。旧probe/revision.tmj未写入。保留写集只在本integration与viewer。导入参考脚本曾自动生成revision-004/__pycache__，已移除本次缓存并禁用后续bytecode写入；源文件未变。

## 画面限制与未通过项

总体镜头按实际landscape固定高度及静态物体投影包围范围拟合，完整看见5楼和全部树灯；滚轮/按钮缩放保持当前中心。近景1.5倍用于看多楼细节，不代表裁掉对象就全场通过。

- 五楼身份与体量不同，静态排序未见整栋明显盖住道路；建筑与预规划庭院仍有轻微边缘/地基方向残差，不作registration-ready声明。
- 两侧灯原生臂分别朝车道内，未使用方向反的旧灯；远侧折肘仍在，灯脚接地和杆高为视觉候选，不称精密配准。
- T01完整树池保留；自然区不用树池复制。T02仍属同族窄冠变体，不计新增树种。
- T03两株针叶比较树在同场仍显偏侧视，与T01俯视感不同，**未通过高俯视/后续量产资格**；只保留明确比较用小子集，未铺满自然区。
- B05底边余量窄与彩边未修原图，运行缩图仍可能见轻微浅色边；未自动声明用户验收。
- 地面使用连续受控色块，局部庭院边缘仍可见规划几何；不是完整城市景观验收。
- 骑手深度为接地点插入规则，未验证逐像素建筑遮挡；车辆多样性未制作。

图片已产出、运行已显示、用户验收为三种独立状态。本次完成前两者的指定接入与证据，后者尚未发生。
