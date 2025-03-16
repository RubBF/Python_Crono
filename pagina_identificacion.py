from playwright.sync_api import Page
import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

URL_IDENTIFICACION = os.getenv("URL_IDENTIFICACION", "https://caep.cronodemo.cl/inicio.aspx")

def consultar_rut(page: Page, rut: str):
    """
    Navega a la página de Identificación General y consulta un RUT.
    Guarda una captura de pantalla como evidencia.
    """
    print("🔵 Navegando a la página principal...")
    page.goto(URL_IDENTIFICACION)
    
    # Esperar que la página cargue completamente
    page.wait_for_load_state("networkidle")

    try:
        print("📂 Haciendo scroll hasta el menú 'Cliente'...")
        page.locator("div#leftPanel").scroll_into_view_if_needed()

        print("📂 Forzando apertura del menú 'Cliente' con JavaScript...")
        page.evaluate('document.querySelector("div#leftPanel > ol > li > label").click()')

        # Esperar a que el submenú esté disponible
        print("⏳ Esperando que el submenú 'Identificación General' esté visible...")
        page.wait_for_selector("div#leftPanel > ol > li > ol > li > a", timeout=6000)

        print("📌 Seleccionando 'Identificación General'...")
        page.click("div#leftPanel > ol > li > ol > li > a")

        # Esperar a que aparezca el iframe después de la navegación
        print("⏳ Esperando que se cargue el iframe 'ifr_contenido'...")
        page.wait_for_selector("iframe#ifr_contenido", timeout=60000)

        # Acceder al primer iframe
        frame = page.frame(name="ifr_contenido")
        if not frame:
            raise Exception("❌ No se encontró el iframe 'ifr_contenido' después de la navegación.")

        # Verificar si hay un iframe adicional dentro
        sub_frame_locator = frame.locator("iframe#solapa_content")
        if sub_frame_locator.count() > 0:
            print("📌 Se detectó un iframe interno, accediendo a 'solapa_content'...")
            frame = frame.frame(name="solapa_content")

        # Esperar a que el campo del RUT esté disponible dentro del iframe correcto
        print("🔎 Buscando campo de RUT en el formulario...")
        input_rut = frame.wait_for_selector("input#rut", timeout=60000)

        print(f"✍️ Ingresando RUT: {rut}")
        input_rut.fill(rut)

        # Hacer clic en el botón de consulta
        print("🔍 Consultando RUT...")
        frame.click("a#btn_consultar")

        # Esperar la carga de los resultados
        frame.wait_for_timeout(5000)

        # Guardar evidencia correctamente desde el iframe
        print("📸 Tomando captura de pantalla...")
        screenshot_path = f"data/evidencias/rut_{rut}.png"
        os.makedirs("data/evidencias", exist_ok=True)
        frame.locator("body").screenshot(path=screenshot_path)  # 🚀 FIX AQUÍ 🚀
        print(f"✅ Captura guardada en {screenshot_path}")

        return {"rut": rut, "status": "success", "evidencia": screenshot_path}

    except Exception as e:
        print(f"❌ Error consultando RUT {rut}: {e}")
        return {"rut": rut, "status": "error", "error": str(e)}
