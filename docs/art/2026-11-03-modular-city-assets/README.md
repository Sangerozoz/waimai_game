# 首批二维拼装素材

**当前实际展示：** [打开二维拼装街角](http://127.0.0.1:4181/modular-city/)。真实运行画面为 `engine-v3.jpg`，旧远景和庭院取景分别存 `engine-v1.jpg`、`engine-v2.jpg`。8件新增美术候选与1件复用骑手已接入，3种建筑复用为8个实例；这是首批方法样板，非整县地图或最终美术验收。

2026-11-03。用户明确“那我们开始吧”后实际制作。制作方式为内置 image_gen；所有原生PNG、每次完整prompt及来源留存，未通过脚本改图、抠alpha、拉伸或重绘原图。生成母版参考为已认可都市街景，素材库示意图仅参考组合形式，不继承其低模画风。

## 当前可接入候选

| ID | 文件 | 用途 |
|---|---|---|
| B01 | B01-cafe.png | 橙棚餐饮楼 |
| B02 | B02-glass-v2.png | 玻璃沿街楼，已提升俯角，仍有小幅绘画透视残差 |
| B03 | B03-residential-v2.png | 商住楼，修正首版俯角 |
| T02 | T02-tree-v2-oblique.png | 短干、向下观察树冠的修订树 |
| T03 | T03-tree.png | 较紧凑的第二树形 |
| P01 | P01-streetlamp-v2-halo-candidate.png | 白天熄灯路灯，外部RGB亮色实际alpha0，不显示 |
| S01-paving | S01-paving.png | 俯视平面人行道材质，按原地面投影铺装 |
| S02-asphalt | S02-asphalt.png | 俯视平面沥青材质，不含标线 |
| R01 | R01-rider.png | 原D骑手NE帧字节复用，非新生人物 |

当前清单为8件新增候选＋1件复用骑手，不等于全部用户验收。12次生图输出包括中间稿/拒绝稿，来源见generation-records.json；原始尺寸/锚点/占地/不确定性见asset-manifest.json和metadata/current-annotations.json。素材背景均保留实际原生RGBA；两种地面材质为原生RGB。

## 用户纠正与版本

用户明确指出T02第一版是正视而地图为斜顶视，原话/参考存tree-v1-feedback.json和user-oblique-view-reference.png。`T02-tree-v1-front-view-rejected.png`已拒绝，禁止接入；旧HT01也不复用。修订通过image_gen重新绘制可见顶部的紧凑树冠/短干，不用把旧图压扁或旋转代替变机位。

B02/B03首版存在视角偏差，已分别另存v2。按可见底边的近似正交分析，B03v2约29.6°俯角、B02v2约27.5°，B01约29.3°；这些是手工角点＋假设推算，不是精密标定或量产同机位证明。B02仍保留残差，需看实际组合后再评估，不以提示词“30°”代替观察。所有旧PNG保留。

## 原坐标小样

sample-layout.json含原点(-1580,75)、3种独立建筑复用为8栋、7树6灯、骑手内存演示与原道路完整节点。背景范围X[-1615,-1548]、Y[40,112]为67×72米；默认镜头聚焦西侧沿街三楼与原道路，边楼允许超出画面，不再为看全缩成沙盘。裁显示不改路网。三栋原主楼临车道静态净距约3.3151/3.0309/2.3587米，位置/占地的隐藏后角仍为美术候选。没有更改正式city.json/经营边界、订单或存档，也没有擅自复原所有原始建筑足迹。v1/v2布局原样保留。

本批独立Cocos2D显示工程与构建由固定开发负责，报告 `docs/reviews/modular-city-20261103/implementation-report.md`。入口已实际显示并保留。平面阴影为低透明近似，图像颜色保留，不是3D实时光照。整图脚点排序存在细粒度遮挡上限、B02透视仍有残差、骑手演示仅一帧方向，这些尚未解决，不代填用户验收。未进行正式游戏测试/回归/typecheck/存档操作。

如需复现静态数据，按顺序运行metadata/build-current-manifest.py、metadata/densify-layout-v2.py、metadata/apply-street-view-focus.py；前两步分别生成首批标注/布局、邻楼填充，最后一步仅恢复当前沿街取景。素材PNG均是原生文件，脚本不改像素。
