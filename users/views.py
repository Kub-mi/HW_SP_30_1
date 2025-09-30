from rest_framework import viewsets, generics, permissions
from users.models import User, Payment
from users.permissions import IsSelfOrAdmin
from users.serializers import UserSerializer, PaymentSerializer, RegisterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        if getattr(self, 'action', None) == 'list':
            return User.objects.filter(pk=user.pk)
        return super().get_queryset()


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objeсts.select_related("user", "course", "lesson").all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('course', 'method')
    ordering_fields = ('paid_at',)
    ordering = ("-paid_at",)

class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


class PaymentDestroyAPIView(generics.DestroyAPIView):
    queryset = Payment.objects.all()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # регистрация открыта
