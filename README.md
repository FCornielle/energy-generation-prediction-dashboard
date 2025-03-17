# Energy Generation Prediction Dashboard

This repository contains the project for creating an energy generation prediction dashboard using **Power BI** and **Azure**.  
It includes data extraction from the coordinating body's API, local data cleaning and preprocessing, and the implementation of data pipelines in **Azure Data Factory**.  
The ultimate goal is to deploy a Power BI dashboard that displays the processed information and the trained predictive models.

## Folder Structure

```bash
energy-generation-prediction-dashboard/
├── README.md                  # General project description
├── requirements.txt           # Dependencies (if using pip)
├── environment.yml            # Environment file (if using conda)
├── .gitignore                 # List of files and folders to ignore
│
├── data/
│   ├── raw/                   # Original data (unprocessed)
│   ├── interim/               # Intermediate data (partially cleaned)
│   └── processed/             # Final data ready for modeling
│
├── notebooks/
│   ├── 01_exploracion.ipynb   # Initial exploratory analysis
│   ├── 02_preprocesamiento.ipynb
│   └── 03_modelado.ipynb      # Model training and evaluation
│
├── src/                       # Main source code or scripts
│   ├── data_ingestion/        # Scripts for data ingestion (API, etc.)
│   ├── data_preprocessing/    # Scripts for data cleaning/transformation
│   ├── modeling/              # Scripts for model training
│   └── evaluation/            # Scripts for evaluation and metrics
│
├── azure/                     # Azure configurations / templates / scripts
│   ├── data_factory/          # Definitions for Data Factory pipelines
│   ├── devops/                # Azure DevOps configs (CI/CD, YAML pipelines)
│   └── key_vault/             # Secret management (optional)
│
├── power_bi/                  # Power BI files (.pbix)
│   └── dashboards/            # Power BI reports and views
│
└── docs/
