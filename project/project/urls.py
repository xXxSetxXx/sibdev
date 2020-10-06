from django.contrib import admin
from django.urls import path, re_path, include

from main_app.views import *

urlpatterns = [
    path('email_verify', email_verify),
    path('load_fake_users', load_fake_users),
    path('admin/', admin.site.urls),
    path('api/v1/', include('main_app.urls_api')),
    path('get_links', get_links),
    path('get_api_links', get_api_links),
    path('get_menu', get_menu),

    re_path('^$', start, name='start'),
    re_path('^authorization.*', start),
    re_path('^.*', start),
]
