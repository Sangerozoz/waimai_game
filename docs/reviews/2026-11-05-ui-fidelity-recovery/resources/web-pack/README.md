# 四类非地图 UI Web 衍生包交付

线程 `thr_rhp4ifmpzk`，父 PM `thr_axf6i4e89t`。**已产资源并接入源码；未构建、未部署、未游戏验证，不能据此关闭用户缺图问题或报98%。** 本轮中断后仅接续落盘产物、补短截止/离线清点/报告，没有重新生产整套资产。

## 范围与实际资产

严格仅底栏及其 UI 皮肤/图标、肖像、车辆侧视图、餐品。未生成任何地图衍生，未写 `ui-v2/showcase/`，未改公共 `manifest.json`、`portraits.json`、`maps.json` 或地图调用。导航“地图”小图标属于底栏图标，不是地图素材。

- 资源绝对目录：`/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/resources/ui-v2/web/`
- 运行映射：上述目录的 `pack.json`，42源路径、143原裁切框→143衍生纹理；`pack.json.meta`、目录 `web.meta` 及每图 meta 齐。
- 原图完整保留、不改不删。42源图 SHA 与生成记录相同；其中40源图也与此前 `resources/asset-audit.json` 一致，另2张是本次补纳入的旧 UI fallback 图集。
- 总计143图：112 PNG（保透明/半透明）、31 JPEG（不透明肖像及背景，quality92、4:4:4、无调色/无重绘）。145个新增主UUID（143图+JSON+目录）不重复，未发现与其他 assets meta 冲突。

| 类别 | 衍生纹理 / key别名 | 对应原图字节 | 衍生图字节 |
|---|---:|---:|---:|
| 底栏/皮肤/图标及旧fallback | 52 / 54 | 20,145,779 | 2,935,786 |
| 主角+30NPC肖像 | 31 / 32 | 15,513,807 | 1,324,821 |
| 10档车辆侧视 | 10 / 10 | 22,694,260 | 7,495,002 |
| 50餐品 | 50 / 50 | 11,342,450 | 5,722,923 |

合计原图 **69,696,296字节** → 衍生图 **17,478,532字节**；加映射28,167字节为 **17,506,699字节（17.51MB）**，比对应原图库少 **74.88%**。这是四类完整资源库的磁盘/候选传输负载比较，不是首屏实测，不包含引擎 import JSON、HTTP头、原图失败回退，也不能推断用户首开提速比例。

肖像32个别名不是32人：`portraits/hero` 与 `cartoon/avatar` 指向同一主角裁切、同一衍生资源 `ui-v2/web/portraits-01c64dfa01b4`；总身份仍31人。

## 实际源码接线

只修改以下3个独占源码（已有恢复修复保留，未用旧备份覆盖）：

1. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/UIArtResources.ts`
   - 新增内部 `loadArtRegion`，原resource+原像素框作统一键。Cartoon归一化框按原图尺寸和原有端点 `Math.round` 规则还原，不拿原框去裁小纹理。
   - 单精灵衍生帧一律 `[0,0,derivedWidth,derivedHeight]`；九宫格边距按实际衍生宽/高分别精确换算，包含整数像素舍入。
   - 两loader共用按真正Cocos路径 `ui-v2/web/<name>/texture` 的纹理Promise及一次addRef，不改全局downloader、不全量预载、不增加启动门禁。
   - 可选pack JSON**单次4s截止**；仅新增 `ui-v2/web/` 纹理每次4s、最多3次并间隔1s/2s，约15s进入原图回退，不让缺包/坏衍生先额外等待183s。原图及原manifest仍保留既有3次/每次60s策略。
   - 失败Promise删除；pack失败下一次可重试；晚到引擎回调忽略。以上时限是源码计时上界，不是已测网络完成时间，也不是网络取消。
2. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/V2ImageSkin.ts`
   - 使用统一region及缩放后的inset。maps manifest显式 `web:false`，原图/原框直接加载，不等待pack。
   - 有效性检查、销毁帧、动态label/热区、隐藏节点成功赋图/fallback规则保持。
3. `/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game/assets/scripts/map-sample/CartoonArt.ts`
   - 仅四类UI key opt-in；世界top车、历史地图/街区等key不走衍生映射。
   - 共享保留帧仍addRef。原图临时回退帧单独缓存复用，不进入成功衍生缓存，后续打开可重试小图；最坏每key多保留一张成功原图fallback帧，非无限创建。
   - 成功赋图前仍检查parent/picture存活，未恢复“隐藏父节点丢图”缺陷。

