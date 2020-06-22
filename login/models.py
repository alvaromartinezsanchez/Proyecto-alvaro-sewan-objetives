from django.db import models

#  ABSTRACTUSER clase nativa de django
from django.contrib.auth.models import AbstractUser

# UUID
import uuid

# Validation error
from rest_framework.exceptions import ValidationError

# Re
import re

# Importa serializers nativo de rest framework
from rest_framework import serializers, permissions

from rest_framework.decorators import api_view, permission_classes
from django.contrib import admin
from rest_framework.permissions import AllowAny
from alvaro_sewan_objetives import settings
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS

# ---------  PERMISOS (COMPRUEBA EL TIPO DE USUARIO)  ---

# Comprueba si es usuario normal o administrador = True si no False
class IsUserCommonOrAdmin(BasePermission):
    def has_permission(self, request, view):

        """if (request.method == 'POST') and \
                not request.user.is_superuser:
            return False"""

        if request.user and request.user.is_authenticated:
            return True

        return False

    def check_object_permission(self, user, obj):
        return bool(user and user.is_authenticated and(
                    bool(user.is_superuser or obj == user) or user.is_staff))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)

# Comprueba si es usuario propietario o administrador
class IsUserOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        """if (request.method == 'POST') and \
                not request.user.is_staff:

            return False"""
        if request.user and request.user.is_authenticated:

            return True

        return False

    def check_object_permission(self, user, obj):
        return bool(user and user.is_authenticated and
                    bool(user.is_staff or obj == user))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)

# Comprueba si es usuario pertenece al departamento
class IsUserForDepartment(BasePermission):
    def has_permission(self, request, view):
        if (request.method == 'POST') and \
                not request.user.is_staff:

            return False
        elif request.user.is_authenticated:

            return bool(request.user and request.user.is_authenticated)

        else:
            return False

    def check_object_permission(self, user, obj):
        return bool(user and user.is_authenticated and
                    bool(user.is_staff or obj == user.department))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)



# ------------------DEPARTAMENTO---------------------------

class Department(models.Model):
    PK = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    

# CREAR Y MODIFICAR DEPARTAMENTOalvaro

# CREAR DEPARTAMENTO
def check_valid_post_department(request):
    data_to_check = {
        'name': request.data.get('name', 'Not found')
    }

    department = Department(name=request.data['name'])

    department.save()

    return department

# MODIFICAR DEPARTAMENTO
def check_if_is_valid_put_department(instance, request):
    
    if request.data.get('name') is not None:
        check_is_empty({'name': request.data.get('name', 'Not found')})
        instance.name = request.data.get('name', instance.name)
    
    instance.save()

    return instance


# --------------------------USUARIO-------------------

