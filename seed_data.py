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
            ("Carlos 'El Chino'", "chino@ctrlz.com", "Cortes clásicos y degradados"),
            ("Miguel 'El Tigre'", "tigre@ctrlz.com", "Diseños y líneas"),
            ("José 'Yordy'", "yordy@ctrlz.com", "Barba y afeitado"),
            ("Rafael 'El Flaco'", "flaco@ctrlz.com", "Cortes modernos"),
        ]
        for nombre, email, especialidad in barberos:
            add_barbero(nombre, email, especialidad)
        print("Barberos de prueba insertados.")

    # Sembrar cortes de prueba
    if not get_cortes():
        cortes = [
            ("Corte Clásico", 300),
            ("Degradado (Fade)", 400),
            ("Corte + Barba", 500),
            ("Diseño con Líneas", 600),
            ("Afeitado Completo", 350),
            ("Corte Infantil", 250),
        ]
        for nombre, precio in cortes:
            add_corte(nombre, precio)
        print("Cortes de prueba insertados.")


if __name__ == "__main__":
    from database import create_table
    create_table()
    seed()
    print("Datos de prueba sembrados correctamente.")
