# 🧪 Estructura del Proyecto: Ciencia de Datos para Predicción de Generación Solar

## 📋 Resumen del Proyecto

Este repositorio contiene el **pipeline completo de ciencia de datos** para predecir la generación de energía solar. El proyecto sigue las mejores prácticas de MLops y está diseñado para desplegar el modelo final en **Azure Functions**.

## 🎯 Objetivo Principal

Desarrollar un modelo de machine learning que prediga la generación de energía solar basándose en:
- **Datos meteorológicos** (temperatura, radiación, humedad, etc.)
- **Datos históricos de generación** (post-despacho)
- **Características temporales** (hora, día, mes, estacionalidad)

## 📊 Arquitectura de Datos

### 1. **Capa de Datos (`data/`)**

```
data/
├── raw/                           # Datos originales sin procesar
│   ├── forecast_meteo_data/       # Datos meteorológicos de pronóstico (API)
│   ├── open_meteo_data/          # Datos meteorológicos históricos
│   └── post_despacho_data/       # Datos de generación real (2013)
├── interim/                       # Datos en proceso de transformación
│   ├── forecast_meteo_data_transform/
│   ├── meteo_data_with_generation/
│   ├── meteo_data_with_generation_clean/
│   └── post_despacho_transformed_data/
├── processed/                     # Datos finales para modelado
├── processed_predictions/         # Predicciones del modelo
└── lookup/                        # Datos de referencia
    ├── central_info.csv          # Información de centrales solares
    └── meteo_variables.csv       # Variables meteorológicas
```

### 2. **Pipeline de Procesamiento (`src/`)**

El pipeline sigue un flujo secuencial:

```python
# 1. Descarga de datos
01 - data_post_despacho_downloader.py
    ↓
# 2. Transformación y limpieza
02 - DB_post_despacho_transform.py
    ↓
# 3. Obtención de datos meteorológicos
03 - open_meteo_history_plant_data.py
    ↓
# 4. Fusión de datos
04 - open_meteo_post_despacho_merger.py
    ↓
# 5. Ingeniería de características
feature_engineer.py
```

## 🔬 Componentes de Ciencia de Datos

### 1. **Ingeniería de Características (`feature_engineer.py`)**

La clase `SolarFeatureEngineer` implementa:

```python
class SolarFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, target='generation', max_lag=24, 
                 roll_windows=None, log_transform_cols=None):
        # Configuración del preprocesador
```

**Características generadas:**
- **Temporales**: hora, día, mes (con codificación cíclica)
- **Lags**: valores retrasados de variables meteorológicas
- **Rolling windows**: medias móviles (3h, 6h, 24h)
- **Diferencias**: para variables no estacionarias
- **Transformaciones logarítmicas**: para variables de radiación

### 2. **Análisis Exploratorio (`notebooks/`)**

- **`Exploratory analysis.ipynb`**: Análisis inicial de datos
- **`Feature Engineering.ipynb`**: Desarrollo de características
- **`Model Builder Search.ipynb`**: Búsqueda y optimización de modelos
- **`Model Consumption.ipynb`**: Consumo y evaluación de modelos

### 3. **Modelos Entrenados (`models/`)**

```
models/
├── solar_feature_engineer.joblib    # Pipeline de preprocesamiento
└── solar_generation_model.joblib    # Modelo de predicción (44MB)
```

## 🚀 Pipeline de Predicción

### 1. **Obtención de Datos de Pronóstico**

```python
# Model Consumption.ipynb
def main():
    # 1. Obtener pronóstico meteorológico (7 días)
    client = openmeteo_requests.Client(session=sess)
    params = {
        "latitude": 18.2158,      # Parque Solar Girasol
        "longitude": -71.0998,
        "hourly": vars_hr,        # 50+ variables meteorológicas
        "forecast_days": 7
    }
    
    # 2. Cargar datos históricos de generación
    df_h = pd.read_parquet(hist_file)
    
    # 3. Combinar histórico + pronóstico
    df_m["generation"] = gen  # Histórico + ceros para futuro
```

