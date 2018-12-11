# coding=utf-8

from django.conf.urls import url
from django.views.generic import TemplateView

from .views import AuthenticateView

urlpatterns = [
    url(r'^login/$', TemplateView.as_view(template_name='user/login.html'), name='login'),
    url(r'^authentication/$', AuthenticateView.as_view(), name='authenticate'),
]
