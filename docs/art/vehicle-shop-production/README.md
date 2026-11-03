# 商城独立生产资源

2026-11-01，用户已批准商城v2落地并授权素材制作；本目录为生产图，与整屏概念稿分开。四张原图均通过内置imagegen生成，原始生成文件保留，未使用整屏稿裁出的车辆或烘焙文字。实际prompt各存独立txt。

| 资源 | 原始尺寸/模式 | 原始生成文件 |
|---|---|---|
| garage-clean-background.png | 1374×1145 RGB | `/Users/sanger/.codex/generated_images/01a1915b-62c5-7b93-95de-bece15a1d48d/exec-56eb41b2-a7dc-4be7-8a73-683543db3776.png` |
| metal-panel.png | 2172×724 RGBA | `/Users/sanger/.codex/generated_images/01a1915b-62c5-7b93-95de-bece15a1d48d/exec-b5745bdc-ee7e-4e51-a7e7-532ab164f1aa.png` |
| card-frame.png | 1122×1402 RGBA | `/Users/sanger/.codex/generated_images/01a1915b-62c5-7b93-95de-bece15a1d48d/exec-a4f05c67-7b5b-415e-83f0-31de03fea035.png` |
| primary-amber-button.png | 2172×724 RGBA | `/Users/sanger/.codex/generated_images/01a1915b-62c5-7b93-95de-bece15a1d48d/exec-96d479c5-a931-42d8-a9c5-8df553998f5e.png` |

背景只含场景，中心有连续空地，不含车、车影、UI或字；皮肤有真实alpha外缘且有透明留白，开发按实际内容rect设置SpriteFrame后九宫格伸缩，不能把透明画布边作为可见框。图标、名称、档位、价格、数量和操作文字全部独立绘制。皮肤是共享资源，普通/选中状态、页签、信息条等可复用，不为每辆车重复做卡。

D与D+使用已有不同原图：D圆灯旧电动车 `docs/art/user-deliveries/2026-10-30-au02/vehicle-d-three-quarter-original.png`；D+方灯翻新电动车 `docs/art/user-deliveries/2026-10-31-vehicles/V01-d-plus-45.png`。不使用概念生成时重新描绘的缩略图，不同车型不能同图复用或靠换色区分。

固定美术负责 `asset-handoff.md` / `manifest.json` 的尺寸、透明内容框、候选切片边界、SHA和十档复用索引；固定开发负责游戏资源导入、布局与交互。生产图已生成不等于已接入或用户验收。游戏仍按用户规定等“阶段完成”再集中测试。
