from django.contrib import admin

from main_app.models import *

admin.site.register(CustomUser)
admin.site.register(Precedents)
admin.site.register(PrecedentsUser)
