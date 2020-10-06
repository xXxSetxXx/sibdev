from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        if UserModel.objects.filter(is_superuser=True, is_staff=True).count() == 0:
            for user in settings.ADMINS:
                username = user[0].replace(' ', '')
                email = user[1]
                password = '1'
                admin = UserModel.objects.create_superuser(email=email, username=username, password=password)
                admin.is_active = True
                admin.is_admin = True
                admin.save()
        else:
            print('Админские аккаунты уже существуют')
