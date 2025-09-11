# 🧪 Energy Generation Prediction Dashboard

Este repositorio contiene el **pipeline completo de ciencia de datos** para predecir la generación de energía solar. El proyecto sigue las mejores prácticas de MLops y está diseñado para desplegar el modelo final en **Azure Functions**.

## 🎯 Objetivo Principal

Desarrollar un modelo de machine learning que prediga la generación de energía solar basándose en:
- **Datos meteorológicos** (temperatura, radiación, humedad, etc.)
- **Datos históricos de generación** (post-despacho 2013)
- **Características temporales** (hora, día, mes, estacionalidad)

## 📊 Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────────────────────────┐
                           🧪 CIENCIA DE DATOS                               
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   📡 APIs                🗄️ Datos             🔧 Pipeline   
│                 │    │   Históricos    │    │   de Proceso    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Open-Meteo    │    │ • Post-Despacho │    │ • Descarga      │
│ • Forecast API  │    │ • Desde 2013    │    │ • Limpieza      │
│ • 30 variables  │    │ • Generación    │    │ • Transformación│
│ • 2 días ahead  │    │   real          │    │ • Fusión        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
                            📊 DATOS PROCESADOS                               
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│   📁 raw/       │   📁 interim/   │  📁 processed/  │   📁 lookup/        │
│                 │                 │                 │                       │
│ • Datos crudos  │ • En proceso    │ • Listos para   │ • Metadatos           │
│ • Sin filtrar   │ • Parcialmente  │   modelado      │ • Referencias         │
│ • APIs directas │   limpios       │ • Características│ • Centrales          │
└─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🔬 INGENIERÍA DE CARACTERÍSTICAS                    │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│ ⏰ Temporales   │   📈 Lags       │   📊 Rolling    │   🔄 Diferencias   │
│                 │                 │   Windows       │                     │
│ • hora_sin/cos  │ • Variables     │ • Medias móviles│ • Variables no     │
│ • dow_sin/cos   │   retrasadas    │ • 3h, 6h, 24h  │   estacionarias    │
│ • month_sin/cos │ • Mejor lag     │ • Estadísticas  │ • Diff(1)          │
│ • Codificación  │   encontrado    │   descriptivas  │ • Estacionarización│
│   cíclica       │ • Correlación   │                 │                     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🤖 MODELADO ML                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   📓 Notebooks  │   🔧 Feature    │   🎯 Modelo     │   📈 Evaluación    │
│                 │   Engineer      │   Entrenado     │                     │
│ • Exploratory   │ • SolarFeature  │ • RandomForest  │ • RMSE, MAE        │
│ • Feature Eng.  │   Engineer      │ • XGBoost       │ • R², MAPE         │
│ • Model Search  │ • Pipeline      │ • LightGBM      │ • TimeSeriesSplit  │
│ • Consumption   │ • Preprocessing │ • Ensemble      │ • Walk-forward     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        💾 MODELOS SERIALIZADOS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│   📁 models/                                                              │
│                                                                           │
│ • solar_feature_engineer.joblib (13KB)                                   │
│   └─ Pipeline de preprocesamiento                                        │
│                                                                           │
│ • solar_generation_model.joblib (44MB)                                   │
│   └─ Modelo de predicción final                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🚀 PREPARACIÓN AZURE FUNCTIONS                      │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   📄 function_  │   📁 utils/     │   📄 require-   │   🔧 Triggers      │
│   app.py        │                 │   ments.txt     │                     │
│                 │                 │                 │                     │
│ • Endpoint HTTP │ • data_processor│ • Dependencias  │ • HTTP Request      │
│ • Predict API   │ • feature_eng.  │   mínimas       │ • Timer (cron)      │
│ • Error handling│ • Validación    │ • joblib        │ • Blob Storage      │
│ • Logging       │ • Caché         │ • pandas        │ • Event Hub         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           📊 POWER BI DASHBOARD                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ • Visualización de predicciones                                           │
│ • Métricas en tiempo real                                                 │
│ • Alertas y notificaciones                                                │
│ • Exportación de reportes                                                 │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📁 Estructura Detallada del Proyecto

