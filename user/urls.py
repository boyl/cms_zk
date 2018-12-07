# coding=utf-8

from django.conf.urls import url
from django.views.generic import TemplateView

from .views import authenticate

urlpatterns = [
    url(r'^login/$', TemplateView.as_view(template_name='user/login.html'), name='login'),
    url(r'^authentication/$', authenticate, name='authenticate'),
]
