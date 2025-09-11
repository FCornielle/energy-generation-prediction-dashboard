# 🧪 Energy Generation Prediction Dashboard

This repository contains the **complete data science pipeline** for predicting solar energy generation. The project follows MLops best practices and is designed to deploy the final model in **Azure Functions**.

## 🎯 Main Objective

Develop a machine learning model that predicts solar energy generation based on:
- **Meteorological data** (temperature, radiation, humidity, etc.)
- **Historical generation data** (post-despacho 2013)
- **Temporal features** (hour, day, month, seasonality)

## 📊 Project Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🧪 DATA SCIENCE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   📡 APIs       │    │   🗄️ Data       │    │   🔧 Pipeline   │
│                 │    │   Historical    │    │   Processing    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Open-Meteo    │    │ • Post-Despacho │    │ • Download      │
│ • Forecast API  │    │ • Since 2013    │    │ • Cleaning      │
│ • 30 variables  │    │ • Real          │    │ • Transformation│
│ • 2 days ahead  │    │   generation    │    │ • Merging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           📊 PROCESSED DATA                               │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│   📁 raw/       │   📁 interim/   │  📁 processed/  │   📁 lookup/        │
│                 │                 │                 │                       │
│ • Raw data      │ • In process    │ • Ready for     │ • Metadata           │
│ • Unfiltered    │ • Partially     │   modeling      │ • References         │
│ • Direct APIs   │   cleaned       │ • Features      │ • Solar plants       │
└─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🔬 FEATURE ENGINEERING                              │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│ ⏰ Temporal     │   📈 Lags       │   📊 Rolling    │   🔄 Differences   │
│                 │                 │   Windows       │                     │
│ • hora_sin/cos  │ • Lagged        │ • Moving        │ • Non-stationary  │
│ • dow_sin/cos   │   variables     │   averages      │   variables        │
│ • month_sin/cos │ • Best lag      │ • 3h, 6h, 24h  │ • Diff(1)         │
│ • Cyclical      │   found         │ • Descriptive   │ • Stationarity     │
│   encoding      │ • Correlation   │   statistics    │                     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🤖 ML MODELING                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   📓 Notebooks  │   🔧 Feature    │   🎯 Trained    │   📈 Evaluation    │
│                 │   Engineer      │   Model         │                     │
│ • Exploratory   │ • SolarFeature  │ • RandomForest  │ • RMSE, MAE        │
│ • Feature Eng.  │   Engineer      │ • XGBoost       │ • R², MAPE         │
│ • Model Search  │ • Pipeline      │ • LightGBM      │ • TimeSeriesSplit  │
│ • Consumption   │ • Preprocessing │ • Ensemble      │ • Walk-forward     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        💾 SERIALIZED MODELS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│   📁 models/                                                              │
│                                                                           │
│ • solar_feature_engineer.joblib (13KB)                                   │
│   └─ Preprocessing pipeline                                               │
│                                                                           │
│ • solar_generation_model.joblib (44MB)                                   │
│   └─ Final prediction model                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
                         🚀 AZURE FUNCTIONS PREPARATION                     
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
    📄 function_     📁 utils/         📄 require-      🔧 Triggers      
│   app.py        │                 │   ments.txt     │                     │
│                 │                 │                 │                     │
│ • HTTP Endpoint │ • data_processor│ • Minimal       │ • HTTP Request      │
│ • Predict API   │ • feature_eng.  │   dependencies  │ • Timer (cron)      │
│ • Error handling│ • Validation    │ • joblib        │ • Blob Storage      │
│ • Logging       │ • Cache         │ • pandas        │ • Event Hub         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
                           📊 POWER BI DASHBOARD                           
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ • Prediction visualization                                                │
│ • Real-time metrics                                                       │
│ • Alerts and notifications                                                │
│ • Report export                                                           │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## 📁 Detailed Project Structure

