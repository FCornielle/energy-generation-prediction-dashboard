# 🏗️ Diagrama de Arquitectura del Proyecto

## 📊 Flujo de Datos y Procesamiento

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🧪 CIENCIA DE DATOS                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   📡 APIs       │    │   🗄️ Datos      │    │   🔧 Pipeline   │
│                 │    │   Históricos    │    │   de Proceso    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Open-Meteo    │    │ • Post-Despacho │    │ • Descarga      │
│ • Forecast API  │    │ • 2013 (diario) │    │ • Limpieza      │
│ • 50+ variables │    │ • Generación    │    │ • Transformación│
│ • 7 días ahead  │    │   real          │    │ • Fusión        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           📊 DATOS PROCESADOS                              │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   📁 raw/       │   📁 interim/   │  📁 processed/  │   📁 lookup/        │
│                 │                 │                 │                     │
│ • Datos crudos  │ • En proceso    │ • Listos para   │ • Metadatos         │
│ • Sin filtrar   │ • Parcialmente  │   modelado      │ • Referencias       │
│ • APIs directas │   limpios       │ • Características│ • Centrales         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🔬 INGENIERÍA DE CARACTERÍSTICAS                    │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│   ⏰ Temporales  │   📈 Lags       │   📊 Rolling    │   🔄 Diferencias   │
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

## 🔄 Flujo de Trabajo Detallado

### **Fase 1: Desarrollo (Este Repositorio)**
```
1. 📡 Obtención de Datos
   ├── API Open-Meteo → Datos meteorológicos
   ├── API Post-Despacho → Datos de generación
   └── Caché y validación

2. 🔧 Procesamiento
   ├── Limpieza de datos
   ├── Transformaciones
   ├── Fusión de fuentes
   └── Validación de calidad

3. 🔬 Ciencia de Datos
   ├── Análisis exploratorio
   ├── Ingeniería de características
   ├── Entrenamiento de modelos
   └── Evaluación y optimización

4. 💾 Serialización
   ├── Pipeline de características
   ├── Modelo final
   └── Documentación
```

### **Fase 2: Despliegue (Azure Functions)**
```
1. 🚀 Azure Function
   ├── Cargar modelos serializados
   ├── Procesar datos de entrada
   ├── Generar predicciones
   └── Retornar resultados

2. 📊 Integración
   ├── API REST endpoint
   ├── Power BI connector
   ├── Monitoreo y logs
   └── Escalabilidad automática
```

## 🎯 Puntos Clave de la Arquitectura

### **Separación de Responsabilidades:**
- **Este repo**: Desarrollo, entrenamiento, validación
- **Azure Functions**: Inferencia, API, escalabilidad

### **Reproducibilidad:**
- Pipeline completo documentado
- Dependencias versionadas
- Modelos serializados

### **Escalabilidad:**
- Serverless en Azure
- Auto-scaling según demanda
- Caché de modelos

### **Monitoreo:**
- Logs de predicciones
- Métricas de rendimiento
- Alertas de errores 