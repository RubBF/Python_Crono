import time
import random
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from pagina_login import iniciar_sesion
from pagina_identificacion import consultar_rut
from Leer_Excel import cargar_rut

PROGRESO_FILE = "data/progreso.json"
LOG_FILE = "data/logs.txt"

def actualizar_progreso(actual, total):
    """Guarda el progreso en un archivo JSON."""
    progreso = {"completado": actual, "total": total}
    with open(PROGRESO_FILE, "w", encoding="utf-8") as f:
        json.dump(progreso, f, indent=4)

def agregar_log(mensaje):
    """Guarda logs en un archivo de texto."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")

def ejecutar_sesion(usuario_id, rut, modo="headless"):
    """
    Inicia sesión, navega a la página de identificación y consulta un RUT.
    Guarda la captura de pantalla de la consulta.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=(modo == "headless"))
        context = browser.new_context()
        page = context.new_page()

        log_msg = f"🟢 Usuario {usuario_id} iniciando sesión..."
        print(log_msg)
        agregar_log(log_msg)
        iniciar_sesion(page)

        time.sleep(random.uniform(1, 3))

        log_msg = f"🔎 Usuario {usuario_id} consultando RUT: {rut}"
        print(log_msg)
        agregar_log(log_msg)

        resultado = consultar_rut(page, rut)

        log_msg = f"🔴 Usuario {usuario_id} cerrando sesión"
        print(log_msg)
        agregar_log(log_msg)
        context.close()
        browser.close()

        resultado["usuario_id"] = usuario_id
        return resultado

def ejecutar_concurrencia(num_concurrentes=5, modo="headless"):
    """
    Ejecuta múltiples sesiones en paralelo para consultar varios RUTs.
    """
    archivo_ruts = os.path.join("data", "listado_postulaciones.xlsx")
    ruts = cargar_rut(archivo_ruts, cantidad=num_concurrentes)

    resultados = []
    actualizar_progreso(0, len(ruts))  # Inicializar progreso
    open(LOG_FILE, "w").close()  # Limpiar logs previos

    with ThreadPoolExecutor(max_workers=num_concurrentes) as executor:
        futuros = {executor.submit(ejecutar_sesion, usuario_id, rut, modo): (usuario_id, rut)
                   for usuario_id, rut in enumerate(ruts, start=1)}

        for i, futuro in enumerate(as_completed(futuros), start=1):
            try:
                resultado = futuro.result()
                resultados.append(resultado)
                log_msg = f"✅ Consulta finalizada para Usuario {resultado['usuario_id']} - RUT {resultado['rut']}"
                print(log_msg)
                agregar_log(log_msg)
            except Exception as e:
                log_msg = f"❌ Error en un hilo: {e}"
                print(log_msg)
                agregar_log(log_msg)

            actualizar_progreso(i, len(ruts))  # Actualizar progreso en cada consulta

    # Guardar resultados en JSON
    ruta_json = "data/resultados.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    
    print(f"📄 Reporte guardado en '{ruta_json}'")
    agregar_log(f"📄 Reporte guardado en '{ruta_json}'")
