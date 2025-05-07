import glob
import pandas as pd
import sys, os
# Folder containing the .parquet files
folder_path = r"data\raw\post_despacho_data"


# Find all .parquet files in the folder
parquet_files = glob.glob(os.path.join(folder_path, "*.parquet"))

if not parquet_files:
    print("No Parquet files were found in the specified folder.")
else:
    # Load each Parquet file and add it to a list
    df_list = []
    for file in parquet_files:
        #print(f"Importing {file}...")
        df_temp = pd.read_parquet(file)
        df_list.append(df_temp)

    # Concatenate all DataFrames into a single one
    df_merged = pd.concat(df_list, ignore_index=True)
    print(f"\nMerged {len(df_list)} DataFrames.")
    print(f"The resulting DataFrame has {df_merged.shape[0]} rows and {df_merged.shape[1]} columns.")

# --- Define Functions ---

import unicodedata
import pandas as pd

def normalize_string(s):
    """
    Converts a string to lowercase and removes accents.
    
    Parameters:
        s (str): The input string.
    
    Returns:
        str: The normalized string.
    """
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return s

def normalize_central_column(df, column="CENTRAL"):
    """
    Normalizes the values in the specified column by converting to lowercase and removing accents.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the column.
        column (str): Column name to normalize (default "CENTRAL").
    
    Returns:
        pd.DataFrame: Updated DataFrame.
    """
    df[column] = df[column].astype(str).apply(normalize_string)
    return df