### 2. **Preprocesamiento**

```python
# Aplicar el pipeline de características
feature_engineer = joblib.load('models/solar_feature_engineer.joblib')
model = joblib.load('models/solar_generation_model.joblib')

# Transformar datos
X_transformed = feature_engineer.transform(X_new)
predictions = model.predict(X_transformed)
```

## 🎯 Preparación para Azure Functions

### 1. **Dependencias Clave**

```txt
# requirements.txt - Dependencias para Azure Functions
pandas==2.2.3
numpy==2.1.3
scikit-learn==1.5.2
joblib==1.5.0
openmeteo_requests==1.4.0
requests-cache==1.2.1
retry-requests==2.0.0
```

### 2. **Estructura para Azure Functions**

```
azure-function-repo/
├── function_app.py              # Función principal
├── models/                      # Modelos serializados
│   ├── solar_feature_engineer.joblib
│   └── solar_generation_model.joblib
├── utils/
│   ├── data_processor.py        # Procesamiento de datos
│   └── feature_engineer.py     # Ingeniería de características
└── requirements.txt
```

### 3. **Flujo de Predicción en Azure**

```python
# function_app.py
import joblib
import pandas as pd
from utils.feature_engineer import SolarFeatureEngineer

def predict_generation(meteo_data):
    # 1. Cargar modelos
    feature_engineer = joblib.load('models/solar_feature_engineer.joblib')
    model = joblib.load('models/solar_generation_model.joblib')
    
    # 2. Preprocesar datos
    X_transformed = feature_engineer.transform(meteo_data)
    
    # 3. Predecir
    predictions = model.predict(X_transformed)
    
    return predictions
```

## 📈 Métricas y Evaluación

### 1. **Métricas de Modelo**
- **RMSE**: Error cuadrático medio
- **MAE**: Error absoluto medio
- **R²**: Coeficiente de determinación
- **MAPE**: Error porcentual absoluto medio

### 2. **Validación Temporal**
- **TimeSeriesSplit**: Validación cruzada temporal
- **Walk-forward validation**: Simulación de predicción en tiempo real

## 🔄 Flujo de Trabajo Completo

```
1. Datos Históricos (2013) → Limpieza → Características → Entrenamiento
2. Datos de Pronóstico (API) → Preprocesamiento → Predicción
3. Modelo Entrenado → Serialización → Azure Functions
4. Azure Functions → API REST → Power BI Dashboard
```

## 🛠️ Tecnologías Utilizadas

### **Ciencia de Datos:**
- **pandas/numpy**: Manipulación de datos
- **scikit-learn**: Modelado de ML
- **statsmodels**: Análisis de series temporales
- **joblib**: Serialización de modelos

### **APIs y Datos:**
- **Open-Meteo API**: Datos meteorológicos
- **Post-Despacho API**: Datos de generación real
- **requests-cache**: Caché de requests

### **Visualización:**
- **Power BI**: Dashboard de predicciones
- **matplotlib/seaborn**: Análisis exploratorio

## 📋 Próximos Pasos para Azure Functions

1. **Extraer código de predicción** de `Model Consumption.ipynb`
2. **Crear función Azure** con el pipeline de predicción
3. **Serializar modelos** y dependencias
4. **Configurar triggers** (HTTP, Timer, etc.)
5. **Implementar logging** y monitoreo
6. **Configurar CI/CD** para despliegue automático

## 🎯 Beneficios de esta Arquitectura

- **Separación clara**: Ciencia de datos vs. despliegue
- **Reproducibilidad**: Pipeline completo documentado
- **Escalabilidad**: Fácil despliegue en Azure
- **Mantenibilidad**: Código modular y bien estructurado
- **Monitoreo**: Métricas y logs para seguimiento 