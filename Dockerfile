# Use an official Python runtime as a parent image (multi-stage build)
FROM python:3.10-slim as builder

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --user -r requirements.txt

# Use a second stage to create a slim final image
FROM python:3.10-slim

# Copy only the necessary from builder
COPY --from=builder /root/.local /root/.local

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the application code needed for production
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PATH=/root/.local:$PATH

# Run the application
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
