import sys
from PyQt6.QtWidgets import QApplication
from controllers.dashboard_controller import DashboardWindow


def main():
    app = QApplication(sys.argv)
    w = DashboardWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()