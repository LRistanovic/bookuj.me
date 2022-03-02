from django.urls import path
from .views import Users, UserDetails, Login, Cities, Books

urlpatterns = [
    path('users/', Users.as_view()),
    path('users/<int:pk>/', UserDetails.as_view()),
    path('login/', Login.as_view()),
    path('cities/', Cities.as_view()),
    path('books/list/', Books.as_view()),
]