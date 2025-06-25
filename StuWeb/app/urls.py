from django.urls import path
import app.views

urlpatterns = [
    path('', app.views.toWelcomeView),
    path('seats/page', app.views.toPageSeatInfos),
    path('reservations/confirm', app.views.toReservationConfirmView),
    path('reservations/history', app.views.toReservationHistoryView),
    path('scan/qr/code', app.views.toScanQrCodeView),
]