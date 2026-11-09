# 车辆V01/V02定向修订：先带图约束，再原生重生

父会话已实际打开v1两张280运行图并读provenance。轮廓差异做到，但两者偏产品写实；V02短边/机位偏离当前街段。V02的referenceFilesSubmitted为空，单靠提示词角度没有锁住几何/画风。本条允许各做一次v2，不是扩大车型库。v1母版/报告全部保留，当前不入邻区运行库。

你是原生制作执行，**必须真实调用当前内置image_gen**，不是仅选型/规划。不要另建Agent、用外部API、程序滤色/模糊/平面旋转/镜像或拉斜v1冒充v2；不改游戏/UI/经济/车辆参数/路网/存档，不tests/typecheck/回归/提交。

## 唯一写集（绝对路径）
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/references/vehicles/（新增明确版本的几何/风格参考，不覆盖v1）
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/native/V01-002/
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/native/V02-002/
其余只读。

## 必做前置：不能再零图片输入
1. 读取revision-003/road-constraint.json，用其真实u/n/axisZ生成每辆车的几何参考：完整四轮接地点、车身/货厢不同体量、垂直边，车身长轴屏幕-28.486deg、横轴+55.406deg，正切向车头右上。候选尺寸小车4.2x1.8x1.5、箱形小货车4.9x2x2.4，不是用户硬尺寸或源实测。几何图只是输入，不是交付美术。
2. 打开已认可地图风格和D骑手图（如revision-005/runtime-280/viewer/assets/rt-HC-R-NE-v1.png），必要时裁出车体表面/画法作小风格参考，标明仅笔触、简化面和光照，不借用摩托车或人物身份。原用户风格图docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png也仅画风。不要整张混合街段作为新车构图输入。
3. 调用image_gen的实际referenced_image_paths中必须有对应几何图与画风参考。provenance保存真实提交路径/SHA，不接受只在prompt里声称参考而参数为空。若工具不支持图片输入请报具体阻塞，不继续text-only试运气。

## v2出图
按V01-v2→V02-v2顺序，每件一次原生，先保存第一件原生/provenance再做第二件。保留V01紧凑两厢、V02箱形载货轮廓区别；画法改为与当前地图一致的日间日系都市厚涂小道具：清晰概括色面、柔和绘制明暗、克制反射，不是展厅写实汽车产品渲染，不要细密金属镜面反光/摄影质感/环境倒影。不是平面图标，也不换成玩具Q版失比例。完整轮接点，真实透明背景，无地板/灰雾/阴影云/文字牌照logo或人物，车灯不发光。

每件交V01-v2.png或V02-v2.png（工具原生逐字节副本）、provenance.json、V01-v2-runtime-280.png或V02-v2-runtime-280.png及.runtime.json、短REPORT。用已有只读export_runtime.py单件导出，运行长边<=280。保留实际原生尺寸，母版不进包。打开运行图和风格参考并排看；仍有偏差就记录，不额外自发第三次重试，也不标记用户验收或接入完成。final只报告真实文件路径、核验、缺陷/阻塞。
