from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models import Q

from courses.models import Course, Lesson


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email')

    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счет'
        STRIPE = 'stripe', 'Stripe'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments', verbose_name='Пользователь')
    paid_at = models.DateTimeField(auto_now=True, verbose_name='Дата оплаты')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='payments', verbose_name='Оплаченный курс')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    method = models.CharField(max_length=20, choices=Method.choices, verbose_name="Способ оплаты",)
    stripe_product_id = models.CharField(max_length=255, blank=True, verbose_name="ID продукта Stripe")
    stripe_price_id = models.CharField(max_length=255, blank=True, verbose_name="ID цены Stripe")
    stripe_session_id = models.CharField(max_length=255, blank=True, verbose_name="ID сессии Stripe")
    stripe_checkout_url = models.URLField(blank=True, verbose_name="Ссылка на оплату")
    stripe_status = models.CharField(max_length=50, blank=True, verbose_name="Статус Stripe")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        constraints = [
            models.CheckConstraint(
                name="payment_exactly_one_of_course_or_lesson",
                check=(
                        (Q(course__isnull=False) & Q(lesson__isnull=True)) |
                        (Q(course__isnull=True) & Q(lesson__isnull=False))
                ),
            )
        ]
        ordering = ["-paid_at", "-id"]

    def __str__(self) -> str:
        target = self.course or self.lesson
        target_name = getattr(target, "title", str(target)) if target else "—"
        return f"#{self.pk} {self.user} → {target_name} ({self.amount})"
