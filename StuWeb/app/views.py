from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from app import models
from background_task import background
from django.utils import timezone
from .models import LibrarySeat, Reservation
# 打开系统首页
def toWelcomeView(request):
    return render(request, 'welcome.html')  # 渲染欢迎页面

# 座位选择页
def toPageSeatInfos(request):
    available_seats = models.LibrarySeat.objects.filter(is_available=True)
    return render(request, 'seats/data.html', {'seats': available_seats})

# 预约确认页
def toReservationConfirmView(request):
    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        user_id = request.POST.get('user_id')
        start_time_str = request.POST.get('start_time')

        start_time = timezone.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        start_time = timezone.make_aware(start_time)
        end_time = start_time + timezone.timedelta(hours=4)  # 最多 4 小时

        seat = models.LibrarySeat.objects.get(id=seat_id)
        seat.is_available = False
        seat.save()

        models.Reservation.objects.create(
            seat=seat,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('/reservations/history')

    seats = models.LibrarySeat.objects.filter(is_available=True)
    return render(request, 'reservations/confirm.html', {'seats': seats})

# 用户预约记录页
def toReservationHistoryView(request):
    user_id = request.GET.get('user_id')
    reservations = models.Reservation.objects.filter(user_id=user_id)
    return render(request, 'reservations/history.html', {'reservations': reservations})

# 扫码页面
def toScanQrCodeView(request):
    return render(request, 'scan_qr_code.html')

# 自动释放超时未使用座位的功能
@background(schedule=60)
def release_overdue_seats():
    now = timezone.now()
    overdue_reservations = Reservation.objects.filter(end_time__lt=now, is_used=False)
    for reservation in overdue_reservations:
        reservation.seat.is_available = True
        reservation.seat.save()
        reservation.delete()