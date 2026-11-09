# T04-v2 原生交付

一次实际内置image_gen请求，真实提交透明底不透明叶团3D结构图与认可图05/TR-35-v1局部参考。真实工具源路径/完整prompt/图片输入路径与SHA/原参考版本和bbox在provenance.json。当前schema仅用了实际referenced_image_paths附件，没有编造mask/edit参数。风格参考下原创补充；候选尺寸[4.5, 4, 5.5]不是源实测。专用实体导引按原u/n/axisZ投影，冠体不透明遮干；它只作输入，不是交付美术。

原生1254×1254 RGBA，1206351字节，alpha [0, 255]；运行280×224，102370字节，长边<=280。工具源和副本逐字节一致，运行SHA核验一致。仅规定只读导出器正等比裁边；未调色/变形/修边。母版未打包。

实体遮挡后大部分枝干被冠体遮住，只有下方短干根露出，较v1减少正视展示枝根；但画面仍有正视树立面感，62.5度高相机顶视无法确认通过，继续hold。冠缘有灰绿/亮绿碎边，无大块灰底；不清边冒机位修好，不第三次生成。

地脚记录（原生像素粗估，不是精密配准）：{"visibleFrontRootFlareBoxNativeApproximate": [552, 912, 672, 1008], "visibleFrontRootTipNativeApproximate": [594, 1000], "worldRootOriginPixel": null, "worldRootOriginVisibility": "under trunk/crown; inferred only, not transparent gap or visible precise root origin", "rearContacts": "hidden"}。无门位/直线连接契约，叶缘不能拿来证明相机轴。

状态：hold-camera-uncertain-and-fringe-no-third-attempt。未用户验收、未相机/场景验收、未接入。T05独立候选，T04继续hold不连锁冻结T05。T04-001只读保留；本轮各一次且不再生成。无工具/网络阻塞，未游戏测试/typecheck/提交/共享库修改，未新服务或派其他角色。
