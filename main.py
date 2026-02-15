# -*- coding: utf-8 -*-
import sys
import random
from PyQt5 import QtWidgets, QtCore
from main_ui import Ui_MainWindow               # Màn hình chính
from pin_detail import Ui_Dialog_pin            # Dialog chi tiết pin
from ui_setting import Ui_Dialog_setting        # Dialog Setting

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Trạm Sạc Pin - VINMOTION")

        # Biến lưu chế độ hoạt động
        self.current_mode = "Auto"
        self.ui.mode_value.setText(self.current_mode)

        # Theo dõi pin đã rút
        self.rut_pin_status = {1: False, 2: False, 3: False, 4: False, 5: False}

        # Dữ liệu mô phỏng 5 pin
        self.pin_data = {
            1: {"percent": 92, "voltage": 51.8, "temp": 33.2, "status": "Đang sạc nhanh"},
            2: {"percent": 67, "voltage": 50.4, "temp": 35.1, "status": "Đang sạc"},
            3: {"percent": 45, "voltage": 49.1, "temp": 37.8, "status": "Ngừng sạc"},
            4: {"percent": 88, "voltage": 51.5, "temp": 32.4, "status": "Đang sạc"},
            5: {"percent": 23, "voltage": 48.3, "temp": 39.5, "status": "Cảnh báo thấp"}
        }

        # Trạng thái tổng + icon robot
        self.status_options = [
            ("IDLE", "🤖💤"),
            ("WAITING", "🤖⌛"),
            ("BUSY", "🤖🔄"),
            ("DONE", "🤖🎉")
        ]

        # Timer update pin mỗi 4 giây
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_all_pins)
        self.timer.start(4000)

        # Kết nối sự kiện
        self.ui.button_setting.clicked.connect(self.open_setting_dialog)

        self.ui.frame_pin_1.mousePressEvent = lambda e: self.open_pin_detail(1)
        self.ui.frame_pin_2.mousePressEvent = lambda e: self.open_pin_detail(2)
        self.ui.frame_pin_3.mousePressEvent = lambda e: self.open_pin_detail(3)
        self.ui.frame_pin_4.mousePressEvent = lambda e: self.open_pin_detail(4)
        self.ui.frame_pin_5.mousePressEvent = lambda e: self.open_pin_detail(5)

        self.ui.pushButton.clicked.connect(lambda: self.rut_pin(1))
        self.ui.pushButton_2.clicked.connect(lambda: self.rut_pin(2))
        self.ui.pushButton_3.clicked.connect(lambda: self.rut_pin(3))
        self.ui.pushButton_4.clicked.connect(lambda: self.rut_pin(4))
        self.ui.pushButton_6.clicked.connect(lambda: self.rut_pin(5))

        # Update lần đầu
        self.update_all_pins()
        self.update_general_status()
        self.update_rut_pin_buttons_visibility()

    def update_rut_pin_buttons_visibility(self):
        """Ẩn/hiện nút rút pin theo mode"""
        visible = (self.current_mode == "Manual")
        self.ui.pushButton.setVisible(visible)
        self.ui.pushButton_2.setVisible(visible)
        self.ui.pushButton_3.setVisible(visible)
        self.ui.pushButton_4.setVisible(visible)
        self.ui.pushButton_6.setVisible(visible)

    def update_pin_card_style(self, pin, is_rut=False):
        """Chỉ đổi màu nền xám cho card pin khi rút, giữ nguyên viền/bo góc"""
        frame = getattr(self.ui, f"frame_pin_{pin}")
        progress = getattr(self.ui, f"progressBar_pin_{pin}_n")
        vol_label = getattr(self.ui, f"pin_{pin}_vol_value_n" if pin > 1 else "pin_1_vol_value_n")
        temp_label = getattr(self.ui, f"pin_{pin}_temp_value_n" if pin > 1 else "pin_1_temp_value_n")
        status_label = getattr(self.ui, f"pin_{pin}_status_value_n" if pin > 1 else "pin_1_status_value_n")

        if is_rut:
            # Nền xám, giữ nguyên viền/bo góc
            frame.setStyleSheet(frame.styleSheet() + "; background-color: #E0E0E0;")

            # Progress bar xám
            progress.setStyleSheet("""
                QProgressBar {
                    background-color: #F0F0F0;
                    border: none;
                    text-align: center;
                    color: transparent;
                }
                QProgressBar::chunk {
                    background-color: #B0B0B0;
                }
            """)
            progress.setValue(0)

            # Text N/A + xám
            label_style = "color: #757575; border: none;"
            vol_label.setText("N/A")
            vol_label.setStyleSheet(label_style)
            temp_label.setText("N/A")
            temp_label.setStyleSheet(label_style)
            status_label.setText("N/A")
            status_label.setStyleSheet(label_style)
        else:
            # Reset nền (giữ nguyên viền/bo góc)
            original_style = frame.styleSheet().replace("background-color: #E0E0E0;", "")
            frame.setStyleSheet(original_style)
            progress.setStyleSheet("")
            label_style = "color: black; border: none;"
            vol_label.setStyleSheet(label_style)
            temp_label.setStyleSheet(label_style)
            status_label.setStyleSheet(label_style)

    def update_all_pins(self):
        for pin in range(1, 6):
            if self.rut_pin_status[pin]:
                continue  # Pin đã rút → không update

            data = self.pin_data[pin]
            data["percent"] = max(0, min(100, data["percent"] + random.randint(-5, 5)))
            data["voltage"] = round(random.uniform(47.0, 52.0), 1)
            data["temp"] = round(random.uniform(30.0, 43.0), 1)

            if data["percent"] >= 80:
                data["status"] = "Đang sạc nhanh"
            elif data["percent"] >= 40:
                data["status"] = "Đang sạc"
            elif data["percent"] >= 20:
                data["status"] = "Sạc chậm"
            else:
                data["status"] = "Pin yếu"

            self.update_pin_ui(pin, data)

    def update_pin_ui(self, pin, data):
        if self.rut_pin_status[pin]:
            return

        progress = getattr(self.ui, f"progressBar_pin_{pin}_n")
        vol_label = getattr(self.ui, f"pin_{pin}_vol_value_n" if pin > 1 else "pin_1_vol_value_n")
        temp_label = getattr(self.ui, f"pin_{pin}_temp_value_n" if pin > 1 else "pin_1_temp_value_n")
        status_label = getattr(self.ui, f"pin_{pin}_status_value_n" if pin > 1 else "pin_1_status_value_n")

        progress.setValue(data["percent"])

        if data["percent"] >= 80:
            color = "#4CAF50"
        elif data["percent"] >= 40:
            color = "#FF9800"
        else:
            color = "#F44336"

        progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 12px; }}")

        vol_label.setText(str(data["voltage"]))
        temp_label.setText(str(data["temp"]))
        status_label.setText(data["status"])

        self.update_pin_card_style(pin, is_rut=False)

    def update_general_status(self):
        status_text, icon = random.choice(self.status_options)
        self.ui.status_value.setText(status_text)
        self.ui.general_status_icon.setText(icon)

        if status_text in ["IDLE", "DONE"]:
            color = "#4CAF50"
        elif status_text == "WAITING":
            color = "#FF9800"
        elif status_text == "BUSY":
            color = "#F44336"
        else:
            color = "#455A64"

        self.ui.status_value.setStyleSheet(f"border: none; border-radius: 0px; color: {color};")

    def open_pin_detail(self, pin_number):
        dialog = QtWidgets.QDialog(self)
        ui_dialog = Ui_Dialog_pin()
        ui_dialog.setupUi(dialog)

        ui_dialog.label.setText(f"PIN {pin_number} - Thông số chi tiết")

        data = self.pin_data[pin_number]
        table = ui_dialog.tableWidget
        table.setRowCount(0)
        table.setRowCount(19)

        table.setItem(0, 0, QtWidgets.QTableWidgetItem("SOC"))
        table.setItem(0, 1, QtWidgets.QTableWidgetItem(f"{data['percent']} %"))

        table.setItem(1, 0, QtWidgets.QTableWidgetItem("SOH"))
        table.setItem(1, 1, QtWidgets.QTableWidgetItem("98 %"))

        table.setItem(2, 0, QtWidgets.QTableWidgetItem("Current (mA)"))
        table.setItem(2, 1, QtWidgets.QTableWidgetItem("12400"))

        table.setItem(3, 0, QtWidgets.QTableWidgetItem("Pack Voltage (V)"))
        table.setItem(3, 1, QtWidgets.QTableWidgetItem(str(data["voltage"])))

        table.setItem(4, 0, QtWidgets.QTableWidgetItem("Nhiệt độ"))
        table.setItem(4, 1, QtWidgets.QTableWidgetItem(f"{data['temp']} °C"))

        table.setItem(5, 0, QtWidgets.QTableWidgetItem("Trạng thái"))
        table.setItem(5, 1, QtWidgets.QTableWidgetItem(data["status"]))

        for i in range(1, 14):
            row = 5 + i
            cell_name = f"Cell {i} Voltage"
            cell_value = round(random.uniform(3.6, 4.2), 3)
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(cell_name))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{cell_value} V"))

        table.resizeColumnsToContents()

        ui_dialog.close_button_pin_dialog_1.clicked.connect(dialog.close)
        dialog.exec_()

    def open_setting_dialog(self):
        """Mở cửa sổ Setting và xử lý lưu cài đặt"""
        dialog = QtWidgets.QDialog(self)
        ui_setting = Ui_Dialog_setting()
        ui_setting.setupUi(dialog)

        if self.current_mode == "Auto":
            ui_setting.checkBox.setChecked(True)
            ui_setting.checkBox_2.setChecked(False)
        else:
            ui_setting.checkBox.setChecked(False)
            ui_setting.checkBox_2.setChecked(True)

        def save_settings():
            if ui_setting.checkBox.isChecked():
                self.current_mode = "Auto"
            elif ui_setting.checkBox_2.isChecked():
                self.current_mode = "Manual"

            self.ui.mode_value.setText(self.current_mode)
            self.update_rut_pin_buttons_visibility()

            ssid = ui_setting.lineEdit.text().strip()
            password = ui_setting.lineEdit_2.text().strip()
            if ssid:
                print(f"Đã lưu WiFi: SSID = {ssid}, Password = {password}")

            QtWidgets.QMessageBox.information(dialog, "Thành công", "Đã lưu cài đặt!")
            dialog.accept()

        ui_setting.pushButton.clicked.connect(save_settings)
        dialog.exec_()

    def rut_pin(self, pin_number):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Xác nhận rút pin",
            f"Bạn có chắc chắn muốn rút Pin {pin_number} không?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.pin_data[pin_number]["percent"] = 0
            self.pin_data[pin_number]["status"] = "Đã rút"
            self.rut_pin_status[pin_number] = True
            self.update_pin_ui(pin_number, self.pin_data[pin_number])
            self.update_pin_card_style(pin_number, is_rut=True)
            QtWidgets.QMessageBox.information(self, "Thành công", f"Pin {pin_number} đã được rút thành công!")
        else:
            QtWidgets.QMessageBox.information(self, "Hủy", "Hủy rút pin.")

    def update_general_status(self):
        status_text, icon = random.choice(self.status_options)
        self.ui.status_value.setText(status_text)
        self.ui.general_status_icon.setText(icon)

        if status_text in ["IDLE", "DONE"]:
            color = "#4CAF50"
        elif status_text == "WAITING":
            color = "#FF9800"
        elif status_text == "BUSY":
            color = "#F44336"
        else:
            color = "#455A64"

        self.ui.status_value.setStyleSheet(f"border: none; border-radius: 0px; color: {color};")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())