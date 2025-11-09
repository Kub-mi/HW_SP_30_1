from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Payment

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # подбери поля под свою модель
    list_display = ("id", "email", "username", "is_active", "is_staff")
    search_fields = ("email", "username")  # важно для autocomplete_fields

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "paid_at",
        "course",
        "lesson",
        "amount",
        "method",
        "stripe_session_id",
        "stripe_status",
    )
    list_filter = ("method", "paid_at", "stripe_status")
    search_fields = ("user__email", "user__username", "course__title", "lesson__title")
    autocomplete_fields = ("user", "course", "lesson")  # теперь будет работать
    ordering = ("-paid_at", "-id")
    readonly_fields = (
        "stripe_product_id",
        "stripe_price_id",
        "stripe_session_id",
        "stripe_checkout_url",
        "stripe_status",
    )
