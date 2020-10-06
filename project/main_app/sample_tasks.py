import random
import string

from django.core.cache import cache
from django.template import Template, Context
from django.db.models import Count
from django.contrib.auth import get_user_model
from celery import shared_task
from project import settings

from main_app.models import Precedents, PrecedentsUser


# Получаем модель пользователя
UserModel = get_user_model()

# шаблон ежедневной рассылки рекомендаций к заполнению
RECOMMENDATION_TEMPLATE = """
Добрый день!
Для увеличения точности подбора наилучшей компании предлагаем Вам добавить 
ранее не заполненые увлечения наиболее популярные среди других участников.

Рекомендации к заполнению:
{% for precedent in precedents %}
       - "{{ precedent.precedents }}"
{% endfor %}
"""


# отправка письма пользователю
@shared_task
def user_email_send(user_id, message, theme):
    """
    Отправка письма пользователю
    :param user_id: id пользователя
    :param message: Текст сообщения пользователю
    :param theme: Тема сообщения
    """
    try:
        user = UserModel.objects.get(pk=user_id)
        user.email_user(theme, message, settings.EMAIL_HOST_USER)
    except UserModel.DoesNotExist:
        pass


@shared_task
def append_fake_users(data):
    """
    Добавление фейковых пользователей
    data: список фейковых пользователей
    """
    for item in data:
        name = item['name']
        # генерация случайного мейла для пользователя
        email = ''.join(random.choices(string.ascii_letters + string.ascii_uppercase, k=15)) + '@mail.ru'
        # установка простого пароля для пользователя
        password = '1'
        # создание пользователя
        try:
            # На случай вдруг сгенерируется такой же мейл как и уже существующий, что маловерятно, пропустим пользователя
            user = UserModel.objects.create_user(username=name, name=name, email=email, password=password, fake=True)
        except:
            continue
        user.save()
        # добавляется фейковому пользователю его предпочтения
        user_precedents = []
        for user_precedents_key, user_precedents_value in item['precedents'].items():
            # Берется из базы предпочтение пользователя
            precedents = Precedents.objects.filter(pk=user_precedents_key).first()
            # Проверяем сучествует ли предпочтение пользователя, если нет то создает его
            if not precedents:
                precedents = Precedents(name=user_precedents_key)
                precedents.save()
            # создается предпочтение для пользователя
            user_precedents.append(PrecedentsUser(user=user, precedents=precedents, attitude=True if user_precedents_value['attitude'] == 'positive' else False, importance=user_precedents_value['importance']))
        PrecedentsUser.objects.bulk_create(user_precedents)


@shared_task
def send_new_precedents_user():
    """
    Отправка для активных пользователей не заполненных предпочтений из списка наиболее популярных
    """
    # Пробегаемся по всем активным пользователям
    for user in UserModel.objects.filter(fake=False, is_superuser=False, is_active=True):
        # Проверяем кеш и наиболее популярных предпочтений

        key = 'cashe_precedentsuser'
        precedents = cache.get(key)
        if precedents is None:
            precedents = PrecedentsUser.objects.all().values('precedents').annotate(count=Count('precedents')).order_by('-count')
            cache.set(key, precedents, 60*60*24)
        # отсеиваем те которые есть у пользователя и оставляем 3 топовых
        precedents = precedents.exclude(precedents__in=PrecedentsUser.objects.filter(user=user).values('precedents'))[:3]

        theme = 'Предлагаем дополнить ваши предпочтения наиболее популярными среди других'
        template = Template(RECOMMENDATION_TEMPLATE)
        # отправляем пользователю почту с сгенерированными данными
        user.email_user(
            theme,
            template.render(context=Context({'precedents': precedents})),
            settings.EMAIL_HOST_USER)
