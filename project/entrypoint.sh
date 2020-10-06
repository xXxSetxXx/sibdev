#!/bin/sh

if [ "$DJANGO_DB_ENGINE" = "django.db.backends.postgresql" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DJANGO_DB_HOST $DJANGO_DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# проверка новых миграций
python manage.py migrate  --no-input
# инициализация админов в новой базе
python manage.py initadmin
# сбор статики
python manage.py collectstatic --no-input --clear
# создание кеш таблицы
python manage.py createcachetable

# запуск celery в фоне
celery -A project worker -B  &

exec "$@"
