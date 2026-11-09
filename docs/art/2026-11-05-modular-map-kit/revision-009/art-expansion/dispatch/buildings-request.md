# 小批原生制作：形态/自然层次补充，不阻塞批量地图

你是原生美术制作执行，必须实际使用已有内置image_gen，**不是只做选型或规划**。本批不是说当前20源几何需要新PNG，而是父已看第三批真实图：四族重复、全单层小体量不足、种植边缺自然层次；用户明确要求建筑/植物等真正多样，不能把“现库能塞”当成美术类型足够。只做下面两件，不开海量朝向或车型矩阵。

共同只读输入：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json（真实投影u/n/Z；现A族u屏幕-28.486、n+55.406、竖边竖直）、/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/references/approved-25-index.json与contact（用户认可25图，图07锁TR25-v2），原用户风格参考、当前第三批实际图与现库仅用于差异核对，不拿新AI图递归充当风格母版。母图/版本/SHA/局部参考bbox如实记录；源图看不清具体物件就写“风格参考下原创补充”，不编原身份/实测尺寸。

每件先在本组references内制作专用**输入几何**，PIL/程序仅可画结构导向，不是最终美术。实际image_gen参数至少附该几何与25图局部画法参考；只写文字声称引用不算。若工具真实schema支持在透明几何底稿上原生编辑，可用其保轮廓再绘画法；不猜参数、不用外部API、不用程序涂成品/旋转镜像/拉斜旧图冒新原生。

画法同已认可日间日系都市厚涂：适度概括色面/笔触/光照，不是写实产品照/强镜面，也不是平面粗描边图标。透明背景、完整地脚/根，单体，无人车/道路/大片地面/天空/文字logo、无夜间亮窗/灯带/荧光叶/大雾底；不屋顶种树。新植物按自然绿深度，不全黄绿，不用大色块地面冒根。

每件一次实际原生请求，先保存工具源逐字节副本和provenance再继续第二件。原生真实尺寸照存，不承诺工具未给出的高清。用只读revision-005/runtime-size-pilot/export_runtime.py单件导出长边<=280，正等比裁透明边，像素缩小不能改世界尺寸。每件交ID-v1.png、ID-runtime-280.png及.runtime.json、provenance.json、REPORT.md，原生工具路径/输入路径/真实prompt/SHA齐全。两图实际打开，标真实可见脚点/门槛像素与隐藏推断，必要编号叠图仅诊断；透明孔不当门，阴影/屋顶边不当脚点，不规则弦不当相机轴。

第一件运行图若明显风格/透明/结构/直边机位错先报告，不盲目整批重试。不要为小纹理角度重生，不能代填精密配准、用户验收/已接入。完成第一件也可给父会话发稳定路径/SHA供增量，不等待无问题回复。最多一次/件，网络失败如实报，不无限自重连、不重复已有输出。

你不改共享库/renderer/Tiled/原city/业务/UI/经济/存档，不测试/typecheck/回归/提交，不创建其他Agent。上轮写权限结束；唯一写下面目录，其他全只读。根catalog由父维护。

## 本组唯一写集
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/references/buildings
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/native/B12-001
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/art-expansion/native/B13-001

## 两件明确目标
[
  {
    "id": "B12",
    "name": "单层带檐小住宅",
    "group": "buildings",
    "dimensionsCandidate": [
      6.4,
      4.6,
      3.8
    ],
    "visualGap": "现库没有真正紧凑单层住宅；不是把B05缩小或裁半",
    "identity": "单层主体、不同于B05的短前廊/偏置门，浅灰抹灰与克制暖砖或木细部、深灰瓦；不做豪华别墅"
  },
  {
    "id": "B13",
    "name": "单层小街铺",
    "group": "buildings",
    "dimensionsCandidate": [
      6.0,
      5.0,
      3.6
    ],
    "visualGap": "区别于三层B01的紧凑临街店铺",
    "identity": "低平顶/局部短雨棚、转角展示窗与明确真实入口，简洁砖/木/灰墙；空白牌面，不是B01改牌"
  }
]
尺寸是PM游戏体量候选，不是源测绘。不得宣称四新件解决全部多样性。
保持紧凑低层而非多层楼缩图；画出可分辨门与有限台阶，入口默认近侧临街面，可有一个真实侧入口但不得靠透明处虚构门。两条真实基座方向需对照导向，0.9/1.1是以后实例比例不是本次把旧楼改尺寸。
