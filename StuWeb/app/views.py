import os
from app import models
from background_task import background
from django.utils import timezone
from .models import LibrarySeat, Reservation
from django.http import HttpResponseBadRequest
import qrcode
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse

# 打开系统首页
def toWelcomeView(request):
    user_id = request.GET.get('user_id')
    error = None
    reservations = []

    if user_id:
        try:
            reservations = Reservation.objects.filter(user_id=user_id).order_by('-start_time')
        except Exception as e:
            error = f"查询失败: {str(e)}"

    return render(request, 'welcome.html', {
        'user_id': user_id,
        'reservations': reservations,
        'error': error,
        'now': timezone.now()
    }) # 渲染欢迎页面

# 座位选择页
def toPageSeatInfos(request):
    # 先释放所有过期座位
    release_overdue_seats.now()  # 立即执行释放任务

    # 获取所有座位并按可用状态排序
    seats = LibrarySeat.objects.all().order_by('-is_available')

    available_count = seats.filter(is_available=True).count()
    reserved_count = seats.count() - available_count

    return render(request, 'seats/data.html', {
        'seats': seats,
        'available_count': available_count,
        'reserved_count': reserved_count
    })

#二维码生成视图
def generateQrCode(request):
    seat_id = request.GET.get('seat_id')
    if not seat_id:
        return HttpResponse("缺少座位ID", status=400)

    # 生成二维码内容（包含座位ID的URL）
    qr_data = f"http://127.0.0.1:8000/scan/qr/code?seat_id={seat_id}"

    # 创建二维码对象
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # 生成图像
    img = qr.make_image(fill_color="black", back_color="white")

    # 将图像保存到内存
    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)

    # 返回图像响应
    return HttpResponse(buffer, content_type="image/png")

#更新二维码生成视图
def toGenerateQrCodeView(request):
    seat_id = request.GET.get('seat_id')
    selected_seat = None

    if seat_id:
        try:
            selected_seat = LibrarySeat.objects.get(id=seat_id)
        except LibrarySeat.DoesNotExist:
            pass

    seats = LibrarySeat.objects.all()

    return render(request, 'qrcode/generate.html', {
        'seats': seats,
        'seat_id': seat_id,
        'selected_seat': selected_seat
    })

# 预约确认页
def toReservationConfirmView(request):
    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        user_id = request.POST.get('user_id')
        start_time_str = request.POST.get('start_time')
        duration_minutes = int(request.POST.get('duration', 60))  # 默认1小时

        # 验证时长不超过4小时
        if duration_minutes > 240:
            return render(request, 'reservations/confirm.html', {
                'error': '预约时长不能超过4小时',
                'seats': LibrarySeat.objects.filter(is_available=True)
            })

        try:
            start_time = timezone.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            start_time = timezone.make_aware(start_time)
        except ValueError:
            return render(request, 'reservations/confirm.html', {
                'error': '请选择正确的日期和时间格式',
                'seats': LibrarySeat.objects.filter(is_available=True)
            })

        # 根据用户选择的时长计算结束时间
        end_time = start_time + timezone.timedelta(minutes=duration_minutes)

        seat = LibrarySeat.objects.get(id=seat_id)
        seat.is_available = False
        seat.save()

        Reservation.objects.create(
            seat=seat,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('/reservations/history?user_id=' + user_id)

    seats = LibrarySeat.objects.filter(is_available=True)
    return render(request, 'reservations/confirm.html', {'seats': seats})


# 用户预约记录页
def toReservationHistoryView(request):
    user_id = request.GET.get('user_id')
    reservations = models.Reservation.objects.filter(user_id=user_id)
    return render(request, 'reservations/history.html', {'reservations': reservations})

# 扫码页面
def toScanQrCodeView(request):
    seat_id = request.GET.get('seat_id')
    error = None
    success = None
    seat = None

    if seat_id:
        try:
            seat = LibrarySeat.objects.get(id=seat_id)
        except LibrarySeat.DoesNotExist:
            error = "未找到该座位"
        else:
            success = f"已成功扫描座位: {seat.seat_number}"

    return render(request, 'scan/qr/code.html', {
        'seat_id': seat_id,
        'seat': seat,
        'error': error,
        'success': success
    })

#添加图片上传
def uploadSeatImage(request):
    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        image_file = request.FILES.get('image')

        if not seat_id or not image_file:
            return HttpResponse("缺少参数", status=400)

        try:
            seat = LibrarySeat.objects.get(id=seat_id)
        except LibrarySeat.DoesNotExist:
            return HttpResponse("座位不存在", status=404)

        # 保存图片到媒体目录
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'seats')
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名
        file_ext = os.path.splitext(image_file.name)[1]
        file_name = f"seat_{seat_id}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(upload_dir, file_name)

        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # 更新座位图片URL
        image_url = os.path.join(settings.MEDIA_URL, 'seats', file_name)
        seat.image_url = image_url
        seat.save()

        return redirect(f'/qrcode/generate?seat_id={seat_id}')

    return HttpResponse("方法不允许", status=405)

#取消预约视图
def cancelReservation(request):
    reservation_id = request.GET.get('id')

    if not reservation_id:
        return HttpResponseBadRequest("缺少预约ID")

    try:
        reservation = Reservation.objects.get(id=reservation_id)

        # 只能取消未使用且未过期的预约
        if not reservation.is_used and reservation.end_time > timezone.now():
            # 释放座位
            reservation.seat.is_available = True
            reservation.seat.save()

            # 删除预约记录
            reservation.delete()

            return redirect(f"/?user_id={reservation.user_id}&message=取消成功")
        else:
            return redirect(f"/?user_id={reservation.user_id}&error=无法取消已过期或已使用的预约")

    except Reservation.DoesNotExist:
        return HttpResponseBadRequest("预约记录不存在")

# 自动释放超时未使用座位的功能
@background(schedule=10)  # 每10秒执行一次（加快检查频率，方便调试）
def release_overdue_seats():
    now = timezone.localtime(timezone.now())  # 使用本地时间
    overdue_reservations = Reservation.objects.filter(
        end_time__lt=now,
        is_used=False
    )

    for reservation in overdue_reservations:
        # 释放座位
        seat = reservation.seat
        seat.is_available = True
        seat.save()

        # 删除过期预约
        reservation.delete()
        print(f"自动释放过期座位: {seat.seat_number}")  # 调试输出