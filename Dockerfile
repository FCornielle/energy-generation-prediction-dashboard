# Use an Azure ML curated Python base image. These images are optimized for Azure ML.
# Using a specific version is recommended for reproducibility.
# You can find options here: https://learn.microsoft.com/azure/machine-learning/reference-aml-images?view=azureml-api-2#base-images
# For Python-based models, a general-purpose CPU image is usually sufficient.
# Example: mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest
# For a more lightweight Python-only base: mcr.microsoft.com/azureml/python:3.9-ubuntu20.04-py39-cpu-inference
# Let's use a robust one for general ML workloads:
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest

# Set the working directory in the container
WORKDIR /app

# Copy your inference requirements file into the container
COPY inference-requirements.txt .

# Install Python dependencies. Using --no-cache-dir and --upgrade pip are good practices.
RUN pip install --no-cache-dir -r inference-requirements.txt

# Copy your scoring script and any other necessary source code
# Assuming 'src' contains 'score.py' and possibly other modules it needs
COPY src /app/src

# Set the PYTHONPATH to include your source directory if it's not already in site-packages
# This ensures that imports like 'from src import my_module' work correctly if needed
ENV PYTHONPATH=/app:$PYTHONPATH

# The Azure ML Managed Online Endpoint service will inject its own ENTRYPOINT and CMD
# to run the inference server and your score.py.
# You typically do NOT define ENTRYPOINT or CMD here for Managed Online Endpoints
# unless you have a very specific advanced scenario, as it can conflict.
# If you explicitly set CMD/ENTRYPOINT, the "runsvdir" error can occur if it
# doesn't align with Azure ML's expectations for starting the server.

# If you had a previous CMD/ENTRYPOINT that caused the 'runsvdir' error, remove it.
# Leave it out for now to let Azure ML manage the process startup.