from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import BSInfo, Device


@admin.register(BSInfo)
class BSInfoAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'contact', 'device_number',
                    'application_date', 'colored_status', 'device_type')
    list_filter = ('state', 'application_date')
    list_display_links = ('colored_status',)
    list_per_page = 50
    search_fields = ('applicant', 'device_number')
    ordering = ('-application_date',)
    date_hierarchy = 'application_date'


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_name', 'del_tag')
    list_filter = ('device_name', 'del_tag')
    list_display_links = ('id', 'device_name')
    list_per_page = 50
    search_fields = ('device_name',)


class MyAdminSite(AdminSite):
    site_header = '中控智慧包管理后台'
    site_title = site_header


admin_site = MyAdminSite('my_admin')
admin_site.register(BSInfo, BSInfoAdmin)
admin_site.register(Device, DeviceAdmin)
