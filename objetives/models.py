from django.db import models
from login.models import MyUser, Department, check_is_empty, check_is_in
from rest_framework.exceptions import ValidationError
import uuid
import datetime
# Importa serializers nativo de rest framework
from rest_framework import serializers, permissions
from rest_framework.decorators import api_view, permission_classes
from django.contrib import admin
from rest_framework.permissions import AllowAny
from alvaro_sewan_objetives import settings
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS

# ------ Q  Cuatrimestre
class Q(models.Model):
    # Clave primaria " uuid4 "
    PK = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # Departamento clave ajena " uuid departamento"
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING)
    # Manager clave ajena " uuid Usuario "
    manager = models.ForeignKey(
        MyUser, related_name='manager', on_delete=models.DO_NOTHING)
    # Empleado clave ajena " uuid Usuario "
    employee = models.ForeignKey(
        MyUser, related_name='employee', on_delete=models.DO_NOTHING)
    # Validacion por Manager
    check_manager = models.BooleanField(default=False)
    # Validacion por Usuario
    check_employee = models.BooleanField(default=False)
    # Actualizar Fecha
    update_date = models.DateTimeField(auto_now=True)
    # Fecha Inicio
    starting_date = models.DateTimeField(auto_now=False)
    # Fecha Fin
    ending_date = models.DateTimeField(auto_now=False)
    # Activo/Cerrado
    is_active = models.BooleanField(default=True)

    



# ----- NOTAS de usuario en plantilla " Q "  ------------------

class Note(models.Model):
    # Clave primaria " uuid4 "
    PK = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # Usuario que escribe la nota " clave primaria "
    User = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING)
    # Q
    Q_Note=models.ForeignKey(Q, on_delete=models.DO_NOTHING)
    # Texto/Contenido de la nota
    text = models.CharField(max_length=50)
    # Fecha de creacion
    date = models.DateTimeField(auto_now=False)
    # Activo/Cerrado
    is_active = models.BooleanField(default=True)

# ------  Objetivos del cuatrimestre " Q "  ---------------------------

class Objectives_Q(models.Model):
    # Clave primaria " uuid4 "
    PK = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # Texto/Contenido del objetivo
    text = models.CharField(max_length=100)
    # Objetivos secundarios
    obj_secundary = models.BooleanField(default=False)
    # Objetivo padre
    obj_father = models.CharField(max_length=100, null=True, blank=True)
    # Puntuacion
    score = models.IntegerField()
    # Activo/Cerrado
    is_active = models.BooleanField(default=True)
    # Q
    Q_Note=models.ForeignKey(Q, on_delete=models.DO_NOTHING)


# ----- PERMISOS  -------------------

# Comprueba si es manager o empleado
class IsUserManageOrEmployee(BasePermission):
    def has_permission(self, request, view):
        if (request.method == 'POST') and \
                not request.user.is_superuser:

            return False
        elif request.user.is_authenticated:

            return bool(request.user and request.user.is_authenticated)

        else:
            return False

    def check_object_permission(self, user, obj):
        return bool(user and user.is_authenticated and
                    bool(obj.manager.PK == user.PK or obj.employee.PK == user.PK))

    def has_object_permission(self, request, view, obj):
        if self.check_object_permission(request.user, obj):
            return permissions.AllowAny



# -- CREAR OBJETIVOS  --------

def check_valid_post_Objectives_Q(request):
    # Comprueba que no este vacio los campos score y text
    check_is_empty({'score': str(request.data.get('score','Not found'))})
    check_is_empty({'text': request.data.get('text', 'Not found')})
    # Comprueba si el campo score es numerico
    if not str(request.data['score']).isnumeric():
        raise ValidationError(" The score is not numeric")

    # Crea objetivo pasandole el texto y score recibidos 
    objetive=Objectives_Q(text=request.data['text'],score=request.data['score'])
    
    # Activamos 
    objetive.is_active=True

    # Comprueba si tiene objetivo secundario
    if request.data['obj_secundary']:
        objetive.obj_secundary=request.data['obj_secundary']
    else:
        objetive.obj_secundary=False
    
    # Comprueba el obj_father
    if request.data['obj_father']:
        objetive.obj_father=request.data['obj_father']
    else:
        objetive.obj_father=""
    Q_Note=Q.objects.filter(PK=request.data['Q_Note'])
    objetive.Q_Note=Q_Note[0]
    
    objetive.save()

    return objetive
    

