# P09 原生候选交付

内置image_gen实际一次请求，真实参数提交了对应几何图及图05/TR-35-v1局部风格裁片。原生逐字节副本、工具源绝对路径、完整prompt、实际输入路径与SHA、原图SHA及裁片box见provenance.json。风格参考下原创补充，不编造原物件bbox或身份。尺寸为PM候选米数，不是源实测或用户硬限；运行像素不改变世界尺寸。

原生：1536×1024 RGBA，1571149字节，alpha [0, 254]。运行：280×252 RGBA，89664字节，长边<=280，规定只读export_runtime.py正等比派生；母版未入包。已核对原生与工具源逐字节一致，运行SHA与.runtime.json一致。

四道拱架、轻质覆膜和内部两排种植可辨，内部土壤限定在棚内；底脚基本完整，但远侧中间接点被膜/植株遮挡。原生有周边灰雾，规定导出器后运行图外围目视较干净，未额外抠图。入口偏+u右上近侧，未严格居中在端面；底部短边目测约+44°而目标+55.406°，长轨约−30°而目标−28.486°，均仅估读。膜局部偏不透明，颜色较淡，不能当作投影与材质完全通过。

足点/地脚/门位/连接边估读（原生像素，非精密）：
{"visibleGroundFeetNativeApproximate": [[307, 696], [560, 941], [795, 804], [995, 717], [1225, 557]], "door": "visible opening near +u upper-right / near-side junction, not exact centered end face", "doorThresholdNativeApproximate": [1105, 623], "connectionEdges": "two longitudinal base rails; far-side feet partly hidden"}

真实投影导引记录位于references/garden/P09-geometry.json，几何图只作输入。已实际打开原生、运行图、完整TR35源图及风格裁片。未做游戏测试、typecheck或回归；未改游戏/路网/存档/其他角色文件；未提交、未集成、未用户验收。无工具阻塞，无重试。
