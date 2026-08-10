"""
Punto de entrada de la aplicación CTRLZ Barbershop.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from app import MainWindow
from database import create_table
from seed_data import seed
from PySide6.QtGui import QIcon


def main():
    # Inicializar la base de datos y poblar datos de prueba
    create_table()
    seed()

    app = QApplication(sys.argv)

    # Cargar estilo (theme)
    theme_path = os.path.join(os.path.dirname(__file__), "styles", "light_theme.qss")
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: No se encontró el archivo de estilos en {theme_path}")

    # Iniciar ventana principal
    window = MainWindow()
    window.resize(900, 700)
    window.setWindowTitle("CTRLZ Barbershop")
    window.setWindowIcon(QIcon("logo.ico"))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
