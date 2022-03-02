from django.contrib import admin

from .models import City, User, Book, Author, Genre, Image

admin.site.register(User)
admin.site.register(City)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Image)
