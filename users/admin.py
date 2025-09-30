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
    list_display = ("id", "user", "paid_at", "course", "lesson", "amount", "method")
    list_filter = ("method", "paid_at")
    search_fields = ("user__email", "user__username", "course__title", "lesson__title")
    autocomplete_fields = ("user", "course", "lesson")  # теперь будет работать
    ordering = ("-paid_at", "-id")
