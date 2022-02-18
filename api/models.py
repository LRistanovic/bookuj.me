from django.db import models
import django.contrib.auth.models

class City(models.Model):
    '''
    This model holds different selectable cities that users can choose when they make their account.
    '''
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class User(models.Model):
    '''
    This model stores basic information about a user's profile,
    and connects it with the django user model with a one to one field.
    '''
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    django_user = models.OneToOneField(django.contrib.auth.models.User, models.CASCADE)
    city = models.ForeignKey(City, models.CASCADE)

class Genre(models.Model):
    '''
    This model holds different genres users can select when they are posting a new book.
    '''
    name = models.CharField(max_length=50)

class Author(models.Model):
    '''
    This model holds different authors users can select when they are posting a new book.
    '''
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

class Book(models.Model):
    '''
    This model holds information about a book instance that is either
    available now, or has been at some point in time, and links it to its owner, author etc.
    It is the main model of the application.
    '''
    name = models.CharField(max_length=100)
    original_owner = models.ForeignKey(User, models.CASCADE)
    author = models.ForeignKey(Author, models.CASCADE)
    genre = models.ForeignKey(Genre, models.CASCADE)
    edition = models.CharField(max_length=4)
    preservation_level = models.IntegerField()

class Image(models.Model):
    '''
    This model holds images related to the book model.
    A single book can have many images, hence they are separated to a different table.
    '''
    image = models.ImageField()
    book = models.ForeignKey(Book, models.CASCADE)

class Status(models.Model):
    '''
    This model is used to keep track of the information about a book
    being available for sale/exchange or not. Can be either 'AVAILABLE',
    'PENDING', or 'UNAVAILABLE'
    '''
    name = models.CharField(max_length=15)

class Exchange(models.Model):
    '''
    This model keeps track of all information about books that are available for exchange,
    as well as all other exchanges that have already occured, using the 'status' field.
    '''
    book_offered = models.ForeignKey(Book, models.CASCADE, related_name='book_offered')
    book_returned = models.ForeignKey(Book, models.SET_NULL, null=True, related_name='book_returned')
    status = models.ForeignKey(Status, models.CASCADE)
    date_published = models.DateField(auto_now=True)
    date_exchanged = models.DateField(auto_now=True, auto_now_add=False, null=True)

class Sale(models.Model):
    '''
    This model keeps track of all information about books that are available for sale,
    as well as all other sales that have already occured, using the 'status' field.
    '''
    book = models.ForeignKey(Book, models.CASCADE)
    buyer = models.ForeignKey(User, models.SET_NULL, null=True)
    status = models.ForeignKey(Status, models.CASCADE)
    date_published = models.DateField(auto_now=True)
    date_sold = models.DateField(auto_now=True, auto_now_add=False, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)