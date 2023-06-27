# -*- coding: utf-8 -*-
import subprocess
import oss2
import logging
import json
import os
import time

logging.getLogger("oss2.api").setLevel(logging.ERROR)
logging.getLogger("oss2.auth").setLevel(logging.ERROR)

LOGGER = logging.getLogger()


def print_excute_time(func):
    def wrapper(*args, **kwargs):
        local_time = time.time()
        ret = func(*args, **kwargs)
        LOGGER.info('current Function [%s] excute time is %.2f seconds' %
                    (func.__name__, time.time() - local_time))
        return ret
    return wrapper


def get_fileNameExt(filename):
    (fileDir, tempfilename) = os.path.split(filename)
    (shortname, extension) = os.path.splitext(tempfilename)
    return fileDir, shortname, extension


@print_excute_time
def handler(event, context):
    LOGGER.info(event)
    evt = json.loads(event)
    oss_bucket_name = evt["oss_bucket_name"]
    object_key = evt["video_key"]
    output_dir = evt["output_prefix"]

    vframes = evt.get("vframes")
    if vframes:
        vframes = str(vframes)
    ss = evt.get("start", 0)
    ss = str(ss)
    t = evt.get("duration")
    if t:
        t = str(t)
    creds = context.credentials
    auth = oss2.StsAuth(creds.accessKeyId,
                        creds.accessKeySecret, creds.securityToken)
    oss_client = oss2.Bucket(
        auth, 'oss-%s-internal.aliyuncs.com' % context.region, oss_bucket_name)

    exist = oss_client.object_exists(object_key)
    if not exist:
        raise Exception("object {} is not exist".format(object_key))

    input_path = oss_client.sign_url('GET', object_key, 3600)
    fileDir, shortname, extension = get_fileNameExt(object_key)
    output_path = os.path.join("/tmp", shortname + extension)

    cmd = ["ffmpeg", "-y", "-ss", ss, "-accurate_seek",
           "-i", input_path, output_path]
    if t:
        cmd = ["ffmpeg", "-y", "-ss", ss, "-t", t, "-accurate_seek",
               "-i", input_path, output_path]
    else:
        if vframes:
            cmd = ["ffmpeg", "-y", "-ss", ss, "-accurate_seek", "-i",
                   input_path, "-vframes", vframes, output_path]

    LOGGER.info("cmd = {}".format(" ".join(cmd)))
    try:
        subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as exc:
        LOGGER.error('returncode:{}'.format(exc.returncode))
        LOGGER.error('cmd:{}'.format(exc.cmd))
        LOGGER.error('output:{}'.format(exc.output))
        LOGGER.error('stderr:{}'.format(exc.stderr))
        LOGGER.error('stdout:{}'.format(exc.stdout))

    output_dir += "剪辑/"
    output_key = os.path.join(output_dir, shortname + '剪辑' + extension)

    oss_client.put_object_from_file(output_key, output_path)

    LOGGER.info("Uploaded {} to {} ".format(
        output_path, output_key))

    os.remove(output_path)

    # vf_args = evt.get("vf_args", "")
    # segment_time_seconds = str(evt['segment_time_seconds'])
    # dst_formats = evt["dst_formats"]

    return {
        # "oss_bucket_name": oss_bucket_name,
        # "video_key": output_key,  # 剪辑过后的视频 -> watermark
        # "output_prefix": output_dir,

        # "vf_args": vf_args,
        # # "segment_time_seconds": segment_time_seconds # may no needed
        # "dst_formats": dst_formats,
    }
