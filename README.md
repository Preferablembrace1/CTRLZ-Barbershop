# ✂️ CTRLZ-Barbershop

Aplicación de escritorio para la gestión integral de una barbería, desarrollada en **Python** con interfaz gráfica moderna usando **PySide6** y base de datos **SQLite**. Permite a los clientes agendar citas y a los administradores gestionar barberos, cortes y el estado de todas las reservaciones.

---

## 📋 Índice

- [✨ Características Principales](#-características-principales)
- [🏗️ Arquitectura del Proyecto](#️-arquitectura-del-proyecto)
- [📂 Estructura de Archivos](#-estructura-de-archivos)
- [⚙️ Requisitos Previos](#️-requisitos-previos)
- [🚀 Instalación y Ejecución](#-instalación-y-ejecución)
- [📖 Guía de Uso](#-guía-de-uso)
  - [Para Clientes](#para-clientes-agendar-cita)
  - [Verificar Cita](#verificar-cita)
  - [Panel de Administración](#panel-de-administración)
- [💾 Base de Datos](#-base-de-datos)
- [📧 Configuración de Correo Electrónico](#-configuración-de-correo-electrónico)
- [🛠️ Tecnologías Utilizadas](#️-tecnologías-utilizadas)
- [🎨 Personalización y Estilos](#-personalización-y-estilos)
- [🔐 Credenciales por Defecto](#-credenciales-por-defecto)
- [📝 Descripción de Módulos](#-descripción-de-módulos)

---

## ✨ Características Principales

- **✅ Sistema de Agendamiento:** Flujo guiado paso a paso para que los clientes reserven citas seleccionando barbero, tipo de corte, fecha y hora.
- **📅 Calendario Interactivo:** Visualización de disponibilidad en tiempo real con colores según el estado de las citas (pendiente/confirmada).
- **👥 Gestión de Barberos:** Alta, baja y listado de barberos con sus especialidades.
- **💇 Gestión de Cortes:** Administración de servicios (cortes) con precios y asignación a barberos específicos o genéricos.
- **🔔 Estados de Citas:** Ciclo completo: `pendiente` → `confirmada` → `cancelada`, con gestión visual por colores.
- **📧 Envío de Correos:** Confirmación automática por email con comprobante HTML personalizado (incluye modo simulado sin credenciales SMTP).
- **🔍 Verificación de Citas:** Los clientes pueden consultar el estado de su cita usando el código único recibido.
- **🎨 Interfaz Moderna:** Diseño con paleta de colores cálidos (beige/marrón), tarjetas con efecto hover, calendario estilizado y tema claro profesional.
- **💾 Datos de Prueba:** Poblado automático de barberos y cortes de ejemplo al iniciar por primera vez.
- **🛡️ Validaciones Robustas:** Verificación de formato de email, teléfono (RD), precios positivos, campos obligatorios y solapamiento de horarios.

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue un patrón **Multi-Page** (múltiples páginas) usando un `QStackedWidget` como contenedor principal, donde cada pantalla del flujo es una página cargada dinámicamente desde un archivo `.ui` de Qt Designer.

```
┌─────────────────────────────────────────────────────┐
│                   MainWindow                         │
│  ┌───────────────────────────────────────────────┐  │
│  │              QStackedWidget                    │  │
│  │  ┌──────┐ ┌──────┐ ┌────────┐ ┌────────────┐  │  │
│  │  │ Home │ │ Datos│ │Barbero │ │   Corte    │  │  │
│  │  └──────┘ └──────┘ └────────┘ └────────────┘  │  │
│  │  ┌──────┐ ┌──────┐ ┌────────┐ ┌────────────┐  │  │
│  │  │Fecha │ │Resumen│ │Verificar│ │ Admin      │  │  │
│  │  └──────┘ └──────┘ └────────┘ └────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```
---

## 📂 Estructura de Archivos

```
CTRLZ-Barbershop/
├── db/
│   └── CTRLZ_BarberShop.db          # Base de datos SQLite (se crea automáticamente)
├── styles/
│   └── light_theme.qss              # Hoja de estilos QSS del tema claro
├── ui/
│   ├── main_window.ui               # Ventana principal + StackedWidget
│   ├── page_home.ui                 # Pantalla de inicio
│   ├── page_datos.ui                # Paso 1: Datos del cliente
│   ├── page_barbero.ui              # Paso 2: Selección de barbero
│   ├── page_corte.ui                # Paso 3: Selección de corte/servicio
│   ├── page_fecha.ui                # Paso 4: Fecha y hora
│   ├── page_resumen.ui              # Paso 5: Resumen y confirmación
│   ├── page_verificar.ui            # Consulta de cita por código
│   └── page_admin.ui                # Panel de administración (2 tabs)
├── .gitignore
├── README.md
├── app.py                           # Lógica principal de la interfaz
├── database.py                      # Acceso a base de datos SQLite
├── email_sender.py                  # Módulo de envío de correos SMTP
├── fix_ui.py                        # Script auxiliar para corregir nombres en .ui
├── logo.ico / logo.png              # Ícono de la aplicación
├── main.py                          # Punto de entrada
└── seed_data.py                     # Poblado de datos de prueba
```

---

## ⚙️ Requisitos Previos

- **Python** 3.8+ (recomendado 3.10+)
- **PySide6** (interfaz gráfica Qt for Python)
- Conexión a internet **solo** si se desea enviar correos reales (requiere credenciales SMTP). Sin ellas, el correo se simula en consola.

---

## 🚀 Instalación y Ejecución

### 1. Clonar o descargar el proyecto

```bash
cd CTRLZ-Barbershop
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install PySide6
```

> Nota: `sqlite3` y `smtplib` vienen incluidos en la biblioteca estándar de Python.

### 4. Ejecutar la aplicación

```bash
python main.py
```

La aplicación creará automáticamente:
- La carpeta `db/` y el archivo `CTRLZ_BarberShop.db` con todas las tablas.
- Insertará **datos de prueba** (4 barberos y varios cortes) si la base está vacía.

---

## 📖 Guía de Uso

### Para Clientes: Agendar Cita

El flujo es un **wizard de 5 pasos**:

1. **🏠 Pantalla de Inicio:** Haz clic en **"Agendar Cita"**.
2. **📝 Datos Personales:** Ingresa nombre, teléfono (formato RD: `809-XXX-XXXX`, `829` o `849`) y correo electrónico.
3. **👨‍🦰 Seleccionar Barbero:** Haz clic en la tarjeta del barbero deseado (muestra sus especialidades).
4. **💇 Seleccionar Corte:** Elige entre los servicios disponibles (aparecerán los cortes genéricos + los específicos del barbero).
5. **📅 Fecha y Hora:**
   - Selecciona una fecha en el calendario (no permite fechas pasadas).
   - Elige una hora de la lista (9:00 AM a 7:00 PM, cada hora). Los horarios ocupados aparecen deshabilitados.
6. **✅ Resumen:** Revisa los detalles y haz clic en **"Confirmar Cita"**. Recibirás un **código único** y un correo electrónico con los datos.

### Verificar Cita

1. En la pantalla de inicio, haz clic en **"Verificar Cita"**.
2. Ingresa el **código numérico** recibido al agendar.
3. Se mostrarán los detalles completos y el estado actual:
   - 🟡 **Pendiente** (por confirmar por el admin)
   - 🟢 **Confirmada**
   - 🔴 **Cancelada**

### Panel de Administración

1. En la pantalla de inicio, haz clic en **"Panel Admin"**.
2. Inicia sesión con las credenciales (ver [Credenciales por Defecto](#-credenciales-por-defecto)).

#### 📊 Tab 1 — Gestión de Citas

- **Calendario con colores:**
  - 🔴 Rojo claro = Citas pendientes ese día
  - 🟢 Verde claro = Todas confirmadas
  - Haz clic en una fecha para filtrar las citas de ese día.
- **Botones de filtro:**
  - **"Ver Pendientes"**: Muestra solo citas ⏳ pendientes.
  - **"Ver Todas"**: Listado completo del historial.
- **Tarjetas de cita:** Cada cita muestra cliente, barbero, servicio, fecha, hora, precio y estado.
  - Si está **pendiente**, muestra botones **"✓ Confirmar"** y **"✕ Cancelar"**.
- **"Eliminar Canceladas"**: Borra permanentemente todas las citas canceladas del sistema (con confirmación).

#### ⚙️ Tab 2 — Gestión (Barberos y Cortes)

**Gestión de Barberos:**
- **Agregar:** Nombre, email (validado) y especialidad → Botón **"Agregar Barbero"**.
- **Eliminar:** Botón rojo "Eliminar" en cada tarjeta (con confirmación).

**Gestión de Cortes:**
- **Agregar:** Nombre, precio (RD$) y selección de barberos (multiselección: "Genérico" = todos los barberos + individuos).
- **Editar:** Modifica a qué barberos está asignado un corte.
- **Eliminar:** Borra el corte de todos los barberos.

---

## 💾 Base de Datos

Motor: **SQLite** (archivo local: `db/CTRLZ_BarberShop.db`)

### Tablas

| Tabla       | Campos Clave                                                                 | Descripción                                      |
|-------------|-----------------------------------------------------------------------------|--------------------------------------------------|
| **barberos** | `id` (PK), `nombre`, `email` (UNIQUE), `especialidad`                      | Personal de la barbería                          |
| **clientes** | `id` (PK), `nombre`, `email` (UNIQUE), `telefono` (UNIQUE)                 | Clientes registrados automáticamente al agendar  |
| **cortes**   | `id` (PK), `barbero_id` (FK, nullable), `nombre`, `precio`                 | Servicios ofrecidos (barbero_id NULL = genérico) |
| **citas**    | `id_cita` (PK), `cliente_id`, `barbero_id`, `corte_id`, `fecha`, `hora`, `estado` (CHECK: pendiente/confirmada/cancelada) | Reservaciones |

### Relaciones
```
clientes 1──N citas N──1 barberos
                N
                │
                1
             cortes
```

---

## 📧 Configuración de Correo Electrónico

El módulo [email_sender.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/email_sender.py) soporta **dos modos**:

### Modo Simulado (por defecto)
Si no hay credenciales configuradas, al confirmar una cita se imprime por consola un resumen del correo. **No requiere configuración adicional.**

```
==================================================
[MODO SIMULADO] Correo de confirmación:
  Para: cliente@email.com
  Asunto: CTRLZ Barbershop — Confirmación de Cita #7
  ...
==================================================
```

### Modo Real (SMTP)
Configura las siguientes **variables de entorno** antes de ejecutar la app:

| Variable         | Valor Ejemplo (Gmail)       | Descripción                                  |
|------------------|-----------------------------|----------------------------------------------|
| `SMTP_HOST`      | `smtp.gmail.com`            | Servidor SMTP de tu proveedor                |
| `SMTP_PORT`      | `587`                       | Puerto (TLS)                                 |
| `SMTP_USER`      | `tucorreo@gmail.com`        | Tu dirección de correo                       |
| `SMTP_PASSWORD`  | `abcd efgh ijkl mnop`       | **App Password** (no tu contraseña normal)   |

#### Configuración en Windows (PowerShell):
```powershell
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "tucorreo@gmail.com"
$env:SMTP_PASSWORD = "tu_app_password"
python main.py
```

> ⚠️ **Para Gmail:** Debes habilitar la verificación en dos pasos y generar una **App Password** en [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

---

## 🛠️ Tecnologías Utilizadas

| Tecnología       | Versión/Módulo          | Propósito                                  |
|------------------|-------------------------|-------------------------------------------|
| **Python**       | 3.8+                    | Lenguaje de programación principal        |
| **PySide6**      | Qt for Python 6.x       | Framework de interfaz gráfica (LGPL)      |
| **Qt Designer**  | `.ui` files             | Diseño visual de pantallas                 |
| **SQLite3**      | `sqlite3` (stdlib)      | Base de datos embebida local               |
| **SMTPLib**      | `smtplib` + `email` (stdlib) | Envío de correos HTML por TLS        |
| **QSS**          | Qt Style Sheets         | Estilos CSS-like para widgets Qt           |

---

## 🎨 Personalización y Estilos

### Tema Visual
El tema claro se define en [styles/light_theme.qss](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/styles/light_theme.qss). Paleta principal:

| Color       | Código    | Uso                                      |
|-------------|-----------|------------------------------------------|
| Beige       | `#FAF7F2` | Fondo principal                          |
| Café        | `#C8956C` | Acento principal (botones, selección)    |
| Gris oscuro | `#2D3748` | Botones principales                      |
| Verde       | `#10B981` | Éxito / Confirmar                        |
| Rojo        | `#EF4444` | Peligro / Cancelar / Eliminar            |
| Texto       | `#1E1E2E` | Color de texto principal                 |

Puedes modificar cualquier estilo editando directamente el archivo `.qss`; los cambios se aplican al reiniciar la app.

### Datos de Prueba
Para personalizar los barberos y cortes iniciales, edita el archivo [seed_data.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/seed_data.py). Los datos se insertan solo si las tablas están vacías.

---

## 🔐 Credenciales por Defecto

| Recurso            | Usuario       | Contraseña   | Dónde cambiarlo                           |
|--------------------|---------------|--------------|-------------------------------------------|
| **Panel Admin**    | `admin`       | `1234`       | [app.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/app.py) líneas 90-91, constantes `ADMIN_USER` y `ADMIN_PASS` |

> ⚠️ **Importante:** Cambia estas credenciales antes de poner la app en producción. Considera moverlas a variables de entorno o almacenarlas con hash.

---

## 📝 Descripción de Módulos

### [main.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/main.py)
**Punto de entrada.** Inicializa:
1. Base de datos (crea tablas si no existen vía `create_table()`).
2. Datos de prueba (vía `seed()`).
3. Instancia `QApplication`, carga el tema QSS y muestra `MainWindow`.

### [app.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/app.py)
**Lógica principal de la UI.** Contiene:
- `MainWindow` — Ventana principal con `QStackedWidget` (8 páginas).
- `UiWrapper` — Helper para acceder a widgets por nombre desde archivos `.ui`.
- `load_ui()` — Carga archivos `.ui` dinámicamente con `QUiLoader`.
- Flujo del wizard de citas (validaciones, navegación entre páginas, persistencia en `appointment_data`).
- Gestión admin: login, tabs, CRUD de barberos/cortes, confirmación/cancelación de citas.
- Renderizado de tarjetas dinámicas (citas, barberos, cortes).
- Coloreado de calendarios según estados.

### [database.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/database.py)
**Capa de acceso a datos (DAO).** Todas las operaciones CRUD:
- `create_table()` — DDL (CREATE TABLE IF NOT EXISTS).
- **Barberos:** `add_barbero`, `get_barberos`, `update_barbero`, `delete_barbero`.
- **Cortes:** `add_corte`, `get_cortes` (soporta filtrado por barbero + genéricos), `update_corte`, `delete_Corte`, `get_all_cortes_with_barbero`, `delete_corte_by_name_price`.
- **Clientes:** `add_cliente` (upsert por teléfono), `get_client_by_phone`.
- **Citas:** `add_cita` (con validación de solapamiento), `get_cita_by_id`, `get_cita_by_fecha`, `get_cita_by_cliente`, `get_all_citas`, `confirm_cita`, `cancel_cita`, `complete_cita`, `delete_canceled_citas`, `get_available_horarios`.

### [email_sender.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/email_sender.py)
**Notificaciones por correo.**
- Configuración vía variables de entorno `SMTP_*`.
- Plantilla HTML responsive con la marca de la barbería.
- Modo simulado automático si faltan credenciales.

### [seed_data.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/seed_data.py)
**Poblado inicial de datos de prueba.**
- 4 barberos de ejemplo con especialidades.
- 3 cortes genéricos (para todos los barberos).
- 7 cortes específicos asignados a barberos individuales.

### [fix_ui.py](file:///c:/Users/Hp%20Gaming/Documents/proyectos%20en%20Python/CTRLZ-Barbershop/fix_ui.py)
**Script utilitario** para convertir nombres `objectName` a propiedad `cssClass` en archivos `.ui` y reemplazar selectores CSS por ID por selectores de atributo en el QSS. Útil durante el desarrollo para mantener compatibilidad entre Qt Designer y los estilos personalizados.

---

💈 **CTRLZ Barbershop** — Gestiona tu barbería con estilo.
