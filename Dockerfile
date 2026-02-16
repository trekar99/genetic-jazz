# 1. Usamos Python 3.10
FROM python:3.10-slim

# 2. Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Instalamos dependencias del sistema CRÍTICAS
# - lilypond: Necesario para que music21 genere los PNG de las partituras
# - build-essential: Para compilar numpy/pandas si hace falta
RUN apt-get update && apt-get install -y \
    lilypond \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Directorio de trabajo
WORKDIR /app

# 5. Copiamos requirements.txt e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copiamos TODO el código
COPY . .

# 7. IMPORTANTE: Crear carpeta output y dar permisos
# Hugging Face corre con el usuario 1000. Si no hacemos esto, 
# la app fallará al intentar guardar "generated_...mid"
RUN mkdir -p output && \
    chmod 777 output

# 8. Creamos el usuario no-root (Seguridad de Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 9. Puerto obligatorio de Hugging Face
EXPOSE 7860

# 10. Comando de arranque
# Usamos gunicorn pero SIN eventlet (porque ya no usas sockets).
# 'app:app' asume que tu archivo se llama 'app.py' y la variable Flask es 'app'.
# Si tu archivo se llama 'main.py', cambia a 'main:app'.
CMD ["gunicorn", "-w", "2", "--bind", "0.0.0.0:7860", "app:app"]
