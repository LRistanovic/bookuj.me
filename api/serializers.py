from .models import City, User, Genre, Author, Book, Image, Status, Exchange, Sale
from rest_framework import serializers

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("name")

class UserSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    class Meta:
        model = User
        fields = ("first_name", "last_name", "django_user", "city")

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name")

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("first_name", "last_name")

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("name", "original_owner", "author", "genre", "edition", "preservation_level")
class ImageSerializer(serializers.ModelSerializer):
    book = BookSerializer(many = True)
    class Meta:
        model = Image
        fields = ("image", "book")

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ("name")

class ExchangeSerializer(serializers.ModelSerializer):
    book_offered = BookSerializer(many = True)
    book_returned = BookSerializer(many = True)
    status = StatusSerializer()
    class Meta:
        model = Exchange
        fields = ("book_offered", "book_returned", "status", "date_published", "date_exchanged")

class SaleSerializer(serializers.ModelSerializer):
    book = BookSerializer(many = True)
    status = StatusSerializer()
    buyer = UserSerializer(many = True)
    class Meta:
        model = Sale
        fields = ("book", "status", "date_published", "date_sold", "price")

