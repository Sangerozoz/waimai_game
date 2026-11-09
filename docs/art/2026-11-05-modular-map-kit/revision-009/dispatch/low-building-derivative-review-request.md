# 两栋不再重生：B13游离像素清理与逐件真实控制点

父已实际看B12/B13运行图并逐字节核tool源，单层住宅/平顶街铺确有形态差异，允许下一步几何复核和少量实景比较，不是已校准或已接入。两件原生/原runtime/metadata/报告永久只读，不要因本条重跑image_gen。

1) B13上方红/浅色游离点是图外碎屑，允许仅做可追溯**派生清理**：先列8连通组件bbox/像素数与标注图，人工区分屋顶/檐/阶/灯/把手等真实结构，不能无脑keep-largest或按颜色全删。仅移除已证完全游离且不属建筑的外部碎点；主连通体/建筑边/阴影/细部不动。另存B13-runtime-280-clean.png，保持原262x280画布/所有保留像素位置/anchorUV/裁框/PPU完全不变，不再次裁边造成隐式世界尺寸变化；原件SHA仍保留，clean新SHA/删除组件清单/前后对照与像素mask另档。若某点属主体或你不能确认，保留并报告，不修轮廓、不涂像素重绘。此不是新family/新原生。

2) 每件另做native-control-points.json与可见墙脚/门阶编号叠图。真正同一直边两端做实际坐标/计算角度，墙脚/屋顶/台阶突出点分开；别两份报告套同“约-25到-28/+50到55”模板。特别B13按报告三估点，长边目测可能偏大，父未据估点直接判废，必须对实际可见直边复读。后角隐藏如实推断，透明处不是门。尺寸仍候选，不靠改PPU/横纵缩放把角度做成合格。

只在/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/native/B12-001与B13-001追加上述derivative/诊断文件，references/buildings可追加诊断输入但不改已提交geometry/provenance。共享库/renderer/Tiled/父admission/catalog只读。交实际前后图与独立点图、精确差分/SHA，供接入作者独立复核。未游戏测试/用户验收、不提交、不扩生产。
