# Expresiones Regulares
import re
# Json
import json
# Validation Error
from rest_framework.serializers import ValidationError
# Serializador nativo django
from django.core.serializers import serialize
from rest_framework import serializers
# Autenticacion nativa django
from django.contrib.auth import authenticate
# Usuario nativo django para la autenticacion
from django.contrib.auth.models import User
# Modelos de Objetivos
from .models import Objectives_Q, Q, Note
# Serializadores de Usuario y Departamento (login)
from login.serializer import MyUserSerializer , DepartmentSerializer
# Modelos de login
from login.models import MyUser

# Serializador de Objetivos
class Objectives_QSerializer(serializers.HyperlinkedModelSerializer):
    Q_Note = serializers.SerializerMethodField()

    def get_Q_Note(self, instance):

        return instance.Q_Note.PK
    class Meta:
        # Especifica modelo a utilizar para el serializador
        model = Objectives_Q
        # PK solo lectura
        read_only_fields = ('PK',)
        # Datos a mostrar
        fields = [
            'PK',
            'text',
            'obj_secundary',
            'obj_father',
            'score',
            'Q_Note',
            'is_active'
        ]


# Serializador de Notas
class NoteSerializer(serializers.HyperlinkedModelSerializer):
    # Guarda el serializador del usuario que escribe la nota
    User =  MyUserSerializer()
    Q_Note = serializers.SerializerMethodField()

    def get_Q_Note(self, instance):

        return instance.Q_Note.PK

    class Meta:
        model = Note
        read_only_fields = ('PK',)
        # Campos a mostrar
        fields = [
            'PK',
            'User',
            'Q_Note',
            'text',
            'date',
            'is_active'
        ]


# Serializador de Cuatrimestre " Q "             
class QSerializer(serializers.HyperlinkedModelSerializer):
    # Guarda serializadores de Manager, departament y employed
    manager = MyUserSerializer()
    department = DepartmentSerializer()
    employee = MyUserSerializer()
    objectives=serializers.SerializerMethodField()
    notes=serializers.SerializerMethodField()

    def get_objectives(self, instance):
        # Busca en los objetos usuario filtrando cullo departamento sea igual a la clave primara recibida por parametro
        search_objectives = Objectives_Q.objects.filter(Q_Note=instance.PK)
        # Crea serializador de usuario recibido
        serializer = Objectives_QSerializer(search_objectives, many=True)

        return serializer.data
    
    def get_notes(self, instance):
        # Busca en los objetos usuario filtrando cullo departamento sea igual a la clave primara recibida por parametro
        search_notes = Note.objects.filter(Q_Note=instance.PK)
        # Crea serializador de usuario recibido
        serializer = NoteSerializer(search_notes, many=True)

        return serializer.data

    class Meta:
        model = Q
        read_only_fields = ('PK',)
        # Campos a mostrar
        fields = [
            'PK',
            'department',
            'manager',
            'employee',
            'check_manager',
            'check_employee',
            'update_date',
            'starting_date',
            'ending_date',
            'notes',
            'objectives',
            'is_active'
        ]
 

