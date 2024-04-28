# Use the official Rasa SDK image as a base
FROM rasa/rasa:3.5.1-full

# Set the working directory in the container
WORKDIR /app

# Copy your Rasa project into the container
COPY . /app

# Expose the Rasa port
EXPOSE 5005

# Start the Rasa server with CORS enabled to accept requests from all domains
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
