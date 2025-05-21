# Dockerfile for Python 3.11 inference
# Before building, export your runtime dependencies:
#   pip freeze > inference-requirements.txt
# and place that file at the repo root.

FROM python:3.11-slim-bullseye

# 1. Install build tools for any native wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# 2. Upgrade pip
RUN python3 -m pip install --upgrade pip

# 3. Copy and install Python dependencies
WORKDIR /app
COPY inference-requirements.txt ./
RUN pip install --no-cache-dir -r inference-requirements.txt

# 4. Copy your model and scoring script
COPY models/ ./models
COPY src/ ./src

# 5. Set entrypoint to run your score.py
ENTRYPOINT ["python3", "src/score.py"]
