# Base image
FROM python:3.11-slim

# Environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install any necessary system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN python manage.py makemigrations
RUN python manage.py migrate
# Expose the port Daphne will run on
EXPOSE 8000

# Default command for the Django ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "mysite.asgi:application"]
