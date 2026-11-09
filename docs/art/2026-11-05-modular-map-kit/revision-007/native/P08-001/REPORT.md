# P08 原生候选交付

内置image_gen实际一次请求，真实参数提交了对应几何图及图05/TR-35-v1局部风格裁片。原生逐字节副本、工具源绝对路径、完整prompt、实际输入路径与SHA、原图SHA及裁片box见provenance.json。风格参考下原创补充，不编造原物件bbox或身份。尺寸为PM候选米数，不是源实测或用户硬限；运行像素不改变世界尺寸。

原生：1254×1254 RGBA，822600字节，alpha [0, 255]。运行：280×230 RGBA，88282字节，长边<=280，规定只读export_runtime.py正等比派生；母版未入包。已核对原生与工具源逐字节一致，运行SHA与.runtime.json一致。

三排叶菜、有限内部土壤、完整低木框可辨；没有扩大为整片农场。原生上侧长边少量红黄碎边，运行缩小后不显眼但未额外清理。土壤颗粒偏细、略写实，仍需场景合成判断画风；不是精确画风/配准验收。

足点/地脚/门位/连接边估读（原生像素，非精密）：
{"groundCornersABCDApproximate": [[208, 692], [819, 345], [1067, 682], [444, 1033]], "door": "none", "connectionEdges": "four timber rim edges; independent bed, no joining guarantee"}

真实投影导引记录位于references/garden/P08-geometry.json，几何图只作输入。已实际打开原生、运行图、完整TR35源图及风格裁片。未做游戏测试、typecheck或回归；未改游戏/路网/存档/其他角色文件；未提交、未集成、未用户验收。无工具阻塞，无重试。
