from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import Users, UserDetails, Login, Cities, Authors, Genres, Books, MyBooks, BookDetails, BookBuy, BookExchange

urlpatterns = [
    path('users/', Users.as_view()),
    path('users/<int:pk>/', UserDetails.as_view()),
    path('login/', Login.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('cities/', Cities.as_view()),
    path('authors/', Authors.as_view()),
    path('genres/', Genres.as_view()),
    path('books/', Books.as_view()),
    path('books/my/', MyBooks.as_view()),
    path('books/<int:pk>/', BookDetails.as_view()),
    path('books/<int:pk>/buy/', BookBuy.as_view()),
    path('books/<int:pk>/exchange/', BookExchange.as_view()),
]