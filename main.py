import sys
from PyQt6.QtWidgets import QApplication
from controllers.dashboard_controller import DashboardWindow

from PyQt6 import QtWidgets , uic
from controllers.login_controller import LoginController
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic


#pip install pyqt6-tools

class Login(QtWidgets.QDialog):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/login.ui", self)
        self.controller = LoginController(self,self)
        self.apply_theme()

    def apply_theme(self):
        is_dark = self.palette().color(QPalette.ColorRole.Window).lightness() <128
        print(f"  dark: {is_dark}")

class Sells(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/dashboard.ui", self)


class AppManager:
    def __init__(self):
        self.login_window=Login()
        self.sell_window = None
        self.sell_window = Sells()
        self.login_window.login_successful.connect(self.show_main_window)

        self.login_window.show()
    def show_main_window(self):
        self.sell_window.show()#mostrar ventana de muestra
        self.login_window.close()#ceramos ventana

app = QtWidgets.QApplication(sys.argv)
manager = AppManager()
sys.exit(app.exec())


def main():
    app = QApplication(sys.argv)
    w = DashboardWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()







