import pandas as pd
from pathlib import Path

def load_generation_data(gen_path: Path) -> pd.DataFrame:
    """
    Load generation data from a Parquet file.
    """
    df_gen = pd.read_parquet(gen_path)
    df_gen["timestamp"] = pd.to_datetime(df_gen["timestamp"], utc=True)
    df_gen = df_gen.set_index("timestamp")
    return df_gen

def load_lookup_data(lookup_path: Path) -> pd.DataFrame:
    """
    Load lookup data from a CSV file containing plant info.
    """
    df_lookup = pd.read_csv(lookup_path, encoding="latin1")
    expected_cols = ["CENTRAL", "FirstAppearance"]
    for col in expected_cols:
        if col not in df_lookup.columns:
            raise KeyError(
                f"Expected column '{col}' not found in lookup file. "
                f"Found columns: {df_lookup.columns.tolist()}"
            )
    df_lookup["firstappearance"] = pd.to_datetime(df_lookup["FirstAppearance"], utc=True)
    df_lookup["central"] = df_lookup["CENTRAL"].str.lower()
    return df_lookup

def load_and_process_meteo_file(meteo_file: Path, shift_hours: int = 4) -> pd.DataFrame:
    """
    Load meteorological data from a Parquet file, optionally shifting the timestamps
    by 'shift_hours' to correct any offset.

    Args:
        meteo_file (Path): Path to a meteorological Parquet file.
        shift_hours (int): Number of hours to shift the timestamps. 
                           Positive shifts the data forward, negative backward.
    """
    df_meteo = pd.read_parquet(meteo_file)

    # Identify the column containing datetime
    if "date" in df_meteo.columns:
        date_col = "date"
    elif "timestamp" in df_meteo.columns:
        date_col = "timestamp"
    else:
        raise KeyError(f"Neither 'date' nor 'timestamp' column found in file: {meteo_file}")

    # Convert to UTC datetime
    df_meteo[date_col] = pd.to_datetime(df_meteo[date_col], utc=True)

    # Shift by 'shift_hours' if needed
    if shift_hours != 0:
        df_meteo[date_col] = df_meteo[date_col] + pd.Timedelta(hours=shift_hours)

    # Rename to 'date' and set as index
    df_meteo = df_meteo.rename(columns={date_col: "date"})
    df_meteo = df_meteo.set_index("date")
    return df_meteo

def merge_generation_and_meteo(df_gen: pd.DataFrame, df_meteo: pd.DataFrame, plant_name: str) -> pd.DataFrame:
    """
    Merge generation and meteorological data based on their date.
    """
    if plant_name not in df_gen.columns:
        raise KeyError(f"Generation column '{plant_name}' not found in generation data.")
    df_gen_temp = df_gen[[plant_name]].reset_index().rename(columns={"timestamp": "date", plant_name: "generation"})
    df_meteo_temp = df_meteo.reset_index()
    df_model = pd.merge(df_gen_temp, df_meteo_temp, on="date", how="inner")
    return df_model

def update_first_appearance_date(df_model: pd.DataFrame, plant_name: str, df_lookup: pd.DataFrame) -> pd.DataFrame:
    """
    Update the first appearance date in the merged DataFrame using lookup data.
    """
    if plant_name in df_lookup["central"].values:
        lookup_date = df_lookup.loc[df_lookup["central"] == plant_name, "firstappearance"].iloc[0]
        earliest_date = df_model["date"].min()
        df_model.loc[df_model["date"] == earliest_date, "date"] = lookup_date
    else:
        print(f"Warning: Plant '{plant_name}' not found in lookup file.")
    return df_model

def process_all_meteo_files(gen_path: Path, meteo_dir: Path, lookup_path: Path, shift_hours: int = 4) -> dict:
    """
    Process all meteorological files by merging generation data and updating the first appearance date.
    """
    df_gen = load_generation_data(gen_path)
    df_lookup = load_lookup_data(lookup_path)
    merged_dfs = {}

    for meteo_file in meteo_dir.glob("*.parquet"):
        plant_name = meteo_file.stem
        plant_name_formatted = plant_name.replace("_", " ").lower()

        try:
            # Load meteo with a time shift if needed
            df_meteo = load_and_process_meteo_file(meteo_file, shift_hours=shift_hours)

            # Merge generation and meteo
            df_model = merge_generation_and_meteo(df_gen, df_meteo, plant_name_formatted)

            # Update earliest date from lookup
            df_model = update_first_appearance_date(df_model, plant_name_formatted, df_lookup)
            merged_dfs[plant_name_formatted] = df_model

            print(f"Processed '{plant_name_formatted}' - shape: {df_model.shape}")
        except KeyError as e:
            print(f"Skipping file '{meteo_file.name}': {e}")

    return merged_dfs

# -------------------------------------------
# MAIN EXECUTION
# -------------------------------------------
if __name__ == "__main__":
    GEN_PATH = Path(r"C:\Users\ferna\Documents\Desktop\11 - Masters\00 - Master AI\99 - Proyecto Final\energy-generation-prediction-dashboard\data\interim\post_despacho_transformed_data")
    METEO_DIR = Path(r"C:\Users\ferna\Documents\Desktop\11 - Masters\00 - Master AI\99 - Proyecto Final\energy-generation-prediction-dashboard\data\raw\open_meteo_data")
    LOOKUP_PATH = Path(r"C:\Users\ferna\Documents\Desktop\11 - Masters\00 - Master AI\99 - Proyecto Final\energy-generation-prediction-dashboard\data\lookup\central_info.csv") 

    # Adjust shift_hours as needed (+4, -4, etc.)
    merged_data = process_all_meteo_files(GEN_PATH, METEO_DIR, LOOKUP_PATH, shift_hours=-4)

    # Save each merged DataFrame
    output_dir = Path(r"C:\Users\ferna\Documents\Desktop\11 - Masters\00 - Master AI\99 - Proyecto Final\energy-generation-prediction-dashboard\data\interim\meteo_data_with_generation")
    output_dir.mkdir(parents=True, exist_ok=True)

    for plant_name, df in merged_data.items():
        file_name = f"{plant_name.replace(' ', '_')}.parquet"
        output_path = output_dir / file_name
        df.to_parquet(output_path, index=False)
        print(f"Saved data for '{plant_name}' to {output_path}")