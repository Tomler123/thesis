# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    libffi-dev \
    libpq-dev \
    git \
    nano \
    curl \
    apt-transport-https \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Microsoft SQL Server ODBC Driver and prerequisites
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install spacy \
    && python -m nltk.downloader stopwords \
    && python -m spacy download en_core_web_sm

# Copy the rest of the application into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
