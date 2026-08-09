import sqlite3
import os 

#Fuad, hice esto con ayuda de la IA, obvio, pero traté de entenderlo y dejar comentarios utiles para que
#entiendas como funciona el codigo un poco
DB_NAME = "CTRLZ_BarberShop.db"

def connect_DB():
    """Establecer conexión con la base de datos"""
    return sqlite3.connect(DB_NAME)

def create_table():
    """Crear tabla en la base de datos si no existe"""
    conn = connect_DB()
    cursor = conn.cursor()

    # Crear tabla de barberos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barberos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            especialidad TEXT NOT NULL
        )
    """)
    #Crear tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefono TEXT NOT NULL UNIQUE
        )
    """)
    
    #Crear tabla de corte
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barbero_id INTEGER,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY (barbero_id) REFERENCES barberos(id)
        )
    """)

    #Crear tabla de citas 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            barbero_id INTEGER NOT NULL,
            corte_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'confirmada', 'cancelada')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (barbero_id) REFERENCES barberos(id),
            FOREIGN KEY (corte_id) REFERENCES cortes(id) 
        )
    """)

    #Manejar errores
    try:
        conn.commit()
        print("Tablas creadas con éxito")
        conn.close()
    except sqlite3.Error as e:
        print(f"Error al crear la tabla: {e}")
        conn.rollback()
    conn.close()

# Ejecutar la creación de tablas al importar el módulo
if __name__ == "__main__":
    create_table()


#Operaciones CRUD

def add_barbero(nombre, email, especialidad):
    """Registrar un barbero"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO barberos (nombre, email, especialidad) VALUES (?, ?, ?)", (nombre, email, especialidad))    
        conn.commit()
        id_barbero = cursor.lastrowid
        print(f"Barbero {nombre} registrado con éxito, ID: {id_barbero}")
        conn.close()
        return id_barbero
    except sqlite3.Error as e:
        print(f"Error al registrar el barbero: {e}")
        conn.rollback()
        conn.close()
        return None

def get_barberos():
    """Obtener todos los barberos"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM barberos")
        barberos = cursor.fetchall()
        conn.close()
        return barberos # Lista de tuplas: [(1, 'Juan', 'juan@ejemplo.com', 'Corte Clásico'), ...]
    except sqlite3.Error as e:
        print(f"Error al obtener los barberos: {e}")
        conn.close()
        return []

def update_barbero(id_barbero, nombre, email, especialidad):
    """Actualizar datos de un barbero"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE barberos SET nombre=?, email=?, especialidad=? WHERE id=?", (nombre, email, especialidad, id_barbero))
        conn.commit()
        actualizados = cursor.rowcount # Número de filas actualizadas
        conn.close()
        return actualizados > 0 # True si se actualizó al menos una fila, False si no
    except sqlite3.Error as e:
        print(f"Error al actualizar el barbero: {e}")
        conn.rollback()
        conn.close()
        return None

def delete_barbero(id_barbero):
    """Eliminar un barbero"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM barberos WHERE id=?", (id_barbero,))
        conn.commit()
        eliminados = cursor.rowcount # Número de filas eliminadas
        conn.close()
        return eliminados > 0 # True si se eliminó al menos una fila, False si no
    except sqlite3.Error as e:
        print(f"Error al eliminar el barbero: {e}")
        conn.rollback()
        conn.close()
        return None

def add_corte(nombre, precio, barbero_id=None):
    """Añadir un nuevo tipo de corte"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cortes (nombre, precio, barbero_id) VALUES (?, ?, ?)", (nombre, precio, barbero_id))
        conn.commit()
        id_corte = cursor.lastrowid
        print(f"Corte {nombre} registrado con éxito, ID: {id_corte}")
        conn.close()
        return id_corte
    except sqlite3.Error as e:
        print(f"Error al registrar el corte: {e}")
        conn.rollback()
        conn.close()
        return None

def get_cortes(barbero_id=None):
    """Obtener todos los cortes o los cortes de un barbero específico"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        if barbero_id:
            cursor.execute("SELECT id, nombre, precio FROM cortes WHERE barbero_id = ? OR barbero_id IS NULL", (barbero_id,))
        else:
            cursor.execute("SELECT id, nombre, precio FROM cortes")
        cortes = cursor.fetchall()
        conn.close()
        return cortes  # Lista de tuplas: [(1, 'Corte Clásico', 100.0), ...]
    except sqlite3.Error as e:
        print(f"Error al obtener los cortes: {e}")
        conn.close()
        return []

