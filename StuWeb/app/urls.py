from django.urls import path
import app.views

urlpatterns = [
    path('', app.views.toWelcomeView),
    path('seats/page', app.views.toPageSeatInfos),
    path('reservations/confirm', app.views.toReservationConfirmView),
    # path('reservations/history', app.views.toReservationHistoryView),
    path('reservations/cancel', app.views.cancelReservation),
    path('scan/qr/code', app.views.toScanQrCodeView),
    path('qrcode/generate', app.views.toGenerateQrCodeView),  # 二维码生成页面
    path('qrcode/image', app.views.generateQrCode),
    path('qrcode/upload_image', app.views.uploadSeatImage),  # 新增图片上传路径
]