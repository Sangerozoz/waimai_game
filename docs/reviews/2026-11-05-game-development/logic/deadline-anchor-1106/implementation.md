# DEADLINE-ANCHOR-IMPLEMENT-1106

状态：**已按PM冻结方案A实际修改两源，仅完成静态核对；未测试、未构建，待独立审查。交回即释放本批写lease，不继承临时Accept Edits，不自行修改模式。**

依据：同目录 `approved-contract.md:7-14`（已先读）；正式V1 `docs/product/2026-11-02-delivery-game-product-v1.md:49,57,59,92`。本批是PM已批准的出发前计时澄清，不再把候选当已确认规则，不附带迁移或历史补偿。

## 实际最小变更

- `delivery-game/assets/scripts/domain/V2TripRules.ts:80`：精确加法签名 `advanceSupply(seconds:number,advanceTripClock:boolean=true):number`。原首个check同时校验有限非负seconds与boolean标志，在读取动作/改变elapsed或G之前拒绝不合法参数。仅把原 `this.s.gameSeconds+=used/a.durationSeconds*a.gameSeconds` 放入 `if(advanceTripClock)`；原单参数调用默认true。
- `delivery-game/assets/scripts/map-sample/V2GameSession.ts:81`：唯一生产调用传入 `this.route.progress.phase!=='planned'`。只在planned时关闭这次动作的行程钟增量，其他phase保持true。
- 每文件仅替换一行，各+1/-1；未改Route、Runtime、UI、ETA查询及三个ETA公式、报价/合同/经济参数、存档版本/字段或地图。未新增依赖/导入、路由计算、位置估算、随机数或时钟读取。

## 静态边界说明

1. **三类量分开**：真实动作仍由原used推进 `a.elapsedSeconds`；完成后仍按原封顶恢复、清除blocked/action并返回剩余现实秒。只条件阻止trip.gameSeconds增加；已有deadlineGameSeconds从未赋新值。action自身nominal gameSeconds仍是原目录/active rest数值，未清零、未重解释。
2. **旧planned正G保留**：当已存G0>0时，新条件不重置/减去G0，也不增加D；其后planned动作仅续完剩余现实耗时及原恢复，保留既有D-G0损失。`beginTrip`、`Trip.begin`及两类完整restore均字节不变，不在读档/详情/ETA重建期限，不重抽天气/抽值、不重报价或补偿。
3. **部分动作不重收钱**：原 `startSupply` 全文不变，已消费价格/库存/来源以及duration/restore/elapsed均沿用。已接未出发仍是active rest（10现实秒、恢复20、nominal 600游戏秒、费用0）；无单仍20秒恢复满、nominal 0。没有通过把active改false获取无单服务。
4. **同帧补给后自动出发**：while开头观察到planned时仅关闭当次补给加G，真实used/afterSupply计算不变。补给结束若尚有时间，原auto planned分支照常beginTrip；随后原route.advance的travel/serviceTime正常加G。若本帧耗尽则照旧等待下帧，不虚造余秒。
5. **ready不是planned**：ready/pickup/travelling/service/idle/finished均传true。已出发后等取餐或等“去下一站”期间确认的补给仍推进原游戏秒；原serviceCharged动作互斥、后台/暂停/广告/rebase门禁不动。
6. **真实时间与NPC不冻**：`used+=seconds-afterSupply`、自动授权实际耗时扣减、wallStart/offset/elapsedSeconds到达时点、advanceFleetTo及账目时间作用域都不变。冻结的是未启动配送的行程钟增量，不是动作时长、NPC经营钟或自动授权时长。
7. **恢复与保存不放宽**：Game4/Route2/Trip2和原旧格式分支不动；Trip/Game完整restore字节不变。Runtime validate→commit→publish、失败保留、唯一写者和slot不动。新planned从G=0的相对预算表示开始；不声称追溯修复旧已损失余额。

## SHA256与差分

编辑前重新读取并核对，匹配PM冻结基线：

| 文件 | 修改前 | 修改后 |
| --- | --- | --- |
| `domain/V2TripRules.ts` | `6ede7a45eed46a1875e187d1f728e045f44db82de6f7d83a685131d9e6093c16` | `213cefc4da3a6166c5ba9b5bd36d3a795b94f676d92fcf5448324df79a768e01` |
| `map-sample/V2GameSession.ts` | `4aedd3ee5fd37a2c68064c5dc17c57505cc8bec18b65f97b922833d25a01a7fd` | `0fe0d7fe23a1457e4c5286539ea32a7f5a796c94fe45312f5f143ddda65abce3` |

