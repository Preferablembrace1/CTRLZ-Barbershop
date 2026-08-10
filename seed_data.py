"""
Módulo para poblar la base de datos con datos de prueba.
Se ejecuta automáticamente al iniciar la app si la BD está vacía.
"""
from database import add_barbero, add_corte, get_barberos, get_cortes


def seed():
    """Poblar la base de datos con datos de prueba si está vacía."""

    # Sembrar barberos de prueba
    if not get_barberos():
        barberos = [
            ("Carlos Rodriguez", "chino@ctrlz.com", "Cortes clásicos y degradados"),
            ("Miguel 'El Tigre' Duran", "tigre@ctrlz.com", "Diseños y líneas"),
            ("José Antonio Cabral", "yordy@ctrlz.com", "Barba y afeitado"),
            ("Rafael Acosta", "flaco@ctrlz.com", "Cortes modernos"),
        ]
        for nombre, email, especialidad in barberos:
            add_barbero(nombre, email, especialidad)
        print("Barberos de prueba insertados.")

    # Sembrar cortes de prueba
    if not get_cortes():
        # Cortes genéricos (sin barbero_id)
        genericos = [
            ("Corte Clásico", 300),
            ("Degradado (Fade)", 400),
            ("Corte Infantil", 250),
        ]
        for nombre, precio in genericos:
            add_corte(nombre, precio)
            
        # Cortes específicos por barbero (1: Chino, 2: Tigre, 3: Yordy, 4: Flaco)
        especificos = [
            ("Corte con barba + mascarilla de puntos negros", 1000, 1), # Chino
            ("Diseño con Líneas (Tribal)", 600, 2), # Tigre
            ("Barba", 300, 3), # Yordy
            ("Cerquillo", 300, 3),
            ("Cerquillo + barba", 400, 3),
            ("Cerquillo + barba + taper (blowout)", 500, 3),
            ("Corte Moderno Asimétrico", 700, 4), # Flaco
        ]
        for nombre, precio, b_id in especificos:
            add_corte(nombre, precio, barbero_id=b_id)
            
        print("Cortes de prueba insertados.")


if __name__ == "__main__":
    from database import create_table
    create_table()
    seed()
    print("Datos de prueba sembrados correctamente.")
