# Nginx Container
FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf

# Install Certbot
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y universe && \
    add-apt-repository -y ppa:certbot/certbot && \
    apt-get update && \
    apt-get install -y certbot python3-certbot-nginx
    
# Certbot renew
RUN echo "0 */12 * * * certbot renew --pre-hook 'nginx -s stop' --post-hook 'nginx'" > /etc/cron.d/certbot-renew

# Flask Container
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
