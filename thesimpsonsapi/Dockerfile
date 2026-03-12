FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/logs

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "streamlit/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
