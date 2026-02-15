# Usamos una imagen de Python ligera
FROM python:3.12-slim

# Instalamos dependencias del sistema para música y gráficos
RUN apt-get update && apt-get install -y \
    lilypond \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiamos el resto del código
COPY . .

# Exponemos el puerto que usa Render
EXPOSE 10000

# Comando para arrancar la app
# --chdir src porque tu app.py está dentro de la carpeta src
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--chdir", "src", "app:app"]
