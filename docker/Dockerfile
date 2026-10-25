FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения и скрипта обучения
COPY app/ .
COPY model/ /model/

# Обучение модели при сборке образа (model.pkl не хранится в Git)
RUN cd / && python model/train.py

EXPOSE 5000
CMD ["python", "app.py"]
