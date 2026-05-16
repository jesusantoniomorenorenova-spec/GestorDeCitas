from PyQt6 import QtWidgets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conexion import Conexion

class LoginController:
    def __init__(self, window, model):
        self.window = window
        self.model = model
        self.db = Conexion()

        if not self.db.conectar():
            QtWidgets.QMessageBox.critical(
                self.window,
                "Error de conexión",
                "No se pudo conectar a la base de datos. Verifique que MySQL esté corriendo."
            )

        self.window.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.window.txt_username.text().strip()
        password = self.window.txt_password.text().strip()

        if username == "" or password == "":
            QtWidgets.QMessageBox.warning(
                self.window,
                "Advertencia",
                "Ingrese usuario y contraseña"
            )
            return

        try:
            # Usar diccionario para obtener resultados con nombres de columnas
            sql = "SELECT usuario, password FROM usuarios WHERE usuario = %s"
            cursor = self.db.ejecutar(sql, (username,))

            if cursor is None:
                QtWidgets.QMessageBox.critical(
                    self.window,
                    "Error",
                    "Error al ejecutar la consulta"
                )
                return

            resultado = cursor.fetchone()

            if resultado:
                # Si usamos dictionary=True en el cursor
                if isinstance(resultado, dict):
                    usuario_db = resultado.get('usuario', '')
                    password_db = resultado.get('password', '')
                else:
                    # Si es tupla
                    usuario_db = resultado[0]
                    password_db = resultado[1]

                if password == password_db:
                    self.window.login_successful.emit()
                    print("Login correcto")
                else:
                    QtWidgets.QMessageBox.warning(
                        self.window,
                        "Error",
                        "Usuario o contraseña incorrectos"
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self.window,
                    "Error",
                    "Usuario o contraseña incorrectos"
                )

        except Exception as e:
            print(f"Error en login: {e}")
            QtWidgets.QMessageBox.critical(
                self.window,
                "Error",
                f"Error inesperado: {e}"
            )