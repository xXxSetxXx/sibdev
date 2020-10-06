from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    """
    Для создания пользователя
    UserCreateAPIView
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class AddPrecedentUserSerializer(serializers.ModelSerializer):
    """
    Для добавления новых предпочтений пользователя
    AddPrecedentUserApiView
    """
    class Meta:
        model = PrecedentsUser
        fields = ('user', 'precedents', 'attitude', 'importance')

class DeletePrecedentUserSerializer(serializers.ModelSerializer):
    """
    Для удаления предпочтения пользователя
    DetailPrecedentUserApiView
    """
    class Meta:
        model = PrecedentsUser
        fields = '__all__'

class GetPrecedentsUserSerializer(serializers.ModelSerializer):
    """
    Для получения предпочтений пользователя
    GetListPrecedentsUserApiView
    """
    class Meta:
        model = PrecedentsUser
        fields = ('pk', 'precedents', 'attitude', 'importance')

class GetListAllPrecedentsSerializer(serializers.ModelSerializer):
    """
    Для получения названий всех предпочтений
    GetListAllPrecedentsApiView
    """
    class Meta:
        model = Precedents
        fields = ('name',)

def user_serializer_custom(user):
    """
    Для преобразования модели в dict удобный для расчета совместимости
    :param user: Обьект пользователя
    :return: dict формат пользователя
    """
    result = {
        'name': user.name,
        'email': user.email,
        'precedents': list(user.precedentsuser_set.all().values('precedents_id', 'attitude', 'importance'))
    }
    return result


def people_serializer(data):
    """
    Для преобразования всех пользователей в dict удобный для расчета совместимости
    :param data: список пользователей с их предпочтениями
    :return: dict формат пользователей
    """
    result = {}
    for item in data:
        # Заготовка для пользователя, ключ основан на уникальном email пользователя
        if not item['email'] in result:
            result[item['email']] = {'name': item['name'], 'precedents': {}}
        if not item['precedentsuser__precedents'] in result[item['email']]['precedents']:
            result[item['email']]['precedents'][item['precedentsuser__precedents']] = {'attitude': item['precedentsuser__attitude'], 'importance':item['precedentsuser__importance']}
    return result