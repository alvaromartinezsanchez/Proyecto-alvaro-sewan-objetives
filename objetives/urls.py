from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import Objectives_QViewSet, QViewSet, NoteViewSet, Check_Q


router = DefaultRouter()
router.register(r'objetives', Objectives_QViewSet)
router.register(r'qs', QViewSet)
router.register(r'notes', NoteViewSet)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    path('Check_Q', Check_Q.as_view())
]