from playwright.sync_api import Page
import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

URL_LOGIN = os.getenv("URL_LOGIN", "https://caep.cronodemo.cl/login.aspx")
USUARIO = os.getenv("USUARIO", "rubenb")
PASSWORD = os.getenv("PASSWORD", "p0w3r3mm4")

def iniciar_sesion(page: Page):
    """
    Automatiza el inicio de sesión en la web de CRONO.
    """
    print("🔵 Navegando a la página de login...")
    page.goto(URL_LOGIN)

    print("✍️ Rellenando usuario y contraseña...")
    page.fill("input[name='LoginUser$UserName']", USUARIO)
    page.fill("input[name='LoginUser$Password']", PASSWORD)

    print("🔓 Iniciando sesión...")
    page.click("input[name='LoginUser$LoginButton']")

    # Esperar a que la página cargue después del login
    page.wait_for_load_state("networkidle")
    print("✅ Sesión iniciada correctamente.")

    return page
