import os
import time
import datetime
import pandas as pd

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Variable global para llevar el conteo de llamadas realizadas hoy
calls_today = 0

def get_historical_data(lat, lon, start_date, cutoff_time, HOURLY_VARS, client, max_retries=5):
    """
    Recupera datos históricos desde start_date hasta cutoff_time utilizando el endpoint del archivo.
    """
    global calls_today
    hist_end_date = cutoff_time.strftime("%Y-%m-%d")
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": hist_end_date,
        "hourly": HOURLY_VARS
    }
    retry_count = 0
    hist_df = pd.DataFrame()
    while retry_count <= max_retries:
        try:
            response = client.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)[0]
            calls_today += 1

            hourly = response.Hourly()
            # Construir un índice datetime a partir del rango de tiempo proporcionado por la API
            times = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )

            # Crear un diccionario de datos para cada variable
            data = {"date": times}
            for i, var in enumerate(HOURLY_VARS):
                var_obj = hourly.Variables(i)
                if var_obj:
                    data[var] = var_obj.ValuesAsNumpy()
                else:
                    # Si la variable no está disponible, se rellena con NaN
                    data[var] = [float("nan")] * len(times)

            hist_df = pd.DataFrame(data)
            # Filtrar para incluir solo datos anteriores a cutoff_time
            hist_df = hist_df[hist_df["date"] < cutoff_time]
            break
        except Exception as e:
            message = str(e)
            if "Hourly API request limit exceeded" in message or "Minutely API request limit exceeded" in message:
                now_retry = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
                if "Minutely" in message:
                    next_minute = now_retry.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
                    wait_secs = (next_minute - now_retry).total_seconds() + 5
                    print(f"⚠️ Minutely request limit reached (historical) — waiting {int(wait_secs)} seconds until {next_minute} UTC")
                else:
                    next_hour = now_retry.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
                    wait_secs = (next_hour - now_retry).total_seconds() + 5
                    print(f"⚠️ Hourly request limit reached (historical) — waiting {int(wait_secs/60)} minutes until {next_hour} UTC")
                time.sleep(wait_secs)
                retry_count += 1
            else:
                print(f"❌ Unrecoverable error (historical): {message}")
                break
    return hist_df

def process_plant(row, client, cutoff_time, HOURLY_VARS, output_folder):
    """
    Procesa una planta: recupera los datos históricos y guarda el resultado en un archivo Parquet.
    """
    name = row["CENTRAL"]
    lat, lon = row["Latitud"], row["Longitud"]
    # Convertir la fecha de primera aparición; ajustar el formato si es necesario.
    start_date = pd.to_datetime(row["FirstAppearance"], dayfirst=True).strftime("%Y-%m-%d")
    print(f"▶️ Processing {name}: from {start_date} until cutoff {cutoff_time.isoformat()}")

    hist_df = get_historical_data(lat, lon, start_date, cutoff_time, HOURLY_VARS, client)

    filename = f"{name.lower().replace(' ', '_')}.parquet"
    filepath = os.path.join(output_folder, filename)
    hist_df.to_parquet(filepath, index=False)
    print(f"✅ Saved {filename} for {name}.")
    return hist_df

def main():
    global calls_today
    # Configuración
    CENTRAL_INFO_CSV = r"data\lookup\central_info.csv"
    OUTPUT_FOLDER = r"data\raw\open_meteo_data"
    MAX_DAILY_CALLS = 10000

    # Nueva lista HOURLY_VARS con las variables deseadas
    HOURLY_VARS = [
        "temperature_2m",
        "dew_point_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "surface_pressure",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "et0_fao_evapotranspiration",
        "vapour_pressure_deficit",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "is_day",
        "sunshine_duration",
        "wet_bulb_temperature_2m",
        "boundary_layer_height",
        "shortwave_radiation",
        "diffuse_radiation",
        "global_tilted_irradiance",
        "shortwave_radiation_instant",
        "diffuse_radiation_instant",
        "global_tilted_irradiance_instant",
        "direct_radiation",
        "direct_normal_irradiance",
        "terrestrial_radiation",
        "direct_radiation_instant",
        "direct_normal_irradiance_instant",
        "terrestrial_radiation_instant",
        "pressure_msl"
    ]

        
    PLANTS_OF_INTEREST = [
        "parque solar girasol"
        # Puedes agregar más centrales según sea necesario
    ]

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    cutoff_time = now - datetime.timedelta(hours=26)

    # Configurar el cliente de Open-Meteo
    cache = requests_cache.CachedSession('.cache', expire_after=-1)
    session = retry(cache, retries=3, backoff_factor=0.2)
    client = openmeteo_requests.Client(session=session)

    # Cargar y filtrar la información de centrales desde el CSV
    df = pd.read_csv(CENTRAL_INFO_CSV, encoding="latin1")
    df_filtered = df[df["CENTRAL"].str.lower().isin([p.lower() for p in PLANTS_OF_INTEREST])].copy()

    # Procesar cada central
    for idx, row in df_filtered.iterrows():
        if calls_today >= MAX_DAILY_CALLS:
            print("✅ Daily API call limit reached — stopping execution.")
            break
        process_plant(row, client, cutoff_time, HOURLY_VARS, OUTPUT_FOLDER)

    print("✅ All plants have been processed.")
    print(f"API calls made today: {calls_today}")

if __name__ == "__main__":
    main()