def update_corte(id_corte, nombre, precio):
    """Actualizar datos de un corte"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE cortes SET nombre=?, precio=? WHERE id=?", (nombre, float(precio), id_corte))
        conn.commit()
        actualizados = cursor.rowcount # Número de filas actualizadas
        conn.close()
        return actualizados > 0 # True si se actualizó al menos una fila, False si no
    except sqlite3.Error as e:
        print(f"Error al actualizar el corte: {e}")
        conn.rollback()
        conn.close()
        return None

def delete_Corte(id_corte):
    """Eliminar un corte"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cortes WHERE id=?", (id_corte,))
        conn.commit()
        eliminados = cursor.rowcount # Número de filas eliminadas
        conn.close()
        return eliminados > 0 # True si se eliminó al menos una fila, False si no
    except sqlite3.Error as e:
        print(f"Error al eliminar el corte: {e}")
        conn.rollback()
        conn.close()
        return None

def add_cliente(nombre, email, telefono): 
    """Registrar un cliente o obtener su ID si ya existe por número de teléfono"""
    conn = connect_DB()
    cursor = conn.cursor()

    # Verificar si ya existe un cliente con el mismo número de teléfono
    cursor.execute("SELECT id FROM clientes WHERE telefono=?", (telefono,))
    cliente_id = cursor.fetchone()
    if cliente_id:
        conn.close()
        return cliente_id[0]  # El cliente ya existe, devolver su ID


#Si no existe, registrar el cliente
    try:
        cursor.execute("INSERT INTO clientes (nombre, email, telefono) VALUES (?, ?, ?)", (nombre, email, telefono))    
        conn.commit()
        id_cliente = cursor.lastrowid
        print(f"Cliente {nombre} registrado con éxito, ID: {id_cliente}")
        conn.close()
        return id_cliente
    except sqlite3.Error as e:
        print(f"Error al registrar el cliente: {e}")
        conn.rollback()
        conn.close()
        return None

def get_client_by_phone(telefono):
    """Obtener el ID de un cliente por número de teléfono"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM clientes WHERE telefono=?", (telefono,))
        cliente_id = cursor.fetchone()
        if cliente_id:
            conn.close()
            return cliente_id[0]  # Devolver el ID del cliente
        else:
            return None  # El cliente no existe
    except sqlite3.Error as e:
        print(f"Error al obtener el cliente: {e}")
        conn.close()
        return None

def add_cita(id_cliente, id_barbero, id_corte, fecha, hora):
    """Registrar una cita en la base de datos"""
    conn = connect_DB()
    cursor = conn.cursor()

    #verificar si ya hay cita con ese barbero en esa fecha y hora
    cursor.execute(
        "SELECT id_cita FROM citas WHERE barbero_id = ? AND fecha = ? AND hora = ? AND estado != 'cancelada'",
        (id_barbero, fecha, hora)
    )
    if cursor.fetchone():
        print(f"Barbero {id_barbero} ya tiene una cita en {fecha} a las {hora}")
        conn.close()
        return False, "El barbero ya tiene una cita en ese horario"  # Ya hay una cita en esa fecha y hora, devolver False y mensaje
    
#Si no hay cita, guardar la nueva
    try:
        # Insertar la nueva cita con estado 'pendiente' por defecto
        cursor.execute("INSERT INTO citas (cliente_id, barbero_id, corte_id, fecha, hora, estado) VALUES (?, ?, ?, ?, ?, 'pendiente')", (id_cliente, id_barbero, id_corte, fecha, hora))    
        conn.commit()
        id_cita = cursor.lastrowid
        print(f"Cita {id_cita} registrada con éxito para el barbero {id_barbero} en {fecha} a las {hora}")
        conn.close()
        return True, id_cita
    except sqlite3.Error as e:
        print(f"Error al guardar la cita: {e}")
        conn.rollback()
        conn.close()
        return False, str(e)

def get_cita_by_cliente(id_cliente):
    """Obtener todas las citas de un cliente con detalle"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT c.id_cita, b.nombre as barbero, cr.nombre as corte, c.fecha, c.hora, c.estado, cr.precio FROM citas c JOIN barberos b ON c.barbero_id = b.id JOIN cortes cr ON c.corte_id = cr.id WHERE c.cliente_id = ? ORDER BY c.fecha DESC, c.hora DESC", (id_cliente,))
        citas = cursor.fetchall()
        conn.close()
        return citas
    except sqlite3.Error as e:
        print(f"Error al obtener las citas: {e}")
        conn.close()
        return []

