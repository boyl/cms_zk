from django.db import models
from django.conf import settings
from django.utils.html import format_html

# Create your models here.


def bs_upload_to(instance, filename):
    return '/'.join([settings.MEDIA_ROOT, 'BS', instance.device_type.device_name, instance.device_number, filename])


class CSInfo(models.Model):
    SYNC_CHOICE = ((0, '未同步'), (1, '已同步'))
    applicant = models.CharField('申请人', default='-', max_length=20, null=True, blank=True)
    contact = models.CharField('联系方式', max_length=20, null=True, blank=True)
    device_number = models.CharField('SN号码', max_length=30)
    is_sync_wx = models.IntegerField('是否同步企业微信', choices=SYNC_CHOICE, default=0)
    is_sync_ff = models.IntegerField('是否同步服服后台', choices=SYNC_CHOICE, default=0)
    deal_tag_wx = models.IntegerField('企业处理标志', choices=((0, '未处理'), (1, '已处理')), default=0)
    deal_tag_ff = models.IntegerField('服服处理标志', choices=((0, '未处理'), (1, '已处理')), default=0)

    device_type = models.ForeignKey('Device', verbose_name='设备型号')

    class Meta:
        unique_together = ("device_number", "device_type")
        verbose_name = '固件记录'
        verbose_name_plural = verbose_name


class BSInfo(models.Model):
    applicant = models.CharField('申请人', default='-', max_length=20, null=True, blank=True)
    contact = models.CharField('联系方式', max_length=20, null=True, blank=True)
    device_number = models.CharField('SN号码', max_length=30)
    device_number_detail = models.TextField('SN号码详情', null=True, blank=True)
    state = models.IntegerField('申请状态', default=0, choices=((0, '申请中'), (1, '已审批通过'), (2, '审批不通过')))
    application_date = models.DateTimeField('申请时间', auto_now_add=True)
    approval_date = models.DateTimeField('审批时间', null=True, blank=True)
    upload_file = models.FileField('文件上传', upload_to=bs_upload_to, null=True, blank=True)
    is_download = models.IntegerField('下载状态', choices=((0, '未下载'), (1, '已下载')), default=0)

    device_type = models.ForeignKey('Device', verbose_name='设备型号')

    def colored_status(self):
        color = 'blue'
        if self.state == 0:
            color = 'red'
        if self.state == 1:
            color = 'green'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.get_state_display()
        )
    colored_status.short_description = u"申请状态"

    def __str__(self):
        return self.applicant

    class Meta:
        ordering = ["-applicant"]
        verbose_name = 'BS申请信息'
        verbose_name_plural = verbose_name


def upload_to(instance, filename):
    return '/'.join([settings.MEDIA_ROOT, 'CS', instance.device_name, filename])


class Device(models.Model):
    model_id = models.CharField('model_id', max_length=30, unique=True)
    device_name = models.CharField('设备类型名', max_length=20)
    del_tag = models.IntegerField('是否删除', default=0, choices=((0, '否'), (1, '是')))
    upload_file = models.FileField('文件上传', upload_to=upload_to, null=True, blank=True)

    def __str__(self):
        return self.device_name

    class Meta:
        unique_together = ('device_name', )
        verbose_name = '设备类型'
        verbose_name_plural = verbose_name


class InterfaceLogs(models.Model):
    status_code = models.IntegerField('状态码')
    status_msg = models.TextField('状态信息')
    model_id = models.CharField('model_id', max_length=30, null=True, blank=True)
    device_sn = models.CharField('设备SN', max_length=20, null=True, blank=True)
    create_time = models.IntegerField('创建时间', null=True, blank=True)
    secret_no = models.CharField(max_length=50, null=True, blank=True)
    device_id = models.BigIntegerField(null=True, blank=True)
    qr_code = models.CharField(max_length=200, null=True, blank=True)
    platform = models.IntegerField('接口平台', choices=((0, '企业微信'), (1, '服服')))
    deal_time = models.DateTimeField('处理时间', auto_now_add=True)

    class Meta:
        verbose_name = "接口日志"
        verbose_name_plural = verbose_name
        ordering = ["-deal_time"]
