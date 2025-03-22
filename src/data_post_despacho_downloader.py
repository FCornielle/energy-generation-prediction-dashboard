# Downloader to .parquet for individual generation data

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time
import sys

def fetch_data_for_date(date_str):
    """
    Performs a GET request for the specified date, measuring the response time.
    It only attempts once. Prints the time in seconds that the request took and returns the received JSON,
    or None in case of an error.
    """
    url = f"https://apps.oc.org.do/wsOCWebsiteChart/Service.asmx/GetPostDespachoJSon?Fecha={date_str}"
    start_req = time.time()
    response = requests.get(url)
    elapsed = time.time() - start_req
    
    if response.status_code == 200:
        print(f"Data downloaded for {date_str} in {elapsed:.2f} seconds.")
        return response.json()
    else:
        print(f"Error {response.status_code} for date {date_str} after {elapsed:.2f} seconds.")
        return None

# Create the folder to store the files if it does not exist
folder = r"data\raw\post_despacho_data"
os.makedirs(folder, exist_ok=True)

# Define the date range for data download
start_date = datetime(2025, 3, 16)
end_date = datetime(2025, 3, 19)
print(f"Downloading data for the range: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")

current_date = start_date
while current_date <= end_date:
    # Make sure to use the format mm/dd/YYYY
    date_str = current_date.strftime("%m/%d/%Y")
    
    print(f"\nProcessing date {date_str}...")
    json_data = fetch_data_for_date(date_str)
    
    if json_data and "GetPostDespacho" in json_data:
        data_list = json_data["GetPostDespacho"]
        df = pd.DataFrame(data_list)
        filename = f"post_despacho_{current_date.strftime('%Y%m%d')}.parquet"
        filepath = os.path.join(folder, filename)
        df.to_parquet(filepath, index=False)
        print(f"Data saved in '{filepath}'.")
        time.sleep(10)  # Wait 10 seconds before the next request
    else:
        print(f"Error obtaining data for {date_str}. Stopping the process.")
        sys.exit(1)  # Stop execution if there's an error in the request
    
    current_date += timedelta(days=1)
