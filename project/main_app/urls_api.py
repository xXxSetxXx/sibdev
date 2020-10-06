from django.urls import path
from .views import *

app_name = 'main_app'


urlpatterns = [
    path('send_mail_auth', auch_mail_confirmation),
    path('auth_token', auth_token),
    path('registration', UserCreateAPIView.as_view()),
    path('get_compatibility_users', get_compatibility_users),

    path('get_precedents_user', GetListPrecedentsUserApiView.as_view()),
    path('add_precedent_user', AddPrecedentUserApiView.as_view()),
    path('delete_precedent_user/<int:pk>', DetailPrecedentUserApiView.as_view()),
    path('get_list_all_precedent', GetListAllPrecedentsApiView.as_view()),

]
