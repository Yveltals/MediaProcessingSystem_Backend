# -*- coding: utf-8 -*-
import subprocess
import oss2
import logging
import json
import os
import time
import requests
import datetime
import html
import re
import base64
import urllib.parse
import hashlib
from urllib.parse import urlencode


logging.getLogger("oss2.api").setLevel(logging.ERROR)
logging.getLogger("oss2.auth").setLevel(logging.ERROR)
LOGGER = logging.getLogger()
cookies: dict = {}

class CC:

    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):
        room_url = f'https://api.cc.163.com/v1/activitylives/anchor/lives?anchor_ccid={self.rid}'
        response = requests.get(url=room_url).json()
        data = response.get('data', 0)
        if data:
            channel_id = data.get(f'{self.rid}').get('channel_id', 0)
            if channel_id:
                response = requests.get(f'https://cc.163.com/live/channel/?channelids={channel_id}').json()
                real_url = response.get('data')[0].get('sharefile')
            else:
                raise Exception('直播间不存在')
        else:
            raise Exception('输入错误')
        return real_url
################################################
class KuWo:

    def __init__(self, rid):
        self.rid = rid
        self.BASE_URL = 'https://jxm0.kuwo.cn/video/mo/live/pull/h5/v3/streamaddr'
        self.s = requests.Session()

    def get_real_url(self):
        res = self.s.get(f'https://jx.kuwo.cn/{self.rid}').text
        roomid = re.search(r"roomId: '(\d*)'", res)
        if roomid:
            self.rid = roomid.group(1)
        else:
            raise Exception('未开播或房间号错误')
        params = {
            'std_bid': 1,
            'roomId': self.rid,
            'platform': 405,
            'version': 1000,
            'streamType': '3-6',
            'liveType': 1,
            'ch': 'fx',
            'ua': 'fx-mobile-h5',
            'kugouId': 0,
            'layout': 1,
            'videoAppId': 10011,
        }
        res = self.s.get(self.BASE_URL, params=params).json()
        if res['data']['sid'] == -1:
            raise Exception('未开播或房间号错误')
        try:
            url = res['data']['horizontal'][0]['httpshls'][0]
        except (KeyError, IndexError):
            url = res['data']['vertical'][0]['httpshls'][0]
        return url
################################################
class PPS:

    def __init__(self, rid):
        self.rid = rid
        self.BASE_URL = 'https://m-x.pps.tv/api/stream/getH5'
        self.s = requests.Session()

    def get_real_url(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Referer': 'https://m-x.pps.tv/'
        }
        tt = int(time.time() * 1000)
        try:
            res = self.s.get(f'https://m-x.pps.tv/room/{self.rid}', headers=headers).text
            anchor_id = re.findall(r'anchor_id":"(\d*)', res)[0]
            params = {
                'qd_tm': tt,
                'typeId': 1,
                'platform': 7,
                'vid': 0,
                'qd_vip': 0,
                'qd_uid': anchor_id,
                'qd_ip': '114.114.114.114',
                'qd_vipres': 0,
                'qd_src': 'h5_xiu',
                'qd_tvid': 0,
                'callback': '',
            }
            res = self.s.get(self.BASE_URL, headers=headers, params=params).text
            real_url = re.findall(r'"hls":"(.*)","rate_list', res)[0]
        except Exception:
            raise Exception('直播间不存在或未开播')
        return real_url
################################################
class XunLei:

    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):
        url = 'https://biz-live-ssl.xunlei.com//caller'
        headers = {
            'cookie': 'appid=1002'
        }
        _t = int(time.time() * 1000)
        u = '1002'
        f = '&*%$7987321GKwq'
        params = {
            '_t': _t,
            'a': 'play',
            'c': 'room',
            'hid': 'h5-e70560ea31cc17099395c15595bdcaa1',
            'uuid': self.rid,
        }
        data = urlencode(params)
        p = hashlib.md5(f'{u}{data}{f}'.encode('utf-8')).hexdigest()
        params['sign'] = p
        with requests.Session() as s:
            res = s.get(url, params=params, headers=headers).json()
        if res['result'] == 0:
            play_status = res['data']['play_status']
            if play_status == 1:
                real_url = res['data']['data']['stream_pull_https']
                return real_url
            else:
                raise Exception('未开播')
        else:
            raise Exception('直播间可能不存在')
