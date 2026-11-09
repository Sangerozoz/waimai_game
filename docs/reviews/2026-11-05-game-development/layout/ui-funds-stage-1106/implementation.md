# UI资金状态刷新：隔离候选交回

状态：已实现stage候选，待PM规格和独立质量门禁；未应用live、未构建、未运行、不自判PASS。

## 基线与文件
- 逻辑目标：`delivery-game/assets/scripts/map-sample/V2GameUI.ts`，live未改。
- 候选：`docs/reviews/2026-11-05-game-development/layout/ui-funds-stage-1106/assets/scripts/map-sample/V2GameUI.ts`。
- stage起始及live前后SHA：`9c9484b24bbd36ea25da10c0cbf6d8080dcd7e5d78a9195603dffeaf423617dc`。
- stage候选SHA：`d2da7f2a95d1c36bf49ffb39457e557d26312ef512784eaaa3e8a23dc298fcc3`。
- 精确补丁：`candidate.diff`，SHA `fc20354b128b82d47c81388aded9b884788fd162e6d5831100e9fb1891a430fd`；9个hunk，在内存逐hunk核对原行/行数并重建候选成功，未应用到live。
- 完整输入哈希、静态证据、覆盖列表、未执行case：`implementation.json`。原`baseline-manifest.json`保持不变。

## 根因及最小修正
原showUpgrade在461–475行仅构造一次shortfall/余额/禁用按钮。余额A<Q时原action没有tap；NPC到账后B>=Q只有HUD变，旧确认层不会恢复。

候选165–177行通过局部Node→refresh注册，801行接既有0.5秒HUD读模型节奏。刷新不调用render或业务命令；不新增timer、Promise或全局UI框架。

- 400–404/492–498：按原id和当前level重读既有riderUpgradeQuote/vehicleUpgradeQuote，不接slots新接口或自己定价。
- 502–541：原层更新余额、差额、详情和费用；金额/报价不变则不改控件，仅报价key或可负担性变更时重建确认按钮。原action/tap启禁链不绕过。
- 点击再次核对当前现金和报价。报价不同先刷新并再次确认；钱不够不commit。原Runtime.command仍是扣费/升级权威，不自动升级。
- 当前modal、button身份、submitting和isValid/active检查防旧触摸及重复提交；关闭、render和destroy先注销、inactive，再销毁。新代码无迟到业务Promise或timer。

## 同类控件及范围
- 补给原257行存在同类cash快照门禁：278–291行以同机制只替换付费按钮，点击复核现金。库存、免费休息、自动补给和三种期限分支保持。
- 首页原164行shortfall文案：按同目标id局部更新，不重建首页。
- 车辆购买、地图购买没有构造期现金enabled快照，原命令校验保持；没有擅自新增门禁。
- 骑手招募/升级入口、车辆归属和主角工作车辆限制保持；不加全局NPC禁用。
- 钱包详情/账单的只读一次性余额或统计不是启禁/shortfall控件，本次未改，不宣称所有金额展示均实时。

## 保留及证据边界
源文本比对确认食品解析、rider几何/身份、车辆/地图/账单、food/ETA订单整段与基线相同（仅升级点击读quote连接点改变）。scrolling helper精确相同；render调用数4→4，scheduleOnce调用数2→2。未改Spacing/Skin/资源/Runtime/领域参数/地图或A的stage。所有冻结输入收口SHA无漂移。

编辑器自动LSP反馈stage行185/401/493的row隐式any；隔离相对依赖没有复制。已只读核对live类型签名，不修改配置或运行tsc消除它，不能宣称编译通过。

## 未执行与应用门禁
F01–F12均未运行：真实NPC到账/反向余额变化、1分阈值和零费用、quote变化、满级/busy、快速重复触摸、取消/切页/销毁/皮肤晚回调、滚动、补给及车辆地图购买领域校验。未tests/typecheck/TS/App函数/Creator/浏览器/业务/档案操作，未commit/push或派Agent。

PM另做独立门禁，核对live仍匹配9c基线后才可应用逻辑替换束；漂移须rebase/续审，不恢复284/81f，不覆盖当前4196已审展示。交回即停止写入，父PM复原Default。
