from rest_framework.routers import DefaultRouter
from django.urls import path
from users.views import UserViewSet


router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [

] + router.urls