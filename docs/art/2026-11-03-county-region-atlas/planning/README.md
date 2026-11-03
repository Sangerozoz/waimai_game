# 全县整区地图：源几何与接缝生产包

2026-11-03。用户已在当前BB PM对话认可REGION-A-v3并授权持续完善整张地图、按需并行分工。本目录为生产规划与code-native结构输入，不是最终美术、拼接成果或引擎截图。没有改源city、业务代码、生成图像像素或存档，没有运行游戏测试/typecheck/回归/页面。

## 实际文件

- `atlas-plan.json`：完整红框源空间分区、邻接、重叠带、城区/郊区/外围主题与状态；固定62.5°/45°，来源SHA齐备。
- `county-region-production-plan.png`：带原路、三框和首批ABCD位置的结构规划图，明确标注NOT FINAL ART。
- `structures/REGION-{B,C,D}-structure.json`：相邻三整区原路、完整源楼参考、原规划补景、地块用途、水系、路口与共享接头。
- `guides/REGION-{B,C,D}-structure-neutral.png`：全新中性1536RGBA几何底稿；源楼与已规划补景都含于底稿，防止仅画少数源楼留下大片空地。结构盒不是最终画风。
- `prompts/REGION-{B,C,D}-v1.json`：每区完整内置image_gen提示词，几何guide与A-v3角色分开，有参考SHA；尚未调用生图。
- `first-four-seam-contracts.json`：AB/AC/BD/CD共享原路接头、完整重叠、局部地块边界、源地面冲突最少的候选接缝。每边有2个不同原路通过点；AC/CD各至少1处源楼足迹冲突，实际绘画应沿完整地物/庭院/道路自然边界绕开，不能直接矩形切楼。
- `runtime-interface-mapping.json`：对齐开发`atlas-interface.json`的坐标、anchor、registration、唯一归属与骑手门控。
- `build-atlas-plan.py`、`finish-planning.py`与`source-manifest.json`：可复现结构输入、来源/输出SHA。脚本只生成规划与几何底稿，不读取/修改A-v3像素。

## 尺度与真实工作量

红框约3323.48×3323.47m，蓝框约2291.17×2150.25m；三框原坐标/相对位置保持。

以A约120×120m为整区绘画范围，16m邻图共同重叠（每侧8m halo），唯一归属核心104×104m。A锚定`[-1580,80]`，B向源x正方向104m、C向源y正方向104m、D两向各104m，四图共享真实源世界坐标。

当前实际分区为32列×33行=**1056个整区**；506个核心与蓝框相交，其中187与绿框相交；550个仅外围景观；2047个邻接边。东边最后0.05m红框残余吸收到邻图已有8m halo，避免为5cm额外生成33张图；红框范围未缩。

这不是“1056张已生成”：当前实际整区美术只有A，A尚未配准；B/C/D只是已备好的生产输入；所有接缝和引擎整区接入仍待实施。平铺网格只是覆盖/调度索引，最终可见接缝需沿源路、庭院、林地等自然边界调整并用互补ownershipPolygonUV唯一归属；整栋建筑、树冠、投影跨界时不能机械裁断。

A guide是1536px、7.8guide-px/m；若构图保持缩至原生1254px，名义值约6.368native-px/m。此换算不是A图实测配准，不能拿开发示例7.8或guide中心直接声称已对齐。真实anchorUV/尺度/残差由配准资料确定，PM确认ready后骑手与路线才允许显示。

如果改成600m整区且仍1254px，原单位细节线密度会降为A的约1/5，不能为了减少张数将这种图称作同质完成。保持批准的细节标准，先把2×2的原路/画面/接缝/连续行驶打通，再分批扩展。

## 第一批的共享原路与生图方式

| 整区 | 图面源范围x/y（m） | 源路/完整源楼参考/控制点 | 与首批邻接 |
| --- | --- | --- | --- |
| B | x[-1536,-1416], y[20,140] | 6 / 2 / 14（另含原布局补景） | A西侧共同16m，D北侧共同16m |
| C | x[-1640,-1520], y[124,244] | 7 / 22 / 21（另含原布局补景） | A南侧共同16m，D东侧共同16m |
| D | x[-1536,-1416], y[124,244] | 9 / 11 / 26（另含原布局补景） | B南侧共同16m，C西侧共同16m |

上下方向指源世界y轴，不等于屏幕正上下。B与A重叠x[-1536,-1520], y[20,140]。所有生图都必须把guide作为唯一道路/几何依据，把A-v3作为画风/尺度/光向与可见边缘参考；不能把A街道布局直接复制到B/C/D，也不能把中性未布置底色画成整片公园或空铺装。先看A真实图配准报告，必要时共同边缘应在保留整体画风的前提下原生修整，不能暗改道路迁就图。

## 后续消费规则

