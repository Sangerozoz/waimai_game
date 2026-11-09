# 25图参考粗摆附件

本附件先借原25图总图及**图03／TR-33-v1**的大市场＋高低住宅/公建组合做一个代表性小街区，不是整县重排、道路配准或最终验收。原v1用户文件和程序主地图均未覆盖。连接502的旧会话已停止并取消第三次自动重试，此附件由地图PM直接在独立目录制作。

## 看结果

- `index.html`：原总图、原单图区参考与实际Cocos画面对照，可直接看静态图片。
- `cocos-reference25.jpg`：真实运行截图，不是生成的效果图。
- 当前项目HTTP入口：`/delivery-kit/reference25/preview-reference/?view=user`。
- 实际运行读回172个视觉节点、32张引用PNG，共享Frame、节点scale=1；这是整份视觉副本的计数，不是172栋楼或新经营点。

## 用Tiled改

先解压原`map-assets-prototype-v1.zip`，再把本附件的`reference25`放在`v1`旁边，不能单独移走附件目录。原34类图片复用`../v1/assets/`，新增P11花箱/P12候车棚在本附件assets中；两项默认锚点/尺寸是粗估，后脚、玻璃和细边保留提示。

1. 打开`reference-layout.tmj`，移动/等比缩放/复制/删放视觉对象。P11/P12另有`templates/`模板。
2. 保存后在reference25目录运行：
   `python3 export_reference_preview.py --map reference-layout.tmj --output preview-user`
3. 通过静态HTTP查看`preview-user/?view=user`。标准库Python即可，无须city原工程或新增账号。首次导出会从相邻v1复制已有引擎壳；只写本附件输出，不写TMJ或v1。附件ZIP不重复携带引擎/已引用PNG，解包后需先导出生成交互预览。

不要重新运行`build_reference_layout.py`来“恢复”用户布局；它是首次制作工具，布局存在时会拒绝重建。后续用户图永不自动重置。

## 真正借用的关系及仍粗的地方

- 市场从旧0.9实例比例改为1.2，让其成为主要大体量；小住宅保持较小尺度。
- 前排小住宅、后排组合住宅与较高街楼、低层公建成组，替代原先三个孤立物件；仍非原图逐楼复刻。
- 庭院与前场连接，增加绿边、花箱及路边空候车棚；原道路完整数组、POI/nav和业务只作只读来源，不新增经营或公交功能。
- 白色铺地、绿地边、楼间空隙仍粗，高楼脚下地面未完善，树/道具可继续调整；未做精密碰撞/导航或用户验收。全县其他区域未因此完成。没有运行游戏测试或回归。

来源、实际参数变化和保护SHA见`references/source-record.json`、`layout-changes.json`及`actual-runtime.json`。参考图是原拼接的派生缩略/裁片，不是新高清母版，也不作为游戏背景纹理。
