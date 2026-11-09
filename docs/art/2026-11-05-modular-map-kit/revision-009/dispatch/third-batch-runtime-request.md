# 第三批20源稳定输入已核：第二批实显回报后再增量接入

你和规划会话的502失败提醒已核；当前已看到你的实际浏览器取图和规划实际脚本输出，恢复不是仅active标签。本条不重试输入、不重复生成素材。请先完成当前第二批5源的真实运行尺寸核验/截图/最终回报，再做这一批，不插队/重置。

固定新输入：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/planning/fit-round-3/third-expansion-batch.json
父核SHA256：654ccb00f1f75af0f487c9d2d3f7e8f88b06258ca1f73542dcc950978c1a6a12
20唯一源/20视觉模块/96实际地面，B01/B02/B05/B06；与首4、第二5源集合无重复。实际是同一180m邻接阈值的连通片，不把180m说成整片直径。原9360首批和1ba663第二批SHA不变。全部已按真实源载体/停靠node分层；不新增或移动业务点/POI/导航边，当前不需新PNG。654+2387的两源一景候选未计入本批，不自动加入。

## 新schema与比例
本批visualReplacementOf用sourceIndices数组＋sourcePolygonsMap（不再是单sourceIndex），每对象目前均单元素；root另有sourceMappings/sourceIndices。适配真实字段，不能读旧单键失败后当空源或伪造ID。保留原source-index集合/多对多语义和sourceDataChanged=false；候选关联不是原source已存在楼-POI绑定。
父已逐件算过：plan.worldSizeUnits等于canonicalWorld*uniformScale，0.9/1/1.1已作用一次，B01=1。节点变换和图框不能再双乘；保留canonicalPPU/UV，实际UI尺寸读回验证，旧比例不改。image和Frame仍按真实file+SHA共享，不能为0.9/1.1另拷PNG。

## 基线与冲突
规划保护visible69稳定快照与冻结第二批5/20预占，不包含第二批接入时你若额外添加的真实场地物/补面。因此接入前以**第二批实际最终基线**全量保护并重新核新20足迹/通道/院落对新增物的冲突，不把规划旧快照当当前全保护。保留全部已有节点/地面字段、镜头、D内存路线、原city/原道路完整顺序/宽度/方向。仅逐新候选处理冲突，必要局部整体平移/有限新通路应派生单列，不能改图门/强压node、改路、删旧楼或全体避碰豁免。原载体豁免仅自己sourceIndices，其他源/蓝边/水/旧场景继续硬守。

## 场景/范围
用districtOrganization的用地和连接关系呈现连续住宅/街铺/办公片，不一律每栋做大三角凸包前场或一排相同模板。新96面按真实用途草地/院落/窄路径组织；若已有资产与净空允许可少量附树/灯等，但额外数量/位置单列，不为了凑“丰富”挤门路。完整场地仍欠的地方如实报告，不假白盒补未画源楼。
仍在你006/integration、006/viewer、009/pipeline独占写集；planning/原生/其他项目与业务源全只读。源输入SHA与派生SHA分别保存，Tiled按persistentId增量，不init/新工程/旋转镜像/非等比，不生图，不游戏tests/typecheck/回归/FPS基准/存档/提交，不新开或暴露服务。地面按有限区域或你已准备的tile引用使用，不能因20对象而常驻全县巨大画布；无FPS/实际内存验证就只报候选预算。

交同一viewer的新片区实际较宽关系图＋2～3个能看清楼门/路径与不同类型的近景（不是20个小点）；记录准入/拒绝数量、真实源绑定与实际累计/本批计数、全部<=280资源字节、节点UI尺寸及Frame共享和保护SHA。20是静态候选数量，不强凑：若某项失败，精确报告但让其余可用项显示。你必须先交第二批5源当前进展，之后再执行本条。
