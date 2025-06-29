# Use Python 3.11 slim base image
FROM python:3.11-slim

# Install curl for health checks (required by docker-compose healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the Flask application
CMD ["python", "app_flask.py"]