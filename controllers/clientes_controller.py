from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conexion import Conexion

UI_DIR = Path(__file__).resolve().parents[1] / "ui"

class ClientesWindow(QMainWindow):
    def __init__(self, volver_callback):
        super().__init__()
        uic.loadUi(str(UI_DIR / "clientes.ui"), self)
        self.volver_callback = volver_callback

        self.db = Conexion()
        if not self.db.conectar():
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")

        self.btnAgregar.clicked.connect(self.insertar_cliente)
        self.btnEditar.clicked.connect(self.modificar_cliente)
        self.btnEliminar.clicked.connect(self.eliminar_cliente)
        self.btnLimpiar.clicked.connect(self.limpiar_campos)
        self.btnVolver.clicked.connect(self.volver)

        self.tblClientes.cellClicked.connect(self.seleccionar_fila)

        self.cargar_clientes()

    def cargar_clientes(self):
        resultado = self.db.ejecutar("SELECT id, nombre, telefono, correo FROM clientes")
        clientes = resultado.fetchall() if resultado else []

        self.tblClientes.setRowCount(len(clientes))
        self.tblClientes.setColumnCount(4)
        self.tblClientes.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Correo"])

        for i, cliente in enumerate(clientes):
            if isinstance(cliente, dict):
                self.tblClientes.setItem(i, 0, QTableWidgetItem(str(cliente.get('id', ''))))
                self.tblClientes.setItem(i, 1, QTableWidgetItem(str(cliente.get('nombre', ''))))
                self.tblClientes.setItem(i, 2, QTableWidgetItem(str(cliente.get('telefono', ''))))
                self.tblClientes.setItem(i, 3, QTableWidgetItem(str(cliente.get('correo', ''))))
            else:
                for j in range(4):
                    self.tblClientes.setItem(i, j, QTableWidgetItem(str(cliente[j])))

    def validar_datos(self, nombre, telefono, correo):
        """Valida los datos del cliente"""
        # Validar nombre
        if not nombre or len(nombre.strip()) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"

        # Validar teléfono - solo números, 10 dígitos
        telefono_limpio = telefono.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if telefono_limpio and (not telefono_limpio.isdigit() or len(telefono_limpio) != 10):
            return False, "El teléfono debe contener exactamente 10 números"

        # Validar email - debe tener @ y dominio
        if correo and "@" not in correo:
            return False, "El email debe incluir '@' y un dominio válido (ej: correo@dominio.com)"

        return True, ""

    def insertar_cliente(self):
        nombre = self.txtNombre.text().strip()
        telefono = self.txtTelefono.text().strip()
        correo = self.txtCorreo.text().strip()

        # Validar datos
        es_valido, mensaje_error = self.validar_datos(nombre, telefono, correo)
        if not es_valido:
            QMessageBox.warning(self, "Error de validación", mensaje_error)
            return

        sql = "INSERT INTO clientes (nombre, telefono, correo) VALUES (%s, %s, %s)"
        valores = (nombre, telefono, correo)

        try:
            self.db.ejecutar(sql, valores)
            self.db.commit()
            QMessageBox.information(self, "Éxito", "Cliente insertado correctamente")
            self.limpiar_campos()
            self.cargar_clientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo insertar: {e}")

    def modificar_cliente(self):
        fila = self.tblClientes.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente de la tabla")
            return

        id_cliente = self.tblClientes.item(fila, 0).text()
        nombre = self.txtNombre.text().strip()
        telefono = self.txtTelefono.text().strip()
        correo = self.txtCorreo.text().strip()

        # Validar datos
        es_valido, mensaje_error = self.validar_datos(nombre, telefono, correo)
        if not es_valido:
            QMessageBox.warning(self, "Error de validación", mensaje_error)
            return

        sql = "UPDATE clientes SET nombre = %s, telefono = %s, correo = %s WHERE id = %s"
        valores = (nombre, telefono, correo, id_cliente)

        try:
            filas = self.db.ejecutar_update(sql, valores)
            if filas > 0:
                QMessageBox.information(self, "Éxito", "Cliente modificado correctamente")
                self.limpiar_campos()
                self.cargar_clientes()
            else:
                QMessageBox.warning(self, "Error", "No se pudo modificar el cliente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo modificar: {e}")

    def eliminar_cliente(self):
        fila = self.tblClientes.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente de la tabla")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar", "¿Está seguro de eliminar este cliente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            id_cliente = self.tblClientes.item(fila, 0).text()
            sql = "DELETE FROM clientes WHERE id = %s"

            try:
                filas = self.db.ejecutar_update(sql, (id_cliente,))
                if filas > 0:
                    QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
                    self.limpiar_campos()
                    self.cargar_clientes()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el cliente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    def seleccionar_fila(self, fila):
        id_cliente = self.tblClientes.item(fila, 0).text()
        nombre = self.tblClientes.item(fila, 1).text()
        telefono = self.tblClientes.item(fila, 2).text()
        correo = self.tblClientes.item(fila, 3).text()

        self.txtNombre.setText(nombre)
        self.txtTelefono.setText(telefono)
        self.txtCorreo.setText(correo)

    def limpiar_campos(self):
        self.txtNombre.clear()
        self.txtTelefono.clear()
        self.txtCorreo.clear()

    def volver(self):
        self.db.cerrar()
        self.close()
        self.volver_callback()