def format_fecha_column(df, column="FECHA"):
    """
    Converts the specified date column to datetime using '%Y-%m-%dT%H:%M:%S'.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the date column.
        column (str): Column name to format (default "FECHA").
    
    Returns:
        pd.DataFrame: Updated DataFrame.
    """
    df[column] = pd.to_datetime(df[column], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
    return df

def remove_unwanted_units(df, unit_col="CENTRAL"):
    """
    Removes rows from the DataFrame where the unit (in unit_col) is in the exclude list.
    
    Parameters:
        df (pd.DataFrame): DataFrame with the unit column.
        unit_col (str): Name of the unit column (default "CENTRAL").
    
    Returns:
        pd.DataFrame: Updated DataFrame with unwanted units removed.
    """
    exclude_units = [
        "arroyo barril",
        "cayman",
        "dajabon",
        "los mina 1",
        "los mina 2",
        "haina 3",
        "puerto plata 1",
        "puerto plata 2",
        "santo domingo 5",
        "santo domingo 8",
        "timbeque 1",
        "timbeque 2",
        "san pedro vapor"
    ]
    df = df[~df[unit_col].isin(exclude_units)]
    return df

def fill_missing_with_next_available(df, date_col='FECHA', central_col='CENTRAL', max_offset=14):
    """
    Fills missing dates in the DataFrame by finding records from a subsequent date that 
    has the same weekday as the missing date. For each missing date, the function checks
    offsets starting at 7 days up to max_offset days. If a record is found, it is duplicated 
    and its date is set to the missing date.
    
    Parameters:
        df (pd.DataFrame): DataFrame with at least the date_col and central_col.
        date_col (str): Name of the date column (assumed to be datetime).
        central_col (str): Name of the plant column.
        max_offset (int): Maximum number of days offset to check (default is 14).
    
    Returns:
        pd.DataFrame: DataFrame with missing dates filled.
    """
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()
    all_dates = pd.date_range(start=df[date_col].min(), end=df[date_col].max())
    present_dates = pd.to_datetime(df[date_col].unique())
    missing_dates = all_dates.difference(present_dates)
    
    fill_rows = []
    
    for missing_date in missing_dates:
        filled = False
        for offset in range(7, max_offset + 1):
            candidate_date = missing_date + pd.Timedelta(days=offset)
            if candidate_date.weekday() != missing_date.weekday():
                continue
            df_candidate = df[df[date_col] == candidate_date]
            if not df_candidate.empty:
                for _, row in df_candidate.iterrows():
                    new_row = row.copy()
                    new_row[date_col] = missing_date
                    fill_rows.append(new_row)
                filled = True
                break
        if not filled:
            print(f"No matching record found to fill missing date {missing_date.date()}")
    
    if fill_rows:
        df_filled = pd.concat([df, pd.DataFrame(fill_rows)], ignore_index=True)
    else:
        df_filled = df.copy()
    
    df_filled = df_filled.sort_values(by=[central_col, date_col]).reset_index(drop=True)
    return df_filled
def standardize_central_names(df, column="CENTRAL"):
    """
    Standardizes central names by applying a mapping. This function assumes that the values 
    in the specified column are already in lowercase.
    
    Mappings applied:
      - "central hidroelectrica hatillo 2" -> "hatillo 2"
      - "parque fotovoltaico bayahonda (bayasol)" -> "parque fotovoltaico bayasol"
      - "parque fotovoltaico montecristi solar1" -> "parque fotovoltaico montecristi solar 1"
      - "parque eolico los guzmancito 2" -> "parque eolico los guzmancitos 2"
      - "hatillo" -> "hatillo 1"
      - "juancho los cocos 1" -> "los cocos 1"
      - "aes andres xxxxxx" -> "aes andres"
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the central names.
        column (str): Name of the column to standardize (default "CENTRAL").
    
    Returns:
        pd.DataFrame: DataFrame with standardized central names.
    """
    mapping = {
        "central hidroelectrica hatillo 2": "hatillo 2",
        "parque fotovoltaico bayahonda (bayasol)": "parque fotovoltaico bayasol",
        "parque fotovoltaico montecristi solar1": "parque fotovoltaico montecristi solar 1",
        "parque eolico los guzmancito 2": "parque eolico los guzmancitos 2",
        "hatillo": "hatillo 1",
        "juancho los cocos 1": "los cocos 1",
        "aes andres xxxxxx": "aes andres"
    }
    
    df[column] = df[column].replace(mapping)
    return df
def remove_daily_duplicates_by_max_hours(df, date_col="FECHA", unit_col="CENTRAL"):
    """
    Removes duplicate rows for the same unit (central) and date by keeping only the row 
    with the highest sum of hour columns (H1 to H24).
    
    Assumes the date column is already normalized (i.e., time set to midnight).
    
    Parameters:
        df (pd.DataFrame): DataFrame containing at least the columns specified in date_col, 
                           unit_col, and hour columns (H1...H24).
        date_col (str): Name of the date column (default "FECHA").
        unit_col (str): Name of the central column (default "CENTRAL").
    
    Returns:
        pd.DataFrame: DataFrame with duplicates removed, keeping only the row with the maximum 
                      hour sum for each combination of unit and date.
    """
    # Identify hour columns (H1 to H24) present in the DataFrame
    hour_cols = [f"H{i}" for i in range(1, 25) if f"H{i}" in df.columns]
    if not hour_cols:
        print("No hour columns found in the DataFrame.")
        return df
    
    # Calculate the sum of hour columns for each row and add it as a temporary column
    df["hour_sum"] = df[hour_cols].sum(axis=1, skipna=True)
    
    # Group by date and unit, and select the index of the row with the maximum hour_sum for each group
    idx = df.groupby([date_col, unit_col])["hour_sum"].idxmax()
    
    # Retrieve those rows and remove the temporary hour_sum column
    df_unique = df.loc[idx].copy()
    df_unique.drop(columns=["hour_sum"], inplace=True)
    
    return df_unique

def aggregate_unit_groups(df, group_mapping, date_col="FECHA", unit_col="CENTRAL"):
    """
    Aggregates rows for unit groups based on a mapping.
    
    For each group defined in group_mapping (where the key is the unified unit name and the value
    is a list of variants), the function:
      1. Filters rows where unit_col is in the variants.
      2. Groups these rows by the date (date_col) and sums the hourly columns (H1 to H24).
      3. Creates new rows with the unified unit name (the key).
      4. Removes the original rows for these variants from the DataFrame.
      5. Appends the aggregated rows back to the DataFrame.
    
    Parameters:
      df (pd.DataFrame): DataFrame containing at least the date_col, unit_col, and hourly columns (H1 ... H24).
      group_mapping (dict): Dictionary where keys are the unified unit names and values are lists of variants.
      date_col (str): Name of the date column (default "FECHA").
      unit_col (str): Name of the unit column (default "CENTRAL").
    
    Returns:
      pd.DataFrame: DataFrame with aggregated rows for each specified group.
    """
    # Identify hourly columns (H1 to H24) that exist in the DataFrame
    hour_cols = [f"H{i}" for i in range(1, 25) if f"H{i}" in df.columns]
    if not hour_cols:
        print("No hourly columns found in the DataFrame.")
        return df

    # Normalize the date column (set time to midnight)
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()
    
    aggregated_rows = []
    
    # Loop over each group in the mapping
    for unified_unit, variants in group_mapping.items():
        # Filter rows where unit is in the variants list
        mask = df[unit_col].isin(variants)
        df_group = df[mask].copy()
        if df_group.empty:
            continue
        # Group by date and sum the hourly columns
        df_agg = df_group.groupby(date_col, as_index=False)[hour_cols].sum()
        # Set the unit column to the unified unit for all aggregated rows
        df_agg[unit_col] = unified_unit
        
        aggregated_rows.append(df_agg)
    
    # If any aggregated rows were created, combine them
    if aggregated_rows:
        df_aggregated = pd.concat(aggregated_rows, ignore_index=True)
    else:
        df_aggregated = pd.DataFrame(columns=[date_col, unit_col] + hour_cols)
    
    # Remove original rows that belong to any of the variants in the mapping
    all_variants = [variant for variants in group_mapping.values() for variant in variants]
    df_remaining = df[~df[unit_col].isin(all_variants)]
    
    # Combine the remaining rows with the aggregated rows
    df_result = pd.concat([df_remaining, df_aggregated], ignore_index=True)
    
    # Sort by unit and date for clarity
    df_result = df_result.sort_values(by=[unit_col, date_col]).reset_index(drop=True)
    
    return df_result

def aggregate_los_mina(df, date_col="FECHA", unit_col="CENTRAL"):
    """
    Aggregates rows for 'los mina' by processing two groups:
      - Group 1: Sum hourly values from rows with unit in ["los mina 5", "los mina 6", "los mina 7"].
      - Group 2: For rows with unit in ["parque energetico los mina cc parcial", "parque energetico los mina cc total"],
                 select the row with the maximum hour sum (H1 to H24) for each day.
    
    For each day with data in either group, a new aggregated row with unit "los mina" is created,
    with hourly values equal to the sum of Group 1 and Group 2 values.
    
    Parameters:
      df (pd.DataFrame): DataFrame containing at least the date_col, unit_col, and hourly columns (H1 ... H24).
      date_col (str): Name of the date column (assumed to be datetime or will be normalized).
      unit_col (str): Name of the unit/central column.
      
    Returns:
      pd.DataFrame: DataFrame with the original rows for these groups removed and replaced with aggregated rows.
    """
    # Ensure the date column is datetime and normalized (time set to midnight)
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()
    
    # Determine hourly columns (H1 to H24) available in df
    hour_cols = [f"H{i}" for i in range(1, 25) if f"H{i}" in df.columns]
    if not hour_cols:
        print("No hourly columns found.")
        return df
    
    # Define the variant groups
    group1_variants = ["los mina 5", "los mina 6", "los mina 7"]
    group2_variants = ["parque energetico los mina cc parcial", "parque energetico los mina cc total"]
    
    # Filter rows for each group
    df_group1 = df[df[unit_col].isin(group1_variants)].copy()
    df_group2 = df[df[unit_col].isin(group2_variants)].copy()
    
    # Determine all unique dates where either group has data
    dates = pd.to_datetime(pd.concat([df_group1[date_col], df_group2[date_col]]).unique())
    
    aggregated_rows = []
    
    for d in dates:
        # Initialize aggregated hourly values for the day as zeros
        agg_values = {col: 0 for col in hour_cols}
        
        # Group 1 aggregation: Sum rows for the date d if present
        df1_d = df_group1[df_group1[date_col] == d]
        if not df1_d.empty:
            sum_group1 = df1_d[hour_cols].sum()
            for col in hour_cols:
                agg_values[col] += sum_group1[col]
        
        # Group 2 aggregation: For the date d, select the row with maximum hour sum if present
        df2_d = df_group2[df_group2[date_col] == d].copy()  # <-- Make an explicit copy here
        if not df2_d.empty:
            df2_d["hour_sum"] = df2_d[hour_cols].sum(axis=1, skipna=True)
            idx = df2_d["hour_sum"].idxmax()
            max_row = df2_d.loc[idx]
            for col in hour_cols:
                agg_values[col] += max_row[col]
        
        # Create the aggregated row if there was data in either group for the day
        if not (df1_d.empty and df_group2.empty):
            new_row = {date_col: d, unit_col: "los mina"}
            for col in hour_cols:
                new_row[col] = agg_values[col]
            aggregated_rows.append(new_row)
    
    # Create a DataFrame from aggregated rows
    if aggregated_rows:
        df_aggregated = pd.DataFrame(aggregated_rows)
    else:
        df_aggregated = pd.DataFrame(columns=[date_col, unit_col] + hour_cols)
    
    # Remove original rows for both groups from the DataFrame
    df_remaining = df[~df[unit_col].isin(group1_variants + group2_variants)]
    
    # Combine the remaining rows with the new aggregated rows
    df_result = pd.concat([df_remaining, df_aggregated], ignore_index=True)
    
    # Sort by unit and date
    df_result = df_result.sort_values(by=[unit_col, date_col]).reset_index(drop=True)
    
    return df_result

def DB_post_despacho_transformer(df):
    import pandas as pd

    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # 1. Drop unwanted columns
    cols_to_drop = ["GRUPOS", "INDICE", "GRUPO", "EMPRESA"]
    df = df.drop(columns=cols_to_drop, errors="ignore")
    
    # Identify hour columns (H1..H24)
    hour_cols = [col for col in df.columns if col.startswith("H")]
    
    # 2. Melt the DataFrame
    df_melted = df.melt(
        id_vars=["CENTRAL", "FECHA"], 
        value_vars=hour_cols,
        var_name="Hour", 
        value_name="Generation"
    )
    
    # Ensure FECHA is converted to datetime
    df_melted["FECHA"] = pd.to_datetime(df_melted["FECHA"], errors="coerce")
    
    # 3. Convert 'Hour' to integer.
    # Aquí, se toma el número de la hora; si es 24 se tratará aparte.
    df_melted["HourNum"] = df_melted["Hour"].str.lstrip("H").astype(int)
    
    # 4. Crear la columna 'timestamp':
    #    - Si HourNum es 24, se suma un día a FECHA (0:00 del día siguiente)
    #    - De lo contrario, se suma la cantidad de horas indicada a FECHA.
    df_melted["timestamp"] = df_melted.apply(
        lambda row: row["FECHA"] + pd.Timedelta(days=1) if row["HourNum"] == 24 
                    else row["FECHA"] + pd.Timedelta(hours=row["HourNum"]),
        axis=1
    )
    
    # 5. Pivot para que cada CENTRAL sea una columna, usando 'timestamp' como índice
    df_pivot = df_melted.pivot_table(
        index="timestamp", 
        columns="CENTRAL", 
        values="Generation", 
        aggfunc="first"
    )
    
    # Remove the column name (the label "CENTRAL")
    df_pivot.columns.name = None

    # Reset the index so that 'timestamp' becomes a normal column
    df_pivot = df_pivot.reset_index()
    
    return df_pivot


# 1. Normalize the 'CENTRAL' column
df_merged = normalize_central_column(df_merged)

# 2. Format the 'FECHA' column to datetime
df_merged = format_fecha_column(df_merged)

# 3. Remove unwanted units
df_merged = remove_unwanted_units(df_merged, unit_col="CENTRAL")

# 4. Fill missing dates by copying records from the same weekday one week later
df_merged = fill_missing_with_next_available(df_merged, date_col='FECHA', central_col='CENTRAL')

# 5. Standardize central names
df_merged = standardize_central_names(df_merged, column="CENTRAL")

# 6. Remove daily duplicates by keeping the row with the highest hour sum
df_merged = remove_daily_duplicates_by_max_hours(df_merged, date_col="FECHA", unit_col="CENTRAL")

group_mapping = {
    "aes andres": ["aes andres fo", "aes andres gn", "aes andres"],
    "cespm 1": ["cespm 1 fo", "cespm 1 gn", "cespm 1"],
    "cespm 2": ["cespm 2 fo", "cespm 2 gn", "cespm 2"],
    "cespm 3": ["cespm 3 fo", "cespm 3 gn", "cespm 3"],
    "estrella del mar 2": ["estrella del mar 2 cfo", "estrella del mar 2 cgn", "estrella del mar 2 sfo", "estrella del mar 2 sgn"],
    "estrella del mar 3": ["estrella del mar 3 ccp", "estrella del mar 3 cct", "estrella del mar 3 cs", "estrella del mar 3 sgn", "estrella del mar 3"],
    "powership azua": ["powership azua kps 26", "powership azua kps 60", "powership azua"],
    "los origenes": ["los origenes power plant fuel oil", "los origenes power plant gas natural", "los origenes"],
    "quisqueya 1": ["quisqueya 1 fo", "quisqueya 1 gn", "quisqueya 1 san pedro", "quisqueya 1 san pedro fo", 
                     "quisqueya 1 san pedro gn", "quisqueya 1b san pedro", "quisqueya 1b san pedro fo", 
                     "quisqueya 1b san pedro gn", "quisqueya 1"],
    "quisqueya 2": ["quisqueya 2 fo", "quisqueya 2 gn"],
    "san felipe": ["san felipe cc", "san felipe vap", "san felipe"],
    "los cocos 1": ["juancho los cocos 1", "los cocos 1"],
    "parque eolico de matafongo": ['parque eolico de matafongo', 'parque eolico matafongo']
}
# 7. aggregate 
df_merged = aggregate_unit_groups(df_merged, group_mapping, date_col="FECHA", unit_col="CENTRAL")
df_merged = aggregate_los_mina(df_merged, date_col="FECHA", unit_col="CENTRAL")

# 8.Pivot
df_transformed = DB_post_despacho_transformer(df_merged)

# Display the first few rows of the transformed DataFrame
print("Transformed DataFrame (timestamp and plant columns):")
print(df_transformed)

# Folder and filename for the output
output_folder = r"data\interim\post_despacho_transformed_data"
output_filename = "post_despacho_transformed.parquet"

# Construct the full path
output_path = os.path.join(output_folder, output_filename)

# Save df_merged to Parquet (overwriting if it already exists)
df_transformed.to_parquet(output_path, index=False)
print(f"File saved to: {output_path}")