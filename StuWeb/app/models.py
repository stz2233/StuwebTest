from django.db import models
from django.utils import timezone

# 图书馆座位信息
class LibrarySeat(models.Model):
    seat_number = models.CharField('座位编号', max_length=20, null=False)
    is_available = models.BooleanField('是否可用', default=True)

    class Meta:
        db_table = 'library_seats'

# 预约信息
class Reservation(models.Model):
    seat = models.ForeignKey(LibrarySeat, db_column='seat_id', null=False, on_delete=models.CASCADE)
    user_id = models.CharField('用户 ID', max_length=50, null=False)
    start_time = models.DateTimeField('开始时间', null=False)
    end_time = models.DateTimeField('结束时间', null=False)
    is_used = models.BooleanField('是否使用', default=False)

    class Meta:
        db_table = 'reservations'
