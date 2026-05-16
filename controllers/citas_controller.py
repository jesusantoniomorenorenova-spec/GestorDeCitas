from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conexion import Conexion

UI_DIR = Path(__file__).resolve().parents[1] / "ui"

class CitasWindow(QMainWindow):
    def __init__(self, volver_callback):
        super().__init__()
        uic.loadUi(str(UI_DIR / "citas.ui"), self)
        self.volver_callback = volver_callback

        self.db = Conexion()
        if not self.db.conectar():
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")

        self.btnAgregar.clicked.connect(self.insertar_cita)
        self.btnEditar.clicked.connect(self.modificar_cita)
        self.btnEliminar.clicked.connect(self.eliminar_cita)
        self.btnEliminar_2.clicked.connect(self.limpiar_campos)
        self.btnVolver.clicked.connect(self.volver)

        self.tblCitas.cellClicked.connect(self.seleccionar_fila)

        self.cargar_clientes()
        self.cargar_servicios()
        self.cargar_estados()
        self.cargar_citas()

    def cargar_clientes(self):
        resultado = self.db.ejecutar("SELECT id, nombre FROM clientes")
        clientes = resultado.fetchall() if resultado else []
        self.cmbCliente.clear()
        if clientes:
            for cliente in clientes:
                if isinstance(cliente, dict):
                    self.cmbCliente.addItem(cliente.get('nombre', ''), cliente.get('id'))
                else:
                    self.cmbCliente.addItem(cliente[1], cliente[0])

    def cargar_servicios(self):
        servicios = ["Corte de cabello", "Corte y barba", "Manicure", "Pedicure", "Tratamiento facial", "Coloración"]
        self.cmbServicio.clear()
        self.cmbServicio.addItems(servicios)

    def cargar_estados(self):
        estados = ["Pendiente", "Confirmada", "Cancelada", "Completada"]
        self.cmbEstado.clear()
        self.cmbEstado.addItems(estados)

    def cargar_citas(self):
        # Usar nombre de respaldo si el cliente ya no existe
        sql = """
        SELECT c.id, COALESCE(cl.nombre, c.nombre_cliente_backup) as cliente,
               c.servicio, c.fecha, c.hora, c.estado, c.notas
        FROM citas c
        LEFT JOIN clientes cl ON c.id_cliente = cl.id
        ORDER BY c.fecha DESC
        """
        
        resultado = self.db.ejecutar(sql)
        citas = resultado.fetchall() if resultado else []

        self.tblCitas.setRowCount(len(citas))
        self.tblCitas.setColumnCount(7)
        self.tblCitas.setHorizontalHeaderLabels(["ID", "Cliente", "Servicio", "Fecha", "Hora", "Estado", "Notas"])

        for i, cita in enumerate(citas):
            if isinstance(cita, dict):
                self.tblCitas.setItem(i, 0, QTableWidgetItem(str(cita.get('id', ''))))
                self.tblCitas.setItem(i, 1, QTableWidgetItem(str(cita.get('cliente', ''))))
                self.tblCitas.setItem(i, 2, QTableWidgetItem(str(cita.get('servicio', ''))))
                self.tblCitas.setItem(i, 3, QTableWidgetItem(str(cita.get('fecha', ''))))
                self.tblCitas.setItem(i, 4, QTableWidgetItem(str(cita.get('hora', ''))))
                self.tblCitas.setItem(i, 5, QTableWidgetItem(str(cita.get('estado', ''))))
                self.tblCitas.setItem(i, 6, QTableWidgetItem(str(cita.get('notas', ''))))
            else:
                for j in range(7):
                    self.tblCitas.setItem(i, j, QTableWidgetItem(str(cita[j]) if cita[j] else ""))

    def obtener_nombre_cliente(self, id_cliente):
        resultado = self.db.ejecutar("SELECT nombre FROM clientes WHERE id = %s", (id_cliente,))
        cliente = resultado.fetchone() if resultado else None
        if cliente:
            if isinstance(cliente, dict):
                return cliente.get('nombre', '')
            else:
                return cliente[0]
        return ''

    def insertar_cita(self):
        if self.cmbCliente.currentIndex() < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente")
            return

        id_cliente = self.cmbCliente.currentData()
        nombre_cliente = self.obtener_nombre_cliente(id_cliente)
        servicio = self.cmbServicio.currentText()
        fecha = self.dateFecha.date().toString("yyyy-MM-dd")
        hora = self.timeHora.time().toString("HH:mm:ss")
        estado = self.cmbEstado.currentText()
        notas = self.txtNotas.toPlainText().strip()

        sql = "INSERT INTO citas (id_cliente, nombre_cliente_backup, servicio, fecha, hora, estado, notas) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        valores = (id_cliente, nombre_cliente, servicio, fecha, hora, estado, notas)

        try:
            self.db.ejecutar(sql, valores)
            self.db.commit()
            QMessageBox.information(self, "Éxito", "Cita insertada correctamente")
            self.limpiar_campos()
            self.cargar_citas()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo insertar: {e}")

    def modificar_cita(self):
        fila = self.tblCitas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una cita de la tabla")
            return

        id_cita = self.tblCitas.item(fila, 0).text()

        if self.cmbCliente.currentIndex() < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente")
            return

        id_cliente = self.cmbCliente.currentData()
        nombre_cliente = self.obtener_nombre_cliente(id_cliente)
        servicio = self.cmbServicio.currentText()
        fecha = self.dateFecha.date().toString("yyyy-MM-dd")
        hora = self.timeHora.time().toString("HH:mm:ss")
        estado = self.cmbEstado.currentText()
        notas = self.txtNotas.toPlainText().strip()

        sql = "UPDATE citas SET id_cliente = %s, nombre_cliente_backup = %s, servicio = %s, fecha = %s, hora = %s, estado = %s, notas = %s WHERE id = %s"
        valores = (id_cliente, nombre_cliente, servicio, fecha, hora, estado, notas, id_cita)

        try:
            filas = self.db.ejecutar_update(sql, valores)
            if filas > 0:
                QMessageBox.information(self, "Éxito", "Cita modificada correctamente")
                self.limpiar_campos()
                self.cargar_citas()
            else:
                QMessageBox.warning(self, "Error", "No se pudo modificar la cita")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo modificar: {e}")

    def eliminar_cita(self):
        fila = self.tblCitas.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una cita de la tabla")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar", "¿Está seguro de eliminar esta cita?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            id_cita = self.tblCitas.item(fila, 0).text()
            sql = "DELETE FROM citas WHERE id = %s"

            try:
                filas = self.db.ejecutar_update(sql, (id_cita,))
                if filas > 0:
                    QMessageBox.information(self, "Éxito", "Cita eliminada correctamente")
                    self.limpiar_campos()
                    self.cargar_citas()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar la cita")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    def seleccionar_fila(self, fila):
        id_cita = self.tblCitas.item(fila, 0).text()

        sql = "SELECT id_cliente FROM citas WHERE id = %s"
        resultado = self.db.ejecutar(sql, (id_cita,))
        cita_data = resultado.fetchone() if resultado else None

        if cita_data:
            if isinstance(cita_data, dict):
                id_cliente_actual = cita_data.get('id_cliente')
            else:
                id_cliente_actual = cita_data[0]

            if id_cliente_actual:
                index = self.cmbCliente.findData(id_cliente_actual)
                if index >= 0:
                    self.cmbCliente.setCurrentIndex(index)

        servicio = self.tblCitas.item(fila, 2).text()
        fecha = self.tblCitas.item(fila, 3).text()
        hora = self.tblCitas.item(fila, 4).text()
        estado = self.tblCitas.item(fila, 5).text()
        notas = self.tblCitas.item(fila, 6).text()

        index = self.cmbServicio.findText(servicio)
        if index >= 0:
            self.cmbServicio.setCurrentIndex(index)

        if fecha:
            fecha_parts = fecha.split("-")
            if len(fecha_parts) == 3:
                from PyQt6.QtCore import QDate
                self.dateFecha.setDate(QDate(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])))

        if hora:
            hora_parts = hora.split(":")
            if len(hora_parts) >= 2:
                from PyQt6.QtCore import QTime
                self.timeHora.setTime(QTime(int(hora_parts[0]), int(hora_parts[1])))

        index = self.cmbEstado.findText(estado)
        if index >= 0:
            self.cmbEstado.setCurrentIndex(index)

        self.txtNotas.setPlainText(notas)

    def limpiar_campos(self):
        if self.cmbCliente.count() > 0:
            self.cmbCliente.setCurrentIndex(0)
        self.cmbServicio.setCurrentIndex(0)
        self.cmbEstado.setCurrentIndex(0)
        self.txtNotas.clear()

    def volver(self):
        self.db.cerrar()
        self.close()
        self.volver_callback()