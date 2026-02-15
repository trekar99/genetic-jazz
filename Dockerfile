# Use Python 3.12 on a Debian-based slim image
FROM python:3.12-slim

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install MuseScore, Xvfb (Virtual Display), and audio dependencies
RUN apt-get update && apt-get install -y \
    musescore \
    xvfb \
    libpulse0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Create the symlink so music21 finds 'mscore3' as expected
RUN ln -s /usr/bin/mscore /usr/bin/mscore3

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the project code
COPY . .

# Pre-configure music21 to point to the correct MuseScore binary
RUN python -c "from music21 import environment; s = environment.UserSettings(); s['musicxmlPath'] = '/usr/bin/mscore3'; s['musescoreDirectPNGPath'] = '/usr/bin/mscore3'"

# Expose Render's default port
EXPOSE 10000

# Start command:
# 1. 'xvfb-run -a' creates a virtual screen for MuseScore to run headless.
# 2. '--timeout 120' prevents Gunicorn from killing the worker during melody generation.
# 3. '--chdir src' ensures Gunicorn finds app.py inside the src folder.
CMD ["xvfb-run", "-a", "gunicorn", "--bind", "0.0.0.0:10000", "--chdir", "src", "--timeout", "120", "app:app"]
