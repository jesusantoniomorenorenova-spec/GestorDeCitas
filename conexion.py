import mysql.connector
from mysql.connector import Error

class Conexion:
    def __init__(self):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "timecontrol"
        }
        self.conexion = None
        self.cursor = None

    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(**self.config)
            self.cursor = self.conexion.cursor(dictionary=True)
            print("Conexión exitosa a MySQL")
            return True
        except Error as e:
            print(f"ERROR de conexión: {e}")
            return False

    def ejecutar(self, sql, valores=None):
        if not self.cursor:
            print("ERROR: No hay cursor disponible")
            return None
        try:
            if valores:
                self.cursor.execute(sql, valores)
            else:
                self.cursor.execute(sql)
            return self.cursor
        except Error as e:
            print(f"ERROR en ejecución: {e}")
            return None

    def commit(self):
        if self.conexion:
            self.conexion.commit()

    def fetchall(self):
        if self.cursor:
            return self.cursor.fetchall()
        return None

    def fetchone(self):
        if self.cursor:
            return self.cursor.fetchone()
        return None

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
            print("Conexión cerrada")