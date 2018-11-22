# coding=utf-8
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 把manage.py所在目录添加到系统目录
os.environ['DJANGO_SETTINGS_MODULE'] = 'AJoke.settings'  # 设置setting文件
django.setup()

from records.models import CSInfo, InterfaceLogs
from ENVS import DICT_TOKEN_PARAM

import asyncio
import json
import time
from datetime import datetime

import aiohttp
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job


def get_request_data(url, data):
    return json.loads(requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data)).text)


def get_token(token_url, token_data):
    dict_data = get_request_data(token_url, token_data)
    return dict_data.setdefault("provider_access_token", '') or dict_data.setdefault("access_token", '')


async def post(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(data)) as resp:
            res_data = await resp.text()
            return json.loads(res_data)


async def request(url, data, obj):  # 异步
    result = await post(url, data)
    param = {"status_code": result["errcode"], "status_msg": result["errmsg"], "platform": 0}
    if result.setdefault("errmsg", '') == "ok":
        param.update(result["device_info"])
        InterfaceLogs.objects.create(**param)
        obj.is_sync_wx = 1
        obj.save()
    else:
        InterfaceLogs.objects.create(**param)


def request_(url, data, obj):  # 同步版
    result = get_request_data(url, data)
    param = {"status_code": result["errcode"], "status_msg": result["errmsg"], "platform": 0}
    if result.setdefault("errmsg", '') == "ok":
        param.update(result["device_info"])
        InterfaceLogs.objects.create(**param)
        obj.is_sync_wx = 1
        obj.save()
    else:
        InterfaceLogs.objects.create(**param)


def main():
    print(datetime.now())
    while True:
        provider_access_token = get_token()
        if provider_access_token:
            to_sync_apps = CSInfo.objects.filter(is_sync_wx=0)  # 待同步的固件升级信息（客户已下载）
            post_url = "https://qyapi.weixin.qq.com/cgi-bin/service/add_device?provider_access_token={0}".format(
                provider_access_token)
            tasks = []
            for app in to_sync_apps:
                post_data = {"model_id": app.device_type.model_id, "device_sn": app.device_number}
                tasks.append(asyncio.ensure_future(request(post_url, post_data, app)))
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(300)


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


@register_job(scheduler, "interval", minutes=1, replace_existing=True)
def main_():  # 同步版
    print(datetime.now())

    def sync_qywx():
        provider_access_token = get_token(DICT_TOKEN_PARAM["qywx"]["token_url"], DICT_TOKEN_PARAM["qywx"]["token_data"])
        if provider_access_token:
            to_sync_apps_wx = CSInfo.objects.filter(is_sync_wx=0, deal_tag_wx=0)  # 待同步企业微信的固件升级信息（客户已下载）
            post_url_wx = "https://qyapi.weixin.qq.com/cgi-bin/service/add_device?provider_access_token={0}".format(
                provider_access_token)
            for app in to_sync_apps_wx:
                post_data_wx = {"model_id": app.device_type.model_id, "device_sn": app.device_number}
                result = get_request_data(post_url_wx, post_data_wx)
                param = {"status_code": result["errcode"], "status_msg": result["errmsg"], "platform": 0}
                if result.setdefault("errmsg", '') == "ok":
                    param.update(result["device_info"])
                    InterfaceLogs.objects.create(**param)
                    app.is_sync_wx = 1
                    app.deal_tag_wx = 1
                    app.save()
                if result["errcode"] == 600021:  # 同步失败，企业微信后台已有此设备SN
                    InterfaceLogs.objects.create(**param)
                    app.is_sync_wx = 1  # 标记已同步
                    app.deal_tag_wx = 1  # 标记已处理
                    app.save()
                else:
                    InterfaceLogs.objects.create(**param)
                    app.deal_tag_wx = 1  # 标记已处理
                    app.save()

    def sync_fufu():
        access_token = get_token(DICT_TOKEN_PARAM["fufu"]["token_url"], DICT_TOKEN_PARAM["fufu"]["token_data"])
        if access_token:
            to_sync_apps_ff = CSInfo.objects.filter(is_sync_ff=0, deal_tag_ff=0)  # 待同步服服CRM的固件升级信息（客户已下载）
            post_url = "http://120.76.167.138:7080/std/spi/update_sn?access_token={0}"
            post_url_ff = post_url.format(access_token)
            for app in to_sync_apps_ff:
                post_data_ff = {"sn": app.device_number, "type": "W_" + app.device_type.device_name}
                result = get_request_data(post_url_ff, post_data_ff)
                if result.setdefault("error", "") == "invalid_token":
                    access_token = get_token(DICT_TOKEN_PARAM["fufu"]["token_url"],
                                             DICT_TOKEN_PARAM["fufu"]["token_data"])
                    post_url_ff = post_url.format(access_token)
                    result = get_request_data(post_url_ff, post_data_ff)
                param = {"status_code": result["encrypted"], "status_msg": result["data"], "platform": 1}
                if result["data"]:
                    InterfaceLogs.objects.create(**param)
                    app.deal_tag_ff = 1
                    app.save()
                else:
                    InterfaceLogs.objects.create(**param)
                    app.is_sync_ff = 1
                    app.deal_tag_ff = 1
                    app.save()

    sync_qywx()
    sync_fufu()


# main_()
register_events(scheduler)
scheduler.start()
print("Scheduler started!")
