# coding=utf-8
from django.core.management.base import BaseCommand, CommandError

from multiprocessing import Process
import sys
import os
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 把manage.py所在目录添加到系统目录
os.environ['DJANGO_SETTINGS_MODULE'] = 'AJoke.settings'  # 设置setting文件
django.setup()

from records.models import CSInfo, InterfaceLogs

import asyncio
import json
import time
from datetime import datetime

import aiohttp
import requests


class Command(BaseCommand):
    help = "Async post request."

    def handle(self, *args, **options):
        p = Process(target=main)
        p.start()


def get_request_data(url, data):
    return json.loads(requests.post(url, data=json.dumps(data)).text)


def get_token():
    token_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_provider_token"
    token_data = {
        "corpid": "wwb712a415cce67382",
        "provider_secret": "PiAHUR71Vo0F8axiJiQFlgLJ__KEnhPFiyrowWDmw4f1ZVWXoptUUuCpqJ_Ur5_Q"
    }
    dict_data = get_request_data(token_url, token_data)
    return dict_data.setdefault("provider_access_token", '')


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


def main():
    print('main():', datetime.now())
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
            print('300s after awake!')


if __name__ == '__main__':
    main()

