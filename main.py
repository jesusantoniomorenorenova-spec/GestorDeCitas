import sys
from pathlib import Path
from PyQt6 import QtWidgets , uic
from PyQt6.QtCore import pyqtSignal
from controllers.login_controller import LoginController
from controllers.dashboard_controller import DashboardWindow
from PyQt6.QtWidgets import QApplication
from PyQt6 import uic


BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"


#pip install pyqt6-tools

class Login(QtWidgets.QDialog):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_DIR / "login.ui"),self)
        self.controller = LoginController(self,self)

class AppManager:
    def __init__(self):
        self.login_window=Login()
        self.main_Window = DashboardWindow()
        self.login_window.login_successful.connect(self.show_main_window)

        self.login_window.show()

    def show_main_window(self):
        self.main_Window.show()#mostrar ventana de muestra
        self.login_window.close()#ceramos ventana



def main():
    app = QApplication(sys.argv)

    manager = AppManager()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()



#jesus antonio moreno



