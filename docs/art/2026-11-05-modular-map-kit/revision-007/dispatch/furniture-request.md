# 场景小物原生制作执行（不是规划）

用户已明确要求在地图中补灯箱、油箱、桌椅板凳、围栏、菜地及其他生活细节。你是原生素材制作角色，必须实际使用当前内置image_gen，不是只出选型/提示词。无需再问是否开工；不另建Agent，不用外部API或shell绘图冒充成品。复用当前已成功生图工具。

## 共同只读输入
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json：真实u/n/axisX/Y/Z；长u屏幕-28.486度，n约+55.406度，竖边竖直。
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/references/approved-25-index.json与approved-25-contact.jpg：25图现行认可版本，图07锁TR25-v2。按物件语境打开一个完整源图后选局部色彩/材质参考，不递归拿新AI图当画风母版，不借完整源图构图。源里看不清的小物可以原创补充，明确记“风格参考下原创补充”，不能编造原物件bbox/身份。
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-005/runtime-size-pilot/export_runtime.py：已有单件派生导出器，只读使用。
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/catalog.json：这批ID、用途、PM候选尺寸与朝向契约。候选米数非源实测。

## 每件生产流程（必须实际提交图片）
1. 在自己的references写集做对应形体/地脚几何图，服从真实投影；PIL/程序仅可画输入几何，不是最终美术。
2. image_gen真实reference参数至少提交对应几何图和25图局部风格参考，角色明确为几何/画法，不接受只在文字里提角度而实际图片输入为空。画法沿用日间日系都市动漫厚涂：概括但有绘制明暗，不是写实产品照/强金属反射，也不是粗描边平面图标。
3. 每件只一次原生请求，保存工具源逐字节副本、实际路径/尺寸/SHA/实际prompt/提交参考路径SHA，再继续下一件。先打开首件运行图检查，明显风格错误或连接/工具阻塞就回报，不盲目做完整批。不要无限网络重试，不去续发已返回图片的调用。
4. 只物件本体、完整地脚，背景透明，无整片地面/道路/天空/人车/文字logo，不带大块烘焙阴影。菜畦内部土壤、拱棚范围内栽培是物件组成，允许有限内部土壤，不扩到周围草坪。
5. 保留大母版但不入运行包，现有导出器裁透明边后最大长边280，保持正等比。不要用运行图像素大小改世界尺寸，别旋转/镜像/拉斜PNG冒充另一个朝向。围栏P06/P07是同款两原生朝向，不计两个新款式。

每件在native/ID-001内交ID-v1.png、ID-runtime-280.png及.runtime.json、provenance.json、REPORT.md（实际缺陷、足点/门位/连接边、尺寸为候选）。可以定义好的双桶组合，但不能做多视角拼板或一张画十种小物。原生/运行图都实际打开；少量碎边/隐藏接点诚实记录，不自动第三次重试或代填精密配准/用户验收。

原路/水/边界/游戏/UI/经济/车辆业务/存档全部不动，不tests/typecheck/回归/提交，不动其他角色的文件或007根目录清单。只写下面自己的目录；上轮写权限已结束，旧成果一律只读，除本任务明确给出的B10修订目录。完成中文简报自动回父会话，首件已归档也可先用bb thread tell thr_2qc9rtsa9r报告路径/SHA以供增量接入，再继续本组，不等待无问题的回复。

## 本组唯一写集
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/references/furniture
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/native/P03-001
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/native/P04-001
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/native/P05-001

## 本组物件
[
  {
    "id": "P03",
    "name": "靠背长椅",
    "owner": "furniture",
    "dimensions": [
      2.0,
      0.65,
      0.9
    ],
    "identity": "木条坐面与靠背、深灰金属腿，长边沿u",
    "contexts": [
      "街边休憩",
      "住宅小院",
      "公共设施外"
    ],
    "status": "assigned-not-produced",
    "dimensionMeaning": "PM-game-scale-candidate-not-source-measured",
    "runtimeMaxEdge": 280
  },
  {
    "id": "P04",
    "name": "独立户外圆桌",
    "owner": "furniture",
    "dimensions": [
      1.0,
      1.0,
      0.75
    ],
    "identity": "圆木桌面＋简洁金属支腿，不绑定椅凳、地板或餐具",
    "contexts": [
      "商业街室外休憩",
      "庭院"
    ],
    "status": "assigned-not-produced",
    "dimensionMeaning": "PM-game-scale-candidate-not-source-measured",
    "runtimeMaxEdge": 280
  },
  {
    "id": "P05",
    "name": "独立圆凳",
    "owner": "furniture",
    "dimensions": [
      0.42,
      0.42,
      0.45
    ],
    "identity": "无靠背圆凳，与P04材质相配，便于不旋转PNG而重复摆放",
    "contexts": [
      "桌边",
      "住宅小院"
    ],
    "status": "assigned-not-produced",
    "dimensionMeaning": "PM-game-scale-candidate-not-source-measured",
    "runtimeMaxEdge": 280
  }
]
