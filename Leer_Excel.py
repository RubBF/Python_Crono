import pandas as pd
import random
import os

def cargar_rut(archivo, cantidad=10):
    """
    Carga y procesa un archivo Excel con RUTs.
    Devuelve una lista de RUTs únicos sin duplicados.
    """
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo {archivo} no existe.")

    ext = os.path.splitext(archivo)[-1].lower()
    if ext != ".xlsx":
        raise ValueError("Formato de archivo no soportado. Usa Excel (.xlsx).")

    df = pd.read_excel(archivo)
    
    if "Rut" not in df.columns:
        raise KeyError("El archivo Excel no contiene una columna llamada 'Rut'.")

    df = df.drop_duplicates(subset=["Rut"], keep="first")
    
    # Seleccionar RUTs al azar
    ruts_seleccionados = random.sample(df["Rut"].tolist(), min(cantidad, len(df)))
    
    return ruts_seleccionados

if __name__ == "__main__":
    ruta_archivo = os.path.join("data", "listado_postulaciones.xlsx")
    try:
        ruts = cargar_rut(ruta_archivo, cantidad=10)
        print("✅ RUTs seleccionados:", ruts)
    except Exception as e:
        print(f"❌ Error: {e}")