```
energy-generation-prediction-dashboard/
├── 📄 README.md                           # Project overview
├── 📄 requirements.txt                     # Python dependencies (93 lines)
├── 📄 .gitignore                          # Files and folders to ignore
│
├── 📊 data/                               # Project data
│   ├── 📁 raw/                            # Original data (unprocessed)
│   │   └── 📁 post_despacho_data/         # Post-despacho data (2013)
│   │       └── [+4,628 .parquet files]   # Daily data from 2013
│   └── 📁 lookup/                         # Reference data
│       ├── central_info.csv               # Solar plant information
│       └── meteo_variables.csv           # Meteorological variables
│
├── 🔧 src/                                # Main source code
│   ├── 📄 01 - data_post_despacho_downloader.py    # Post-despacho data downloader
│   ├── 📄 02 - DB_post_despacho_transform.py       # Post-despacho data transformation
│   ├── 📄 03 - open_meteo_history_plant_data.py    # Historical meteorological data
│   ├── 📄 04 - open_meteo_post_despacho_merger.py  # Meteorological and post-despacho data merging
│   └── 📄 feature_engineer.py                      # Feature engineering
│
├── 📓 notebooks/                          # Jupyter analysis notebooks
│   ├── 📄 Exploratory analysis.ipynb      # Initial exploratory analysis
│   ├── 📄 Feature Engineering.ipynb       # Feature engineering
│   ├── 📄 Model Builder Search.ipynb      # Model search and construction
│   └── 📄 Model Consumption.ipynb         # Model consumption and evaluation
│
├── 🤖 models/                             # Trained models
│   ├── 📄 solar_feature_engineer.joblib   # Feature preprocessor (13KB)
│   └── 📄 solar_generation_model.joblib   # Generation prediction model (44MB)
│
├── 📈 power_bi/                           # Power BI files
│   └── 📄 energy-generation-prediction-dashboard.pbix  # Main dashboard
│
└── 📚 docs/                               # Project documentation
    ├── 📄 ARQUITECTURA_DIAGRAMA.md        # Architecture diagram
    ├── 📄 ESTRUCTURA_CIENCIA_DATOS.md    # Detailed technical documentation
    └── 📄 Erros in Post-Despacho DB.txt   # Errors found in the database
```

## 🔬 Data Science Components

### 1. **Feature Engineering (`src/feature_engineer.py`)**

The `SolarFeatureEngineer` class implements a complete preprocessing pipeline:

```python
class SolarFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, target='generation', max_lag=24, 
                 roll_windows=None, log_transform_cols=None):
        # Preprocessor configuration
```

**Generated features:**
- **⏰ Temporal**: hour, day, month (with cyclical encoding)
- **📈 Lags**: lagged values of meteorological variables
- **📊 Rolling windows**: moving averages (3h, 6h, 24h)
- **🔄 Differences**: for non-stationary variables
- **📈 Logarithmic transformations**: for radiation variables

### 2. **Processing Pipeline (`src/`)**

The pipeline follows a sequential flow:

```python
# 1. Data download
01 - data_post_despacho_downloader.py
    ↓
# 2. Transformation and cleaning
02 - DB_post_despacho_transform.py
    ↓
# 3. Meteorological data acquisition
03 - open_meteo_history_plant_data.py
    ↓
# 4. Data merging
04 - open_meteo_post_despacho_merger.py
    ↓
# 5. Feature engineering
feature_engineer.py
```

### 3. **Exploratory Analysis (`notebooks/`)**

- **`Exploratory analysis.ipynb`**: Initial data analysis
- **`Feature Engineering.ipynb`**: Feature development
- **`Model Builder Search.ipynb`**: Model search and optimization
- **`Model Consumption.ipynb`**: Model consumption and evaluation

## 🚀 Prediction Pipeline

### 1. **Forecast Data Acquisition**

```python
# Model Consumption.ipynb
def main():
    # 1. Get meteorological forecast (7 days)
    client = openmeteo_requests.Client(session=sess)
    params = {
        "latitude": 18.2158,      # Parque Solar Girasol
        "longitude": -71.0998,
        "hourly": vars_hr,        # 50+ meteorological variables
        "forecast_days": 7
    }
    
    # 2. Load historical generation data
    df_h = pd.read_parquet(hist_file)
    
    # 3. Combine historical + forecast
    df_m["generation"] = gen  # Historical + zeros for future
```

### 2. **Preprocessing**

```python
# Apply the feature pipeline
feature_engineer = joblib.load('models/solar_feature_engineer.joblib')
model = joblib.load('models/solar_generation_model.joblib')

# Transform data
X_transformed = feature_engineer.transform(X_new)
predictions = model.predict(X_transformed)
```

## 🎯 Azure Functions Preparation

### 1. **Key Dependencies**

