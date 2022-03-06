from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import Http404
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import date

from django.contrib.auth.models import User as DjangoUser
from .models import User, City, Book, Image, Author, Genre, Status, Sale, Exchange
from .serializers import UserSerializer, CitySerializer, AuthorSerializer, GenreSerializer, BookSerializer

def check_availability(book):
    '''
    Checks whether the given book is available for sale or exchange
    '''
    available = Status.objects.get(name='AVAILABLE')
    if Sale.objects.filter(book=book, status=available).exists():
        book.for_sale = True
        book.price = Sale.objects.get(book=book).price
    else:
        book.for_sale = False
        book.price = None
    if Exchange.objects.filter(book_offered=book, status=available).exists():
        book.for_exchange = True
    else:
        book.for_exchange = False
    return book

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
        books = []
        sales = Sale.objects.all()
        for sale in sales:
            if sale.status == Status.objects.get(name='AVAILABLE'):
                books.append(sale.book)
        exchanges = Exchange.objects.all()
        for exchange in exchanges:
            if exchange.status == Status.objects.get(name='AVAILABLE'):
                books.append(exchange.book_offered)
        for book in books:
            book.original_owner.email = book.original_owner.django_user.email
            book = check_availability(book)
            # if book.for_sale == False and book.for_exchange == False:
            #     books.remove(book)
        serializer = BookSerializer(books, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        '''
        Post a new book
        '''
        data = request.data
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

            book_status = Status.objects.get(name='AVAILABLE')
            if data.get('for_sale') == 'true' and 'price' in data.keys():
                sale = Sale(
                    book=book,
                    buyer=None,
                    status=book_status,
                    date_published=date.today(),
                    date_sold=None,
                    price=request.data['price']
                )
                sale.save()
            if data.get('for_exchange') == 'true':
                exchange = Exchange(
                    book_offered=book,
                    book_returned=None,
                    status=book_status,
                    date_published=date.today(),
                    date_exchanged=None,
                )
                exchange.save()
            
            book.original_owner.email = book.original_owner.django_user.email
            book = check_availability(book)
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        except:
            return Response({'Error': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)

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
            book = check_availability(book)
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
        book = check_availability(book)
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
        book = check_availability(book)
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    def delete(self, request, pk, format=None):
        '''
        Delete object.
        '''
        book = self.get_book(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookBuy(APIView):
    '''
    Mark a book as bought
    '''
    def get(self, request, pk, format=None):
        book = Book.objects.get(pk=pk)

        if not request.user.is_authenticated:
            return Response({'Error': 'You have to log in to buy a book.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not Sale.objects.filter(book=book).exists():
            return Response({'Error': 'Chosen book is not available for sale.'}, status=status.HTTP_400_BAD_REQUEST)
        if book.original_owner == request.user.user:
            return Response({'Error': 'You can\'t buy your own book!'}, status=status.HTTP_400_BAD_REQUEST)
        
        sale = Sale.objects.get(book=book)
        if sale.status != Status.objects.get(name='AVAILABLE'):
            return Response({'Error': 'Invalid book for sale.'}, status=status.HTTP_400_BAD_REQUEST)

        sale.buyer = request.user.user
        sale.status = Status.objects.get(name='UNAVAILABLE')
        sale.date_sold = date.today()

        sale.save()
        return Response(status=status.HTTP_200_OK)

class BookExchange(APIView):
    '''
    Ask for book exchange
    '''
    def post(self, request, pk, format=None):
        book_offered = Book.objects.get(pk=pk)
        if not request.user.is_authenticated:
            return Response({'Error': 'You have to log in to exchange for a book.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not Exchange.objects.filter(book_offered=book_offered).exists():
            return Response({'Error': 'Chosen book is not available for exchange.'}, status=status.HTTP_400_BAD_REQUEST)
        if book_offered.original_owner == request.user.user:
            return Response({'Error': 'You can\'t exchange with your own book!'}, status=status.HTTP_400_BAD_REQUEST)
        
        exchange = Exchange.objects.get(book_offered=book_offered)
        if exchange.status != Status.objects.get(name='AVAILABLE'):
            return Response({'Error': 'Invalid book for exchange.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book_returned = Book.objects.get(id=request.data['book_id'])
            if book_returned.original_owner != request.user.user:
                return Response({'Error': 'You have to provide your book.'}, status=status.HTTP_403_FORBIDDEN)

            exchange.book_returned = book_returned
            exchange.status = Status.objects.get(name='PENDING')
            exchange.date_exchanged = date.today()

            exchange.save()
            return Response(status=status.HTTP_200_OK)

        except:
            return Response({'Error': 'You offered an invalid book in return.'}, status=status.HTTP_400_BAD_REQUEST)

class ExchangeAccept(APIView):
    def post(self, request, pk, format=None):
        data = request.data
        book_offered = Book.objects.get(pk=pk)
        exchange = Exchange.objects.get(book_offered=book_offered)
        if exchange.status == Status.objects.get(name='PENDING'):
            if data.get('accept')  == 'true':
                exchange.status = Status.objects.get(name='ACCEPTED')

class ExchangeDecline(APIView):
    def post(self, request, pk, format=None):
        data = request.data
        book_offered = Book.objects.get(pk=pk)
        exchange = Exchange.objects.get(book_offered=book_offered)
        if exchange.status == Status.objects.get(name='PENDING'):
            if data.get('accept')  == 'false':
                exchange.status = Status.objects.get(name='DECLINE')
