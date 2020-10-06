FROM python:3.7-slim

# Рабочая директория проекта
WORKDIR /usr/src/app

# установка переменных python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Копирование проекта и установка зависимостей
COPY . /usr/src/app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# запуск entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
