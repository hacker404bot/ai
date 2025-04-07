# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Flask uses (important for Render)
EXPOSE 10000

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=10000
ENV FLASK_RUN_HOST=0.0.0.0

# Run the app
CMD ["flask", "run"]
