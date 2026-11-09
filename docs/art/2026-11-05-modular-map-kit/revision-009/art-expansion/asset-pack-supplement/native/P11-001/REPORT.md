# P11 资产包补充候选

原生：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/asset-pack-supplement/native/P11-001/P11-v1.png，[1536, 1024] RGBA，1583969字节，alpha [0, 254]。
工具源：/Users/sanger/.codex/generated_images/01a1ac1c-02e8-76f0-b1d9-82f4dab00260/exec-4bca1d87-e3c8-45b3-a899-b81327e48422.png。
源与副本逐字节SHA256一致：`081ce32d4471968a456a599ed9857d2b6ce37bb05f66403944e3a42e13de9381`。
运行：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/asset-pack-supplement/native/P11-001/P11-runtime-280.png，[280, 213]，77736字节，SHA256 `0bb4b6c84c01f6371bffa7daf2c7843e75e1bb85cd8f6ce11b62b9f1129101be`。只读export_runtime.py等比裁透明边派生，原生不进包。

默认游戏候选尺寸：[1.6, 0.55, 0.75]米（u/n/z，非源测绘）；原生地面锚点粗估[829, 775]，运行UV粗估[0.5548387096774193, 0.7835550181378477]。不是锁定尺度，不以运行像素改世界米数；摆位/等比缩放交用户后调。

- 木条长箱和两处底脚清楚，完整植物/箱体，少量白粉花；不是无箱灌木。
- 原生alpha最大254，边缘有极低alpha杂点；工具预览柔光背景在外部抽样alpha为0，运行图未见大块底。
- 画面比旧参考略柔和；长轴目测约-29至-30度，非精密标定。
- 默认落脚锚点为两处可见箱脚接地的粗估中点；后缘部分被箱体遮挡，用户后续可等比缩放/移动。

alpha检查：{'extrema': [0, 254], 'bbox': [0, 23, 1506, 1008], 'outsideSamples': [0, 0, 0]}。原生与运行PNG均已实际打开。每件内置生图一次，无重试。几何和TR33局部参考实际随调用提交，完整prompt/路径/SHA/原图版本见provenance.json。物件为“参考画风下原创补充”，未声称源物件身份/bbox。

未精密配准/用户验收/地图完成，未改共享库/包/renderer/用户手调文件/路水边界/业务存档，无游戏tests/typecheck/回归/FPS/提交。
