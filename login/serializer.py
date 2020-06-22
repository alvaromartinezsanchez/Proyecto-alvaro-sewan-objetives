from rest_framework import serializers, permissions
from .models import MyUser, Department

# --login---

# Usuario nativo django 
from django.contrib.auth.models import User
# Autenticate
from django.contrib.auth import authenticate
# Validation Error
from rest_framework.serializers import ValidationError
# Re
import re
import json
from django.core.serializers import serialize


# SERIALIZADOR DE MODELO " MYUSER "

class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    # SerializerMethodField ==> Un campo de solo lectura que obtiene su representación llamando a un método en clase de serializador principal.
    department=serializers.SerializerMethodField()

    # Muestra el titulo del departamento y no el objeto departamento al ser llamado
    def get_department(self, instance): # instance recibe el objeto(MyUser)
        if instance.department:
            name_dep=instance.department.name
        else:
            name_dep=None
        return name_dep

    
    # Formato de los datos al llamar al serializador
    class Meta:
        model=MyUser # Especifica modelo a utilizar al consultar los datos
        read_only_fields=('PK',) # Indicamos que la clave primaria es de solo lectura al mostrar los datos

        # Contiene los campos que queremos mostrar
        fields = [
            # Estos atributos se heredan de AbstracUser menos PK y department
            'PK',
            'username',
            'email',
            'password',
            'department',
            'is_staff',
            'is_superuser',
            'is_active'
        ]


# SERIALIZADOR DE MODELO " DEPARTMENT "

class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    # SerializerMethodField ==> Un campo de solo lectura que obtiene su representación llamando a un método en clase de serializador principal.
    users = serializers.SerializerMethodField()

    def get_users(self, instance):
        # Busca en los objetos usuario filtrando cullo departamento sea igual a la clave primara recibida por parametro
        search_users = MyUser.objects.filter(department=instance.PK)
        # Crea serializador de usuario recibido
        serializer = MyUserSerializer(search_users, many=True)

        return serializer.data

    class Meta:
        model = Department # Especifica modelo a utilizar al consultar los datos
        read_only_fields = ('PK',) # Indicamos que la clave primaria es de solo lectura al mostrar los datos
        # Contiene los campos a mostrar en la vista
        fields = ['PK', 'name', 'users', 'is_active']# Estos atributos se heredan de AbstracUser menos PK y department


# SERIALIZADOR DE LOGIN (No tiene modelo)

class LoginSerializer(serializers.Serializer):
    # Crea variables de nombre y contraseña e indicamos que son serializadores de cadena de texto
    username = serializers.CharField()
    password = serializers.CharField()

    # Valida nombre y contraseña recibidos/introducidos
    def validate(self, attrs):
        # Guarda el nombre y contraseña
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Si el nombre de usuario tiene la siguiente estructura " *@*.* "
            if re.match(r'^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',
                        username.lower()):
                # Guardamos usuario cuyo email sea igual al nombre de usuario introducido
                users = User.objects.filter(email=username)

                if len(users) != 1:
                    raise ValidationError(
                        'The user with that username or email not exist.')
                
                # Guarda nombre de usuario 
                username = users[0].username
        # Realiza la autenticacion pasamos el nombre y la contraseña obtenidas
        user = authenticate(username=username,
                            password=password)

        if not user:

            user_aux = User.objects.filter(username=attrs['username'])

            if len(user_aux) != 0:
                if not user_aux[0].is_active:
                    raise ValidationError('User is disabled.')

            raise ValidationError('Incorrect username or password.')

        return {'user': user}