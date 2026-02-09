FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any
# RUN apt-get update && apt-get install -y gcc

# Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code
COPY . .

# Expose API port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
