FROM python:3.11.4-alpine

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
WORKDIR /app
COPY Generator.py .
COPY script.py .

CMD python3 script.py
