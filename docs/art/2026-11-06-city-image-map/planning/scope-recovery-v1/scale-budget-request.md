# 只读续作：统一可读设计标尺与真实制作预算

用户在父说明总规草案、两次尺寸未命中、生产仍暂停后回复“可以的”。按认可纠偏方向继续研究；**不解释为批准64街坊棋盘、调整面积/清晰度/图数，或增加Images请求**。

继续复用本会话：acp-hermes-agent → openai-api:gpt-6.1-sol/high。只读，不改变default权限、不申请编辑租约。不新增/联系其他Agent或跨产品线派工。

## 目标
用现有证据给父PM一份可执行的“设计标尺提案＋有条件制作预算”，推进上次独审的两个阻塞，不再只重复阻塞。标尺是新设计选择，不是从一条路推定旧图真实米数；最终未达门槛仍须如实保留。

## 输入（都只读）
工程根 /Users/sanger/Documents/ChatGPT/taptap 2。
- docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/：CITY-CONTRACT.md、scope-plan.json、capacity-direction-addendum.json、independent-review.json。
- capacity-proof/experiment-results.json、两次provenance和native：3824×2144→1674×940；3840×2160→1672×941。同输入/模型/质量，不能把请求像素当产能。
- 已获认可的A2完整原生及integration/next-C/identity-and-edge-contract.json。C可作几何证据，但其美术并未获用户认可，不能代替A2可读性基线。
- 必要时只读旧city的道路宽度档位、旧zoning和25图名义放置清单。旧拼图未配准，不能把名义米数或图数当实测面积；不遍历旧长聊天。

## 输出（仅回复简短JSON，不写文件）
1. selectedDesignTrial：提出一个推荐的道路/建筑可读设计尺，指出原生实证、设计假设、未锁定的近景要求；如选8m道路档位与约54px样板，明确这是可逆设计提案，不是实测映射。
2. scaleEvidenceNeeded：让提案成立最少还缺哪些可在已有素材中取得的证据。不得为本轮补收费图、启动游戏或制造存档。别把未知相机俯角/路向写成已测值。
3. budgetScenarios：按真实返回像素给少量条件试算，分清城区与自然背景、统一采样与不同LOD、重叠损耗。公式注明路向/俯角/设计米尺假设；不把条件估计的几十张说成已经证实的必须图数，也不假装4～6张已经够用。保留“目标面积/近景优先，图数从证据推导”的顺序。
4. recommendation：下一件可真正落实、无需新增图像能力的交付是什么；明确有无需要用户决定的重大取舍，不让用户替我们选技术参数。
5. sourceHashes和limits：绑定实际查看的主要证据。没有找到依据就说缺失，不脑补。

只准读文件/图片、纯JSON解析、hash和数学。**禁止新Images请求、换模型/端点/账号、依赖探针/安装、运行候选生成器或游戏、tests/typecheck/回归/构建/新服务/存档/提交；禁止重试曾被拒ps或用另一工具绕行。** 不写报告、候选或进度文件，父保存结果。D和其他普通生产仍暂停。完成只读交还。
