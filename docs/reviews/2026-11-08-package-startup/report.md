# 历史构建清理与启动传输优化

用户要求清理构建/缓存、缩小游戏包，并明确指定TinyPNG。**清理已完成；HTTP与启动改善已实测，最终复审中，尚未切换试玩；TinyPNG图片压缩仍被网页失败和未收到API密钥阻塞。** 总任务没有完成，图片体积仍为原值。

## 磁盘清理

检查了本地监听服务实际目录和正在运行的Creator工程。只删除当前项目19个停用v2构建与主工程library/temp，共**4,259,390,978逻辑字节 / 4,295,905,280分配字节**。所有旧生成文件的路径/大小/SHA已保存，源素材、文档证据、Git、用户档及其他工程未动。地图4181、历史仍运行4187/4194、正式4182/4196及一个回退包在清理时保留；已关闭本PM过期4198并取消其分享。[清理回执](cleanup-receipt.json)。

## 图片压缩真实状态

原包210,799,733字节，PNG200,588,751字节；254张PNG/JPG共201,877,408字节。用户允许压缩运行图片、原高清素材继续保留。静态核对发现46项V2未用资源约60.35MB，但原包默认还有旧入口，直接删除哈希资源会破坏引用，本批未做盲删。

按用户指定实际尝试TinyPNG公网网页：669827字节nav-icons与一个约69kB的已裁切PNG先后得到“Something went wrong / INVALID”，没有输出下载链接。官方API空请求可到达并返回401；环境无已配置TinyPNG变量，安全输入请求超时，未收到密钥。**没有将任何本地压缩结果冒称TinyPNG。** [第一次失败](tinypng/web-failure-observed.json) · [重试](tinypng/web-retry-observed.json) · [凭据状态](tinypng/credential-status.json)。

官方API批处理脚本已准备在`tinypng-batch.py`：只读高清源，按输入SHA复用结果，检查格式与尺寸，不向日志回显key，官方计数达到免费月500前停下；未得到密钥前未执行图片压缩。总图片预算及实际TinyPNG来源门禁仍失败。第三方服务说明：[TinyPNG官方API](https://tinypng.com/developers)、[API文档](https://tinypng.com/developers/reference/http)。

## 独立完成的启动传输工作

现行Python标准server没有Content-Encoding压缩。新增`serve-web.py`并由原serve-web.sh接入：gzip/identity协商、Vary、按表示区分ETag、HEAD/304、HTML重新校验及带内容版本资源长期缓存；保留loopback绑定和目录跳转，限制根目录及符号链接越界。

首次真实RED8项2pass/6fail，GREEN8/8；B首审发现identity拒绝与子目录301边界。补测RED9pass/2fail→GREEN11/11，原始失败及两轮冻结全部保留。打包器仅以明确`--transport-only`创建工作副本：所有254张图片、city和非启动业务JS保持字节；配置去掉固定2000ms启动等待，正确更新settings→application→entry→HTML版本链，添加gzip sidecar。Cocos文档支持启动屏配置：[官方构建选项](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/build-options.html)。

末尾自生成收据缺gzip的问题通过现有包检查发现并修复，产物只新增package-receipt.json.gz，前575项SHA都相同。现有25份gzip均精确解压回原数据。图片整体检查仍为**4通过/2失败**，失败明确为TinyPNG实际来源及PNG50MiB内部预算，未修改用例掩盖。本传输工作包212,884,632字节（含gzip副本），**磁盘包体没有变小**；减少的是实际HTTP下载字节，后续仍必须完成图像压缩。[传输测试](transport-followup-green-receipt.json) · [包门禁](transport-package-final-gates.log)。

## 真实冷启动对照

全新headless origin，缓存关闭，下载200000字节/秒（1.6Mbps）、延迟150ms，每版各一次有界样本。新档仅用于隔离浏览器，从真实开始按钮进入首页；没有访问或清除用户进度。

| 实测项 | 前包 | 本传输副本 |
|---|---:|---:|
| 入口可操作时间 | 23.1535秒 | 7.6402秒 |
| 入口累计资源体积（编码body） | 3,681,344字节 | 979,796字节 |
| 点击开始→Runtime及首页可操作 | 23.9369秒 | 5.5468秒 |
| 首页可操作时累计资源body | 8,669,031字节 | 2,263,155字节 |

两样本Runtime/观测错误均空。入口到点击之间的人为等待不计入点击耗时；该结果是一次先后有界测量，不能推广为每个玩家的打开时间或设备FPS。首页可操作不等于所有后台图片已显示；已另取消限速检查截图，图片仍为原字节。[完整对照](cold-comparison.json) · [画面](transport-home.jpg)。

最初用错Puppeteer限速参数导致ProtocolError、随后整段采集超host调用期限均留在cold-attempt-01/与原始日志；改成分段启动和浏览器内rAF记录后得到上述有效样本，未把失败计时混入结果。

## 仍待完成

TinyPNG实际输出、图片像素预算及压缩画面检查；远程已登录用户链路与点击即玩目标仍未验收。上一批U01长历史帧事务约99–101ms、真机FPS、原档跨打包原字节恢复、广告SDK、长期二八与整体98%不因本轮启动改善关闭。当前等独立复审完成后交付传输改善；TinyPNG需安全提供官方API key或网页恢复后继续，不使用别的压缩器冒称。
