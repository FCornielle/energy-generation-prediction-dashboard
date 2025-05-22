import os
import json
import numpy as np
import pandas as pd
import joblib # This is the correct library for .joblib files
# import tensorflow as tf # You mentioned LSTM/Conv1D, so keep these in mind for future use
# import keras
# import lightgbm as lgb
# import xgboost as xgb
from sklearn.preprocessing import StandardScaler # You are using StandardScaler in your pipelines

# Path to the model file - Azure ML mounts the model here
MODEL_DIR = os.environ.get("AZUREML_MODEL_DIR")
MODEL_FILE_NAME = "solar_generation_model.joblib" # <--- THIS IS THE CRUCIAL CHANGE

# Global variable to store the model and potentially the scaler
model = None
scaler = None # Declare a global scaler if you use a pipeline or scale manually

def init():
    """
    This function is called once when the container is started.
    It loads the model and sets up any global resources.
    """
    global model
    global scaler # If your model is part of a pipeline that includes a scaler
    try:
        model_path = os.path.join(MODEL_DIR, MODEL_FILE_NAME)
        
        # Load your model (which is a Pipeline with StandardScaler + RandomForestRegressor)
        model = joblib.load(model_path)
        print(f"Model '{MODEL_FILE_NAME}' loaded successfully from {model_path}")

        # If your model object is a scikit-learn Pipeline that includes the scaler,
        # you don't need a separate 'scaler' global. The pipeline handles it.
        # Verify your 'best_model' object type if you're unsure.
        # From your notebook: `pipeline = Pipeline([("scaler", StandardScaler()), ("rf", RandomForestRegressor(...))])`
        # and `best_model = grid_rf.best_estimator_` which is the fitted pipeline.
        # So, the `model` object itself will handle scaling.

    except Exception as e:
        print(f"Error loading model: {e}")
        # Log the full traceback for more details in Azure ML logs
        import traceback
        traceback.print_exc()
        raise # Re-raise the exception to indicate a critical startup failure

def run(raw_data):
    """
    This function is called for every incoming request.
    It takes the input data, performs inference, and returns the predictions.
    """
    try:
        # Assuming raw_data is a JSON string, e.g., from a REST request
        # The structure should match the features your model was trained on.
        # Your model expects data that would typically come from X_test or X_train
        # which are DataFrames after dropping "generation".
        # So, input should be a list of lists representing rows of features.
        # Example expected input: {"data": [[feature1, feature2, ...], [feature1, feature2, ...]]}
        
        data = json.loads(raw_data)["data"]
        df_input = pd.DataFrame(data)

        # Your model `best_model` (which is `grid_rf.best_estimator_`) is a Pipeline
        # that already includes StandardScaler. So, you don't need to manually scale here.
        predictions = model.predict(df_input)

        # Convert predictions to a JSON serializable format (e.g., list)
        return json.dumps({"predictions": predictions.tolist()})

    except Exception as e:
        error = f"Error during inference: {e}"
        print(error)
        # Log the full traceback for more details in Azure ML logs
        import traceback
        traceback.print_exc()
        # Return error message as JSON
        return json.dumps({"error": error})