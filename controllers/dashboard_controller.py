from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from pathlib import Path

from controllers.clientes_controller import ClientesWindow
from controllers.citas_controller import CitasWindow
from controllers.reporte_controller import ReporteWindow

UI_DIR = Path(__file__).resolve().parents[1] / "ui"

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_DIR / "dashboard.ui", self)
        self._ventana_actual = None 

        self.btnClientes.clicked.connect(self.abrir_clientes)
        self.btnCitas.clicked.connect(self.abrir_citas)
        self.btnReporte.clicked.connect(self.abrir_reporte)
        self.btnSalir.clicked.connect(self.close)


    def abrir_clientes(self):
        self._abrir_ventana(ClientesWindow)

    def abrir_citas(self):
        self._abrir_ventana(CitasWindow)

    def abrir_reporte(self):
        self._abrir_ventana(ReporteWindow)

    def _abrir_ventana(self, ClaseVentana):
        self.hide()
        self._ventana_actual = ClaseVentana(volver_callback=self.volver_a_dashboard)
        self._ventana_actual.show()
    
    def volver_a_dashboard(self):
        if self._ventana_actual:
            self._ventana_actual.close()
            self._ventana_actual = None
        self.show()