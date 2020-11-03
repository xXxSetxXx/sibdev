import json

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .sample_tasks import *
from main_app.serializers import *

"""
qwew22
"""

############################# Переменные #############################
# ссылки для сайта
links = {
}

# ссылки API для взаимодействия frontend с backend
api_links = {
    'sendMailAuth': '/api/v1/send_mail_auth',
    'auth_token ': '/api/v1/auth_token',
    'getUserList': '/api/v1/get_userlist',
    'email_verify': '/api/v1/email_verify',
    'add_precedent_user': '/api/v1/add_precedent_user',
    'get_precedents_user': '/api/v1/get_precedents_user',
    'get_list_all_precedent': '/api/v1/get_list_all_precedent',
    'delete_precedent_user': '/api/v1/delete_precedent_user/',
    'get_compatibility_users': '/api/v1/get_compatibility_users'
}

# меню навигации сайта
nav_menu = [
    {
        'name': 'Главная',
        'url': '/',
        "icon": 'home',
    },
    {
        'name': 'Пользовательская',
        'url': '/user',
        "icon": 'people',
        "submenu": [
            {
                'name': 'Рекомендации',
                'url': '/user/recommendations',
                "icon": 'people',
            },
            {
                'name': 'Профиль',
                'url': '/user/profile',
                "icon": 'face',
            },
        ]
    }
]


#######################################################################################


############################# функции #############################
def calc_compatibility(human_main, people, percent):
    """
    Расчет совместимости между human_main и людьми из списка peoples
    :return: Список людей с совместимостью > percent %
    """
    tmp_rating = {}
    # Пробегаюсь по всем предпочтениям человека
    for user_precedents in human_main['precedents']:
        # Пробегаюсь по всем остальным людям
        for key_assessed_person, value_assessed_person in people.items():
            # Проверяю есть ли у человека из списка схожие предпочтения
            if user_precedents['precedents_id'] in value_assessed_person['precedents']:
                # заготовка рейтинга совместимости
                if not key_assessed_person in tmp_rating:
                    tmp_rating[key_assessed_person] = {'summ': 0, 'count': 0, 'result': 0}
                # Проверка совместимости
                if value_assessed_person['precedents'][user_precedents['precedents_id']]['attitude'] == user_precedents['attitude']:
                    # если совместимые предпочтения (определяет совместимость в плюс)
                    tmp_rating[key_assessed_person]['summ'] += (100 - abs(user_precedents['importance'] - value_assessed_person['precedents'][user_precedents['precedents_id']]['importance']) * 5)
                else:
                    # Если не совместимые предпочтения (определяет совместимость в минус)
                    tmp_rating[key_assessed_person]['summ'] += (user_precedents['importance'] + value_assessed_person['precedents'][user_precedents['precedents_id']]['importance']) * (-5)
                tmp_rating[key_assessed_person]['count'] += 1

    # Расчет результата по совместимости в % для всех и отсеивание тех кто меньше определенного %
    rating = []
    for key, _ in tmp_rating.items():
        tmp_rating[key]['result'] = tmp_rating[key]['summ'] / tmp_rating[key]['count']
        if tmp_rating[key]['result'] > percent:
            rating.append({'email': key, 'result': round(tmp_rating[key]['result'])})
    tmp_rating.clear()
    rating = sorted(rating, key=lambda item: item['result'])[::-1][:20]
    return rating


#################################################################################################################################################


########################## вьюшки ##########################
def start(request):
    '''
    Запуск приложения на vuejs
    '''
    return render(request, template_name='index.html')


def get_links(request):
    """
    Отдача ссылок для frontend приложения
    """
    if request.method == "POST":
        return JsonResponse(links, safe=False)
    return HttpResponse(status=204)


def get_api_links(request):
    """
        Отдача ссылок API для frontend приложения
    """
    if request.method == "POST":
        return JsonResponse(api_links, safe=False)
    return HttpResponse(status=204)


def get_menu(request):
    """
    Отдача меню для формирования на сайте
    """
    if request.method == "POST":
        return JsonResponse(nav_menu, safe=False)
    return HttpResponse(status=204)


def load_fake_users(request):
    """
    Добавление фейковых пользователей для примера просмотра рейтинга совместимости
    """
    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse({'text': f'Произошла ошибка {e}'}, status=status.HTTP_400_BAD_REQUEST, safe=False)
    append_fake_users.delay(data)
    return JsonResponse({'text': 'Принято в обработку'}, status=status.HTTP_202_ACCEPTED, safe=False)


def email_verify(request):
    """
    todo проверить с подменой токена
    Подтверждение электронной почты
    Принимает get параметр token
    """
    try:
        user = CustomUser.objects.get(verification_token=request.GET['token'], is_active=False)
    except CustomUser.DoesNotExist:
        raise Http404("Пользователь с данным токеном не найден или уже подтвержден")

    user.is_active = True
    user.save()
    return redirect('start')


class UserCreateAPIView(generics.CreateAPIView):
    """
    Регистрация нового пользователя с подтверждением по email после создания в базе
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        # сохранение в базе пользователя
        serializer.save(is_active=False)
        # отправка пользователю письма с подтверждением
        user = CustomUser.objects.get(email=self.request.data["email"])
        host_name = self.request.META['HTTP_HOST']
        theme = f"Подтверждение электронной почты на сайте {host_name}"
        message = f"""Для подтверждения электронной почты перейдите по ссылке
                      http://{host_name}/email_verify?token={user.verification_token}"""

        user_email_send.delay(user.id, message, theme)


