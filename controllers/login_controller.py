from PyQt6 import QtWidgets


class LoginController:
    def __init__(self, window, model):
        self.window = window
        self.model = model
        self.window.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.window.txt_username.text()
        password = self.window.txt_password.text()

        if username =="admin"and password == "123":
            self.window.login_successful.emit()
            print("login correcto")
        else:
            QtWidgets.QMessageBox.warning(
                self.window,
                "Abarrotes Tec - Error",
                "Login incorrecto"
            )
            print("login button clicked")
