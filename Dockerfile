# Базовый образ 
FROM python:3.11-slim

# запретит внутри контейнера создавать файлы с кешем
ENV PYTHONDONTWRITEBYTECODE=1

ENV DJANGO_SETTINGS_MODULE=sh.settings

# делает так, что Python сразу выводит сообщения в консоль, без задержки в буфере
ENV PYTHONUNBUFFERED=1

# Папка в которой будет храниться приложение
WORKDIR /app

# Обновляет pip внутри контейнера 
RUN pip install --upgrade pip

# копирует этот файл из локальной машины в контейнер, будет использоваться для установки зависимостей
COPY requirements.txt .

# установка зависимостей проекта
RUN pip install -r requirements.txt

# Команда для копирования файлов и папок с ПК в контейнер
COPY . . 

# говорит какой порт надо открыть ( работает как документация) 
EXPOSE 8000

# Команда для запуска Daphne ASGI сервера

CMD ["sh", "-c", "python3 manage.py migrate --noinput && python3 manage.py collectstatic --noinput &&  daphne -b 0.0.0.0 -p 8000 sh.asgi:application"]

#daphne -b 0.0.0.0 -p 8000 sh.asgi:application