def auch_mail_confirmation(request):
    """
    Подтверждение аутентификации по электронной почте.
    """
    # Проверяем данные пришедшие с сайта
    try:
        data = json.loads(request.body)
        email = data['email']
        password = data['password']
    except:
        return JsonResponse({'error': 'Произошла ошибка сервера при получении данных'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
    # Берем пользователя по имени или мэйлу
    user = CustomUser.objects.filter(email=email).first()
    # Проверяем есть ли пользователь и валидный ли пароль
    if user and user.check_password(password):
        # Проверка учетной записи на активность
        if not user.is_active:
            return JsonResponse({'text': 'Учетная запись не активна'}, status=status.HTTP_400_BAD_REQUEST, safe=False)
        auth_code = ''.join(random.choices(string.digits, k=4))
        host_name = request.META['HTTP_HOST']
        theme = f"Подтверждение входа пользователя на сайте {host_name}"
        message = f"""
        Попытка входа на сайт {host_name} с действительными учетными данными
        Одноразовый код авторизации {auth_code}
        
        Если это не вы пытаетесь войти тогда необходимо сменить пароль для учетной записи.
        """
        user.auth_code = auth_code
        user.save()
        user_email_send.delay(user_id=user.pk, message=message, theme=theme)
        return JsonResponse({'text': 'Одноразовый код авторизации отправлен по почте'}, status=status.HTTP_202_ACCEPTED, safe=False)
    # Если не получилось авторизоваться с введенными данными то выкидываем ошибку
    return JsonResponse({'text': 'Логин и пароль не найдены'}, status=status.HTTP_400_BAD_REQUEST, safe=False)


def auth_token(request):
    """
    Авторизация и выдача токена
    """
    # Проверяем данные пришедшие с сайта
    try:
        data = json.loads(request.body)
        email = data['email']
        password = data['password']
        auth_code = data['auth_code']
    except:
        return JsonResponse({'error': 'Произошла ошибка сервера при получении данных'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
    # Берем пользователя по мэйлу
    user = CustomUser.objects.filter(email=email).first()
    # Проверка существования пользователя, временного пароля, постоянного пароля и выдача токена в случае успешной проверки
    if user and user.auth_code == auth_code and user.check_password(password):
        # Провверка на существование токена или его создание
        try:
            token = Token.objects.get(user=user).key
        except:
            token = Token.objects.create(user=user).key
        # очистка временного пароля после авторизации, для безопасности
        user.auth_code = None
        user.save()
        return JsonResponse({'auth_token': token}, status=status.HTTP_200_OK, safe=False)
    # Если не получилось авторизоваться с введенными данными то выкидываем ошибку
    return JsonResponse({'text': 'Логин или пароль неверны'}, status=status.HTTP_400_BAD_REQUEST, safe=False)


def get_compatibility_users(request):
    """
    получение совместимости пользователей
    """
    # получение пользователя
    try:
        token = request.headers.get('Authorization').split(' ')[-1]
    except:
        return JsonResponse({'error': 'Даные пользователя предоставлены неверно'}, status=status.HTTP_401_UNAUTHORIZED, safe=False)
    user = Token.objects.get(key=token).user
    # получаем данные пользователя в удобном формате
    user_dict = user_serializer_custom(user)
    # Так получаем список пользователей со схожими интересами в dict удобном для расчета
    people = (CustomUser.objects
              .filter(precedentsuser__precedents__in=PrecedentsUser.objects.filter(user=user).values('precedents'))
              .values('email', 'name', 'precedentsuser__precedents', 'precedentsuser__attitude', 'precedentsuser__importance')
              .exclude(pk=user.pk))
    # Обрабатываем пользователей в удобный формат
    people_dict = people_serializer(people)
    # задаем процент совместимости(на всякий случай, вдруг потом изменится условие и нужно будет спрашивать у пользователя)
    percent = 75
    # рассчитываем совместимость
    rating = calc_compatibility(human_main=user_dict, people=people_dict, percent=percent)

    # Преобразовываем в формат для сайта
    compatibility_users = []
    for item in rating:
        user = CustomUser.objects.get(email=item['email'])
        compatibility_users.append({'email': user.email, 'name': user.name, 'rating': item['result']})
    return JsonResponse(compatibility_users, status=status.HTTP_200_OK, safe=False)


class AddPrecedentUserApiView(generics.CreateAPIView):
    """
    Добавление нового интереса пользователя
    """
    queryset = PrecedentsUser.objects.all()
    serializer_class = AddPrecedentUserSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        # Получение предпочтения и добавление нового, если его раньше небыло
        precedents, created = Precedents.objects.get_or_create(name=self.request.data['precedents'])
        # проверка данных и сохранение
        serializer = self.get_serializer(data={'user': user.pk, 'precedents': precedents.pk, 'attitude': self.request.data['attitude'], 'importance': self.request.data['importance']})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer.save())

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DetailPrecedentUserApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    Изменение или удаление пользовательского предпочтения
    """
    queryset = PrecedentsUser.objects.all()
    serializer_class = DeletePrecedentUserSerializer


class GetListPrecedentsUserApiView(generics.ListAPIView):
    """
    Получение списка предпочтений пользователя
    """
    serializer_class = GetPrecedentsUserSerializer

    def get_queryset(self):
        queryset = PrecedentsUser.objects.filter(user=self.request.user)
        return queryset


class GetListAllPrecedentsApiView(generics.ListAPIView):
    """
    Получение названий всех предпочтений
    """
    serializer_class = GetListAllPrecedentsSerializer
    queryset = Precedents.objects.all()
