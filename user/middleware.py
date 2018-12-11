# coding=utf-8
from django.utils.deprecation import MiddlewareMixin

from utils import CookieTool


class CookieMiddleware(MiddlewareMixin):

    cookie_tool_instance = CookieTool()

    def process_request(self, request):
        self.cookie_tool_instance.set_user_by_cookie(request)
