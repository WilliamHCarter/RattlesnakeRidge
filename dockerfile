# Flask Container
FROM python:3.11-slim

WORKDIR /usr/src/app

COPY /server ./server
COPY requirements.txt .
COPY run_server.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "run_server.py"]