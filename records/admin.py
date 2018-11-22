from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import BSInfo, Device, InterfaceLogs, CSInfo


@admin.register(BSInfo)
class BSInfoAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'contact', 'device_number',
                    'application_date', 'colored_status', 'device_type')
    list_filter = ('state', 'application_date')
    list_display_links = ('device_number', 'colored_status',)
    list_per_page = 50
    search_fields = ('applicant', 'device_number')
    ordering = ('-application_date',)
    date_hierarchy = 'application_date'


@admin.register(CSInfo)
class CSInfoAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'contact', 'device_number',
                    'is_sync_wx', 'is_sync_ff', 'device_type', 'deal_tag_wx', 'deal_tag_ff')
    list_display_links = ('device_number',)
    list_filter = ('device_type', 'device_number')
    list_per_page = 50
    search_fields = ('device_type', 'device_number')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_name', 'del_tag')
    list_filter = ('device_name', 'del_tag')
    list_display_links = ('id', 'device_name')
    list_per_page = 50
    search_fields = ('device_name',)


@admin.register(InterfaceLogs)
class InterfaceLogsAdmin(admin.ModelAdmin):
    list_display = (
        'status_code', 'status_msg', 'model_id', 'device_sn', 'secret_no', 'device_id', 'qr_code',
        'platform', 'create_time', 'deal_time')
    list_filter = ('status_msg', 'create_time', 'deal_time')
    list_per_page = 50
    search_fields = ('device_sn', 'platform', 'status_code')
    readonly_fields = list_display


class MyAdminSite(AdminSite):
    site_header = '固件升级包后台管理'
    site_title = site_header


admin_site = MyAdminSite('my_admin')
admin_site.register(BSInfo, BSInfoAdmin)
admin_site.register(Device, DeviceAdmin)
admin_site.register(CSInfo, CSInfoAdmin)
admin_site.register(InterfaceLogs, InterfaceLogsAdmin)
admin.site.site_header = '固件升级包后台管理'
admin.site.site_title = '固件升级包后台管理'
