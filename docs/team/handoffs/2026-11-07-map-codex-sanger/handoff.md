# 地图任务接续：Codex / GPT-6.1-Sol（Sanger）/ max

**实际新主会话：@thread:thr_fs5qphhxgc。** 以同目录`current-dispatch.json`为准：首次启动前已做仅本线程的Account Pooler bypass，实际execution读回指定model/max，已观测到真实工具执行，fresh环境没有旧池路由变量。首个`dispatch.json`/`thr_5xd9wkm7y2`因已固化旧Pool provider失败，仅保留迁移诊断，不能作为当前主会话。91件保护地图文件在交接后再次核SHA不变；没有改全局路由或凭据。

## 用户最新直接指令与角色

本接续仅地图线，产品/UI/经济/存档与地图完全独立，不能替产品线派工。源对话为 @thread:thr_2qc9rtsa9r；不要fork或读整个旧长聊天，用本交接及下面当前文件接续，同一checkout所有未提交内容保留。

用户最新原话：
- “我现在在 codex 里面接入了模型。我们不使用 hermes 了。你能把任务切换过去，并且继续任务，保持任务进度，任务要求不丢失吗？”
- “新的模型在codex里面，选择6.1-sol（Sanger），强度使用max”
- 后续“继续”。

**本次地图路由覆盖AGENTS中11-06的旧Hermes地图路由要求，不扩大为产品线迁移。** 当前目录已核：provider=`codex`，完整model ID=`ccs-sanger/gpt-6.1-sol`，displayName=`GPT-6.1-Sol（Sanger）`，支持`max`。不是旧OpenAI原生`gpt-6.1-sol`，不使用任何GPT-6-astra，不改凭据/全局Provider/账户池设置。当前接续应成为新的地图主会话；旧Hermes/旧原生Codex会话留历史，不续派或自动重试旧任务。

## 环境

- root `/Users/sanger/Documents/ChatGPT/taptap 2`
- project `proj_3sznws2gfk`，environment `env_e54zrbdgxt`，host `host_tr578kqahd`
- branch `codex/food-delivery`，同一checkout，不新worktree、不切分支、不覆盖/清理未提交。
- 安全底线：不读/输出凭据，不操作真实浏览器游戏进度或存档，不改产品/UI/经济/正式路由，不发布/强推，不擅自扩大任务。

## 当前真实路线（最重要）

旧单楼素材/006～009来源绑定扩张已经不是当前路线。用户之后因单体房屋朝向与任意道路不匹配，改为**完整小街区/整区底图＋Tiled独立矢量描路**，独立导航小样已获“导航可以”。不要再恢复一堆单体方向矩阵或旧163对象主图的源净距扩张，也不因旧Agent延迟回报又重做B12/B13/T04等。

当前主入口：`docs/art/2026-11-06-city-image-map/planning/progress-current.json`。

真实已有：
- A/B/C三个地区原生图已产并实际入图；当前art为A2、B1、C-001，A-v2核心增密视觉方向获认可，A-v1像郊区的反馈不能丢。
- 可看地图 `docs/art/2026-11-06-city-image-map/compact-three-v1/index.html`；官方Tiled/接入和导航证据按progress与各目录记录读取。19节点/21边/1连通分量是该小样，不是整城全路网。
- C原生：`regions/C-001/native.png`，1536×1024，SHA `6aa6063d2326c6d4004f97dee35b02fb58b87b2d2e22d1c3a89b5b6b2ebecfba`。
- 用户认可已有画风、颜色、清晰度、比例/道路表现与A2核心密度，不等于全城规模、面积、全路网或正式游戏验收。

## 仍未解决，不能迁移后假装通过

用户质疑三地区总图太小、路网太少，问达到目标一半了吗。目标约旧25图总体面积1/4，不是图数/文件像素1/4；同形状参考约1.66×1.66km（旧框约3.32km本身近似）。不能补D就称整城，现A/B/C尚未建立可信米制覆盖，不能报达到一半。

当前权威文件依次读：
1. `planning/current-scope.json`
2. `planning/scale-scope-audit.json`
3. `planning/scope-recovery-v1/CITY-CONTRACT.md`
4. `planning/scope-recovery-v1/README.md`、`scope-plan.json`
5. `planning/scope-recovery-v1/capacity-proof/RESULT.md`、`independent-review.json`
6. `planning/scope-recovery-v1/scale-board-status.md`、`consumer-scale-source-contract.json`

