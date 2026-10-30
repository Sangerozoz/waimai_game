# ORDER-LAYOUT 独立测试

最终结论：Revision2独立技术复验通过。订单卡及结算收益金额完整单行、实际字体宽度不超列宽；结算内容居中，关闭在右上。下文v1失败保留历史，最终判断以v2证据为准。用户体验验收未执行。


## Revision2 最终复验

采用freeze-ready.json 2026-10-30T08:59:31.727609+08:00冻结版。独立复制构建至output/playwright/order-layout-independent/after2，没有采用开发40状态结果充当本人执行。playwright-cli -s=order-independent run-code读取independent-matrix-v2.js退出0：同上五组尺寸35状态全部实际执行，原始independent-after2.log、结构化independent-after2.json、35张independent-after2-*图。python3 independent-verify-v2.py退出0（independent-verify-v2.log）：金额真实parsedString单行、Canvas同字体实宽不超列宽、金额与邻标签矩形无重叠、结算标签与卡中心差小于0.1设计单位且center对齐、关闭中心在卡中心右侧，晚到和餐损实际影响行均存在。全部冻结source SHA逐项匹配；复制构建与当前生产逐字节一致（仅排除fixture index注入）。最终全量指纹independent-final-v2-sha.json。

playwright-cli执行independent-extra-v2.js退出0：先前失败的普通结算¥21.63现在parsedString=["¥21.63"]，字号82、列616；¥123456.78在规划及toDropoff仍完整单行，长备注回退滚动，普通规划scrollMax=0。亲看independent-extra-v2-receipt.png；另亲看independent-after2-320x480-effects.png：¥654.32完整一行，两条影响行居中；independent-after2-280x420-receipt.png：¥1345.67完整一行。

280×420大厅补查：independent-scroll.js退出0，offset=max=5942；亲看independent-scroll-bottom.png，末单¥23.24与抢单按钮完整在视窗内，先前第二卡露半截是滚动列表正常裁边，并非金额列自身裁切。刷新2/2在280短屏仍换行，该按钮未在本轮生产修改，不扩为本轮返修。

最终技术断言通过，用户4181实际页面、触感/真机FPS和用户验收仍未操作。每次引擎Storage支持探针setItem('storage')被拦一次，独立样板没有生产存档访问。

## v1 独立证据与实际执行（历史）

当前checkout HEAD cdafa0c79892b01b2283ecfdc2ffdccf40ac3a48，生产含未提交内容，以文件SHA为准。独立before在改动前复制构建至output/playwright/order-layout-independent/before，源与构建SHA见independent-before-sha.json；after与开发freeze-ready.json冻结构建逐字节一致，仅index注入独立fixture脚本。完整源/构建/样板/图SHA见independent-final-sha.json。

- before：320×480 + safe，大厅和当前卡真实Cocos Label parsedString均为["¥19.","84"]；字号70、Canvas实际宽232.0458984375、列宽210。根因是CSS可读字号随比例放大，而金额列固定210。命令playwright-cli -s=order-independent run-code读取independent-before.js退出0；日志independent-before.log及两张independent-before-{lobby,current}.png。
- after：独立脚本independent-matrix.js在隔离4197页面运行退出0，35个状态×视口：720×1280、360×560、320×480安全区、320×812安全区、280×420安全区，各含普通大厅/转单大厅/规划/取餐途中/长金额/结算/有影响结算。independent-after.json保留真实引擎行数组、同字体测量、边界及相邻标签边界。python3 independent-verify.py退出0，全部订单金额单行、字体实宽不超列宽、邻标签矩形不重叠；结算各标签中心与卡中心一致，center对齐。验证日志independent-verify.log。该PASS针对这些断言，不包含结算收益单行。
- 补充independent-extra.js退出0：320×480安全区真实¥123456.78在规划及toDropoff均单行，长地名/400字备注回退滚动；普通规划scrollMax=0，极端1530、送餐1398。未模拟手指拖动。
- 引擎每次隔离加载Storage.setItem('storage')支持探针被拦一次；生产start/update/save预先替换，内存OrderBook，不创建CountySaveStore。不称零Storage访问。未进入用户4181游戏。

## 发现与冲突核对

订单卡independent-after-280x420-long.png为¥1234.56，字号80、实际360.2734、列369、parsedString=["¥1234.56"]，完整单行。美术所谓长金额折行实际来自independent-after-280x420-receipt.png，是结算收益字段；不是订单卡断言失败。

结算收益存在真实问题：independent-extra-receipt.png为普通¥21.63，parsedString=["本单收益 ¥21.","63"]，字号82、列616；independent-after-320x480-effects.png为["本单收益 ¥654.","32"]。标题和其余内容都居中，右上X仍在。已向新PM报告，待明确返修结果后复验；不能把中心对齐通过扩为金额完整通过。

亲看图片：independent-before-current.png；independent-after-720x1280-lobby.png；independent-after-320x480-current.png、effects.png；independent-after-280x420-long.png。影响行最终图independent-after-320x480-effects.png真实显示晚到影响−¥11.11、餐损影响−¥680.24；通过调整内存receipt.outcome并用生产quoteCountyIncome重算获得，非仅修改状态文字。

## 限制

本轮未亲跑开发241全回归/typecheck/构建，未将其记为本人结果。真实Cocos Chromium渲染不代替用户页面操作、用户体验、真机字体/触感/FPS。未检查所有设备、金额上限及全部菜名；280×420列表只显示第二卡上半是滚动视窗现象，后续v2已补查滚动到底完整性。刷新按钮换行已由美术另报，当前未判其为本轮新增回归。只写independent-*及隔离output路径，未改生产、开发tests、经济或存档。
