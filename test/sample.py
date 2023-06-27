# -*- coding: utf-8 -*-
import fc2
import json


# LTAI5t7EWcV6VHL4wgCZsXGA
# L7vnFWgpE3INyhl8XJxQKTyjtNn9I2
# 1885707335435084.cn-hangzhou.fc.aliyuncs.com
client = fc2.Client(endpoint="http://1885707335435084.cn-hangzhou.fc.aliyuncs.com",
                    accessKeyID="LTAI5t7EWcV6VHL4wgCZsXGA", accessKeySecret="L7vnFWgpE3INyhl8XJxQKTyjtNn9I2")

# 提取音视频信息 返回json格式音视频meta信息


def GetMediaMeta():
    # "bucket_name" : "bucket-yveltal",
    #     "object_key" : "480P_10.mov"  # 待处理音视频
    resp = client.invoke_function("ffmpeg-app", "GetMediaMeta", payload=json.dumps(
        {
            "bucket_name": "bucket-chanfun",
            "object_key": "test.mp4",
        })).data
    print(resp)

# 获取视频时长 返回时长


def GetDuration():
    resp = client.invoke_function("ffmpeg-app", "GetDuration", payload=json.dumps(
        {
            "bucket_name": "bucket-chanfun",
            "object_key": "test.mp4",
        })).data
    print(resp)


# 制作缩略图 生成一张或多张雪碧图, output目录下生成480P1.jpg,480P2.jpg
def GetSprites():
    resp = client.invoke_function("ffmpeg-app", "GetSprites", payload=json.dumps(
        {
            # "bucket_name" : "bucket-yveltal",
            # "object_key" : "480P_10.mov"  # 待处理音视频
            "bucket_name": "bucket-chanfun",
            "object_key": "test.mp4",
            "output_dir": "test/output/",
            "tile": "2*2",    # 必填，雪碧图的 rows * cols
            "start": 0,       # 选填, 从第几秒开始
            "duration": 18,   # 选填, 基于 start 之后的多长时间的视频内进行截图
            "scale": "-1:-1",  # 选填, 320:240，默认-1:-1为原视频大小,
            "interval": 3,    # 选填, 每隔多少秒截图一次
            "padding": 1,     # 选填, 图片之间的间隔，默认0
            "color": "Black",  # 选填, 背景色 https://ffmpeg.org/ffmpeg-utils.html#color-syntax
            "dst_type": "jpg"  # 选填, jpg, png
        })).data
    print(resp)

# 视频加水印 生成output/480P.mov


def VideoWatermark():
    resp = client.invoke_function("ffmpeg-app", "VideoWatermark", payload=json.dumps(
        {
            "bucket_name": "bucket-chanfun",
            # "object_key": "video/inputs/abc.mov",
            "object_key": "480P.mov",
            "output_dir": "test/output/",
            "vf_args": "drawtext=fontfile=/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc:text='hello函数计算':x=100:y=50:fontsize=24:fontcolor=DarkBlue"
            # x y与左上角像素距离, fontsize字体大小, fontcolor同GetSprites()中的color
        }), headers={"x-fc-invocation-type": "Async"}).data
    # , headers={"x-fc-invocation-type": "Async"}
    print(resp)

# 视频转GIF 生成output/480P.gif


def VideoGif():
    resp = client.invoke_function("ffmpeg-app", "VideoGif", payload=json.dumps(
        {
            "bucket_name": "bucket-yveltal",
            "object_key": "480P_10.mov",
            "output_dir": "test/output/",
            "start": 0,      # 可选, 均不填写默认整个视频转GIF
            "duration": 3,   # 可选, start开始的某段时间转GIF
            "vframes": 30    # 可选, start开始的指定帧数转GIF, 同时存在时以duration为准
        })).data
    print(resp)


# 音视频格式转换 生成output/480P.wav
# 视频 ->音频/视频  音频 ->音频
def AudioVideoConvert():
    # "bucket_name" : "bucket-yveltal",
    # "object_key" : "480P_10.mov",
    resp = client.invoke_function("ffmpeg-app", "AudioVideoConvert", payload=json.dumps(
        {
            "bucket_name": "bucket-chanfun",
            # "object_key": "test.mp4",
            "object_key": "video/inputs/abc.mov",
            "output_dir": "test/output/",
            "dst_type": ".mp4",
            "ac": "1",       # 音频可选, 声道数
            "ar": "32000",   # 音频可选, 采样率 8000 16000 32000 44100 48000
            "vf": "320:200"  # 视频可选, 分辨率
        }), headers={"x-fc-invocation-type": "Async"}).data
    print(resp)


def AudioVideoClip():
    resp = client.invoke_function("myfnf-demo", "clip", payload=json.dumps(
        {
            "oss_bucket_name": "bucket-chanfun",
            "video_key": "480P.mov",
            "output_prefix": "test/output/",
            "start": 15,      # 可选, 默认从头开始
            "duration": 10,   # 可选, 剪辑start开始的某段时间
            "vframes": 100    # 可选, 剪辑start开始的指定帧数, 同时存在时以duration为准
        }), headers={"x-fc-invocation-type": "Async"}).data
    print(resp)

# 音视频剪辑 生成output/480P.mov
def AudioVideoClipMulti():
    clip_params = [{"start": 0, "duration": 5, "vframes": 50},
                   {"start": 10, "duration": 8, "vframes": 80}]
    resp = client.invoke_function("myfnf-demo", "clip_multi", payload=json.dumps(
        {
            "oss_bucket_name": "bucket-chanfun",
            "video_key": "480P.mov",
            "output_prefix": "test/output/",
            "clip_params": clip_params
            # "start": 15,      # 可选, 默认从头开始
            # "duration": 10,   # 可选, 剪辑start开始的某段时间
            # "vframes": 100    # 可选, 剪辑start开始的指定帧数, 同时存在时以duration为准
        })).data
    print(resp)

# 直播流录制 生成output.mp4


def LiveRecord():
    resp = client.invoke_function("ffmpeg-app", "LiveRecord", payload=json.dumps(
        {
            "bucket_name": "bucket-yveltal",
            "output_dir": "test/record/",
            "object_key": "output.mp4",  # 录制保存的文件名
            "source_url": "rtmp://mobliestream.c3tv.com:554/live/goodtv.sdp",
            "duration": 5,               # 录制时间(秒)
        })).data
    print(resp)


# GetMediaMeta()
# GetDuration()
# GetSprites()
# VideoGif()
# AudioVideoConvert()
# LiveRecord()

# AudioVideoClip()
AudioVideoClipMulti()
# VideoWatermark()