```
energy-generation-prediction-dashboard/
├── 📄 README.md                           # Descripción general del proyecto
├── 📄 requirements.txt                     # Dependencias de Python (93 líneas)
├── 📄 .gitignore                          # Archivos y carpetas a ignorar
├── 📄 manage service principal.txt        # Configuración de Azure Service Principal
│
├── 📊 data/                               # Datos del proyecto
│   ├── 📁 raw/                            # Datos originales (sin procesar)
│   │   ├── 📁 forecast_meteo_data/        # Datos meteorológicos de pronóstico
│   │   │   └── parque_solar_girasol_forecast_api_request.csv
│   │   ├── 📁 open_meteo_data/           # Datos meteorológicos históricos
│   │   │   └── parque_solar_girasol.parquet
│   │   └── 📁 post_despacho_data/        # Datos de post-despacho (2013)
│   │       └── [+4378 archivos .parquet]  # Datos diarios del año 2013
│   ├── 📁 interim/                        # Datos intermedios (parcialmente procesados)
│   │   ├── 📁 forecast_meteo_data_transform/
│   │   │   └── parque_solar_girasol_forecast_api_transformed.csv
│   │   ├── 📁 meteo_data_with_generation/
│   │   │   └── parque_solar_girasol.parquet
│   │   ├── 📁 meteo_data_with_generation_clean/
│   │   │   └── parque_solar_girasol_clean.parquet
│   │   └── 📁 post_despacho_transformed_data/
│   │       ├── post_despacho_transformed.parquet
│   │       └── post_despacho_transformed_parquet_fix.parquet
│   ├── 📁 processed/                      # Datos finales listos para modelado
│   │   ├── parque_solar_girasol_model_ready.parquet
│   │   ├── parque_solar_girasol_forecast_model_ready.parquet
│   │   └── parque_solar_girasol_predicciones_alineadas.csv
│   ├── 📁 processed_predictions/          # Predicciones del modelo
│   │   └── parque_solar_girasol_generation.csv
│   └── 📁 lookup/                         # Datos de referencia
│       ├── central_info.csv               # Información de centrales solares
│       └── meteo_variables.csv           # Variables meteorológicas
│
├── 🔧 src/                                # Código fuente principal
│   ├── 📄 01 - data_post_despacho_downloader.py    # Descargador de datos post-despacho
│   ├── 📄 02 - DB_post_despacho_transform.py       # Transformación de datos post-despacho
│   ├── 📄 03 - open_meteo_history_plant_data.py    # Datos meteorológicos históricos
│   ├── 📄 04 - open_meteo_post_despacho_merger.py  # Fusión de datos meteorológicos y post-despacho
│   └── 📄 feature_engineer.py                      # Ingeniería de características
│
├── 📓 notebooks/                          # Jupyter notebooks de análisis
│   ├── 📄 Exploratory analysis.ipynb      # Análisis exploratorio inicial (9.6MB)
│   ├── 📄 Feature Engineering.ipynb       # Ingeniería de características (368KB)
│   ├── 📄 Model Builder Search.ipynb      # Búsqueda y construcción de modelos (493KB)
│   ├── 📄 Model Consumption.ipynb         # Consumo y evaluación de modelos (146KB)
│   └── 📄 temporary.ipynb                 # Notebook temporal (58KB)
│
├── 🤖 models/                             # Modelos entrenados
│   ├── 📄 solar_feature_engineer.joblib   # Preprocesador de características (13KB)
│   └── 📄 solar_generation_model.joblib   # Modelo de predicción de generación (44MB)
│
├── 📈 power_bi/                           # Archivos de Power BI
│   ├── 📄 energy-generation-prediction-dashboard.pbix  # Dashboard principal (1.9MB)
│   └── 📄 Simple Design.pptx              # Diseño del dashboard (696KB)
│
├── 📚 docs/                               # Documentación del proyecto
│   ├── 📄 Presentation.pptx               # Presentación del proyecto (2.3MB)
│   ├── 📄 Predicción de la Generación Fotovoltaica a Gran Escala.docx
│   ├── 📄 Azure Resources.docx            # Recursos de Azure utilizados (469KB)
│   ├── 📄 Transform Plants ADF.xlsx       # Transformaciones en ADF (12KB)
│   ├── 📄 Erros in Post-Despacho DB.txt   # Errores encontrados en la base de datos
│   ├── 📄 Image of Proyect.docx           # Imágenes del proyecto (230KB)
│   ├── 📄 ESTRUCTURA_CIENCIA_DATOS.md    # Documentación técnica detallada
│   └── 📄 ARQUITECTURA_DIAGRAMA.md        # Diagrama de arquitectura
│
└── ☁️ az/                                 # Configuraciones de Azure (vacío actualmente)
```

## 🔬 Componentes de Ciencia de Datos

### 1. **Ingeniería de Características (`src/feature_engineer.py`)**

La clase `SolarFeatureEngineer` implementa un pipeline completo de preprocesamiento:

```python
class SolarFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, target='generation', max_lag=24, 
                 roll_windows=None, log_transform_cols=None):
        # Configuración del preprocesador
```

**Características generadas:**
- **⏰ Temporales**: hora, día, mes (con codificación cíclica)
- **📈 Lags**: valores retrasados de variables meteorológicas
- **📊 Rolling windows**: medias móviles (3h, 6h, 24h)
- **🔄 Diferencias**: para variables no estacionarias
- **📈 Transformaciones logarítmicas**: para variables de radiación

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

### 3. **Análisis Exploratorio (`notebooks/`)**

- **`Exploratory analysis.ipynb`**: Análisis inicial de datos (9.6MB)
- **`Feature Engineering.ipynb`**: Desarrollo de características (368KB)
- **`Model Builder Search.ipynb`**: Búsqueda y optimización de modelos (493KB)
- **`Model Consumption.ipynb`**: Consumo y evaluación de modelos (146KB)

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

## 📚 Documentación Adicional

- **`docs/ESTRUCTURA_CIENCIA_DATOS.md`**: Documentación técnica detallada
- **`docs/ARQUITECTURA_DIAGRAMA.md`**: Diagrama de arquitectura completo
- **`docs/Azure Resources.docx`**: Recursos de Azure utilizados
- **`docs/Presentation.pptx`**: Presentación del proyecto
