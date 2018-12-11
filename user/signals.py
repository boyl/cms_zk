# coding=utf-8
from django.core.signals import request_started
from django.dispatch import receiver


@receiver(request_started)
def refresh_cookie(sender, **kwargs):
    print(sender, kwargs)
