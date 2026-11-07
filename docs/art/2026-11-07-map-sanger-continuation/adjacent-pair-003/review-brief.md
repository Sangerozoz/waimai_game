# 新增相邻两区证据只读复核

复用地图审查会话 thr_978x3n893w；不是产品线。主会话 thr_fs5qphhxgc，Codex / ccs-sanger/gpt-6.1-sol / max。用户“允许”已批准突破4～6的PM预算，先做相邻两区，再据实际清晰度/完整街坊/接缝定图数；20～24不是已定批量。本轮原生已真实返回两张，无新后端/凭据变化，不恢复旧D或Hermes队列。

同checkout，只读本目录。不要改文件、不要运行写入型builder/verifier或导出；允许读取脚本并在内存独立检查，读取/查看图。不要打开游戏或真档、跑游戏tests/typecheck/FPS，不读取旧聊天。当前主会话会另做官方Tiled导出和独立浏览器证据；你的结论请注明自己确实验证的范围，不代证GUI/游戏。

先读 PLAN.md、authorization.json、pair-plan.json、W/result.json、E/result.json、E/adaptive-pixel-guide.json。两原生都是1672×941 RGB：

- W/native.png SHA 996a21df642f583c14071a5d7118579d4113d9b1bb238fbaecfc940d0f75a976
- E/native.png SHA 4686e0c7b3a35e0989d25f6dfb486a2b5fbfaab11192bf5978aba8c7810bf57d

主检查：

1. 实看完整原生与 assembly/pair-native-pixels.png：是否每区六完整街坊（合十二），沿共享道路裁界是否切自己的楼/庭院、路是否真连续。已知普遍住宅语言仍相关、部分暖亮店面未完全纠正，未用户美术验收。不是8街坊旧图裁成两张。
2. assembly-record.json：只平移 E 原图(1576,-4)，W裁[0,0,1608,937]，E裁[32,4,1672,941]，E核心放(1608,0)，合3248×937。无本地缩放/扭曲/滤色。三处最大接口残差12.3693px，保留六个真实街口节点（错位口部沿共享沥青短连接），未强吸附成三点。图外碎片和北侧错开的外延路不算六街坊或已认证导航。
3. actual-pair-graph.json / actual-blocks.json / build_pair_evidence.py / verify_pair.py：24节点35边1分量12有界面；每个单边排除仍连通。主路径3158.3693px，排除W-h-1-2后3933.6226px；只双向几何假设，不称车道/交通通过。独立查路径、交叉、重叠、脸与街坊对应、坐标是否落实际沥青。
4. tiled/adjacent-pair.tmj、W-native.tmj、E-native.tmj：所有折线顶点/属性/名称覆盖与坐标偏移只一次，核心图片与原生无额外缩放。verify_pair.py 已有444检查（含1953对成对线段）通过，但请独立核关键结论。新静态报告 verification/static-checks.json；官方CLI/浏览器报告主会话仍在生成，不把尚未生成的记录当成已通过。
5. 真实性：设计米与像素仍分开。两图没有严格保留结构导向的留边/尺度，不假认米制标定，不给整城覆盖百分比/一半/4K/固定20～24/全游戏/用户验收。旧A2/B1/C和91保护源不改。

请只回复Critical/Important/Minor发现及证据，或明确无阻塞；要给“独立实测证据可展示”和“普通地图生产/整城验收”不同结论。此目录会新增验证截图/报告/结果说明，但图与图结构已稳定；如发现问题先反馈，勿改文件。