def get_cita_by_fecha(fecha):
    """Obtener todas las citas en una fecha específica con detalle (Admin)"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT c.id_cita, cl.nombre as cliente, b.nombre as barbero, cr.nombre as corte, c.fecha, c.hora, c.estado, cr.precio FROM citas c JOIN clientes cl ON c.cliente_id = cl.id JOIN barberos b ON c.barbero_id = b.id JOIN cortes cr ON c.corte_id = cr.id WHERE c.fecha = ? ORDER BY c.hora DESC", (fecha,))
        citas = cursor.fetchall()
        conn.close()
        return citas
    except sqlite3.Error as e:
        print(f"Error al obtener las citas: {e}")
        conn.close()
        return []

def cancel_cita(id_cita):
    """Cancelar una cita por ID"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE citas SET estado = 'cancelada' WHERE id_cita=?", (id_cita,))
        conn.commit()
        eliminados = cursor.rowcount # Número de filas canceladas
        conn.close()
        return True, f"Cita {id_cita} cancelada con éxito" if eliminados > 0 else f"Cita {id_cita} no encontrada" # True si se canceló al menos una fila, False si no
    except sqlite3.Error as e:
        print(f"Error al cancelar la cita: {e}")
        conn.rollback()
        conn.close()
        return False, str(e)

def complete_cita(id_cita):
    """Completar una cita por ID"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        # Verificar si la cita está pendiente
        cursor.execute("SELECT estado FROM citas WHERE id_cita=?", (id_cita,))
        estado = cursor.fetchone()
        if not estado or estado[0] != 'pendiente':
            conn.close()
            return False, "Solo se puede completar citas pendientes"
        
        # Actualizar el estado a completada
        cursor.execute("UPDATE citas SET estado = 'completada' WHERE id_cita=?", (id_cita,))
        conn.commit()
        eliminados = cursor.rowcount # Número de filas completadas
        conn.close()
        return True, f"Cita {id_cita} completada con éxito" if eliminados > 0 else f"Cita {id_cita} no encontrada" # True si se completó al menos una fila, False si no
    except sqlite3.Error as e:
        print(f"Error al completar la cita: {e}")
        conn.rollback()
        conn.close()
        return False, str(e)

def get_available_horarios(id_barbero, fecha):
    """Obtener los horarios disponibles para un barbero en una fecha específica"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT hora FROM citas WHERE barbero_id = ? AND fecha = ? AND estado = 'pendiente'", (id_barbero, fecha))
        horarios = cursor.fetchall()
        conn.close()
        return [hora[0] for hora in horarios]  # Convertir tuplas a lista de strings
    except sqlite3.Error as e:
        print(f"Error al obtener los horarios disponibles: {e}")
        conn.close()
        return []

def get_cita_by_id(id_cita):
    """Obtener detalle de una cita específica por su ID"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT c.id_cita, cl.nombre as cliente, b.nombre as barbero, cr.nombre as corte, c.fecha, c.hora, c.estado, cr.precio FROM citas c JOIN clientes cl ON c.cliente_id = cl.id JOIN barberos b ON c.barbero_id = b.id JOIN cortes cr ON c.corte_id = cr.id WHERE c.id_cita = ?", (id_cita,))
        cita = cursor.fetchone()
        conn.close()
        return cita
    except sqlite3.Error as e:
        print(f"Error al obtener la cita: {e}")
        conn.close()
        return None

def get_all_citas():
    """Obtener todas las citas con detalle completo (Admin)"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT c.id_cita, cl.nombre as cliente, b.nombre as barbero, 
                          cr.nombre as corte, c.fecha, c.hora, c.estado, cr.precio 
                          FROM citas c 
                          JOIN clientes cl ON c.cliente_id = cl.id 
                          JOIN barberos b ON c.barbero_id = b.id 
                          JOIN cortes cr ON c.corte_id = cr.id 
                          ORDER BY c.fecha DESC, c.hora ASC""")
        citas = cursor.fetchall()
        conn.close()
        return citas
    except sqlite3.Error as e:
        print(f"Error al obtener las citas: {e}")
        conn.close()
        return []

def confirm_cita(id_cita):
    """Confirmar una cita pendiente (Admin)"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT estado FROM citas WHERE id_cita=?", (id_cita,))
        estado = cursor.fetchone()
        if not estado or estado[0] != 'pendiente':
            conn.close()
            return False, "Solo se puede confirmar citas pendientes"
        cursor.execute("UPDATE citas SET estado = 'confirmada' WHERE id_cita=?", (id_cita,))
        conn.commit()
        actualizados = cursor.rowcount
        conn.close()
        if actualizados > 0:
            return True, f"Cita {id_cita} confirmada con éxito"
        return False, f"Cita {id_cita} no encontrada"
    except sqlite3.Error as e:
        print(f"Error al confirmar la cita: {e}")
        conn.rollback()
        conn.close()
        return False, str(e)

def get_all_cortes_with_barbero():
    """Obtener todos los cortes con el nombre del barbero asociado"""
    conn = connect_DB()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT c.id, c.nombre, c.precio, 
                          COALESCE(b.nombre, 'Genérico') as barbero
                          FROM cortes c 
                          LEFT JOIN barberos b ON c.barbero_id = b.id 
                          ORDER BY c.id""")
        cortes = cursor.fetchall()
        conn.close()
        return cortes
    except sqlite3.Error as e:
        print(f"Error al obtener los cortes: {e}")
        conn.close()
        return []