################################################
class DouYu:

    def __init__(self, rid):
        self.did = '10000000000000000000000000001501'
        self.t10 = str(int(time.time()))
        self.t13 = str(int((time.time() * 1000)))

        self.s = requests.Session()
        self.res = self.s.get('https://m.douyu.com/' + str(rid), timeout=30).text
        result = re.search(r'rid":(\d{1,8}),"vipId', self.res)

        if result:
            self.rid = result.group(1)
        else:
            raise Exception('房间号错误')

    @staticmethod
    def md5(data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def get_pre(self):
        url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + self.rid
        data = {
            'rid': self.rid,
            'did': self.did
        }
        auth = DouYu.md5(self.rid + self.t13)
        headers = {
            'rid': self.rid,
            'time': self.t13,
            'auth': auth
        }
        res = self.s.post(url, headers=headers, data=data, timeout=30).json()
        error = res['error']
        data = res['data']
        key = ''
        url = ''
        if data:
            rtmp_live = data['rtmp_live']
            url = data['rtmp_url'] + '/' + rtmp_live
            key = re.search(r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}p?(.m3u8|/playlist)', rtmp_live).group(1)
        return error, key, url

    def get_js(self):
        result = re.search(r'(function ub98484234.*)\s(var.*)', self.res).group()
        func_ub9 = re.sub(r'eval.*;}', 'strc;}', result)
        if use_quickjs:
            js_func = quickjs.Function('ub98484234', func_ub9)
            res = js_func()
        else:
            js = execjs.compile(func_ub9)
            res = js.call('ub98484234')

        v = re.search(r'v=(\d+)', res).group(1)
        rb = DouYu.md5(self.rid + self.did + self.t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        if use_quickjs:
            js_func = quickjs.Function('sign', func_sign)
            params = js_func(self.rid, self.did, self.t10)
        else:
            js = execjs.compile(func_sign)
            params = js.call('sign', self.rid, self.did, self.t10)

        params += '&ver=219032101&rid={}&rate=-1'.format(self.rid)

        url = 'https://m.douyu.com/api/room/ratestream'
        res = self.s.post(url, params=params, timeout=30).json()['data']
        key = re.search(r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}p?(.m3u8|/playlist)', res['url']).group(1)

        return key, res['url']

    def get_pc_js(self, cdn='ws-h5', rate=2):
        res = self.s.get('https://www.douyu.com/' + str(self.rid), timeout=30).text
        result = re.search(r'(vdwdae325w_64we[\s\S]*function ub98484234[\s\S]*?)function', res).group(1)
        func_ub9 = re.sub(r'eval.*?;}', 'strc;}', result)
        if use_quickjs:
            js_func = quickjs.Function('ub98484234', func_ub9)
            res = js_func()
        else:
            js = execjs.compile(func_ub9)
            res = js.call('ub98484234')

        v = re.search(r'v=(\d+)', res).group(1)
        rb = DouYu.md5(self.rid + self.did + self.t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        if use_quickjs:
            js_func = quickjs.Function('sign', func_sign)
            params = js_func(self.rid, self.did, self.t10)
        else:
            js = execjs.compile(func_sign)
            params = js.call('sign', self.rid, self.did, self.t10)

        params += '&cdn={}&rate={}'.format(cdn, rate)
        url = 'https://www.douyu.com/lapi/live/getH5Play/{}'.format(self.rid)
        res = self.s.post(url, params=params, timeout=30).json()['data']

        return res['rtmp_url'] + '/' + res['rtmp_live']

    def get_real_url(self):
        ret = {}
        error, key, url = self.get_pre()
        if error == 0:
            ret['900p'] = url
        elif error == 102:
            raise Exception('房间不存在')
        elif error == 104:
            raise Exception('房间未开播')
        else:
            key, url = self.get_js()
            ret['2000p'] = url
        return url
################################################
class BiliBili:

    def __init__(self, rid):
        self.rid = rid
    
    def get_status(self):
        full_url: str = 'http://api.live.bilibili.com/room/v1/Room/room_init?id=' + self.rid
        response = requests.get(url=full_url, cookies=cookies)
        doc: dict = json.loads(response.text)
        msg: str = doc.get('msg')
        if doc.get('data'):
            live_state = True
        else:
            live_state = None
        return live_state, msg


    def get_m3u8(self):
        qn: str = str(1)
        full_url: str = 'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl?cid={}&platform=h5&otype=json&quality={}'.format(self.rid, qn)
        response = requests.get(url=full_url, cookies=cookies)
        doc: dict = json.loads(response.text)
        msg: str = doc.get('message')
        try:
            m3u8_url: str = doc.get('data').get('durl')[0].get('url')
        except:
            return None, msg
        else:
            return m3u8_url, msg


    def get_real_url(self):
        room_status: tuple = self.get_status()
        if room_status[0]:
            room_m3u8: tuple = self.get_m3u8()
            if room_m3u8[0]:
                LOGGER.info("m3u8 url found.")
                LOGGER.info(room_m3u8[0])
                return room_m3u8[0]
            else:
                print('m3u8 url NOT found.Error message:' + room_m3u8[1])
        else:
            print('未找到直播间.Error message:' + room_status[1])
################################################


def get_real_url(site: str, rid: str):
    try:
        if site == "BiliBili":
            return BiliBili(rid).get_real_url()
        elif site == "CC":
            return CC(rid).get_real_url()
        elif site == "PPS":
            return PPS(rid).get_real_url()
        elif site == "KuWo":
            return KuWo(rid).get_real_url()
        elif site == "XunLei":
            return XunLei(rid).get_real_url()
        else:
            LOGGER.info('Unreached site: {}'.format(site))
    except Exception as e:
        print('Exception: ', e)
        return False


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
    oss_bucket_name = evt["bucket_name"]
    site = evt["site"]
    room_id = str(evt["room_id"])
    segment_time = str(evt["segment_time"])
    duration = str(min(evt["duration"],720))
    live_name = evt["live_name"]
    dst_type = evt["dst_type"]
    output_dir = evt["output_dir"]
    
    source_url = get_real_url(site, room_id)
    LOGGER.info(source_url)
    
    now_time = (datetime.datetime.utcnow()+datetime.timedelta(hours=8)).strftime("-%Y-%m-%d-%H-%M-%S")
    object_key = live_name + now_time

    creds = context.credentials
    auth = oss2.StsAuth(creds.accessKeyId,
                        creds.accessKeySecret, creds.securityToken)
    oss_client = oss2.Bucket(
        auth, 'oss-%s-internal.aliyuncs.com' % context.region, oss_bucket_name)

    # cmd = ['ffmpeg','-i',source_url,'-t','13','-c','copy','-f','segment','-segment_time',segment_time,'/tmp/{}-%03d{}'.format(object_key,dst_type)]
    cmd = ['ffmpeg','-i',source_url,'-t',duration,'-c','copy','-f','segment','-segment_time',segment_time,'/tmp/{}-%03d{}'.format(object_key,dst_type)]

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

    for filename in os.listdir('/tmp/'):
        filepath = '/tmp/' + filename
        LOGGER.info("filename = {}".format(filename))
        # if filename[:-8] == object_key:
        filekey = os.path.join(output_dir, filename)
        oss_client.put_object_from_file(filekey, filepath)
        os.remove(filepath)
        LOGGER.info("Uploaded {} to {}".format(filepath, filekey))
    
    return "ok"
