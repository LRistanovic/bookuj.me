from django.contrib import admin

from .models import City, User, Book, Author, Genre, Image, Status, Sale, Exchange

admin.site.register(User)
admin.site.register(City)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Image)
admin.site.register(Status)
admin.site.register(Sale)
admin.site.register(Exchange)
