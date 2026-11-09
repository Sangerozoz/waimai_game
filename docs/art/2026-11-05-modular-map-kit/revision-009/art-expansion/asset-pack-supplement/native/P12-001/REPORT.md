# P12 资产包补充候选

原生：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/asset-pack-supplement/native/P12-001/P12-v1.png，[1254, 1254] RGBA，566874字节，alpha [0, 255]。
工具源：/Users/sanger/.codex/generated_images/01a1ac1c-02e8-76f0-b1d9-82f4dab00260/exec-bfeb5748-881c-48d8-a684-c2a753d32bd0.png。
源与副本逐字节SHA256一致：`0426e58808b3913491ccbfba61a5fa993264dc8f3d5d658b864596c32190535c`。
运行：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/asset-pack-supplement/native/P12-001/P12-runtime-280.png，[280, 270]，56397字节，SHA256 `e802d8769f540d1117da8ca0208eb9269e2f052642e38157d039dbae585207eb`。只读export_runtime.py等比裁透明边派生，原生不进包。

默认游戏候选尺寸：[4, 1.5, 2.6]米（u/n/z，非源测绘）；原生地面锚点粗估[620, 845]，运行UV粗估[0.49122807017543857, 0.7423382519863791]。不是锁定尺度，不以运行像素改世界米数；摆位/等比缩放交用户后调。

- 空候车棚、灰蓝不发光顶棚、细柱与背/侧挡风板，未绑定椅/车/人/站牌/地面。
- 棚顶确实遮住后柱上部，未把柱画穿屋顶；后足存在遮挡/位置推断不确定性。
- 原生棚顶边有细蓝白碎边；玻璃视觉偏乳白、半透明效果待背景合成，勿当玻璃透过率已验收。
- 长边目测约-30度、短边约+53度，竖柱近竖直，存在角度残差；未精密配准。
- 入口朝画面右下方长边，棚内空出；默认地面中心锚点为可见/推断脚点粗估，后续允许用户移动等比缩放。

alpha检查：{'extrema': [0, 255], 'bbox': [33, 19, 1218, 1099], 'outsideSamples': [0, 0, 0], 'windPanelSamples': [{'pixel': [300, 830], 'alpha': 221}, {'pixel': [700, 690], 'alpha': 204}]}。原生与运行PNG均已实际打开。每件内置生图一次，无重试。几何和TR33局部参考实际随调用提交，完整prompt/路径/SHA/原图版本见provenance.json。物件为“参考画风下原创补充”，未声称源物件身份/bbox。

未精密配准/用户验收/地图完成，未改共享库/包/renderer/用户手调文件/路水边界/业务存档，无游戏tests/typecheck/回归/FPS/提交。
