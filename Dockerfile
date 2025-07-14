FROM python:3.13-slim

WORKDIR /app

# Ensure distutils is available for Python builds
RUN apt-get update && \
    apt-get install -y python3-distutils && \
    rm -rf /var/lib/apt/lists/*

# Prevent unnecessary bytecode and ensure logs flush properly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

