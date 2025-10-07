FROM python:3.11-slim

# Install ffmpeg and system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directories
RUN mkdir -p /app/output/scenes

# Expose port from environment
ENV BACKEND_PORT=13000
EXPOSE ${BACKEND_PORT}

CMD ["python", "app.py"]
