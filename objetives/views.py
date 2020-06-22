from django.shortcuts import render

# Rest Framework import
# Vistas
from rest_framework import viewsets, views, authentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
# Httpcode status
from rest_framework import status as httpcodes
# Validation Error
from rest_framework.exceptions import ValidationError
# Response
from rest_framework.response import Response

# ----  Modelos de login  -------------
from login.models import IsUserCommonOrAdmin, IsUserOwnerOrAdmin

from django.db.models import Q as Q_django
# Modelos Objetivos |--------------------------- OBJETIVOS_Q ----------------------------------------------|--NOTAS--------------------------------------------|----  Q  -----------------------------|--- PERMISOS  ---------|
from .models import Objectives_Q, Q, Note, check_valid_post_Objectives_Q, check_if_is_valid_put_Objectives_Q, check_valid_post_Note, check_if_is_valid_put_Note, check_valid_post_Q, check_valid_put_Q, IsUserManageOrEmployee
# Serializadores Objetivos
from .serializers import Objectives_QSerializer, QSerializer, NoteSerializer
# Permisos
from rest_framework import permissions 
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter
from django.http import HttpResponse
from django.utils.encoding import force_bytes
import re


#  VISTA OBJETIVOS
class Objectives_QViewSet(viewsets.ModelViewSet):
    queryset = Objectives_Q.objects.get_queryset().order_by('PK')
    serializer_class = Objectives_QSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Crear Objetivo_Q
    def create(self, request, *args, **kwargs):
        objetiv = check_valid_post_Objectives_Q(request)
        serializer = Objectives_QSerializer(objetiv, context={'request': request})
        return Response(serializer.data, status=httpcodes.HTTP_200_OK)

    # Modificar Objetivo_Q
    def update(self, request, *args, **kwargs):
        NewDataObjective_Q = check_if_is_valid_put_Objectives_Q(
            self.get_object(), request)
        serializer = Objectives_QSerializer(NewDataObjective_Q)
        data = serializer.data
        response = data
        status = httpcodes.HTTP_200_OK

    # Mostrar datos Objetivo_Q
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.is_active:
            serializer = self.get_serializer(instance)
            response = serializer.data
            status = httpcodes.HTTP_200_OK
        else:
            status = httpcodes.HTTP_404_NOT_FOUND
            response = 'This objective is disable'

        return Response(response, status=status)

    # Borrar Objetivo_Q
    def destroy(self, request, *args, **Kwargs):

        instance = self.get_object()

        instance.is_active = False

        instance.save()
        status = httpcodes.HTTP_200_OK

        return Response(status=status)


# VISTA NOTA
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.get_queryset().order_by('PK')
    serializer_class = NoteSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Crear Nota
    def create(self, request, *args, **kwargs):
        note = check_valid_post_Note(request)
        serializer = NoteSerializer(note)

        return Response(serializer.data, status=httpcodes.HTTP_200_OK)

    # Modificar Nota
    def update(self, request, *args, **kwargs):
        NewDataNote = check_if_is_valid_put_Note(self.get_object(), request)
        serializer = NoteSerializer(NewDataNote)
        data = serializer.data
        response = data
        status = httpcodes.HTTP_200_OK

    # Borrar Note
    def destroy(self, request, *args, **Kwargs):

        instance = self.get_object()

        instance.is_active = False

        instance.save()
        status = httpcodes.HTTP_200_OK

        return Response(status=status)

# VISTA CUATRIMESTRE " Q "


class QViewSet(viewsets.ModelViewSet):
    queryset = Q.objects.get_queryset().order_by('PK')
    serializer_class = QSerializer
    permission_classes = (IsUserManageOrEmployee,)
    
    # Crear " Q "

    def create(self, request, *args, **kwargs):
        quatrimestre = check_valid_post_Q(request)
        serializer = QSerializer(quatrimestre)

        return Response(serializer.data, status=httpcodes.HTTP_200_OK)
    
    # Modificar " Q "
    def update(self, request, *args, **kwargs):
        
        NewDataQ = check_valid_put_Q(
            self.get_object(), request)
        serializer = QSerializer(NewDataQ)
        data = serializer.data
        
        response = data
        status = httpcodes.HTTP_200_OK
    
    # Borrar/Cerrar " Q "
    def destroy(self, request, *args, **Kwargs):

        instance = self.get_object()

        instance.is_active = False

        instance.save()
        status = httpcodes.HTTP_200_OK

        return Response(status=status)
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser or not request.user.is_staff:
            queryset = queryset.filter(Q_django(manager=request.user.PK) | Q_django(employee=request.user.PK))
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class Check_Q(views.APIView):

    def post(self, request):
        # Comprueba si hay usuario logeado
        if not request.user.is_anonymous:
            # Guarda el usuario logeado
            user = request.user
        else:
            # Si no gurada el usuario admin de la base de datos
            search_admin=MyUser.objects.filter(username="admin")
            if len(search_admin) != 0:
                user=search_admin[0]
            else:
                raise ValidationError("User admin not exists")
        
        # Obtiene el Q correspondiente al PK recibido en Q_N
        search_Q = Q.objects.filter(PK=request.data['Q'])

        if len(search_Q) != 0:
            Q_N=search_Q[0]
        else:
            raise ValidationError(" Q dont exist")

        # Modifica el campo segun el usuario logeado manager/employee
        if Q_N.manager == user:
            Q_N.check_manager = True

        elif Q_N.employee == user and Q_N.check_manager:
            Q_N.check_employee = True
        
        else:
            raise ValidationError("El usuario indicado no pertenece a esta Q ")

        Q_N.save()
        serializer = QSerializer(Q_N)
        data = serializer.data

        return Response(data, status = httpcodes.HTTP_200_OK)
        
