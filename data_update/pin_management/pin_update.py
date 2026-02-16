# PinManager
#  ├── pin_data
#  ├── rut_pin_status
#  ├── update_all_pins()
#  ├── update_general_status()
#  ├── rut_pin()

# data_update/pin_manager.py
import random


class PinManager:
    def __init__(self):
        self.rut_pin_status = {1: False, 2: False, 3: False, 4: False, 5: False}

        self.pin_data = {
            1: {"percent": 92, "voltage": 51.8, "temp": 33.2, "status": "Đang sạc nhanh"},
            2: {"percent": 67, "voltage": 50.4, "temp": 35.1, "status": "Đang sạc"},
            3: {"percent": 45, "voltage": 49.1, "temp": 37.8, "status": "Ngừng sạc"},
            4: {"percent": 88, "voltage": 51.5, "temp": 32.4, "status": "Đang sạc"},
            5: {"percent": 23, "voltage": 48.3, "temp": 39.5, "status": "Cảnh báo thấp"},
        }

        self.status_options = [
            ("IDLE", "🤖💤"),
            ("WAITING", "🤖⌛"),
            ("BUSY", "🤖🔄"),
            ("DONE", "🤖🎉"),
        ]

    # -------- PIN UPDATE --------

    def update_all_pins(self):
        for pin in range(1, 6):
            if self.rut_pin_status[pin]:
                continue

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

    def rut_pin(self, pin_number):
        self.rut_pin_status[pin_number] = True
        self.pin_data[pin_number]["percent"] = 0
        self.pin_data[pin_number]["status"] = "Đã rút"

    # -------- GENERAL STATUS --------

    def get_general_status(self):
        return random.choice(self.status_options)

