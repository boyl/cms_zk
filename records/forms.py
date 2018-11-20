# coding=utf-8
from django import forms

from .models import Device


class CSForm(forms.Form):
    device_type = forms.ModelChoiceField(queryset=Device.objects.all(),
                                         empty_label='选择产品型号')
    device_no = forms.CharField()
    mobile_phone = forms.CharField()
    applicant = forms.CharField()

    device_type.widget.attrs.update({'class': 'sninput'})
    device_no.widget.attrs.update({'class': 'sninput1', 'placeholder': '输入SN码'})
    mobile_phone.widget.attrs.update({'class': 'sninput', 'placeholder': '请输入您的手机(选填)'})
    mobile_phone.widget.attrs.update({'class': 'sninput1', 'placeholder': '请输入您的姓名(选填)'})


