import time
import random
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from pagina_login import iniciar_sesion
from pagina_identificacion import consultar_rut
from Leer_Excel import cargar_rut

# Número de sesiones concurrentes
NUM_CONCURRENTES = 2

def ejecutar_sesion(usuario_id, rut):
    """
    Inicia sesión, navega a la página de identificación y consulta un RUT.
    Guarda la captura de pantalla de la consulta.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"🟢 Usuario {usuario_id} iniciando sesión...")
        iniciar_sesion(page)

        time.sleep(random.uniform(1, 3))

        print(f"🔎 Usuario {usuario_id} consultando RUT: {rut}")
        resultado = consultar_rut(page, rut)

        print(f"🔴 Usuario {usuario_id} cerrando sesión")
        context.close()
        browser.close()

        resultado["usuario_id"] = usuario_id
        return resultado

def ejecutar_concurrencia():
    """
    Ejecuta múltiples sesiones en paralelo para consultar varios RUTs.
    Guarda los resultados en un archivo JSON.
    """
    archivo_ruts = os.path.join("data", "listado_postulaciones.xlsx")
    ruts = cargar_rut(archivo_ruts, cantidad=NUM_CONCURRENTES)

    resultados = []

    with ThreadPoolExecutor(max_workers=NUM_CONCURRENTES) as executor:
        futuros = {executor.submit(ejecutar_sesion, usuario_id, rut): (usuario_id, rut)
                   for usuario_id, rut in enumerate(ruts, start=1)}

        for futuro in as_completed(futuros):
            try:
                resultado = futuro.result()
                resultados.append(resultado)
                print(f"✅ Consulta finalizada para Usuario {resultado['usuario_id']} - RUT {resultado['rut']}")
            except Exception as e:
                print(f"❌ Error en un hilo: {e}")

    # Guardar resultados en JSON
    ruta_json = "data/resultados.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    print(f"📄 Reporte guardado en '{ruta_json}'")

if __name__ == "__main__":
    ejecutar_concurrencia()
