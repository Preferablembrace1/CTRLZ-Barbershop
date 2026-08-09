import os
import re
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMessageBox, QLabel, QPushButton, 
    QFrame
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QDate
import database
from email_sender import send_appointment_email

UI_DIR = os.path.join(os.path.dirname(__file__), "ui")

class UiWrapper:
    def __init__(self, widget):
        self._widget = widget

    def __getattr__(self, name):
        from PySide6.QtCore import QObject
        child = self._widget.findChild(QObject, name)
        if child is not None:
            return child
        return super().__getattribute__(name)
        
    def __call__(self):
        return self._widget
        
    def findChild(self, *args, **kwargs):
        return self._widget.findChild(*args, **kwargs)

def load_ui(ui_file_name):
    loader = QUiLoader()
    path = os.path.join(UI_DIR, ui_file_name)
    ui_file = QFile(path)
    if not ui_file.open(QFile.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
    ui = loader.load(ui_file)
    ui_file.close()
    return UiWrapper(ui)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargar main_window.ui
        self.ui = load_ui("main_window.ui")
        self.setCentralWidget(self.ui())
        self.setWindowTitle("CTRLZ Barbershop")
        
        self.stacked_widget = self.ui.stackedWidget
        
        # Datos de la cita actual
        self.appointment_data = {
            "nombre": "",
            "telefono": "",
            "correo": "",
            "id_barbero": None,
            "barbero_nombre": "",
            "id_corte": None,
            "corte_nombre": "",
            "corte_precio": 0.0,
            "fecha": "",
            "hora": ""
        }
        
        # Instanciar páginas
        self.page_home = load_ui("page_home.ui")
        self.page_datos = load_ui("page_datos.ui")
        self.page_barbero = load_ui("page_barbero.ui")
        self.page_corte = load_ui("page_corte.ui")
        self.page_fecha = load_ui("page_fecha.ui")
        self.page_resumen = load_ui("page_resumen.ui")
        self.page_verificar = load_ui("page_verificar.ui")
        
        # Agregar al stacked widget (indices 0 a 6)
        self.stacked_widget.addWidget(self.page_home())      # 0
        self.stacked_widget.addWidget(self.page_datos())     # 1
        self.stacked_widget.addWidget(self.page_barbero())   # 2
        self.stacked_widget.addWidget(self.page_corte())     # 3
        self.stacked_widget.addWidget(self.page_fecha())     # 4
        self.stacked_widget.addWidget(self.page_resumen())   # 5
        self.stacked_widget.addWidget(self.page_verificar()) # 6
        
        self.setup_connections()
        
    def setup_connections(self):
        # --- Page Home ---
        self.page_home.btnAgendar.clicked.connect(lambda: self.go_to_page(1))
        self.page_home.btnVerificar.clicked.connect(lambda: self.go_to_page(6))
        self.page_home.btnAdmin.clicked.connect(self.show_admin_msg)
        
        # --- Page Datos ---
        self.page_datos.btnBack.clicked.connect(lambda: self.go_to_page(0))
        self.page_datos.btnNext.clicked.connect(self.validate_datos)
        
        # --- Page Barbero ---
        self.page_barbero.btnBack.clicked.connect(lambda: self.go_to_page(1))
        self.page_barbero.btnNext.clicked.connect(lambda: self.go_to_page(3))
        
        # --- Page Corte ---
        self.page_corte.btnBack.clicked.connect(lambda: self.go_to_page(2))
        self.page_corte.btnNext.clicked.connect(lambda: self.go_to_page(4))
        
        # --- Page Fecha ---
        self.page_fecha.btnBack.clicked.connect(lambda: self.go_to_page(3))
        self.page_fecha.btnNext.clicked.connect(self.go_to_resumen)
        self.page_fecha.calendarWidget.setMinimumDate(QDate.currentDate())
        self.page_fecha.calendarWidget.clicked.connect(self.update_horarios)
        
        # --- Page Resumen ---
        self.page_resumen.btnBack.clicked.connect(lambda: self.go_to_page(4))
        self.page_resumen.btnConfirmar.clicked.connect(self.confirmar_cita)
        
        # --- Page Verificar ---
        self.page_verificar.btnHome.clicked.connect(lambda: self.go_to_page(0))
        self.page_verificar.btnBuscar.clicked.connect(self.verificar_cita)

    def go_to_page(self, index):
        if index == 2:
            self.load_barberos()
        elif index == 3:
            self.load_cortes()
        elif index == 4:
            self.update_horarios()
            self.page_fecha.btnNext.setEnabled(False)
        self.stacked_widget.setCurrentIndex(index)

    def show_admin_msg(self):
        QMessageBox.information(self, "Admin", "Módulo de administración próximamente.")

    # --- Validaciones y lógica específica ---

    def validate_datos(self):
        nombre = self.page_datos.txtNombre.text().strip()
        telefono = self.page_datos.txtTelefono.text().strip()
        correo = self.page_datos.txtCorreo.text().strip()
        
        if not nombre or not telefono or not correo:
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos.")
            return
            
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, correo):
            QMessageBox.warning(self, "Error", "Correo electrónico inválido.")
            return
            
        self.appointment_data["nombre"] = nombre
        self.appointment_data["telefono"] = telefono
        self.appointment_data["correo"] = correo
        
        self.go_to_page(2)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def load_barberos(self):
        layout = self.page_barbero.gridLayoutCards
        self.clear_layout(layout)
        
        barberos = database.get_barberos()
        self.barbero_cards = []
        
        row, col = 0, 0
        for b in barberos:
            id_b, nombre, correo, especialidad = b
            
            card = QFrame()
            card.setProperty("class", "CardWidget")
            card.setProperty("selected", False)
            card.setMinimumSize(250, 120)
            
            # Hacer la tarjeta clickeable
            card.mousePressEvent = lambda event, b_id=id_b, b_name=nombre, c=card: self.select_barbero(b_id, b_name, c)
            
            vbox = QVBoxLayout(card)
            lbl_nombre = QLabel(nombre)
            lbl_nombre.setProperty("class", "CardTitle")
            lbl_esp = QLabel(f"Servicios: {especialidad}")
            lbl_esp.setProperty("class", "CardSubtitle")
            lbl_esp.setWordWrap(True)
            
            vbox.addWidget(lbl_nombre)
            vbox.addWidget(lbl_esp)
            
            layout.addWidget(card, row, col)
            self.barbero_cards.append(card)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        self.page_barbero.btnNext.setEnabled(self.appointment_data["id_barbero"] is not None)

    def select_barbero(self, b_id, b_name, selectedCard):
        self.appointment_data["id_barbero"] = b_id
        self.appointment_data["barbero_nombre"] = b_name
        
        for card in self.barbero_cards:
            is_selected = "true" if card == selectedCard else "false"
            card.setProperty("selected", is_selected)
            card.style().unpolish(card)
            card.style().polish(card)
            
        self.page_barbero.btnNext.setEnabled(True)

    def load_cortes(self):
        layout = self.page_corte.gridLayoutCards
        self.clear_layout(layout)
        
        # Filtrar cortes por el barbero seleccionado (o genéricos)
        cortes = database.get_cortes(self.appointment_data["id_barbero"])
        self.corte_cards = []
        
        row, col = 0, 0
        for c in cortes:
            id_c, nombre, precio = c
            
            card = QFrame()
            card.setProperty("class", "CardWidget")
            card.setProperty("selected", False)
            card.setMinimumSize(250, 120)
            
            card.mousePressEvent = lambda event, c_id=id_c, c_name=nombre, c_precio=precio, cd=card: self.select_corte(c_id, c_name, c_precio, cd)
            
            vbox = QVBoxLayout(card)
            lbl_nombre = QLabel(nombre)
            lbl_nombre.setProperty("class", "CardTitle")
            lbl_precio = QLabel(f"RD$ {precio}")
            lbl_precio.setProperty("class", "CardPrice")
            
            vbox.addWidget(lbl_nombre)
            vbox.addWidget(lbl_precio)
            
            layout.addWidget(card, row, col)
            self.corte_cards.append(card)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        self.page_corte.btnNext.setEnabled(self.appointment_data["id_corte"] is not None)

    def select_corte(self, c_id, c_name, c_precio, selectedCard):
        self.appointment_data["id_corte"] = c_id
        self.appointment_data["corte_nombre"] = c_name
        self.appointment_data["corte_precio"] = float(c_precio)
        
        for card in self.corte_cards:
            is_selected = "true" if card == selectedCard else "false"
            card.setProperty("selected", is_selected)
            card.style().unpolish(card)
            card.style().polish(card)
            
        self.page_corte.btnNext.setEnabled(True)

    def update_horarios(self):
        fecha = self.page_fecha.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        layout = self.page_fecha.verticalLayoutHorarios
        self.clear_layout(layout)
        
        # Generar horas de 9:00 AM a 7:00 PM cada 1h
        horas = [f"{h:02d}:00" for h in range(9, 19)]
        
        ocupados = database.get_available_horarios(self.appointment_data["id_barbero"], fecha)
        
        self.horario_buttons = []
        
        for hora in horas:
            btn = QPushButton(hora)
            btn.setCheckable(True)
            if hora in ocupados:
                btn.setEnabled(False)
                btn.setText(f"{hora} (Ocupado)")
            else:
                btn.clicked.connect(lambda checked, h=hora, b=btn: self.select_horario(h, b))
                
            layout.addWidget(btn)
            self.horario_buttons.append(btn)
            
        # Reset selección
        self.appointment_data["fecha"] = fecha
        self.appointment_data["hora"] = ""
        self.page_fecha.btnNext.setEnabled(False)

    def select_horario(self, hora, selectedBtn):
        self.appointment_data["hora"] = hora
        
        for btn in self.horario_buttons:
            if btn != selectedBtn:
                btn.setChecked(False)
                
        self.page_fecha.btnNext.setEnabled(True)

    def go_to_resumen(self):
        d = self.appointment_data
        self.page_resumen.lblResumenNombre.setText(f"Cliente: {d['nombre']}")
        self.page_resumen.lblResumenBarbero.setText(f"Barbero: {d['barbero_nombre']}")
        self.page_resumen.lblResumenCorte.setText(f"Corte: {d['corte_nombre']}")
        self.page_resumen.lblResumenPrecio.setText(f"Precio: RD$ {d['corte_precio']}")
        self.page_resumen.lblResumenFecha.setText(f"Fecha: {d['fecha']} a las {d['hora']}")
        
        self.go_to_page(5)

    def confirmar_cita(self):
        d = self.appointment_data
        
        # 1. Crear cliente si no existe
        id_cliente = database.add_cliente(d['nombre'], d['correo'], d['telefono'])
        if not id_cliente:
            QMessageBox.critical(self, "Error", "No se pudo registrar el cliente. Verifica que el teléfono no esté siendo usado por otro nombre.")
            return
            
        # 2. Guardar cita
        success, res = database.add_cita(id_cliente, d['id_barbero'], d['id_corte'], d['fecha'], d['hora'])
        
        if success:
            id_cita = res
            # 3. Enviar correo
            email_data = {
                "codigo": id_cita,
                "nombre": d['nombre'],
                "barbero": d['barbero_nombre'],
                "corte": d['corte_nombre'],
                "precio": d['corte_precio'],
                "fecha": d['fecha'],
                "hora": d['hora']
            }
            send_appointment_email(d['correo'], email_data)
            
            QMessageBox.information(self, "¡Cita Confirmada!", 
                f"Tu cita ha sido agendada con éxito.\nCódigo de verificación: {id_cita}\nSe ha enviado un correo con los detalles.")
            
            self.reset_wizard()
            self.go_to_page(0)
        else:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la cita: {res}")

    def reset_wizard(self):
        self.appointment_data = {
            "nombre": "", "telefono": "", "correo": "",
            "id_barbero": None, "barbero_nombre": "",
            "id_corte": None, "corte_nombre": "", "corte_precio": 0.0,
            "fecha": "", "hora": ""
        }
        self.page_datos.txtNombre.clear()
        self.page_datos.txtTelefono.clear()
        self.page_datos.txtCorreo.clear()
        self.page_fecha.calendarWidget.setSelectedDate(QDate.currentDate())

    def verificar_cita(self):
        codigo = self.page_verificar.txtCodigo.text().strip()
        if not codigo.isdigit():
            self.page_verificar.lblResultado.setText("Por favor ingresa un número de código válido.")
            return
            
        cita = database.get_cita_by_id(int(codigo))
        if cita:
            id_cita, cliente, barbero, corte, fecha, hora, estado, precio = cita
            color = "#C8956C" if estado == "pendiente" else ("#10B981" if estado == "completada" else "#EF4444")
            
            res = f"""
            <h3 style='color: #1E1E2E;'>Detalles de la Cita #{id_cita}</h3>
            <p><b>Cliente:</b> {cliente}</p>
            <p><b>Barbero:</b> {barbero}</p>
            <p><b>Servicio:</b> {corte} (RD$ {precio})</p>
            <p><b>Cuándo:</b> {fecha} a las {hora}</p>
            <p><b>Estado:</b> <span style='color: {color}; font-weight: bold;'>{estado.upper()}</span></p>
            """
            self.page_verificar.lblResultado.setText(res)
        else:
            self.page_verificar.lblResultado.setText(f"No se encontró ninguna cita con el código #{codigo}.")
