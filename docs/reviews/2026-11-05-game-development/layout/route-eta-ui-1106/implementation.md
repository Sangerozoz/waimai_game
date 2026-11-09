# 逐单 ETA 接入路线选择：开发B交回

**源码已实际修改，未测试/未构建/未部署，待父 PM 独立复审。**

唯一源码：`delivery-game/assets/scripts/map-sample/V2GameUI.ts`。

- 起始 SHA-256：`705a2f051a53c6b39243086212673ca3f0e20ab8a0ca6a05be68ed370cc99b46`
- 候选 SHA-256：`af94fd449ef23f44f8fc2894440fa1b2dc35842689713cf0929a3add64d9a5a4`
- [实际精确增量](candidate.diff)；[字段映射/高度公式/冻结依赖SHA/未测项](implementation.json)。原源码为未跟踪文件，增量来自本轮内存保存的完整起始字节，不以空git diff充当证据。

## 实际接入

`orders()`的planned路线卡现在展示实际合并别名、距离、预计现实用时、当前天气与预计耗体力。遍历每个真实可行方案的全部orders，按id关联本批序号/现有餐名和送达名；每单展示“预计…后完成（游戏时间）”，直接读取lateGameSeconds作迟到预警，>0显示红色。权威safe单只按tripState同id的safe说明“不计迟到”，不根据累计订单推断，不说概率或保证准时。

界面保留两条说明：“连续行驶与取送服务的条件估算”“不含手动等待及后续补给/事件/停顿”。不把etaGameSeconds当绝对钟表时刻，不与deadline/gameSeconds重算迟到，不重建期限。显示取整仅生成字符串；时间先ceil整秒再拆分/秒，余秒使用%60，不生成“X分60秒”。DTO未改写。

## 所有行与动态高度的静态依据

- `choices.map`及每个`choice.orders.forEach`均无截取、固定3单或首几项限制；一张路线卡包含3条元数据，每单再追加2条文本，可换行。
- 复用现有`textHeight(value,size,660)`估算每段高度，字体19/20/21/23，与相邻卡片可读范围一致；绘制使用同一高度、wrap+CLAMP，不用缩小字号塞数据。
- 每卡高度为`24 + Σ(line.height+6) + 50`；卡内逐行用相同高度/间距推进，最后一行与按钮相隔6，按钮保持唯一且高50。
- 卡片Y偏移按每卡真实高度+12累加；routeHeight包含两条说明和全部卡片高度；ScrollView内容高度同步包含routeHeight、全部原批次详情和末尾说明。
- 保留`orders:trip` key与508/-340视口，原固定控制栏顶边-348，二者间隔8。声明内容高度在末尾说明中心以下还有84余量，末尾行可以继续滚入视口，不要求显示在固定栏背后。

这些证明没有源码枚举上限、固定88步长或漏算订单行；**不是实际字体排版/长名称无截断的运行证明**。文本高度使用项目既有估算helper，实际字体、极长名称和滚动仍须外观核对。

## 保留与验证边界

静态精确比较确认：orders()前除导入textHeight外逐字不变；空choices/非planned说明分支逐字不变；从`const orderTop`到文件结尾逐字不变。原详情、大厅、重量/币图/图标修订、P0 routeMotion/跟随/HUD、骑手排版、万元规则、车辆背景均未夹带改动。

原`beginTrip(r.preference)`、返回首页与`!t?.action`禁用保持，没有自动出发、新确认弹窗或业务/存档写入。Route/Game/Runtime和皮肤/资源helper/manifest/PNG未编辑，收口依赖SHA与读取时一致。

只做源码、字节差分、哈希和静态几何检查；patch自动报告per-file tsc skipped，不是编译通过。未运行tests/typecheck/TS/回归/Creator/浏览器/游戏/购买/接单/造档或读写slot，未commit/push、派Agent或生图。未真实触达active-batch界面、未造截图，不宣称UI验收、反馈关闭或98%。

**源码及报告交回父 PM，释放写lease并停止写入；独立复审、统一构建/非消费外观核对与模式恢复由父 PM 安排。**
