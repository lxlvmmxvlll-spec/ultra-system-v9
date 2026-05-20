FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install aiogram==3.4.1

CMD ["python", "main.py"]