`VehicleSideArt.ts`、`FoodImages.ts` 无需改动，原签名、车型/餐品key及真实调用均通过CartoonArt接入；其当前SHA也在清点文件。公共manifest仍保存原引用，保留原source/SHA/status，不擅改资产验收状态。

## 2x预算、先样图与图片目视

先实际生成10档车的pilot，再查看完整10档及放大的D车/SS/SSS车轮、箱体和细节；再覆盖其余三类。未另生新身份或换色。

- 车辆：现有主图框500×350，contain到约1000×667，不放大原图。
- NPC肖像：最大现有cover框104×146，按覆盖后2x预算裁缩；主角方形在104×146 cover框需要146×146，衍生292×292。
- 餐品：现有146方框扣除原10px内缩，按136×136 contain的2x预算。
- 图标采用包含旧UI较大图标的保守108逻辑像素预算；勾选框36、抢单圆146、其他皮肤预算逐key记录于生成脚本/asset-records。九宫格保留切边结构，不以大空白中心强行增加纹理。原图低于预算时不放大。

[原左/衍生右离线目视入口](review.html)、[首类pilot](pilot.html)。已逐张打开四类接触表，并放大脸/车轮核对；未见新增身份、明显色调偏移或轮廓缺失。少量已有餐图裁切中的邻图碎片/源画面瑕疵如实保留，未借压缩重画。接触表部分图标放大到160px便于检查，72px勾选框在该放大图上会更软；实际逻辑框36px。没有声称零画质损失、原生高清、引擎显示通过或用户验收。

## 证据、复现与SHA

报告/脚本绝对目录：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/reviews/2026-11-05-ui-fidelity-recovery/resources/web-pack/`

- [generate-web-pack.py](generate-web-pack.py)：Pillow 11.3.0，`--category vehicles`为首类；`--category all`复现四类（PM无需为本次接续再运行，正确资产已在磁盘）。仅读原图和原manifest；输出只到专属web和本报告目录。
- [asset-records.json](asset-records.json)：每源/每衍生的**绝对路径、尺寸、字节、完整SHA256、原裁切框、衍生框、缩放/inset、预算、key别名和meta UUID**。
- [inventory-web-pack.py](inventory-web-pack.py) / [image-inventory.json](image-inventory.json)：纯图片/文件清点，143图及146别名映射完整、尺寸/alpha/inset/哈希/UUID无清点异常。没有执行TS、引擎或游戏。
- `pack.json` SHA256：`fb8b62bfff79bb840f915cab6f977ccf37f1cb7e9ae0d116c40c56de3377de30`
- `UIArtResources.ts` SHA256：`73e29316a757f4a37a2f47f188e8f558aa074aeb8270d7ce148cecab2ec9949f`
- `V2ImageSkin.ts` SHA256：`e0a160ee04ecbe0374e6d65c5b453e0921f2be4c6fa4cdfb8e6e05c01559faca`
- `CartoonArt.ts` SHA256：`5b59bb9d4c15fba335754f430641d228a20ea31023cf6385f333fba200d73e52`

地图严格排除：生成器不读取maps.json作生产输入，pack内无map-preview映射；5张map-preview原图逐一与旧audit SHA一致。`maps.json`未写，当前SHA `26f7f09c385ec3f7c7c9fb03c04b3a1779c98331be6dc07639530b8bb93a4743`。没有需要隔离的地图衍生，也未新增后撤销地图别名。

## 未验证项与PM接续

- **未运行**tests/typecheck/回归/故障注入、Creator导入/构建/部署、浏览器游戏操作、真实/合成存档。4182旧版本不代表本源码。
- 待PM独立源码与图片审核、统一Creator导入/构建，核实导出resources索引确有pack JSON和143条texture路径、JPEG/PNG解码及九宫格实际显示。磁盘/meta齐全不等于已进构建。
- 短截止是可选新包的候选策略，未测用户带宽/解码；慢网可能走原图（继承最长原图等待），超时也不能取消底层请求，可能出现旧任务与重试重叠。应由PM统一预览后按真实Timing审定，不能据此称传输问题已修复。
- 单精灵按需传图减少每次带上整图集的负载，但完整图库的请求数增加；未测引擎HTTP排队、GPU纹理内存/动态合图、首屏时长或移动端表现。
- 没有远程真实显示证据，首次全类缺图共同根因仍未确定；大图不是被证实的唯一根因。无外部依赖阻塞本次源码/图片交付，剩余发布与运行验证归PM。
