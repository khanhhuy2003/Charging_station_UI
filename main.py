# main.py
import sys
from PyQt5 import QtWidgets
from controller.main_controller import MainController

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainController()
    window.show()
    sys.exit(app.exec_())