# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the server directory contents into the container
COPY /server ./server
COPY requirements.txt .
COPY run_server.py .
# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "run_server.py"]
