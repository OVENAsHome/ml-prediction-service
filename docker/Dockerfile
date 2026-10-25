FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения и модели
COPY app/ .
COPY model/ /model/

EXPOSE 5000
CMD ["python", "app.py"]
