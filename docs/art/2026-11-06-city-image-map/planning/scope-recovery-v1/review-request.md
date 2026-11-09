# 独立只读复核：整体规范与真实容量证据

角色本轮切换为独立审查，**不是生产/修图/接入作者**。本次候选由父PM编写，你未参与这些规范/几何生成器及高返回尺寸探针，适合作独立只读审核。仍acp-hermes-agent→openai-api:gpt-6.1-sol/high，原生模式default保持，不申请编辑能力、不新Agent/换模型/改配置。

用户因当前三地区图路少、没有整体城市感而暂停生产，随后明确授权PM去落实整体规范/能力验证。旧美术认可保留。目标仍旧25图面积约1/4，不能拿图数替代面积，不能暗缩镜头/建筑来凑范围。

## 冻结候选（工程根/Users/sanger/Documents/ChatGPT/taptap 2）
目录 docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/
- CITY-CONTRACT.md
- scope-plan.json（新规划设计米制、64街坊/81节点/144分段/18走廊的建议起点，不是用户指定数量或已标定原生）
- build_scope_plan.py及overall-skeleton.png（PIL结构草图，不是美术）
- capacity-proof/input-spec.json、run_capacity_probe.py、provenance.json、native.png、result-summary.json
- 只读对照：../current-scope.json、../scale-scope-audit.json，原zoning/selection.json与原city.json仅所需字段，不全面重查旧长历史。

**关键新事实要独立核，不照抄父判断：** 父仅一次请求3824×2144，实际原始API回1674×940（约1.57MP），无本地放大。图实际含8个街坊输入意图，实际输出街坊/道路与原生局部细节尚需核。不能从这次结果断言厂商绝对上限/内部路由，但不能声称高原生已实现或4～6张够全城。不要继续普通D任务、不要再请求图。

## 审查边界
只用read_file/图片查看/纯JSON、hash与数学复核。**不写任何文件，不导入运行候选生成器/游戏程序，不执行被拒的依赖或ps命令，不游戏tests/typecheck/回归/构建/服务/存档/Images请求。** 不因默认模式阻止写文件就索要编辑权；本来就是无写入报告。

检查：
1. 旧范围1/4面积/长宽关系与新设计坐标是否自洽，是否偷换成4张图或伪称现3区覆盖已知。
2. 路网与街坊组织/功能比例叙述是否内部一致，有无重新擅自锁棋盘/街坊数量/米数、将数量当净用地比例等错误。
3. 容量公式假设/有效地面下界/相机未实测是否标清，当前真实返回低尺寸对图数/清晰度承诺的影响。不能把参数支持当实际输出支持。
4. 原生能力探针是否真仅一次/无本地插值/源与输出SHA可核，实际8街坊道路、局部阅读尺度能否与A2/C基准混为通过。
5. 规范是不是还缺一个必须先解决的决定；最多给3个阻塞/最小修正，不泛化成新方法大研发或全面审计。

回复一个简短JSON：planningReadyForScopeReview、productionReady、blockingFindings[{file,line,trigger,minimalFix}]、suggestions（最多3）、sourceHashes、limits。planningReady只指可拿去审整体组织，不代表用户验收；productionReady需真实尺度/容量关卡，不得因父已跑脚本就写通过。源/候选若无法读取明确未完成。不要给我重复制作清单，完成只读交还。