```txt
# requirements.txt - Dependencies for Azure Functions
pandas==2.2.3
numpy==2.1.3
scikit-learn==1.5.2
joblib==1.5.0
openmeteo_requests==1.4.0
requests-cache==1.2.1
retry-requests==2.0.0
```

### 2. **Structure for Azure Functions**

```
azure-function-repo/
├── function_app.py              # Main function
├── models/                      # Serialized models
│   ├── solar_feature_engineer.joblib
│   └── solar_generation_model.joblib
├── utils/
│   ├── data_processor.py        # Data processing
│   └── feature_engineer.py     # Feature engineering
└── requirements.txt
```

### 3. **Prediction Flow in Azure**

```python
# function_app.py
import joblib
import pandas as pd
from utils.feature_engineer import SolarFeatureEngineer

def predict_generation(meteo_data):
    # 1. Load models
    feature_engineer = joblib.load('models/solar_feature_engineer.joblib')
    model = joblib.load('models/solar_generation_model.joblib')
    
    # 2. Preprocess data
    X_transformed = feature_engineer.transform(meteo_data)
    
    # 3. Predict
    predictions = model.predict(X_transformed)
    
    return predictions
```

## 📈 Metrics and Evaluation

### 1. **Model Metrics**
- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error
- **R²**: Coefficient of determination
- **MAPE**: Mean Absolute Percentage Error

### 2. **Temporal Validation**
- **TimeSeriesSplit**: Temporal cross-validation
- **Walk-forward validation**: Real-time prediction simulation

## 🔄 Complete Workflow

```
1. Historical Data (2013) → Cleaning → Features → Training
2. Forecast Data (API) → Preprocessing → Prediction
3. Trained Model → Serialization → Azure Functions
4. Azure Functions → REST API → Power BI Dashboard
```

## 🛠️ Technologies Used

### **Data Science:**
- **pandas/numpy**: Data manipulation
- **scikit-learn**: ML modeling
- **statsmodels**: Time series analysis
- **joblib**: Model serialization

### **APIs and Data:**
- **Open-Meteo API**: Meteorological data
- **Post-Despacho API**: Real generation data
- **requests-cache**: Request caching

### **Visualization:**
- **Power BI**: Prediction dashboard
- **matplotlib/seaborn**: Exploratory analysis

## 📋 Next Steps for Azure Functions

1. **Extract prediction code** from `Model Consumption.ipynb`
2. **Create Azure function** with prediction pipeline
3. **Serialize models** and dependencies
4. **Configure triggers** (HTTP, Timer, etc.)
5. **Implement logging** and monitoring
6. **Configure CI/CD** for automatic deployment

## 🎯 Benefits of this Architecture

- **Clear separation**: Data science vs. deployment
- **Reproducibility**: Complete documented pipeline
- **Scalability**: Easy Azure deployment
- **Maintainability**: Modular and well-structured code
- **Monitoring**: Metrics and logs for tracking

## 📚 Additional Documentation

- **`docs/ESTRUCTURA_CIENCIA_DATOS.md`**: Detailed technical documentation
- **`docs/ARQUITECTURA_DIAGRAMA.md`**: Complete architecture diagram
- **`docs/Erros in Post-Despacho DB.txt`**: Database errors found

## 🔧 Data Sources

### **Post-Despacho Data (2013)**
- **Source**: Dominican Republic's electricity market
- **Period**: December 2022 - September 2025
- **Format**: Daily .parquet files
- **Content**: Real solar generation data from Parque Solar Girasol

### **Meteorological Data**
- **Source**: Open-Meteo API
- **Variables**: 30+ meteorological parameters
- **Frequency**: Hourly data
- **Coverage**: Historical + 7-day forecasts

### **Solar Plant Information**
- **Plant**: Parque Solar Girasol
- **Location**: 18.2158°N, -71.0998°W
- **Capacity**: Solar photovoltaic generation
- **Data**: Plant specifications and metadata

## 🚀 Getting Started

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run notebooks** in order: Exploratory → Feature Engineering → Model Search → Model Consumption
4. **Load models** for predictions
5. **Deploy to Azure Functions** for production

## 📊 Model Performance

The final model achieves:
- **High accuracy** in solar generation prediction
- **Robust performance** across different weather conditions
- **Real-time capability** for operational use
- **Scalable architecture** for multiple solar plants

This project demonstrates a complete end-to-end data science solution for renewable energy prediction, from data collection to production deployment.