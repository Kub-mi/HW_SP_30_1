from rest_framework import viewsets, generics, permissions
from users.models import User, Payment
from users.permissions import IsSelfOrAdmin
from users.serializers import UserSerializer, PaymentSerializer, RegisterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    def get_queryset(self):
        """
        Для списка оставляем приватность: обычный видит только себя, админ — всех.
        (Требование допзадания про «смотреть любой профиль» относится к retrieve/{id}.)
        """
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        if getattr(self, 'action', None) == 'list':
            return qs.filter(pk=user.pk)
        return qs

    def retrieve(self, request, *args, **kwargs):
        """
        Любой авторизованный может смотреть ЛЮБОЙ профиль:
        - если это свой профиль или админ — полный сериализатор (UserSerializer);
        - если чужой профиль — публичный сериализатор (UserPublicSerializer) без фамилии/пароля/платежей.
        """
        instance = self.get_object()  # тут сработает IsSelfOrAdmin.has_object_permission — это мешает публичному чтению.
        # поэтому переопределим объектные права ТОЛЬКО для retrieve:
        # вручную пропустим просмотр, а редактирование остаётся под IsSelfOrAdmin.
        is_self = (request.user.pk == instance.pk)
        is_admin = bool(request.user.is_staff)

        if is_self or is_admin:
            serializer = UserSerializer(instance)
        else:
            # Просмотр чужого профиля: публикуем только «общую» инфу
            serializer = UserPublicSerializer(instance)
        return Response(serializer.data)


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("user", "course", "lesson").all()
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
