"""
Módulo para envío de correo electrónico con comprobante de cita.
Si no hay credenciales SMTP configuradas, opera en modo simulado (imprime en consola).

Configuración vía variables de entorno:
    SMTP_HOST     — Servidor SMTP (default: smtp.gmail.com)
    SMTP_PORT     — Puerto SMTP (default: 587)
    SMTP_USER     — Usuario/correo para autenticación
    SMTP_PASSWORD  — Contraseña o App Password
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def send_appointment_email(destinatario, datos_cita):
    """
    Enviar correo de confirmación de cita.

    Args:
        destinatario: Dirección de correo del cliente.
        datos_cita: Diccionario con las claves:
            codigo, nombre, barbero, corte, precio, fecha, hora
    
    Returns:
        True si se envió correctamente, False en caso de error.
    """
    subject = f"CTRLZ Barbershop — Confirmación de Cita #{datos_cita['codigo']}"

    html = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #F5F0EB; margin: 0; padding: 30px;">
        <div style="max-width: 520px; margin: 0 auto; background-color: #FFFFFF; border-radius: 16px; padding: 36px; border: 1px solid #E2D8CD;">
            
            <div style="text-align: center; margin-bottom: 24px;">
                <p style="font-size: 36px; margin: 0;">✂️</p>
                <h1 style="color: #1E1E2E; font-size: 22px; margin: 8px 0 4px; letter-spacing: 2px;">CTRLZ BARBERSHOP</h1>
                <p style="color: #6B7280; font-size: 14px; margin: 0;">Confirmación de Cita</p>
            </div>

            <div style="background-color: #FFFBF5; border: 1px solid #E2D8CD; border-radius: 10px; padding: 20px; margin-bottom: 20px; text-align: center;">
                <p style="color: #9CA3AF; font-size: 11px; margin: 0 0 4px; letter-spacing: 1px; text-transform: uppercase;">Código de Cita</p>
                <p style="color: #C8956C; font-size: 28px; font-weight: bold; margin: 0; letter-spacing: 2px;">#{datos_cita['codigo']}</p>
            </div>

            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr>
                    <td style="padding: 10px 0; color: #9CA3AF; width: 120px;">Cliente</td>
                    <td style="padding: 10px 0; color: #1E1E2E; font-weight: 500;">{datos_cita['nombre']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #9CA3AF;">Barbero</td>
                    <td style="padding: 10px 0; color: #1E1E2E; font-weight: 500;">{datos_cita['barbero']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #9CA3AF;">Corte</td>
                    <td style="padding: 10px 0; color: #1E1E2E; font-weight: 500;">{datos_cita['corte']}</td>
                </tr>
                <tr style="border-top: 1px solid #E2D8CD;">
                    <td style="padding: 10px 0; color: #9CA3AF;">Precio</td>
                    <td style="padding: 10px 0; color: #C8956C; font-weight: bold; font-size: 16px;">RD$ {datos_cita['precio']}</td>
                </tr>
                <tr style="border-top: 1px solid #E2D8CD;">
                    <td style="padding: 10px 0; color: #9CA3AF;">Fecha</td>
                    <td style="padding: 10px 0; color: #1E1E2E; font-weight: 500;">{datos_cita['fecha']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #9CA3AF;">Hora</td>
                    <td style="padding: 10px 0; color: #1E1E2E; font-weight: 500;">{datos_cita['hora']}</td>
                </tr>
            </table>

            <hr style="border: none; border-top: 1px solid #E2D8CD; margin: 20px 0;">
            
            <p style="color: #9CA3AF; text-align: center; font-size: 12px; line-height: 1.6; margin: 0;">
                Guarda este código para verificar o consultar tu cita.<br>
                ¡Te esperamos en CTRLZ Barbershop!
            </p>
        </div>
    </body>
    </html>
    """

    # --- Modo simulado si no hay credenciales ---
    if not SMTP_USER or not SMTP_PASSWORD:
        print("=" * 50)
        print("[MODO SIMULADO] Correo de confirmación:")
        print(f"  Para: {destinatario}")
        print(f"  Asunto: {subject}")
        print(f"  Código: #{datos_cita['codigo']}")
        print(f"  Cliente: {datos_cita['nombre']}")
        print(f"  Barbero: {datos_cita['barbero']}")
        print(f"  Corte: {datos_cita['corte']} — RD$ {datos_cita['precio']}")
        print(f"  Fecha: {datos_cita['fecha']} a las {datos_cita['hora']}")
        print("=" * 50)
        return True

    # --- Envío real ---
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = destinatario
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Correo enviado exitosamente a {destinatario}")
        return True

    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
