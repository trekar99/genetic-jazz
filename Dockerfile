# Usamos Python 3.12 sobre una base Debian para mayor compatibilidad con MuseScore
FROM python:3.12-slim

# Evita que Apt haga preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Instalar MuseScore, Xvfb (servidor gráfico virtual) y dependencias de audio
RUN apt-get update && apt-get install -y \
    musescore \
    xvfb \
    libpulse0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos solo los requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiamos el resto del código del proyecto
COPY . .

# Exponemos el puerto de Render
EXPOSE 10000

# Comando para arrancar la app:
# 1. 'xvfb-run' crea la pantalla virtual para MuseScore.
# 2. '--timeout 120' evita que el generador de Jazz se corte por tiempo.
# 3. '--chdir src' porque tu app.py está dentro de esa carpeta.
CMD ["xvfb-run", "gunicorn", "--bind", "0.0.0.0:10000", "--chdir", "src", "--timeout", "120", "app:app"]
