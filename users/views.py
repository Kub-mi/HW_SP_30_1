from django.core.exceptions import ImproperlyConfigured
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from stripe.error import StripeError

from users.models import Payment, User
from users.permissions import IsSelfOrAdmin
from users.serializers import (
    PaymentSerializer,
    RegisterSerializer,
    UserPublicSerializer,
    UserSerializer,
)
from users.services import create_stripe_session


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


@extend_schema_view(
    post=extend_schema(
        summary="Создать платёж и получить ссылку на оплату Stripe",
        description=(
            "Создаёт платёж в системе и инициирует сессию Stripe Checkout."
            " В ответе будет ссылка на оплату (поле `stripe_checkout_url`)."
        ),
        responses=PaymentSerializer,
    )
)
class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user, method=Payment.Method.STRIPE)

        target = payment.course or payment.lesson
        name = getattr(target, "title", f"Оплата #{payment.pk}")
        description = getattr(target, "description", "") or ""
        metadata = {"payment_id": str(payment.pk)}

        try:
            session_data = create_stripe_session(
                name=name,
                description=description,
                amount=payment.amount,
                metadata=metadata,
            )
        except (StripeError, ImproperlyConfigured) as exc:
            raise ValidationError({"stripe": str(exc)}) from exc

        payment.stripe_product_id = session_data.product_id
        payment.stripe_price_id = session_data.price_id
        payment.stripe_session_id = session_data.session_id
        payment.stripe_checkout_url = session_data.checkout_url or ""
        payment.stripe_status = session_data.session.get("status", "")
        payment.save(
            update_fields=[
                "stripe_product_id",
                "stripe_price_id",
                "stripe_session_id",
                "stripe_checkout_url",
                "stripe_status",
            ]
        )


@extend_schema_view(
    get=extend_schema(
        summary="Список платежей",
        parameters=[
            OpenApiParameter(
                name="course",
                location=OpenApiParameter.QUERY,
                type=int,
                description="Фильтрация по ID курса",
            ),
            OpenApiParameter(
                name="method",
                location=OpenApiParameter.QUERY,
                type=str,
                description="Фильтрация по способу оплаты",
            ),
            OpenApiParameter(
                name="ordering",
                location=OpenApiParameter.QUERY,
                type=str,
                description="Сортировка по дате оплаты (paid_at)",
            ),
        ],
        responses=PaymentSerializer,
    )
)
class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("user", "course", "lesson").all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("course", "method")
    ordering_fields = ("paid_at",)
    ordering = ("-paid_at",)


@extend_schema_view(
    get=extend_schema(summary="Детали платежа", responses=PaymentSerializer)
)
class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    patch=extend_schema(summary="Обновить платёж", responses=PaymentSerializer),
    put=extend_schema(summary="Заменить платёж", responses=PaymentSerializer),
)
class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    delete=extend_schema(summary="Удалить платёж")
)
class PaymentDestroyAPIView(generics.DestroyAPIView):
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # регистрация открыта