# --- MODIFICAR OBJETIVOS  ------

def check_if_is_valid_put_Objectives_Q(instance, request):
    field=""
    # Comprueba que no este vacio los campos score y text
    check_is_empty({'score': str(request.data.get('score','Not found'))})
    check_is_empty({'text': request.data.get('text', 'Not found')})
    # Comprueba si el campo score es numerico
    if not str(request.data['score']).isnumeric():
        raise ValidationError(" The score is not numeric")

    instance.score=request.data['score']
    instance.text=request.data['text']
    instance.obj_secundary=request.data['obj_secundary']
    instance.obj_father=request.data['obj_father']
    instance.is_active=request.data['is_active']

    instance.save()
    
    return instance


# ----  CREAR NOTAS  ------------

def check_valid_post_Note(request):
    data_to_check={
        'text': request.data.get('text', 'Not found')
    }
    check_is_empty(data_to_check)
    fecha= datetime.datetime.now()
    if not request.user.is_anonymous:
        user=request.user
    else:
        search_admin=MyUser.objects.filter(username="admin")
        if len(search_admin) != 0:
            user=search_admin[0]
        else:
            raise ValidationError("User admin not exists")
    search_Q =Q.objects.filter(PK=request.data['Q_Note'])
    if len(search_Q) != 0:
        Q_N = search_Q[0]
    else:
        raise ValidationError("Q_N not exists")
    note=Note()
    note.User= user
    note.date=fecha
    note.is_active=True
    note.text=request.data['text']
    note.Q_Note=Q_N
    
    
    
    note.Q_Note= Q_N

    note.save()

    return note
    

# ----  MODIFICAR NOTAS  --------------------

def check_if_is_valid_put_Note(instance, request):
    data_to_check={
        'text': request.data.get('text', 'Not found')
    }
    check_is_empty(data_to_check)
    user=request.user
    if instance.User == user:
        instance.text=request.data['text']
        fecha= datetime.datetime.now()
        instance.date=fecha
        instance.save()
    else:
        raise ValidationError("Your user can't change to Note values")

    return instance



# --- CREAR CUATRIMESTRE " Q "  --------------

def check_valid_post_Q(request):
    # Guarda la instancia al objeto Departamento cuya PK sea igual a la introducida en el campo department(Vista)
    departments = Department.objects.filter(PK=request.data['department'])
    manager = MyUser.objects.filter(PK=request.data['manager'])
    employee = MyUser.objects.filter(PK=request.data['employee'])

    Quatrimestre=Q()
    Quatrimestre.department=departments[0]
    Quatrimestre.manager=manager[0]
    Quatrimestre.employee=employee[0]
    Quatrimestre.starting_date=request.data['starting_date']
    Quatrimestre.ending_date=request.data['ending_date']
    Quatrimestre.save()
    return Quatrimestre

# --- MODIFICAR CUATRIMESTRE  " Q "   -----------------

def check_valid_put_Q(instance, request):
    # Actualiza valores de atributos por valores enviados en la vista
    departments = Department.objects.filter(PK=request.data['department'])
    manager = MyUser.objects.filter(PK=request.data['manager'])
    employee = MyUser.objects.filter(PK=request.data['employee'])


    
    instance.department=departments[0]
    instance.manager=manager[0]
    instance.employee=employee[0]
    instance.starting_date=request.data['starting_date']
    instance.ending_date=request.data['ending_date']
    instance.save()
    return instance