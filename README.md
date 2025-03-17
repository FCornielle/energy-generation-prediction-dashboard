# Energy Generation Prediction Dashboard

Este repositorio contiene el proyecto para la creación de un *dashboard* de predicción de generación de energía, haciendo uso de **Power BI** y **Azure**.  
Incluye la extracción de datos desde el API del organismo coordinador, su limpieza y preprocesamiento local, y la implementación de pipelines de datos en **Azure Data Factory**.  
El objetivo final es desplegar un *dashboard* en Power BI que muestre la información procesada y los modelos predictivos entrenados.

## Estructura de carpetas

```bash
energy-generation-prediction-dashboard/
├── README.md                  # Explicación general del proyecto
├── requirements.txt           # Dependencias (si usas pip)
├── environment.yml            # Archivo de entorno (si usas conda)
├── .gitignore                 # Lista de archivos y carpetas a ignorar
│
├── data/
│   ├── raw/                   # Datos originales descargados (sin procesar)
│   ├── interim/               # Datos intermedios (limpieza parcial)
│   └── processed/             # Datos finales listos para modelar
│
├── notebooks/
│   ├── 01_exploracion.ipynb   # Análisis exploratorio inicial
│   ├── 02_preprocesamiento.ipynb
│   └── 03_modelado.ipynb      # Entrenamiento y evaluación de modelos
│
├── src/                       # Código fuente o scripts principales
│   ├── data_ingestion/        # Scripts de ingestión de datos (API, etc.)
│   ├── data_preprocessing/    # Scripts de limpieza / transformación
│   ├── modeling/              # Scripts para entrenamiento de modelos
│   └── evaluation/            # Scripts de evaluación y métricas
│
├── azure/                     # Configuraciones / plantillas / scripts de Azure
│   ├── data_factory/          # Definiciones de pipelines de Data Factory
│   ├── devops/                # Configs de Azure DevOps (CI/CD, YAML pipelines)
│   └── key_vault/             # Manejo de secretos (opcional)
│
├── power_bi/                  # Archivos de Power BI (.pbix)
│   └── dashboards/            # Reportes y vistas en Power BI
│
└── docs/                      # Documentación adicional (diagramas, etc.)
    └── arquitectura.md
