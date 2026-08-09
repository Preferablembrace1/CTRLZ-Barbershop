import os
import re
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, 
    QPushButton, QFrame, QDialog, QLineEdit, QComboBox
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QFont
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
        self.page_admin = load_ui("page_admin.ui")
        
        # Agregar al stacked widget (indices 0 a 7)
        self.stacked_widget.addWidget(self.page_home())      # 0
        self.stacked_widget.addWidget(self.page_datos())     # 1
        self.stacked_widget.addWidget(self.page_barbero())   # 2
        self.stacked_widget.addWidget(self.page_corte())     # 3
        self.stacked_widget.addWidget(self.page_fecha())     # 4
        self.stacked_widget.addWidget(self.page_resumen())   # 5
        self.stacked_widget.addWidget(self.page_verificar()) # 6
        self.stacked_widget.addWidget(self.page_admin())     # 7
        
        # Credenciales de admin
        self.ADMIN_USER = "admin"
        self.ADMIN_PASS = "1234"
        
        self.setup_connections()
        
    def setup_connections(self):
        # --- Page Home ---
        self.page_home.btnAgendar.clicked.connect(lambda: self.go_to_page(1))
        self.page_home.btnVerificar.clicked.connect(lambda: self.go_to_page(6))
        self.page_home.btnAdmin.clicked.connect(self.show_admin_login)
        
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
        
        # --- Page Admin ---
        self.page_admin.btnBack.clicked.connect(lambda: self.go_to_page(0))
        self.page_admin.btnTabCitas.setCheckable(True)
        self.page_admin.btnTabGestion.setCheckable(True)
        self.page_admin.btnTabCitas.setChecked(True)
        self.page_admin.btnTabCitas.clicked.connect(lambda: self.switch_admin_tab(0))
        self.page_admin.btnTabGestion.clicked.connect(lambda: self.switch_admin_tab(1))
        self.page_admin.adminCalendar.clicked.connect(self.load_admin_citas_by_date)
        self.page_admin.adminCalendar.selectionChanged.connect(self.color_calendar_dates)
        self.page_admin.btnVerPendientes.clicked.connect(self.load_admin_pendientes)
        self.page_admin.btnVerTodas.clicked.connect(self.load_admin_citas)
        self.page_admin.btnAddBarbero.clicked.connect(self.admin_add_barbero)
        self.page_admin.btnAddCorte.clicked.connect(self.admin_add_corte)

    def go_to_page(self, index):
        if index == 2:
            self.load_barberos()
        elif index == 3:
            self.load_cortes()
        elif index == 4:
            self.update_horarios()
            self.page_fecha.btnNext.setEnabled(False)
        elif index == 7:
            self.color_calendar_dates()
            self.load_admin_citas()
            self.load_admin_barberos()
            self.load_admin_cortes()
            self.load_barbero_combo()
            self.switch_admin_tab(0)
        self.stacked_widget.setCurrentIndex(index)

    # --- Login de Admin ---

    def show_admin_login(self):
        """Mostrar diálogo de login para acceder al panel de admin"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🔐 Acceso Admin")
        dialog.setFixedSize(380, 330)
        dialog.setStyleSheet("QDialog { background-color: #FAF7F2; }")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(32, 28, 32, 28)
        
        # Título
        lbl_title = QLabel("Iniciar Sesión")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E1E2E;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_sub = QLabel("Ingresa tus credenciales de administrador")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(lbl_sub)
        
        # Campo Usuario
        lbl_user = QLabel("Usuario")
        lbl_user.setStyleSheet("font-size: 13px; font-weight: bold; color: #1E1E2E;")
        layout.addWidget(lbl_user)
        txt_user = QLineEdit()
        txt_user.setPlaceholderText("Ingresa tu usuario")
        layout.addWidget(txt_user)
        
        # Campo Contraseña
        lbl_pass = QLabel("Contraseña")
        lbl_pass.setStyleSheet("font-size: 13px; font-weight: bold; color: #1E1E2E;")
        layout.addWidget(lbl_pass)
        txt_pass = QLineEdit()
        txt_pass.setPlaceholderText("Ingresa tu contraseña")
        txt_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(txt_pass)
        
        # Espacio
        layout.addSpacing(8)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setProperty("cssClass", "btnSecondary")
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_login = QPushButton("Ingresar")
        btn_login.setProperty("cssClass", "btnAction")
        
        def attempt_login():
            user = txt_user.text().strip()
            password = txt_pass.text().strip()
            if user == self.ADMIN_USER and password == self.ADMIN_PASS:
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Error", "Usuario o contraseña incorrectos.")
                txt_pass.clear()
                txt_pass.setFocus()
        
        btn_login.clicked.connect(attempt_login)
        txt_pass.returnPressed.connect(attempt_login)
        txt_user.returnPressed.connect(lambda: txt_pass.setFocus())
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_login)
        layout.addLayout(btn_layout)
        
        # Mostrar diálogo y navegar si se acepta
        if dialog.exec() == QDialog.Accepted:
            self.go_to_page(7)

    # --- Admin: Navegación de Tabs ---

    def switch_admin_tab(self, index):
        """Cambiar entre las pestañas de Citas y Gestión"""
        self.page_admin.adminStackedWidget.setCurrentIndex(index)
        self.page_admin.btnTabCitas.setChecked(index == 0)
        self.page_admin.btnTabGestion.setChecked(index == 1)
        
        if index == 0:
            self.color_calendar_dates()
            self.load_admin_citas()
        else:
            self.load_admin_barberos()
            self.load_admin_cortes()
            self.load_barbero_combo()

    # --- Admin: Calendario con colores ---

    def color_calendar_dates(self):
        """Colorear las fechas del calendario según el estado de las citas"""
        calendar = self.page_admin.adminCalendar
        selected_date = calendar.selectedDate()
        
        # Limpiar formatos previos
        calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        citas = database.get_all_citas()
        
        # Agrupar citas por fecha y determinar el estado dominante
        fechas_estado = {}
        for cita in citas:
            fecha_str = cita[4]  # fecha
            estado = cita[6]     # estado
            
            if estado == "cancelada":
                continue
            
            if fecha_str not in fechas_estado:
                fechas_estado[fecha_str] = set()
            fechas_estado[fecha_str].add(estado)
        
        for fecha_str, estados in fechas_estado.items():
            parts = fecha_str.split("-")
            if len(parts) != 3:
                continue
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            qdate = QDate(year, month, day)
            
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Bold)
            
            is_selected = (qdate == selected_date)
            
            if "pendiente" in estados:
                # Pendiente
                if is_selected:
                    fmt.setBackground(QColor("#DC2626"))  # Solid Red
                    fmt.setForeground(QColor("#FFFFFF"))
                else:
                    fmt.setBackground(QColor("#FEE2E2"))  # Light Red
                    fmt.setForeground(QColor("#DC2626"))
            elif "confirmada" in estados:
                # Confirmada
                if is_selected:
                    fmt.setBackground(QColor("#059669"))  # Solid Green
                    fmt.setForeground(QColor("#FFFFFF"))
                else:
                    fmt.setBackground(QColor("#D1FAE5"))  # Light Green
                    fmt.setForeground(QColor("#059669"))
            
            calendar.setDateTextFormat(qdate, fmt)
        
        # Si la fecha seleccionada no tiene citas, forzar su color de selección normal
        selected_date_str = selected_date.toString("yyyy-MM-dd")
        if selected_date_str not in fechas_estado:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#C8956C"))
            fmt.setForeground(QColor("#FFFFFF"))
            fmt.setFontWeight(QFont.Bold)
            calendar.setDateTextFormat(selected_date, fmt)
            
        # Actualizar el label informativo
        total_pendientes = sum(1 for c in citas if c[6] == "pendiente")
        total_confirmadas = sum(1 for c in citas if c[6] == "confirmada")
        self.page_admin.lblCalendarInfo.setText(
            f"📊 Resumen:\n\n"
            f"🔴 {total_pendientes} cita(s) pendiente(s)\n"
            f"🟢 {total_confirmadas} cita(s) confirmada(s)\n\n"
            f"Selecciona una fecha para ver sus citas."
        )

    # --- Admin: Gestión de Citas ---

    def load_admin_citas(self):
        """Cargar todas las citas en el panel de admin"""
        layout = self.page_admin.layoutAdminCitas
        self.clear_layout(layout)
        self.page_admin.lblCitasHeader.setText("Todas las Citas")
        
        citas = database.get_all_citas()
        
        if not citas:
            lbl_empty = QLabel("No hay citas registradas.")
            lbl_empty.setStyleSheet("color: #9CA3AF; font-size: 14px; padding: 20px;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_empty)
            return
        
        for cita in citas:
            id_cita, cliente, barbero, corte, fecha, hora, estado, precio = cita
            self._create_cita_card(layout, id_cita, cliente, barbero, corte, fecha, hora, estado, precio)

    def load_admin_pendientes(self):
        """Cargar solo las citas pendientes"""
        layout = self.page_admin.layoutAdminCitas
        self.clear_layout(layout)
        self.page_admin.lblCitasHeader.setText("⏳ Citas Pendientes")
        
        citas = database.get_all_citas()
        pendientes = [c for c in citas if c[6] == "pendiente"]
        
        if not pendientes:
            lbl_empty = QLabel("¡No hay citas pendientes! 🎉")
            lbl_empty.setStyleSheet("color: #10B981; font-size: 14px; padding: 20px; font-weight: bold;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_empty)
            return
        
        for cita in pendientes:
            id_cita, cliente, barbero, corte, fecha, hora, estado, precio = cita
            self._create_cita_card(layout, id_cita, cliente, barbero, corte, fecha, hora, estado, precio)

    def load_admin_citas_by_date(self):
        """Cargar citas filtradas por la fecha seleccionada en el calendario"""
        layout = self.page_admin.layoutAdminCitas
        self.clear_layout(layout)
        
        fecha = self.page_admin.adminCalendar.selectedDate().toString("yyyy-MM-dd")
        self.page_admin.lblCitasHeader.setText(f"Citas del {fecha}")
        citas = database.get_cita_by_fecha(fecha)
        
        if not citas:
            lbl_empty = QLabel(f"No hay citas para {fecha}.")
            lbl_empty.setStyleSheet("color: #9CA3AF; font-size: 14px; padding: 20px;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_empty)
            return
        
        for cita in citas:
            id_cita, cliente, barbero, corte, fecha, hora, estado, precio = cita
            self._create_cita_card(layout, id_cita, cliente, barbero, corte, fecha, hora, estado, precio)

    def _create_cita_card(self, layout, id_cita, cliente, barbero, corte, fecha, hora, estado, precio):
        """Crear una tarjeta de cita en el panel admin con borde de color lateral"""
        # Color del borde izquierdo según estado
        if estado == "pendiente":
            border_color = "#F59E0B"  # Amarillo/naranja
            estado_icon = "⏳"
            estado_color = "#D97706"
        elif estado == "confirmada":
            border_color = "#10B981"  # Verde
            estado_icon = "✅"
            estado_color = "#059669"
        else:
            border_color = "#EF4444"  # Rojo
            estado_icon = "❌"
            estado_color = "#DC2626"
        
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E2D8CD;
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 4px;
            }}
            QFrame:hover {{
                border: 1px solid #C8956C;
                border-left: 4px solid {border_color};
                background-color: #FFFBF5;
            }}
        """)
        card.setMinimumHeight(70)
        card.setMaximumHeight(100)
        
        hbox = QHBoxLayout(card)
        hbox.setContentsMargins(14, 8, 12, 8)
        hbox.setSpacing(12)
        
        # Info de la cita
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        lbl_header = QLabel(f"#{id_cita}  {cliente}")
        lbl_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E1E2E; border: none; background: transparent;")
        
        lbl_detail = QLabel(f"✂️ {corte} con {barbero}  •  📅 {fecha} {hora}  •  RD$ {precio}")
        lbl_detail.setStyleSheet("color: #6B7280; font-size: 12px; border: none; background: transparent;")
        lbl_detail.setWordWrap(True)
        
        lbl_estado = QLabel(f"{estado_icon} {estado.upper()}")
        lbl_estado.setStyleSheet(f"color: {estado_color}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        
        info_layout.addWidget(lbl_header)
        info_layout.addWidget(lbl_detail)
        info_layout.addWidget(lbl_estado)
        
        hbox.addLayout(info_layout, 1)
        
        # Botones de acción (solo si está pendiente)
        if estado == "pendiente":
            btn_layout = QVBoxLayout()
            btn_layout.setSpacing(4)
            
            btn_confirm = QPushButton("✓ Confirmar")
            btn_confirm.setProperty("cssClass", "btnConfirm")
            btn_confirm.setFixedSize(110, 32)
            btn_confirm.clicked.connect(lambda checked, cid=id_cita: self.admin_confirmar_cita(cid))
            
            btn_cancel = QPushButton("✕ Cancelar")
            btn_cancel.setProperty("cssClass", "btnCancel")
            btn_cancel.setFixedSize(110, 32)
            btn_cancel.clicked.connect(lambda checked, cid=id_cita: self.admin_cancelar_cita(cid))
            
            btn_layout.addWidget(btn_confirm)
            btn_layout.addWidget(btn_cancel)
            hbox.addLayout(btn_layout)
        
        layout.addWidget(card)

    def admin_confirmar_cita(self, id_cita):
        """Confirmar una cita desde el panel admin"""
        success, msg = database.confirm_cita(id_cita)
        if success:
            QMessageBox.information(self, "Cita Confirmada", msg)
        else:
            QMessageBox.warning(self, "Error", msg)
        self.color_calendar_dates()
        self.load_admin_citas()

    def admin_cancelar_cita(self, id_cita):
        """Cancelar una cita desde el panel admin"""
        reply = QMessageBox.question(self, "Confirmar Cancelación", 
            f"¿Seguro que deseas cancelar la cita #{id_cita}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, msg = database.cancel_cita(id_cita)
            if success:
                QMessageBox.information(self, "Cita Cancelada", msg)
            else:
                QMessageBox.warning(self, "Error", msg)
            self.color_calendar_dates()
            self.load_admin_citas()

    # --- Admin: Gestión de Barberos ---

    def load_admin_barberos(self):
        """Cargar la lista de barberos en el panel de gestión"""
        layout = self.page_admin.layoutBarberosList
        self.clear_layout(layout)
        
        barberos = database.get_barberos()
        
        if not barberos:
            lbl = QLabel("No hay barberos registrados.")
            lbl.setStyleSheet("color: #9CA3AF; font-size: 13px;")
            layout.addWidget(lbl)
            return
        
        for b in barberos:
            id_b, nombre, email, especialidad = b
            
            card = QFrame()
            card.setProperty("cssClass", "AdminItemCard")
            hbox = QHBoxLayout(card)
            hbox.setContentsMargins(10, 6, 10, 6)
            
            info = QVBoxLayout()
            lbl_name = QLabel(nombre)
            lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
            lbl_esp = QLabel(f"{especialidad} • {email}")
            lbl_esp.setStyleSheet("color: #6B7280; font-size: 12px;")
            info.addWidget(lbl_name)
            info.addWidget(lbl_esp)
            
            btn_del = QPushButton("Eliminar")
            btn_del.setProperty("cssClass", "btnDelete")
            btn_del.setFixedWidth(80)
            btn_del.clicked.connect(lambda checked, bid=id_b, bname=nombre: self.admin_delete_barbero(bid, bname))
            
            hbox.addLayout(info, 1)
            hbox.addWidget(btn_del)
            layout.addWidget(card)

    def admin_add_barbero(self):
        """Agregar un nuevo barbero desde el panel admin"""
        nombre = self.page_admin.txtBarberoNombre.text().strip()
        email = self.page_admin.txtBarberoEmail.text().strip()
        especialidad = self.page_admin.txtBarberoEspecialidad.text().strip()
        
        if not nombre or not email or not especialidad:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            QMessageBox.warning(self, "Error", "Correo electrónico inválido.")
            return
        
        result = database.add_barbero(nombre, email, especialidad)
        if result:
            QMessageBox.information(self, "Éxito", f"Barbero '{nombre}' agregado correctamente.")
            self.page_admin.txtBarberoNombre.clear()
            self.page_admin.txtBarberoEmail.clear()
            self.page_admin.txtBarberoEspecialidad.clear()
            self.load_admin_barberos()
            self.load_barbero_combo()
        else:
            QMessageBox.warning(self, "Error", "No se pudo agregar el barbero. Verifica que el email no esté duplicado.")

    def admin_delete_barbero(self, id_barbero, nombre):
        """Eliminar un barbero con confirmación"""
        reply = QMessageBox.question(self, "Confirmar Eliminación",
            f"¿Seguro que deseas eliminar al barbero '{nombre}'?\nEsto podría afectar citas existentes.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            result = database.delete_barbero(id_barbero)
            if result:
                QMessageBox.information(self, "Eliminado", f"Barbero '{nombre}' eliminado.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el barbero.")
            self.load_admin_barberos()
            self.load_barbero_combo()

    # --- Admin: Gestión de Cortes ---

    def load_barbero_combo(self):
        """Cargar el combo de barberos para asociar cortes"""
        combo = self.page_admin.cmbCorteBarbero
        combo.clear()
        combo.addItem("Genérico (todos los barberos)", None)
        
        barberos = database.get_barberos()
        for b in barberos:
            combo.addItem(b[1], b[0])  # nombre, id

    def load_admin_cortes(self):
        """Cargar la lista de cortes en el panel de gestión"""
        layout = self.page_admin.layoutCortesList
        self.clear_layout(layout)
        
        cortes = database.get_all_cortes_with_barbero()
        
        if not cortes:
            lbl = QLabel("No hay cortes registrados.")
            lbl.setStyleSheet("color: #9CA3AF; font-size: 13px;")
            layout.addWidget(lbl)
            return
        
        for c in cortes:
            id_c, nombre, precio, barbero_name = c
            
            card = QFrame()
            card.setProperty("cssClass", "AdminItemCard")
            hbox = QHBoxLayout(card)
            hbox.setContentsMargins(10, 6, 10, 6)
            
            info = QVBoxLayout()
            lbl_name = QLabel(nombre)
            lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
            lbl_detail = QLabel(f"RD$ {precio} • Barbero: {barbero_name}")
            lbl_detail.setStyleSheet("color: #C8956C; font-size: 12px; font-weight: bold;")
            info.addWidget(lbl_name)
            info.addWidget(lbl_detail)
            
            btn_del = QPushButton("Eliminar")
            btn_del.setProperty("cssClass", "btnDelete")
            btn_del.setFixedWidth(80)
            btn_del.clicked.connect(lambda checked, cid=id_c, cname=nombre: self.admin_delete_corte(cid, cname))
            
            hbox.addLayout(info, 1)
            hbox.addWidget(btn_del)
            layout.addWidget(card)

    def admin_add_corte(self):
        """Agregar un nuevo corte desde el panel admin"""
        nombre = self.page_admin.txtCorteNombre.text().strip()
        precio_text = self.page_admin.txtCortePrecio.text().strip()
        
        if not nombre or not precio_text:
            QMessageBox.warning(self, "Error", "Nombre y precio son obligatorios.")
            return
        
        try:
            precio = float(precio_text)
            if precio <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "El precio debe ser un número positivo.")
            return
        
        # Obtener barbero seleccionado del combo
        combo = self.page_admin.cmbCorteBarbero
        barbero_id = combo.currentData()
        
        result = database.add_corte(nombre, precio, barbero_id)
        if result:
            QMessageBox.information(self, "Éxito", f"Corte '{nombre}' agregado correctamente.")
            self.page_admin.txtCorteNombre.clear()
            self.page_admin.txtCortePrecio.clear()
            self.page_admin.cmbCorteBarbero.setCurrentIndex(0)
            self.load_admin_cortes()
        else:
            QMessageBox.warning(self, "Error", "No se pudo agregar el corte.")

    def admin_delete_corte(self, id_corte, nombre):
        """Eliminar un corte con confirmación"""
        reply = QMessageBox.question(self, "Confirmar Eliminación",
            f"¿Seguro que deseas eliminar el corte '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            result = database.delete_Corte(id_corte)
            if result:
                QMessageBox.information(self, "Eliminado", f"Corte '{nombre}' eliminado.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el corte.")
            self.load_admin_cortes()

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
