from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import Http404
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from django.contrib.auth.models import User as DjangoUser
from .models import User, City, Book, Image, Author, Genre
from .serializers import UserSerializer, CitySerializer, AuthorSerializer, GenreSerializer, BookSerializer

class Cities(APIView):
    '''
    List all possible city options
    '''
    def get(self, request, format=None):
        city_objects = City.objects.all()
        cities = []
        for city in city_objects:
            cities.append(city.name)
        return Response(cities, status=status.HTTP_200_OK)

class Users(APIView):
    '''
    List or create users
    '''
    def get(self, request, format=None):
        '''
        List all users
        '''
        users = User.objects.all()
        for user in users:
            user.email = user.django_user.email
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        '''
        Create a new user
        '''
        data = request.data
        fields = ['first_name', 'last_name', 'password', 'email', 'city']
        for field in fields:
            if field not in fields:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if DjangoUser.objects.filter(email=data['email']).exists():
            return Response({'Error': 'User with given email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if not City.objects.filter(name=data['city']).exists():
            return Response({'Error': f'There is no city named {data["city"]} in the database.'}, status=status.HTTP_400_BAD_REQUEST)

        print(data['password'])
        print(make_password(data['password']))
        django_user = DjangoUser.objects.create(
            username=data['email'],
            password=make_password(data['password']),
            email=data['email']
        )
        city = City.objects.get(name=data['city'])
        user = User.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            django_user=django_user,
            city=city
        )

        data['id'] = user.id
        return Response(data, status=status.HTTP_201_CREATED)

class UserDetails(APIView):
    '''
    Retrieve, update or delete user info
    '''
    def get_user(self, pk):
        try:
            user = User.objects.get(pk=pk)
            user.email = user.django_user.email
            return user
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        '''
        Retrieve information about a single user
        '''
        user = self.get_user(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk, format=None):
        '''
        Update an existing user that is authenticated and authorized
        '''
        if not request.user.is_authenticated or request.user.user.id != pk:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = self.get_user(pk)
        data = request.data
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'password' in data:
            user.django_user.password = make_password(data['password'])
            user.django_user.save()
        if 'city' in data:
            city = City.objects.get(name=data['city'])
            user.city = city
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def delete(self, request, pk, format=None):
        '''
        Delete an existing user that is authenticated and authorized
        '''
        if not request.user.is_authenticated or request.user.user.id != pk:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = self.get_user(pk)
        user.django_user.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Login(APIView):
    '''
    Ask for access and refresh token, provided email and password
    '''
    def post(self, request, format=None):
        data = request.data
        if 'email' not in data.keys() or 'password' not in data.keys():
            return Response({'Error': 'You have to supply an email and a password.'}, status=status.HTTP_400_BAD_REQUEST)
        django_user = DjangoUser.objects.get(email=data['email'])
        if django_user == DjangoUser.objects.none():
            return Response({'Error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(data['password'], django_user.password):
            return Response({'Error': 'Wrong password.'}, status=status.HTTP_404_NOT_FOUND)
        access = AccessToken.for_user(django_user)
        refresh = RefreshToken.for_user(django_user)
        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user_id': str(django_user.user.id)
        })

class Authors(generics.ListCreateAPIView):
    '''
    List all available authors, or add a new one
    '''
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [ permissions.IsAuthenticatedOrReadOnly ]

class Genres(generics.ListCreateAPIView):
    '''
    List all available genres, or add a new one
    '''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [ permissions.IsAuthenticatedOrReadOnly ]

class Books(APIView):
    '''
    List all books or post a new one.
    '''
    def get(self, request, format=None):
        '''
        List all books.
        '''
        books = Book.objects.all()
        for book in books:
            book.original_owner.email = book.original_owner.django_user.email
        serializer = BookSerializer(books, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        '''
        Post a new book
        '''
        data = request.data
        if set(data.keys()) != set(['name', 'author', 'genre', 'edition', 'preservation_level']):
            return Response({'Error': 'You haven\'t given all the neccessary data.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_authenticated:
            return Response({'Error': 'You have to be logged in to post a book.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            author = Author.objects.get(id=data['author'])
            genre = Genre.objects.get(id=data['genre'])
            request.user.user.email = request.user.email
            book = Book(
                name=data['name'],
                original_owner=request.user.user,
                author=author,
                genre=genre,
                edition=data['edition'],
                preservation_level=data['preservation_level'],
            )
            book.save()
            if request.data['for_sale'] == True:
                sale = Sale(
                    book=book,
                    buyer=None,
                    status='AVAILABLE'
                    date_sold=None,
                    price=request.data['price'],
                )
                sale.save()
            else:
                exchange = Exchange(
                    book_offered=None,
                    book_returned=None,
                    status='AVAILABLE',
                    date_exchanged=None,
                )
                exchange.save()
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        except:
            return Response({'Error': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)

        # serializer = BookSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyBooks(APIView):
    '''
    List all books of the logged in user.
    '''
    def get(self, request, format=None):
        '''
        List all books of the user.
        '''
        if not request.user.is_authenticated:
            return Response({'Error': 'You aren\'t logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        books = Book.objects.filter(original_owner=request.user.user)
        for book in books:
            book.original_owner.email = book.original_owner.django_user.email
        serializer = BookSerializer(books, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookDetails(APIView):
    '''
    Retrieve, update or delete book info
    '''
    def get_book(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        '''
        Retrieve information about a single book
        '''
        book = self.get_book(pk)
        book.original_owner.email = book.original_owner.django_user.email
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        '''
        Update book instance.
        If updating name, edition, genre or preservation level, provide exact values.
        If updating the author, provide the id of chosen value
        '''
        data = request.data
        book = self.get_book(pk)

        if not request.user.is_authenticated or request.user.user != book.original_owner:
            return Response({'Error': 'You are unauthorized to edit this book.'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'name' in data:
            book.name = data['name']
        if 'edition' in data:
            book.edition = data['edition']
        if 'preservation_level' in data:
            book.preservation_level = data['preservation_level']
        if 'author' in data:
            try:
                book.author = Author.objects.get(id=data['author'])
            except Author.DoesNotExist:
                return Response({'Error': 'You provided an invalid author id.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'genre' in data:
            try:
                book.genre = Genre.objects.get(name=data['genre'])
            except Genre.DoesNotExist:
                return Response({'Error': 'You provided an invalid genre.'}, status=status.HTTP_400_BAD_REQUEST)
        
        book.save()

        book.original_owner.email = book.original_owner.django_user.email
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    def delete(self, request, pk, format=None):
        '''
        Delete object.
        '''
        book = self.get_book(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
