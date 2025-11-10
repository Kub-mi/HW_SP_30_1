from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


@shared_task
def deactivate_inactive_users() -> int:
    """Deactivate users who have been inactive for more than 30 days."""
    User = get_user_model()
    threshold = timezone.now() - timedelta(days=30)

    affected_users = User.objects.filter(
        is_active=True,
    ).filter(
        models.Q(last_login__lt=threshold)
        | models.Q(last_login__isnull=True, date_joined__lt=threshold)
    )

    updated = affected_users.update(is_active=False)
    return updated
