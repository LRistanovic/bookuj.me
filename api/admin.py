from django.contrib import admin

from .models import City, User

admin.site.register(User)
admin.site.register(City)
