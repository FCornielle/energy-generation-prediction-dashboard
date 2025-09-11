# Tabla Comparativa de Modelos de Predicción de Generación Solar

## Resumen de Modelos Evaluados

| Modelo | Tipo | CV MAE | Mejores Hiperparámetros | Tiempo de Entrenamiento | Complejidad |
|--------|------|---------|-------------------------|-------------------------|-------------|
| **RandomForest** | Ensemble (Bagging) | **5.0148** | `n_estimators=200, max_depth=20, min_samples_leaf=5` | Medio | Baja |
| **XGBoost** | Boosting | 5.2227 | `n_estimators=100, max_depth=4, learning_rate=0.1` | Medio | Media |
| **GradientBoosting** | Boosting | 5.3272 | `n_estimators=100, max_depth=3, learning_rate=0.1, subsample=0.8` | Medio | Media |
| **SVR** | Máquina de Vectores | En proceso | `kernel=rbf/linear, C=0.1/1/10, epsilon=0.01/0.1/1` | Alto | Media |
| **LSTM** | Red Neuronal Recurrente | 14.9515 | `units=16, optimizer=adam, batch_size=32, epochs=10` | Muy Alto | Alta |
| **Conv1D** | Red Neuronal Convolucional | En proceso | `filters=16/32, kernel_size=2/3/5, optimizer=adam/rmsprop` | Alto | Alta |

## Métricas de Evaluación en Test (RandomForest - Mejor Modelo)

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **MAE** | 6.435 | Error absoluto medio en MW |
| **RMSE** | 11.588 | Error cuadrático medio en MW |
| **R²** | 0.900 | 90% de la varianza explicada |

## Análisis Detallado por Modelo

### 1. RandomForestRegressor ⭐ **MEJOR RENDIMIENTO**
- **CV MAE**: 5.0148
- **Ventajas**: 
  - Mejor rendimiento general
  - Robusto a overfitting
  - Maneja bien features no lineales
  - Interpretable
- **Desventajas**: 
  - Puede ser lento con datasets grandes
  - No captura dependencias temporales

### 2. XGBoost
- **CV MAE**: 5.2227
- **Ventajas**: 
  - Excelente rendimiento
  - Manejo eficiente de memoria
  - Regularización incorporada
- **Desventajas**: 
  - Más propenso a overfitting
  - Requiere más tuning

### 3. GradientBoosting
- **CV MAE**: 5.3272
- **Ventajas**: 
  - Buen rendimiento
  - Regularización robusta
- **Desventajas**: 
  - Más lento que XGBoost
  - Sensible a outliers

### 4. SVR (Support Vector Regression)
- **Estado**: En proceso de entrenamiento
- **Ventajas**: 
  - Robusto a outliers
  - Maneja bien espacios de alta dimensión
- **Desventajas**: 
  - Computacionalmente costoso
  - Difícil interpretar

### 5. LSTM (Long Short-Term Memory)
- **CV MAE**: 14.9515
- **Ventajas**: 
  - Diseñado para secuencias temporales
  - Puede capturar dependencias a largo plazo
- **Desventajas**: 
  - Requiere mucho más datos
  - Computacionalmente costoso
  - Difícil de entrenar y optimizar

### 6. Conv1D (Convolutional Neural Network)
- **Estado**: En proceso de entrenamiento
- **Ventajas**: 
  - Puede capturar patrones temporales
  - Eficiente para features secuenciales
- **Desventajas**: 
  - Requiere más datos que modelos clásicos
  - Computacionalmente costoso

## Configuración del Dataset

- **Features**: 402 variables numéricas
- **Tamaño de entrenamiento**: 31,317 muestras
- **Tamaño de test**: 720 muestras (30 días × 24 horas)
- **Validación**: TimeSeriesSplit con 3 folds
- **Métrica de optimización**: MAE (Mean Absolute Error)

## Recomendaciones

### 🥇 **Modelo de Producción**: RandomForest
- **Razón**: Mejor rendimiento (CV MAE: 5.0148)
- **Ventajas**: Robusto, interpretable, rápido en inferencia
- **Uso**: Predicciones en tiempo real

### 🥈 **Modelo Secundario**: XGBoost
- **Razón**: Segundo mejor rendimiento (CV MAE: 5.2227)
- **Uso**: Ensemble con RandomForest para mejorar robustez

### 🔬 **Investigación Futura**:
- **Ensemble**: Combinar RandomForest + XGBoost
- **Feature Engineering**: Crear features temporales más sofisticadas
- **Deep Learning**: Si se dispone de más datos históricos

## Notas Técnicas

- **Preprocesamiento**: StandardScaler aplicado a todos los modelos
- **Validación**: TimeSeriesSplit para respetar la naturaleza temporal de los datos
- **Hiperparámetros**: Optimizados mediante GridSearchCV
- **Hardware**: Utiliza 1/3 de los cores disponibles (22 cores → 7 jobs)

---
*Tabla generada automáticamente basada en los resultados del notebook "Model Builder Search.ipynb"*





