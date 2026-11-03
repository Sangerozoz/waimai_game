# 11-04 生产输入纠正（未生图、未运行验证）

这次是后批偏黄和建筑同质化的生产根因纠正，不套用“整图后修微小地砖差异”。A-v3认可风格仍为原锚；新修正样板尚未由本次改动产生或验收。

- `architecture-diversity-policy.json` 定义住宅、商业、办公、实际校园/社区和景观的形态词汇：体量、楼层节奏、屋顶、立面、入口。只按真实用地挑选，不把学校/地标作为每区配方。
- `make-region-input.py` 输出 `architecture/<区域>-architecture-intent.json`，按已有建筑身份稳定分配适用组合，并写入结构与完整prompt。保留地块rings用于归属，未知用途明确unresolved；组合只是设计意图，不是实测达标数。所有地面足迹、原路、62.5/45与三框保留。
- 结构底稿去掉奶黄色墙/屋顶/路边填色，主提示固定中性日光、白灰墙、真实灰路及局部材料色。邻图仅供共享边缘几何与轮廓，不传递其色调或内部建筑；不整体加蓝。
- `county-region-fill.js` 默认拒绝无本次修正样板验收参数的调用。新增 `acceptedCorrection` 对象须包含 `status: accepted-correction`、`acceptedBy: thr_7w55f3h66f`、`imageFile`、`imageSha256`、`evidenceFile`、`evidenceSha256`。只读闸代理须实际核对文件与哈希，并确认原始证据明确接受本次11-04纠正、绑定同一图片，而非拿旧A-v3验收顶替。未通过则不得进入生图。
- 必须提供全新 `productionVersion`（字母数字下划线连字符），输入/原图/预览放在 `production/<区域>/<版本>/`，不覆盖旧input。生成器仍拒绝非空输出目录。样板通过后通过 `--accepted-style-reference` 进入参考序列，作为palette/style主参考，不能照抄其建筑集。
- 结果字段 `qualityBlocked` 将整体黄染/明显建筑雷同阻断后续波次；不是用户验收，也不证明配准。原有preview-only含义不变。

本次仅改生产脚本、政策和本说明；未生成新输入或图片，未启动workflow，未运行tests/typecheck/游戏/HTTP/browser/Git。PM随后完成工作流语法验证，记录不代表画面验收。名义楼高是底稿取景参考，不恢复历史统一楼高硬上限，造型可以有合理层高/体量变化且不压路。下一步由PM先取得实际修正样板与真实验收证据，再决定恢复生产；本说明不构成恢复授权。
