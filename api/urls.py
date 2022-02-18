from django.urls import path
from .views import Users, UserDetails, Cities

urlpatterns = [
    path('users/', Users.as_view()),
    path('users/<int:pk>/', UserDetails.as_view()),
    path('cities/', Cities.as_view()),
]