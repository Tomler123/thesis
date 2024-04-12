# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for pyodbc and ODBC Driver for SQL Server
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    apt-transport-https \
    gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*
# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --default-timeout=1000 --retries=5 -r requirements.txt

# Define environment variable
ENV FLASK_APP=app.py \
    FLASK_ENV=production

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
# CMD ["python3", "app.py"]

