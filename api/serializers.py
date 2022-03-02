from rest_framework import serializers

from .models import City, User, Genre, Author, Book, Image, Status, Exchange, Sale

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["name"]

class UserSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(read_only=True, slug_field='name')
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "city")

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", 'id')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("first_name", "last_name", 'id')

class BookSerializer(serializers.ModelSerializer):
    # image_set = serializers.SlugRelatedField(read_only = True, many=True, slug_field='image')
    original_owner = UserSerializer()
    author = AuthorSerializer()
    genre = serializers.SlugRelatedField(read_only=True, slug_field='name')
    class Meta:
        model = Book
        fields = ("name", "original_owner", "author", "genre", "edition", "preservation_level", "image_set", 'id')

class ImageSerializer(serializers.ModelSerializer):
    # book = BookSerializer(many = True)
    image = serializers.ImageField()
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

