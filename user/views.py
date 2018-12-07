from django.views.generic.base import View
from requests.exceptions import RequestException
from django.shortcuts import render

from utils import OAuthRequestTool
from ENVS import APP_ID, APP_SECRET, TOKEN_URL_FMT, USER_INFO_URL

# Create your views here.

oauth = OAuthRequestTool()


def authenticate(request):
    """主要目的: 1.获取用户信息并保存; 2.设置cookie"""
    pass


class AuthenticateView(View):
    template_name = "records/index.html"

    def get(self, request):
        code = request.GET.get("code", None)
        if code:
            token_url = TOKEN_URL_FMT.format(APP_ID, APP_SECRET, code)
            try:
                token_dict = oauth.get_access_token_dict(token_url)
            except RequestException:
                raise
            else:
                access_token, open_id, expires_in = (token_dict.get("access_token"),
                                                     token_dict.get("openid"), token_dict.get("expires_in"))
                user_info_url = USER_INFO_URL.format(access_token, open_id)
                try:
                    user = oauth.get_user_profile(user_info_url)  # 获取用户对象
                except RequestException:
                    user = None
                else:
                    user.save_user_2db(access_token)  # 若数据库异常， 则直接抛出
            response = render(request, self.template_name)
            response.set_cookie("cookie_id", user.cookie if user else None)  # 设置cookie
            return response

    def post(self, request):
        pass
