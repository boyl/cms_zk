"""AJoke URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView, ListView
from django.views.static import serve
from django.conf.urls.static import static

from django.conf import settings
from records.admin import admin_site
from records.views import download_file, single_apply, download_check, batch_apply, single_download, batch_download
from records.models import Device

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^my_admin/', admin_site.urls),
    url(r'^$', TemplateView.as_view(template_name='records/index.html'), name='index'),
    url(r'^index_up$', TemplateView.as_view(template_name='records/index_up.html'), name='index_up'),
    url(r'^index_up_cs$', ListView.as_view(model=Device, template_name='records/index_up_cs.html'), name='index_up_cs'),
    url(r'^index_up_cs_d$', TemplateView.as_view(template_name='records/index_up_cs_d.html'), name='index_up_cs_d'),
    url(r'^index_up_bs1$', ListView.as_view(model=Device, template_name='records/index_up_bs1.html'), name='index_up_bs1'),
    url(r'^index_up_cs1$', ListView.as_view(model=Device, template_name='records/index_up_cs1.html'), name='index_up_cs1'),
    url(r'^index_up_bs$', ListView.as_view(model=Device, template_name='records/index_up_bs.html'), name='index_up_bs'),
    url(r'^index_up_bs_d$', TemplateView.as_view(template_name='records/index_up_bs_d.html'), name='index_up_bs_d'),
    url(r'^download_check$', download_check, name='download_check'),
    url(r'^download_file$', download_file, name='download_file'),
    url(r'^do_action$', single_apply, name='do_action'),
    url(r'^single_download$', single_download, name='single_download'),
    url(r'^batch_apply$', batch_apply, name='batch_apply'),
    url(r'^batch_download$', batch_download, name='batch_download'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


import records.interfaceprocess
