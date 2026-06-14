# Python Docker image for the python-ci FastAPI application
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app sources
COPY . /app

# Expose port used by uvicorn
EXPOSE 3000

# Default command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
