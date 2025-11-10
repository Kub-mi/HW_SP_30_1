from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from courses.models import Course, Subscription


@shared_task
def send_course_update_notifications(course_id: int) -> int:
    """Send notifications about course updates to subscribed users."""
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return 0

    subscriptions = (
        Subscription.objects
        .filter(course_id=course_id)
        .select_related("user")
        .only("user__email")
    )
    recipients = [sub.user.email for sub in subscriptions if sub.user and sub.user.email]

    if not recipients:
        return 0

    subject = f"Обновление курса «{course.title}»"
    message = (
        "Материалы курса были обновлены. Зайдите в личный кабинет, чтобы ознакомиться с новыми материалами."
    )

    return send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipients,
        fail_silently=True,
    )
