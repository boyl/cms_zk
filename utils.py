# coding=utf-8
import hashlib
import random
import string
import time

import requests
from django.conf import settings

from user.models import UserProfile, OAuth


class OAuthRequestTool(object):
    def __init__(self):
        pass

    def get_access_token_dict(self, token_url):
        return self.send_request(token_url)

    def refresh_access_token(self, token_url):
        pass

    def is_active_access_token(self, token_url):
        pass

    def get_user_profile(self, token_url):
        resp = self.send_request(token_url)
        return UserInfo(**resp)

    @classmethod
    def send_request(cls, url):
        return requests.get(url).text


class UserInfo(object):
    def __init__(self, **kwargs):
        for key, value in kwargs:
            setattr(self, key, value)

    def save_user_2db(self, token):
        dict_user_profile = dict()
        for key in [f.name for f in UserProfile._meta.fields if f.name != 'id']:
            setattr(dict_user_profile, key, getattr(self, key))
        user = UserProfile.objects.create(**dict_user_profile)
        dict_oauth = {"user": user, "oauth_id": getattr(self, "openid"), "oauth_union_id": getattr(self, "unionid")}
        dict_oauth.update({"access_token": token})
        OAuth.objects.create(**dict_oauth)

    def generate_cookie(self):
        pass

    def get_object_from_oauth(self):
        return OAuth.objects.filter(oauth_union_id=getattr(self, "unionid"))


class CookieTool(object):
    def __init__(self):
        pass

    def cookie2user(self, user):
        if isinstance(user, UserInfo):
            user.cookie = self.get_cookie(user.get_object_from_oauth())
            return user

    def get_cookie(self, user):
        user_id = user.id
        access_token = user.access_token
        active_in = 1800
        random_str = self.generate_random_str()
        expires_in = int(time.time()) + active_in
        to_hash = self.list_2char([user_id, access_token, expires_in, random_str])
        hash_str = self.md5(to_hash)
        OAuth.objects.filter(id=user_id).update(expires_in=expires_in, random_str=random_str, md5=hash_str)
        return ':'.join([str(user_id), str(expires_in), hash_str])

    @classmethod
    def generate_random_str(cls):  # 随机生成4-8为字符
        return ''.join(random.sample(string.ascii_letters + string.digits, random.choice(range(4, 9))))

    @classmethod
    def md5(cls, arg):  # 这是加密函数，将传进来的函数加密
        md5_pwd = hashlib.md5(bytes(settings.SECRET_KEY, encoding='utf-8'))
        md5_pwd.update(bytes(arg, encoding='utf-8'))
        return md5_pwd.hexdigest()  # 返回加密的数据

    @classmethod
    def list_2char(cls, raw_list):
        return ''.join([str(i) for i in raw_list])

    def check_cookie(self, cookie):  # 验证cookie是否有效
        if cookie:
            user_id, expires_in, cookie_md5 = cookie.split(":")
            if time.time() > int(expires_in):
                return False
            try:
                oauth = OAuth.objects.get(id=int(user_id))
            except OAuth.DoesNotExist:
                return False
            else:
                the_str = self.list_2char([oauth.id, oauth.access_token, oauth.expires_in, oauth.random_str])
                return cookie_md5 == self.md5(the_str)
        return False
