import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, \
    QMessageBox, QLineEdit, QDateEdit, QTimeEdit
from PyQt5.QtCore import Qt, QDateTime
import django
from django.conf import settings
from django.utils import timezone

# 配置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StuWeb.settings')  # 根据你的项目名称调整
django.setup()

# 导入模型
from app.models import LibrarySeat, Reservation


class LibraryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('图书馆座位预约系统')
        self.setGeometry(100, 100, 800, 600)

        # 创建主布局
        main_layout = QVBoxLayout()

        # 座位选择部分
        seat_layout = QHBoxLayout()
        self.seat_combobox = QComboBox()
        self.refresh_seats()
        seat_layout.addWidget(QLabel('选择座位:'))
        seat_layout.addWidget(self.seat_combobox)
        main_layout.addLayout(seat_layout)

        # 用户ID输入部分
        user_id_layout = QHBoxLayout()
        self.user_id_input = QLineEdit()
        user_id_layout.addWidget(QLabel('用户 ID:'))
        user_id_layout.addWidget(self.user_id_input)
        main_layout.addLayout(user_id_layout)

        # 预约部分
        reservation_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDateTime(QDateTime.currentDateTime())
        reservation_layout.addWidget(QLabel('开始日期:'))
        reservation_layout.addWidget(self.start_date_edit)

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDateTime(QDateTime.currentDateTime())
        reservation_layout.addWidget(QLabel('开始时间:'))
        reservation_layout.addWidget(self.start_time_edit)

        self.duration_combobox = QComboBox()
        self.duration_combobox.addItems(['30分钟', '1小时', '2小时', '3小时', '4小时'])
        reservation_layout.addWidget(QLabel('预约时长:'))
        reservation_layout.addWidget(self.duration_combobox)

        reserve_button = QPushButton('确认预约')
        reserve_button.clicked.connect(self.make_reservation)
        reservation_layout.addWidget(reserve_button)

        main_layout.addLayout(reservation_layout)

        # 扫码部分
        scan_layout = QHBoxLayout()
        self.scan_input = QLineEdit()
        scan_layout.addWidget(QLabel('扫描二维码或输入座位 ID:'))
        scan_layout.addWidget(self.scan_input)
        scan_button = QPushButton('扫码确认')
        scan_button.clicked.connect(self.scan_qr_code)
        scan_layout.addWidget(scan_button)
        main_layout.addLayout(scan_layout)

        # 预约历史部分
        history_button = QPushButton('查看预约历史')
        history_button.clicked.connect(self.show_reservation_history)
        main_layout.addWidget(history_button)

        # 设置布局
        self.setLayout(main_layout)

    def refresh_seats(self):
        self.seat_combobox.clear()
        seats = LibrarySeat.objects.all()
        for seat in seats:
            status = "可用" if seat.is_available else "已预约"
            self.seat_combobox.addItem(f"{seat.seat_number} ({status})", seat.id)

    def make_reservation(self):
        # 检查用户ID是否为空
        user_id = self.user_id_input.text().strip()
        if not user_id:
            QMessageBox.warning(self, '错误', '请输入用户ID')
            return

        seat_id = self.seat_combobox.currentData()
        start_date = self.start_date_edit.date().toString('yyyy-MM-dd')
        start_time = self.start_time_edit.time().toString('HH:mm')
        start_time_str = f"{start_date}T{start_time}"
        duration_text = self.duration_combobox.currentText()

        # 转换预约时长为分钟
        duration_minutes = {
            '30分钟': 30,
            '1小时': 60,
            '2小时': 120,
            '3小时': 180,
            '4小时': 240
        }.get(duration_text, 60)

        # 验证时长不超过4小时
        if duration_minutes > 240:
            QMessageBox.warning(self, '错误', '预约时长不能超过4小时')
            return

        try:
            # 解析并转换为带时区的时间
            start_time = timezone.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            if not timezone.is_aware(start_time):
                start_time = timezone.make_aware(start_time)
        except ValueError:
            QMessageBox.warning(self, '错误', '请选择正确的日期和时间格式')
            return

        # 计算结束时间
        end_time = start_time + timezone.timedelta(minutes=duration_minutes)

        # 检查开始时间是否早于当前时间
        if start_time < timezone.now():
            QMessageBox.warning(self, '错误', '预约时间不能早于当前时间')
            return

        try:
            seat = LibrarySeat.objects.get(id=seat_id)
            if not seat.is_available:
                QMessageBox.warning(self, '错误', f'座位 {seat.seat_number} 已被预约')
                return

            # 创建预约
            Reservation.objects.create(
                seat=seat,
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                is_used=False
            )

            # 更新座位状态
            seat.is_available = False
            seat.save()

            QMessageBox.information(self, '成功', f'已成功预约座位 {seat.seat_number}')
            self.refresh_seats()

        except LibrarySeat.DoesNotExist:
            QMessageBox.warning(self, '错误', '未找到该座位')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'预约失败: {str(e)}')

    def scan_qr_code(self):
        seat_id = self.scan_input.text()
        if not seat_id:
            QMessageBox.warning(self, '错误', '请输入座位 ID 或扫描二维码')
            return

        try:
            seat = LibrarySeat.objects.get(id=seat_id)
            status = "可用" if seat.is_available else "已预约"
            QMessageBox.information(self, '座位状态', f'座位 {seat.seat_number} 当前状态: {status}')
        except LibrarySeat.DoesNotExist:
            QMessageBox.warning(self, '错误', '未找到该座位')

    def show_reservation_history(self):
        user_id = self.user_id_input.text().strip()
        if not user_id:
            QMessageBox.warning(self, '错误', '请输入用户 ID')
            return

        try:
            reservations = Reservation.objects.filter(user_id=user_id).order_by('-start_time')
            if not reservations.exists():
                QMessageBox.information(self, '预约历史', '未找到该用户的预约记录')
                return

            history_text = "您的预约历史:\n\n"
            for i, reservation in enumerate(reservations, 1):
                status = "已使用" if reservation.is_used else "未使用"
                if not reservation.is_used and reservation.end_time < timezone.now():
                    status = "已过期"

                history_text += (
                    f"{i}. 座位: {reservation.seat.seat_number}\n"
                    f"   开始时间: {reservation.start_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"   结束时间: {reservation.end_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"   状态: {status}\n\n"
                )

            QMessageBox.information(self, '预约历史', history_text)

        except Exception as e:
            QMessageBox.warning(self, '错误', f'查询失败: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    library_app = LibraryApp()
    library_app.show()
    sys.exit(app.exec_())