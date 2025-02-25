FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create data directory for SQLite database
RUN mkdir -p data

# Expose the port the app runs on
ENV PORT=8000
EXPOSE ${PORT}

# Command to run the application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT} 