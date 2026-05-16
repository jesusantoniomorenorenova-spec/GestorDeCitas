from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conexion import Conexion

UI_DIR = Path(__file__).resolve().parents[1] / "ui"

class ReporteWindow(QMainWindow):
    def __init__(self, volver_callback):
        super().__init__()
        uic.loadUi(str(UI_DIR / "reporte.ui"), self)
        self.volver_callback = volver_callback

        self.db = Conexion()
        if not self.db.conectar():
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")

        self.cargar_estados()
        self.btnImprimir.clicked.connect(self.exportar_pdf)
        self.btnVolver.clicked.connect(self.volver)

        self.cargar_todas_citas()

    def cargar_estados(self):
        estados = ["Todos", "Pendiente", "Confirmada", "Cancelada", "Completada"]
        self.cmbEstadoFiltro.clear()
        self.cmbEstadoFiltro.addItems(estados)

    def cargar_todas_citas(self):
        sql = """
        SELECT c.id, COALESCE(cl.nombre, c.nombre_cliente_backup) as cliente,
               c.servicio, c.fecha, c.hora, c.estado, c.notas
        FROM citas c
        LEFT JOIN clientes cl ON c.id_cliente = cl.id
        ORDER BY c.fecha DESC
        """
        
        resultado = self.db.ejecutar(sql)
        citas = resultado.fetchall() if resultado else []
        self.mostrar_en_tabla(citas)

    def filtrar_citas(self):
        estado_filtro = self.cmbEstadoFiltro.currentText()

        if estado_filtro == "Todos":
            self.cargar_todas_citas()
        else:
            sql = """
            SELECT c.id, COALESCE(cl.nombre, c.nombre_cliente_backup) as cliente,
                   c.servicio, c.fecha, c.hora, c.estado, c.notas
            FROM citas c
            LEFT JOIN clientes cl ON c.id_cliente = cl.id
            WHERE c.estado = %s
            ORDER BY c.fecha DESC
            """
            resultado = self.db.ejecutar(sql, (estado_filtro,))
            citas = resultado.fetchall() if resultado else []
            self.mostrar_en_tabla(citas)

    def mostrar_en_tabla(self, citas):
        self.tblReporte.setRowCount(len(citas))
        self.tblReporte.setColumnCount(7)
        self.tblReporte.setHorizontalHeaderLabels(["ID", "Cliente", "Servicio", "Fecha", "Hora", "Estado", "Notas"])

        for i, cita in enumerate(citas):
            if isinstance(cita, dict):
                self.tblReporte.setItem(i, 0, QTableWidgetItem(str(cita.get('id', ''))))
                self.tblReporte.setItem(i, 1, QTableWidgetItem(str(cita.get('cliente', ''))))
                self.tblReporte.setItem(i, 2, QTableWidgetItem(str(cita.get('servicio', ''))))
                self.tblReporte.setItem(i, 3, QTableWidgetItem(str(cita.get('fecha', ''))))
                self.tblReporte.setItem(i, 4, QTableWidgetItem(str(cita.get('hora', ''))))
                self.tblReporte.setItem(i, 5, QTableWidgetItem(str(cita.get('estado', ''))))
                self.tblReporte.setItem(i, 6, QTableWidgetItem(str(cita.get('notas', ''))))
            else:
                for j in range(7):
                    self.tblReporte.setItem(i, j, QTableWidgetItem(str(cita[j]) if cita[j] else ""))

    def exportar_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar a PDF",
            "reporte_citas.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:
            html = """
            <html>
            <head>
                <style>
                    body { font-family: Arial; }
                    h1 { text-align: center; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid black; padding: 8px; text-align: left; }
                    th { background-color: #D0EDFC; }
                </style>
            </head>
            <body>
                <h1>REPORTE DE CITAS</h1>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Cliente</th>
                        <th>Servicio</th>
                        <th>Fecha</th>
                        <th>Hora</th>
                        <th>Estado</th>
                        <th>Notas</th>
                    </tr>
            """

            for row in range(self.tblReporte.rowCount()):
                html += "<tr>"
                for col in range(self.tblReporte.columnCount()):
                    item = self.tblReporte.item(row, col)
                    text = item.text() if item else ""
                    html += f"<td>{text}</td>"
                html += "</tr>"

            fecha_actual = QDate.currentDate().toString("dd/MM/yyyy")
            html += f"""
                </table>
                <p><strong>Fecha de generación:</strong> {fecha_actual}</p>
            </body>
            </html>
            """

            document = QTextDocument()
            document.setHtml(html)

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFileName(file_path)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Landscape)

            document.print(printer)

            QMessageBox.information(
                self,
                "Éxito",
                f"Reporte exportado correctamente a:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo exportar el reporte: {e}"
            )

    def volver(self):
        self.db.cerrar()
        self.close()
        self.volver_callback()