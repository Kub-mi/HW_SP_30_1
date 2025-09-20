from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    preview = models.ImageField(upload_to='courses/', blanck=True, null=True, verbose_name='превью')
    description = models.TextField(verbose_name='описание')


class Lesson(models.Model):
    title = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    preview = models.ImageField(upload_to='courses/', blanck=True, null=True, verbose_name='превью')
    link = models.URLField(blank=True, null=True)
