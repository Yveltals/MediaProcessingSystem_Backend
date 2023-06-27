# MediaProcessingSystem_Backend

# 应用详情

基于函数计算 FC + FFmpeg + OSS 实现 Serverless 架构的弹性高可用的高度自定义音视频处理应用，包括以下多个模块：

- AudioVideoConvert: 音视频格式转换
- AudioVideoClip: 音视频剪辑
- GetMediaMeta: 获取音视频 meta 信息
- GetDuration: 获取音视频时长
- VideoGif: 视频转(提取) gif 
- GetSprites: 制作雪碧图
- VideoWatermark: 视频添加水印
- LiveRecord: 直播流录制

# 部署

> 一人部署即可

- [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) 
- 初始化项目：`s init ffmpeg-app -d ffmpeg-app`   
- 进入项目，并进行项目部署：`cd ffmpeg-app && s deploy -y`

# 函数使用
> 详细使用例见sample.py
## get_media_meta 获取音视频 meta 信息

**event format:**

```json
{
  "bucket_name": "test-bucket",
  "object_key": "a.mov"
}
```

**response:**

```json
{
   "format": {
      "bit_rate": "488281",
      "duration": "179.955000",
      "filename": "http://fc-hz-demo.oss-cn-hangzhou-internal.aliyuncs.com/a.mov",
      "format_long_name": "QuickTime / MOV",
      "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
      ...
   },
   "streams": []
   ...
}
```

**S 工具调用示例:**

```bash
$ s GetMediaMeta invoke -e '{"bucket_name": "test-bucket","object_key": "a.mp4"}'
```

**python sdk 调用函数示例:**

```python
import fc2
import json

client = fc2.Client(endpoint="http://1123456.cn-hangzhou.fc.aliyuncs.com",accessKeyID="xxxxxxxx",accessKeySecret="yyyyyy")

resp = client.invoke_function("FcOssFFmpeg", "GetMediaMeta", payload=json.dumps(
{
    "bucket_name" : "test-bucket",
    "object_key" : "a.mp4"
})).data

print(resp)
```
