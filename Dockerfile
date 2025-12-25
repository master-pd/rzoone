FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/cache results/exports results/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MARPD_ENV=production

# Run as non-root user
RUN useradd -m -u 1000 marpd
USER marpd

# Run the application
CMD ["python", "main.py"]