表中文件均相对 `delivery-game/assets/scripts/`。使用捕获的真实修改前全文逐字构造预期两行替换，与当前全文比较：除此之外全部源码字节一致。Route、Runtime、GameUI、Dispatch、Fleet、Economy、EconomyConfig、SupplyCatalog及PM approved-contract在本次编辑前后SHA一致。没有把并行会话早于本轮的合法更新算作漂移，也没有恢复他人旧版本。

下列完整unified diff的UTF-8 SHA256为 `b5812ff65407ad74f065423ac5e1c5ed7f541cb46bed92fc60bec8d32bd3507f`（含结尾换行）：

```diff
--- delivery-game/assets/scripts/domain/V2TripRules.ts
+++ delivery-game/assets/scripts/domain/V2TripRules.ts
@@ -77,7 +77,7 @@
   if(automatic)p.spentCents+=cost;this.s.supplySpentCents+=cost;
   this.s.action={kind,source:rest?'rest':source,costCents:cost,elapsedSeconds:0,durationSeconds:rest?active?10:20:item!.durationSeconds,gameSeconds:rest?active?600:0:item!.gameSeconds,restore:rest?active?20:100:item!.restore};
  }
- advanceSupply(seconds:number):number {check(finite(seconds));const a=this.s.action;if(!a)return seconds;const used=Math.min(seconds,a.durationSeconds-a.elapsedSeconds);a.elapsedSeconds+=used;this.s.gameSeconds+=used/a.durationSeconds*a.gameSeconds;
+ advanceSupply(seconds:number,advanceTripClock:boolean=true):number {check(finite(seconds)&&typeof advanceTripClock==='boolean');const a=this.s.action;if(!a)return seconds;const used=Math.min(seconds,a.durationSeconds-a.elapsedSeconds);a.elapsedSeconds+=used;if(advanceTripClock)this.s.gameSeconds+=used/a.durationSeconds*a.gameSeconds;
   if(a.elapsedSeconds>=a.durationSeconds){this.s.stamina=Math.min(100,this.s.stamina+a.restore);this.s.blocked=false;this.s.action=null;}return seconds-used;
  }
  pickupGroup(ids:string[]):boolean {
--- delivery-game/assets/scripts/map-sample/V2GameSession.ts
+++ delivery-game/assets/scripts/map-sample/V2GameSession.ts
@@ -78,7 +78,7 @@
   // Spend this interval across action and batch boundaries. A stop consumes no tail time.
   while(seconds>0){
    const iterationStart=seconds;
-   const afterSupply=this.trip.advanceSupply(seconds);used+=seconds-afterSupply;seconds=afterSupply;
+   const afterSupply=this.trip.advanceSupply(seconds,this.route.progress.phase!=='planned');used+=seconds-afterSupply;seconds=afterSupply;
    if(seconds<=0)break;
    // Settle only work available at this action instant, never borrow frame-end NPC income.
    const actionAt=wallStart+used;this.dispatch.advanceFleetTo(actionAt);
```

## 未执行案例与限制

- planned新批的付费/库存补给、active rest，完整动作与分段推进：保持G/D不变、现实恢复正确且只消费一次。
- 旧planned且G0>0、动作已部分完成，跨读档后续完：不回滚G0/elapsed，不延长期限，不重付/重吃。
- 同帧完成补给后自动出发，真实余秒、正常道路/服务加G及NPC事件时点；自动授权耗尽的末段。
- ready/pickup/travelling确认动作照旧加G，serviceCharged互斥、无单rest、取消后动作和后续新批。
- 默认单参数调用维持true；false仅停止G；非boolean标志在任何状态改变前拒绝。
- 重复/回退帧、后台、暂停、广告、rebase首帧、零体力与恢复封顶；真实期限/迟到/到账与UI效果。

以上均未执行。没有运行tests/typecheck/TS/编译/回归/Creator/浏览器/游戏/购买接单/真实或合成存档。patch工具明确跳过per-file tsc；自动LSP仍提示旧Game.includes目标lib缺失，相关行全文未变，本批不改lib、不清理无关诊断，不声称编译通过。

编辑只用正常patch/write_file；未改权限、未派Agent/Codex、未commit/push。未构建/部署；既有 `v2-product-eta-1106` 是历史候选，不包含本次新改动，不能据其入口检查推称本次已验证。父PM后续组织独立复审/必要构建，作者不判全产品完成。
