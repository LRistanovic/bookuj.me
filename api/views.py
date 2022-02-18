from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User as DjangoUser
from .models import User, City
from .serializers import UserSerializer, CitySerializer

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
        Update an existing user that is authenticated and authorized
        '''
        if not request.user.is_authenticated or request.user.user.id != pk:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = self.get_user(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