class MyUser(AbstractUser):
    PK = models.UUIDField(primary_key=True, default=uuid.uuid4)
    department = models.ForeignKey(
        Department, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    


# METODOS PARA CREAR Y MODIFICAR USUARIOS

# CREAR USUARIOS

def check_valid_post_user(request):
    # comprueba si el campo email existe
    if request.data.get('email', '') != '':
        # si existe, comprueba que es valido
        check_email(request.data['email'])

        # Comprueba si el nombre de email ya esta registrado en el sistema
        if len(MyUser.objects.filter(email=request.data['email'])) != 0:
            # Si ya esta registrado devuelve error
            raise ValidationError(
                'This email is being used by another user.')

    # Asigna valor a los atributos, utilizando las funciones para validar los datos recibidos
    is_staff = check_is_in(request.data.get('is_staff', 'False'))
    is_superuser = check_is_in(request.data.get('is_superuser', 'False'))
    # Guarda el valor de departamento, si no existe guarda " None "
    department = request.data.get('department', None)

    # Crea Diccionario con campos que no pueden estar vacios
    data_to_check = {
        'username': request.data.get('username', 'Not found'),
        'password': request.data.get('password', 'Not found'),
        'email': request.data.get('email', 'Not found')
    }
    # Comprueba si los campos del Diccionario estan vacios
    check_is_empty(data_to_check)

    # Utiliza metodo create_user heredado de AbstractUser para crear el usuario
    user = MyUser.objects.create_user(
        
        # Crea usuario pasando los datos del nombre y contraseña
        username=request.data['username'], password=request.data['password'])
    
    # Asigna valor a los atributos del usuario creado
    user.email = request.data['email']
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.is_active = True

    # Si el departamento existe, es decir el usuario tiene un departamento asignado
    if department is not None:
        # obtenemos lista de departamentos por su clave primaria
        departments = Department.objects.filter(PK=department)
        # Si hay uno o mas departamentos
        if len(departments) != 0:
            # Guarda el nombre del departamento
            department = departments[0]
        else:
            department = None

    # Asigna valor al campo departamento
    user.department = department

    # Guarda el usuario en la base de datos
    user.save()

    return user


# MODIFICA USUARIOS

# modifica usuarios
def check_if_is_valid_put_user(instance, request): # instance ==> objeto que hace la llamada ; request ==> Datos que se reciben ( Nuevos datos )
    field = ""
    # Comprueba que se ha recibido el campo email
    if request.data.get('email', '') != '':
        # Valida el campo recibido en email
        check_email(request.data['email'])

        # Comprueba si el nombre de email ya esta registrado en el sistema
        if len(MyUser.objects.filter(email=request.data['email']).exclude(pk=instance.pk)) != 0:
            # Si ya esta registrado devuelve error
            raise serializers.ValidationError(
                'This email is being used by another user.')
    # Comprueba valor de is_active ( para ver si el usuario esta o no activo )
    check_is_active = request.data.get('is_active', True)

    is_active = check_is_in(check_is_active)

    # Guarda si es usuario trabajador
    is_staff = check_is_in(request.data.get('is_staff', 'False'))
    # Almacena si es superusuario
    is_superuser = check_is_in(request.data.get('is_superuser', 'False'))
    # Guarda el departamento pasado por parametro, si no hay se asigna " None "
    department = request.data.get('department', None)

    # Datos que no pueden enviarse en blanco
    data_to_check = {
        'username': request.data.get('username', 'Not found'),
        'email': request.data.get('email', 'Not found')
    }
    # Comprueba que los campos indicados no estan vacios
    check_is_empty(data_to_check)


    # --------------CAMBIAR CONTRASEÑA --------------------
    # Si la contraseña o la repeticion de la contraseña es None
    if request.data.get('password', 'notFound') is None or request.data.get(
            'repeat_password', 'notFound') is None:
        field += 'Password' # field = None

    # Si entra en el if anterior field = None ; si no field = ""
    if field != "":
        raise ValidationError(
            'Invalid data for {fields}'.format(fields=field))

    # Si contraseña o repeticion es distinto de '' , es decir tiene contenido
    if request.data.get('password', '') != '' or request.data.get(
            'repeat_password', '') != '':

        # Comprueba que los campos no estan vacios
        check_is_empty({'password': request.data.get('password', 'Not found'),
                        'repeat_password': request.data.get('repeat_password',
                                                            'Not found')})

        # Comprueba contraseña antigua y que contraseña nueva y repeticion de contraseña nueva coinciden
        if instance.check_password(request.data.get('old_password', '')) and \
                request.data['password'] == request.data['repeat_password']:
            # Modifica constraseña antigua por nueva
            instance.set_password(request.data['password'])

        # Comprueba que contraseña y repeticion coinciden
        elif request.data['password'] != request.data['repeat_password']:
            raise ValidationError(
                'The password need to be identical')

        # Comprueba que la contraseña antigua coincide
        else:
            raise ValidationError('Incorrect old passwords')


    # ---------------------CAMBIAR DEPARTAMENTO--------------------------
    # Comprueba que el usuario tiene un departamento asignado
    if request.data.get('department') is not None:
        # Comprueba que el campo departamento del usuario no esta vacio
        check_is_empty(
            {'department': request.data.get('department', 'Not found')})
        # Guardamos el valor del departamento
        department = request.data.get('department')
        # Guarda en lista departamentos filtrados por su PK
        search_department = Department.objects.filter(PK=department)

        # Si existe el departamento
        if len(search_department) != 0:
            # Guarda el departamento en el objeto usuario
            instance.department = search_department[0]

    else:
        field += 'Department, '
    # Guarda el nombre de usuario en el objeto
    instance.username = data_to_check['username']
    # Guarda valores activo, administrador, trabajador
    instance.is_active = is_active
    instance.is_superuser = is_superuser
    instance.is_staff = is_staff
    # Guarda el nuevo objeto usuario modificado
    instance.save()
    # Devuelve el objeto modificado
    return instance



# ---------------- METODOS DE VALIDACION DE CAMPOS ------

# VALIDAR  CAMPO E-MAIL 
def check_email(email):
    if isinstance(email, str) is False:
        raise ValidationError('The email need to be string')

    if re.match(r'^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',
                email.lower()):
        return True
    else:
        raise ValidationError('Not valid email')


# Comprueba si los campos pasados por el request no estan vacios y existen

def check_is_empty(attrs):
    for attribute in attrs:
        if attrs[attribute] == 'Not found':
            raise ValidationError(
                'The {data} has not been sent'.format(data=attribute))

        if isinstance(attrs[attribute], str) is False:
            raise ValidationError(
                'The {data} need to be string'.format(data=attribute))

        if len(attrs[attribute]) == 0:
            raise ValidationError(
                'The {data} is empty'.format(data=attribute))

    return True

# Formatea y devuelve un formato de boleano valido para python
def check_is_in(param):
    response = {
        True: True,
        False: False,
        'true': True,
        'false': False,
    }

    if not isinstance(param, str) and not isinstance(param, bool):
        raise ValidationError('Only true or false in string')

    if isinstance(param, str):
        param = param.lower()

    if param not in response:
        raise ValidationError('Only true or false in string')

    return response[param]