# 图像高输出尺寸未保留：可转发的无密钥诊断

本文件仅本地准备，未自动发给服务商。未附密钥、账号凭据或原始参考图片。

- 路线：现有openai-api兼容服务，host=zee.zeehub.cn；操作images.edit，model=gpt-image-2，quality=high，n=1，max_retries=0。
- 输入图片和所有非尺寸参数相同；仅同步改变size和prompt中对应尺寸文字。
- 实验1 UTC 2026-11-06T11:43:23.427097+00:00：请求3824x2144，原始返回1674×940，SHA0ab233b8bf8f8465a19e0470b4be4dadfd7937b8a27426a732cd749cc6482b87。
- 实验2 UTC 2026-11-06T12:12:35.071433+00:00：请求3840x2160，原始返回1672×941，SHA112cc4aad350be35d96902c2d2ecf394d17cef2a38465b6d6431734186a77054。
- 客户端直接解码API图片payload并原字节保存；没有输出裁切、插值或改大小。
- model catalog显示gpt-image-2存在，但未提供输出尺寸能力元数据。存在模型名不等于大尺寸能力已确认。
- 本地未记录服务请求ID，不能补造；可以按上述时刻及账户侧请求记录定位。

请确认：该服务images.edit是否支持原始返回3840×2160；是否需要文档明确的其他参数或通道；若不支持，实际支持的输出像素预算是什么。当前只请求说明，不授权更换账户/凭据或升级套餐。

OpenAI接口参照链接（本环境仅检索摘要可用，完整正文抓取失败）：https://developers.openai.com/api/reference/python/resources/images/methods/edit
