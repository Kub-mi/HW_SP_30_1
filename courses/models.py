from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    preview = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name='превью')
    description = models.TextField(verbose_name='описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    preview = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name='превью')
    link = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson', null=True, blank=True)


    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="пользователь",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="курс",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "подписка на курс"
        verbose_name_plural = "подписки на курсы"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="uniq_subscription_user_course"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.course}"
