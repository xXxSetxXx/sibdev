import uuid

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class CustomUser(AbstractUser):
    """
     Модель пользователей
     name - ФИО пользователя
     auth_code - одноразовый код авторизации
     verification_token - код активации учетной записи по почте
     fake - признак фейкового пользователя
    """
    username = models.CharField(max_length=150, blank=True, null=True, verbose_name="Имя пользователя")
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name='ФИО пользователя')
    email = models.EmailField(verbose_name='email адресс', unique=True)
    auth_code = models.CharField(max_length=4, verbose_name='Одноразовый код авторизации', blank=True, null=True)
    verification_token = models.UUIDField('Идентификатор подтверждения email адреса', default=uuid.uuid4)
    fake = models.BooleanField(verbose_name="Фейковый", default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.email

    class META:
        db_table = 'custom_user'
        verbose_name = 'Пользователи'


class Precedents(models.Model):
    """
    Список интересов
    """
    name = models.CharField(max_length=100, verbose_name="Предпочтения", primary_key=True)

    def __str__(self):
        return self.name


class PrecedentsUser(models.Model):
    """
    Список предпочтений пользователей
    user - пользователь
    precedents - интерес пользователя
    attitude - отношение к интересу
    importance - важность отношения
    """
    user = models.ForeignKey(to='main_app.CustomUser', verbose_name="Участник", on_delete=models.CASCADE)
    precedents = models.ForeignKey(to='main_app.Precedents', verbose_name="Интерес", on_delete=models.CASCADE)
    attitude = models.BooleanField(verbose_name="Отношение, 0 - негативное, 1 - позитивное")
    importance = models.PositiveSmallIntegerField(verbose_name="Важность")

    def __str__(self):
        return f'{self.user} - {self.precedents} - {"Позитивное" if self.attitude else "Негативное"} - {self.importance}'