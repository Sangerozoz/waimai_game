# ORDER-LAYOUT 项目经理验收记录

2026-10-30。Revision 2技术交付完成，用户体验待验收。范围来源 docs/team/tasks/2026-10-30-order-text-layout.md。生产仅开发修改CompactOrderInfo.ts与MapSample.ts；沿当前checkout，未清理既有未跟踪文件、未提交、未操作用户游戏或存档。

## 最终结果

大厅普通/转单及当前规划/配送信息卡按真实字体宽度分配金额列，达到预算后适配长金额字号；金额保留原数值及两位小数，完整单行，无截尾或邻列遮挡。结算标题、收益标题、金额、事实状态、晚到/餐损影响及评价经验相对卡中心居中，X仍在右上。收益标题与金额分行，避免小数被拆；保留紧凑自适应和原计价语义。

## 证据

- 开发implementation-report.md：Revision2完整241项回归、typecheck与构建包装退出0，构建08:59:17 Finished；原始引擎诊断保留，不等同于原始Cocos子进程无异常。开发5尺寸40渲染状态。
- 测试independent-test-report.md：独立真实Cocos五尺寸35矩阵及4补充状态通过，覆盖720×1280、360×560、320×480安全区、320×812安全区、280×420安全区；真实parsedString、同字体实宽、相邻边界、中心及关闭位置断言。普通¥21.63、长收益¥1345.67、订单¥123456.78及真实影响行通过。长备注回退滚动，普通规划零滚动。
- 美术art-review.md：实际看R2独立长订单、普通/长收益及影响行图，视觉终检通过。280大厅滚动到底末单完整，列表裁边属于正常滚动视窗；既有刷新按钮窄屏换行保留记录，非本轮修改。
- PM亲看independent-after2-280x420-receipt.png和independent-after2-320x480-effects.png，确认金额、居中和X。pm-final-check.json：31源码、66构建文件SHA逐项匹配冻结清单，39张最终独立图记录SHA；4181六份静态入口/主包/配置逐字节匹配最新构建。仅请求HTTP静态资源。

第一版结算收益拆小数为真实发现，失败日志/图与v1清单保留；不能将v1结算图作为最终通过证据。唯一当前冻结freeze-ready.json revision=2。最终源与构建清单final-source-sha.json、build-manifest.json；独立源/构建/样板/图片另见independent-final-v2-sha.json。

## 边界

引擎setItem('storage')支持探针实际被拦，非零Storage访问；隔离内存fixture预先替换生产启动/更新/保存，不创建生产存档。没有代用户实际4181操作、真机字体/FPS/触感验收。当前仍为M1收尾及此前获准M2手动取送切片；不自动展开其他阶段。
