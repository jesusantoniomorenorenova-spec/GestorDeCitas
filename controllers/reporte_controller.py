from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from pathlib import Path

UI_DIR = Path(__file__).resolve().parents[1] / "ui"

class ReporteWindow(QMainWindow):
    def __init__(self, volver_callback):
        super().__init__()
        uic.loadUi(str(UI_DIR / "reporte.ui"), self)
        self.volver_callback = volver_callback

        self.btnVolver.clicked.connect(self.volver)

    def volver(self):
        self.close()
        self.volver_callback()