当前草案：64街坊/81交口/18走廊是PM组织提案，不是用户钦定的棋盘/数量。必须保完整主干/次干/生活支路、功能与密度过渡；住宅约半按蓝内净可用面积理解，不按楼数假达标。4～6图是尚未被容量证明的PM预算，暂以6讨论，不是用户硬规定；不能自动恢复9/16/25或暗缩城市、楼/路、相机来凑图数。

实际高返回能力已做两次：请求3824×2144返回1674×940；控制请求3840×2160返回1672×941。不是成功拿到4K，不存在已验证高清母版；不插值冒高清、不把实验图当新增正式地区。progress仍记录`newImageRequestsAllowed=0`/D未恢复/productionReady=false；而最近直接用户又说“继续生图吧”。你应读取实际规范和最近授权，继续已授权的范围/能力工作，但**这不表示尺寸/规模技术门禁已经解决**。若仍需要城市范围、清晰度、图数的真实取舍，用已有证据具体汇报，不能盲批量或保证下次必成功。迁移本身不改变这些事实。

## 制作要求

- 风格与建筑身份可参考原认可25图，图07锁TR25-v2；还要参考其整张拼图的楼群、相对位置/大小、楼与路宽/地块比例、前后排/院落与城区→郊区→外围疏密，不只是从图里挑同款楼。原拼图仍名义拼接，不当米制真值或直接运行底图。
- 固定斜俯视、日间日系都市厚涂，保持用户认可颜色，不整体加蓝/发黄，不普遍亮灯，不屋顶种树。建筑/树/车/道具有真实形态差别，不以换色/改牌/移位计新款。
- 不把AI整图裁切剪断楼后称完成。分块按完整街坊与道路/绿地走廊，真实接头与拓扑重要，小像素差可接受，新底图按实际画面描新路，不强套旧road坐标。
- 旧city/旧红蓝绿文件/旧路网/用户手调布局/原图/业务/存档都留只读，不在正式旧图上做破坏性迁移。新图世界与旧图资料分开，绝不覆盖用户手调。
- “280像素运行图”仅旧单体素材包政策，不能把新整区底图压到280。整区清晰度绑定真实返回、CSS画幅/DPR/合法最大近景预算，不能把比例尺数字当整幅视宽。
- 静态源码核得CityMap的720设计单位是整幅宽，60是比例尺线；最近全幅120m、默认180m、最远1200m是现有源码行为，不是用户设备/新图镜头验收。375CSSpx、3.125px/m等仍假设，不拿来假定整城图数。
- 正式地图游戏测试未获本批授权；产品线“继续并测试”不覆盖地图。必要独立Tiled导入/图片/导航交付与用户验收分开，不跑全游戏tests/typecheck/回归/FPS，不碰真档。

## 历史成果与旧回报

旧模块包与163对象/506地面主图保留，实际scene SHA `237252cf5858346686c707335f1a323c0d14261631ec6262b6d403bbfd94b5cc`、TMJ SHA `26eb9baad3f38a13570c5c23d4cadd5a5f4f4ef29f1c5a174436d3c566fd99e8`，仅历史/可手调资产来源；不重放旧批次。B13 clean/T05/T04-v2延迟消息也只归档，不触发旧生产路线。

00:34产品线曾写`docs/team/handoffs/2026-11-07-codex-migration/`，其停止记录是产品A/B，不是本地图接续。不要修改或接管产品会话。

本次查旧消息曾对旧thr_8vs8ndqxxa做一次失败轮重试；识别最新地图路线后已主动停止，旧队列不再继续。未改账户/全局设置。旧163场景/TMJ再次读回仍为上述SHA。所有旧地图Agent现保留来源，后续只在正确Sanger路由按必要写集派工。

## 新主会话开工第一步

先`bb status --json`和`bb thread options --self --json`确认实际provider/model/max，写本目录`new-thread-receipt.json`（只放非秘密ID/设置/已读当前入口/当前阶段/下一具体动作）。然后继续当前尺度/范围与真实原生能力的实际任务，不只确认收到后停。

不需要用户重讲已有要求。遇能力/网络阻塞如实报告并限时，不假装后台有图在生成。凡新图/代码/导出都须实际文件、尺寸/hash、实际显示证据支撑。先保持任务进度与约束，再在最新范围内向下推进；当前无授权改全局登录、API密钥或机器权限。
