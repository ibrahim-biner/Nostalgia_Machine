# Python 3.9'u temel alıyoruz
FROM python:3.9-slim

# Çalışma dizinini /app olarak ayarla
WORKDIR /app

# Sistem bağımlılıklarını yükle (OpenCV için gerekli)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Önce gereksinimleri kopyalayıp yükle
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Model dosyalarını kopyala
COPY ./models /app/models

# Uygulama kodunu kopyala
COPY ./app /app/app

# Arayüz (frontend) dosyalarını kopyala
COPY ./frontend /app/frontend

# Uygulamanın çalışacağı portu belirt
EXPOSE 8000

# Konteyner çalıştığında FastAPI uygulamasını başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]