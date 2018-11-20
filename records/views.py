from django.http.response import JsonResponse, FileResponse
from django.utils.http import urlquote
from django.db.utils import IntegrityError

from records.models import BSInfo, Device, CSInfo
from pyexcel.exceptions import FileTypeNotSupported


# Create your views here.


def single_apply(request):
    if request.method == 'POST':
        device_sn = request.POST.get('device_sn', '')
        device_id = request.POST.get('device_id', '')
        if not (device_sn and device_id):
            return JsonResponse({"msg": "0"})  # '0': SN不能为空！
        device = Device.objects.get(id=device_id)
        if BSInfo.objects.filter(device_number=device_sn, device_type=device):
            return JsonResponse({"msg": "1"})  # '1': 已存在!
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        if name:
            BSInfo(applicant=name, contact=phone, device_type=device, device_number=device_sn).save()
        else:
            BSInfo(contact=phone, device_type=device, device_number=device_sn).save()
        return JsonResponse({"msg": "2"})  # 申请成功


def single_download(request):
    if request.method == 'POST':
        device_sn = request.POST.get('device_sn', '')
        device_id = request.POST.get('device_id', '')
        if not (device_sn and device_id):
            return JsonResponse({"msg": "0"})  # '0': SN不能为空！
        device = Device.objects.get(id=device_id)
        if CSInfo.objects.filter(device_number=device_sn, device_type=device):  # '1': 已存在, 直接下载
            return JsonResponse({"msg": "1", "file_path": device.upload_file.name})
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        if name:
            CSInfo(applicant=name, contact=phone, device_type=device, device_number=device_sn).save()
        else:
            CSInfo(contact=phone, device_type=device, device_number=device_sn).save()
        return JsonResponse({"msg": "1", "file_path": device.upload_file.name})  # 保存后，下载


def download_check(request):
    if request.method == 'POST':
        device_sn = request.POST.get('device_sn', '')
        device_id = request.POST.get('device_id', '')
        if not device_id:
            return JsonResponse({"msg": "0"})
        device = Device.objects.filter(id=device_id)
        app_info = BSInfo.objects.filter(device_number=device_sn, device_type=device)
        if not app_info:
            return JsonResponse({"msg": "1"})  # 未申请
        app = app_info[0]
        if app.state == 0:
            return JsonResponse({"msg": "2"})
        if app.state == 2:
            return JsonResponse({"msg": "3"})
        if app.state == 1:  # 审批通过
            if app.upload_file:  # 已上传升级包
                return JsonResponse({"msg": "5", 'file_path': app.upload_file.name, 'id': app.id})
            else:
                return JsonResponse({"msg": "4"})  # 未上传升级包


def download_file(request):
    file_path = request.GET.get('file_path', '')
    pk = request.GET.get('id', '')
    if pk:
        BSInfo.objects.filter(id=pk).update(is_download=1)
    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(urlquote(file_path.split('/')[-1]))
    return response


def batch_apply(request):
    file = request.FILES.get('f', '')
    name = request.POST.get('name', '')
    phone = request.POST.get('phone', '')
    data, _ = handle_file(file)
    if isinstance(data, dict):  # 错误信息字典
        return JsonResponse(data)
    str_data = str(dict(data))
    device_number = data[0][1]
    device_type = Device.objects.get(device_name=data[0][0])
    if BSInfo.objects.filter(device_number=device_number):
        return JsonResponse({"status": 4})
    if name:
        BSInfo(applicant=name, contact=phone, device_number=device_number,
               device_type=device_type, device_number_detail=str_data).save()
    else:
        BSInfo(contact=phone, device_number=device_number,
               device_type=device_type, device_number_detail=str_data).save()
    return JsonResponse({"status": 2})  # success


def batch_download(request):
    file = request.FILES.get('f', '')
    name = request.POST.get('name', '')
    phone = request.POST.get('phone', '')
    data, sn_list = handle_file(file)
    if isinstance(data, dict):  # 错误信息字典
        return JsonResponse(data)
    if len(set(sn_list)) != 1:  # 同一批量申请的设备型号要唯一
        return JsonResponse({"status": 2})
    apps_list = []
    device = Device.objects.get(device_name=data[0][0])
    for info in data:
        apps_list.append(CSInfo(applicant=name or '-', contact=phone, device_type=device, device_number=info[1]))
    try:
        CSInfo.objects.bulk_create(apps_list)
    except IntegrityError:
        return JsonResponse({"status": "5"})
    return JsonResponse({"status": "4", "file_path": device.upload_file.name})


def handle_file(file):
    if not file:
        return {"status": -1}, ''
    try:
        list_data = file.get_array()
    except FileTypeNotSupported:
        return {"status": 0}, ''
    if not list_data:
        return {"status": 0}, ''
    head_data = list_data[0]
    body_data = list_data[1:]
    if not body_data:
        return {"status": 3}, ''
    try:
        if head_data[0] != '产品型号' or head_data[1] != 'SN号码':
            return {"status": 0}, ''
    except IndexError:
        return {"status": 0}, ''
    sn_type_list = []
    for data in body_data:  # 只要有不符合要求的条目，就不做后续处理
        sn_type_list.append(data[0])
        if not all([data[0], data[1], Device.objects.filter(device_name=data[0])]):
            return {"status": 1}, ''  # sn, 产品型号不能为空, 且产品型号必须存在!
    return body_data, sn_type_list
