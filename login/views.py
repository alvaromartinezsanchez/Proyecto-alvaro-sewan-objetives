from django.shortcuts import render

"""Una ViewSetclase es simplemente un tipo de Vista basada en clases, que no proporciona ningún manejador de métodos como .get()o .post(), y en su lugar proporciona acciones como .list()y .create().
Por lo general, en lugar de registrar explícitamente las vistas en un conjunto de vistas en urlconf, registrará el conjunto de vistas con una clase de enrutador, que determina automáticamente el urlconf por usted.
"""
# Vistas de rest framework
from rest_framework import viewsets, views, authentication
from rest_framework.decorators import api_view, permission_classes
# Response
from rest_framework.response import Response

# Status HttpCode (Codigos de error)
from rest_framework import status as httpcodes

# Importaciones de  modelo  -------------------- USUARIO-------------------- |--DEPARTAMENTO------------------------------------------------------------|---Permision ----------------------------------------------------|
from .models import MyUser, check_valid_post_user, check_if_is_valid_put_user, Department, check_if_is_valid_put_department, check_valid_post_department, IsUserCommonOrAdmin, IsUserOwnerOrAdmin, IsUserForDepartment

# Importa Serializador |--USUARIO--------|--DEPARTAMENTO------|--Login---------|
from .serializer import MyUserSerializer, DepartmentSerializer, LoginSerializer

# Validation error
from rest_framework.exceptions import ValidationError

# Importacion de logeo
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.utils import json

# Permisos
from rest_framework import permissions 
from rest_framework.permissions import AllowAny

from rest_framework.filters import OrderingFilter
from django.http import HttpResponse
from django.utils.encoding import force_bytes
import re




# --------- VISTA DE USUARIO ------------

class MyUserViewSet(viewsets.ModelViewSet):
    # queryset, serializer_class son atributos de ModelViewSet
    # Asigna valor a atributo, accediendo a la funcion get_queryset() y ordenando los resultados por su " PK "
    # get_queryset-->Esta función es la que se encarga de obtener los objetos del modelo que le indicas en la variable model de tu clase. Ésta función por defecto obtiene el queryset de la llamada model.objects.all()
    queryset = MyUser.objects.get_queryset().order_by('PK')
    # Crea serializador de usuario
    serializer_class = MyUserSerializer
    permission_classes = [IsUserOwnerOrAdmin|IsUserCommonOrAdmin]

    # CREAR USUARIO
    def create(self, request, *args, **kwargs):
        # Filtrado para ver que tipo usuario hace la llamada
        # codigo...

        # Asigna valor a usuario validando los datos recibidos
        user = check_valid_post_user(request)
        # Crea Serializador de usuario
        serializer = MyUserSerializer(user)
        # Devuelve Respuesta con los datos del serializador, y codigo de stado http OK
        return Response(serializer.data, status=httpcodes.HTTP_200_OK)
    

    # MODIFICAR USUARIO
    def update(self, request, *args, **krwargs):
        # Guarda datos de usuario tras validar los datos cecibidos
        NewDataUser = check_if_is_valid_put_user(self.get_object(), request)
        # Crea serializador de Usuario con los datos recibidos y validados
        serializer = MyUserSerializer(NewDataUser)
        # Guarda datos de atributos de usuario
        data = serializer.data
        # Devuelve datos modificados 
        response = data
        
        status = httpcodes.HTTP_200_OK

    
    # MUESTRA DATOS DE USUARIO
    def retrieve(self, request, *args, **kwargs):
        # instance => Guarda objeto usuario que realiza la llamada
        # self => Hace referencia al objeto donde se encuentra la funcion en este caso MyUserViewSet
        instance = self.get_object()
        # Si Usuario activo y Trabajador
        if instance.is_active is True or request.user.is_staff:
            # Crea searializador de usuario
            serializer = self.get_serializer(instance)
            # Guarda datos a mostrar
            response = serializer.data
            status = httpcodes.HTTP_200_OK
        else:
            status = httpcodes.HTTP_404_NOT_FOUND
            response = 'Not found'
        return Response(response, status=status)
        

    # BORRAR USUARIO
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        # El borrado se hace cambiando el atributo Activo = False
        instance.is_active = False
        # Y borrando al usuario del departamento
        instance.department = None
        
        instance.save()
        
        status = httpcodes.HTTP_200_OK

        return Response(status=status)

    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser or not request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ------- VISTA DEPARTAMENTO ---------------------
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.get_queryset().order_by('PK')
    serializer_class = DepartmentSerializer
    permission_classes = [IsUserForDepartment|IsUserCommonOrAdmin]

    def create(self, request, *args, **kwargs):
        
        department = check_valid_post_department(request)

        serializer = DepartmentSerializer(department)

        return Response(serializer.data, status=httpcodes.HTTP_200_OK)
        
    def update(self, request, *args, **krwargs):

        instance = check_if_is_valid_put_department(self.get_object(), request)
        
        serializer = DepartmentSerializer(instance)
        
        data = serializer.data
        
        response = data
        
        status = httpcodes.HTTP_200_OK
    
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        search_user_into_department = MyUser.objects.filter( department = instance )

        if len(search_user_into_department) !=0:
            # Nos hemos quedaoooo por aqui
            raise ValidationError("Cannot be erased, this department contains employees")
        else:
            instance.is_active = False
        
        instance.save()
        
        status = httpcodes.HTTP_200_OK

        return Response(status=status)
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser or not request.user.is_staff:
            queryset = queryset.filter(PK=request.user.department.PK)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# ---------------VISTA LOGIN-----------------

class CustomAuth(views.APIView):
    permission_classes=(AllowAny,)
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
    
            status = httpcodes.HTTP_200_OK
            data = MyUserSerializer(user).data
  
            response = data

        except Exception as error:
            status = httpcodes.HTTP_409_CONFLICT
            response = error.args[0]
            if not isinstance(response, str) and response.get(
                    'non_field_errors', False):
                response = str(response['non_field_errors'][0])
            

        return Response(response, status=status)


class CustomLogOut(views.APIView):

    def post(self, request):
        try:
            logout(request)
            status = httpcodes.HTTP_200_OK
        except Exception as error:
            status = httpcodes.HTTP_409_CONFLICT

        return Response(status=status)