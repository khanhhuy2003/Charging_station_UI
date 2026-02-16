# controller/main_controller.py
from PyQt5 import QtWidgets, QtCore
from view.ui_gen.main_ui import Ui_MainWindow
from view.ui_gen.pin_detail import Ui_Dialog_pin
from view.ui_gen.ui_setting import Ui_Dialog_setting
from model.pin_model import PinModel
import random
class MainController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = PinModel()

        self.setWindowTitle("Trạm Sạc Pin - VINMOTION")

        # Timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_all)
        self.timer.start(4000)

        # Kết nối sự kiện
        self.ui.button_setting.clicked.connect(self.open_setting_dialog)

        for i in range(1, 6):
            frame = getattr(self.ui, f"frame_pin_{i}")
            frame.mousePressEvent = lambda e, p=i: self.open_pin_detail(p)

            btn_name = f"replace_button_{i}" if i < 6 else "replace_button_5"  # theo tên mới của bạn
            btn = getattr(self.ui, btn_name)
            btn.clicked.connect(lambda _, p=i: self.replace_pin(p))

        # Update lần đầu
        self.update_all()
        self.update_replace_pin_buttons_visibility()

    def update_all(self):
        for pin in range(1, 6):
            self.model.update_pin(pin)
            self.update_pin_ui(pin)
        self.update_general_status()

    def update_pin_ui(self, pin):
        if self.model.replace_pin_status[pin]:
            return

        data = self.model.pin_data[pin]

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

    def update_general_status(self):
        status_text, icon = self.model.get_random_status_and_icon()
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

    def update_replace_pin_buttons_visibility(self):
        visible = (self.model.current_mode == "Manual")
        self.ui.replace_button_1.setVisible(visible)
        self.ui.replace_button_2.setVisible(visible)
        self.ui.replace_button_3.setVisible(visible)
        self.ui.replace_button_4.setVisible(visible)
        self.ui.replace_button_5.setVisible(visible)

    def update_pin_card_style(self, pin, is_rut=False):
        frame = getattr(self.ui, f"frame_pin_{pin}")
        progress = getattr(self.ui, f"progressBar_pin_{pin}_n")
        vol_label = getattr(self.ui, f"pin_{pin}_vol_value_n" if pin > 1 else "pin_1_vol_value_n")
        temp_label = getattr(self.ui, f"pin_{pin}_temp_value_n" if pin > 1 else "pin_1_temp_value_n")
        status_label = getattr(self.ui, f"pin_{pin}_status_value_n" if pin > 1 else "pin_1_status_value_n")

        if is_rut:
            frame.setStyleSheet(frame.styleSheet() + "; background-color: #E0E0E0;")
            progress.setStyleSheet("""
                QProgressBar { background-color: #F0F0F0; border: none; color: transparent; }
                QProgressBar::chunk { background-color: #B0B0B0; }
            """)
            progress.setValue(0)
            label_style = "color: #757575; border: none;"
            vol_label.setText("N/A"); vol_label.setStyleSheet(label_style)
            temp_label.setText("N/A"); temp_label.setStyleSheet(label_style)
            status_label.setText("N/A"); status_label.setStyleSheet(label_style)
        else:
            original = frame.styleSheet().replace("background-color: #E0E0E0;", "")
            frame.setStyleSheet(original)
            progress.setStyleSheet("")
            label_style = "color: black; border: none;"
            vol_label.setStyleSheet(label_style)
            temp_label.setStyleSheet(label_style)
            status_label.setStyleSheet(label_style)

    def open_pin_detail(self, pin_number):
        dialog = QtWidgets.QDialog(self)
        ui_dialog = Ui_Dialog_pin()
        ui_dialog.setupUi(dialog)

        ui_dialog.label.setText(f"PIN {pin_number} - Thông số chi tiết")

        data = self.model.pin_data[pin_number]
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
        dialog = QtWidgets.QDialog(self)
        ui_setting = Ui_Dialog_setting()
        ui_setting.setupUi(dialog)

        if self.model.current_mode == "Auto":
            ui_setting.checkBox.setChecked(True)
            ui_setting.checkBox_2.setChecked(False)
        else:
            ui_setting.checkBox.setChecked(False)
            ui_setting.checkBox_2.setChecked(True)

        def save_settings():
            if ui_setting.checkBox.isChecked():
                self.model.current_mode = "Auto"
            elif ui_setting.checkBox_2.isChecked():
                self.model.current_mode = "Manual"

            self.ui.mode_value.setText(self.model.current_mode)
            self.update_replace_pin_buttons_visibility()

            ssid = ui_setting.lineEdit.text().strip()
            password = ui_setting.lineEdit_2.text().strip()
            if ssid:
                print(f"Đã lưu WiFi: SSID = {ssid}, Password = {password}")

            QtWidgets.QMessageBox.information(dialog, "Thành công", "Đã lưu cài đặt!")
            dialog.accept()

        ui_setting.pushButton.clicked.connect(save_settings)
        dialog.exec_()

    def replace_pin(self, pin_number):
        reply = QtWidgets.QMessageBox.question(
            self, "Xác nhận rút pin",
            f"Bạn có chắc chắn muốn rút Pin {pin_number} không?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.model.replace_pin(pin_number)
            self.update_pin_ui(pin_number)
            self.update_pin_card_style(pin_number, is_rut=True)
            QtWidgets.QMessageBox.information(self, "Thành công", f"Pin {pin_number} đã được rút!")
        else:
            QtWidgets.QMessageBox.information(self, "Hủy", "Hủy rút pin.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainController()
    window.show()
    sys.exit(app.exec_())