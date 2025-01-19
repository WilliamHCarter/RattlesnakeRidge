# Flask Container
FROM python:3.13-slim
WORKDIR /usr/src/app

# Copy application files
COPY /server ./server
COPY pyproject.toml .
COPY run_server.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "run_server.py"]
