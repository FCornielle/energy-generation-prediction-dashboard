import joblib
import json
import numpy as np
from azureml.core.model import Model

def init():
    global model
    model_path = Model.get_model_path("solar-generation-model")
    model = joblib.load(model_path)

def run(raw_data):
    data = json.loads(raw_data)
    X = np.array(data["inputs"])
    preds = model.predict(X)
    return {"predictions": preds.tolist()}
