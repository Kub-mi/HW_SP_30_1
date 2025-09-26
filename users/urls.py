from rest_framework.routers import DefaultRouter
from django.urls import path
from users.views import UserViewSet,PaymentCreateAPIView, PaymentListAPIView, PaymentRetrieveAPIView, PaymentUpdateAPIView, PaymentDestroyAPIView


router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),                 # GET ?course=&lesson=&method=&ordering=
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),      # POST
    path('payments/<int:pk>/', PaymentRetrieveAPIView.as_view(), name='payment-detail'),  # GET
    path('payments/<int:pk>/update/', PaymentUpdateAPIView.as_view(), name='payment-update'),  # PUT/PATCH
    path('payments/<int:pk>/delete/', PaymentDestroyAPIView.as_view(), name='payment-delete'), # DELETE

] + router.urls