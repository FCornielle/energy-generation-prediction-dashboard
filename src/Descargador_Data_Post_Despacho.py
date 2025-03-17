
# Descargador en .parquet datos de generación de manera individual

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time
import sys

def fetch_data_for_date(date_str):
    """
    Realiza la solicitud GET para la fecha indicada, midiendo el tiempo de respuesta.
    Se intenta solo una vez. Imprime el tiempo en segundos que tomó la solicitud y retorna el JSON recibido,
    o None en caso de error.
    """
    url = f"https://apps.oc.org.do/wsOCWebsiteChart/Service.asmx/GetPostDespachoJSon?Fecha={date_str}"
    start_req = time.time()
    response = requests.get(url)
    elapsed = time.time() - start_req
    
    if response.status_code == 200:
        print(f"Datos descargados para {date_str} en {elapsed:.2f} segundos.")
        return response.json()
    else:
        print(f"Error {response.status_code} para la fecha {date_str} después de {elapsed:.2f} segundos.")
        return None

# Crear la carpeta para guardar los archivos si no existe
folder = "generación post despacho"
os.makedirs(folder, exist_ok=True)

# Define el rango de fechas para descargar los datos
start_date = datetime(2024, 7, 7)
end_date = datetime(2025, 3, 9)
print(f'Descargando datos del rango: {start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}')

current_date = start_date
while current_date <= end_date:
    # Asegúrate de usar formato mm/dd/YYYY
    date_str = current_date.strftime("%m/%d/%Y")
    
    print(f"\nProcesando fecha {date_str}...")
    json_data = fetch_data_for_date(date_str)
    
    if json_data and "GetPostDespacho" in json_data:
        data_list = json_data["GetPostDespacho"]
        df = pd.DataFrame(data_list)
        filename = f"post_despacho_{current_date.strftime('%Y%m%d')}.parquet"
        filepath = os.path.join(folder, filename)
        df.to_parquet(filepath, index=False)
        print(f"Datos guardados en '{filepath}'.")
        time.sleep(10)  # Espera 10 segundos antes de la siguiente solicitud
    else:
        print(f"Error al obtener datos para {date_str}. Deteniendo el proceso.")
        sys.exit(1)  # Detiene la ejecución si hay error en la solicitud
    
    current_date += timedelta(days=1)
