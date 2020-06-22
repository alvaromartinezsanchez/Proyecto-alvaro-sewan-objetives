from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import MyUserViewSet, DepartmentViewSet, CustomAuth, CustomLogOut

router = DefaultRouter()
router.register(r'users', MyUserViewSet)
router.register(r'departments',DepartmentViewSet)


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    path('setLogin/', CustomAuth.as_view()),
    path('logOut/', CustomLogOut.as_view()),
]