1. PM统一内置image_gen生产整区并保存原生、prompt、源SHA，当前子任务不自行启动生图。
2. 配准工序测量实际图像控制点和残差；至少3个分布开的非共线对应点仅是最低输入，不能据此掩盖局部错误。
3. 每邻边实际制作自然接缝，四区共有角同解，互补归属避免重复路标/树冠和漏地面。
4. 开发只接收真实已有PNG及有证据的runtime manifest；未生成区域保持缺失状态，不重复A、镜像A或程序楼填充伪装完成。
5. 运行接入与用户验收分开记录；过程不运行游戏测试，用户说“阶段完成”后集中测试。

## 惰性生产CLI与完整连续队列（本轮新增）

`make-region-input.py`读取已有atlas，不重新执行`build-atlas-plan.py`，不会改planning原有分区/BCD产物。每次只提取一个精确region id的源几何，并写入调用者指定的独立、空版本目录；非空目录拒绝覆盖，planning及其子目录也拒绝作为worker输出。所有源SHA先与atlas核对，源变化应先显式更新规划。

示例（由PM/生产worker执行；本子任务未创建production输出）：

```sh
python3 docs/art/2026-11-03-county-region-atlas/planning/make-region-input.py \
  --id 'REGION-B' \
  --output-dir 'docs/art/2026-11-03-county-region-atlas/production/REGION-B/input-v2' \
  --neighbor-art 'REGION-A=docs/art/2026-11-03-whole-region-map/REGION-A-v3.png'
```

后续任意区域同样按id调用，实际相邻图已保存后提供参考（下例B路径应替换为PM已归档的真实文件，不是保证该文件已存在）：

```sh
python3 docs/art/2026-11-03-county-region-atlas/planning/make-region-input.py \
  --id 'R-+02-+00' \
  --output-dir 'docs/art/2026-11-03-county-region-atlas/production/R-+02-+00/input-v1' \
  --neighbor-art 'REGION-B=docs/art/2026-11-03-county-region-atlas/production/REGION-B/REGION-B-v1.png'
```

产物在指定目录下为`structures/<id>-structure.json`、`guides/<id>-structure-neutral.png`、`prompts/<id>-v1.json`和`source-manifest.json`。参考路径绝对化，prompt带相邻region身份、原图SHA与共同源路约束；未提供真实相邻图时明确标`needs-real-neighbor-art-before-seam-production`，不能声称可无缝派出。

默认保持历史1536 guide的7.8px/m构图，不会悄悄替换已经被消费的BCD输入。可显式加`--match-approved-scale`，按配准A的7.1345800795native-px/m、anchor[613.8999,640.6815]映射到1536guide；所有版本都记录A边缘约15–42px漂移，匹配尺度也不等于接缝已解决。此参数生成新的结构guide，不调整/变形原生美术。

CLI按zone分开编写主题：绿框多样都市建筑，蓝绿之间低中密度社区/学校/运动场与完整庭院，红蓝之间仅树林/低山/河谷/草地等外景，不沿用住宅提示词。蓝/绿混合区域带原坐标边界。**所有屋顶完全禁止任何绿植**，包括树、灌木、草坪、盆栽、藤蔓和屋顶花园。

`production-order.json`列出1056个唯一region、264批（每批4项），另有`production-order-first8.md`便于查看。顺序为A/B/C/D连续首块 → 从当前块按曼哈顿广度向外铺完187个绿框相交区域 → 剩余319郊区 → 550外围景观。每个新region都有此前几何相邻region，实际派出仍等所选相邻原生图存在；同批不代表无依赖可并行，A只作既有参考不重复生成。队列生成过程对数量/重复/遗漏做生产完整性约束，不是运行游戏测试。

本轮仅执行队列生成与CLI `--help`查看；未在production目录运行提取，未生图/运行游戏/测试。后续直接消费队列逐区准备，无需手工复制1055份脚本。

### 新CLI生产纠偏（保留此前BCD输入和原图）

针对生产中发现的地标复制与道路漂移，`make-region-input.py`新增最高优先级约束：source guide原机位/框定/共享路口和道路走廊优先，其次真实邻区边缘且不得挪源路，A-v3仅作为材料/画风参考。严禁把每张图都画成“玻璃塔＋L形学校篮球场＋弧顶厅＋灰坡顶排屋”同一组合；不能将上段道路降为浅俯视直线、穿楼或迁就风格图改变原路。

新CLI按该区实际`parcels.landUse`生成设施许可：源数据的学校用地实际类型为`campus`（全蓝框规划19块），只有本区确含`campus`/`school`才允许在对应原地块安排学校设施；`community`只允许对应社区服务地块。无这些类型时明确禁止凭空插入学校、运动场、市政/社区地标。普通住宅可用不同体量庭院、楼群和合用途的小便民店，不因每区120m而强添一所学校。现有`mixed`/`garden`/`park`不自动授予学校或市政地标许可。

550个外围景观单元可在后续按信息密度探索合并为更大的**生产候选**，具体范围、原生像素密度、邻接与自然接缝需单独记录。当前atlas仍1056个覆盖单元，队列不变；没有擅自用低细节外景图铺满，也没有把候选合并数量当作实际美术数量。
