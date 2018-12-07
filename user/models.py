from django.db import models

# Create your models here.


class UserProfile(models.Model):
    nickname = models.CharField('昵称', max_length=32)
    sex = models.SmallIntegerField('性别', choices=((1, '男'), (2, '女')))
    province = models.CharField('省份', max_length=16)
    city = models.CharField('城市', max_length=16)
    country = models.CharField('国家', max_length=8)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name


class OAuth(models.Model):  # 其他第三方认证可在此扩展
    user = models.ForeignKey(UserProfile)

    oauth_type = models.CharField('认证类型', max_length=8, default='wechat')
    oauth_id = models.CharField('openid', max_length=28)
    oauth_union_id = models.CharField('union_id', max_length=29)
    access_token = models.CharField(max_length=512)
    expires_in = models.IntegerField(default=0)
    random_str = models.CharField(max_length=8, null=True, blank=True)
    md5 = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return "{0}:{1}".format(self.user_id, self.oauth_type)

    class Meta:
        verbose_name = '认证信息'
        verbose_name_plural = verbose_name
